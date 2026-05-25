import customtkinter as ctk
import os
import tkinter as tk
import threading

from . import app
from .baseFrame import BaseTableFrame


RK_ACCENT = ("the ",)


class RkFrame(BaseTableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._current_skp_id = None
        self._rk_list_full = []  # RAM cache (termasuk rkid)
        self._on_rk_deleted_callback = None

        self.cache_dir = app.CACHE_DIR
        self.rk_cache_file = os.path.join(self.cache_dir, "rk.json")

        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent", height=40)
        top.pack(fill="x", padx=8, pady=(8, 4))
        top.pack_propagate(False)

        self.btn_refresh = ctk.CTkButton(
            top, text="Reload", width=100,
            font=ctk.CTkFont(size=13),
            command=self.reload_rk
        )
        self.btn_refresh.pack(side="left")

        # ── Info row via BaseClass ────────────────────────────────
        self.setup_info_row(
            parent_frame=self,
            info_default_text="Belum login ke KiPApp.",
            delete_cmd=self._delete_checked_rk,
            clear_cmd=self._hapus_tabel
        )

        # ── Treeview Setup via BaseClass ──────────────────────────
        table_wrap = ctk.CTkFrame(self, height=300)
        table_wrap.pack_propagate(False)

        cols = ("check", "no", "capaian", "rencanakinerja", "tim", "jenis")
        headings = {
            "check": "☐",
            "no": "No.",
            "jenis": "Jenis",
            "tim": "Tim",
            "rencanakinerja": "Rencana Kinerja",
            "capaian": "Capaian",
        }
        widths = {
            "check":         (40,  "center", False),
            "no":            (50,  "center", False),
            "capaian":       (70,  "center", False),
            "rencanakinerja":(330, "w",      True),
            "tim":           (150, "w",      True),
            "jenis":         (100, "center", False),
        }

        self.setup_tree(table_wrap, cols, headings, widths)

    # ── Public API ─────────────────────────────────────────────────
    def get_rk_list(self):
        """Return list RK (dengan rkid) untuk dipakai TaskFrame."""
        return self._rk_list_full

    # ── Reload / Hapus Tampilan ────────────────────────────────────
    def reload_rk(self):
        if not self._current_skp_id:
            self._log("⚠️ Belum ada SKP yang dipilih untuk reload RK.")
            return
        self._log("Reloading Rencana Kinerja...")
        self.load_rk(self._current_skp_id, force=True)

    def _hapus_tabel(self):
        self._clear_tree()
        try:
            if os.path.exists(self.rk_cache_file):
                os.remove(self.rk_cache_file)
        except Exception as ex:
            self._log(f"Gagal hapus cache RK: {ex}")
        self.lbl_info.configure(text="Tabel RK dihapus.", text_color="gray")

    # ── Load RK ────────────────────────────────────────────────────
    def load_rk(self, skp_id, quiet=False, force=False):
        if not skp_id:
            return
            
        if skp_id == "EMPTY":
            msg = "Tidak ada periode SKP yang sudah dibuat. Silakan buat dulu di web KiPApp."
            self._clear_tree()
            self.lbl_info.configure(text=msg, text_color="orange")
            return
            
        self._current_skp_id = skp_id

        if force:
            try:
                cache = app.read_json(self.rk_cache_file, {})
                rk_map = cache.get("rk_map", {})
                if skp_id in rk_map:
                    del rk_map[skp_id]
                    app.write_json(self.rk_cache_file, {"rk_map": rk_map})
            except Exception as ex:
                self._log(f"WARNING Gagal hapus cache RK: {ex}")
            rk_map = {}
        else:
            cache = app.read_json(self.rk_cache_file, {})
            rk_map = cache.get("rk_map", {})

        if not force and skp_id in rk_map:
            cached_data = rk_map[skp_id]
            self._rk_list_full = []
            rows = []
            for item in cached_data:
                if len(item) < 6:
                    self._rk_list_full = []
                    break
                item = self._normalize_row_order(item)
                rows.append(item)
                self._rk_list_full.append({
                    "ketjenis":       item[4],
                    "namatim":        item[3],
                    "rencanakinerja": item[2],
                    "rkid":           item[5],
                })

            if rows:
                self._fill_tree(rows)
                self.lbl_info.configure(text=f"Total RK: {len(rows)} (cache lokal)", text_color="gray")
                if not quiet:
                    self._log("📦 Rencana Kinerja dimuat dari cache.")
                return
            else:
                self._log("⚠️ Cache RK versi lama terdeteksi, memuat ulang dari server...")

        self._clear_tree()
        self.lbl_info.configure(text="Memuat RK...", text_color="gray")
        threading.Thread(target=self._load_rk_worker, args=(skp_id,), daemon=True).start()

    def _load_rk_worker(self, skp_id):
        sess = self._get_session()
        if not sess:
            self.after(0, lambda: self.lbl_info.configure(text="Menunggu sesi...", text_color="gray"))
            return

        try:
            m_rk, u_rk = app.get_api_info("rk")
            r_rk = sess.request(m_rk, u_rk, params={"skpid": skp_id, "direct": 1}, timeout=15)

            if r_rk.status_code != 200:
                self._log(f"❌ Server error {r_rk.status_code} saat muat RK.")
                self.after(0, lambda: self.lbl_info.configure(text=f"Error {r_rk.status_code}", text_color="red"))
                return

            try:
                rk_list = r_rk.json()
            except Exception:
                self._log(f"❌ Respon bukan JSON: {r_rk.text[:100]}")
                self.after(0, lambda: self.lbl_info.configure(text="Respon server invalid", text_color="red"))
                return

            self._rk_list_full = rk_list
            rows = []
            for i, item in enumerate(rk_list):
                capaian = item.get("jmlcapaian") or 0
                row = (
                    str(i + 1),
                    str(capaian),
                    item.get("rencanakinerja", "-"),
                    item.get("namatim", "-"),
                    item.get("ketjenis", "-"),
                    item.get("rkid"),
                )
                rows.append(row)

            # Simpan ke cache
            cache = app.read_json(self.rk_cache_file, {})
            rk_map = cache.get("rk_map", {})
            rk_map[skp_id] = rows
            app.write_json(self.rk_cache_file, {"rk_map": rk_map})

            self.after(0, lambda: self._fill_tree(rows))
            self.after(0, lambda: self.lbl_info.configure(
                text=f"Total RK: {len(rows)}", text_color="gray"
            ))

        except Exception as ex:
            self._log(f"❌ Gagal memuat RK: {ex}")

    # ── Delete RK ──────────────────────────────────────────────────
    def _delete_checked_rk(self):
        checked = [i for i in self.tree.get_children() if self.tree.set(i, "check") == "☑"]
        if not checked:
            return
        if not tk.messagebox.askyesno(
            "Konfirmasi Hapus RK",
            f"Hapus {len(checked)} Rencana Kinerja terpilih dari server?"
        ):
            return
        self.btn_delete.configure(state="disabled", text="Hapus...")
        threading.Thread(target=self._delete_rk_worker, args=(checked,), daemon=True).start()

    def _delete_rk_worker(self, iids):
        def _on_success(deleted_iids):
            # Update cache lokal
            if self._current_skp_id:
                try:
                    cache = app.read_json(self.rk_cache_file, {})
                    rk_map = cache.get("rk_map", {})
                    if self._current_skp_id in rk_map:
                        deleted_set = set(str(i) for i in deleted_iids)
                        rk_map[self._current_skp_id] = [
                            r for r in rk_map[self._current_skp_id]
                            if str(r[5]) not in deleted_set
                        ]
                        app.write_json(self.rk_cache_file, {"rk_map": rk_map})
                except Exception as ex:
                    self._log(f"⚠️ Gagal update cache RK: {ex}")

            remaining = len(self.tree.get_children())
            self.lbl_info.configure(text=f"Total RK: {remaining}")

            if self._on_rk_deleted_callback:
                self._on_rk_deleted_callback()
            else:
                self.reload_rk()

        self.btn_delete.configure(state="disabled", text="Hapus...")
        self.execute_api_delete(
            endpoint_alias="rk_del",
            name_col="rencanakinerja",
            iids=iids,
            callback_after_success=_on_success
        )

    # ── Tree helpers ───────────────────────────────────────────────
    def _looks_like_capaian(self, value):
        try:
            int(str(value).strip())
            return True
        except Exception:
            return False

    def _normalize_row_order(self, row):
        if len(row) < 6 or self._looks_like_capaian(row[1]):
            return row
        return (row[0], row[4], row[3], row[2], row[1], row[5])

    def _fill_tree(self, rows):
        """rows: list of (no, capaian, rencanakinerja, tim, jenis, rkid)"""
        # slice element 1 to 4 -> (capaian, rk, tim, jenis)
        self.fill_tree_data(
            rows, 
            id_extractor=lambda r: str(r[5]) if r[5] else None, 
            start_col_index=1
        )
