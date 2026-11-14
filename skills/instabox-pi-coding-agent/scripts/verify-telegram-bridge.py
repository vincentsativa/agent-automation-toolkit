#!/usr/bin/env python3
"""Probe pi's Telegram bridge: systemd unit, state.json, live getMe.

Exits 0 when healthy, 1 with the failing checks listed otherwise.
Prints only verification outcomes, never the bot token or bus secret.
"""
import json
import os
import subprocess
import sys
import urllib.request

AGENT = os.path.expanduser("~/.pi/agent")
STATE = os.path.join(AGENT, "tmp", "pi-telegram", "state.json")
TELEGRAM = os.path.join(AGENT, "telegram.json")

def unit_active():
    try:
        out = subprocess.run(
            ["systemctl", "--user", "is-active", "pi-telegram.service"],
            capture_output=True, text=True, timeout=15,
        )
        return out.stdout.strip()
    except Exception as exc:
        return f"query-failed: {exc}"

def main():
    problems = []

    unit = unit_active()
    print(f"unit={unit}")
    if unit != "active":
        problems.append(f"pi-telegram.service is {unit}")

    try:
        with open(STATE, encoding="utf-8") as fh:
            profile = json.load(fh)["profiles"]["default"]
    except Exception as exc:
        print(f"state.json unreadable: {exc}")
        problems.append("state.json unreadable")
        profile = None

    if profile:
        pid = profile.get("transport", {}).get("pid")
        runtime = profile.get("runtime", {}).get("runtime", {}) or {}
        polling = runtime.get("pollingActive")
        polling_info = runtime.get("polling") or {}
        phase = polling_info.get("phase")
        reason = polling_info.get("stopReason")
        lock = runtime.get("lockState")
        alive = bool(pid) and os.path.exists(f"/proc/{pid}")
        print(f"pid={pid} alive={alive} pollingActive={polling} phase={phase} stopReason={reason} lock={lock}")
        if not alive:
            problems.append(f"bridge pid {pid} not running")
        if polling is not True:
            problems.append(f"polling not active (phase={phase}, stopReason={reason})")
        if lock != "active here":
            problems.append(f"lock is {lock!r}, expected 'active here'")

    try:
        with open(TELEGRAM, encoding="utf-8") as fh:
            token = json.load(fh)["profiles"]["default"]["botToken"]
        with urllib.request.urlopen(
            f"https://api.telegram.org/bot{token}/getMe", timeout=15
        ) as resp:
            result = json.load(resp)
        bot = (result.get("result") or {}).get("username")
        print(f"getMe ok={result.get('ok')} bot=@{bot}")
        if not result.get("ok") or not bot:
            problems.append("getMe returned not-ok")
    except Exception as exc:
        problems.append(f"getMe failed: {exc}")

    if problems:
        print("UNHEALTHY: " + "; ".join(problems))
        return 1
    print("healthy")
    return 0

if __name__ == "__main__":
    sys.exit(main())
