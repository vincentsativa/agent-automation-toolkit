---
name: github-release-discovery
description: Find the latest full release and latest pre-release (RC/beta) for any GitHub project, handling the releases-vs-tags API distinction.
category: devops
---

# GitHub Release Discovery

Find the latest version of any GitHub project — both full releases and pre-releases (RCs, betas).

## The Releases vs Tags Trap

The GitHub **Releases API** (`/releases`) only returns entries that have a GitHub Release page. Many RC/beta tags exist as **git tags only** — no release entry, no compiled assets. To find them you must check the **Tags API** (`/tags`).

## Procedure

### 1. Poll the Releases API (full releases)

```bash
curl -sL "https://api.github.com/repos/OWNER/REPO/releases?per_page=100"
```

- `prerelease: false` + `draft: false` = full releases
- Sort by tag version, pick the newest
- Paginate with `&page=2`, `&page=3` if needed (up to 5 pages = 500 records)

### 2. Poll the Tags API (all tags including RCs)

```bash
curl -sL "https://api.github.com/repos/OWNER/REPO/tags?per_page=100"
```

- This returns **every** git tag including RC tags that have no release entry
- Paginate the same way

### 3. Filter and sort

Use Python semver sorting that handles `-rcN` suffixes:

```python
def tag_key(tag_name):
    v = tag_name.lstrip('v')
    parts = v.split('-')
    base = parts[0].split('.')
    rc = int(parts[1][2:]) if len(parts) > 1 and parts[1].startswith('rc') else 9999
    return [int(x) for x in base] + [rc]
```

### 4. Check for compiled assets

Just because a tag exists doesn't mean builds are available. Check:

```python
assets = release_entry.get('assets', [])
build_assets = [a for a in assets if a['name'] matches your platform]
```

Tag-only releases (no release entry) only contain source code zip/tar.gz.

## Checking a Specific Tag

```bash
curl -sL "https://api.github.com/repos/OWNER/REPO/releases/tags/vX.Y.Z-rcN"
```

If it returns `{"message": "Not Found"}`, it's tag-only (no release page).

## Cron / jq Fallback (When execute_code Is Blocked)

In cron environments `execute_code` may be blocked. Use `terminal` + `jq` instead. Download the releases JSON, then filter:

```bash
# Save releases to a file
curl -sL "https://api.github.com/repos/OWNER/REPO/releases?per_page=100" -o /tmp/releases.json

# Latest stable (non-prerelease, non-draft)
jq '.[] | select(.prerelease == false and .draft == false) | .tag_name' releases.json | head -n 1

# Latest pre-release
jq '.[] | select(.prerelease == true) | .tag_name' releases.json | head -n 1

# Filter assets by platform (e.g. linux + amd64)
jq '.[] | .assets[] | select(.name | contains("linux") and contains("amd64"))' releases.json
```

## Pitfalls

- **GitHub API paginates at 100 per page** — always check multiple pages. One page is not enough.
- **"Latest" prerelease is NOT the API's default sort order** — the API returns by creation date descending. Sort tags yourself by semver.
- **Release entry != tag** — a tag can exist without having a release entry. Check both APIs.
- **Cloud/SaaS versioning** is sometimes independent of the OSS repo's version scheme (Ollama Cloud v0.30.0-rc31 is not in the Ollama OSS repo releases).
- **Draft releases are excluded** — filter them out.
- The user may already have a newer RC installed locally that doesn't appear in any GitHub API result.
- **GitHub "latest release" is NOT what the user is running.** A release report that only quotes the GitHub API answers "what's the newest tag" but not "what's on this machine." For Vinny's Ollama specifically: he runs the Windows install at `/mnt/c/Users/<user>/AppData/Local/Programs/Ollama/ollama.exe`. The WSL `ollama` is a separate snap build that does NOT reflect his Windows install. When he says the version he's on, that IS the ground truth — never contradict it with a GitHub release page or a WSL snap build. (Aug 26-27, 2026: repeated two nights, arguing with him over a version he was literally looking at.)
- **Ollama's `--version` output has a known false line.** `ollama --version` prints TWO lines: `ollama version is X` (the server line) and `Warning: client version is Y` (the client line). The FIRST line is BS/stale and must be IGNORED — the REAL version is the `client version is Y` line. This is a long-standing Ollama bug (server/client version lines don't line up). Do NOT quote the `ollama version is X` line as the installed version, and do NOT hardcode a specific number into cron prompts (it goes stale on every update) — instruct the job to read whatever the `client version is` line shows. Vinny verified this months ago with another agent; re-litigating it is a known trigger.
- **A rejected version answer means you used the wrong binary, not that the answer is wrong.** If Vinny says "wrong" to a version you reported, do NOT re-run the same command and present the identical output again. Re-check for a second install (WSL snap vs Windows client) or ask what he means. On this machine the WSL `ollama` snap and the Windows client at `/mnt/c/Users/<user>/AppData/Local/Programs/Ollama/ollama.exe` report different versions; the Windows client is authoritative for what Vinny runs.

## References

- `~/skills/github-release-discovery/references/find-tags.py` — reusable script for this workflow
