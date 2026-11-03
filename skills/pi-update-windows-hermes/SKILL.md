---
name: update-windows-hermes
description: Update the Windows-native Hermes agent (user `<windows-user>`, AppData\Local\hermes), the install accessible from the MSYS/Windows shell directly, WITHOUT WSL. Use when the user says "update my windows hermes agent", "update the windows hermes", or anything about updating the Hermes agent on Windows. Runs the full update, handles the hermes.exe file-lock problem, snapshots local edits, and repairs the "Telegram/agent stopped working after update" stale-venv ABI failure, then reports truthfully.
---

# Update Windows Hermes Agent

## ⚠️ CRITICAL: There are TWO Hermes installs, use the Windows one here.

| | Windows (THIS ONE) | WSL Ubuntu |
|---|---|---|
| **Who** | user `<windows-user>` on Windows | user `<linux-user>` in WSL |
| **Agent home** | `~\AppData\Local\hermes` | `~/.hermes` |
| **Source repo** | `~\AppData\Local\hermes\hermes-agent` | `~/.hermes/hermes-agent` |
| **Exe / bin** | `~\AppData\Local\hermes\bin\hermes.exe` | `~/.local/bin/hermes` |
| **Gateway** | Scheduled Task `Hermes_Gateway` (usually run manually) | systemd `hermes-gateway` |

**The pi shell runs in MSYS/Windows by default**, so a bare `hermes` command here resolves to THIS (Windows) install. Use the full exe path. Do NOT confuse it with the WSL agent.

> **Use `bin\hermes.exe`, NOT the old `hermes-agent\venv\Scripts\hermes.exe`.** That in-tree venv is retired (pre-PM) and is now quarantined, see failure mode #2. `bin\hermes.exe` is the minted store-Python launcher and is the correct entry point. `hermes version` is **not** a command; use `hermes --version`.

---

## The two venvs (memorize this)

Since the 2026-09 Python migration, this install has a **managed** dependency env and a **retired** in-tree venv:

| | Managed env (correct) | Legacy in-tree venv (RETIRED) |
|---|---|---|
| **Path** | `hermes-agent\..\installs\<key>\environments\<gen>\venv` | `hermes-agent\venv` |
| **Python** | matches the runtime (e.g. 3.14.7) | old (e.g. 3.11.15) |
| **`_pydantic_core`** | `.cp314-win_amd64.pyd` | `.cp311-win_amd64.pyd` |
| **Written by** | `pm` (`hermes pm install` / `update`) | pre-PM installers, abandoned |

The committed env is recorded in `installs\<key>\facts.json` → `packages.venv.environment`. `pm.environments.selected_venv()` returns it. **Any process loading `hermes-agent\venv\Lib\site-packages` is wrong** and will hit ABI failures.

---

## Known failure mode #1: `hermes.exe` gets file-locked

The Windows updater reinstalls its own `hermes.exe`, but the **running gateway / desktop process holds the file open** (`os error 32`). If you see:

```
error: failed to remove file ...\Scripts\hermes.exe ... being used by another process (os error 32)
⚠ Could not quarantine hermes.exe (PermissionError: another process is holding it open)
```

…the dependency sync did NOT finish. The git code may be pulled, but deps are half-installed. Fix it by stopping the gateway (step 4), then re-run the update.

---

## Known failure mode #2: Telegram/agent "stopped working" after a Python upgrade

**This is the most common post-update symptom.** Telegram is *not* actually down, it connects, polls, and logs inbound messages. But **every agent turn fails**, and the bot never replies.

### Symptom

```
ERROR gateway.run: Agent error in session agent:main:telegram:dm:<chat>
ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'

ERROR gateway.run: Supervised task hosted_room_worker died: ModuleNotFoundError("No module named 'pydantic_core._pydantic_core'")
```

### Cause

