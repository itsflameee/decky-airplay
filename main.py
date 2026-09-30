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

SETTINGS_FILE = os.path.join(decky_plugin.DECKY_SETTINGS_DIR, "settings.json")
COVER_PATH = "/tmp/airplay_cover"

def detect_default_device_name() -> str:
    try:
        product_file = "/sys/class/dmi/id/product_name"
        vendor_file = "/sys/class/dmi/id/sys_vendor"

        product = ""
        vendor = ""

        if os.path.exists(product_file):
            with open(product_file, "r") as f:
                product = f.read().strip().lower()

        if os.path.exists(vendor_file):
            with open(vendor_file, "r") as f:
                vendor = f.read().strip().lower()

        if any(deck_id in product for deck_id in ["jupiter", "galileo", "steam deck"]):
            return "Steam Deck"

        if any(sm_id in product for sm_id in ["fremont", "steam machine"]) or ("valve" in vendor and "machine" in product):
            return "Steam Machine"

        if any(frame_id in product for frame_id in ["deckard", "steam frame", "frame"]):
            return "Steam Frame"

    except Exception as e:
        decky_plugin.logger.error(f"[AirPlay] DMI detection error: {e}")

    try:
        if os.path.exists("/etc/machine-info"):
            with open("/etc/machine-info", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_HOSTNAME="):
                        val = line.split("=", 1)[1].strip().strip('"')
                        if val:
                            return val
    except Exception:
        pass

    host = socket.gethostname()
    if host and host not in ["localhost", "localhost.localdomain"]:
        return host

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

            cmd = ["uxplay"] + self.build_uxplay_args() + ["-fs", "-vs", "waylandsink", "-as", "pulsesink"]
            decky_plugin.logger.info(f"[AirPlay] Starting: {' '.join(cmd)}")

            self.listener_process = subprocess.Popen(
                cmd,
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
                            parsed_device = after_from.split("(", 1)[0].strip()
                        else:
                            parsed_device = after_from.split("with deviceID", 1)[0].strip()
                        if parsed_device:
                            client_name = parsed_device
                    except Exception:
                        pass

                elif "starting mirroring" in line_str:
                    decky_plugin.logger.info(f"[AirPlay] Mirroring started from {client_name}")
                    decky_plugin.emit_to_frontend("screen_mirroring", {
                        "device": client_name
                    })
                    if self.appid:
                        short_id = (self.appid >> 32)
                        subprocess.Popen(["steam", f"steam://rungameid/{short_id}"])

                elif line_str.startswith("Artist:"):
                    current_artist = line_str.split("Artist:", 1)[1].strip()

                elif line_str.startswith("Title:"):
                    current_title = line_str.split("Title:", 1)[1].strip()
                    decky_plugin.emit_to_frontend("now_playing", {
                        "device": client_name,
                        "artist": current_artist,
                        "title": current_title,
                        "cover": get_cover_base64()
                    })

        threading.Thread(target=run_loop, daemon=True).start()

    async def _unload(self):
        self.is_running = False
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