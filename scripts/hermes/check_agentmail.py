#!/usr/bin/env python3
"""
check_agentmail.py, EMAIL TASK PROCESSOR script gate for Frank (Agent 2).

Checks Frank's AgentMail inbox ([REDACTED_EMAIL]) for UNREAD threads.
If there is unread mail, prints the list of unread threads so the cron agent
processes them. If there is no unread mail, prints nothing (silent), so the
cron stays quiet and no notification fires.

Exit code 0 always (unless an API/config error occurs).

Interpreter note (why ``_activate_project_dependencies`` exists): cron runs a no_agent
script with the GATEWAY's ``sys.executable`` (cron/scheduler_script.py::_script_argv),
and after a managed-runtime update that interpreter is the bare toolchain Python
(``~/.hermes/tools/python-<ver>/bin/python3``), whose site-packages holds only pip.
The project's real dependency tree lives in the install venv and reaches a process only
when ``pm.environments.activate_dependencies`` runs at boot, which the Hermes entry
points do and a standalone cron script does not. Without this call the config fallback
below never reaches PyYAML and silently degrades to the regex path.

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

    Never raises and never changes ``sys.executable``: if PM is unavailable the script
    falls back to the interpreter's own packages and the regex path below, which is
    exactly the previous behaviour.
    """
    src_root = os.environ.get("HERMES_PYTHON_SRC_ROOT")
    if not src_root or not os.path.isdir(src_root):
        home = os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes")
        candidate = os.path.join(home, "hermes-agent")
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


def get_api_key():
    """Read AGENTMAIL_API_KEY from env, then config.yaml fallback."""
    key = os.environ.get("AGENTMAIL_API_KEY")
    if key:
        return key.strip()
    # Fallback: parse ~/.hermes/config.yaml mcp_servers.agentmail.env
    cfg_path = os.path.expanduser("~/.hermes/config.yaml")
    raw = None
    try:
        with open(cfg_path) as f:
            raw = f.read()
    except Exception as e:
        print(f"ERROR: could not read {cfg_path}: {e}", file=sys.stderr)
        sys.exit(1)
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
        # Stdlib-only fallback: the cron interpreter may have no PyYAML,
        # so pull the key from the mcp_servers block with a regex instead.
        import re
        m = re.search(r"mcp_servers:.*?AGENTMAIL_API_KEY:\s*(\S+)", raw, re.S)
        if m:
            return m.group(1).strip().strip("'\"")
    except Exception as e:
        print(f"ERROR: could not parse API key from {cfg_path}: {e}", file=sys.stderr)
        sys.exit(1)
    print("ERROR: AGENTMAIL_API_KEY not found in env or config.yaml", file=sys.stderr)
    sys.exit(1)

def api_get(path):
    """GET an AgentMail API endpoint, return parsed JSON."""
    req = urllib.request.Request(f"{API}{path}", headers={
        "Authorization": f"Bearer {get_api_key()}",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"ERROR: AgentMail API GET {path} failed: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    _activate_project_dependencies()
    # List threads, filter to unread ones.
    data = api_get(f"/inboxes/{INBOX}/threads")
    threads = data.get("threads", data if isinstance(data, list) else [])
    unread = []
    for t in threads:
        labels = [l.lower() for l in t.get("labels", [])]
        # A thread is unread if it has an 'unread' label or the last message is unread.
        last = (t.get("last_message") or {})
        last_labels = [l.lower() for l in last.get("labels", [])]
        if "unread" in labels or "unread" in last_labels:
            unread.append({
                "thread_id": t.get("id"),
                "subject": t.get("subject") or "(no subject)",
                "from": t.get("from") or last.get("from") or "(unknown)",
                "last_snippet": (last.get("text") or t.get("last_snippet") or "")[:200],
            })

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
