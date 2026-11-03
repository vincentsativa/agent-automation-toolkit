# Hermes Environment Corruption Repair (Windows)

## Root Cause

The built-in `hermes update` command on Windows uses `uv` to reinstall dependencies. When it stashes/pulls/restores local changes during the update, `uv` sometimes resolves a minimal set that **drops 15+ essential packages** (`python-dotenv`, `pydantic`, `rich`, `click`, `pyyaml`, `requests`, `urllib3`, etc.). The editable `.pth` files survive but the actual packages don't, the CLI launcher exists but crashes on any import.

## The Environment Path Is Not Fixed

Hermes now runs from a **PM-managed environment**: `%LOCALAPPDATA%\hermes\installs\<install-key>\environments\<env-hash>\venv\`. The `<env-hash>` changes every time the environment is rebuilt, so any hardcoded path in a script or note goes stale silently.

**Resolve the live interpreter before repairing anything:**

```cmd
powershell -NoProfile -Command "(Get-ChildItem $env:LOCALAPPDATA\hermes\installs\*\facts.json | Sort-Object LastWriteTime | Select-Object -Last 1 | ForEach-Object { (Get-Content $_ -Raw | ConvertFrom-Json).packages.venv.environment })"
```

Append `\Scripts\python.exe` to the printed path. `hermes doctor` prints the same thing in its Python Environment section: `Runtime venv staged (...) (active in this process)`.

**The old paths are dead.** `%LOCALAPPDATA%\hermes\hermes-agent\venv\` does not exist, it was quarantined to `%LOCALAPPDATA%\hermes\backups\legacy-venv-cp311-quarantine-20260924\` on 2026-09-24. Do not reinstall into it and do not add it to PATH.

## Symptoms

- `hermes --version` crashes with `ImportError: cannot import name 'load_dotenv' from 'dotenv'`
- Desktop app (Hermes.exe) still works fine, only the CLI environment breaks
- `where hermes` finds the launcher, but running it immediately errors
- Files in `%LOCALAPPDATA%\hermes\` are intact

## Repair Command

Run this from **Command Prompt** (not WSL), with `<resolved env>` replaced by the path from the command above:

```batch
%LOCALAPPDATA%\hermes\bin\uv.exe pip install -e "%LOCALAPPDATA%\hermes\hermes-agent" --python "<resolved env>\Scripts\python.exe"
```

Or from PowerShell:

```powershell
$env_path = (Get-ChildItem "$env:LOCALAPPDATA\hermes\installs\*\facts.json" | Sort-Object LastWriteTime | Select-Object -Last 1 | ForEach-Object { (Get-Content $_ -Raw | ConvertFrom-Json).packages.venv.environment })
& "$env:LOCALAPPDATA\hermes\bin\uv.exe" pip install -e "$env:LOCALAPPDATA\hermes\hermes-agent" --python "$env_path\Scripts\python.exe"
```

This reinstalls ALL missing dependencies from the editable source install in about 60 seconds.

## One-Click Repair Script

`%LOCALAPPDATA%\hermes\fix-after-update.cmd` resolves the environment itself and checks the venv, the desktop build, and the CLI. Run it instead of hand-typing the repair command. The skill's own copy is `scripts/fix-after-update.cmd`; deploy it to `%LOCALAPPDATA%\hermes\fix-after-update.cmd` after editing.

Note `%LOCALAPPDATA%\hermes\scripts\repair-venv.cmd` is the OLD one-click script and carries the dead `hermes-agent\venv` path. It has been rewritten to resolve the environment dynamically; if you find a copy still pointing at `hermes-agent\venv\Scripts\python.exe`, it is stale and should be replaced from `scripts/repair-venv.cmd`.

## Prevention: Disable Auto-Update

The update command triggers this corruption every time. Disable it in config.yaml:

```yaml
updates:
  enabled: false
  check_on_start: false
  backup_keep: 0
  non_interactive_local_changes: abort
  pre_update_backup: false
```

After disabling, Hermes only updates when the user explicitly runs `hermes update`.

## Verify Repair

```cmd
hermes --version
```

Expected: the version line prints without an ImportError. If you want to prove the environment itself rather than the launcher, run the resolved interpreter directly with `-c "import dotenv, fastapi, pydantic, yaml, rich"` and expect a clean exit.
