"""
main.py - Launcher otomatis KiPApp Helper v3.
Menjalankan package frames.
Otomatis menginstal dependensi jika belum ada.
"""
import sys
import os
import importlib
import base64
import json
import re
import shutil
import stat
import zlib


def _endpoint_key_from_source():
    from frames import PACKAGE_ACCENT
    from frames.entriFrame import ENTRI_ACCENT
    from frames.rkFrame import RK_ACCENT
    from frames.skpFrame import SKP_ACCENT
    from frames.taskFrame import TASK_ACCENT
    from frames.update import UPDATE_ACCENT

    parts = (
        PACKAGE_ACCENT[0],
        ENTRI_ACCENT[0],
        RK_ACCENT[0],
        SKP_ACCENT[0],
        TASK_ACCENT[0],
        PACKAGE_ACCENT[1],
        UPDATE_ACCENT[0],
        UPDATE_ACCENT[1],
        UPDATE_ACCENT[2],
        UPDATE_ACCENT[3],
        UPDATE_ACCENT[4],
        UPDATE_ACCENT[2],
        UPDATE_ACCENT[5],
        UPDATE_ACCENT[6],
    )
    return "".join(parts).encode("utf-8")


def _make_endpoint_blob(data):
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    key = _endpoint_key_from_source()
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


def _remove_readonly(func, path):
    os.chmod(path, os.stat(path).st_mode | stat.S_IWRITE)
    func(path)


def cleanup_files(*filenames):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_real = os.path.realpath(base_dir)

    for filename in filenames:
        path = os.path.realpath(os.path.join(base_dir, filename))
        if path == base_real or not path.startswith(base_real + os.sep):
            continue

        try:
            if os.path.isdir(path):
                shutil.rmtree(path, onerror=_remove_readonly)
            elif os.path.isfile(path):
                os.chmod(path, os.stat(path).st_mode | stat.S_IWRITE)
                os.remove(path)
        except OSError:
            pass


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
    cleanup_files("extras.7z")
    check_deps()

    base_dir = os.path.dirname(os.path.abspath(__file__))

    if not os.path.isdir(os.path.join(base_dir, "frames")):
        print("Folder frames tidak ditemukan.")
        sys.exit(1)

    seal_endpoints_if_source(base_dir)
    gui = importlib.import_module("frames.gui")
    app = gui.Gui()
    app.mainloop()


if __name__ == "__main__":
    main()
