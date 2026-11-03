#!/usr/bin/env python3
"""Post-update health check for the write-guard / scratch-path defense.

Runs after the nightly Hermes update. ZERO agent, ZERO tokens: registered as a cron
job with no_agent=True, so stdout is delivered verbatim and nothing is billed.

Contract: print NOTHING when everything is healthy (cron treats empty stdout as a
silent success). Print an alert ONLY when something regressed, so Vinny hears about a
broken update the same night instead of finding a "File-mutation verifier" warning on
his 8AM report.

Exit code: always 0 unless the script itself crashes, so a bad night is a message and
not a cron failure alert.

Interpreter note (why ``_activate_project_dependencies`` exists): cron runs a no_agent
script with the GATEWAY's ``sys.executable`` (cron/scheduler_script.py::_script_argv),
and after a managed-runtime update that interpreter is the bare toolchain Python
(``~/.hermes/tools/python-<ver>/bin/python3``), whose site-packages holds only pip.
The project's real dependency tree lives in the install venv and reaches a process only
when ``pm.environments.activate_dependencies`` runs at boot — which the Hermes entry
points do and a standalone cron script does not. Without this call the probes below
import-crash on ``yaml``/``ruamel.yaml`` and report a HEALTHY install as a regression.
"""
import json
import os
import subprocess
import sys
import tempfile

HERMES_HOME = os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes")
HOOK_SCRIPT = os.path.join(HERMES_HOME, "scripts", "scratch_path_guard.py")
ALLOWLIST = os.path.join(HERMES_HOME, "shell-hooks-allowlist.json")
CONFIG = os.path.join(HERMES_HOME, "config.yaml")
HOOK_COMMAND = "python3 " + HOOK_SCRIPT
JOBS_FILE = os.path.join(HERMES_HOME, "cron", "jobs.json")
SRC_ROOT = os.path.join(HERMES_HOME, "hermes-agent")

problems = []


def note(msg: str) -> None:
    problems.append(msg)


def _activate_project_dependencies() -> None:
    """Put the install's committed dependency tree on ``sys.path``.

    Mirrors what every Hermes entry point does via hermes_bootstrap: import the source
    root, then let PM put the selected environment's site-packages on the path WITHOUT
    re-execing. Never raises and never changes ``sys.executable``: if PM is unavailable
    the script just runs on whatever the interpreter already carries, which is the old
    behaviour.
    """
    src_root = os.environ.get("HERMES_PYTHON_SRC_ROOT")
    if not src_root or not os.path.isdir(src_root):
        candidate = SRC_ROOT
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
        pass  # PM absent or unreadable: fall back to the interpreter's own packages


# --- 1. The guard still exists and still refuses a stale fixed path ---------
def check_guard_behaviour() -> None:
    """The guard is supposed to REFUSE an unread existing file. If it stops refusing,
    upstream removed/changed it and the hook's assumptions need re-checking."""
    sys.path.insert(0, SRC_ROOT)
    try:
        from tools.file_tools_write_guards import _stale_overwrite_blocker
    except Exception as exc:
        note("write-guard module no longer importable (%s: %s). Upstream moved it; "
             "the scratch-path hook needs review." % (type(exc).__name__, exc))
        return

    fd, path = tempfile.mkstemp(prefix="guardprobe_", suffix=".py")
    os.close(fd)
    try:
        with open(path, "w") as fh:
            fh.write("x=1\n")
        task = "update_health_probe_%d" % os.getpid()
        try:
            import tools.file_tools_read_tracking as rt
            with rt._read_tracker_lock:
                rt._read_tracker.pop(task, None)
            blocker = _stale_overwrite_blocker(path, path, task)
        except Exception as exc:
            note("write-guard probe crashed (%s: %s)." % (type(exc).__name__, exc))
            return
        if not blocker:
            note("write-guard no longer refuses an unread existing file. Upstream "
                 "changed it; re-verify the scratch-path hook still applies.")
    finally:
        for p in (path,):
            try:
                os.unlink(p)
            except OSError:
                pass


