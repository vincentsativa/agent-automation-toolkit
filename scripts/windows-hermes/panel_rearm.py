#!/usr/bin/env python3
"""Re-arm the panel launcher job before its 16:40 poll window.

The launcher (f0a3c8a37dfc) pauses itself once the day's panel is complete and
emailed. This job resumes it every day at 16:35 and clears the pause marker.
Prints nothing, so the delivery is silent.
"""
import datetime
import os
import subprocess

HERMES = r"C:\Users\<user>\AppData\Local\hermes\bin\hermes.cmd"
JOB = "f0a3c8a37dfc"
STATE = r"C:\Users\<user>\AppData\Local\hermes\state"
FLAG = os.path.join(STATE, "panel_paused.flag")


def main():
    try:
        r = subprocess.run([HERMES, "cron", "resume", JOB], capture_output=True, text=True, timeout=180)
        out = (r.stdout or "").strip()
    except Exception as e:
        print("PANEL RE-ARM FAILED: " + str(e))
        return 1
    try:
        if os.path.exists(FLAG):
            os.remove(FLAG)
    except Exception:
        pass
    if r.returncode != 0:
        print("PANEL RE-ARM FAILED rc=" + str(r.returncode) + " " + (out[-200:] or (r.stderr or "")[-200:]))
        return 1
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    with open(os.path.join(STATE, "panel_rearm.log"), "a") as fh:
        fh.write(stamp + " resumed " + JOB + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
