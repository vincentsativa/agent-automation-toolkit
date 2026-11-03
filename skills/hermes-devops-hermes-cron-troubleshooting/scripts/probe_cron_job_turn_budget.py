#!/usr/bin/env python3
"""Prove which turn ceiling a cron job actually gets at run construction.

Why: `_resolve_cron_agent_setup` is where the iteration cap is decided, and a job's own
`max_turns` field is easy to persist without ever reading it there. When that happens the
job record advertises a budget it never receives, the run dies at the GLOBAL ceiling
mid-pipeline, and the ledger still reads as a finished run. This probe drives the real
resolver and asserts both directions:

  * a job that carries `max_turns` gets THAT number (override path)
  * a job that does not gets `agent.max_turns` from config (inherit path)

The inherit cases are the guard on the guard: a fix that raises every job to the override
value silently changes every other job on the box, so they must be asserted, not assumed.

Run it under the install venv so the import is real, resolve the interpreter, never
hardcode it:

    grep -o '"/[^"]*environments/[^"]*venv"' ~/.hermes/installs/*/facts.json
    "$ENV_VENV/bin/python3" <skill_dir>/scripts/probe_cron_job_turn_budget.py

A synthetic harness is a floor, not a finish: it proves the resolution logic. Confirm the
real win afterwards by reading the next dispatch's turn-end line in agent.log
(`Turn ended: reason=... api_calls=N/N`) and checking it reports the job's own ceiling.
"""

from __future__ import annotations

import os
import sys

HERMES_HOME = os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes")
SRC_ROOT = os.environ.get("HERMES_PYTHON_SRC_ROOT") or os.path.join(HERMES_HOME, "hermes-agent")
if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)

GLOBAL_TURNS = 90  # what agent.max_turns resolves to in the config used below


def _neutralise_gates(scheduler) -> None:
    """Stub out everything that would need a live provider, credential, or MCP registry,
    so the probe exercises ONLY the turn-budget resolution."""
    scheduler._guard_job_credential_exfil = lambda job: None
    scheduler._preflight_or_block = lambda job, job_id, name, cfg: None
    scheduler._resolve_job_runtime = lambda job, job_id, jc: ({"provider": "probe"}, "probe-model")
    scheduler._resolve_job_reasoning_config = lambda job, cfg, model: None
    scheduler._job_fallback_chain = lambda job, cfg: None
    scheduler._load_credential_pool = lambda runtime, job_id: None
    scheduler._init_cron_mcp_tools = lambda job_id: None
    scheduler._cron_preflight_enabled = lambda cfg: False
    scheduler._load_prefill_messages = lambda cfg, job_id: None


def main() -> int:
    try:
        import cron.scheduler as scheduler
    except Exception as exc:  # noqa: BLE001 - report, never traceback into a cron report
        print("cannot import cron.scheduler from %s: %s" % (SRC_ROOT, exc))
        return 2

    _neutralise_gates(scheduler)

    class StubJC:
        def __init__(self) -> None:
            self.cfg = {"agent": {"max_turns": GLOBAL_TURNS}}
            self.model = "probe-model"

    def resolved(job: dict):
        return scheduler._resolve_cron_agent_setup(job, "probe-job", "probe", StubJC()).max_iterations

    cases = [
        ("job carries max_turns 200", {"max_turns": 200}, 200),
        ("job carries max_turns 300", {"max_turns": 300}, 300),
        ("job carries no max_turns (inherits global)", {}, GLOBAL_TURNS),
        ("job carries None (inherits global)", {"max_turns": None}, GLOBAL_TURNS),
    ]

    failures = 0
    for label, job, want in cases:
        try:
            got = resolved(job)
        except Exception as exc:  # noqa: BLE001
            print("%-45s want=%-5s RAISED %s" % (label, want, exc))
            failures += 1
            continue
        ok = got == want
        failures += 0 if ok else 1
        print("%-45s want=%-5s got=%-5s %s" % (label, want, got, "PASS" if ok else "FAIL"))

    if failures:
        print("\nRESULT: %d case(s) FAILED, the job's own max_turns is not the value the run gets." % failures)
    else:
        print("\nRESULT: ALL PASS, per-job override wins, absent field still inherits the global.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
