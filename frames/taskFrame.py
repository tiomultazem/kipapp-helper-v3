import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
import threading
import openpyxl
import csv
import io
import re
import requests
from datetime import date, datetime, time, timedelta
from openpyxl.utils.datetime import from_excel
from . import app


TASK_ACCENT = ("thing ",)


from .baseFrame import BaseTableFrame

DATE_FORMATS = (
    "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d",
    "%d.%m.%Y", "%d %m %Y", "%Y.%m.%d", "%m/%d/%Y",
    "%Y%m%d", "%d%m%Y", "%d %b %Y", "%d %B %Y",
    "%b %d %Y", "%B %d %Y", "%Y %b %d", "%Y %B %d",
    "%d %b", "%d %B", "%b %d", "%B %d"
)
TIME_FORMATS = (
    "%H:%M", "%H.%M", "%H:%M:%S", "%H.%M.%S", "%I:%M %p", "%I.%M %p"
)
CHECK_EMPTY = "\u2610"
CHECKED = "\u2611"
IMPORT_MODES = ("Excel", "Spreadsheet")
MONTH_ALIASES = {
    "jan": 1, "january": 1, "januari": 1,
    "feb": 2, "february": 2, "februari": 2,
    "mar": 3, "march": 3, "maret": 3, "mrt": 3,
    "apr": 4, "april": 4,
    "may": 5, "mei": 5,
    "jun": 6, "june": 6, "juni": 6,
    "jul": 7, "july": 7, "juli": 7,
    "aug": 8, "august": 8, "agu": 8, "agt": 8, "agustus": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10, "okt": 10, "oktober": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12, "des": 12, "desember": 12,
}
NUMERIC_DATE_FORMATS = (
    "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d",
    "%d.%m.%Y", "%d %m %Y", "%Y.%m.%d", "%m/%d/%Y",
    "%Y%m%d", "%d%m%Y", "%Y %m %d", "%m %d %Y",
    "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S",
    "%d-%m-%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S",
)
PARTIAL_DATE_FORMATS = (
    "%d %m", "%d-%m", "%d/%m", "%d.%m", "%d%m",
    "%m %d", "%m-%d", "%m/%d", "%m.%d",
)

