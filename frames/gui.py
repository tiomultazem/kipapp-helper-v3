import customtkinter as ctk
import os
import sys
from . import app
from .skpFrame   import SkpFrame
from .rkFrame    import RkFrame
from .entriFrame import EntriFrame
from .logFrame   import LogFrame
from .taskFrame  import TaskFrame
from .app import restart_app, BASE_DIR
from .update import check_update_background, get_local_version

def _get_ui_config():
    return app.get_config().get("ui", {})


def _save_ui_config(ui_config):
    cfg = app.get_config().copy()
    cfg["ui"] = ui_config
    app.write_json(app.CONFIG_FILE, cfg)
    app._config_cache = cfg


ctk.set_appearance_mode(_get_ui_config().get("theme", "dark"))
ctk.set_default_color_theme("green")

ARROW_UP = "\u25b2"
ARROW_DOWN = "\u25bc"
COPYRIGHT = "\u00a9"
HEART = "\u2764"
EM_DASH = "\u2014"


class Gui(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.ui_config = _get_ui_config()
        self.iconbitmap(os.path.join(BASE_DIR, "assets", "favicon.ico"))
        self.title("KiPApp Helper v3")
        self.geometry("900x700")
        self.resizable(False, True)

        self._normal_height = 750
        self._collapsed_row_height = 48
        self._update_treeview_style(ctk.get_appearance_mode().lower())

        # Build footer duluan agar selalu menempel di bawah (terhindar dari cutoff)
        self._build_footer()
        self._build_body()
        
        # Panggil cek update di background setelah aplikasi terbuka
        self.after(2000, lambda: check_update_background(self, mode="auto"))

    # Body
    def _build_body(self):
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(padx=12, pady=8, fill="both", expand=True)

        self.grid_container = ctk.CTkFrame(self.body, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True)
        self.grid_container.columnconfigure(0, weight=1, uniform="col")
        self.grid_container.columnconfigure(1, weight=1, uniform="col")
        self.grid_container.rowconfigure(0, weight=1)
        self.grid_container.rowconfigure(1, weight=1)

        # Row 0: SKP (left) + Task (right)
        self.skp_wrapper = self._make_collapsible(self.grid_container, "SKP", SkpFrame)
        self.skp_wrapper["container"].grid(row=0, column=0, sticky="nsew", padx=(0, 4), pady=(0, 4))

        self.task_wrapper = self._make_collapsible(self.grid_container, "Kegiatan", TaskFrame)
        self.task_wrapper["container"].grid(row=0, column=1, sticky="nsew", padx=(4, 0), pady=(0, 4))

        # Row 1: RK (left) + Right Panel (Entri + Log)
        self.rk_wrapper = self._make_collapsible(self.grid_container, "Rencana Kinerja", RkFrame)
        self.rk_wrapper["container"].grid(row=1, column=0, sticky="nsew", padx=(0, 4), pady=(0, 8))

        self.right_panel = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.right_panel.grid(row=1, column=1, sticky="nsew", padx=(4, 0), pady=(0, 8))
        self.right_panel.rowconfigure(0, weight=0)
        self.right_panel.rowconfigure(1, weight=1)
        self.right_panel.columnconfigure(0, weight=1)

        self.entri_wrapper = self._make_collapsible(self.right_panel, "SSO", EntriFrame)
        self.entri_wrapper["container"].grid(row=0, column=0, sticky="nsew", pady=(0, 4))
        self.entri_frame = self.entri_wrapper["frame"]

        self.log_wrapper = self._make_collapsible(self.right_panel, "Log", LogFrame)
        self.log_wrapper["container"].grid(row=1, column=0, sticky="nsew")

        self.log_ref = self.log_wrapper["frame"]

        # Wire up dependencies
        self.skp_frame = self.skp_wrapper["frame"]
        self.rk_frame = self.rk_wrapper["frame"]
        self.task_frame = self.task_wrapper["frame"]

        self.entri_frame._log_fn = self.master_log
        self.skp_frame._log_fn = self.master_log
        self.skp_frame._session_getter = lambda: self.entri_frame._session

        self.rk_frame._log_fn = self.master_log
        self.rk_frame._session_getter = lambda: self.entri_frame._session

        self.task_frame._log_fn = self.master_log
        self.task_frame._session_getter = lambda: self.entri_frame._session
        
        self.task_frame.skp_frame = self.skp_frame
        self.task_frame.rk_frame = self.rk_frame

        def on_skp_changed(skp_id):
            if hasattr(self.rk_frame, "load_rk"):
                force = bool(getattr(self.skp_frame, "_force_related_reload", False))
                self.skp_frame._force_related_reload = False
                self.rk_frame.load_rk(skp_id, force=force)

        self.skp_frame._on_skp_changed_callback = on_skp_changed

        def on_rk_deleted():
            self.skp_frame.reload_all()

        self.rk_frame._on_rk_deleted_callback = on_rk_deleted

        # Saat session siap (resume/login), trigger reload agar RK tidak kena race condition
        def on_session_ready():
            self.skp_frame.load_periode()

        self.entri_frame._on_session_ready = on_session_ready
        self._refresh_layout_weights()

    def master_log(self, msg):
        if hasattr(self, "log_ref") and hasattr(self.log_ref, "log"):
            self.log_ref.log(msg)

    def _save_ui_state(self):
        _save_ui_config(self.ui_config)

    def _frame_state_key(self, FrameClass):
        return FrameClass.__name__.replace("Frame", "").lower()

    def _get_frame_expanded(self, key):
        frames = self.ui_config.get("frames", {})
        return frames.get(key, {}).get("expanded", True)

    def _set_frame_expanded(self, key, expanded):
        frames = self.ui_config.setdefault("frames", {})
        frames.setdefault(key, {})["expanded"] = expanded
        self._save_ui_state()

    def _refresh_layout_weights(self):
        if not hasattr(self, "grid_container"):
            return

        top_expanded = (
            getattr(self, "skp_wrapper", {}).get("expanded", True)
            or getattr(self, "task_wrapper", {}).get("expanded", True)
        )
        bottom_expanded = (
            getattr(self, "rk_wrapper", {}).get("expanded", True)
            or getattr(self, "entri_wrapper", {}).get("expanded", True)
            or getattr(self, "log_wrapper", {}).get("expanded", True)
        )
        self.grid_container.rowconfigure(0, weight=1 if top_expanded else 0)
        self.grid_container.rowconfigure(1, weight=1 if bottom_expanded else 0)

        if hasattr(self, "right_panel"):
            self.right_panel.rowconfigure(0, weight=1 if self.entri_wrapper["expanded"] else 0)
            self.right_panel.rowconfigure(1, weight=1 if self.log_wrapper["expanded"] else 0)

        self._resize_for_collapsed_rows(top_expanded, bottom_expanded)

    def _resize_for_collapsed_rows(self, top_expanded, bottom_expanded):
        collapsed_rows = 0
        if not top_expanded:
            collapsed_rows += 1
        if not bottom_expanded:
            collapsed_rows += 1

        row_height = max((self._normal_height - 120) // 2, self._collapsed_row_height)
        new_height = self._normal_height - (collapsed_rows * (row_height - self._collapsed_row_height))
        new_height = max(260, new_height)
        self.geometry(f"1000x{new_height}")

    def _make_collapsible(self, parent, title, FrameClass):
        state_key = self._frame_state_key(FrameClass)
        container = ctk.CTkFrame(parent)
        
        # Header (Title Bar)
        title_bar = ctk.CTkFrame(container, fg_color=("gray85", "gray25"), height=32, corner_radius=6, cursor="hand2")
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        label = ctk.CTkLabel(title_bar, text=title,
                             font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
        label.pack(side="left", padx=8)

        arrow_btn = ctk.CTkLabel(
            title_bar, text=ARROW_UP, width=28,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        arrow_btn.pack(side="right", padx=10)

        # Content
        frame_content = FrameClass(container)
        is_expanded = self._get_frame_expanded(state_key)
        if is_expanded:
            frame_content.pack(fill="both", expand=True)
        else:
            arrow_btn.configure(text=ARROW_DOWN)
            container.configure(height=32)
            container.grid_propagate(False)

        ref = {"frame": frame_content, "btn": arrow_btn,
               "container": container, "expanded": is_expanded}

        def toggle_collapse(event=None):
            if ref["expanded"]:
                frame_content.pack_forget()
                arrow_btn.configure(text=ARROW_DOWN)
                container.configure(height=32)
                container.grid_propagate(False)
                ref["expanded"] = False
                self._set_frame_expanded(state_key, False)
                self._refresh_layout_weights()
            else:
                container.grid_propagate(True)
                frame_content.pack(fill="both", expand=True)
                arrow_btn.configure(text=ARROW_UP)
                ref["expanded"] = True
                self._set_frame_expanded(state_key, True)
                self._refresh_layout_weights()

        # Bind click to header and labels
        title_bar.bind("<Button-1>", toggle_collapse)
        label.bind("<Button-1>", toggle_collapse)
        arrow_btn.bind("<Button-1>", toggle_collapse)

        return ref

    # Footer
    def _build_footer(self):
        # Pack dari bawah ke atas
        ff = ctk.CTkFrame(self, fg_color="transparent")
        ff.pack(side="bottom", pady=(4, 8))
        ctk.CTkFrame(self, height=1, fg_color=("gray70", "gray30")).pack(side="bottom", fill="x", padx=12)

        def make_label(text, cursor=None, color="gray"):
            return ctk.CTkLabel(ff, text=text, font=ctk.CTkFont(size=10),
                                text_color=color, cursor=cursor or "")

        local_version = get_local_version()
        lbl_version = make_label(f"v{local_version} ", cursor="hand2", color="#3a7ebf")
        lbl_version.pack(side="left")
        lbl_version.bind("<Button-1>", lambda e: check_update_background(self, mode="manual"))

        dev_restart = bool(app.get_config().get("dev_restart", False))
        lbl_c = make_label(COPYRIGHT, cursor="hand2" if dev_restart else None)
        lbl_c.pack(side="left")
        if dev_restart:
            lbl_c.bind("<Button-1>", lambda e: restart_app())

        make_label(" 2026 Made with ").pack(side="left")

        lbl_heart = make_label(HEART, cursor="hand2", color="#e74c3c")
        lbl_heart.pack(side="left")
        lbl_heart.bind("<Button-1>", lambda e: self._toggle_theme())

        make_label("  Gilang Wahyu Prasetyo").pack(side="left")

        if app.DEV_MODE:
            lbl_strip = make_label(f" {EM_DASH} ", cursor="hand2")
            lbl_strip.pack(side="left")
            lbl_strip.bind("<Button-1>", lambda e: self._wipe_session())
        else:
            make_label(f" {EM_DASH} ").pack(side="left")

        make_label("BPS Kabupaten Tabalong").pack(side="left")

    def _wipe_session(self):
        from .app import wipe_session
        wipe_session(self.master_log)

    def _update_treeview_style(self, mode):
        from tkinter import ttk
        style = ttk.Style()
        style.theme_use("default")
        
        if mode == "dark":
            bg_color = "#2b2b2b"
            fg_color = "#dce4ee"
            field_bg = "#2b2b2b"
            sel_bg = "#1f538d"
            head_bg = "#1f1f1f"
            head_fg = "#dce4ee"
        else:
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            field_bg = "#ffffff"
            sel_bg = "#3a7ebf"
            head_bg = "#e0e0e0"
            head_fg = "#000000"

        style.configure("Treeview",
                        background=bg_color,
                        foreground=fg_color,
                        fieldbackground=field_bg,
                        borderwidth=0,
                        rowheight=30,
                        font=("Arial", 11))
                        
        style.map("Treeview",
                  background=[("selected", sel_bg)])
                  
        style.configure("Treeview.Heading",
                        background=head_bg,
                        foreground=head_fg,
                        relief="flat",
                        font=("Arial", 12, "bold"))
                        
        style.map("Treeview.Heading",
                  background=[("active", sel_bg)])

    def _toggle_theme(self):
        hwnds_to_freeze = []
        if sys.platform == "win32":
            import ctypes
            try:
                hwnds_to_freeze.append(int(self.wm_frame(), 16))
                for hwnd in hwnds_to_freeze:
                    ctypes.windll.user32.SendMessageW(hwnd, 11, 0, 0)
            except Exception:
                pass

        try:
            current = ctk.get_appearance_mode()
            new_mode = "light" if current == "Dark" else "dark"
            ctk.set_appearance_mode(new_mode)
            self._update_treeview_style(new_mode)
            self.ui_config["theme"] = new_mode
            self._save_ui_state()
            
            for wrapper in [self.skp_wrapper, self.rk_wrapper, self.task_wrapper, self.entri_wrapper, self.log_wrapper]:
                if "frame" in wrapper and hasattr(wrapper["frame"], "update_theme"):
                    wrapper["frame"].update_theme(new_mode)
        finally:
            if sys.platform == "win32" and hwnds_to_freeze:
                import ctypes
                for hwnd in hwnds_to_freeze:
                    ctypes.windll.user32.SendMessageW(hwnd, 11, 1, 0)
                    ctypes.windll.user32.RedrawWindow(hwnd, None, None, 0x0185)
