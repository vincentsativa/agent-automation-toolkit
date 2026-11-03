---
name: windows-hermes-troubleshooting
description: Diagnostic and repair patterns for Hermes installations on Windows, locating the installation when it seems "gone," verifying shortcuts, CLI PATH, desktop app, and data integrity
trigger: "user says Windows Hermes is broken, missing, gone, won't start, or can't find it"
---

# Windows Hermes Troubleshooting

## Architecture

A Windows Hermes installation has three independent components:

| Component | Default Location | What It Is |
|-----------|-----------------|------------|
| **Desktop app** | `%LOCALAPPDATA%\hermes\hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe` | Electron-based GUI | 
| **CLI** | `%LOCALAPPDATA%\hermes\bin\hermes.exe` (launcher; it dispatches into the live PM-managed environment) | CLI entry point, added to PATH by installer. **The old `%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts\hermes.exe` path no longer exists**; that venv was quarantined to `backups\legacy-venv-cp311-quarantine-20260924\` on 2026-09-24. |
| **Data / Config** | `%LOCALAPPDATA%\hermes\` | config.yaml, skills/, sessions/, memories/, state.db, etc. |

Shortcuts:
- Start Menu: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Hermes.lnk`
- Desktop: `%USERPROFILE%\Desktop\Hermes.lnk` and/or `%USERPROFILE%\OneDrive\Desktop\Hermes.lnk`

## Key Insight: "It's gone" Usually Means Shortcut or PATH

Most "my Hermes is gone" reports from Windows resolve to one of these, NOT actual data loss:

1. **Desktop shortcut deleted**, the .lnk file in Desktop or OneDrive/Desktop got removed. The actual Hermes.exe is still there.
2. **PATH entry broken**, System/User PATH was reset by a Windows update, Python update, or user action. The CLI binary exists but `hermes` isn't on PATH.
3. **Start menu unpinned**, Unpinned from Start. The shortcut in Start Menu\\Programs still exists.
4. **Taskbar un pinned**, App was running fine, user just can't find the launcher.
5. **Startup behavior changed**, Gateway or background service stopped auto-starting after reboot.
6. **Venv corruption from `hermes update`**, The built-in update (`hermes update`) uses `uv` to reinstall deps, but on Windows it sometimes resolves a minimal set that drops essential packages (`python-dotenv`, `pydantic`, `rich`, and 15+ others). The editable `.pth` files survive but the dependencies don't. The CLI binary still exists at `%LOCALAPPDATA%\hermes\bin\hermes.exe` but crashes on import. **This is the most common cause of "my Hermes broke after an update."**

## Verification Checklist (run from WSL)

From WSL, all Windows paths are under `/mnt/c/`. Map `%LOCALAPPDATA%` to `/mnt/c/Users/<username>/AppData/Local/hermes/` and `%APPDATA%` to `/mnt/c/Users/<username>/AppData/Roaming/`.

```
# 1. Check data directory (this is what matters, everything else is replaceable)
ls /mnt/c/Users/<username>/AppData/Local/hermes/config.yaml
ls /mnt/c/Users/<username>/AppData/Local/hermes/state.db
ls /mnt/c/Users/<username>/AppData/Local/hermes/sessions/

# 2. Check desktop app binary
ls -la /mnt/c/Users/<username>/AppData/Local/hermes/hermes-agent/apps/desktop/release/win-unpacked/Hermes.exe

# 3. Check CLI launcher and resolve the LIVE python environment
ls /mnt/c/Users/<username>/AppData/Local/hermes/bin/hermes.exe
cmd.exe /c "where hermes 2>&1"   # Check CLI is on PATH

# Resolve the live interpreter (PM-managed; the hash changes on rebuild)
python3 -c "import json,glob;print(json.load(open(sorted(glob.glob('/mnt/c/Users/<username>/AppData/Local/hermes/installs/*/facts.json'))[-1]))['packages']['venv']['environment'])"
# append \Scripts\python.exe to that path
# `hermes doctor` also prints it: "Runtime venv staged (...) (active in this process)"

# 4. Check shortcuts
ls /mnt/c/Users/<username>/AppData/Roaming/Microsoft/Windows/Start\ Menu/Programs/Hermes.lnk
ls /mnt/c/Users/<username>/Desktop/Hermes.lnk
ls "/mnt/c/Users/<username>/OneDrive/Desktop/Hermes.lnk"
```

## What "Gone" Usually Means (Diagnostic)

| Symptom | Likely Root Cause | Fix |
|---------|------------------|-----|
| CLI crashes with `ImportError` or `No module named`, or `hermes.exe` exists but does nothing | Venv corruption from update, `uv` resolved minimal dep set, dropped essential packages (`python-dotenv`, `pydantic`, `rich`, 15+ others) | Reinstall deps against the RESOLVED live interpreter: run `scripts\fix-after-update.cmd`, or `uv pip install -e "%LOCALAPPDATA%\hermes\hermes-agent" --python "<resolved env>\Scripts\python.exe"` (see `references/venv-corruption-repair.md`) |
| Desktop app icon missing from desktop and start menu | Shortcuts deleted or OneDrive Desktop sync issue | Recreate shortcuts: run `%LOCALAPPDATA%\\hermes\\make-shortcut.ps1` and `%LOCALAPPDATA%\\hermes\\make-desktop-shortcut.ps1` from PowerShell |
| `hermes` not found in CMD/PowerShell | PATH broken or launcher directory missing from PATH | Add `%LOCALAPPDATA%\\hermes\\bin` to User PATH, or run from full path. (`%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts` no longer exists and must NOT be added.) |
| Desktop app crashes on launch | Corrupted Electron cache or old profile | Delete `%LOCALAPPDATA%\hermes\hermes-agent\apps\desktop\release\win-unpacked\` and re-run `%LOCALAPPDATA%\hermes\hermes-setup.exe` |
| Gateway won't start / cron not running | Windows service not installed or stopped | Re-run gateway install: `hermes gateway install` from an admin PowerShell |
| Everything gone, empty `AppData\Local\hermes\` | Actual data loss (rare) | Check Windows Backup / File History. Check if a Windows update reset AppData permissions. |
| Config is there but old, skills/sessions are there but no new data | User is looking at a stale backup or secondary profile | Check `hermes profile list` for active profile. Check `config.yaml` for `profile:` setting. |

## Recreating Shortcuts

If shortcuts are missing but the app binary exists, the installer ships PowerShell scripts:

```powershell
# Start Menu shortcut
powershell -File "%LOCALAPPDATA%\hermes\make-shortcut.ps1"