# --- 2. The hook is wired, allowlisted, and unchanged since approval -------
def check_hook_wiring() -> None:
    if not os.path.exists(HOOK_SCRIPT):
        note("hook script MISSING at %s. Fixed-path writes will be refused again." % HOOK_SCRIPT)
        return

    try:
        # Hermes reads config.yaml through hermes_yaml (ruamel.yaml); PyYAML is
        # excluded from the install on purpose (pyproject: pyyaml = false), so
        # importing "yaml" here only measured the interpreter's stray packages.
        from hermes_yaml import safe_load as load_config
        with open(CONFIG, encoding="utf-8") as fh:
            cfg = load_config(fh) or {}
    except Exception as exc:
        note("could not read config.yaml (%s: %s)." % (type(exc).__name__, exc))
        return

    hooks = cfg.get("hooks") or {}
    entries = hooks.get("pre_tool_call") or []
    wired = any(isinstance(e, dict) and e.get("command") == HOOK_COMMAND for e in entries)
    if not wired:
        note("hook is NOT registered in config.yaml (hooks.pre_tool_call). Registering "
             "it is a 5-line YAML block; fixed-path writes stay refused until then.")

    if not os.path.exists(ALLOWLIST):
        note("hook allowlist file missing — the hook will not register (gateway has no "
             "TTY to approve it). Re-approve: %s" % ALLOWLIST)
        return
    try:
        with open(ALLOWLIST, encoding="utf-8") as fh:
            data = json.load(fh)
        entry = next((e for e in data.get("approvals", [])
                      if e.get("command") == HOOK_COMMAND), None)
    except Exception as exc:
        note("could not parse allowlist (%s: %s)." % (type(exc).__name__, exc))
        return

    if entry is None:
        note("hook is NOT allowlisted — it will silently not register. Re-approve it.")
        return

    # mtime drift: editing the script invalidates consent and the hook stops firing.
    recorded = entry.get("script_mtime_at_approval")
    try:
        from datetime import datetime, timezone
        actual = datetime.fromtimestamp(os.path.getmtime(HOOK_SCRIPT), tz=timezone.utc)
        actual_iso = actual.isoformat().replace("+00:00", "Z")
    except Exception:
        return
    if recorded:
        try:
            a = datetime.fromisoformat(recorded.replace("Z", "+00:00"))
            b = datetime.fromisoformat(actual_iso.replace("Z", "+00:00"))
            if abs((a - b).total_seconds()) > 1:
                note("hook script changed since approval (mtime drift) — it will NOT "
                     "fire. Re-approve it to reactivate.")
        except Exception:
            pass


# --- 3. The hook actually fires and clears a stale fixed path --------------
def check_hook_live() -> None:
    if not os.path.exists(HOOK_SCRIPT):
        return
    path = os.path.join("/tmp", "update_health_probe_helper.py")
    try:
        with open(path, "w") as fh:
            fh.write("print('old')\n")
        payload = {"hook_event_name": "pre_tool_call", "tool_name": "write_file",
                   "tool_input": {"path": path, "content": "print('new')\n"},
                   "session_id": "update_health", "cwd": os.path.expanduser("~"),
                   "profile": "default", "extra": {}}
        proc = subprocess.run([sys.executable, HOOK_SCRIPT],
                              input=json.dumps(payload), capture_output=True,
                              text=True, timeout=30)
        if proc.returncode != 0:
            note("hook exited %d on a synthetic payload (it must exit 0)." % proc.returncode)
    except subprocess.TimeoutExpired:
        note("hook TIMED OUT on a synthetic payload.")
    except Exception as exc:
        note("hook probe failed (%s: %s)." % (type(exc).__name__, exc))
    finally:
        for p in (path,):
            try:
                os.unlink(p)
            except OSError:
                pass
        d, b = os.path.dirname(path), os.path.basename(path)
        try:
            for n in os.listdir(d):
                if n.startswith(b + ".stale-"):
                    os.unlink(os.path.join(d, n))
        except OSError:
            pass


