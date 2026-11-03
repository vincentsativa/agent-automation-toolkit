---
name: hermes-backup-restore
title: Hermes Configuration Backup & Restore
description: Full backup and restore of Hermes Agent configuration — config, env, skills, cron, memories, and kanban. Covers Windows (native) and the staging-directory git pattern with weekly cron automation.
version: 1.0.0
created: 2026-06-11
---

# Hermes Configuration Backup & Restore

## What to Back Up

| Path | What | Required |
|------|------|----------|
| `config.yaml` | Main Hermes configuration | Yes |
| `.env` | API keys, secrets, credentials | Yes (if exists) |
| `skills/` | All installed skills with refs/templates/scripts | Yes |
| `cron/jobs.json` | Cron job definitions | If cron configured |
| `cron/output/` | Cron run history | Optional |
| `memories/MEMORY.md` | Persistent memory notes | Yes |
| `memories/USER.md` | User profile | Yes |
| `kanban/workspaces/` | Kanban board files | If kanban used |

### What to EXCLUDE

Do NOT include these — they're runtime artifacts:
- `logs/` — gateway and error logs
- `cache/` — model caches, bootstrap cache, context length cache
- `audio_cache/` — TTS/STT audio artifacts
- `media_cache/` — image/media artifacts
- `checkpoints/` — filesystem snapshots (in `state-snapshots/`)
- `sessions/` — session transcripts
- `state.db` / `state.db-shm` / `state.db-wal` — session database (too large, recreates)
- `kanban.db` / `kanban.db.init.lock` — kanban database (ask user first, can be large)
- `*.lock`, `*.pid` — runtime lock files
- `gateway.lock`, `gateway.pid`, `gateway_state.json` — gateway runtime state

## Backup Workflow

### 1. Create Staging Directory

Use a temp directory, never the source directory:

```bash
BACKUP_DIR="~/AppData/Local/Temp/hermes-backup"
HERMES_DIR="~/AppData/Local/hermes"

rm -rf "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/config"
mkdir -p "$BACKUP_DIR/skills"
mkdir -p "$BACKUP_DIR/cron/output"
mkdir -p "$BACKUP_DIR/memories"
mkdir -p "$BACKUP_DIR/kanban"
```

### 2. Copy Files

```bash
cp "$HERMES_DIR/config.yaml" "$BACKUP_DIR/config/"
[ -f "$HERMES_DIR/.env" ] && cp "$HERMES_DIR/.env" "$BACKUP_DIR/config/"

# Skills - skip .git tracking dirs
for d in "$HERMES_DIR/skills/"*/; do
  bn=$(basename "$d")
  [ "$bn" = ".git" ] && continue
  cp -r "$d" "$BACKUP_DIR/skills/"
done

[ -f "$HERMES_DIR/cron/jobs.json" ] && cp "$HERMES_DIR/cron/jobs.json" "$BACKUP_DIR/cron/"
[ -d "$HERMES_DIR/cron/output" ] && [ "$(ls -A "$HERMES_DIR/cron/output" 2>/dev/null)" ] && cp -r "$HERMES_DIR/cron/output/"* "$BACKUP_DIR/cron/output/"

[ -f "$HERMES_DIR/memories/MEMORY.md" ] && cp "$HERMES_DIR/memories/MEMORY.md" "$BACKUP_DIR/memories/"
[ -f "$HERMES_DIR/memories/USER.md" ] && cp "$HERMES_DIR/memories/USER.md" "$BACKUP_DIR/memories/"

[ -d "$HERMES_DIR/kanban/workspaces" ] && cp -r "$HERMES_DIR/kanban/workspaces" "$BACKUP_DIR/kanban/"
```

### 3. Git Init and Push

```bash
cd "$BACKUP_DIR"
git init -q
git checkout -b main -q
git add -A >/dev/null 2>&1
git commit -qm "Backup $(date '+%Y-%m-%d')"
git remote add origin https://github.com/<user>/<repo>.git
git pull --rebase origin main 2>/dev/null || true

# Resolve any merge conflicts from the fresh staging dir (add/add conflicts)
# Accept the live versions as they are the most up-to-date
if [ -d "$BACKUP_DIR/.git/rebase-merge" ] || git ls-files -u | grep -q .; then
  echo "Resolving merge conflicts with --theirs..."
  git checkout --theirs . 2>/dev/null || true
  git add -A
  git -c user.name="Hermes Backup" -c user.email="hermes@local" \
    commit -qm "Weekly backup $(date '+%Y-%m-%d') (conflict resolution)"
fi

git push -u origin main --force-with-lease -q
```

