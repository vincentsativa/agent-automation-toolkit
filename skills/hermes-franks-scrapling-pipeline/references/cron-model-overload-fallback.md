# Cron Job Failures: Model Provider Overload (HTTP 503)

## Context

The weekly cron job (`6accb5651479`) failed on its first run (May 4, 2026 at 13:00 EDT) with:

```
RuntimeError: HTTP 503: Error code: 503 - {'error': 'Server overloaded, please retry shortly'}
```

A retry at 13:39 got the same error with a different ref ID — confirming it was a persistent provider overload, not a transient blip.

**Root cause:** The cron job uses the default model (DeepSeek-v4-flash via Ollama.com), which was under heavy load. Scrapling itself was healthy — manual Python terminal tests returned HTTP 200 on all 9 targets.

## Diagnosis

1. Run Scrapling directly via Python in terminal — if all targets return 200, Scrapling is fine.
2. The 503 is coming from the model provider (the agent that processes the scraping task), not from Scrapling or the target sites.
3. The cron job has no model override set — it inherits whatever the current default is.

## Fallback: Manual Pipeline Run

When the cron job fails due to model overload, run the pipeline manually:

### Step 1: Verify Scrapling still works
```bash
~/hermes-agent/venv/bin/python3 -c "
from scrapling.fetchers import StealthyFetcher
sf = StealthyFetcher()
page = sf.fetch('https://simonwillison.net', headless=True, network_idle=True)
print(f'Status: {page.status}, Body: {len(page.body)} bytes')
"
```

### Step 2: Scrape all targets via Python terminal
Run the scrape script directly. All 9 targets known to be reachable:
- simonwillison.net
- levels.io (redirects to X — will show login wall but profile data is visible)
- www.designjoy.co (redirects from designjoy.co)
- lilianweng.github.io
- danluu.com
- marclou.com
- www.lennysnewsletter.com (redirects from lennysnewsletter.com)
- www.swyx.io (redirects from swyx.io)
- ollama.com/blog (NOT ollama.ai/blog — 301 redirect)

Use StealthyFetcher with `headless=True, network_idle=True`. For sites that are JS-heavy (levels.io/X, lennysnewsletter.com/Substack, designjoy.co), use browser_navigate for richer content extraction.

### Step 3: Extract content from key targets
Use browser_navigate on the most important targets for full content extraction:
- **simonwillison.net** — most active target, always has new posts
- **swyx.io** — publishes semi-regularly
- **marclou.com** — revenue data visible
- **danluu.com** — static archive but check for new posts
- **lilianweng.github.io** — silent since May 2025 but worth confirming

Collect: post titles, publish dates, content types, structural changes, revenue data.

### Step 4: Build the JSON + brief
Use write_file to save:
1. Raw JSON to `~/data/scrapling/raw/weekly-YYYY-MM-DD.json`
2. Intelligence brief to `/mnt/c/Users/<user>/workspace/data/scrapling/weekly-brief-YYYY-MM-DD.md`
   - Also copy to Desktop: `cp ... /mnt/c/Users/<user>/Desktop/`

### Step 5: Verify
- `test -f` both files exist
- `test -s` both files non-empty
- Python JSON parse on the raw file
- Brief has all 6 sections

## Model-Override Note

The cron job should NOT be permanently pinned to a different model — Vinny wants to leave it as the default and swap back when the provider recovers. If you re-run the manual fallback, use whatever model is available and working (switch to another in your provider chain) rather than the default.

## Paths

- Raw JSON (WSL only): `~/data/scrapling/raw/weekly-YYYY-MM-DD.json`
- Weekly brief (Windows): `C:\Users\<user>\workspace\data\scrapling\weekly-brief-YYYY-MM-DD.md`
