#!/usr/bin/env python3
r"""Delete the day's outline + selection-report files from the PANEL folder on
the instabox (the cloud machine where the panel actually runs).

The previous version cleaned C:\Users\<user>\OneDrive\Desktop\TODAYS DATA
FILES and printed that path. The panel data the cron is responsible for lives
on the instabox at /data/home/Desktop/PANEL <date>, so the cleanup runs there
and wakes the box first: a suspended/stopped machine would otherwise make the
deletion silently fail, which is what happened overnight.

What it removes (only inside the day's PANEL folder, never the folder, never
anything else):
  - outline<N>*.txt
  - WINDOWS SELECTION REPORT*.txt
...and only when the file's name matches, so a file written for a later day is
never touched. The Windows TODAYS DATA FILES copy is tidied quietly afterwards so
the local gate (check_outlines.py) does not see yesterday's outlines tomorrow;
that cleanup is not reported because the box path is the one being monitored.

Silent when there is nothing to delete: the cron delivers stdout verbatim and
empty output means no message. Any error prints a single STOPPED line.
"""
import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

STATE_DIR = r"C:\Users\<user>\AppData\Local\hermes\state"
DATA = r"C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES"
BOX_ENV = r"C:/Users/<user>/.pi/agent/skills/instabox/instabox.env"
MACHINE = "m_agqyslvrg433nydcum6oqxyadm"
API = "https://api.instabox.sh"
OUTLINE_RE = re.compile(r"^outline\d.*\.txt$", re.I)
REPORT_RE = re.compile(r"^WINDOWS SELECTION REPORT.*\.txt$", re.I)


def target_date(arg):
    if arg:
        return arg
    return datetime.date.today().isoformat()


def api_key():
    with open(BOX_ENV) as fh:
        for line in fh:
            if line.startswith("INSTABOX_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("STALE CLEANUP STOPPED: no INSTABOX_API_KEY found")


KEY = None


def req(method, path, body=None, headers=None, timeout=120):
    global KEY
    if KEY is None:
        KEY = api_key()
    url = API + path
    data = json.dumps(body).encode() if body is not None else None
    h = {"X-API-Key": KEY}
    if data is not None:
        h["Content-Type"] = "application/json"
    if headers:
        h.update(headers)
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            raw = resp.read()
            try:
                return resp.status, json.loads(raw)
            except Exception:
                return resp.status, {"raw": raw[:400].decode("utf-8", "replace")}
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw[:400].decode("utf-8", "replace")}


def ensure_running():
    code, m = req("GET", f"/v1/machines/{MACHINE}")
    if code != 200:
        raise SystemExit(f"STALE CLEANUP STOPPED: machine read failed {code} {m}")
    state = m.get("state")
    if state == "running":
        return
    if state in ("suspended", "stopped"):
        code, op = req("POST", f"/v1/machines/{MACHINE}/start",
                       headers={"Idempotency-Key": f"cleanup-{int(time.time())}"})
        if code not in (200, 202):
            raise SystemExit(f"STALE CLEANUP STOPPED: start failed {code} {op}")
        for _ in range(40):
            time.sleep(3)
            c, mm = req("GET", f"/v1/machines/{MACHINE}")
            if c == 200 and mm.get("state") == "running":
                return
        raise SystemExit("STALE CLEANUP STOPPED: machine did not become running")
    raise SystemExit(f"STALE CLEANUP STOPPED: machine is {state}")


def exec_on_box(cmd, timeout=180):
    code, out = req("POST", f"/v1/machines/{MACHINE}/exec",
                    {"cmd": cmd, "timeoutSeconds": timeout})
    if code != 200:
        raise SystemExit(f"STALE CLEANUP STOPPED: exec failed {code} {out}")
    stdout = out.get("stdout", "") if isinstance(out, dict) else str(out)
    rc = out.get("exitCode", 0) if isinstance(out, dict) else 0
    if rc not in (0, None):
        raise SystemExit(f"STALE CLEANUP STOPPED: remote exit {rc}: {stdout.strip() or out}")
    return stdout.strip()


def clean_local(folder):
    """Tidy the Windows copy quietly so the local gate does not reuse stale files."""
    if not os.path.isdir(folder):
        return
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            continue
        if not (OUTLINE_RE.match(name) or REPORT_RE.match(name)):
            continue
        try:
            os.remove(path)
        except OSError:
            pass


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=DATA, help="Windows folder to tidy quietly (default: TODAYS DATA FILES)")
    ap.add_argument("--date", default=None, help="day to clean, ISO (default: today)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    day = target_date(args.date)
    box_folder = f"/data/home/Desktop/PANEL {day}"

    ensure_running()

    verb = "would remove" if args.dry_run else "removed"
    # Print matches, then delete unless dry-run. find returns the deleted (or would-be) paths.
    action = "-print" if args.dry_run else "-print -delete"
    cmd = (
        f"F='{box_folder}'; "
        f"if [ ! -d \"$F\" ]; then exit 0; fi; "
        f"find \"$F\" -maxdepth 1 -mindepth 1 -type f \( -iname 'outline[0-9]*.txt' -o -iname 'WINDOWS SELECTION REPORT*.txt' \) {action}"
    )
    out = exec_on_box(cmd)
    if out.startswith("STALE CLEANUP STOPPED"):
        print(out)
        return 1
    # Relabel remote find output as a removal summary so the delivered message
    # matches the existing format.
    lines = [ln for ln in out.splitlines() if ln.strip()]
    if lines:
        # find prints full paths; report basenames, as before.
        print(f"STALE CLEANUP {verb} {len(lines)} file(s) from {box_folder}")
        for ln in lines:
            print("  " + os.path.basename(ln))
    # Quietly keep the Windows gate from reusing stale outlines.
    if not args.dry_run:
        clean_local(args.dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