### 4. Create Private Repo

```bash
# Via gh CLI (if authenticated):
gh repo create <repo-name> --private --description "Hermes Agent backup"

# Via API:
curl -s -X POST https://api.github.com/user/repos \
  -H "Authorization: Bearer $(gh auth token)" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{"name":"<repo-name>","private":true,"description":"Hermes Agent backup"}'
```

## Weekly Auto-Backup (Cron)

### 1. Place Script in `~/.hermes/scripts/`

The cron system only accepts relative script names. Absolute paths are rejected with: "Script path must be relative to ~/.hermes/scripts/."

**IMPORTANT: Use Python, not bash, for cron scripts on Windows.** Bash scripts break because the cron runner resolves relative script paths to Windows absolute paths (e.g. `~\...\hermes-backup.sh`), then passes them to bash. Bash interprets `\U`, `\D`, `\A`, `\L`, `\h`, `\s` as escape sequences, mangling the path to `~AppDataLocalhermesscriptshermes-backup.sh` — exit code 127 every time.

Python scripts handle Windows paths natively. The cron runner detects `.py` extension and runs via Python.

Copy the canonical robust script from this skill's `scripts/hermes-backup.py` to `~/.hermes/scripts/hermes-backup.py`. Do **not** inline a hand-rolled version; the canonical script encodes five fixes (PAT-in-URL, no-prompt env, per-call git timeouts, unique timestamped staging dir, clone-based history) that a naive version will silently miss. See the "Robust Script Template" section below for what the script does and why each fix exists, and `references/2026-07-19-fine-grained-pat-credential-hang.md` for the incident that produced them.

If you must regenerate the script from scratch instead of copying, the full source is in `scripts/hermes-backup.py` in this skill directory. Read it with `skill_view(name='hermes-backup-restore', file_path='scripts/hermes-backup.py')` and copy it verbatim.

### 2. Schedule via Cron

```bash
# Create using the cronjob tool:
# Action: create
# Name: windows-weekly-backup
# Schedule: 0 3 * * 0   (Sundays at 3 AM)
# Script: hermes-backup.py  (relative name only — no path prefix)
# no_agent: true              (script-only, zero LLM tokens)
# deliver: local              (log to cron/output, no Telegram spam)
```

### Pitfall: Bash Scripts Break on Windows Cron (Backslash Mangling)

**Do not use `.sh` scripts for cron on Windows.** The cron runner resolves relative script paths to Windows absolute paths with backslashes (e.g. `~\AppData\Local\hermes\scripts\hermes-backup.sh`), then passes that string to bash. Bash interprets `\U`, `\D`, `\A`, `\L`, `\h`, `\s` as escape sequences, stripping them all. The result is a mangled path like `~AppDataLocalhermesscriptshermes-backup.sh` — exit code 127, "No such file or directory."

**Fix:** Write the backup script in Python (`.py` extension). The cron runner detects `.py` and runs via Python, which handles Windows paths natively. The script lives in `~/.hermes/scripts/` and is referenced by bare filename, same as a `.sh` script.

### Pitfall: Read-Only .git/objects on Windows

When `shutil.rmtree()` tries to delete the staging directory's `.git/objects/` tree, it hits `PermissionError: [WinError 5] Access is denied` on git object files. Git marks pack files and loose objects as read-only on Windows.

**Fix:** Pass an `onerror` handler to `shutil.rmtree()` that clears the read-only bit and retries:

```python
def _remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

shutil.rmtree(BACKUP_DIR, onerror=_remove_readonly)
```

### Pitfall: Relative Script Path Only

The `cronjob` tool **requires** a bare filename for the `script` parameter. Absolute paths like `~\\AppData\\Local\\hermes\\scripts\\hermes-backup.py` or home-prefixed paths like `~/hermes-backup.py` are rejected. Always place scripts in `~/.hermes/scripts/` and pass just the filename.

### Pitfall: Stale Git State

If `git pull --rebase` fails (e.g., force-push or divergent histories), the backup stops. The Python script's `subprocess.run` with `capture_output=True` does not raise on non-zero exit by default, but the pull failure means the push will also fail. For robustness, check the return code of the pull and handle it before the push.

### Pitfall: Merge Conflicts on Re-Push

When running a fresh backup from a staging directory (not a git clone), `git pull --rebase` can produce merge conflicts on files that changed on both sides (config.yaml, jobs.json, skill files). The fresh staging dir has no history — it's a new init. The remote has the previous backup's history. Git sees every file as an add/add conflict.