The update upgraded the runtime Python (e.g. 3.11 → 3.14) and moved deps to the managed env. The retired in-tree `hermes-agent\venv` (cp311 binaries) still exists, and `gateway/run.py` → `_ensure_windows_gateway_venv_imports()` **hardcodes `project_root / "venv"`**, finds it, and **inserts its `Lib\site-packages` at the FRONT of `sys.path`**, shadowing the working 3.14 `pydantic`. The 3.14 interpreter then cannot load the cp311 `_pydantic_core` extension.

Upstream fixed the general case in PR #122161 (“never activate legacy venv”), but **missed this gateway code path**, `origin/main` is still identical as of 2026-09-25. Updating will NOT fix it; the stale venv must be removed.

### Diagnose (quick)

```bash
BASE="~/AppData/Local/hermes"
# 1) Is the retired in-tree venv still present, and what ABI is it?
ls -d "$BASE/hermes-agent/venv" 2>/dev/null && \
  find "$BASE/hermes-agent/venv" -iname "_pydantic_core*" 2>/dev/null

# 2) What did the running gateway actually load?
PID=$(grep -o '"pid": *[0-9]*' "$BASE/gateway.pid" 2>/dev/null | grep -o '[0-9]*')
powershell.exe -NoProfile -Command "Get-Process -Id $PID | Select-Object -ExpandProperty Modules | Where-Object { \$_.FileName -like '*pydantic*' } | Select-Object ModuleName,FileName | Format-Table -Auto -Wrap"
```

If the loaded module is `hermes-agent\venv\...\pydantic_core` (cp311), that's the bug. Optional deeper check, the live gateway env:

```bash
TOOLS_PY="$(ls -d "$BASE"/tools/python-*/ | head -1)python.exe"   # e.g. tools/python-3.14.7+.../python.exe
"$TOOLS_PY" -I -c "
import os,sys
from pathlib import Path
root=r'~\AppData\Local\hermes\hermes-agent'
sys.path.insert(0,root); os.environ['HERMES_HOME']=r'~\AppData\Local\hermes'
from pm.environments import activate_dependencies; activate_dependencies(Path(root))
import psutil; e=psutil.Process(int('$PID')).environ()
print('VIRTUAL_ENV =', e.get('VIRTUAL_ENV'))
print('PYTHONPATH  =', e.get('PYTHONPATH'))
"
```

`VIRTUAL_ENV=...\hermes-agent\venv` and/or a legacy `venv\Lib\site-packages` in `PYTHONPATH` confirms it.

### Fix (non-destructive, survives updates)

Stop the gateway, then **quarantine** the retired in-tree venv (a `mv`, reversible), then restart:

```bash
BASE="~/AppData/Local/hermes"
HERMES="$BASE/bin/hermes.exe"

"$HERMES" gateway stop 2>&1 | tail -6
powershell.exe -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object {\$_.CommandLine -like '*hermes_cli.main*'} | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force -ErrorAction SilentlyContinue }"
sleep 3

DST="$BASE/backups/legacy-venv-cp311-quarantine-$(date +%Y%m%d)"
if [ -e "$DST" ]; then
  echo "quarantine already exists: $DST (nothing to move)"
elif [ -d "$BASE/hermes-agent/venv" ]; then
  mv "$BASE/hermes-agent/venv" "$DST" && echo "quarantined -> $DST"
else
  echo "no in-tree venv present (already clean)"
fi

"$HERMES" gateway start 2>&1 | tail -4
```

No code edits, this is filesystem state, so future updates won't churn. If `hermes-agent\venv` ever reappears after an update, just re-run the `mv`.

### Verify the fix

```bash
BASE="~/AppData/Local/hermes"
PID=$(grep -o '"pid": *[0-9]*' "$BASE/gateway.pid" | grep -o '[0-9]*')

# A) gateway env clean (VIRTUAL_ENV unset; PYTHONPATH = hermes-agent;<managed site-packages>)
#    (re-run the psutil diagnostic above)

# B) the loaded extension is the MANAGED cp314 one
powershell.exe -NoProfile -Command "Get-Process -Id $PID | Select-Object -ExpandProperty Modules | Where-Object { \$_.FileName -like '*pydantic*' } | Select-Object FileName | Format-Table -Auto -Wrap"

# C) no pydantic / hosted_room_worker errors after the restart timestamp
awk '/<restart-time>/{f=1} f' "$BASE/logs/gateway.log" | grep -iE "pydantic|hosted_room_worker died|Agent error" | head
```

