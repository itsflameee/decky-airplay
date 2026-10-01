import os
import sys

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
if PLUGIN_DIR not in sys.path:
    sys.path.insert(0, PLUGIN_DIR)

import socket
import json
import base64
import subprocess
import threading
import decky_plugin
from py_modules.steam_shortcuts import register_airplay
from py_modules.session_utils import get_session_user_env

SETTINGS_FILE = os.path.join(decky_plugin.DECKY_SETTINGS_DIR, "settings.json")
COVER_PATH = "/tmp/airplay_cover"
FLAG_ACTIVE = "/tmp/airplay_stream_active"

def detect_default_device_name() -> str:
    try:
        info = ""
        for path in ("/sys/class/dmi/id/product_name", "/sys/class/dmi/id/board_name"):
            if os.path.exists(path):
                with open(path, "r") as f:
                    info += " " + f.read().strip().lower()

        if any(d in info for d in ["jupiter", "galileo", "steam deck"]):
            return "Steam Deck"

        if "fremont" in info or "steam machine" in info:
            return "Steam Machine"
    except Exception as e:
        decky_plugin.logger.error(f"[AirPlay] DMI detection error: {e}")

    try:
        host = socket.gethostname()
        if host and host not in ["localhost", "localhost.localdomain"]:
            return host
    except Exception:
        pass

    return "Decky AirPlay"

def get_cover_base64() -> str | None:
    if os.path.exists(COVER_PATH) and os.path.getsize(COVER_PATH) > 0:
        try:
            with open(COVER_PATH, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                return f"data:image/jpeg;base64,{encoded}"
        except Exception as e:
            decky_plugin.logger.error(f"[AirPlay] Failed to read cover: {e}")
    return None

class Plugin:
    def __init__(self):
        self.listener_process = None
        self.appid = None
        self.is_running = False
        self.settings = {
            "server_name": detect_default_device_name(),
            "fps": 60,
            "avdec": True,
            "pin": True,
            "custom_args": ""
        }

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    self.settings.update(json.load(f))
            except Exception as e:
                decky_plugin.logger.error(f"[AirPlay] Config load error: {e}")

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            decky_plugin.logger.error(f"[AirPlay] Config save error: {e}")

    def build_uxplay_args(self) -> list:
        args = ["-nh", "-ca", COVER_PATH]
        if self.settings.get("server_name"):
            args.extend(["-n", self.settings["server_name"]])
        if self.settings.get("avdec"):
            args.append("-avdec")
        if self.settings.get("pin"):
            args.append("-p")
        args.extend(["-fps", str(self.settings.get("fps", 60))])

        custom = self.settings.get("custom_args", "").strip()
        if custom:
            args.extend(custom.split())
        return args

    async def _main(self):
        self.load_settings()
        plugin_dir = decky_plugin.DECKY_PLUGIN_DIR
        self.appid = register_airplay(plugin_dir)
        self.start_daemon()

    def start_daemon(self):
        if self.is_running:
            return
        self.is_running = True

        def run_loop():
            if os.path.exists(COVER_PATH):
                try:
                    os.remove(COVER_PATH)
                except Exception:
                    pass
            if os.path.exists(FLAG_ACTIVE):
                try:
                    os.remove(FLAG_ACTIVE)
                except Exception:
                    pass

            username, _, _, env = get_session_user_env()

            cmd = [
                "sudo", "-u", username, "-E",
                "uxplay"
            ] + self.build_uxplay_args() + ["-fs", "-vs", "waylandsink", "-as", "pulsesink"]

            decky_plugin.logger.info(f"[AirPlay] Launching: {' '.join(cmd)}")

            self.listener_process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            client_name = "Apple Device"
            current_artist = ""
            current_title = ""

            for line in self.listener_process.stdout:
                line_str = line.strip()

                if "connection request from" in line_str:
                    try:
                        after_from = line_str.split("connection request from", 1)[1].strip()
                        if "(" in after_from:
                            parsed = after_from.split("(", 1)[0].strip()
                        else:
                            parsed = after_from.split("with deviceID", 1)[0].strip()
                        if parsed:
                            client_name = parsed
                    except Exception:
                        pass

                elif "starting mirroring" in line_str:
                    decky_plugin.logger.info(f"[AirPlay] Mirroring started from {client_name}")
                    with open(FLAG_ACTIVE, "w") as f:
                        f.write("1")

                    decky_plugin.emit_to_frontend("show_toast", {
                        "title": f"{client_name} — Screen Sharing",
                        "message": "Screen Sharing started"
                    })

                    if self.appid:
                        short_id = (self.appid >> 32)
                        subprocess.Popen(
                            ["sudo", "-u", username, "-E", "steam", f"steam://rungameid/{short_id}"],
                            env=env
                        )

                elif "teardown" in line_str.lower() or "stopping mirroring" in line_str.lower():
                    if os.path.exists(FLAG_ACTIVE):
                        try:
                            os.remove(FLAG_ACTIVE)
                        except Exception:
                            pass

                elif line_str.startswith("Artist:"):
                    current_artist = line_str.split("Artist:", 1)[1].strip()

                elif line_str.startswith("Title:"):
                    current_title = line_str.split("Title:", 1)[1].strip()
                    decky_plugin.emit_to_frontend("show_toast", {
                        "title": f"{client_name} — Now Playing",
                        "message": f"{current_artist} — {current_title}"
                    })
                    decky_plugin.emit_to_frontend("now_playing", {
                        "device": client_name,
                        "artist": current_artist,
                        "title": current_title,
                        "cover": get_cover_base64()
                    })

        threading.Thread(target=run_loop, daemon=True).start()

    async def _unload(self):
        self.is_running = False
        if os.path.exists(FLAG_ACTIVE):
            try:
                os.remove(FLAG_ACTIVE)
            except Exception:
                pass
        if self.listener_process:
            self.listener_process.terminate()

    async def get_settings(self):
        return self.settings

    async def update_settings(self, new_settings: dict):
        self.settings.update(new_settings)
        self.save_settings()
        await self._unload()
        self.start_daemon()
        return self.settings