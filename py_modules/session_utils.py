import os
import pwd
import subprocess

def get_session_user_env() -> tuple[str, str, int, dict]:
    username = None
    uid = None

    try:
        pid_out = subprocess.check_output(
            ["pgrep", "-u", "1000", "-o", "-x", "steam"],
            text=True
        ).strip().splitlines()[0]
        if pid_out:
            stat_info = os.stat(f"/proc/{pid_out}")
            uid = stat_info.st_uid
            username = pwd.getpwuid(uid).pw_name
    except Exception:
        pass

    if not username:
        try:
            sessions = subprocess.check_output(["loginctl", "list-sessions", "--no-legend"], text=True)
            for line in sessions.strip().splitlines():
                parts = line.split()
                if len(parts) >= 3 and int(parts[1]) >= 1000:
                    uid = int(parts[1])
                    username = parts[2]
                    break
        except Exception:
            pass

    if not username:
        cand = os.environ.get("SUDO_USER") or os.environ.get("LOGNAME")
        if cand and cand != "root":
            try:
                uid = pwd.getpwnam(cand).pw_uid
                username = cand
            except KeyError:
                pass

    if not username or uid is None:
        for p in pwd.getpwall():
            if p.pw_uid >= 1000 and p.pw_dir.startswith("/home/"):
                username = p.pw_name
                uid = p.pw_uid
                break

    if not username:
        username = "deck"
        uid = 1000

    pw = pwd.getpwnam(username)
    home_dir = pw.pw_dir
    runtime_dir = f"/run/user/{uid}"

    env = os.environ.copy()
    env["USER"] = username
    env["LOGNAME"] = username
    env["HOME"] = home_dir
    env["XDG_RUNTIME_DIR"] = runtime_dir
    env["WAYLAND_DISPLAY"] = "wayland-0"
    env["DISPLAY"] = ":0"

    pulse_sock = f"{runtime_dir}/pulse/native"
    if os.path.exists(pulse_sock):
        env["PULSE_SERVER"] = f"unix:{pulse_sock}"

    return username, home_dir, uid, env