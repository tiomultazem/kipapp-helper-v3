import customtkinter as ctk
import requests
import json
import os
import subprocess
import sys
import threading
from . import app

UPDATE_ACCENT = ("'", "ve", " ", "ev", "er", "do", "ne")

CHANGELOG_URL = "https://raw.githubusercontent.com/tiomultazem/kipapp-helper-v3/main/changelog.json"

def get_local_changelog():
    changelog_path = os.path.join(app.BASE_DIR, "changelog.json")
    if os.path.exists(changelog_path):
        try:
            with open(changelog_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def get_local_version():
    config_path = os.path.join(app.BASE_DIR, "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "currentVersion" in data:
                    return data["currentVersion"]
        except Exception:
            pass
    # Fallback ke cara lama (baca changelog.json) jika di config belum ada
    data = get_local_changelog()
    if data:
        return max(data.keys())
    return "3.0000.00"

def get_remote_changelog():
    response = requests.get(CHANGELOG_URL, timeout=5)
    response.raise_for_status()
    return response.json()

class UpdatePopup(ctk.CTkToplevel):
    def __init__(self, parent, mode="auto", local_version="", remote_version="", remote_changelog=None):
        super().__init__(parent)
        self.title("Pembaruan KiPApp Helper v3")
        self.geometry("350x450")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.mode = mode
        self.local_version = local_version
        self.remote_version = remote_version
        self.remote_changelog = remote_changelog or {}

        self._build_ui()

        # Biarkan jendela menghitung ukuran yang dibutuhkan konten
        self.update_idletasks()
        width = 380
        height = self.main_frame.winfo_reqheight() + 20 # Tambah sedikit padding
        
        # Batasi tinggi maksimal agar tidak melebihi layar (misal 600px)
        if height > 600: height = 600
        
        # Hitung posisi tengah relatif terhadap parent
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        
        self.geometry(f"{width}x{int(height)}+{x}+{y}")

    def _build_ui(self):
        # Frame utama
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        is_update_available = self.remote_version > self.local_version

        if self.mode == "auto" or is_update_available:
            lbl_title = ctk.CTkLabel(
                self.main_frame,
                text=f"Versi anda sekarang {self.local_version}.\nTerdapat versi baru {self.remote_version} di Github,\ndengan rincian update:",
                font=ctk.CTkFont(size=14, weight="bold"),
                justify="left"
            )
        else:
            lbl_title = ctk.CTkLabel(
                self.main_frame,
                text=f"KiPApp Helper v3 anda sudah versi terbaru!\nPerubahan pada versi terbaru ini ({self.remote_version}):",
                font=ctk.CTkFont(size=14, weight="bold"),
                justify="left"
            )
            
        lbl_title.pack(anchor="w", pady=(0, 10))

        # Changelog terbaru
        latest_logs = self.remote_changelog.get(self.remote_version, [])
        latest_text = "\n".join([f"- {log}" for log in latest_logs])
        
        lbl_latest = ctk.CTkLabel(
            self.main_frame,
            text=latest_text,
            justify="left",
            anchor="w"
        )
        lbl_latest.pack(fill="x", pady=(0, 15))

        # Scrollable frame untuk riwayat
        lbl_history = ctk.CTkLabel(self.main_frame, text="Riwayat Update:", font=ctk.CTkFont(weight="bold"))
        lbl_history.pack(anchor="w", pady=(0, 5))

        scroll_frame = ctk.CTkScrollableFrame(self.main_frame, height=150)
        scroll_frame.pack(fill="both", expand=True, pady=(0, 15))

        sorted_versions = sorted(self.remote_changelog.keys(), reverse=True)
        for ver in sorted_versions:
            if ver == self.remote_version:
                continue # Skip latest
            
            lbl_ver = ctk.CTkLabel(scroll_frame, text=f"Versi {ver}:", font=ctk.CTkFont(weight="bold"), anchor="w")
            lbl_ver.pack(fill="x", pady=(5, 0))
            
            logs = self.remote_changelog[ver]
            logs_text = "\n".join([f"- {log}" for log in logs])
            lbl_log = ctk.CTkLabel(scroll_frame, text=logs_text, justify="left", anchor="w")
            lbl_log.pack(fill="x", pady=(0, 5))

        # Tombol
        if self.mode == "auto" or is_update_available:
            lbl_ask = ctk.CTkLabel(self.main_frame, text=f"Update ke versi terbaru ({self.remote_version})?", font=ctk.CTkFont(weight="bold"))
            lbl_ask.pack(pady=(0, 10))

            btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            btn_frame.pack(fill="x")
            
            btn_yes = ctk.CTkButton(btn_frame, text="Ya", width=100, command=self.do_update)
            btn_yes.pack(side="left", expand=True, padx=5)
            
            btn_no = ctk.CTkButton(btn_frame, text="Tidak", width=100, fg_color="gray", hover_color="darkgray", command=self.destroy)
            btn_no.pack(side="right", expand=True, padx=5)

    def do_update(self):
        base_dir = app.BASE_DIR
        
        if sys.platform == "win32":
            update_script = os.path.join(base_dir, "update.bat")
            if os.path.exists(update_script):
                creation_flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
                subprocess.Popen([update_script], creationflags=creation_flags)
                sys.exit(0)
        else:
            # macOS atau Linux
            update_script = os.path.join(base_dir, "update.sh")
            if os.path.exists(update_script):
                # Jalankan menggunakan bash
                subprocess.Popen(["bash", update_script])
                sys.exit(0)

        print("Script update tidak ditemukan.")
        self.destroy()

def check_update_background(parent, mode="auto"):
    def worker():
        local_changelog = get_local_changelog()
        local_version = get_local_version()
        
        try:
            remote_changelog = get_remote_changelog()
        except Exception as e:
            if mode == "manual":
                err_str = f"⚠️ Gagal mengecek update: {e}"
                print(err_str)
                if hasattr(parent, "master_log"):
                    parent.master_log(err_str)
                
                # Tetap tampilkan popup menggunakan data lokal
                parent.after(0, lambda: UpdatePopup(
                    parent, 
                    mode="manual", 
                    local_version=local_version, 
                    remote_version=local_version, 
                    remote_changelog=local_changelog
                ))
            return

        remote_version = max(remote_changelog.keys()) if remote_changelog else local_version

        if mode == "auto":
            if remote_version > local_version:
                # Tampilkan popup karena ada update
                parent.after(0, lambda: UpdatePopup(parent, mode="auto", local_version=local_version, remote_version=remote_version, remote_changelog=remote_changelog))
        else:
            # Mode manual: klik dari footer, selalu tampilkan
            parent.after(0, lambda: UpdatePopup(parent, mode="manual", local_version=local_version, remote_version=remote_version, remote_changelog=remote_changelog))

    threading.Thread(target=worker, daemon=True).start()
