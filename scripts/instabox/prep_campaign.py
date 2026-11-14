#!/usr/bin/env python3
"""Gate + launcher for the article-outline chatbot panel (instabox Hermes cron).

Prints a compact status block the cron agent reads:

  WAITING             - no panel folder dropped on the desktop yet
  LAUNCHED <folder>   - a fresh bot run was just started in the background
  RUNNING <folder>    - a bot run for this folder is still going
  READY <folder>      - the bot run finished; answer files are on disk
  FAILED <reason>     - the run died or the folder is malformed
"""
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

RUN_DIR = "/data/workspace/chatbot-run"
CHROME_PROFILE = "/data/workspace/chrome-cdp-profile"
DESKTOP = "/data/home/Desktop"
PROMPT_SRC = os.path.join(RUN_DIR, "panel_prompt.txt")
STATE = os.path.join(RUN_DIR, "current.json")


def newest_panel_folder():
    cands = []
    for p in glob.glob(os.path.join(DESKTOP, "*")):
        if not os.path.isdir(p):
            continue
        if "PANEL" not in os.path.basename(p).upper():
            continue
        cands.append((os.path.getmtime(p), p))
    return sorted(cands)[-1][1] if cands else None


def outlines_in(folder):
    return sorted(f for f in glob.glob(os.path.join(folder, "*.txt"))
                  if re.match(r"^outline\d", os.path.basename(f), re.I))


def report_in(folder):
    for f in glob.glob(os.path.join(folder, "*.txt")) + glob.glob(os.path.join(folder, "*.md")):
        b = os.path.basename(f).upper()
        if b.startswith("OUTLINE") or b == "PROMPT.TXT":
            continue
        if "REPORT" in b or "SELECTION" in b:
            return f
    return None


def close_chrome():
    """Close the CDP Chrome this job drives so it is not left running on the box."""
    try:
        subprocess.run(["pkill", "-f", "user-data-dir=" + CHROME_PROFILE], timeout=20,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False


def read_json(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception:
        return {}


def emit_ready(folder, outdir, report, outlines):
    print(f"READY {folder}")
    print(f"OUTDIR {outdir}")
    print(f"STATUS {os.path.join(outdir, 'status.json')}")
    print(f"REPORT {report}")
    for o in outlines:
        print(f"OUTLINE {o}")


def main():
    folder = newest_panel_folder()
    if not folder:
        print("WAITING no PANEL folder on the box desktop")
        return

    outlines = outlines_in(folder)
    report = report_in(folder)
    if len(outlines) != 3 or not report:
        print(f"WAITING {folder} has {len(outlines)} outlines, report={bool(report)}")
        return

    if os.path.exists(os.path.join(folder, ".report-sent")):
        close_chrome()
        print(f"ALREADY_SENT {folder}")
        print("The panel report for this folder was already written and emailed.")
        return

    done_marker = os.path.join(folder, ".bots-done")
    outdir_file = os.path.join(folder, ".outdir")
    outdir = open(outdir_file).read().strip() if os.path.exists(outdir_file) else ""

    if os.path.exists(done_marker) and outdir:
        close_chrome()
        emit_ready(folder, outdir, report, outlines)
        return

    state = read_json(STATE)
    same = state.get("folder") == folder

    if same and state.get("pid") and pid_alive(state["pid"]):
        print(f"RUNNING {folder}")
        print(f"OUTDIR {state.get('out')}")
        print(f"STATUS {os.path.join(state.get('out') or '', 'status.json')}")
        return

    if same and state.get("out"):
        st = read_json(os.path.join(state["out"], "status.json"))
        if st.get("done"):
            open(done_marker, "w").write("done")
            if not outdir:
                open(outdir_file, "w").write(state["out"])
            close_chrome()
            emit_ready(folder, state["out"], report, outlines)
            return
        close_chrome()
        print(f"FAILED bot run died before finishing; status={os.path.join(state['out'], 'status.json')}")
        print(f"FOLDER {folder}")
        return

    if not os.path.exists(PROMPT_SRC):
        print(f"FAILED prompt file missing at {PROMPT_SRC}")
        return

    shutil.copyfile(PROMPT_SRC, os.path.join(folder, "prompt.txt"))

    os.makedirs(os.path.join(RUN_DIR, "logs"), exist_ok=True)
    logf = os.path.join(RUN_DIR, "logs", "panel-launch.log")
    env = dict(os.environ)
    env["DISPLAY"] = ":1"
    with open(logf, "ab") as log:
        proc = subprocess.Popen(
            ["node", os.path.join(RUN_DIR, "bots.mjs"), folder],
            cwd=RUN_DIR, env=env, stdout=log, stderr=log, start_new_session=True,
        )

    newdir = ""
    for _ in range(60):
        cands = sorted(glob.glob(os.path.join(RUN_DIR, "out", "*")), key=os.path.getmtime)
        if cands:
            newest = cands[-1]
            st = os.path.join(newest, "status.json")
            if os.path.exists(st) and read_json(st).get("folder") == folder:
                newdir = newest
                break
        time.sleep(0.5)

    with open(STATE, "w") as fh:
        json.dump({"folder": folder, "out": newdir, "pid": proc.pid,
                   "started": datetime.datetime.utcnow().isoformat()}, fh, indent=1)
    if newdir:
        open(outdir_file, "w").write(newdir)

    print(f"LAUNCHED {folder}")
    print(f"OUTDIR {newdir}")
    print(f"STATUS {os.path.join(newdir, 'status.json')}")
    print(f"REPORT {report}")
    for o in outlines:
        print(f"OUTLINE {o}")


if __name__ == "__main__":
    sys.exit(main())
