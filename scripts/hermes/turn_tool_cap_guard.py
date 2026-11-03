#!/usr/bin/env python3
"""pre_tool_call shell hook: per-TURN tool-call cap.

WHY
---
Hermes ships no per-turn total tool-call ceiling. `tool_loop_guardrails.loop_caps`
covers only `max_web_searches` and `max_subagents`; the failure-based thresholds
fire on repeated FAILURES or identical REPLAYS, never on "many different
successful calls". Measured from ~/.hermes/state.db (4,263 turns): the median
interactive turn is 3 tool calls, p90 is 18, p99 is 49, and the worst is 120.
The tail is the failure Vinny sees: a one-line question turned into a long
silent pipeline instead of an answer.

WHAT IT DOES
------------
Counts tool calls in the CURRENT conversation turn (keyed on session_id +
turn_id, with a rolling-window fallback when turn_id is absent) and blocks the
call once the cap is passed. The block message tells the model to answer with
what it already has. Blocking one tool call never ends the turn.

THRESHOLDS (measured, not guessed)
----------------------------------
  interactive sessions:  warn at 20, block past 80   (measured median turn is
                         3 calls and p90 is 18; Vinny raised the cap from 50
                         to 60 on 2026-09-20 after a real turn hit 51 and lost
                         its last step, then to 80 on 2026-09-22)
  cron sessions:         warn at 40, never block     (a mid-report block would
                                                      silently truncate a report,
                                                      which is worse than a long turn)

FAILURE MODE
------------
Configured with fail_closed: false. If this script cannot spawn or crashes, the
tool call proceeds and a warning is logged. A broken guard must never brick the
agent; the cost is that a silent crash means no enforcement, which is why
`hermes hooks doctor` is part of the verification.

Wire (agent/shell_hooks.py::_serialize_payload):
  stdin  {"hook_event_name": "pre_tool_call", "tool_name": "...",
          "tool_input": {...}, "session_id": "...", "cwd": "...",
          "profile": "...", "extra": {"turn_id": "...", ...}}
  stdout {"action": "block", "message": "..."}   (or exit 2 + stderr)
"""
import hashlib
import json
import os
import sys
import time

STATE_DIR = os.path.expanduser("~/.hermes/state/turn_tool_caps")
INTERACTIVE_WARN = 20
INTERACTIVE_CAP = 80
CRON_WARN = 40
WINDOW_SECONDS = 1800          # fallback window when turn_id is absent
STALE_AFTER = 7200             # prune entries older than this
MAX_FILES = 400


def _tool_and_ids(payload):
    tool = payload.get("tool_name") or ""
    session = payload.get("session_id") or ""
    extra = payload.get("extra")
    turn = ""
    if isinstance(extra, dict):
        turn = str(extra.get("turn_id") or "")
    return tool, session, turn


def _is_cron(session, payload):
    if session.startswith("cron_"):
        return True
    extra = payload.get("extra")
    if isinstance(extra, dict) and extra.get("cron_session"):
        return True
    return os.environ.get("HERMES_CRON_SESSION", "").strip().lower() in {"1", "true", "yes", "on"}


def _state_path(session, turn):
    if turn:
        key = "%s|%s" % (session, turn)
    else:
        # No turn id: bucket by half-hour so a long session still gets a fresh count
        key = "%s|w%d" % (session, int(time.time() // WINDOW_SECONDS))
    return os.path.join(STATE_DIR, hashlib.sha1(key.encode("utf-8")).hexdigest() + ".json")


def _read_count(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            return 0, None
        first = data.get("first_ts")
        if isinstance(first, (int, float)) and (time.time() - first) > STALE_AFTER:
            return 0, None
        n = data.get("count")
        return (n if isinstance(n, int) and n >= 0 else 0), first
    except (OSError, ValueError):
        return 0, None


def _write_count(path, count, first_ts):
    tmp = "%s.tmp.%d" % (path, os.getpid())
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"count": count, "first_ts": first_ts, "last_ts": time.time()}, fh)
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def _prune():
    try:
        entries = sorted(
            (os.path.join(STATE_DIR, n) for n in os.listdir(STATE_DIR)),
            key=os.path.getmtime, reverse=True,
        )
    except OSError:
        return
    for p in entries[MAX_FILES:]:
        try:
            os.unlink(p)
        except OSError:
            pass


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict) or payload.get("hook_event_name") != "pre_tool_call":
        return 0

    tool, session, turn = _tool_and_ids(payload)
    if not session:
        return 0

    cron = _is_cron(session, payload)
    warn_at = CRON_WARN if cron else INTERACTIVE_WARN
    cap = None if cron else INTERACTIVE_CAP

    try:
        os.makedirs(STATE_DIR, exist_ok=True)
    except OSError:
        return 0

    path = _state_path(session, turn)
    count, first_ts = _read_count(path)
    count += 1
    if first_ts is None:
        first_ts = time.time()
    _write_count(path, count, first_ts)
    if count % 25 == 0:
        _prune()

    if cap is not None and count > cap:
        sys.stderr.write(
            "turn tool-call cap reached: %d calls in this turn (cap %d, tool=%s). "
            "Answer with what you already have.\n" % (count, cap, tool)
        )
        print(json.dumps({
            "action": "block",
            "message": (
                "BLOCKED BY TURN GUARD: you have now made %d tool calls in this single turn "
                "(the ceiling is %d). No more tool calls will run this turn. Stop gathering and "
                "reply to the user now with the result you already have. If something is genuinely "
                "missing, say exactly what is missing in one line."
            ) % (count, cap),
        }))
        return 0

    if count == warn_at:
        sys.stderr.write(
            "turn tool-call notice: %d calls in this turn (warn at %d, cap %s)\n"
            % (count, warn_at, cap)
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