# --- 4. No stale fixed-path scratch files sitting around -------------------
def check_no_stale_scratch() -> None:
    """A leftover fixed-path helper is the thing that trips the guard. Report any that
    have accumulated, so the source (a job writing a fixed name) gets fixed."""
    stale = []
    for name in ("extract_all.py", "extract_batch_all.py", "fetch_all.py",
                 "batch_dl.py", "dedup.py", "dedup2.py", "pb_cats.py"):
        p = os.path.join("/tmp", name)
        if os.path.exists(p):
            stale.append(p)
    for name in os.listdir(os.path.expanduser("~")):
        if name.startswith("send_") and name.endswith(".py"):
            stale.append(os.path.join(os.path.expanduser("~"), name))
    if stale:
        note("stale fixed-path scratch files present (%d): %s — a job is still writing a "
             "fixed name. Confirm the skills still say to use mktemp -d."
             % (len(stale), ", ".join(sorted(stale)[:6])))


# --- 5. The cron scheduler still honors a per-job max_turns ----------------
def _probe_resolution(job: dict, cfg: dict):
    """Drive the REAL _resolve_cron_agent_setup with every side-effecting gate stubbed.

    Returns the resolved iteration cap, or raises. The stub set is exactly the work that
    needs a live provider, credential pool, or MCP registry; nothing that touches the
    line under test. The module-level import is what makes this an integrity probe: a
    dropped local patch or a rebased-away fix cannot import-crash, so the assertion on
    the returned VALUE is the part that detects the regression.
    """
    import cron.scheduler as S

    class _JC:
        def __init__(self, cfg):
            self.cfg = cfg
            self.model = "probe-model"

    S._guard_job_credential_exfil = lambda j: None
    S._preflight_or_block = lambda j, i, n, c: None
    S._resolve_job_runtime = lambda j, i, jc: ({"provider": "probe"}, "probe-model")
    S._resolve_job_reasoning_config = lambda j, c, m: None
    S._job_fallback_chain = lambda j, c: None
    S._load_credential_pool = lambda r, i: None
    S._init_cron_mcp_tools = lambda i: None
    S._cron_preflight_enabled = lambda c: False
    S._load_prefill_messages = lambda c, i: None
    return S._resolve_cron_agent_setup(job, "health-probe", "health probe", _JC(cfg)).max_iterations


def check_per_job_max_turns() -> None:
    """A job carrying its own ``max_turns`` must resolve to THAT number, while a job
    without one still inherits the global cap.

    This is the probe that catches a clobbered fix. On 2026-10-01 a report-producing job
    stored ``max_turns: 200`` in its record and still ran on the global 90, so it was cut
    off at the ceiling with the report built and the email, the desktop copy, and the DB
    cleanup all unsent. The field existed and the scheduler never read it.
    """
    if not os.path.isdir(SRC_ROOT):
        note("cron scheduler source missing at %s — cannot verify the per-job turn budget."
             % SRC_ROOT)
        return
    if SRC_ROOT not in sys.path:
        sys.path.insert(0, SRC_ROOT)

    cfg = {"agent": {"max_turns": 90}}
    try:
        with_field = _probe_resolution({"max_turns": 200}, cfg)
        without_field = _probe_resolution({}, cfg)
    except Exception as exc:
        note("per-job turn-budget probe could not run (%s: %s). The cron scheduler may "
             "not import at all." % (type(exc).__name__, exc))
        return

    if with_field != 200:
        note("PER-JOB TURN BUDGET REGRESSED: a job asking for max_turns 200 resolved to "
             "%r. The per-job field is being ignored — a heavy cron job will be cut off "
             "at the global agent.max_turns and lose its tail (email, file copy, cleanup). "
             "Re-apply the scheduler fix or check whether upstream PR 120093 / issue 63267 "
             "has landed." % (with_field,))
    if without_field != 90:
        note("per-job turn-budget fallback changed: a job with no max_turns resolved to "
             "%r, expected the global 90. Every cron job's budget moved." % (without_field,))


def main() -> int:
    _activate_project_dependencies()
    check_guard_behaviour()
    check_hook_wiring()
    check_hook_live()
    check_no_stale_scratch()
    check_per_job_max_turns()

    if not problems:
        return 0  # silent success

    print("⚠️ Hermes update check: %d problem(s) found\n" % len(problems))
    for i, p in enumerate(problems, 1):
        print("%d. %s" % (i, p))
    print()
    print("The scratch-path defense (SOUL.md rule + pre_tool_call hook) is what stops "
          "the 'File-mutation verifier' warnings on cron reports. Anything above means "
          "that protection is weakened.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
