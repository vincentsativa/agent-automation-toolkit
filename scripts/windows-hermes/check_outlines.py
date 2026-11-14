#!/usr/bin/env python3
"""Gate for the daily article-outline panel run (Windows Hermes cron).

Prints one status block that the cron agent reads. States:

  OUTLINES_NOT_READY n/3      - today's outlines are not all on disk yet; stay silent
  READY_FOR_WRITEUP           - 3 outlines present, no selection report written yet
  REPORT_WRITTEN              - report exists, not pushed to the box yet
  PANEL_PUSHED                - pushed, box is still working; stay silent
  PANEL_COMPLETE              - box sent the report; stay silent
  PANEL_STALLED               - pushed long ago and the box never finished; alert Vinny
  WRITEUP_MISSING             - the writeup was already ordered today and the report is
                                still not on disk; alert instead of ordering a second pick
"""
import datetime
import glob
import subprocess
import json
import os
import re
import sys

DATA = r"C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES"
STATE_DIR = r"C:\Users\<user>\AppData\Local\hermes\state"
BOX_ENV = r"C:/Users/<user>/.pi/agent/skills/instabox/instabox.env"
MACHINE = "m_agqyslvrg433nydcum6oqxyadm"
BOX_POINTS = "https://api.instabox.sh"
STALL_MINUTES = 45
HERMES = r"C:\Users\<user>\AppData\Local\hermes\bin\hermes.cmd"
SELF_JOB = "f0a3c8a37dfc"
PAUSED_FLAG = r"C:\Users\<user>\AppData\Local\hermes\state\panel_paused.flag"


def pause_self():
    """Park this launcher job until the re-arm job resumes it tomorrow."""
    try:
        r = subprocess.run([HERMES, "cron", "pause", SELF_JOB], capture_output=True, text=True, timeout=120)
        out = (r.stdout or "").strip()[:200]
        with open(PAUSED_FLAG, "w") as fh:
            fh.write(datetime.datetime.now().isoformat() + " rc=" + str(r.returncode) + " " + out + "\n")
        return r.returncode
    except Exception as e:
        with open(PAUSED_FLAG, "w") as fh:
            fh.write("pause failed: " + str(e) + "\n")
        return -1


def today():
    return datetime.date.today().isoformat()


def outlines():
    files = glob.glob(os.path.join(DATA, "outline*.txt"))
    keep = [f for f in files if re.match(r"^outline\d", os.path.basename(f), re.I)]
    return sorted(keep)


def report_path():
    return os.path.join(DATA, f"WINDOWS SELECTION REPORT {today()}.txt")


def state_file():
    return os.path.join(STATE_DIR, f"panel_{today()}.json")


def load_state():
    try:
        with open(state_file()) as fh:
            return json.load(fh)
    except Exception:
        return {}


def save_state(st):
    with open(state_file(), "w") as fh:
        json.dump(st, fh, indent=1)


def api_key():
    try:
        with open(BOX_ENV) as fh:
            for line in fh:
                if line.startswith("INSTABOX_API_KEY="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        return ""


def box_marker(box_folder):
    """True if the box wrote .report-sent into the panel folder."""
    import urllib.request
    import urllib.parse
    key = api_key()
    if not key:
        return None
    url = BOX_POINTS + "/v1/machines/" + MACHINE + "/files?path=" + urllib.parse.quote(box_folder)
    req = urllib.request.Request(url, headers={"X-API-Key": key})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            data = json.load(r)
        names = [e.get("name") for e in data.get("entries", [])]
        return ".report-sent" in names
    except Exception:
        return None


def main():
    os.makedirs(STATE_DIR, exist_ok=True)
    if not os.environ.get("FORCE_PANEL_CHECK") and (datetime.datetime.now().hour < 16 or (datetime.datetime.now().hour == 16 and datetime.datetime.now().minute < 40)):
        print("OUTLINES_NOT_READY before 16:40")
        return
    files = outlines()
    st = load_state()
    rep = report_path()
    folder = st.get("box_folder", "")
    marker = box_marker(folder) if (st.get("pushed_at") and folder) else None

    # Completion parks the launcher and depends on the box marker alone, so it is
    # checked before the local outline count: a renamed outline file must not keep
    # the launcher armed after the panel is done.
    if marker and not os.path.exists(PAUSED_FLAG):
        print("PANEL_COMPLETE")
        print(f"BOX_FOLDER {folder}")
        rc = pause_self()
        print("LAUNCHER_PAUSED rc=" + str(rc) + " (re-armed daily at 16:35)")
        return

    if len(files) < 3:
        print(f"OUTLINES_NOT_READY {len(files)}/3")
        for f in files:
            print(f"FOUND {f}")
        return

    if not os.path.exists(rep) and not st.get("pushed_at"):
        # The writeup is ordered exactly once per day. A run that answers in chat
        # without writing the report used to leave this state unchanged, so the
        # next five-minute poll ordered a second pick and delivered it again.
        if st.get("writeup_requested_at"):
            try:
                asked = datetime.datetime.fromisoformat(st["writeup_requested_at"])
                minutes = int((datetime.datetime.now() - asked).total_seconds() / 60.0)
            except Exception:
                minutes = -1
            print("WRITEUP_MISSING")
            print(f"REQUESTED_AT {st['writeup_requested_at']}")
            print(f"MINUTES_AGO {minutes}")
            print(f"REPORT {rep}")
            for f in files:
                print(f"OUTLINE {f}")
            return
        st["writeup_requested_at"] = datetime.datetime.now().isoformat(timespec="seconds")
        try:
            save_state(st)
        except Exception:
            pass
        print("READY_FOR_WRITEUP")
        print(f"REPORT_TO_WRITE {rep}")
        for f in files:
            print(f"OUTLINE {f}")
        return

    if not st.get("pushed_at"):
        print("REPORT_WRITTEN")
        print(f"REPORT {rep}")
        for f in files:
            print(f"OUTLINE {f}")
        return

    if marker:
        print("PANEL_COMPLETE")
        print(f"BOX_FOLDER {folder}")
        return

    try:
        pushed = datetime.datetime.fromisoformat(st["pushed_at"])
    except Exception:
        pushed = datetime.datetime.now()
    age = (datetime.datetime.now() - pushed).total_seconds() / 60.0
    if age < STALL_MINUTES:
        print("PANEL_PUSHED")
        print(f"BOX_FOLDER {folder}")
        print(f"MINUTES_AGO {int(age)}")
        return

    print("PANEL_STALLED")
    print(f"BOX_FOLDER {folder}")
    print(f"MINUTES_AGO {int(age)}")
    print(f"MARKER_SEEN {marker}")
    if st.get("trigger_output"):
        print("TRIGGER_OUTPUT " + str(st["trigger_output"])[:300])


if __name__ == "__main__":
    sys.exit(main())