Success = `_pydantic_core.cp314-win_amd64.pyd` under the managed `installs\...` path, `VIRTUAL_ENV` unset, and no errors after restart. Then ask the user to send a Telegram message to confirm end-to-end.

---

## Steps

### 1. Locate the install (expected)

```bash
HERMES="~/AppData/Local/hermes/bin/hermes.exe"
ls -la "$HERMES"
```

### 2. Check version + upstream status

```bash
"$HERMES" --version | head -7
cd ~/AppData/Local/hermes/hermes-agent && git rev-parse --short HEAD
```

Note: `hermes update --check` can hit transient network errors (`✗ Network error`). `hermes --version` already reports "Update available: N commits behind", trust that, and `git fetch` to confirm:

```bash
cd ~/AppData/Local/hermes/hermes-agent
git fetch origin 2>&1 | tail -3
echo "local: $(git rev-parse --short HEAD)  origin/main: $(git rev-parse --short origin/main)"
```

### 3. Snapshot uncommitted edits (do NOT rely on autostash)

```bash
cd ~/AppData/Local/hermes/hermes-agent
D=~/AppData/Local/hermes/updates-preupdate-snapshot-$(date +%Y%m%d-%H%M)
mkdir -p "$D"
git diff > "$D/local-changes.diff"
git status --short > "$D/status.txt"
echo "saved: $D/local-changes.diff ($(wc -l < "$D/local-changes.diff") lines)"
```

### 4. Stop the gateway to release files (IMPORTANT)

```bash
"$HERMES" gateway stop 2>&1 | tail -8
```

Then kill any leftover `hermes_cli.main` processes still holding files:

```bash
powershell.exe -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object {\$_.CommandLine -like '*hermes_cli.main*'} | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force -ErrorAction SilentlyContinue; 'killed ' + \$_.ProcessId }"
```

### 5. Run the update

```bash
cd ~/AppData/Local/hermes/hermes-agent
timeout 900 "$HERMES" update --yes --gateway
echo "EXIT: $?"
```

Expect: deps installed, web UI rebuilt, "✓ Already up to date! [main @ <hash>]", gateway cold-started.

### 6. Check for the stale in-tree venv (failure mode #2)

A Python upgrade leaves the retired in-tree venv behind. Confirm it is absent (or quarantine it per failure mode #2):

```bash
BASE="~/AppData/Local/hermes"
ls -d "$BASE/hermes-agent/venv" 2>/dev/null && echo "⚠ stale in-tree venv present, quarantine it (failure mode #2)"
```

### 7. Verify

```bash
"$HERMES" --version | head -7
"$HERMES" gateway status 2>&1 | head -8
cd ~/AppData/Local/hermes/hermes-agent && git status --short && echo "HEAD: $(git rev-parse --short HEAD)"
```

Success = version shows the right Python + "Up to date", gateway process running, **gateway log free of `pydantic_core` / `hosted_room_worker died` errors**, clean tree.

## Troubleshooting

- **Agent turns fail with `pydantic_core._pydantic_core` (Telegram gets no replies)** → failure mode #2: quarantine `hermes-agent\venv`, restart the gateway.
- **`os error 32` / "another process is holding it open"** → a gateway/desktop process still runs. Repeat step 4 and re-run step 5.
- **`HTTP 429 Too Many Requests` on ZIP fallback** → the updater hit the release-server rate limit. Wait ~1 min and re-run `hermes update --yes --force`.
- **Stash conflict on `contributors/emails/*`** → upstream deletes these tracking files; the updater leaves the codebase clean. `git stash list` preserves your changes, apply with `git stash apply <ref>` if needed.
- **Gateway not restarted after update** → `"$HERMES" gateway start` (or `gateway status`).
- **`✗ Gateway service is not installed` on start** → normal; this install runs the gateway manually via direct spawn. The message is informational.
