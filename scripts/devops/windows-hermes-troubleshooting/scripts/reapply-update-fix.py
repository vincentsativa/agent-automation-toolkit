#!/usr/bin/env python3
"""Re-apply the Windows `hermes.exe` self-lock fix to gateway/run.py.

The `hermes.exe` shim self-locks during `hermes update` (the launcher stays
resident as the update's parent and holds its own image open without
FILE_SHARE_DELETE), so the update's quarantine step cannot rename it and the
dependency sync dies with os error 32 / PermissionError.

The permanent fix makes `_resolve_hermes_bin()` prefer
`[sys.executable, "-m", "hermes_cli.main"]` over the `hermes.exe` shim on
Windows. This is a LOCAL patch to the checkout — every `git pull` / ZIP update
overwrites it, so run this script after any update that touches gateway/run.py.

Idempotent: exits 0 with "already patched" if the marker is present.

Usage:
    python reapply-update-fix.py [path/to/gateway/run.py]

If no path is given, it auto-locates the Windows checkout at
%LOCALAPPDATA%\\hermes\\hermes-agent\\gateway\\run.py (or the WSL checkout at
~/.hermes/hermes-agent/gateway/run.py when running under WSL).
"""

import os
import sys
from pathlib import Path

MARKER = "hermes.exe shim self-locks"

WINDOWS_BRANCH = '''    import shutil

    # Windows: the hermes.exe shim self-locks during update (see docstring).
    # Prefer the module invocation so no hermes.exe process holds the file.
    if sys.platform == "win32":
        try:
            import importlib.util

            if importlib.util.find_spec("hermes_cli") is not None:
                return [sys.executable, "-m", "hermes_cli.main"]
        except Exception:
            pass

    hermes_bin = shutil.which("hermes")
'''


def _default_path() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", "")
        if base:
            return Path(base) / "hermes" / "hermes-agent" / "gateway" / "run.py"
    home = Path.home()
    return home / ".hermes" / "hermes-agent" / "gateway" / "run.py"


def _find_function_end(lines: list[str], start_idx: int) -> int:
    """Return the index of the last line of the function starting at start_idx.

    The function body is indented; the function ends at the first line at
    column 0 (a new top-level def/import/etc.) after the def line.
    """
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if line.strip() == "":
            continue
        if not line[0].isspace():
            return i - 1
    return len(lines) - 1


def apply(path: Path) -> str:
    text = path.read_text(encoding="utf-8")

    if MARKER in text:
        return "already patched"

    lines = text.splitlines(keepends=True)

    # Locate the function definition.
    def_idx = None
    for i, line in enumerate(lines):
        if line.startswith("def _resolve_hermes_bin()"):
            def_idx = i
            break
    if def_idx is None:
        return "ERROR: could not find `def _resolve_hermes_bin()`"

    end_idx = _find_function_end(lines, def_idx)

    # Locate the `import shutil` statement inside the function body.
    import_idx = None
    for i in range(def_idx + 1, end_idx + 1):
        if lines[i].strip() == "import shutil":
            import_idx = i
            break
    if import_idx is None:
        return "ERROR: could not find `import shutil` inside the function"

    # Replace the `import shutil` line (and the following `hermes_bin = ...`
    # line if present) with the Windows-preferring block.
    # Find the `hermes_bin = shutil.which("hermes")` line to bound the swap.
    hermes_bin_idx = None
    for i in range(import_idx + 1, end_idx + 1):
        if "hermes_bin = shutil.which" in lines[i]:
            hermes_bin_idx = i
            break

    if hermes_bin_idx is None:
        # Fallback: just insert the Windows branch after `import shutil`.
        new_lines = (
            lines[: import_idx + 1]
            + [WINDOWS_BRANCH.splitlines(keepends=True)[0] + "\n"]
            + WINDOWS_BRANCH.splitlines(keepends=True)[1:]
            + lines[import_idx + 1 :]
        )
    else:
        # Replace from `import shutil` through `hermes_bin = ...` inclusive.
        new_lines = (
            lines[:import_idx]
            + WINDOWS_BRANCH.splitlines(keepends=True)
            + lines[hermes_bin_idx + 1 :]
        )

    path.write_text("".join(new_lines), encoding="utf-8")
    return "patched"


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else _default_path()
    if not path.exists():
        print(f"ERROR: {path} does not exist")
        return 1

    result = apply(path)
    print(f"{result}: {path}")

    if result.startswith("ERROR"):
        return 1

    # Verify the patched file still compiles.
    import py_compile

    try:
        py_compile.compile(str(path), doraise=True)
        print("compile check: OK")
    except py_compile.PyCompileError as exc:
        print(f"compile check: FAILED — {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