# Desktop shortcut
powershell -File "%LOCALAPPDATA%\hermes\make-desktop-shortcut.ps1"
```

These scripts create .lnk files pointing to the packaged Hermes.exe with working directory `%LOCALAPPDATA%\hermes`.

### Blank Icon After Update

After an update wipes and rebuilds the desktop app, the shortcut icon goes blank because Windows caches the icon from the old deleted binary. The shortcut target is still correct, the icon is just stale. Recreate the shortcuts (above) to point at the fresh exe. If still blank, clear the icon cache with `ie4uinit.exe -show` or reboot. Verify the shortcut target with a `.ps1` file (see PowerShell-from-WSL below).

## Running PowerShell from WSL: Use a .ps1 File

`cmd.exe /c "powershell -Command \"...\""` mangles `$` variables and quotes (they get eaten by cmd.exe, observed: `$s` becomes empty, `$s.TargetPath` becomes `.TargetPath`). The reliable pattern is to write a `.ps1` script file to the Windows filesystem and run it with:

```
cmd.exe /c "powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\<user>\AppData\Local\hermes\script.ps1"
```

This is the only reliable way to run PowerShell with variables from WSL. Clean up the temp `.ps1` after.

The script has to sit somewhere Windows can see, so copy it onto the Windows mount before invoking it (`cp "$SCRATCH/probe.ps1" /mnt/c/Users/<user>/AppData/Local/Temp/probe.ps1` and pass that path to `-File`); a `/home/...` path is invisible to `powershell.exe`. Piping a bash heredoc into `-Command` fails the same way from the other side, because bash expands `$env:TEMP`, `$d`, and `$null` before PowerShell ever parses them. Also note `wmic` and `tasklist /FI "IMAGENAME eq X"` fail through cmd.exe from WSL, use `tasklist` piped to `grep` instead.

## Data Integrity Check

Core files that matter (irreplaceable):
- `%LOCALAPPDATA%\\hermes\\config.yaml`, all settings
- `%LOCALAPPDATA%\\hermes\\.env`, API keys and secrets
- `%LOCALAPPDATA%\\hermes\\state.db`, session and memory database
- `%LOCALAPPDATA%\\hermes\\sessions\\`, conversation transcripts
- `%LOCALAPPDATA%\\hermes\\skills\\`, installed skills
- `%LOCALAPPDATA%\\hermes\\memories\\`, persistent memory
- `%LOCALAPPDATA%\\hermes\\auth.json`, OAuth tokens
- `%LOCALAPPDATA%\\hermes\\channel_directory.json`, gateway channel config
- `%LOCALAPPDATA%\\hermes\\scripts\\repair-venv.cmd`, one-click venv repair script

Replaceable files (will be regenerated):
- `hermes-agent\\` source directory, `hermes update` or reinstall
- `hermes-setup.exe`, re-download
- `bin\\uv.exe`, auto-downloaded by installer
- `logs\\`, diagnostic only
- `cache\\`, temporary

## Repair Procedure: Venv Corruption

When `hermes --version` crashes with `ImportError: cannot import name 'load_dotenv' from 'dotenv'` (or any missing package), the update corrupted the environment. Resolve the live interpreter first (see Verification Checklist step 3), then repair with:

```cmd
%LOCALAPPDATA%\hermes\bin\uv.exe pip install -e "%LOCALAPPDATA%\hermes\hermes-agent" --python "<resolved env>\Scripts\python.exe"
```

Or run `scripts\fix-after-update.cmd`, which resolves the interpreter itself. See `references/venv-corruption-repair.md` for full details and prevention.

## Update-Lock → ZIP-Fallback: Update Wipes the Packaged Desktop App

A distinct failure from plain venv corruption. When `hermes update` runs, the updater process holds its OWN `hermes.exe` binary open and cannot quarantine/replace it. The "another process is holding it open" is the updater itself, NOT the desktop app, REPL, or gateway. Verify before blaming those: check `tasklist` for `hermes.exe`, and check the `Hermes_Gateway` / `Hermes_Browser` scheduled tasks' Last Run Time against the update timestamp. Do not assume the desktop app was open, the user will call you on it. The update log shows:

```
⚠ Could not quarantine hermes.exe (PermissionError: another process is holding it open).
  Close Hermes Desktop, exit other `hermes` REPLs, stop the gateway...
