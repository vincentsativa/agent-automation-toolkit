---
name: backup-websites
description: Complete backup of all websites under phantom-byte.com, articles.phantom-byte.com, and vincent-sativa.com to GitHub. Use when the user says "backup my sites", "backup everything", "push to github", "send to github", "back it all up", or similar phrasing.
---

# Backup Websites to GitHub

## ⚠️ THE PI BACKUP REPO (MY OWN CONFIG — DO NOT FORGET THIS)

**There IS a dedicated GitHub backup for MY OWN pi agent config/skills/extensions. It is literally named "PI BACKUP". Use it FIRST whenever the user says "back up", "push to github", or any change is made to skills/settings.**

| What | Value |
|---|---|
| **Repo (GitHub)** | `vincentsativa/pi-agent-backup` — description: "Backup of pi coding agent configs, skills, extensions, and custom packages" |
| **Local clone** | `~/workspace/pi-agent-backup/` |
| **Visibility** | PUBLIC |
| **Structure** | `config/` (models.json, settings.json, trust.json), `extensions/` (browser-tool, context-manager.ts), `npm/`, `skills/` (all skills) |

**When to push to this repo:**
- After ANY edit to a skill (e.g. `process-article`, `publish-article`, this file)
- After adding/removing skills
- After changing `settings.json`, `models.json`, extensions, or npm packages
- Basically any time the `.pi/agent/` config changes and the user wants a backup

**Source vs repo layout:**
- Live config lives in `~/.pi/agent/` (has `auth.json`, `github-token.txt`, `models-store.json`, `sessions/` at the root — **NEVER copy these**).
- The repo splits the safe files into `config/`, `extensions/`, `npm/`, `skills/` subfolders.
- Sync safe files only: skills → `skills/`, extensions source (NO node_modules) → `extensions/`, `models.json`/`settings.json`/`trust.json` → `config/`, `package*.json` → `npm/`.

**Files that must NEVER be pushed (they contain real credentials):**
- `auth.json`, `github-token.txt`, `test-token.ps1`, `token-*.png`, `models-store.json`, `sessions/`, and `skills/blogwatcher/config/n8n.env` (real `N8N_API_KEY`). The repo `.gitignore` already excludes these — do not `git add -f` them.

**Push workflow (from the local clone `~/workspace/pi-agent-backup/`):**
```bash
cd ~/workspace/pi-agent-backup
# 1. Sync the safe files from .pi/agent (cp/rscp skills, extensions minus node_modules, config, npm)
# 2. Run a real-secret scan first (actual token formats, NOT just documented prefixes):
grep -rnE 'ghp_[a-zA-Z0-9]{20,}|gho_[a-zA-Z0-9]{20,}|github_pat_[a-zA-Z0-9_]{20,}|sk_live_[a-zA-Z0-9]{16,}|AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY' --include='*' . --exclude-dir=.git
# 3. Commit + push:
git add -A
git commit -m "Sync pi agent config - YYYY-MM-DD"
git push origin main
```

> ⚠️ **KNOWN FALSE POSITIVE:** `skills/backup-websites/SKILL.md` legitimately *documents* the secret-detection patterns (`ghp_`, `sk_live_`, etc.) as grep examples. The pre-commit hook will flag it. Verify it's just the documented prefixes (no real 20+ char tokens) — if so, commit with `git commit --no-verify`. Do NOT weaken the hook for this.

> ⚠️ The pre-commit secret-scan hook (from `prevent-secret-leak` skill) must be installed in this repo. If it's missing, copy it:
> `cp ~/.pi/agent/scripts/prevent-secret-leak.sh .git/hooks/pre-commit`

---

## Site Inventory

### Domain: `phantom-byte.com`

| Site / App | Local Path | GitHub Repo | Visibility |
|---|---|---|---|
| Main website | `~/workspace/phantom-byte-website/` | `vincentsativa/phantom-byte-website` | PUBLIC (hosts live site) |
| Landing page (Cloud Run) | `~/workspace/landing-page/` | `vincentsativa/phantom-byte-landing-page` | PUBLIC (hosts live site) |
| Contact form API | `~/phantom-byte-contact-api/` | `vincentsativa/phantom-byte-contact-api` | **PRIVATE** (contains SMTP credentials) |
| Funnel pages (primary) | `~/workspace/funnel-pages/` | `vincentsativa/phantom-byte-funnels` | **PRIVATE** (internal) |
| Funnel pages (ready) | `~/workspace/funnels-ready/` | `vincentsativa/phantom-byte-funnels-ready` | **PRIVATE** (internal) |
| AI app | `~/phantom-ai/` | `vincentsativa/phantom-ai` | **PRIVATE** (internal) |

