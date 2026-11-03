---
name: github-release-discovery
description: Find the latest full release and latest pre-release (RC/beta) of any GitHub repo via the GitHub API. Includes a cron-environment jq fallback for when execute_code is blocked.
---

# GitHub Release Discovery

Find the latest **stable** release and the latest **pre-release** (RC/beta)
of any GitHub repo using the GitHub API.

## Basic approach

Fetch the releases endpoint and filter:

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/releases" -o releases.json
```

## Cron-environment jq fallback

In cron environments `execute_code` may be **blocked**. Use `terminal` +
`jq` instead.

### Latest stable release

```bash
jq '.[] | select(.prerelease == false and .draft == false) | .tag_name' releases.json | head -n 1
```

### Latest pre-release (RC/beta)

```bash
jq '.[] | select(.prerelease == true and .draft == false) | .tag_name' releases.json | head -n 1
```

### Filter assets by name

To find the Linux amd64 asset for a release:

```bash
jq '.[] | select(.prerelease == false and .draft == false) | .assets[] | select(.name | contains("linux") and contains("amd64")) | .browser_download_url' releases.json | head -n 1
```

## Notes / pitfalls

- Always filter out `.draft == true` — draft releases are not public.
- `head -n 1` gives the newest matching release because the API returns them
  in creation order (newest first).
- If `execute_code` is available (interactive), prefer it; fall back to the
  jq path only when blocked (e.g. in cron).
- **A rejected version answer means you used the wrong binary, not that the answer is wrong.** If Vinny says "wrong" to a version you reported, do NOT re-run the same command and present the identical output again. Re-check for a second install (WSL snap vs Windows client) or ask what he means. On this machine the WSL `ollama` snap and the Windows client at `/mnt~/AppData/Local/Programs/Ollama/ollama.exe` report different versions; the Windows client is authoritative for what Vinny runs.