⚠ Git update failed: ... returned non-zero exit status 2.
→ Falling back to ZIP download...
→ Extracting... ✓ Updated 90 items from ZIP
```

The ZIP fallback replaces the desktop **source tree** but does NOT rebuild the packaged app. Result: `apps/desktop/release/win-unpacked/Hermes.exe` and `apps/desktop/node_modules/` are gone, and `desktop-build-stamp.json` is stale (old `contentHash`, old `builtAt`). The desktop backend still boots fine (`HERMES_BACKEND_READY port=N`) but there is no packaged app to display, the window never appears.

**Diagnostic signature (from WSL):**
```bash
HERMES_WIN="/mnt/c/Users/<user>/AppData/Local/hermes"
ls "$HERMES_WIN/hermes-agent/apps/desktop/release/win-unpacked/Hermes.exe"   # missing
ls -d "$HERMES_WIN/hermes-agent/apps/desktop/node_modules"                  # missing
cat "$HERMES_WIN/desktop-build-stamp.json"                                  # stale hash/builtAt
tail -n 40 "$HERMES_WIN/logs/update.log"                                    # the PermissionError + ZIP fallback
grep -n "Traceback" "$HERMES_WIN/logs/desktop.log" | head -1                 # ImportError load_dotenv
```
The `ImportError: cannot import name 'load_dotenv' from 'dotenv'` traceback in desktop.log is the venv corruption symptom riding on top of the same botched update, the desktop backend crashes on boot (hundreds of `HERMES_BACKEND_READY` + `could not read served dashboard token` 404 lines = repeated failed boot attempts).

**Fix, rebuild the packaged app:**
```cmd
cd /d C:\Users\<user>\AppData\Local\hermes && hermes desktop --build-only
```
This runs npm install + electron-builder and regenerates `release/win-unpacked/Hermes.exe`. Verify: `ls` the exe (≈200 MB) and confirm `desktop-build-stamp.json` has a fresh `builtAt` and new `contentHash`. The venv is usually fine after the rebuild (the `load_dotenv` import resolves once deps are reinstalled); confirm with a one-liner if unsure.

**Prevention, the REAL fix (verified 2026-08-16):** the `hermes.exe` shim self-locks. When you run `hermes.exe update`, the shim launcher stays resident as the update's parent process and holds its own `hermes.exe` image open without `FILE_SHARE_DELETE`, so the update's quarantine step cannot rename it and the dependency sync dies with `os error 32` / `PermissionError`. Closing the desktop app, REPLs, and gateway does NOT fix this, the lock is the updater's own parent shim. The fix is to run the update via the module invocation, which leaves no `hermes.exe` process to hold the file:

```cmd
cd /d C:\Users\<user>\AppData\Local\hermes
"%LOCALAPPDATA%\hermes\bin\hermes.exe" --print-runtime-command
```

That prints the exact interpreter + `-c` payload the launcher uses; run the update through it. The equivalent for the CLI itself, without depending on the launcher:

```cmd
cd /d C:\Users\<user>\AppData\Local\hermes
for /f "delims=" %P in ('python -c "import json,glob;print(json.load(open(sorted(glob.glob(r'%LOCALAPPDATA%\hermes\installs\*\facts.json'))[-1]))['packages']['venv']['environment'])") do set VENV=%P
"%VENV%\Scripts\python.exe" -m hermes_cli.main update
```

Resolve that interpreter path once and reuse it; hardcoding a `installs\...\environments\<hash>\venv` path breaks the next time the environment is rebuilt.

This is the ONLY reliable way to update on Windows. `hermes.exe update` will keep failing with the quarantine PermissionError no matter what you close. (POSIX/WSL is unaffected, the `hermes` shim there is a shell script, and POSIX allows renaming a running script.)

**Permanent code fix (applied 2026-08-16):** `gateway/run.py` → `_resolve_hermes_bin()` now prefers `[sys.executable, "-m", "hermes_cli.main"]` over the `hermes.exe` shim on Windows, so the `/update` slash command from Telegram also bypasses the self-lock. This is a local patch to the Windows checkout, it will be overwritten by the next `git pull`/ZIP update, so re-apply it after any update that touches `gateway/run.py` (or upstream it).

**Re-apply script:** `scripts/reapply-update-fix.py` (in this skill, also deployed to `%LOCALAPPDATA%\hermes\scripts\reapply-update-fix.py`). Idempotent, run it after any update to restore the patch:

```bash
# From WSL (targets the Windows checkout):
python3 ~/.hermes/skills/devops/windows-hermes-troubleshooting/scripts/reapply-update-fix.py /mnt/c/Users/<user>/AppData/Local/hermes/hermes-agent/gateway/run.py

# Or on Windows directly (auto-locates the checkout):
python "%LOCALAPPDATA%\hermes\scripts\reapply-update-fix.py"
```

It prints `patched` / `already patched` and runs a `py_compile` check; exits non-zero on failure. After re-applying, restart the gateway (`hermes gateway restart`) to load the change.

**Vinny's update policy (decided 2026-08-14):** He updates ONLY on version releases, NOT daily. The bleeding edge was worth it early when Hermes was still filling gaps, but now they've built everything he needs, new features mostly don't apply or duplicate what he already built, so daily updates are a liability (risk of breaking the foundation for features he won't use). Consequences for how you handle update tasks:
- Do NOT recommend or push daily updates. Version-gated updates are the standing policy.
- The WSL side is too important to update casually, it holds memory, skills, sessions, the whole history. Never update it on a whim.
- Test repair scripts on the disposable Windows side FIRST (it does one task; losing it costs nothing). Only after it works on Windows is it safe for WSL.
- When a version does drop, update deliberately: close desktop + gateway, run the update, then run the repair script.

**Post-update repair scripts (run after ANY `hermes update`):** the ZIP fallback breaks the venv and wipes the packaged desktop app, and the update reports success (exit 0) so nothing flags it. Run the matching repair script after every update, it checks venv deps, the desktop build, and the CLI, and auto-repairs:
- **Windows:** `scripts/fix-after-update.cmd` (deploy to `C:\Users\<user>\AppData\Local\hermes\fix-after-update.cmd`)
- **WSL:** `scripts/fix-after-update.sh` (deploy to `~/.hermes/fix-after-update.sh`)

Both verify `fastapi,uvicorn,pydantic,openai,yaml,dotenv,rich` import cleanly, rebuild the desktop app if `Hermes.exe`/`Hermes` is missing, and confirm the CLI. This turns an hour of log-digging into a 2-minute fix. Note: `python_dotenv` is NOT a real package, the real one is `dotenv`; don't flag a venv as broken for a missing `python_dotenv` import.

**Hardened behavior (2026-08-15):** both scripts now (a) exit non-zero on any failure instead of silently passing, and (b) retry the desktop rebuild up to 3 times, re-verifying/reinstalling the venv before each retry. Rationale: the update log often shows "Optional extras failed" during the same update that wipes the desktop app, so the venv can still be broken when the script runs, and a single `hermes desktop --build-only` attempt with a broken CLI fails silently. The retry loop closes that gap. On failure the script prints "re-run after closing all Hermes windows/gateways" and exits 1.

**PITFALL, `.cmd` `for`-loop parsing.** Inside a `for /L` block in a `.cmd` file, `echo (attempt %%A)` breaks parsing, the `)` closes the block early and cmd errors with `venv was unexpected at this time`. Never put a literal `)` inside an `echo` line within a parenthesized `for`/`if` block. Use parens-free text (`echo   attempt %%A - build failed, retrying...`). Always test the `.cmd` by piping a newline to dismiss the trailing `pause`: `printf '\n' | cmd.exe /c "C:\...\fix-after-update.cmd"`.

**PITFALL, the venv and the desktop wipe are independent.** This session hit a case where the venv was healthy (DEPS OK) but the ZIP fallback had still wiped the packaged app, [1/3] passes, [2/3] is the one that matters. Always confirm the exe exists and the build stamp is fresh after running the script, not just that the script printed "Done."

**WSL has no desktop app to close.** The "close the desktop app before update" step is Windows-only. On WSL the pre-update checklist is just: stop the gateway, then update. The WSL repair script's desktop-build step is a no-op if the Linux desktop build is never used, it sees the exe absent and skips, which is correct.

**PITFALL, Telegram `/update` on Windows: the gateway can't stop itself.** A distinct trigger from the "updater holds its own exe" case above. When the update is fired from Telegram (`/update`), `hermes update` runs as a CHILD of the gateway process. The update's own "pause gateway" step only stops agent processing, the gateway process stays alive to stream output back to the user, so its venv launcher (`venv\Scripts\python.exe -m hermes_cli.main gateway run`) keeps `hermes.exe` and the `.pyd` files mapped. The quarantine rename and the dependency sync both fail with `PermissionError: another process is holding it open`, the update falls to the ZIP path, and the packaged desktop app gets wiped. So the "another process holding it open" is NOT always the updater itself, when the update came from Telegram, it is the gateway (specifically its venv launcher). Diagnostic signature: `gateway.log` shows `Update finished (exit=1)` while the gateway stays alive; `gateway-stdio.log` shows the early-pass dependency recovery followed by `✗ Another gateway instance is already running (PID ...)`. Fix: fully stop the gateway (kill the process tree, not pause), run `hermes update` from a detached shell (NOT from Telegram), then run `fix-after-update.cmd`, then restart the gateway. The `/update` slash command is fundamentally broken on Windows for this reason, updates must run from a detached shell after the gateway is down.

## WSL Hermes + Windows Desktop App: Two Connection Patterns

There are **two distinct ways** to use the Hermes Desktop app with a WSL backend. Do not conflate them.

### Pattern A: Run the Electron GUI Inside WSL (WSLg)

The Hermes Desktop app is an Electron GUI that can run from inside WSL, pointed at your WSL Hermes config. This is a Linux build of the same app, displayed on your Windows desktop via WSLg.

#### Distinction: `hermes dashboard` vs `hermes desktop`

| Command | What it is | How to access |
|---------|-----------|---------------|
| `hermes dashboard` | Web UI on port 9119 | Open `http://localhost:9119` in browser |
| `hermes desktop` | Native Electron desktop app | Launches a GUI window (requires WSLg or X server) |

