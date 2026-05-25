import customtkinter as ctk
import tkinter as tk
import threading
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from . import app


ENTRI_ACCENT = ("is ",)


class EntriFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._session  = None
        self._log_fn   = None  # callback ke LogFrame, di-set dari luar
        self._on_session_ready = None  # callback ke gui saat session berhasil
        self._auth_lock = threading.Lock()

        self._build()

    def _build(self):
        # ── Baris tombol ──────────────────────────────────────────
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=8, pady=(8, 4))

        self.btn_sso = ctk.CTkButton(
            btn_row, text="👤 Impor SSO",
            width=120, command=self._impor_sso
        )
        self.btn_sso.pack(side="left", padx=(0, 6))

        self.btn_login = ctk.CTkButton(
            btn_row, text="🔐 Login",
            width=100, command=self._login,
            state="disabled"
        )
        self.btn_login.pack(side="left")

        self.btn_logout = ctk.CTkButton(
            btn_row, text="🚪 Logout",
            width=80, command=self._logout,
            fg_color="#c0392b", hover_color="#e74c3c"
        )
        self.btn_logout.pack_forget()

        # Status label dipindah ke paling kanan
        self.lbl_status = ctk.CTkLabel(
            btn_row, text="", font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.lbl_status.pack(side="right", padx=8)

        # ── Placeholder form ──────────────────────────────────────
        ctk.CTkLabel(self, text="(form entri akan muncul di sini)",
                     text_color="gray").pack(padx=8, pady=(4, 8))
        self.after(100, lambda: threading.Thread(target=self._try_resume_session, daemon=True).start())

    # ── Resume/Revive Session ────────────────────────────────────────────────
    def _try_resume_session(self):
        if not self._auth_lock.acquire(blocking=False):
            return

        try:
            token, cookies, saved_user = self._load_session()
            if not token:
                return

            self._log("🔄 Mencoba resume sesi sebelumnya...")
            s = requests.Session()
            s.headers.update({"User-Agent": app.HTTP_UA, "Authorization": f"Bearer {token}"})

            try:
                m_u, u_u = app.get_api_info("user")
                r_user = s.request(m_u, u_u, timeout=15)
                if r_user.status_code == 200:
                    user_info = r_user.json() if r_user.ok else {}
                    nama_user = user_info.get("name") or user_info.get("nama") or user_info.get("username") or saved_user or "-"

                    self._session = s
                    self._save_session(token, {}, nama_user)
                    self._log(f"✅ Sesi dilanjutkan! User: {nama_user}")
                    self.after(0, lambda: self.lbl_status.configure(text=f"✅ {nama_user}", text_color="green"))
                    self.after(0, self._show_logout_ui)
                    if self._on_session_ready:
                        self.after(0, self._on_session_ready)
                else:
                    self._log("⚠️ Sesi lama expired, silakan login ulang.")
                    self._clear_session()

            except Exception as ex:
                errmsg = str(ex)
                if "NameResolutionError" in errmsg or "getaddrinfo failed" in errmsg or "Max retries exceeded" in errmsg:
                    self._log("⚠️ Gagal resume sesi: Tidak dapat terhubung ke server. Periksa koneksi internet.")
                elif "401" in errmsg or "Unauthorized" in errmsg:
                    self._log("Sesi anda habis. Harap login ulang.")
                    self._clear_session()
                else:
                    self._log(f"⚠️ Gagal resume sesi: {ex}")
                    self._clear_session()
        finally:
            self._auth_lock.release()

    # ── Helper log ────────────────────────────────────────────────
    def _reset_session(self):
        self._session = None
        self._clear_session()

    def _log(self, msg):
        if self._log_fn:
            self._log_fn(msg)

    # ── Impor SSO ─────────────────────────────────────────────────
    def _impor_sso(self):
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
        env_path = os.path.normpath(env_path)

        if not os.path.exists(env_path):
            self._log(f"❌ File .env tidak ditemukan di: {env_path}")
            self.lbl_status.configure(text="❌ .env tidak ada", text_color="red")
            return

        load_dotenv(env_path, override=True)
        user = os.getenv("USER") or os.getenv("usr")
        pw   = os.getenv("PASS") or os.getenv("pwd")

        if not user or not pw:
            self._log("❌ File .env tidak mengandung USER/PASS.")
            self.lbl_status.configure(text="❌ .env tidak valid", text_color="red")
            return

        self._log(f"✅ SSO dimuat dari .env | User: {user}")
        self.lbl_status.configure(text=f"👤 {user}", text_color="green")
        self.btn_login.configure(state="normal")

    # ── Login ─────────────────────────────────────────────────────
    def _login(self):
        self.btn_login.configure(state="disabled", text="⏳ Login...")
        self._log("🔄 Memulai proses login...")
        threading.Thread(target=self._do_login, daemon=True).start()

    def _do_login(self):
        with self._auth_lock:
            if self._session:
                return

            # Coba resume dulu
            token, cookies, saved_user = self._load_session()
            if token:
                self._log("🔄 Mencoba sesi tersimpan...")
                s = requests.Session()
                s.headers.update({
                    "User-Agent": app.HTTP_UA,
                    "Authorization": f"Bearer {token}"
                })
                try:
                    m_u, u_u = app.get_api_info("user")
                    r_user = s.request(m_u, u_u, timeout=15)
                    user_info = r_user.json() if r_user.ok else {}
                    nama_user = user_info.get("name") or user_info.get("nama") or user_info.get("username") or "-"

                    if r_user.status_code == 200:
                        self._save_session(token, {}, nama_user)
                        self._log(f"✅ Login sukses! User: {nama_user}")
                        self._session = s
                        self.after(0, lambda: self.lbl_status.configure(text=f"✅ {nama_user}", text_color="green"))
                        self.after(0, self._show_logout_ui)
                        if self._on_session_ready:
                            self.after(0, self._on_session_ready)
                        return
                    else:
                        self._log("⚠️ Sesi expired, melakukan fresh login...")
                        self._clear_session()
                except Exception as ex:
                    self._log(f"⚠️ Gagal resume: {ex}, melakukan fresh login...")
                    self._clear_session()

            # Fresh login
            user = os.getenv("USER") or os.getenv("usr")
            pw   = os.getenv("PASS") or os.getenv("pwd")

            if not user or not pw:
                self._log("❌ Kredensial tidak ada. Impor SSO dulu.")
                self.after(0, lambda: self.btn_login.configure(state="normal", text="🔐 Login"))
                return

            try:
                s = requests.Session()
                s.headers.update({"User-Agent": app.HTTP_UA})

                sso_cfg = app.get_sso_config()
                auth_url = sso_cfg.get("auth")
                redirect_uri = sso_cfg.get("redirect")

                self._log("🌐 Menghubungi SSO BPS...")
                r = s.get(
                    auth_url,
                    params={
                        "client_id":     "03340-kipapp-h0m",
                        "redirect_uri":  redirect_uri,
                        "response_type": "code",
                        "scope":         "profile-pegawai email",
                    },
                    timeout=15, allow_redirects=True
                )

                soup = BeautifulSoup(r.text, "html.parser")
                form = soup.find("form")
                if not form:
                    raise Exception(f"Form login tidak ditemukan. URL: {r.url}")

                self._log("🔑 Mengirim kredensial...")
                r2 = s.post(form["action"], data={"username": user, "password": pw},
                            timeout=15, allow_redirects=True)

                soup2 = BeautifulSoup(r2.text, "html.parser")

                if soup2.find("input", {"name": "otp"}):
                    self._log("📱 OTP diperlukan. Masukkan OTP di popup...")
                    otp = self._ask_otp()
                    if otp is None:
                        self._log("❌ Login dibatalkan — OTP tidak dimasukkan.")
                        self._reset_session()
                        self.after(0, lambda: self.btn_login.configure(state="normal", text="🔐 Login"))
                        return
                    form2 = soup2.find("form")
                    data  = {i["name"]: i.get("value", "") for i in form2.find_all("input") if i.get("name")}
                    data.pop("cancel", None)
                    data["otp"] = otp
                    self._log("🔄 Mengirim OTP...")
                    r2 = s.post(form2["action"], data=data, timeout=15, allow_redirects=True)

                if "kipapp.bps.go.id" not in r2.url:
                    raise Exception(f"Login gagal. Redirect ke: {r2.url}")

                token = r2.url.split("?t=")[-1]
                s.headers.update({"Authorization": f"Bearer {token}"})
                self._session = s
                self._save_session(token, {}, user) # user from env

                self._log(f"✅ Login sukses!")
                self.after(0, lambda: self.lbl_status.configure(text=f"✅ {user}", text_color="green"))
                self.after(0, self._show_logout_ui)
                if self._on_session_ready:
                    self.after(0, self._on_session_ready)

            except Exception as ex:
                self._log(f"❌ Error: {ex}")
                self._reset_session()
                self.after(0, lambda: self.btn_login.configure(state="normal", text="🔐 Login"))
                self.after(0, lambda: self.lbl_status.configure(text="❌ Login gagal", text_color="red"))

    def _ask_otp(self):
        result = {"value": None}
        event  = threading.Event()

        def show_dialog():
            dialog = ctk.CTkToplevel(self)
            dialog.title("OTP Diperlukan")
            dialog.geometry("300x150")
            dialog.resizable(False, False)
            dialog.grab_set()

            ctk.CTkLabel(dialog, text="Masukkan kode OTP:").pack(pady=(16, 4))
            entry = ctk.CTkEntry(dialog, width=200, placeholder_text="Kode OTP")
            entry.pack(pady=4)
            entry.focus()

            def submit():
                result["value"] = entry.get().strip() or None
                dialog.destroy()
                event.set()

            def cancel():
                result["value"] = None
                dialog.destroy()
                event.set()

            ctk.CTkButton(dialog, text="Masuk", command=submit).pack(pady=8)
            dialog.protocol("WM_DELETE_WINDOW", cancel)
            entry.bind("<Return>", lambda e: submit())

        self.after(0, show_dialog)
        event.wait()
        return result["value"]

    def _save_session(self, token, cookies, user=None):
        app.write_json(app.SESSION_FILE, {
            "token": token,
            "cookies": cookies,
            "user": user
        })

    def _load_session(self):
        data = app.read_json(app.SESSION_FILE, {})
        return data.get("token"), data.get("cookies", {}), data.get("user")

    def _clear_session(self):
        if os.path.exists(app.SESSION_FILE):
            os.remove(app.SESSION_FILE)
        self._session = None

    def _show_logout_ui(self):
        self.btn_login.pack_forget()
        self.btn_logout.pack(side="left", after=self.btn_sso)
        self.btn_sso.configure(state="disabled")

    def _show_login_ui(self):
        self.btn_logout.pack_forget()
        self.btn_login.pack(side="left", after=self.btn_sso)
        self.btn_login.configure(state="normal", text="🔐 Login")
        self.btn_sso.configure(state="normal")

    def _logout(self):
        confirm = tk.messagebox.askyesno("Logout", "Apakah Anda yakin ingin logout dan mengakhiri sesi?")
        if not confirm: return

        self._log("🔄 Melakukan logout SSO...")
        
        def logout_worker():
            try:
                sso_cfg = app.get_sso_config()
                logout_url = sso_cfg.get("logout")
                
                # Panggil endpoint logout SSO
                if self._session:
                    self._session.get(logout_url, timeout=15)
                else:
                    requests.get(logout_url, timeout=15)
                
                self._log("✅ Sesi SSO telah di-invalidkan.")
            except Exception as e:
                self._log(f"⚠️ Gagal menghubungi SSO logout: {e}")
            
            # Tetap hapus lokal biarpun API gagal
            self._clear_session()
            self._log("🗑️ Cache sesi lokal dihapus.")
            self.after(0, self._show_login_ui)
            self.after(0, lambda: self.lbl_status.configure(text="Sesi berakhir", text_color="orange"))

        threading.Thread(target=logout_worker, daemon=True).start()
