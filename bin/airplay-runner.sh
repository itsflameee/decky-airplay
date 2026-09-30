#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
SETTINGS_FILE="${DECKY_SETTINGS_DIR:-$HOME/.config/decky-airplay}/settings.json"

if [ -f "${SCRIPT_DIR}/uxplay" ]; then
    UXPLAY_BIN="${SCRIPT_DIR}/uxplay"
else
    UXPLAY_BIN="$(command -v uxplay)"
fi

SERVER_NAME="Decky AirPlay"
FPS="60"
AVDEC="-avdec"
PIN="-p"
CUSTOM_ARGS=""

if [ -f "$SETTINGS_FILE" ]; then
    eval $(python3 -c "
import json
try:
    with open('$SETTINGS_FILE') as f:
        d = json.load(f)
        print(f'SERVER_NAME=\"{d.get(\"server_name\", \"Decky AirPlay\")}\"')
        print(f'FPS=\"{d.get(\"fps\", 60)}\"')
        print(f'AVDEC=\"{\"-avdec\" if d.get(\"avdec\", True) else \"\"}\"')
        print(f'PIN=\"{\"-p\" if d.get(\"pin\", True) else \"\"}\"')
        print(f'CUSTOM_ARGS=\"{d.get(\"custom_args\", \"\")}\"')
except Exception:
    pass
")
fi

exec "$UXPLAY_BIN" -n "$SERVER_NAME" -nh $AVDEC -fps "$FPS" $PIN $CUSTOM_ARGS -fs -vs waylandsink -as pulsesink