They are completely different things. The user will correct you if you conflate them.

#### First-Time Build

The desktop app source lives at `~/.hermes/hermes-agent/apps/desktop/`. First run of `hermes desktop` builds it automatically (npm install + electron-builder). The packaged output goes to `release/linux-unpacked/`.

Prerequisites: Node.js (check with `node --version`).

#### WSL Sandbox Workaround

On WSL, the Electron sandbox helper needs `sudo` to set permissions, which isn't available in non-interactive contexts. The build succeeds but the sandbox setup fails with:

```
sudo: a terminal is required to read the password
✗ Failed to configure Electron's Linux sandbox helper
```

**Two options to fix:**

1. **One-time sudo setup** (from an interactive WSL terminal):
   ```bash
   sudo chown root ~/.hermes/hermes-agent/apps/desktop/release/linux-unpacked/chrome-sandbox
   sudo chmod 4755 ~/.hermes/hermes-agent/apps/desktop/release/linux-unpacked/chrome-sandbox
   ```

2. **Launch with `--no-sandbox`** (works fine on WSL, no security concern in WSL context):
   ```bash
   ~/.hermes/hermes-agent/apps/desktop/release/linux-unpacked/Hermes --no-sandbox
   ```

#### WSLg Requirement

The desktop app needs either:
- **WSLg** (built into modern WSL2), window appears on Windows desktop automatically
- **Third-party X server** (VcXsrv, X410, etc.), requires `export DISPLAY=:0` before launching

