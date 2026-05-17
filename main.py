"""
main.py - Launcher otomatis KiPApp Helper v3.
Mendeteksi versi Python dan menjalankan package yang sesuai (frames12/frames13/frames14).
Otomatis menginstal dependensi jika belum ada.
"""
import sys
import os
import importlib
import base64
import json
import re
import zlib


ENDPOINT_KEY_PARTS = ("kip", "app", "helper", "v3")


def _make_endpoint_blob(data):
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    key = "".join(ENDPOINT_KEY_PARTS).encode("utf-8")
    xored = bytes(byte ^ key[index % len(key)] for index, byte in enumerate(raw))
    return base64.urlsafe_b64encode(zlib.compress(xored, 9)).decode("ascii")


def seal_endpoints_if_source(base_dir):
    app_path = os.path.join(base_dir, "frames", "app.py")
    endpoints_path = os.path.join(base_dir, "endpoints.json")
    if not os.path.exists(app_path) or not os.path.exists(endpoints_path):
        return

    with open(endpoints_path, "r", encoding="utf-8-sig") as f:
        endpoint_data = json.load(f)
    blob = _make_endpoint_blob(endpoint_data)

    with open(app_path, "r", encoding="utf-8") as f:
        source = f.read()

    pattern = r'^(SEALED_ENDPOINTS\s*=\s*)"[A-Za-z0-9_\-=]*"'
    patched, count = re.subn(pattern, rf'\1"{blob}"', source, count=1, flags=re.MULTILINE)
    if count == 0:
        raise RuntimeError("SEALED_ENDPOINTS tidak ditemukan di frames/app.py")
    if patched != source:
        with open(app_path, "w", encoding="utf-8") as f:
            f.write(patched)

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
        print(f"Menginstal dependensi: {', '.join(missing)}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *missing, "-q"],
            stdout=subprocess.DEVNULL
        )
        print("Dependensi terinstal.")

def main():
    check_deps()

    minor = sys.version_info.minor
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Prioritaskan folder 'frames' (source) jika ada (untuk Developer)
    if os.path.isdir(os.path.join(base_dir, "frames")):
        seal_endpoints_if_source(base_dir)
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
            print(f"Python 3.{minor} tidak didukung.")
            if supported:
                print(f"   Versi yang tersedia: {', '.join(supported)}")
            sys.exit(1)

    gui = importlib.import_module(f"{pkg}.gui")
    app = gui.Gui()
    app.mainloop()

if __name__ == "__main__":
    main()
