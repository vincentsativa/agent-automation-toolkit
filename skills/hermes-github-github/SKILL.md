---
name: github
description: >-
  Complete GitHub workflow guide: authentication, code review, issues, PRs,
  repo management, releases, Actions, secrets, and codebase inspection. One
  skill covering the full GitHub API surface via `gh` CLI or `git`+`curl`
  fallback.
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Git, Pull-Requests, Code-Review, Issues, Actions, Releases, Auth]
---

# GitHub Complete Workflow

A comprehensive guide for working with GitHub through Hermes Agent. Every
section shows `gh` CLI first, then `git`+`curl` fallback for machines without
`gh`.

## Subsections

1. **[Authentication](#1-authentication)** — HTTPS tokens, SSH keys, gh CLI login
2. **[Code Review](#2-code-review)** — Review local changes and PR diffs
3. **[Issues](#3-issues)** — Create, triage, label, assign, comment
4. **[Pull Requests](#4-pull-requests)** — Branch, commit, open, CI, merge
5. **[Repository Management](#5-repository-management)** — Clone, create, fork, settings
6. **[Releases & Actions](#6-releases--actions)** — Releases, workflows, CI monitoring
7. **[Codebase Inspection](#7-codebase-inspection)** — LOC, language breakdown, ratios
8. **[Secrets Management](#8-secrets-management)** — GitHub Actions secrets
9. **[Release Discovery](#9-release-discovery)** — Find latest full release and pre-release across repos
10. **[Quick Reference](#10-quick-reference)** — Cheatsheet tables

---

## Universal Auth Detection

All sections share this setup block. Run at the start of any GitHub workflow:

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi
echo "AUTH_METHOD=$AUTH"

REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [ -n "$REMOTE_URL" ]; then
  OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
  OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
  REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
fi
```

For standalone scripts, the helper script at `scripts/gh-env.sh` exports these.

---

## 1. Authentication

### Git-Only: HTTPS with Personal Access Token

```bash
# Set up credential helper
git config --global credential.helper store
# Then do a test operation — enter username + token as password
git ls-remote https://github.com/<user>/<repo>.git

# Set identity
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

Alternative: SSH key authentication (`ssh-keygen -t ed25519`, then add to GitHub).

### gh CLI Authentication

```bash
# Interactive browser login
gh auth login

# Token-based (headless)
echo "<TOKEN>" | gh auth login --with-token
gh auth setup-git

# Verify
gh auth status
```

### API Access Without gh

```bash
export GITHUB_TOKEN="<token>"
curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

See `references/github-auth-detailed.md` for full SSH setup, credential troubleshooting, and multi-account patterns.

---

## 2. Code Review

### Local Changes (Pre-Push)

```bash
git diff main...HEAD --stat                    # Scope
git diff main...HEAD                            # Full diff
git diff main...HEAD -- src/file.py             # File-by-file
git log main..HEAD --oneline                    # Commit history
```

Check for common issues:
```bash
git diff main...HEAD | grep -n "print(\|console\.log\|TODO\|FIXME\|HACK\|XXX\|debugger"
git diff main...HEAD --stat | sort -t'|' -k2 -rn | head -10
git diff main...HEAD | grep -in "password\|secret\|api_key\|token.*=\|private_key"
git diff main...HEAD | grep -n "<<<<<<\|>>>>>>\|======="
```

### Review Output Format

```
## Code Review Summary

### Critical
- **file:line** — Issue description. Suggestion: fix.

### Warnings
- **file:line** — Issue description.

### Suggestions
- **file:line** — Improvement idea.

### Looks Good
- Positive observations.
```

### Reviewing PRs on GitHub

```bash
gh pr view 123
gh pr diff 123
gh pr checkout 123
```

Or with git-only:
```bash
git fetch origin pull/123/head:pr-123
git checkout pr-123
git diff main...pr-123
```

### Leaving Comments

```bash
gh pr comment 123 --body "Overall looks good."
gh pr review 123 --approve --body "LGTM!"
gh pr review 123 --request-changes --body "See inline comments."
```

See `references/review-checklist.md` and `references/review-output-template.md` for the systematic review checklist (correctness, security, code quality, testing, performance, documentation) and templates.

---

## 3. Issues

### Viewing Issues

```bash
gh issue list
gh issue list --state open --label "bug"
gh issue list --assignee @me
gh issue view 42
```

### Creating Issues

```bash
gh issue create \
  --title "Login redirect ignores ?next= parameter" \
  --body "## Description\nAfter logging in..." \
  --label "bug,backend" \
  --assignee "username"
```

Templates at `templates/bug-report.md` and `templates/feature-request.md`.

### Managing Issues

| Action | gh | curl API |
|--------|-----|---------|
| Add labels | `gh issue edit N --add-label ...` | `POST /repos/{o}/{r}/issues/N/labels` |
| Assign | `gh issue edit N --add-assignee ...` | `POST /repos/{o}/{r}/issues/N/assignees` |
| Comment | `gh issue comment N --body ...` | `POST /repos/{o}/{r}/issues/N/comments` |
| Close | `gh issue close N` | `PATCH /repos/{o}/{r}/issues/N` |

### Linking Issues to PRs

Use keywords in PR body: `Closes #42`, `Fixes #42`, `Resolves #42`

---

## 4. Pull Requests

### Branch Creation

```bash
git checkout main && git pull origin main
git checkout -b feat/add-user-authentication
```

Naming: `feat/`, `fix/`, `refactor/`, `docs/`, `ci/` prefixes.

### Commit Convention

```
type(scope): short description

Longer explanation at 72 chars.
```
Types: `feat`, `fix`, `refactor`, `docs`, `test`, `ci`, `chore`, `perf`

### Open a PR

```bash
git push -u origin HEAD
gh pr create --title "feat: add auth" --body "## Summary\n..." --label "enhancement"
```

### Monitor CI

```bash
gh pr checks
gh pr checks --watch
```

### Auto-Fix CI Loop

1. Check CI → identify failures
2. Read logs → understand error
3. Fix code → `git commit -m "fix: ..." && git push`
4. Wait for CI → re-check
5. Repeat up to 3 attempts, then ask user

### Merge

```bash
gh pr merge --squash --delete-branch
gh pr merge --auto --squash --delete-branch   # Auto-merge when checks pass
```

See `references/ci-troubleshooting.md` and `references/conventional-commits.md`.

---

## 5. Repository Management

### Clone

```bash
git clone https://github.com/owner/repo.git
gh repo clone owner/repo
```

### Create

```bash
gh repo create my-project --public --clone
gh repo create my-org/repo --public --clone
```

### Fork

```bash
gh repo fork owner/repo --clone
git remote add upstream https://github.com/owner/repo.git
```

### Settings

```bash
gh repo edit --description "..." --visibility public
gh repo edit --enable-wiki=false --default-branch main
gh repo edit --add-topic "machine-learning,python"
```

### Branch Protection

```bash
# View
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection

# Set up (requires maintainer/admin access)
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection \
  -d '{
    "required_status_checks": {"strict": true, "contexts": ["ci/test", "ci/lint"]},
    "enforce_admins": false,
    "required_pull_request_reviews": {"required_approving_review_count": 1}
  }'
```

---

## 6. Releases & Actions

### Releases

```bash
gh release create v1.0.0 --title "v1.0.0" --generate-notes
gh release create v2.0.0-rc1 --draft --prerelease --generate-notes
gh release list
gh release download v1.0.0 --dir ./downloads
```

### Actions / Workflows

```bash
gh workflow list
gh run list --limit 10
gh run view <RUN_ID> --log-failed
gh run rerun <RUN_ID> --failed
gh workflow run ci.yml --ref main
```

---

## 7. Codebase Inspection (pygount)

Analyze repositories for LOC, language breakdown, file counts:

```bash
pip install pygount
pygount --format=summary --folders-to-skip=".git,node_modules,venv,.venv,__pycache__" .
```

Common folder exclusions:
- Python: `.git,venv,.venv,__pycache__,dist,build,.tox,.eggs,.mypy_cache`
- JS/TS: `.git,node_modules,dist,build,.next,.cache,.turbo,coverage`
- General: `.git,node_modules,venv,.venv,__pycache__,dist,build,vendor,third_party`

Filter by language:
```bash
pygount --suffix=py --format=summary .
pygount --suffix=py,yaml,yml --format=summary .
```

Output formats: `summary` (default), `json` (programmatic), detailed (file-by-file).

Pitfalls:
- Always use `--folders-to-skip` — without it pygount crawls everything
- Markdown counts as 0 code lines (classified as comments)
- For large monorepos, use `--suffix` to target specific languages

---

## 8. Secrets Management

```bash
gh secret set API_KEY --body "your-secret-value"
gh secret set SSH_KEY < ~/.ssh/id_rsa
gh secret list
gh secret delete API_KEY
```

For `gh`-less systems, secrets require encryption with the repo's public key (see `references/github-api-cheatsheet.md`).

---

## 9. Release Discovery

Find the latest version of any GitHub project — both full releases and pre-releases (RCs, betas).

### The Releases vs Tags Trap

The GitHub **Releases API** (`/releases`) only returns entries that have a GitHub Release page. Many RC/beta tags exist as **git tags only** — no release entry, no compiled assets. To find them you must check the **Tags API** (`/tags`).

### Procedure

**1. Poll the Releases API (full releases):**
```bash
curl -sL "https://api.github.com/repos/OWNER/REPO/releases?per_page=100"
```
- `prerelease: false` + `draft: false` = full releases
- Paginate with `&page=2` through `&page=5` (500 records)

**2. Poll the Tags API (all tags including RCs):**
```bash
curl -sL "https://api.github.com/repos/OWNER/REPO/tags?per_page=100"
```

**3. Filter and sort** with Python semver that handles `-rcN` suffixes.

**4. Check for compiled assets** — tag-only releases have only source zip/tar.gz.

### Checking a Specific Tag
```bash
curl -sL "https://api.github.com/repos/OWNER/REPO/releases/tags/vX.Y.Z-rcN"
```

### Pitfalls
- GitHub API paginates at 100 per page — always check multiple pages.
- "Latest" prerelease is NOT the API's default sort order; sort tags by semver yourself.
- Release entry != tag — a tag can exist without a release entry. Check both APIs.
- Cloud/SaaS versioning is sometimes independent of the OSS repo's version scheme.
- Draft releases are excluded — filter them out.

The helper script at `scripts/find-latest-rc.py` (under `github-release-discovery/`) automates this workflow.

## 10. Quick Reference

| Action | gh | curl endpoint |
|--------|-----|--------------|
| List issues | `gh issue list` | `GET /repos/{o}/{r}/issues` |
| Create issue | `gh issue create ...` | `POST /repos/{o}/{r}/issues` |
| View PR | `gh pr view N` | `GET /repos/{o}/{r}/pulls/N` |
| Create PR | `gh pr create ...` | `POST /repos/{o}/{r}/pulls` |
| Merge PR | `gh pr merge N` | `PUT /repos/{o}/{r}/pulls/N/merge` |
| List workflows | `gh workflow list` | `GET /repos/{o}/{r}/actions/workflows` |
| List releases | `gh release list` | `GET /repos/{o}/{r}/releases` |
| Create release | `gh release create ...` | `POST /repos/{o}/{r}/releases` |
| List repos | `gh repo list` | `GET /user/repos` |
| View repo | `gh repo view o/r` | `GET /repos/{o}/{r}` |

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `git push` asks for password | Use PAT as password, or switch to SSH |
| `remote: Permission to X denied` | Token lacks `repo` scope |
| `fatal: Authentication failed` | Stale credentials — `git credential reject` then re-auth |
| `ssh: connect to host github.com port 22: Connection refused` | Try SSH over HTTPS (Host github.com with Port 443) |
| Multiple accounts | SSH keys per host alias, or per-repo credential URLs |