If the app starts but no window appears, WSLg may not be running. Check with `wsl.exe --version` and ensure `WSLg` is listed.

#### No Conflict with Windows Desktop

The WSL Desktop app and the Windows Desktop app are completely independent:
- Different processes, different configs, different filesystems
- The WSL app uses `~/.hermes/` (Linux paths)
- The Windows app uses `%LOCALAPPDATA%\\hermes\\` (Windows paths)
- Both can run simultaneously without interference

### Pattern B: Connect Native Windows Desktop App to WSL Backend (Remote Gateway)

The **native Windows Hermes Desktop app** can connect to a Hermes backend running in WSL via `hermes serve`. This is a **documented, supported feature**, the Desktop App is a front-end that drives the same agent runtime whether that runtime is local, in WSL, or on a remote VPS.

**Setup steps:**

1. On the WSL side, set auth credentials in `~/.hermes/.env`:
   ```
   HERMES_DASHBOARD_BASIC_AUTH_USERNAME=<your-username>
   HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=<your-password>
   HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)
   ```

2. Start the backend bound to all interfaces:
   ```bash
   hermes serve --host 0.0.0.0 --port 9119
   ```

3. Find your WSL IP: `hostname -I`

4. In the Windows Desktop App: Settings → Gateway → Remote Gateway, enter `http://<WSL-IP>:9119` plus credentials.

**Full details:** See `references/wsl-desktop-access.md` for the complete setup including auth options, mirrored networking mode (localhost instead of IP), and keeping the backend alive.

**PITFALL, Do not claim impossibility.** The Hermes Desktop app is explicitly designed to be decoupled from where the agent runs. The GUI is a front-end, not a separate agent, it drives the exact same runtime, sessions, memory, skills, and config whether that runtime lives on the local machine, in WSL, or on a remote VPS over Tailscale. Connecting a native Windows desktop app to a WSL-hosted backend is a documented, supported use case. If a user asks "can I point my WSL Hermes to my Windows desktop app," the answer is YES, via `hermes serve` as the backend and the Desktop App's Remote Gateway settings. Always check the docs before answering capability questions about Hermes features.

## Diagnostic: "It Works But Acts Retarded / Dumb"

When the user says Windows Hermes functions but behaves stupidly, ignoring instructions, making obvious mistakes, failing at simple tasks, and the model/config are identical to a working WSL agent:

### Root Cause: Terminal Backend

The most common cause is **cmd.exe as the terminal backend**. Every tool call that runs a shell command (terminal, execute_code, file operations via shell) goes through cmd.exe on Windows, which:

- Doesn't understand forward slashes in paths (`/c/Users/...` fails)
- Has no `ls`, `grep`, `find`, `sed`, `awk`, `cat`, `head`, `tail`, `diff`, `ps`, `kill`, `chmod`, `chown`, `rsync`, `scp`, `curl` (unless Git Bash is on PATH)
- Uses different quoting rules (`"` vs `\"`)
- Has no pipe/redirect semantics that match Linux
- Throws UNC path errors when started from WSL context
- Has no `&&` chaining that works the same way
- LSP (pyright) fails to initialize, `%1 is not a valid Win32 application`

The agent spends significant cognitive budget translating between Linux-idiomatic commands and Windows-compatible ones, and often gets it wrong. This manifests as "acting retarded", the model is fine, the execution environment is hostile.

### Diagnostic Checklist

| Symptom | Likely Cause |
|---------|-------------|
| Same model, same config, same reasoning_effort, but Windows agent is noticeably dumber | **Lack of accumulated work history**, memory, skills, and session history are per-installation, not shared. WSL Hermes has months of context; Windows native starts from zero. This is the most common cause when the model and config are identical. |
| Same model, same config, same reasoning_effort, but Windows agent is noticeably dumber | cmd.exe terminal backend vs WSL bash, every shell command goes through cmd.exe which lacks Linux tools and path semantics |
| Terminal commands fail with path errors (`UNC paths not supported`, `cannot access '/c/...'`) | cmd.exe doesn't understand Linux paths |
| LSP errors in logs (`%1 is not a valid Win32 application`) | pyright binary is Linux-only, can't run on Windows |
| Web search / browser tools unavailable | `check_web_api_key` / `_browser_cdp_check` returning False, missing API keys or CDP setup |
| Agent keeps trying Linux commands that fail | No pitfall guidance in the skill about cmd.exe limitations |

### Fix

1. **Keep terminal backend as `local`**, this is the correct setting for the Windows Hermes agent. Setting it to `wsl` causes the agent to try routing commands through WSL while still using Windows terminal semantics, which breaks most tool operations.

   ```powershell
   hermes config set terminal.backend local
   ```

2. **Or accept the limitation**, the agent will be slower and dumber on Windows native. Use the TUI/desktop app for chat and let the heavy lifting happen on WSL.

3. **Verify the fix**, after confirming the backend, run a simple command:
   ```powershell
   hermes -c "echo hello"
   ```

### Additional Diagnostic: Provider Name Mismatch

When the Windows agent behaves poorly despite identical model/config to a working WSL agent, check whether the **provider name** in the Windows config actually has a corresponding `providers.<name>:` block defined.

**The pattern:**
- WSL config has `provider: ollama-com` AND `providers.ollama-com: base_url: ... api_key: ...`
- Windows config has `provider: ollama-cloud` but **no** `providers.ollama-cloud:` block

