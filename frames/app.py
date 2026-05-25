import os
import json
import sys
import base64
import zlib
from . import PACKAGE_ACCENT

# BASE_DIR naik satu level karena app.py sekarang di dalam frames/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Set ke False sebelum build produksi (diatur otomatis oleh builder.py)
DEV_MODE = True

# User-Agent HTTP terpusat untuk semua request
HTTP_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"

# Pindahkan session ke folder cache
SESSION_FILE = os.path.join(CACHE_DIR, "session.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

SEALED_ENDPOINTS = "eNo90U1zmkAAxvFlkeUdXMyyvIiaxLTTdBJL05g66UxiIiKsoAWkdTTx5LS99JBrD_nqtZd-gGfm98z_AwtDd_Aggagu4pkIBL5kqRMsiePeC0ueAWMt6RIlSQqqpTZVAHeLRoMGD0sJOiJMgnpRjN4P31amIxqiDLexZVktFlQn-7COnlZUacc_WL_nCDlL4NVFCMoNhzmsfv0ORd6dP8Gb3tX4W-7NUazFASCJ4Jvqr_IFXfdBsmXY1MYi8YtoatithLQl8HnZtVuP2ePo51kI0v-L6OWc0EQSx94NF3UPqovjd8PevoqhChKMkbnK2CqIvTjsvQGT-8C4nZ6cF1voO69NXYZJHV6fHYfDyjyoxoQVDntsWEiYd2CDxx58zhC-c0__7Hal1zZsxzaO_I2rswYCs42nmWrGp7TRBJ1pd_ZAhBQWqs-hvvB6CUgOqE5FNbcpt5Mw9mut9jTFKAj694MrISl369RNjowO2au9j890EXuTjUySreNRoMS7eu6byG_BNDbJQROs09J2WXNJx7KyB59-Y6HitgWW5QxsBGIIlhXotuONadHFh076dIZArlkzvFA4Fd1Nv1zS7iqYF1jTioNq0La1vF0Bx6tmpq9RIOI4QrYBXeZPWNZy_gKAA1ZT"

# CONFIG & API
_config_cache = None
_endpoint_cache = None


def _endpoint_key():
    from .entriFrame import ENTRI_ACCENT
    from .rkFrame import RK_ACCENT
    from .skpFrame import SKP_ACCENT
    from .taskFrame import TASK_ACCENT
    from .update import UPDATE_ACCENT

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


def _read_json_file(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def _merge_config(base, override):
    merged = dict(base or {})
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_config(merged[key], value)
        else:
            merged[key] = value
    return merged


def _strip_endpoint_config(data):
    cleaned = dict(data or {})
    for key in ("api_base", "endpoints", "sso"):
        cleaned.pop(key, None)
    return cleaned


def _decode_sealed_endpoints():
    global _endpoint_cache
    if _endpoint_cache is not None:
        return _endpoint_cache

    if not SEALED_ENDPOINTS:
        raise RuntimeError("SEALED_ENDPOINTS kosong. Suntik endpoints.json dulu.")

    key = _endpoint_key()
    packed = base64.urlsafe_b64decode(SEALED_ENDPOINTS.encode("ascii"))
    xored = zlib.decompress(packed)
    raw = bytes(byte ^ key[index % len(key)] for index, byte in enumerate(xored))
    _endpoint_cache = json.loads(raw.decode("utf-8"))
    return _endpoint_cache


def get_config():
    global _config_cache
    if _config_cache is None:
        user_cfg = _read_json_file(CONFIG_FILE, {})
        endpoint_cfg = _decode_sealed_endpoints()
        _config_cache = _merge_config(user_cfg, endpoint_cfg)
    return _config_cache or {}


def get_api_info(key):
    cfg = get_config()
    raw = cfg.get("endpoints", {}).get(key, "")
    if not raw:
        return None, None

    parts = raw.split()
    method = parts[0] if len(parts) > 1 else "GET"
    path = parts[1] if len(parts) > 1 else parts[0]

    base = cfg.get("api_base", "")
    return method.upper(), f"{base}{path}"


def get_url(key):
    _, url = get_api_info(key)
    return url


def get_sso_config():
    cfg = get_config()
    return cfg.get("sso", {})


# SISTEM & FILE
def restart_app():
    python = sys.executable
    os.execv(python, [python] + sys.argv)


def wipe_session(log_fn=None):
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        if log_fn:
            log_fn("Session data dihapus.")
    else:
        if log_fn:
            log_fn("Tidak ada session data.")


def read_json(path, default):
    return _read_json_file(path, default)


def write_json(path, data):
    try:
        if os.path.abspath(path) == os.path.abspath(CONFIG_FILE):
            data = _strip_endpoint_config(data)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# TREEVIEW UTILS
def bind_treeview_scroll(tree):
    def on_mousewheel(event):
        tree.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def on_shift_mousewheel(event):
        tree.xview_scroll(int(-20 * (event.delta / 120)), "units")
        return "break"

    tree.bind("<MouseWheel>", on_mousewheel)
    tree.bind("<Shift-MouseWheel>", on_shift_mousewheel)


def bind_treeview_sort(tree):
    sort_state = {}

    def sort_by(col):
        items = [(tree.set(k, col), k) for k in tree.get_children('')]
        current = sort_state.get(col)
        if current == 'asc':
            items.sort(reverse=True)
            sort_state[col] = 'desc'
        else:
            items.sort(reverse=False)
            sort_state[col] = 'asc'
        for index, (val, k) in enumerate(items):
            tree.move(k, '', index)
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            tree.item(k, tags=(tag,))

    for col in tree['columns']:
        if col == "check":
            continue
        tree.heading(col, command=lambda c=col: sort_by(c))


def bind_treeview_hover(tree):
    def on_motion(event):
        item = tree.identify_row(event.y)
        tree.tk.call(tree, "tag", "remove", "hover")
        if item and item not in tree.selection():
            tree.tk.call(tree, "tag", "add", "hover", item)

    tree.bind("<Motion>", on_motion)
    tree.bind("<Leave>", lambda e: tree.tk.call(tree, "tag", "remove", "hover"))


def update_treeview_tags(tree, mode):
    if mode == "dark":
        tree.tag_configure("evenrow", background="#2a2d2e", foreground="white")
        tree.tag_configure("oddrow", background="#343638", foreground="white")
        tree.tag_configure("hover", background="#1f538d")
    else:
        tree.tag_configure("evenrow", background="#f0f0f0", foreground="black")
        tree.tag_configure("oddrow", background="#ffffff", foreground="black")
        tree.tag_configure("hover", background="#9fbbe8")
