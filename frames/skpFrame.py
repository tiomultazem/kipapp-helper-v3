import customtkinter as ctk
from tkinter import filedialog
import threading
from datetime import datetime
import os
import tkinter as tk
import openpyxl

from . import app


from .baseFrame import BaseTableFrame


SKP_ACCENT = ("stupidest ",)


class SkpFrame(BaseTableFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._skp_map = {}
        self._kegiatan_cache_data = None # RAM cache
        self._selected_skp = None
        self._selected_label = None
        self._on_skp_changed_callback = None
        self._force_related_reload = False

        self.cache_dir = app.CACHE_DIR
        self.skp_cache_file = os.path.join(self.cache_dir, "skp.json")
        self.kegiatan_cache_file = os.path.join(self.cache_dir, "kegiatan.json")

        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent", height=40)
        top.pack(fill="x", padx=8, pady=(8, 4))
        top.pack_propagate(False)

        ctk.CTkLabel(top, text="Periode",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")

        self.cmb_periode = ctk.CTkComboBox(
            top,
            values=["Memuat periode..."],
            width=200, # Reduced width
            state="readonly",
            font=ctk.CTkFont(size=13),
            command=self._on_select_periode
        )
        self.cmb_periode.pack(side="left", padx=(8, 0))
        self.cmb_periode.set("Memuat periode...")

        self.btn_refresh = ctk.CTkButton(
            top,
            text="Reload",
            width=80, # Reduced width
            font=ctk.CTkFont(size=13),
            command=self.reload_all
        )
        self.btn_refresh.pack(side="left", padx=(8, 0))

        self.btn_unduh = ctk.CTkButton(
            top,
            text="Unduh",
            width=80,
            font=ctk.CTkFont(size=13),
            fg_color="#27ae60",
            hover_color="#2ecc71",
            command=self._unduh_xlsx
        )
        self.btn_unduh.pack(side="left", padx=(8, 0))

        # Info row via BaseClass
        self.setup_info_row(
            parent_frame=self,
            info_default_text="Pilih periode untuk melihat kegiatan.",
            delete_cmd=self._delete_checked_server,
            clear_cmd=self._hapus_tampilan
        )

        self.table_wrap = ctk.CTkFrame(self, height=300)
        self.table_wrap.pack_propagate(False)

        self.tree = None

        cols = (
            "check",
            "no",
            "tanggal",
            "tanggalselesai",
            "jammulai",
            "jamselesai",
            "rencanakinerja",
            "kegiatan",
            "capaian",
            "progres",
            "datadukung",
            "iscapaianskp",
        )

        self._headings_dict = {
            "check": "☐",
            "no": "No.",
            "tanggal": "Start Date",
            "tanggalselesai": "End Date",
            "jammulai": "Jam Mulai",
            "jamselesai": "Jam Selesai",
            "rencanakinerja": "Rencana Kinerja",
            "kegiatan": "Kegiatan",
            "capaian": "Capaian",
            "progres": "Progres",
            "datadukung": "Link Bukti",
            "iscapaianskp": "Centang",
        }

        widths = {
            "check": (40, "center", False),
            "no": (50, "center", False),
            "tanggal": (100, "center", False),
            "tanggalselesai": (100, "center", False),
            "jammulai": (90, "center", False),
            "jamselesai": (90, "center", False),
            "rencanakinerja": (220, "w", True),
            "kegiatan": (260, "w", True),
            "capaian": (80, "center", False),
            "progres": (80, "center", False),
            "datadukung": (180, "w", True),
            "iscapaianskp": (80, "center", False),
        }

        self.setup_tree(self.table_wrap, cols, self._headings_dict, widths)

        self.after(300, self.load_periode)

    def _can_modify(self):
        if self._selected_skp and str(self._selected_skp.get("statusskp")).lower() == "dinilai":
            return False
        return True

    def get_active_skp_id(self):
        if self._selected_skp:
            return str(self._selected_skp.get("id"))
        return None

    def _unduh_xlsx(self):
        if not self.tree.get_children():
            self._log("⚠️ Tidak ada data untuk diunduh.")
            return

        filename = f"{self._selected_label}.xlsx".replace("/", "-")
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=filename,
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not filepath: return

        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "SKP"

            # Header (Skip checklist)
            cols = list(self.tree["columns"])
            headers = [self._headings_dict[c] for c in cols if c != "check"]
            ws.append(headers)

            # Data
            for item_id in self.tree.get_children():
                vals = self.tree.item(item_id)["values"]
                # Skip first value (checklist symbol)
                ws.append(list(vals[1:]))

            wb.save(filepath)
            self._log(f"✅ SKP berhasil diunduh ke: {os.path.basename(filepath)}")
        except Exception as e:
            self._log(f"❌ Gagal unduh SKP: {e}")

    def _hapus_tampilan(self):
        """Hapus data kegiatan dari variabel dan tampilan tabel."""
        self._clear_skp_tree()
        self.lbl_info.configure(
            text="Pilih periode untuk melihat kegiatan.",
            text_color="gray"
        )
        self._log("🗑️ Tampilan kegiatan SKP dihapus.")

    def reload_all(self, force_related=False):
        self._force_related_reload = bool(force_related)
        try:
            if os.path.exists(self.skp_cache_file):
                os.remove(self.skp_cache_file)
            if os.path.exists(self.kegiatan_cache_file):
                os.remove(self.kegiatan_cache_file)
        except Exception as ex:
            self._log(f"⚠️ Gagal menghapus cache: {ex}")

        # Simpan label yang sedang dipilih agar bisa dikembalikan setelah reload
        self._last_selected_before_reload = self._selected_label
        
        self._skp_map = {}
        self._kegiatan_cache_data = None # Kosongkan RAM cache agar benar-benar ambil dari server
        self._selected_skp = None
        self._selected_label = None

        self._clear_tree()

        self.load_periode(force=True)

    def load_periode(self, force=False):
        if not force:
            if self._skp_map and self._selected_label:
                options = list(self._skp_map.keys())
                self.cmb_periode.configure(values=options)
                self.cmb_periode.set(self._selected_label)
                self._on_select_periode(self._selected_label, quiet=True)
                return

            cache = app.read_json(self.skp_cache_file, {})
            tahun_now = datetime.now().year

            if cache.get("tahun") == tahun_now and cache.get("options") and cache.get("skp_map"):
                self._skp_map = cache.get("skp_map", {})
                options = cache.get("options", [])
                selected_label = cache.get("selected_label")

                self.cmb_periode.configure(values=options)
                pilih = selected_label if selected_label in self._skp_map else options[0]
                self.cmb_periode.set(pilih)
                self._selected_label = pilih
                self.lbl_info.configure(
                    text=f"Ditemukan {len(options)} periode SKP (cache lokal).",
                    text_color="gray"
                )
                self._log("📦 Periode SKP dimuat dari skp.json.")
                self._on_select_periode(pilih)
                return

        sess = self._get_session()
        if not sess:
            self.cmb_periode.configure(values=[" "])
            self.cmb_periode.set("Belum login ke KiPApp")
            self.lbl_info.configure(text="Belum login ke KiPApp.", text_color="orange")
            self._clear_tree()
            return

        self.cmb_periode.configure(values=["Memuat periode..."])
        self.cmb_periode.set("Memuat periode...")
        self._clear_tree()
        threading.Thread(target=self._load_periode_worker, daemon=True).start()

    def _load_periode_worker(self):
        sess = self._get_session()
        if not sess: return

        tahun_now = datetime.now().year
        try:
            m_th, u_th = app.get_api_info("tahun")
            r_tahun = sess.request(m_th, u_th, params={"jenis": 2}, timeout=15)
            tahun_list = r_tahun.json()
            periode_id = next(t["id"] for t in tahun_list if t["tahunawal"] == tahun_now)

            m_u, u_u = app.get_api_info("user")
            r_user = sess.request(m_u, u_u, timeout=15)
            pegawai_id = r_user.json()["id"]

            m_s, u_s = app.get_api_info("skp")
            r_skp = sess.request(m_s, u_s,
                             params={"periodeid": periode_id, "pegawaiid": pegawai_id, "jenis": 2}, timeout=15)
            skp_list = r_skp.json()

            options = []
            skp_map = {}
            for item in skp_list:
                tahun = tahun_now
                triwulan = item.get("keteranganperiodepenilaian", "-")
                status = item.get("statusskp", "-")
                label = f"{tahun} - Triwulan {triwulan} - {status}"
                options.append(label)
                skp_map[label] = item

            if not options:
                msg = "Tidak ada periode SKP yang sudah dibuat. Silakan buat dulu di web KiPApp."
                self.after(0, lambda: self.cmb_periode.configure(values=[msg]))
                self.after(0, lambda: self.cmb_periode.set(msg))
                self.after(0, lambda: self.lbl_info.configure(text=msg, text_color="orange"))
                if self._on_skp_changed_callback:
                    self.after(0, lambda: self._on_skp_changed_callback("EMPTY"))
                return

            self._skp_map = skp_map
            
            # Tentukan pilihan awal: jika ada memori pilihan sebelumnya, gunakan itu
            pilih_akhir = options[0]
            if hasattr(self, "_last_selected_before_reload") and self._last_selected_before_reload in skp_map:
                pilih_akhir = self._last_selected_before_reload
            
            self._selected_label = pilih_akhir

            app.write_json(self.skp_cache_file, {
                "tahun": tahun_now,
                "selected_label": self._selected_label,
                "options": options,
                "skp_map": skp_map,
            })

            self.after(0, lambda: self.cmb_periode.configure(values=options))
            self.after(0, lambda: self.cmb_periode.set(pilih_akhir))
            self.after(0, lambda: self._on_select_periode(pilih_akhir))

        except Exception as ex:
            self._log(f"❌ Gagal memuat periode SKP: {ex}")

    def _on_select_periode(self, selected_label, quiet=False):
        if not selected_label or selected_label not in self._skp_map:
            return

        self._selected_label = selected_label
        self._selected_skp = self._skp_map[selected_label]
        
        cache = app.read_json(self.skp_cache_file, {})
        if cache:
            cache["selected_label"] = selected_label
            app.write_json(self.skp_cache_file, cache)

        skp_id = str(self._selected_skp["id"])
        if self._on_skp_changed_callback:
            self._on_skp_changed_callback(skp_id)

        # Gunakan RAM cache jika sudah ada
        if self._kegiatan_cache_data is None:
            self._kegiatan_cache_data = app.read_json(self.kegiatan_cache_file, {})
        
        kegiatan_map = self._kegiatan_cache_data.get("kegiatan_map", {})

        self._clear_tree()

        if skp_id in kegiatan_map:
            rows = kegiatan_map[skp_id]
            self._fill_tree(rows)
            self.lbl_info.configure(
                text=f"Total kegiatan di KiPApp: {len(rows)} (cache lokal)",
                text_color="green" if rows else "orange"
            )
            return

        self.lbl_info.configure(text="Memuat kegiatan...", text_color="gray")
        threading.Thread(target=self._load_kegiatan_worker, args=(self._selected_skp,), daemon=True).start()

    def _load_kegiatan_worker(self, skp_item):
        sess = self._get_session()
        if not sess: return

        try:
            skp_id = str(skp_item["id"])
            m_k, u_k = app.get_api_info("kegiatan")
            r_kegiatan = sess.request(m_k, u_k, params={"skpid": skp_id}, timeout=15)
            kegiatan_list = r_kegiatan.json()

            rows = []
            for row in kegiatan_list:
                rows.append((
                    row.get("kegiatanperhariid", ""),
                    row.get("tanggal", ""),
                    row.get("tanggalselesai", ""),
                    row.get("jammulai", ""),
                    row.get("jamselesai", ""),
                    row.get("rencanakinerja", ""),
                    row.get("kegiatan", ""),
                    row.get("capaian", ""),
                    row.get("progres", ""),
                    row.get("datadukung", ""),
                    row.get("iscapaianskp", "")
                ))

            # Update RAM cache dan disk
            if self._kegiatan_cache_data is None:
                self._kegiatan_cache_data = {"kegiatan_map": {}}
            
            kegiatan_map = self._kegiatan_cache_data.get("kegiatan_map", {})
            kegiatan_map[skp_id] = rows
            app.write_json(self.kegiatan_cache_file, {"kegiatan_map": kegiatan_map})

            self.after(0, lambda: self._fill_tree(rows))
            self.after(0, lambda: self.lbl_info.configure(
                text=f"Total kegiatan di KiPApp: {len(rows)}",
                text_color="green" if rows else "orange"
            ))

        except Exception as ex:
            self._log(f"❌ Gagal memuat kegiatan: {ex}")

    def _delete_checked_server(self):
        checked_items = []
        for item in self.tree.get_children():
            if self.tree.set(item, "check") == "☑":
                checked_items.append(item)

        if not checked_items: return

        confirm = tk.messagebox.askyesno("Konfirmasi Hapus", f"Hapus {len(checked_items)} kegiatan terpilih dari SERVER dan lokal?")
        if not confirm: return

        self.btn_delete.configure(state="disabled", text="Hapus...")
        threading.Thread(target=self._delete_worker, args=(checked_items,), daemon=True).start()

    def _delete_worker(self, iids):
        # Proteksi Terakhir: Cek status SKP sebelum mulai menghapus
        if self._selected_skp and str(self._selected_skp.get("statusskp")).lower() == "dinilai":
            self._log("❌ Gagal: SKP sudah dinilai. Penghapusan dibatalkan demi keamanan.")
            self.after(0, lambda: self.btn_delete.configure(state="normal"))
            return

        def _on_success(deleted_iids):
            self.reload_all(force_related=True)

        self.btn_delete.configure(state="disabled", text="Hapus...")
        self.execute_api_delete(
            endpoint_alias="kegiatan_del",
            name_col="kegiatan",
            iids=iids,
            callback_after_success=_on_success
        )

    def _fill_tree(self, rows):
        self.fill_tree_data(
            rows,
            id_extractor=lambda r: str(r[0]) if r[0] else None,
            start_col_index=1
        )