This is a **silent failure**, the agent doesn't crash, it just uses defaults or falls back to an unconfigured provider, producing degraded behavior. The model name is the same, the config looks similar, but the provider plumbing is missing.

**How to check (from WSL):**
```bash
# Read Windows config
cat /mnt/c/Users/<username>/AppData/Local/hermes/config.yaml

# Check if the provider name in `model.provider:` has a matching `providers.<name>:` block
# e.g. if model.provider is "ollama-cloud", there must be a "providers.ollama-cloud:" section
grep -A2 "^providers:" /mnt/c/Users/<username>/AppData/Local/hermes/config.yaml
```

**Fix:** Either add the missing `providers.<name>:` block with the correct `base_url` and `api_key`, or change `model.provider` to match an existing provider block. Compare against the WSL config as the reference.

**PITFALL, Don't assume the provider name is correct just because the model works.** The provider name is a config key, not a URL. If the key doesn't match a defined provider block, the agent silently degrades. Always verify the provider block exists.

## Agent Topology (corrected by Vinny 2026-08-13)

The **windows hermes agent is NOT Pi.** Pi is a *separate* Windows coding agent. Do NOT conflate them:

- The Windows Hermes install (browser on port 9223) belongs to the **windows hermes agent**, not Pi. Vinny will authorize fixing it on request.
- Only touch Pi's machine if Vinny explicitly names Pi.
- When Vinny gives a fix task, just execute. Do not re-litigate boundaries, apologize repeatedly, or over-explain. That drew "you need to stop doing that."

**Pi is Vinny's go-to coding harness** (made by Mario, whom Vinny likes and respects). It's the lightest, most minimal, fully-customizable harness he uses, and it's part of his production pipeline, he uses it to upload his articles. He also has Claude Code but prefers Pi. Do not suggest replacing Pi with a newer harness (e.g. DeepSeek Harness) as a default; Pi is the proven workhorse. Vinny is curious about how new harnesses compare but waits for them to mature before considering a switch.

## Real-Profile Browsing (`browser.use_real_profile`)

Hermes' "browse as you" feature, agent drives a snapshot of the user's real
default-Chromium profile (their logins) instead of a clean browser. Consent flag
`browser.use_real_profile` (OFF by default), set via `hermes config set`. It
snapshots ONLY auth-bearing files into `~/.hermes/browser-profile/`, re-syncs on
each launch, and fails CLOSED for non-Chromium defaults. **WSL gotcha:** the WSL
Hermes has no installed default Chromium, and the bundled Playwright Chromium
doesn't count (clean, no logins), so the flag is on but unusable until a Linux
Chromium is installed and logged into. Full mechanics, consent state, and Vinny's
usage boundaries: `references/real-profile-browsing.md`.

## Making the Hermes Browser Survive Updates (root-cause fix)

**Why it breaks after every update:** The dedicated CDP browser (WSL port 9222, Windows port 9223) is launched as a plain background process that lives inside the gateway's process tree. `hermes update` restarts the gateway, and the browser dies with it. Nothing auto-relaunches it. This is the recurring "browser down after update" root cause.

**Permanent fix, make the browser its own managed service, detached from the gateway:**

### WSL side (Linux/systemd)
`~/.config/systemd/user/hermes-browser.service`, chromium under `xvfb-run` (WSL has no real display and its GPU env crashes Chromium), `Restart=always`, `WantedBy=default.target`, `ExecStartPre` clears a stale `SingletonLock`. Enable + start, verify CDP with `curl http://127.0.0.1:9222/json/version`. Full working unit in `references/browser-service-persistence.md`.

### Windows side (scheduled task)
Mirror the existing `Hermes_Gateway` scheduled task pattern, create a `Hermes_Browser` task that runs the idempotent launcher `.bat` at logon, with `RestartCount 999` + `RestartInterval 5min` + `StartWhenAvailable`. Verify the browser's own loopback responds (WSL cannot reach Windows `127.0.0.1`, check from the Windows side).

## Prerequisite: Windows Debloat for Agent Hosting

Before running Hermes or any agent software on Windows, the machine must be debloated. Windows Defender, OneDrive, Copilot, telemetry services, and Windows Update all actively interfere with agent operations, quarantining binaries, slowing file I/O, and rebooting mid-cron-run.

The user maintains a debloat script (stored on a Raspberry Pi) that strips all of this. See `references/windows-debloat-for-agents.md` for the full breakdown of what gets disabled and why.

**Key rule:** If a Windows machine is running agents and the user hasn't mentioned debloating, ask whether the debloat script has been applied. If not, recommend it before any deeper troubleshooting.

## Pitfalls

- **Don't cherry-pick log evidence.** The user will call you on it. If you find one session using a different model, that doesn't prove the model is the problem, check whether it's the norm or the exception.

## NameError: `_history_media_paths` Not Defined

This is a code bug in `gateway/run.py` that affects both WSL and Windows installs. See `references/nameerror-history-media-paths.md` for the full fix and restart procedure.

## Syncing Skills Between WSL and Windows

When the user has both a WSL Hermes installation (`~/.hermes/`) and a Windows installation (`/mnt/c/Users/<username>/AppData/Local/hermes/`), and one side has a newer or corrected version of a skill, sync from WSL to Windows.

### Path Mapping

| WSL Path | Windows Path (from WSL) |
|----------|------------------------|
| `~/.hermes/skills/` | `/mnt/c/Users/<username>/AppData/Local/hermes/skills/` |
| `~/.hermes/skills/<category>/<skill>/` | `/mnt/c/Users/<username>/AppData/Local/hermes/skills/<category>/<skill>/` |

