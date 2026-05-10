"""
main.py — Launcher otomatis KiPApp Helper v3.
Mendeteksi versi Python dan menjalankan package yang sesuai (frames12/frames13/frames14).
Otomatis menginstal dependensi jika belum ada.
"""
import sys
import os
import importlib

def check_deps():
    """Periksa dan instal dependensi yang belum ada."""
    deps = {
        "customtkinter": "customtkinter",
        "requests": "requests",
        "openpyxl": "openpyxl",
        "dotenv": "python-dotenv",
        "bs4": "beautifulsoup4",
    }
    missing = []
    for imp_name, pkg_name in deps.items():
        try:
            __import__(imp_name)
        except ImportError:
            missing.append(pkg_name)

    if missing:
        import subprocess
        print(f"📦 Menginstal dependensi: {', '.join(missing)}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *missing, "-q"],
            stdout=subprocess.DEVNULL
        )
        print("✅ Dependensi terinstal.")

def main():
    check_deps()

    minor = sys.version_info.minor
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Prioritaskan folder 'frames' (source) jika ada (untuk Developer)
    if os.path.isdir(os.path.join(base_dir, "frames")):
        pkg = "frames"
    else:
        # Jika tidak ada, baru cari folder terkompilasi sesuai versi (untuk User)
        pkg = f"frames{minor}"
        if not os.path.isdir(os.path.join(base_dir, pkg)):
            supported = sorted([
                f"3.{d[6:]}" for d in os.listdir(base_dir)
                if os.path.isdir(os.path.join(base_dir, d))
                and d.startswith("frames") and d[6:].isdigit()
            ])
            print(f"❌ Python 3.{minor} tidak didukung.")
            if supported:
                print(f"   Versi yang tersedia: {', '.join(supported)}")
            sys.exit(1)

    gui = importlib.import_module(f"{pkg}.gui")
    app = gui.Gui()
    app.mainloop()

if __name__ == "__main__":
    main()
