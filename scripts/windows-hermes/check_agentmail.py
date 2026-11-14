#!/usr/bin/env python3
"""
check_agentmail.py, EMAIL TASK PROCESSOR script gate for Karma (Agent 3, Windows).

Checks Karma's AgentMail inbox ([REDACTED_EMAIL]) for UNREAD threads.
If there is unread mail, prints the list of unread threads so the cron agent
processes them. If there is no unread mail, prints nothing meaningful
("wakeAgent:false"), so the cron stays quiet and no notification fires.

Exit code 0 always (unless an API/config error occurs).

Interpreter note: cron runs a script with the GATEWAY's sys.executable, which
after a managed-runtime update is the bare toolchain Python whose site-packages
holds only pip. _activate_project_dependencies() below puts the install's real
dependency tree on sys.path so PyYAML is reachable; if that is unavailable the
stdio-only regex fallback still reads the key out of config.yaml.

Usage: python3 check_agentmail.py
"""
import json
import os
import sys
import urllib.request

INBOX = "[REDACTED_EMAIL]"
API = "https://api.agentmail.to/v0"


def _activate_project_dependencies() -> None:
    """Put the install's committed dependency tree on ``sys.path``.

    Never raises and never changes ``sys.executable``: if PM is unavailable the
    script falls back to the interpreter's own packages and the regex path below.
    """
    src_root = os.environ.get("HERMES_PYTHON_SRC_ROOT")
    if not src_root or not os.path.isdir(src_root):
        candidate = os.path.join(_hermes_home(), "hermes-agent")
        src_root = candidate if os.path.isdir(candidate) else None
    if not src_root:
        return
    if src_root not in sys.path:
        sys.path.insert(0, src_root)
    try:
        from pathlib import Path

        from pm.environments import activate_dependencies

        activate_dependencies(Path(src_root))
    except Exception:
        pass


def _hermes_home() -> str:
    """Resolve HERMES_HOME: env var, then the parent of this script's dir.

    This script lives at <HERMES_HOME>/scripts/check_agentmail.py, so the
    install root is always two levels up regardless of the OS/user profile.
    """
    env = os.environ.get("HERMES_HOME")
    if env and os.path.isdir(env):
        return env
    derived = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.isdir(derived):
        return derived
    return os.path.expanduser("~/.hermes")


def get_api_key():
    """Read AGENTMAIL_API_KEY from env, then config.yaml fallback."""
    key = os.environ.get("AGENTMAIL_API_KEY")
    if key:
        return key.strip()
    cfg_path = os.path.join(_hermes_home(), "config.yaml")
    raw = None
    try:
        with open(cfg_path, encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        print(f"ERROR: could not read {cfg_path}: {e}", file=sys.stderr)
        return None
    try:
        import yaml

        cfg = yaml.safe_load(raw) or {}
        key = (
            (cfg.get("mcp_servers") or {})
            .get("agentmail", {})
            .get("env", {})
            .get("AGENTMAIL_API_KEY")
        )
        if key:
            return str(key).strip()
    except ImportError:
        # Stdlib-only fallback: the cron interpreter may have no PyYAML, so pull
        # the key from the mcp_servers block with a regex instead.
        import re

        m = re.search(r"mcp_servers:.*?AGENTMAIL_API_KEY:\s*(\S+)", raw, re.S)
        if m:
            return m.group(1).strip().strip("'\"")
    except Exception as e:
        print(f"ERROR: could not parse API key from {cfg_path}: {e}", file=sys.stderr)
        return None
    print("ERROR: AGENTMAIL_API_KEY not found in env or config.yaml", file=sys.stderr)
    return None


def api_get(path, key):
    """GET an AgentMail API endpoint, return parsed JSON (or None on error)."""
    req = urllib.request.Request(
        f"{API}{path}",
        headers={
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"ERROR: AgentMail API GET {path} failed: {e}", file=sys.stderr)
        return None


def main():
    _activate_project_dependencies()
    key = get_api_key()
    if not key:
        # Fail loud on config errors so a broken gate is visible, not silent.
        sys.exit(1)

    data = api_get(f"/inboxes/{INBOX}/threads", key)
    if data is None:
        sys.exit(1)
    threads = data.get("threads", data if isinstance(data, list) else [])

    unread = []
    for t in threads:
        labels = [l.lower() for l in t.get("labels", [])]
        last = t.get("last_message") or {}
        last_labels = [l.lower() for l in last.get("labels", [])]
        if "unread" in labels or "unread" in last_labels:
            senders = t.get("senders") or t.get("from") or last.get("from") or []
            if isinstance(senders, list):
                sender = ", ".join(str(s) for s in senders) or "(unknown)"
            else:
                sender = str(senders)
            snippet = last.get("text") or t.get("preview") or t.get("last_snippet") or ""
            unread.append(
                {
                    "thread_id": t.get("thread_id") or t.get("id") or t.get("threadId"),
                    "subject": t.get("subject") or "(no subject)",
                    "from": sender,
                    "last_snippet": str(snippet)[:200],
                }
            )

    if not unread:
        # Nothing to process, stay silent so the cron does not fire.
        print("wakeAgent:false")
        return

    print(f"wakeAgent:true, {len(unread)} unread thread(s) in {INBOX}:")
    for u in unread:
        print("-" * 60)
        print(f"thread_id: {u['thread_id']}")
        print(f"subject:   {u['subject']}")
        print(f"from:      {u['from']}")
        print(f"snippet:   {u['last_snippet']}")


if __name__ == "__main__":
    main()