Discover the Windows username with `ls /mnt/c/Users/` if unknown.

### Procedure

1. **Locate the Windows skill directory**:
   ```bash
   find /mnt/c/Users/<username>/AppData/Local/hermes/skills -maxdepth 5 -type d -name "<skill-name>"
   ```

2. **Compare the two versions**:
   ```bash
   diff -rq ~/.hermes/skills/<category>/<skill>/ /mnt/c/Users/<username>/AppData/Local/hermes/skills/<category>/<skill>/
   ```

3. **Replace the Windows version with the WSL version** (WSL is authoritative):
   ```bash
   WIN_DIR="/mnt/c/Users/<username>/AppData/Local/hermes/skills/<category>/<skill>"
   WSL_DIR="~/.hermes/skills/<category>/<skill>"
   rm -rf "$WIN_DIR"
   cp -r "$WSL_DIR" "$WIN_DIR"
   ```

4. **Verify byte-for-byte match**:
   ```bash
   diff -rq "$WSL_DIR" "$WIN_DIR"
   ```

### Rules

- **WSL is authoritative.** When the two versions differ, the WSL version is the correct one. Replace the Windows version entirely.
- **Do NOT create backups of the old Windows version.** The user considers the replaced version wrong and does not want clutter. Overwrite directly.
- **Copy the entire skill directory** (SKILL.md, scripts/, references/, templates/) as a unit. Partial copies leave stale support files behind.
- **Remove stale files.** The Windows version may have scripts or references that no longer exist in the WSL version. `rm -rf` then `cp -r` ensures a clean replacement.

### Creating a NEW skill on both trees (change-brief / multi-agent sync)

The `rm -rf` + `cp` flow above is for syncing an EXISTING skill. When replicating a brand-new skill to both trees:

1. **Create it on WSL with `skill_manage`**, this is the authoritative create path and enforces the description budget.
2. **Replicate to Windows with `write_file`**, not `skill_manage` (which only writes to `~/.hermes/skills/`). Write the identical SKILL.md directly to `/mnt/c/Users/<username>/AppData/Local/hermes/skills/<category>/<name>/SKILL.md`.

### Making a skill mandatory on BOTH agents (`skills.auto_load`)

A standing ruleset (the constitution) must be injected every session, not left to the model to remember. The supported mechanism is `skills.auto_load` in config.yaml, which renders named skills fully loaded into the system prompt at session start on every surface:

```yaml
skills:
  auto_load:
    - vinny-constitution
```

Set it with the JSON array form so it lands as a real list:

```bash
cd ~ && hermes config set skills.auto_load '["vinny-constitution"]'
```

**`hermes config set` with a bare value writes a STRING and the loader silently ignores it.** The resolver checks `isinstance(auto_load, list)`, so a string yields `[]` and the skill never loads, with no error anywhere. Always assert the type after setting:

```bash
python3 -c "import yaml; v=yaml.safe_load(open('$HOME/.hermes/config.yaml'))['skills'].get('auto_load'); print(repr(v), type(v).__name__)"
```

Expect a `list`, never a `str`.

**Prove the injection resolves on each home, do not assume it.** Point `HERMES_HOME` at the home you are checking:

```bash
cd ~ && python3 - <<'EOF'
import sys, os
sys.path.insert(0, '~/hermes-agent')
os.environ['HERMES_HOME'] = '/mnt/c/Users/<user>/AppData/Local/hermes'  # or the WSL home
from agent.skill_commands import resolve_auto_load_skills, build_auto_load_prompt
print("resolved:", resolve_auto_load_skills())
text, loaded, missing = build_auto_load_prompt()
print("loaded:", loaded, "| missing:", missing, "| chars:", len(text))
EOF
```

Success is the skill name in `loaded` with `missing: []`. A name in `missing` means a typo or an entry in that home's `disabled` list. Resolution happens once per session when the system prompt is first built, so the change applies to the NEXT new session, and a running gateway needs a restart.

**Check the Windows RULES FILES are not STALE, not just present.** A skill file existing in the Windows tree does not mean it carries the current rules. Diff it against the WSL copy with line endings normalized before every sync of a rules-bearing skill; a months-old copy quietly runs an outdated rulebook.

### Editing the Windows config.yaml

The Windows home is `/mnt/c/Users/<user>/AppData/Local/hermes/` (config.yaml at the root). The security guard that blocks `patch`/`write_file` on the WSL config does NOT apply here, so writes go through directly, and that makes the following mandatory:

1. **Back up first, then RE-LIST the backup in a separate step to prove it persists.** A backup that is never re-listed may not be on disk, and a vanished backup turns a recoverable edit into a loss.
2. **Anchor the insert on a unique block and assert the match count** before replacing (e.g. `skills:\r\n  external_dirs: []\r\n`), so exactly one key is inserted and the `disabled` list and every other section survive.
3. **`diff` against the backup afterward** and confirm the only changed lines are the ones you intended.

### Pitfalls (multi-tree sync)

- **The two trees are NOT identical.** WSL and Windows files can differ (e.g. a Windows constitution ending at Article 5 with no Enforcement section while WSL had one). Always read the target file on EACH tree before patching, the same `old_string` may match on one and not the other. Patch per-tree.
- **Windows files use CRLF line endings.** A plain Python `open(p,'w')` on a Windows config or skill file silently converts the whole file to LF, so read and write with `newline=""` and reuse the file's own line endings when you script the change. Verify with `file <path>` (expect "with CRLF line terminators"). The `patch` tool preserves line endings on its own; hand-written Python does not.
- **Verify subagent self-reports when you delegate per-tree.** Subagents can silently skip an item (observed: a Windows subagent omitted one brief section). After a delegated bulk sync, re-read or `grep` the target files to confirm each item landed, and patch gaps yourself.