### Domain: `articles.phantom-byte.com`

| Site / App | Local Path | GitHub Repo | Visibility |
|---|---|---|---|
| Deployed HTML site | `~/workspace/articles/` | `vincentsativa/articles-phantom-byte` | PUBLIC (hosts live site) |
| Astro source code | `~/workspace/articles-site/` | `vincentsativa/articles-site-source` | **PRIVATE** (source code) |

### Domain: `vincent-sativa.com`

| Site / App | Local Path | GitHub Repo |
|---|---|---|
| Personal website | `~/workspace/vincent-sativa-website/` | `vincentsativa/vincent-sativa-website` | PUBLIC (hosts live site) |

### Backup Archives (not pushed to GitHub)

| Archive | Path | Contents |
|---|---|---|
| Old ZIP backups | `~/workspace/website-backups/` | Full site ZIPs from Mar 2026 |
| Old articles backup | `~/phantom-byte-backup/` | Old backup ZIP + extracted `websites/` dir (from Apr 2026) |

---

## Prerequisites

- GitHub credentials are stored in `~/.git-credentials`
- Git is configured with user: `vincentsativa`, email: `user@example.com`
- GitHub API token works for `vincentsativa` account

## Repo Existence Check

Before pushing, check if each repo exists on GitHub:

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/vincentsativa/<repo-name>/contents/"
```

- **HTTP 200** = repo has content (already backed up)
- **HTTP 404 on contents** = repo exists but empty OR doesn't exist
- Use the full repo GET to distinguish: `curl -s "https://api.github.com/repos/vincentsativa/<repo-name>"`

If a repo doesn't exist, create it:

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"<repo-name>\",\"private\":true,\"description\":\"Backup of <description>\",\"auto_init\":false}" \
  "https://api.github.com/user/repos"
```

## Standard Backup Workflow

For each site that needs backing up:

### 1. Initialize Git (if no .git)

```bash
cd <site-path>
git init
git checkout -b main
```

### 2. Create .gitignore (with secret patterns)

```bash
cat > .gitignore << 'GITIGNORE'
# Dependencies
node_modules/

# Environment & secrets
.env
.env.*
*.key
*.pem
*.p12
*.pfx
*-credentials.json
*secret*
*credential*
*service-account*
firebase-service-account.json
google-indexing-credentials.json
frank-hermes-key.json

# Logs & temp
*.log
.DS_Store
Thumbs.db
desktop.ini
.cache/
backups/
temp*

# Build outputs
dist/
build/
.next/
GITIGNORE
```

> ⚠️ **CRITICAL: Pre-commit secret scan** — Before adding/committing, scan all staged files for leaked credentials:
>
> ```bash
> # Scan for Google/Firebase API keys, tokens, etc.
> echo "--- Scanning for secrets in staged files... ---"
> git add -A
> 
> # Check for API key patterns that should NOT be in a public repo
> SECRET_FOUND=false
> git diff --cached --name-only | while read file; do
>   if [ -f "$file" ]; then
>     # Scan for AIzaSy pattern (Google API keys - only flag if NOT a Firebase config context)
>     if grep -q 'AIzaSy' "$file" 2>/dev/null; then
>       echo "🔴 WARNING: $file contains 'AIzaSy...' pattern (Google API key)"
>       echo "   This is likely a Firebase Web SDK key, which is intended to be public."
>       echo "   VERIFY it's safe before proceeding."
>     fi
>     # Scan for known secret patterns
>     for pat in 'ghp_' 'gho_' 'ghu_' 'ghs_' 'ghr_' 'sk-' 'sk_live_' 'pk_live_' 'AKIA' '-----BEGIN.*PRIVATE KEY-----'; do
>       if grep -q "$pat" "$file" 2>/dev/null; then
>         echo "🔴 SECRET FOUND in $file: pattern '$pat' detected"
>         SECRET_FOUND=true
>       fi
>     done
>   fi
> done
> 
> if [ "$SECRET_FOUND" = true ]; then
>   echo "❌ Aborting: secrets detected in staged files. Remove them first."
>   git reset
>   exit 1
> fi
> ```
>
> If a secret was already committed in a previous backup, remove it from history:
> ```bash
> git rm --cached <secret-file>
> echo "<secret-file>" >> .gitignore
> git add .gitignore
> git commit -m "Remove committed secret file from tracking"
> ```