**Fix:** After the pull + rebase produces conflicts, resolve with `git checkout --theirs .` to accept the live versions (they are the most up-to-date), then `git add -A && git commit -m "..." && git push -u origin main --force-with-lease`. The `--force-with-lease` is safe here because the backup repo is private and single-user — it only overwrites if no one else has pushed.

**Better fix:** Prefer `git clone` of the existing backup repo over `git init` + `git pull --rebase`. Clone preserves history, sets up origin and remote-tracking refs, and removes the entire add/add conflict-resolution branch. Push becomes a clean fast-forward. The robust script template below uses this approach.

### Pitfall: Fine-Grained PAT Has No Write Access to the Backup Repo (CRITICAL — observed 2026-07-19)

`gh auth token` returns a **fine-grained PAT**, not a classic PAT. Fine-grained PATs are scoped per-repository. If the backup repo (`windows-hermes-backup`) is not in the token's allowed repository list, every `git push` returns `403: Write access to repository not granted`. This is invisible until you actually try to push — `gh auth status` reports "✓ Logged in" and reads work fine, but write access is denied.

**Symptom chain:** The weekly backup cron hung for the full 3600s timeout every run. Root cause: `git push` 403'd on the fine-grained PAT, fell back to `git-credential-manager get` for an interactive prompt, and the detached cron process has **no stdin**, so the prompt blocks forever. The cron runner eventually kills the python process, but the spawned `git.exe` / `git-remote-https.exe` / `git-credential-manager.exe` tree is **not reaped** and keeps running (see the orphan pitfall below).

**Verification command (run before trusting any backup cron):**
```bash
PAT=$(gh auth token)
git ls-remote "https://${PAT}@github.com/<user>/<repo>.git" HEAD
# 403 "Write access to repository not granted" = token cannot push to this repo
```
Also check the PAT's scopes header — fine-grained PATs return an empty `X-OAuth-Scopes:` value:
```bash
curl -sI -H "Authorization: token $(gh auth token)" https://api.github.com/user | grep -i "x-oauth-scopes"
```

**Fix (one of):**
1. In GitHub, edit the fine-grained PAT and add the backup repo to its repository access list (user does this in browser).
2. Create a classic PAT with `repo` scope and re-run `gh auth login` with it. Classic PATs work for all repos the account owns.
3. Switch `REPO_URL` to a repo the token already has write access to (verify with `GET /user/repos?per_page=100` filtered by name, check `permissions.push == true`).

**Do NOT assume `gh auth status` showing "✓ Logged in" means push works.** Always verify write access with `git ls-remote` using the PAT-embedded URL before scheduling the cron.

### Pitfall: Orphan Git Processes Poison the Next Run (WinError 32 — observed 2026-07-19)

When a prior backup run times out or is killed mid-push, the `git.exe` process tree (git, git-remote-https, git-credential-manager) is **not terminated** on Windows. Those processes hold an open handle on the staging directory (`%TEMP%\hermes-backup`). The next cron run calls `shutil.rmtree(BACKUP_DIR)` and crashes immediately:

```
PermissionError: [WinError 32] The process cannot access the file because it is being used by another process: '~\\AppData\\Local\\Temp\\hermes-backup'
```

This error is misleading — it looks like a permissions problem, but the real cause is a **zombie git from a prior failed run**. Every subsequent run fails the same way until you manually kill the orphans.

**Fix (in the script):**
1. Use a **unique timestamped staging dir** per run (`hermes-backup-YYYYMMDD-HHMMSS`) instead of a fixed `hermes-backup` path. A prior run's orphan cannot lock a directory that doesn't exist yet.
2. At the end of each run, clean up staging dirs older than 24h (best-effort, never abort the backup on cleanup failure).
3. Before debugging a `WinError 32`, check for orphan git: `tasklist | grep git` or PowerShell `Get-CimInstance Win32_Process -Filter "Name='git.exe'" | Select ProcessId, CommandLine`. The credential-manager process is the one actually holding the handle; kill the tree leaf-to-root.

### Pitfall: Detached Cron Has No stdin — Every Prompt Hangs Forever

Cron script-only jobs (`no_agent: true`) run as detached subprocesses with **no stdin**. Any tool that tries to read interactive input will block indefinitely until the cron 3600s timeout kills the python parent (but not its spawned children — see the orphan pitfall above).

This affects: `git` credential prompts, `gh auth login` (browser flow), `ssh` host-key prompts, any `read` in a shell script, `input()` in Python.

