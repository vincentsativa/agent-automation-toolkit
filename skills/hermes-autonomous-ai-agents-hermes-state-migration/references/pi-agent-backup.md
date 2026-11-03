# Pi agent backup repo, restoring Pi on a new machine

Pi is an external autonomous coding agent (separate from Hermes, Codex, Claude Code, OpenCode). Its config backup lives in a private repo and restoring it is a **sync, not a git clone-over**.

## Backup repo layout

`vincentsativa/pi-agent-backup` (private) mirrors Pi's config from a **Windows** machine (see `config/trust.json` → `C:\Users\<user>`). Hierarchical:
- `config/` → `models.json`, `settings.json`, `trust.json`
- `extensions/` → `browser-tool/` (package.json, package-lock.json, test-contact-form.js), `context-manager.ts`
- `npm/` → package.json, package-lock.json, `pi-web-search/` (index.ts, README, LICENSE)
- `skills/` → `backup-websites`, `blogwatcher`, `clone-website`, `process-article`, `publish-article`, `reorder-articles`, `swap-ads` (each SKILL.md + scripts/references)

## Pi's home layout on Linux, flat, DIFFERENT from the repo

`~/.pi/agent/`:
- `auth.json`, `models.json`, `models-store.json`, `settings.json`, directly in the folder (flat)
- `bin/fd`, `npm/`, `sessions/` (per-project jsonl transcripts under `sessions/<cwd-slug>/`)
- `~/.pi/agent` is **not** a git repo

## Key insight: sync missing pieces, don't clone over

Because the backup came from a different machine layout, "make Pi a clone of the backup" means **copying the missing items into `~/.pi/agent/`**, not `git clone` over the folder. On this box the missing items were: `trust.json`, all `skills/`, all `extensions/`, `pi-web-search`. The existing `models.json` and `settings.json` already matched the backup's model list and default model.

## Pitfalls

- **`~/.pi/agent/settings.json` is LIVE**, the running Pi session (and the Hermes session whose model config it references) depends on it. Do NOT overwrite a working settings file blindly. Ask: copy-in-only-missing vs full-replace.
- **Auth is in `~/.git-credentials`** (plaintext, user `vincentsativa`; git uses `credential.helper=store`). Extract the token with sed, never print it:
  ```bash
  TOKEN=$(sed 's#https://[^:]*:\(.*\)@github.com#\1#' ~/.git-credentials)
  curl -s -H "Authorization: token $TOKEN" https://api.github.com/user  # 200 = auth OK
  curl -s -H "Authorization: token $TOKEN" "https://api.github.com/user/repos?per_page=100&type=all"  # list repos
  ```
- **API base64 file reads mangle on newlines**, for reading repo files, `git clone --depth 1` the repo and `cat` locally instead of decoding the contents API `content` field:
  ```bash
  git clone --depth 1 https://vincentsativa:$TOKEN@github.com/vincentsativa/pi-agent-backup.git
  ```