## Diagnosing a Failing Windows-Agent Cron From WSL

The Windows agent's cron store is NOT under `~/.hermes` or `%USERPROFILE%\\.hermes`; it lives in the Windows data home: `/mnt/c/Users/<user>/AppData/Local/hermes/cron/jobs.json`. The same script is often duplicated under `.clawdbot/cron/jobs.json` and `OpenclawBackup/cron/jobs.json` from older agents, those are stale, do not edit them.

```bash
# 1. Find the real job and read its last_error (the whole diagnosis lives here)
python3 -c "import json;d=json.load(open('/mnt/c/Users/<user>/AppData/Local/hermes/cron/jobs.json'));print([j for j in d['jobs'] if 'NAME' in j['name']])"

# 2. Read the script the job invokes
read_file /mnt/c/Users/<user>/AppData/Local/hermes/scripts/<script>

# 3. Read the per-run output files for the failure streak
ls /mnt/c/Users/<user>/AppData/Local/hermes/cron/output/<job_id>/
```

`last_error` plus `failure_streak` tell you whether you are looking at a new fault or one bug that has been failing repeatedly. A high streak with an identical message every run means ONE root cause, not many, read the message literally, because the exact string is usually the whole bug.

**PITFALL, a global `core.hooksPath` guard can block pushes that look fine.** `git config --global core.hooksPath` on the Windows box may point at a `~/.githooks` directory (e.g. a pre-push guard that refuses public repos). A backup job can then fail for many consecutive runs with a `PUSH BLOCKED` / `could not verify visibility` message that has nothing to do with the backup script. Check `core.hooksPath` in `/mnt/c/Users/<user>/.gitconfig` before blaming the script. See `references/git-push-guard-hooks.md`.

**PITFALL, verify the fix with the WINDOWS git and python, not the WSL ones.** WSL has its own `git` and its own global config, so a WSL-side test does not exercise the Windows hook path or the Windows credential helper. Run the real script the way cron runs it:

```bash
GIT="/mnt/c/Program Files/Git/bin/git.exe"
PY="/mnt/c/Users/<user>/AppData/Local/Programs/Python/Python312/python.exe"
PATH="/mnt/c/Program Files/Git/bin:$PATH" "$PY" "C:/Users/<user>/AppData/Local/hermes/scripts/<script>.py"; echo "EXIT=$?"
```

Prefer the WSL paths of Windows executables (`/mnt/c/...`) over `cmd.exe /c`, the UNC-path errors that come with launching from `\\wsl.localhost` break git's "dubious ownership" check. Then confirm the effect server-side (`gh api repos/<owner>/<repo>/commits --jq '.[0].sha'`), because a script printing "complete" is not proof the push landed.

**PITFALL, a 403 from GitHub happens before pre-push runs.** Testing the guard by pushing to a repo you lack write access to proves nothing: the remote rejects the push during connection, so the hook never executes and prints nothing. Test the hook directly instead:

```bash
bash /mnt/c/Users/<user>/.githooks/pre-push origin https://github.com/<known-public-owner>/<repo>; echo "EXIT=$?"
```

Always confirm the guard still blocks what it is supposed to block after changing it, so a fix does not quietly disable the protection.

## WSL as Desktop Agent

See `references/wsl-desktop-access.md` for the full pattern of running Hermes in WSL and accessing the Windows desktop filesystem directly. This covers both:

- **File access** via `/mnt/c/`, one agent, one memory bank, one set of skills, with the Windows desktop as just another directory
- **Remote backend** via `hermes serve`, connect the native Windows Desktop App to your WSL Hermes backend

## Pitfalls

- **`C:\Users\<user>\.hermes` is NOT the Hermes home.** That directory exists on these machines but holds only `workspace/`, `creds/`, `chrome-debug*/`, and a browser launcher `.bat`; it has no `skills/`, no `config.yaml`, and no `cron/jobs.json`. The home is `%LOCALAPPDATA%\hermes`. A recursive grep or an `ls` against `.hermes` returns empty and reads as a clean result, so prove the target before making any claim about it: `find <home>/skills -name SKILL.md | wc -l` must be non-zero, and `ls <home>/cron/jobs.json` must hit. Claiming 'checked the Windows agent' off a `.hermes` sweep is a false statement the user will catch on the next question.
- **OneDrive Desktop vs Local Desktop**: Windows sync can mean shortcuts exist in ONE but not the OTHER. Check both `%USERPROFILE%\\Desktop\\` and `%USERPROFILE%\\OneDrive\\Desktop\\`.
- **WSL vs Windows paths**: From WSL, `cmd.exe /c "where hermes"` is the only reliable way to check Windows PATH. WSL doesn't inherit Windows PATH by default.
- **Windows PATH reset**: Recent Windows updates have been known to reset User PATH environment variables. The CLI is still installed, the path just needs to be re-added.
- **Don't conflate "no icon" with "no data"**: The most common case is shortcut loss, not data loss. Check the data directory first.
- **Dual installation risk**: If Hermes was installed via both the PowerShell installer AND pip (within WSL), there may be two separate installations with different configs. Verify which one the user actually uses.
- **OpenClaw rollback from WSL**: When OpenClaw on Windows breaks after an npm update, you can roll it back from WSL using `powershell.exe -Command "npm install -g openclaw@<version>"`. See `references/openclaw-rollback-from-wsl.md` for the full procedure including config restore and gateway reinstall.
