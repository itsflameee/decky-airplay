import os
import zlib
import vdf

def calculate_appid(exe: str, app_name: str) -> int:
    key = f"{exe}{app_name}".encode("utf-8")
    crc = zlib.crc32(key) | 0x80000000
    return (crc << 32) | 0x02000000

def get_shortcuts_path() -> str | None:
    steam_base = os.path.expanduser("~/.steam/steam/userdata")
    if not os.path.exists(steam_base):
        steam_base = os.path.expanduser("~/.local/share/Steam/userdata")

    if not os.path.exists(steam_base):
        return None

    user_dirs = [d for d in os.listdir(steam_base) if d.isdigit() and d != "0"]
    if not user_dirs:
        return None

    return os.path.join(steam_base, user_dirs[0], "config", "shortcuts.vdf")

def register_airplay(plugin_dir: str) -> int | None:
    shortcuts_path = get_shortcuts_path()
    if not shortcuts_path:
        return None

    runner_path = os.path.join(plugin_dir, "bin", "airplay-runner.sh")
    icon_path = os.path.join(plugin_dir, "assets", "icon.png")
    app_name = "AirPlay"

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
            return calculate_appid(runner_path, app_name)

    appid = calculate_appid(runner_path, app_name)
    new_idx = str(len(shortcuts))

    shortcuts[new_idx] = {
        "appid": appid,
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

    return appid