**Fix (in the backup script):**
1. Embed the PAT in the remote URL so git never prompts: `https://<pat>@github.com/<user>/<repo>.git` (fetch it at runtime via `gh auth token`).
2. Set `GIT_TERMINAL_PROMPT=0` and `GCM_INTERACTIVE=never` in the git subprocess environment so git **fails fast** instead of prompting.
3. Put a hard `timeout=` on every `subprocess.run` call (180s is plenty for clone/push). A hung git gets killed rather than blocking the whole run.

### Robust Script Template

The canonical robust backup script lives at `scripts/hermes-backup.py` in this skill directory. It implements all the fixes above: PAT-in-URL via `gh auth token`, `GIT_TERMINAL_PROMPT=0` + `GCM_INTERACTIVE=never`, per-call git timeouts, unique timestamped staging dir, clone-based history preservation (no init+pull+rebase), and stale-dir cleanup. Copy it to `~/AppData/Local/hermes/scripts/hermes-backup.py` and reference it from the cron job by bare filename. See `references/2026-07-19-fine-grained-pat-credential-hang.md` for the full debugging session and reproduction recipe.

## Restore from Backup

### Full Restore

```bash
REPO_URL="https://github.com/<user>/<repo>.git"
HERMES_DIR="~/AppData/Local/hermes"
BACKUP_DIR="~/AppData/Local/Temp/hermes-restore"

# Clone
git clone "$REPO_URL" "$BACKUP_DIR"

# Restore config files
cp "$BACKUP_DIR/config/config.yaml" "$HERMES_DIR/config.yaml"
[ -f "$BACKUP_DIR/config/.env" ] && cp "$BACKUP_DIR/config/.env" "$HERMES_DIR/.env"

# Restore skills (backup existing first)
cp -r "$BACKUP_DIR/skills/"* "$HERMES_DIR/skills/"

# Restore cron
[ -f "$BACKUP_DIR/cron/jobs.json" ] && cp "$BACKUP_DIR/cron/jobs.json" "$HERMES_DIR/cron/"

# Restore memories
[ -f "$BACKUP_DIR/memories/MEMORY.md" ] && cp "$BACKUP_DIR/memories/MEMORY.md" "$HERMES_DIR/memories/"
[ -f "$BACKUP_DIR/memories/USER.md" ] && cp "$BACKUP_DIR/memories/USER.md" "$HERMES_DIR/memories/"

# Restore kanban
cp -r "$BACKUP_DIR/kanban/workspaces" "$HERMES_DIR/kanban/"
```

### Selective Restore

Copy individual files from the cloned repo's `config/`, `skills/`, `cron/`, `memories/`, or `kanban/` directories. Always backup the destination first:

```bash
cp "$HERMES_DIR/config.yaml" "$HERMES_DIR/config.yaml.backup-$(date +%Y%m%d)"
```

## Windows-Specific Notes

### Hermes Home Path

On Windows, Hermes lives at:
```
%LOCALAPPDATA%\hermes\
# Which resolves to:
C:\Users\<username>\AppData\Local\hermes\
```

