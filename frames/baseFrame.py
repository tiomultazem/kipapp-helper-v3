import customtkinter as ctk
from tkinter import ttk
from . import app


class BaseTableFrame(ctk.CTkFrame):
    """
    Base class untuk frame yang berisi tabel (Treeview) dengan fitur checklist,
    shift-click range, hapus massal, log, dan integrasi session.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self._session_getter = None
        self._log_fn = None
        self._last_checked_iid = None
        
        # UI Elements yang akan di-set oleh child
        self.tree = None
        self.table_wrap = None
        self.info_row = None
        self.btn_delete = None
        self.lbl_info = None
        self.lbl_hapus = None

    # ── Basic Services ────────────────────────────────────────────────
    def _log(self, msg):
        if self._log_fn:
            self._log_fn(msg)

    def _get_session(self):
        return self._session_getter() if self._session_getter else None

    # ── Shared UI Builders ────────────────────────────────────────────
    def setup_info_row(self, parent_frame, info_default_text, delete_cmd=None, clear_cmd=None):
        """Membuat deretan info: [Hapus] [Info Teks] [Hapus Tampilan]"""
        self.info_row = ctk.CTkFrame(parent_frame, fg_color="transparent", height=32)
        self.info_row.pack(fill="x", padx=8, pady=(0, 4))
        self.info_row.pack_propagate(False)

        self.btn_delete = ctk.CTkButton(
            self.info_row, text="Hapus(0)", width=80, height=26,
            fg_color="#c0392b", hover_color="#e74c3c",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=delete_cmd
        )

        self.lbl_info = ctk.CTkLabel(
            self.info_row, text=info_default_text, text_color="gray",
            font=ctk.CTkFont(size=13)
        )
        self.lbl_info.pack(side="left")

        if clear_cmd:
            self.lbl_hapus = ctk.CTkLabel(
                self.info_row, text="Hapus tampilan", text_color="red",
                font=ctk.CTkFont(size=13), cursor="hand2"
            )
            self.lbl_hapus.bind("<Button-1>", lambda e: clear_cmd())
            
        return self.info_row

    # ── Treeview Builder ──────────────────────────────────────────────
    def setup_tree(self, parent_frame, cols, headings, widths, height=8):
        """Membuat treeview dan scrollbar, mereturn tree object"""
        self.table_wrap = parent_frame
        
        self.tree = ttk.Treeview(self.table_wrap, columns=cols, show="headings", height=height)

        for col in cols:
            self.tree.heading(col, text=headings.get(col, col))
            if col in widths:
                w, a, s = widths[col]
                self.tree.column(col, width=w, anchor=a, stretch=s)

        # Jika ada kolom check, bind header untuk toggle all
        if "check" in cols:
            self.tree.heading("check", command=self._toggle_check_all)

        yscroll = ttk.Scrollbar(self.table_wrap, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(self.table_wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

        self.table_wrap.grid_rowconfigure(0, weight=1)
        self.table_wrap.grid_columnconfigure(0, weight=1)

        app.bind_treeview_scroll(self.tree)
        app.bind_treeview_sort(self.tree)
        app.bind_treeview_hover(self.tree)

        self.tree.bind("<Button-1>", self._on_tree_click)
        return self.tree

    # ── Treeview Helpers ──────────────────────────────────────────────
    def _clear_tree(self):
        if not self.tree: return
        for item in self.tree.get_children():
            self.tree.delete(item)
        if self.table_wrap:
            self.table_wrap.pack_forget()
        if self.btn_delete:
            self.btn_delete.pack_forget()
        if self.lbl_hapus:
            self.lbl_hapus.pack_forget()
        
        # Reset check header
        try:
            self.tree.heading("check", text="☐")
        except:
            pass

    def fill_tree_data(self, rows, id_extractor=None, start_col_index=0):
        """
        Fungsi standar mengisi treeview. 
        Asumsi kolom 0 = check, kolom 1 = no.
        Data dari rows akan dimasukkan mulai dari start_col_index (misal index list data asli).
        """
        self._clear_tree()
        if not rows: return
        
        if self.table_wrap:
            self.table_wrap.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        if self.lbl_hapus:
            self.lbl_hapus.pack(side="left", padx=(8, 0))
            
        for i, row in enumerate(rows):
            iid = id_extractor(row) if id_extractor else str(i)
            # Potong row menggunakan start_col_index
            data_cols = tuple(row[start_col_index:]) if start_col_index > 0 else tuple(row)
            
            display_vals = ("☐", str(i + 1)) + data_cols
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", "end", iid=iid, values=display_vals, tags=(tag,))

    def update_theme(self, mode):
        if self.tree:
            app.update_treeview_tags(self.tree, mode)

    # ── Checkbox Logic ────────────────────────────────────────────────
    def _can_modify(self):
        """Hook: bisa di-override oleh child class jika ada kondisi tertentu (misal SKP Dinilai)"""
        return True

    def _on_tree_click(self, event):
        if not self._can_modify(): return
        
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            col = self.tree.identify_column(event.x)
            if col == "#1":  # Asumsi kolom pertama selalu check
                iid = self.tree.identify_row(event.y)
                if iid:
                    cur = self.tree.set(iid, "check")
                    new_val = "☑" if cur == "☐" else "☐"
                    self.tree.set(iid, "check", new_val)

                    # Shift-click range support
                    if getattr(event, "state", 0) & 0x0001 and self._last_checked_iid:
                        children = self.tree.get_children()
                        try:
                            idx1 = children.index(self._last_checked_iid)
                            idx2 = children.index(iid)
                            start = min(idx1, idx2)
                            end = max(idx1, idx2)
                            for child in children[start:end + 1]:
                                self.tree.set(child, "check", new_val)
                        except ValueError:
                            pass

                    self._last_checked_iid = iid
                    self._update_delete_button_visibility()
                    return "break"

    def _toggle_check_all(self):
        if not self._can_modify(): return

        cur = self.tree.heading("check")["text"]
        new_val = "☑" if cur == "☐" else "☐"
        self.tree.heading("check", text=new_val)
        
        for iid in self.tree.get_children():
            self.tree.set(iid, "check", new_val)
            
        self._update_delete_button_visibility()

    def _update_delete_button_visibility(self):
        if not self.tree or not self.btn_delete: return
        
        if not self._can_modify():
            self.btn_delete.pack_forget()
            return
            
        checked_count = sum(1 for iid in self.tree.get_children() if self.tree.set(iid, "check") == "☑")
        
        if checked_count > 0:
            self.btn_delete.configure(text=f"Hapus({checked_count})")
            if self.lbl_info:
                self.btn_delete.pack(side="left", padx=(0, 8), before=self.lbl_info)
            else:
                self.btn_delete.pack(side="left", padx=(0, 8))
        else:
            self.btn_delete.pack_forget()

    # ── API Server Delete Logic ───────────────────────────────────────
    def execute_api_delete(self, endpoint_alias, name_col, iids, callback_after_success=None):
        """
        Fungsi generik untuk memproses API DELETE secara paralel ke server.
        """
        sess = self._get_session()
        if not sess:
            self.after(0, lambda: self.btn_delete.configure(state="normal"))
            return

        m_del, u_del = app.get_api_info(endpoint_alias)
        total = len(iids)
        success_iids = []
        fail_count = 0

        for i, iid in enumerate(iids):
            # Coba ambil nama baris jika index column disediakan
            try:
                item_name = self.tree.set(iid, name_col)[:50]
            except:
                item_name = f"Item-{iid}"

            try:
                r = sess.request(m_del, u_del, json={"id": iid}, timeout=15)
                if r.status_code == 200:
                    res = r.json()
                    if res.get("status"):
                        success_iids.append(iid)
                        self._log(f"✅ [{i+1}/{total}] {item_name} → Berhasil dihapus.")
                        self.after(0, lambda iid_=iid: self.tree.exists(iid_) and self.tree.delete(iid_))
                    else:
                        fail_count += 1
                        self._log(f"❌ [{i+1}/{total}] {item_name} → {res.get('message', 'Gagal')}")
                else:
                    fail_count += 1
                    self._log(f"❌ [{i+1}/{total}] {item_name} → Server Error {r.status_code}")
            except Exception as e:
                fail_count += 1
                self._log(f"❌ [{i+1}/{total}] {item_name} → Error: {e}")

        success_count = len(success_iids)
        self._log(f"🏁 Selesai. Berhasil: {success_count}, Gagal: {fail_count}.")
        
        self.after(0, lambda: self.btn_delete.configure(state="normal"))
        self.after(0, self._update_delete_button_visibility)
        
        if success_count > 0 and callback_after_success:
            self.after(0, lambda: callback_after_success(success_iids))
