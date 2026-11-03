---
name: update-wsl-hermes
description: Update the Hermes agent that lives INSIDE WSL Ubuntu (user `<linux-user>`), NOT the Windows install. Use when the user says "update my WSL hermes agent", "update hermes", "update the WSL agent", or anything about updating the Hermes agent in WSL. Runs the full update to completion, snapshots local edits first, and truthfully reports whether upstream has new commits.
---

# Update WSL Hermes Agent

## ⚠️ CRITICAL: There are TWO Hermes installs. Use the WSL one.

| | WSL (THE ONE THIS SKILL UPDATES) | Windows (DO NOT touch for WSL task) |
|---|---|---|
| **Who runs it** | user `<linux-user>` inside WSL Ubuntu | user `<windows-user>` on Windows |
| **Agent home** | `~/.hermes` | `~\AppData\Local\hermes` |
| **Source repo** | `~/.hermes/hermes-agent` | `~\AppData\Local\hermes\hermes-agent` |
| **Exe / entry** | `~/.local/bin/hermes` (venv: `hermes-agent/venv/bin/python`) | `hermes-agent\venv\Scripts\hermes.exe` |
| **Services** | systemd user: `hermes-gateway`, `hermes-browser` | Scheduled Task `Hermes_Gateway` |
| **Config** | `~/.hermes/config.yaml` | `AppData\Local\hermes\config.yaml` |

**The pi shell runs in Msys/Windows by default.** A bare `hermes` command there hits the WINDOWS install. To reach the WSL agent you MUST route through WSL:

```bash
wsl.exe -d Ubuntu -- bash -lc '...'
```

**NEVER point a bare `hermes`/`git` command at `~` from the Windows side.**

---

## Overview

1. Confirm which install (must be WSL/Ubuntu/`<linux-user>`).
2. Check `hermes version` and whether upstream is actually ahead.
3. Snapshot uncommitted local edits before updating (safety).
4. Run `hermes update --yes --gateway` to completion (exit 0).
5. Verify version, git HEAD, and that gateway/browser services are `active`.
6. Report truthfully — if upstream has no new commits, say so plainly.

---

## 1. Locate / confirm the WSL install

```bash
wsl.exe -d Ubuntu -- bash -lc '
whoami
echo $HOME
ls -la ~ | grep -i herm
~/.local/bin/hermes version
'
```

Expected: user `<linux-user>`, home `~`, install `~/.hermes/hermes-agent`.

## 2. Check version + whether an update exists

```bash
wsl.exe -d Ubuntu -- bash -lc '
~/.local/bin/hermes version | head -6
cd ~/.hermes/hermes-agent && git rev-parse --short HEAD
'
```

Compare `upstream <short-hash>` in `hermes version` against `git rev-parse --short origin/main` after a fetch:

```bash
wsl.exe -d Ubuntu -- bash -lc '
cd ~/.hermes/hermes-agent && git fetch origin 2>&1 | tail -3
echo "local HEAD:  $(git rev-parse --short HEAD)"
echo "origin/main: $(git rev-parse --short origin/main)"
'
```

- If they match → the agent is at tip of `main`. Run the update anyway to sync deps/skills/web UI (see step 4) and report "no new upstream commits".
- If `origin/main` is ahead → a real upstream update is available.

## 3. Snapshot uncommitted local edits (ALWAYS)

Your repo often has uncommitted edits to files like `gateway/run.py`, `plugins/platforms/photon/sidecar/package.json`, `plugins/platforms/telegram/adapter.py`. The updater autostashes/restores them, but never rely on that alone.

```bash
wsl.exe -d Ubuntu -- bash -lc '
cd ~/.hermes/hermes-agent
D=~/.hermes/updates-preupdate-snapshot-$(date +%Y%m%d)
mkdir -p "$D"
git diff > "$D/local-changes.diff"
echo "saved: $D/local-changes.diff  ($(wc -l < "$D/local-changes.diff") lines)"
git status --short
'
```

## 4. Run the update

```bash
wsl.exe -d Ubuntu -- bash -lc '
cd ~/.hermes/hermes-agent
timeout 600 ~/.local/bin/hermes update --yes --gateway
echo "EXIT: $?"
'
```

Flags explained:
- `--yes` → auto-accept config migration / stash restore prompts.
- `--gateway` → use file-based IPC instead of stdin (internal, required by the updater).

This syncs Python deps, Node deps, rebuilds the web UI, syncs bundled skills, migrates config, and restarts the gateway.

## 5. Verify

```bash
wsl.exe -d Ubuntu -- bash -lc '
~/.local/bin/hermes version | head -6
systemctl --user is-active hermes-gateway
systemctl --user is-active hermes-browser
cd ~/.hermes/hermes-agent && git status --short && echo "HEAD: $(git rev-parse --short HEAD)"
'
```

Success = version updated/confirmed, both services `active`, local edits preserved (or stashed).

## 6. Report truthfully

- State the exact new version/hash.
- If no new upstream commits existed, say so explicitly rather than implying features arrived.
- If gateway/browser are NOT active, report it — do not claim success.

## Troubleshooting

- **"hermes: command not found"** → use full path `~/.local/bin/hermes`.
- **Update stalls / gateway held** → the WSL gateway runs under systemd user services. Do NOT `--force-venv` from Windows; instead restart via `systemctl --user restart hermes-gateway`.
- **Local edits lost after update** → restore from the snapshot in step 3, or `git stash apply <stash-ref>` (the updater prints the stash ref).