class TaskFrame(BaseTableFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.skp_frame = None
        self.rk_frame = None

        self._task_data = []       # list of row tuples
        self._rk_id_map = {}       # iid -> rkid (mapping hasil Ubah RK)

        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent", height=40)
        top.pack(fill="x", padx=8, pady=(8, 4))
        top.pack_propagate(False)

        saved_import_mode = self._get_saved_import_mode()
        self.import_mode = tk.StringVar(value=saved_import_mode)

        self.entry_spreadsheet = ctk.CTkEntry(
            top,
            width=240,
            placeholder_text="Paste link spreadsheet"
        )

        self.import_button_wrap = ctk.CTkFrame(top, fg_color="transparent")
        self.import_button_wrap.pack(side="left")

        self.btn_impor = ctk.CTkButton(
            self.import_button_wrap, text="Impor Excel", width=116,
            corner_radius=6,
            font=ctk.CTkFont(size=13),
            command=self._run_import
        )
        self.btn_impor.pack(side="left")

        self.btn_import_dropdown = ctk.CTkButton(
            self.import_button_wrap, text="\u25be", width=28,
            corner_radius=6,
            font=ctk.CTkFont(size=13),
            command=self._show_import_menu
        )
        self.btn_import_dropdown.pack(side="left", padx=(0, 0))

        self.import_menu = tk.Menu(self, tearoff=0)
        self.import_menu.add_command(label="Impor Excel", command=lambda: self._set_import_mode("Excel"))
        self.import_menu.add_command(label="Impor Spreadsheet", command=lambda: self._set_import_mode("Spreadsheet"))

        self._on_import_mode_changed(saved_import_mode, save=False)

        self.btn_ubah_rk = ctk.CTkButton(
            top, text="Ubah RK", width=100,
            font=ctk.CTkFont(size=13),
            fg_color="#f39c12",
            hover_color="#e67e22",
            command=self._ubah_rk
        )
        # Hidden initially

        self.btn_entri = ctk.CTkButton(
            top, text="Entri", width=100,
            font=ctk.CTkFont(size=13),
            fg_color="#2980b9",
            hover_color="#3498db",
            command=self._mulai_entri
        )
        # Hidden initially

        # Info row with delete button and counter
        self.setup_info_row(
            parent_frame=self,
            info_default_text="Belum ada file kegiatan diimpor.",
            delete_cmd=self._delete_checked_local,
            clear_cmd=self._hapus_tabel
        )

        self.table_wrap = ctk.CTkFrame(self, height=300)
        self.table_wrap.pack_propagate(False)

        self.tree = None

    def _show_import_menu(self):
        x = self.btn_import_dropdown.winfo_rootx()
        y = self.btn_import_dropdown.winfo_rooty() + self.btn_import_dropdown.winfo_height()
        try:
            self.import_menu.tk_popup(x, y)
        finally:
            self.import_menu.grab_release()

    def _get_saved_import_mode(self):
        mode = app.get_config().get("ui", {}).get("task", {}).get("import_mode", "Excel")
        return mode if mode in IMPORT_MODES else "Excel"

    def _save_import_mode(self, mode):
        cfg = app.get_config().copy()
        ui_cfg = cfg.get("ui", {}).copy()
        task_cfg = ui_cfg.get("task", {}).copy()
        task_cfg["import_mode"] = mode
        ui_cfg["task"] = task_cfg
        cfg["ui"] = ui_cfg
        app.write_json(app.CONFIG_FILE, cfg)
        app._config_cache = cfg

    def _set_import_mode(self, mode):
        self.import_mode.set(mode)
        self._on_import_mode_changed(mode)

    def _on_import_mode_changed(self, mode, save=True):
        if mode not in IMPORT_MODES:
            mode = "Excel"
            self.import_mode.set(mode)
        if mode == "Spreadsheet":
            self.btn_impor.configure(text="Impor Spreadsheet", width=138)
            if not self.entry_spreadsheet.winfo_ismapped():
                self.entry_spreadsheet.pack(side="left", padx=(0, 6), before=self.import_button_wrap)
        else:
            self.btn_impor.configure(text="Impor Excel", width=116)
            self.entry_spreadsheet.pack_forget()
        if save:
            self._save_import_mode(mode)

    def _run_import(self):
        if self.import_mode.get() == "Spreadsheet":
            self._impor_spreadsheet()
        else:
            self._impor_xlsx()

    def _is_blank(self, value):
        return value is None or str(value).strip() == "" or str(value).strip().lower() == "none"

    def _default_import_year(self):
        label = getattr(self.skp_frame, "_selected_label", "") if self.skp_frame else ""
        match = re.search(r"\b(19\d{2}|20\d{2})\b", str(label))
        if match:
            return int(match.group(1))
        return date.today().year

    def _clean_date_text(self, text):
        text = str(text).strip()
        text = re.sub(r"([A-Za-z])\.", r"\1", text)
        text = text.replace(",", " ")
        text = text.replace("\\", "/")
        text = re.sub(r"(?<=\d)T(?=\d)", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(
            r"\s+\d{1,2}[:.]\d{2}(?::\d{2}(?:\.\d+)?)?(\s*[AP]M|Z|[+-]\d{2}:?\d{2})?$",
            "",
            text,
            flags=re.IGNORECASE,
        )
        return text.strip()

    def _replace_month_names(self, text):
        aliases = sorted(MONTH_ALIASES, key=len, reverse=True)
        pattern = r"\b(" + "|".join(re.escape(alias) for alias in aliases) + r")\b"

        def repl(match):
            return f"{MONTH_ALIASES[match.group(1).lower()]:02d}"

        return re.sub(pattern, repl, text, flags=re.IGNORECASE)

    def _normalize_date(self, value, row_num, col_name, required=False):
        if self._is_blank(value):
            if required:
                raise ValueError(f"Baris {row_num}: {col_name} wajib diisi.")
            return ""

        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        if isinstance(value, date):
            return value.strftime("%Y-%m-%d")
        if isinstance(value, (int, float)):
            try:
                return from_excel(value).strftime("%Y-%m-%d")
            except Exception:
                pass

        text = self._clean_date_text(value)
        normalized_text = self._replace_month_names(text)
        candidates = [text]
        if normalized_text != text:
            candidates.append(normalized_text)

        for candidate in candidates:
            for fmt in NUMERIC_DATE_FORMATS:
                try:
                    return datetime.strptime(candidate, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    pass

        year = self._default_import_year()
        for candidate in candidates:
            for fmt in PARTIAL_DATE_FORMATS:
                try:
                    return datetime.strptime(f"{candidate} {year}", f"{fmt} %Y").strftime("%Y-%m-%d")
                except ValueError:
                    pass

        supported = ", ".join(DATE_FORMATS)
        raise ValueError(f"Baris {row_num}: {col_name} tidak valid ({value}). Format didukung: {supported}.")

    def _normalize_time(self, value, row_num, col_name):
        if self._is_blank(value):
            return ""

        if isinstance(value, datetime):
            return value.strftime("%H:%M")
        if isinstance(value, time):
            return value.strftime("%H:%M")
        if isinstance(value, timedelta):
            total_minutes = int(value.total_seconds() // 60)
            return f"{(total_minutes // 60) % 24:02d}:{total_minutes % 60:02d}"
        if isinstance(value, (int, float)):
            if 0 <= value < 1:
                total_minutes = int(round(value * 24 * 60))
                return f"{(total_minutes // 60) % 24:02d}:{total_minutes % 60:02d}"
            if 0 <= value < 24:
                hours = int(value)
                minutes = int(round((value - hours) * 60))
                return f"{hours:02d}:{minutes:02d}"
            if 100 <= value <= 2359:
                text = str(int(value)).zfill(4)
                return f"{text[:-2]}:{text[-2:]}"

        text = str(value).strip()
        if " " in text and ":" in text:
            parts = text.split()
            text = parts[1] if len(parts) > 1 and "-" in parts[0] else parts[0]

        if text.isdigit():
            if len(text) <= 2 and 0 <= int(text) < 24:
                return f"{int(text):02d}:00"
            if len(text) in (3, 4):
                text = text.zfill(4)
                return f"{text[:-2]}:{text[-2:]}"

        for fmt in TIME_FORMATS:
            try:
                return datetime.strptime(text, fmt).strftime("%H:%M")
            except ValueError:
                pass

        supported = ", ".join(TIME_FORMATS)
        raise ValueError(f"Baris {row_num}: {col_name} tidak valid ({value}). Format didukung: {supported}.")

    def _normalize_excel_row(self, row, row_num):
        values = list(row)
        values[0] = self._normalize_date(values[0], row_num, "Start Date", required=True)
        values[1] = self._normalize_date(values[1], row_num, "End Date")
        values[2] = self._normalize_time(values[2], row_num, "Jam Mulai")
        values[3] = self._normalize_time(values[3], row_num, "Jam Selesai")
        return tuple(str(v) if v is not None else "" for v in values)

    def _normalize_import_rows(self, rows_iter):
        header_row = next(rows_iter, None)
        if not header_row:
            raise ValueError("Data kosong.")

        if len(header_row) != 10:
            raise ValueError(f"Format salah! Harus 10 kolom, ditemukan {len(header_row)} kolom.")

        data = []
        for row_idx, row in enumerate(rows_iter, start=2):
            if any(not self._is_blank(v) for v in row):
                row = tuple(row)
                if len(row) != 10:
                    raise ValueError(f"Baris {row_idx}: Harus 10 kolom, ditemukan {len(row)} kolom.")
                data.append(self._normalize_excel_row(row, row_idx))
        return data

    def _finish_import(self, data, source_name):
        self._task_data = data
        self._build_tree()
        self._fill_tree(data)

        self.import_button_wrap.pack_forget()
        self.entry_spreadsheet.pack_forget()
        self.btn_ubah_rk.pack(side="left", padx=(8, 0))
        self.btn_entri.pack(side="left", padx=(8, 0))
        
        self.lbl_info.configure(
            text=f"Total kegiatan siap entri: {len(data)}",
            text_color="green" if data else "orange"
        )
        self.lbl_hapus.pack(side="left", padx=(8, 0))
        self._log(f"OK Berhasil impor {len(data)} baris kegiatan.")
        self._log(f"Sumber {source_name} telah diimpor.")

    def _impor_xlsx(self):
        filepath = filedialog.askopenfilename(
            title="Pilih file kegiatan (.xlsx)",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not filepath: return

        wb = None
        try:
            wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
            ws = wb.active
            data = self._normalize_import_rows(ws.iter_rows(values_only=True))
            filename = filepath.replace("\\", "/").split("/")[-1]
            self._finish_import(data, filename)

        except Exception as ex:
            self._log(f"ERROR Gagal impor Excel: {ex}")
        finally:
            if wb:
                wb.close()

    def _spreadsheet_csv_url(self, url):
        url = url.strip()
        if "output=csv" in url or "format=csv" in url:
            return url

        match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
        if not match:
            return url

        sheet_id = match.group(1)
        gid_match = re.search(r"(?:gid=|#gid=)(\d+)", url)
        gid = gid_match.group(1) if gid_match else "0"
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    def _impor_spreadsheet(self):
        raw_url = self.entry_spreadsheet.get().strip()
        if not raw_url:
            self._log("ERROR Link spreadsheet masih kosong.")
            return

        try:
            csv_url = self._spreadsheet_csv_url(raw_url)
            self._log("Mengambil data spreadsheet...")
            response = requests.get(csv_url, timeout=30)
            response.raise_for_status()

            rows = csv.reader(io.StringIO(response.text))
            data = self._normalize_import_rows(iter(rows))
            self._finish_import(data, "spreadsheet")

        except Exception as ex:
            self._log(f"ERROR Gagal impor spreadsheet: {ex}")

    def _build_tree(self):
        if self.tree is not None:
            self.tree.destroy()
        for widget in self.table_wrap.winfo_children():
            widget.destroy()

        cols = (
            "check", "no", "tanggal", "tanggalselesai", "jammulai", "jamselesai",
            "rencanakinerja", "kegiatan", "capaian", "progres", "datadukung", "iscapaianskp"
        )
        headings = {
            "check": CHECK_EMPTY, "no": "No.", "tanggal": "Start Date", "tanggalselesai": "End Date",
            "jammulai": "Jam Mulai", "jamselesai": "Jam Selesai", "rencanakinerja": "Rencana Kinerja",
            "kegiatan": "Kegiatan", "capaian": "Capaian", "progres": "Progres",
            "datadukung": "Link Bukti", "iscapaianskp": "Centang"
        }
        widths = {
            "check": (40, "center", False), "no": (50, "center", False),
            "tanggal": (100, "center", False), "tanggalselesai": (100, "center", False),
            "jammulai": (90, "center", False), "jamselesai": (90, "center", False),
            "rencanakinerja": (220, "w", True), "kegiatan": (260, "w", True),
            "capaian": (80, "center", False), "progres": (80, "center", False),
            "datadukung": (180, "w", True), "iscapaianskp": (80, "center", False)
        }

        self.setup_tree(self.table_wrap, cols, headings, widths)

    def _update_delete_button_visibility(self):
        super()._update_delete_button_visibility()
        if self.btn_delete.winfo_ismapped():
            self.btn_ubah_rk.pack_forget()
            self.btn_entri.pack_forget()
        else:
            self.btn_ubah_rk.pack(side="left", padx=(8, 0))
            self.btn_entri.pack(side="left", padx=(8, 0))

    def _fill_tree(self, rows):
        self.fill_tree_data(rows)

    def _ubah_rk(self):
        if not self.rk_frame:
            self._log("ERROR RK Frame belum terhubung.")
            return
        
        rk_list = self.rk_frame.get_rk_list()
        if not rk_list:
            self._log("WARNING Tidak ada data RK tersedia. Pastikan tabel RK sudah terisi.")
            return

        count = 0
        for item_id in self.tree.get_children():
            vals = list(self.tree.item(item_id)["values"])
            # Kolom Rencana Kinerja ada di index ke-6 (0:check, 1:no, 2:tgl, 3:tglselesai, 4:jammulai, 5:jamselesai, 6:rk)
            rk_val = str(vals[6]).strip()
            
            if rk_val.isdigit():
                idx = int(rk_val) - 1
                if 0 <= idx < len(rk_list):
                    rk_obj = rk_list[idx]
                    # Update Treeview visual
                    vals[6] = rk_obj.get("rencanakinerja", "-")
                    self.tree.item(item_id, values=vals)
                    # Simpan rkid untuk proses entri
                    self._rk_id_map[item_id] = rk_obj.get("rkid")
                    count += 1
        
        if count > 0:
            self._log(f"OK Berhasil memetakan {count} Rencana Kinerja.")
        else:
            self._log("WARNING Tidak ada nomor RK yang ditemukan untuk diubah.")

    def _mulai_entri(self):
        if not self.skp_frame or not self.skp_frame.get_active_skp_id():
            self._log("ERROR Belum ada SKP yang dipilih. Pilih periode SKP dulu!")
            return

        confirm = tk.messagebox.askyesno("Konfirmasi Entri", "Mulai proses entri otomatis ke KiPApp?")
        if not confirm: return

        self._log("LOADING Memulai entri kegiatan ke KiPApp...")
        self.btn_entri.configure(state="disabled", text="Entri...")
        threading.Thread(target=self._entri_worker, daemon=True).start()

    def _entri_worker(self):
        from concurrent.futures import ThreadPoolExecutor

        sess = self._get_session()
        if not sess:
            self._log("ERROR Sesi belum tersedia. Login dulu sebelum entri.")
            self.after(0, lambda: self.btn_entri.configure(state="normal", text="Entri"))
            return

        try:
            skp_id_raw = self.skp_frame.get_active_skp_id()
            skp_id = int(skp_id_raw) if skp_id_raw else None
        except:
            skp_id = None

        m_post, u_post = app.get_api_info("kegiatan_post")
        items = self.tree.get_children()
        total = len(items)

        # Helper format.
        def format_val(val, mode="text"):
            if val is None or str(val).strip() == "" or str(val).lower() == "none":
                return None
            if hasattr(val, "strftime"):
                if mode == "date": return val.strftime("%Y-%m-%d")
                if mode == "time": return val.strftime("%H:%M")
            s = str(val).strip()
            if mode == "date" and " " in s: s = s.split(" ")[0]
            if mode == "time" and " " in s: s = s.split(" ")[1]
            if mode == "time" and len(s) > 5: s = s[:5]
            return s

        # Siapkan tasks, lewati item tanpa rkid sebelum masuk thread.
        tasks = []
        for i, item_id in enumerate(items):
            vals = self.tree.item(item_id)["values"]
            rkid = self._rk_id_map.get(item_id)
            kegiatan_text = str(vals[7])[:50]

            if not rkid:
                self._log(f"WARNING [{i+1}/{total}] {kegiatan_text} -> RK belum dipetakan, dilewati.")
                continue

            payload = {
                "skpid":          skp_id,
                "rkid":           rkid,
                "tanggal":        format_val(vals[2], "date"),
                "tanggalselesai": format_val(vals[3], "date"),
                "jammulai":       format_val(vals[4], "time"),
                "jamselesai":     format_val(vals[5], "time"),
                "kegiatan":       str(vals[7]),
                "capaian":        str(vals[8]),
                "progres":        int(float(vals[9])) if str(vals[9]).replace(".", "").replace(",", "").isdigit() else 100,
                "datadukung":     str(vals[10]),
                "iscapaianskp":   1
            }
            tasks.append((i, item_id, kegiatan_text, payload))

        attempted = len(tasks)
        if attempted == 0:
            self._log("WARNING Tidak ada kegiatan valid untuk dientri.")
            self.after(0, lambda: self.btn_entri.configure(state="normal", text="Entri"))
            return

        def process_item(task):
            import time
            i, item_id, kegiatan_text, payload = task
            t0 = time.time()
            try:
                r = sess.request(m_post, u_post, json=payload, timeout=20)
                dur = time.time() - t0
                if r.status_code == 200:
                    res_json = r.json()
                    if res_json.get("status"):
                        return (i, True,  item_id, f"OK [{i+1}/{total}] {kegiatan_text} -> Sukses ({dur:.1f}s).")
                    else:
                        msg = res_json.get("message") or res_json.get("error") or "Status False"
                        return (i, False, None, f"ERROR [{i+1}/{total}] {kegiatan_text} -> {msg} ({dur:.1f}s)")
                else:
                    return (i, False, None, f"ERROR [{i+1}/{total}] {kegiatan_text} -> Server Error {r.status_code} ({dur:.1f}s)")
            except Exception as e:
                dur = time.time() - t0
                return (i, False, None, f"ERROR [{i+1}/{total}] {kegiatan_text} -> Error: {e} ({dur:.1f}s)")

        # Dispatch paralel, kumpulkan hasil terurut.
        import time
        t_total = time.time()
        max_workers = app.get_config().get("entri", {}).get("max_workers", 3)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(process_item, tasks))

        # Log semua hasil dalam urutan input
        success_count = 0
        for _, ok, item_id, msg in results:
            self._log(msg)
            if ok:
                success_count += 1
                self.after(0, lambda iid=item_id: self._hapus_baris_sukses(iid))

        total_dur = time.time() - t_total
        if success_count == attempted:
            self._log(f"SUKSES! Seluruh {attempted} kegiatan dientri dalam {total_dur:.1f}s.")
        else:
            self._log(f"Selesai. {success_count}/{attempted} berhasil dalam {total_dur:.1f}s.")
        self.after(0, lambda: self.btn_entri.configure(state="normal", text="Entri"))

        if success_count > 0:
            self.after(500, lambda: self.skp_frame.reload_all(force_related=True))


    def _hapus_baris_sukses(self, item_id):
        """Hapus satu baris dari Treeview dan memori setelah sukses entri."""
        if self.tree.exists(item_id):
            idx = int(item_id)
            # Karena item_id adalah index asli, kita hapus saja
            self.tree.delete(item_id)
            if item_id in self._rk_id_map:
                del self._rk_id_map[item_id]
            
            # Update counter label
            remaining = len(self.tree.get_children())
            self.lbl_info.configure(text=f"Total kegiatan siap entri: {remaining}")
            
            # Update Cache JSON (Opsional, tapi sebaiknya disinkronkan)
            # Untuk simplifikasi, kita biarkan saja dulu karena _task_data akan di-refresh jika impor ulang

    def _delete_checked_local(self):
        if not self.tree: return
        checked = [i for i in self.tree.get_children() if self.tree.set(i, "check") == CHECKED]
        if not checked: return
        if tk.messagebox.askyesno("Hapus", f"Hapus {len(checked)} baris terpilih?"):
            for i in checked:
                self.tree.delete(i)
                if i in self._rk_id_map: del self._rk_id_map[i]
            self._update_delete_button_visibility()
            self.lbl_info.configure(text=f"Total kegiatan siap entri: {len(self.tree.get_children())}")

    def _hapus_tabel(self):
        self._clear_tree()
        self.btn_ubah_rk.pack_forget()
        self.btn_entri.pack_forget()
        self.import_button_wrap.pack(side="left")
        self._on_import_mode_changed(self.import_mode.get())
        self._rk_id_map = {}
        self.lbl_info.configure(text="Belum ada file kegiatan diimpor.", text_color="gray")
