#!/usr/bin/env python3
"""Push today's selection report + the 3 outlines to the instabox desktop folder,
then wake the box and trigger the box-side panel cron.

Run:  python push_panel_to_instabox.py
Prints a JSON summary. Exit code 0 = pushed and triggered.
"""
import datetime
import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DATA = r"C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES"
STATE_DIR = r"C:\Users\<user>\AppData\Local\hermes\state"
BOX_ENV = r"C:/Users/<user>/.pi/agent/skills/instabox/instabox.env"
MACHINE = "m_agqyslvrg433nydcum6oqxyadm"
API = "https://api.instabox.sh"
BOX_CRON_NAME = "ARTICLE OUTLINE PANEL - 5 CHATBOTS"
BOX_CRON_ID = "39e77afa6da6"


def api_key():
    with open(BOX_ENV) as fh:
        for line in fh:
            if line.startswith("INSTABOX_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("no INSTABOX_API_KEY found")


KEY = api_key()


def req(method, path, body=None, headers=None, timeout=120):
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
        raise SystemExit(f"machine read failed {code} {m}")
    state = m.get("state")
    if state == "running":
        return "already running"
    if state in ("suspended", "stopped"):
        code, op = req("POST", f"/v1/machines/{MACHINE}/start",
                       headers={"Idempotency-Key": f"panel-{int(time.time())}"})
        if code not in (200, 202):
            raise SystemExit(f"start failed {code} {op}")
        opid = op.get("id") or (op.get("operation") or {}).get("id")
        for _ in range(40):
            time.sleep(3)
            c, mm = req("GET", f"/v1/machines/{MACHINE}")
            if c == 200 and mm.get("state") == "running":
                return "started"
        return "start requested, still not running"
    raise SystemExit(f"machine is {state}; cannot push")


def exec_on_box(cmd, timeout=180):
    code, out = req("POST", f"/v1/machines/{MACHINE}/exec",
                    {"cmd": cmd, "timeoutSeconds": timeout})
    if code != 200:
        return code, out
    return 0, out


def upload(local_path, box_path):
    with open(local_path, "rb") as fh:
        blob = fh.read()
    url = API + f"/v1/machines/{MACHINE}/files?path=" + urllib.parse.quote(box_path) + "&parents=true"
    r = urllib.request.Request(url, data=blob, headers={"X-API-Key": KEY}, method="PUT")
    with urllib.request.urlopen(r, timeout=180) as resp:
        return json.loads(resp.read())


def main():
    os.makedirs(STATE_DIR, exist_ok=True)
    day = datetime.date.today().isoformat()
    rep = os.path.join(DATA, f"WINDOWS SELECTION REPORT {day}.txt")
    if not os.path.exists(rep):
        raise SystemExit(f"report missing: {rep}")
    outs = sorted(f for f in glob.glob(os.path.join(DATA, "outline*.txt"))
                  if re.match(r"^outline\d", os.path.basename(f), re.I))
    if len(outs) != 3:
        raise SystemExit(f"expected 3 outlines, found {len(outs)}")

    print("step: wake", flush=True)
    wake = ensure_running()
    print("step: awake ->", wake, flush=True)

    box_folder = f"/data/home/Desktop/PANEL {day}"
    print("step: mkdir", flush=True)
    code, out = exec_on_box(f"mkdir -p '{box_folder}' && echo ok")
    if code != 0:
        raise SystemExit(f"mkdir failed {code} {out}")

    # Clear yesterday's/test files INSIDE the folder, never the folder itself.
    # A missing folder makes the box cron print WAITING and skip the whole panel,
    # so the folder is the one thing on that desktop that must survive every re-arm.
    print("step: clear stale files (keeping folder)", flush=True)
    code, out = exec_on_box(
        f"find '{box_folder}' -maxdepth 1 -mindepth 1 -type f -delete && "
        f"rm -f '{box_folder}/.report-sent' '{box_folder}/.bots-done' '{box_folder}/.outdir' && "
        f"test -d '{box_folder}' && echo kept-folder")
    if code != 0:
        raise SystemExit(f"stale-clear failed {code} {out}")

    print("step: upload", flush=True)
    uploaded = []
    uploaded.append(upload(rep, f"{box_folder}/{os.path.basename(rep)}"))
    for f in outs:
        uploaded.append(upload(f, f"{box_folder}/{os.path.basename(f)}"))

    print("step: trigger", flush=True)
    # hermes cron run blocks until the job finishes, so detach it or exec never returns
    code, out = exec_on_box(
        "export PATH=$HOME/.local/bin:$PATH; "
        f"nohup hermes cron run {BOX_CRON_ID} > /data/workspace/chatbot-run/logs/cron-trigger.log 2>&1 & "
        "sleep 3; echo triggered")
    trigger = out.get("stdout", "") if isinstance(out, dict) else str(out)

    state = {
        "date": day,
        "pushed_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "box_folder": box_folder,
        "wake": wake,
        "uploaded": [u.get("path") for u in uploaded],
        "trigger_output": trigger.strip()[:500],
        "cron_job": BOX_CRON_ID,
    }
    with open(os.path.join(STATE_DIR, f"panel_{day}.json"), "w") as fh:
        json.dump(state, fh, indent=1)
    print(json.dumps(state, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
