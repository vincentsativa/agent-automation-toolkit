#!/usr/bin/env python3
"""Audit every cron script for imports the cron interpreter cannot satisfy.

Why: a no_agent cron job runs ``sys.executable <script>`` (cron/scheduler_script.py::
_script_argv), and that interpreter is the gateway's own, on this box the standalone
managed toolchain under ~/.hermes/tools/python-<ver>/bin/python3, whose site-packages
holds only pip. The project's real dependencies live in the install venv. A script that
imports ``yaml``, ``ruamel.yaml``, or a Hermes module without bootstrapping the install's
site-packages crashes and prints an alert that reads like a regression in the thing it
was checking.

Run it WITH the toolchain python (the interpreter cron actually uses):

    ~/.hermes/tools/python-<ver>-<platform>/bin/python3 \
        <skill_dir>/scripts/audit_cron_script_imports.py

The report is a list of scripts and their missing top-level modules. Any script listed is
a latent false alarm; fix it by making the script call
``pm.environments.activate_dependencies`` at the top of main() (see SKILL.md) or by
keeping it stdlib-only. Report findings; fix only what you were ordered to fix.

Stdlib-only on purpose: it must be runnable by the very interpreter whose gaps it finds.
"""

from __future__ import annotations

import ast
import importlib.util
import os
import sys

SCRIPTS_DIR = os.path.join(
    os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes"), "scripts"
)


def top_level_modules(path: str) -> set[str]:
    """Top-level modules a file imports, at any nesting depth (so try/except fallbacks
    that swallow the ImportError are still counted, a fallback hides the gap)."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            tree = ast.parse(fh.read())
    except (OSError, SyntaxError):
        return set()
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            mods.add(node.module.split(".")[0])
    return mods


def main() -> int:
    if not os.path.isdir(SCRIPTS_DIR):
        print("no scripts dir at %s" % SCRIPTS_DIR)
        return 0
    print("interpreter: %s" % sys.executable)
    print("scripts dir: %s\n" % SCRIPTS_DIR)
    flagged = 0
    for name in sorted(os.listdir(SCRIPTS_DIR)):
        if not name.endswith(".py"):
            continue
        path = os.path.join(SCRIPTS_DIR, name)
        missing = [m for m in sorted(top_level_modules(path)) if importlib.util.find_spec(m) is None]
        if missing:
            flagged += 1
            print("MISSING  %-40s %s" % (name, ", ".join(missing)))
    if not flagged:
        print("ok, every cron script imports only what this interpreter carries")
    else:
        print("\n%d script(s) will crash or silently take a fallback under this interpreter." % flagged)
    return 0


if __name__ == "__main__":
    sys.exit(main())
