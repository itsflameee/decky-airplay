import os
import sys
import pwd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import zlib
import vdf
from py_modules.session_utils import get_session_user_env

def calculate_appid(exe: str, app_name: str) -> tuple[int, int]:
    key = f"{exe}{app_name}".encode("utf-8")
    crc = zlib.crc32(key) | 0x80000000
    
    # 64-битный unsigned ID для steam://rungameid/<id>
    full_id = (crc << 32) | 0x02000000
    
    # 32-битный signed int для поля "appid" внутри binary VDF
    raw_crc = zlib.crc32(key)
    signed_32_id = raw_crc if raw_crc < 0x80000000 else raw_crc - 0x100000000
    
    return signed_32_id, full_id

def get_shortcuts_path() -> str | None:
    _, home_dir, _, _ = get_session_user_env()
    candidates = [
        os.path.join(home_dir, ".local/share/Steam/userdata"),
        os.path.join(home_dir, ".steam/steam/userdata"),
        os.path.join(home_dir, ".steam/root/userdata"),
    ]

    steam_base = None
    for cand in candidates:
        if os.path.exists(cand):
            steam_base = cand
            break

    if not steam_base:
        return None

    try:
        user_dirs = [d for d in os.listdir(steam_base) if d.isdigit() and d != "0"]
        if not user_dirs:
            return None
        user_dirs.sort(key=lambda d: os.path.getmtime(os.path.join(steam_base, d)), reverse=True)
        return os.path.join(steam_base, user_dirs[0], "config", "shortcuts.vdf")
    except Exception:
        return None

def register_airplay(plugin_dir: str) -> int | None:
    shortcuts_path = get_shortcuts_path()
    if not shortcuts_path:
        return None

    runner_path = os.path.join(plugin_dir, "bin", "airplay-runner.sh")
    icon_path = os.path.join(plugin_dir, "assets", "icon.png")
    app_name = "AirPlay"

    signed_32_id, full_id = calculate_appid(runner_path, app_name)

    data = {"shortcuts": {}}
    if os.path.exists(shortcuts_path):
        try:
            with open(shortcuts_path, "rb") as f:
                data = vdf.binary_loads(f.read())
        except Exception:
            data = {"shortcuts": {}}

    shortcuts = data.setdefault("shortcuts", {})

    for idx, item in shortcuts.items():
        if item.get("AppName") == app_name:
            return full_id

    new_idx = str(len(shortcuts))
    shortcuts[new_idx] = {
        "appid": signed_32_id,
        "AppName": app_name,
        "Exe": f'"{runner_path}"',
        "StartDir": f'"{os.path.join(plugin_dir, "bin")}"',
        "icon": icon_path,
        "LaunchOptions": "",
        "IsHidden": 1,
        "AllowDesktopConfig": 1,
        "AllowOverlay": 1,
        "OpenVR": 0,
        "Devkit": 0,
    }

    with open(shortcuts_path, "wb") as f:
        f.write(vdf.binary_dumps(data))

    username, _, uid, _ = get_session_user_env()
    gid = pwd.getpwuid(uid).pw_gid
    os.chown(shortcuts_path, uid, gid)

    return full_id