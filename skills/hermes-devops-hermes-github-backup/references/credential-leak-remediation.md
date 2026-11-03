# Credential Leak Remediation

When live API keys or tokens have already been pushed to the backup repo, you must purge them from git history — not just delete the current file.

## Detection

Check what's in the repo before pushing:

```bash
# Check if sensitive files are tracked
git ls-files config/
git ls-files | grep -E '\.env|config\.yaml'

# Check if tokens appear in any committed file
git grep -n 'TELEGRAM_BOT_TOKEN\|GITHUB_TOKEN\|api_key' HEAD -- config/
```

## Remediation: git filter-branch

Remove files from all history (not just HEAD):

```bash
cd /tmp/hermes-backup
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch config/.env config/config.yaml' \
  --prune-empty -- --all
```

Then force-push to rewrite remote history:

```bash
git push --force origin main
```

## Remediation: git-filter-repo (alternative)

If `git-filter-repo` is available (install via `pip install git-filter-repo` or `apt install git-filter-repo`):

```bash
cd /tmp/hermes-backup
git filter-repo --path config/.env --path config/config.yaml --invert-paths
git remote add origin https://github.com/vincentsativa/wsl-hermes-backup.git
git push --force origin main
```

## Post-Remediation

1. **Rotate any exposed tokens.** If the `.env` or `config.yaml` was public even briefly, assume the keys are compromised. Generate new tokens for:
   - OpenRouter API key
   - Telegram bot token
   - GitHub PAT
2. **Add a `.gitignore`** to prevent re-occurrence (see main SKILL.md).
3. **Update the backup script** to never sync sensitive files (see `scripts/hermes-backup.sh`).

## Prevention

The backup script and `.gitignore` are the primary defense. The script should never `rsync` `config.yaml` or `.env` into the backup dir. The `.gitignore` is a safety net for manual operations.