Not `%USERPROFILE%\.hermes\` (that's the Linux path). Always use `$APPDATA/../Local/hermes` or `/c/Users/<user>/AppData/Local/hermes` in bash/MSYS.

### Script Shell

The cron system runs `.sh` scripts via bash (git-bash/MSYS on Windows). Use POSIX shell syntax:
- `$(date ...)` not PowerShell `$(Get-Date)`
- Single-quoted strings
- MSYS-style paths (`/c/Users/...`)
- No PowerShell cmdlets

If you need PowerShell, write a `.ps1` — but `.ps1` scripts from cron run through Python, not PowerShell directly, so `.sh` is simpler for script-only cron jobs on Windows.

### gh CLI Path

On Windows, `gh` installs to `C:\Program Files\GitHub CLI\gh.exe`. The git-bash PATH usually includes it. If missing:
```bash
winget install GitHub.cli
# OR download MSI from: https://github.com/cli/cli/releases/latest
```

## Verification Checklist

- [ ] Repo is private on GitHub
- [ ] All file categories accounted for (config/skills/cron/memories)
- [ ] `.env` excluded from git history (contains secrets) — confirm in `.gitignore`
- [ ] No lock files, logs, cache in the backup
- [ ] Cron job registered and enabled (`cronjob action=list`)
- [ ] Orphan file handling: skills without SKILL.md (like `apple/DESCRIPTION.md`) are backed up as-is
- [ ] Empty directories (kanban with no boards) are captured or noted as empty

## Pitfalls

- **Path confusion on Windows**: Hermes data lives at `%LOCALAPPDATA%\hermes\`, not `%USERPROFILE%\.hermes\`. The Linux convention `~/.hermes/` does NOT map to the right place on native Windows.
- **`.env` is sensitive**: The `.env` file contains API keys and tokens. Ensure the backup repo is PRIVATE. Consider adding a `.gitignore` in the staging dir before `git add`.
- **Kanban DB not directories**: The kanban board data lives in `kanban.db` (SQLite), not `kanban/workspaces/`. The workspaces directory may be empty. If the user wants kanban backed up, add `kanban.db` to the file list.
- **Staging in temp**: The staging dir in `%TEMP%` is ephemeral — the backup lives in git, not on disk. Don't rely on `hermes-backup/` persisting across reboots.
- **Large repos**: Skills with many references/scripts (PowerPoint XSD schemas, research LaTeX templates, etc.) can produce 700+ files. Initial push is slow; subsequent incremental pushes are fast.
- **Point-in-time snapshot, not continuous history**: The backup captures whatever is on disk at the moment it runs. Skills created and deleted between backup runs are lost forever from git. If a skill was deleted before the backup ran, it was never captured. The backup repo's git history will show no trace of it. Do not assume `git log --diff-filter=D` will reveal deletions — it only shows deletions that happened to files that were previously committed, which a skill deleted before the first backup never was.
- **`.archive/` vs true deletion**: Skills moved to `.archive/` are preserved and recoverable. Skills that were `rm -rf`'d (no `.archive` entry) are gone from the Windows side. Check `.archive/` first before assuming a skill is lost.

## WSL Secondary Recovery

When a skill is missing from both the live Windows Hermes and the GitHub backup, check the WSL Hermes as a secondary source. This user runs Hermes on both Windows and WSL (Ubuntu), and skills are often created on WSL first then copied to Windows.

### WSL Hermes Path

```
~/.hermes/skills/
```

### Recovery Pattern

```bash
# 1. Check if the skill exists on WSL
wsl bash -c "ls ~/.hermes/skills/<skill-name>/"

# 2. Read the SKILL.md from WSL
wsl bash -c "cat ~/.hermes/skills/<skill-name>/SKILL.md"

# 3. Check for reference files
wsl bash -c "ls -la ~/.hermes/skills/<skill-name>/references/"

# 4. Restore to Windows
mkdir -p "~/AppData/Local/hermes/skills/<skill-name>/references"
wsl bash -c "cp ~/.hermes/skills/<skill-name>/SKILL.md /mnt~/AppData/Local/hermes/skills/<skill-name>/SKILL.md"
wsl bash -c "cp ~/.hermes/skills/<skill-name>/references/*.md /mnt~/AppData/Local/hermes/skills/<skill-name>/references/"
```

### Proven recovery (June 13, 2026)

`ghostwriter-terminal` was copied from WSL to Windows on June 9, deleted before the June 11 backup ran, and was never in the backup repo. WSL still had the full skill with 4 reference files. Restored successfully via the pattern above. See `references/wsl-recovery-ghostwriter-terminal.md` for the full reproduction recipe.

## GitHub Backup Recovery

When you need to recover a cron job prompt or config from the GitHub backup:

- **Repo:** https://github.com/vincentsativa/windows-hermes-backup.git
- **Branch:** main
- **Schedule:** Weekly (Sunday 3 AM)
- **Script:** `~/AppData/Local/hermes/scripts/hermes-backup.py`

### Recover a Cron Job Prompt

```bash
git clone https://github.com/vincentsativa/windows-hermes-backup.git /tmp/hermes-backup
cd /tmp/hermes-backup
python3 -c "
import json
with open('cron/jobs.json') as f:
    d = json.load(f)
for j in d['jobs']:
    if j['id'] == '<JOB_ID>':
        print(j['prompt'])
"
```

### Critical Rules When Restoring

1. **Do NOT paraphrase or truncate.** Read the exact prompt text from the backup file. Every word, every line break, every instruction is there for a reason.
2. **Verify the full prompt** before writing it back. The backup is the source of truth, not your memory of what the prompt said.
3. **Do NOT "improve" the prompt** during restoration. The user wrote it. Restore it verbatim.
4. **Session proof (July 7, 2026):** A truncated/paraphrased restoration was rejected with "that is NOT the prompt i wrote." The full original was only found by cloning the backup repo and reading `cron/jobs.json` directly.

### Limitations

- Only one commit per week (the latest backup). No granular history between backups.
- If a cron was created and modified between two backup runs, only the latest state is preserved.
- The backup script uses `--force-with-lease` on push, so concurrent pushes from multiple machines may conflict.