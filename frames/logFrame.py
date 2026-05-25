import customtkinter as ctk


class LogFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=8, pady=(6, 2))

        self.lbl_hapus = ctk.CTkLabel(top, text="Hapus log", text_color="red",
                                       font=ctk.CTkFont(size=13), cursor="hand2")
        self.lbl_hapus.pack(side="right")
        self.lbl_hapus.bind("<Button-1>", lambda e: self._hapus_log())

        self.textbox = ctk.CTkTextbox(self, height=120, state="disabled",
                                       font=ctk.CTkFont(family="Courier", size=13))
        self.textbox.pack(fill="both", expand=True, padx=8, pady=(2, 8))

    def log(self, pesan):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", f"{pesan}\n")
        self.textbox.configure(state="disabled")
        self.textbox.see("end")


    def _hapus_log(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")