### 3. Add, Commit, Push (with verification)

```bash
git add -A
git commit -m "Full backup of <site-name> - YYYY-MM-DD"
git remote add origin https://github.com/vincentsativa/<repo-name>.git
git push -u origin main
```

### 4. Post-Push Verification

```bash
# Check the repo has content
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/vincentsativa/<repo-name>/contents/" | \
  node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>console.log(JSON.parse(d).length+' items'))"

# Final check: pull back fresh and scan for secrets
cd /tmp
rm -rf verify-<repo-name>
git clone "https://github.com/vincentsativa/<repo-name>.git" verify-<repo-name>
echo "--- Verifying pushed content has no secrets ---"
grep -rn 'AIzaSy\|ghp_\|sk_live_\|-----BEGIN.*PRIVATE KEY' verify-<repo-name>/ --include='*.js' --include='*.py' --include='*.json' --include='*.html' --include='*.sh' --include='*.yml' --include='*.yaml' --include='*.env' --include='*.txt' --include='*.md' 2>/dev/null | grep -v node_modules | head -20 || echo "✅ Clean - no secrets detected"
rm -rf verify-<repo-name>
```

---

## Existing GitHub Repos (vincentsativa)

Full list as of 2026-05-26:

| Repo | Contents | Last Pushed |
|---|---|---|
| `clawdbot` | Clawd bot project | — |
| `larry-bot` | Larry bot | — |
| `larry-bot-rebuild` | Larry bot rebuild | — |
| `NoMoreWars` | NoMoreWars project | — |
| `phantom-byte-funnels` | PhantomByte funnel pages | May 24 | PRIVATE |
| `PhantomByte-Dev` | Entire workspace (mono backup) | — | PRIVATE |
| `profile` | GitHub profile | — | PUBLIC |
| `sativa-ai-ultra` | Ultra AI project | — | PRIVATE |
| `the-truth` | Truth site | — | PRIVATE |
| `the-truth-v2` | Truth site v2 | — | PRIVATE |
| `trends-tracker-free` | Trends tracker | — | PRIVATE |
| `vincent-sativa-website` | vincent-sativa.com | May 24 | PUBLIC |
| `articles-phantom-byte` | articles.phantom-byte.com | May 26 | PUBLIC |
| `phantom-byte-website` | phantom-byte.com | May 26 | PUBLIC |
| `articles-site-source` | Astro source for articles | May 26 | PRIVATE |
| `phantom-byte-funnels-ready` | Funnel pages (ready) | May 26 | PRIVATE |
| `phantom-byte-contact-api` | Contact API | May 26 | PRIVATE |
| `phantom-ai` | Phantom AI app | May 26 | PRIVATE |
| `phantom-byte-landing-page` | Landing page | May 26 | PUBLIC |
| `pi-agent-backup` | **MY OWN pi config/skills/extensions ("PI BACKUP")** | Jun 10 / Aug 7 | PUBLIC |

## Quick Reference

| Domain | Live URL | Local Dir | GitHub Repo |
|---|---|---|---|
| Main | `https://phantom-byte.com/` | `workspace/phantom-byte-website/` | `phantom-byte-website` | PUBLIC |
| Articles | `https://articles.phantom-byte.com/` | `workspace/articles/` | `articles-phantom-byte` | PUBLIC |
| Personal | `https://vincent-sativa.com/` | `workspace/vincent-sativa-website/` | `vincent-sativa-website` | PUBLIC |

### GCP Project

All Cloud Run services are under: `gen-lang-client-0237860564` (us-central1)

Key Cloud Run services:
- `articles` — articles.phantom-byte.com (from `workspace/articles/`)
- `landing-page` — landing page (from `workspace/landing-page/`)
- `phantom-byte-website` — phantom-byte.com (from `workspace/phantom-byte-website/`)

### Credentials

- GitHub user: `vincentsativa`
- GitHub token stored in `~/.git-credentials`
- Git configured in `~/.gitconfig`
