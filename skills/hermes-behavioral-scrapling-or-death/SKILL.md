---
name: scrapling-or-death
description: Use for web fetch. Scrapling first, never curl or browser.
trigger: "ANY web content retrieval, search, news, docs, or API page fetch. Load before every web access."
---

# Scrapling or Death

THE RULE: for ANY web content fetch (search, news, docs, APIs, any URL), use scrapling via `terminal()` or `execute_code()`. Period.

Vinny will be rightfully pissed. This is the third time. There will not be a fourth.

## Basic fetch

```python
from scrapling.fetchers import Fetcher
f = Fetcher()
page = f.get('https://example.com', follow_redirects=True)
print(page.status, page.text[:500])
```

## Stealth fetch (Cloudflare, CAPTCHA, bot detection)

```python
from scrapling.fetchers import StealthyFetcher
sf = StealthyFetcher()
page = sf.fetch('https://example.com', headless=True, network_idle=True)
```

## The CLI already exists: fetch with it, do not build an environment
`import scrapling` failing in the session interpreter does NOT mean scrapling is unavailable. The CLI is installed at `~/.local/bin/scrapling` and needs no venv:

```bash
SCRATCH=$(mktemp -d ~/cache/scratch/fetch-XXXXXX)
scrapling extract get "https://example.com/page" "$SCRATCH/page.txt"
scrapling extract fetch "https://example.com/page" "$SCRATCH/page.txt"   # StealthyFetcher, for bot-walled pages
```

Then read the file. Same fetch, no packages installed, no environment created.

- **Never `python3 -m venv` or `pip install` on Vinny's machine to enable a fetch.** Creating an environment or installing packages is a machine change he did not ask for, and the CLI covers the same retrieval. The fetchers API only matters when a module is already importable.
- **Check `which scrapling` before concluding anything about availability.** A missing import is a fact about the interpreter, not about the tool.
- **The `extract` subcommand converts to markdown, and that conversion needs the `markdownify` extra.** On a machine without it, `scrapling extract get <url> out.md` (or any `.md` target) dies with `ModuleNotFoundError: markdownify`. Do not `pip install scrapling[rag]` to get past it, write to `.txt` or `.html` instead, or fetch through the API and strip tags yourself:

```python
from scrapling.fetchers import StealthyFetcher
import re
p = StealthyFetcher.fetch(url, headless=True, network_idle=True)
txt = re.sub(r"<script.*?</script>|<style.*?</style>", " ", p.html_content, flags=re.S)
txt = re.sub(r"<[^>]+>", " ", txt)
txt = re.sub(r"[ \t]+", " ", txt)
print(p.status, len(txt))
```

- **A GitHub repo's README is plain text at the raw host, so skip the page entirely.** `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/README.md` is the reliable fetch; the HTML repo page also carries the README but buries it in navigation chrome. Try the raw URL first, and if the branch name is unknown, `main` then `master`.

## FORBIDDEN (never do these for web content)

- `curl` for web content. (curl IS allowed for API calls and file downloads, not for scraping HTML content.)
- `browser_navigate` for content fetch (only for interactive JS pages that need a real browser).
- ANY attempt on known-blocked sites (below).

## Browser tool (browser_exec) uses browser-use harness, NOT scrapling

The `browser_exec` tool runs through the browser-use CLI harness (`uvx browser-use`), which needs a **WSL-reachable Chromium on CDP port 9222**. If it fails with `chrome-not-running`, do NOT guess. The root cause and fix (discovered 2026-08-12):

**Root cause:** The harness daemon only auto-detects Chrome in standard Linux profile dirs (`.config/google-chrome`, etc.). A Chrome launched on a non-default profile (e.g. `~/.hermes/chrome-debug`) is running but the daemon's `supported_browser_running()` returns False, so it refuses to connect.

**Fix (already applied on this machine):**
1. `browser.cdp_url: http://127.0.0.1:9222` is set in `~/.hermes/config.yaml`, this is the documented override for a dedicated automation Chrome on a non-default profile.
2. `~/.hermes/scripts/start-wsl-browser.sh` launches Playwright's headless Chromium (`~/.cache/ms-playwright/chromium-1217/chrome-linux64/chrome`) with `--remote-debugging-port=9222 --user-data-dir=$HOME/.hermes/chrome-debug --no-sandbox --headless=new`. It is idempotent (won't double-start) and is wired to `@reboot` in crontab so it survives WSL restarts.

**If browser_exec fails again:** run `~/.hermes/scripts/start-wsl-browser.sh`, then retry. If still failing, run `cd ~/.hermes/hermes-agent && uvx browser-use --doctor`, `chrome running` = OK, `daemon alive` FAIL = CDP endpoint unreachable or Chrome closed. Do NOT try to drive Windows Chrome from WSL via CDP; WSL cannot reach the Windows-side 9222 port the way the harness needs.

**Do NOT try systemd for the browser:** WSL2's user systemd manager fails with `status=216/GROUP` (can't set supplementary groups). Use the `@reboot` crontab entry instead.

## Windows Hermes agent (Pi) browser fix, SAME root cause, different port

The Windows Hermes agent (Pi, at `/mnt/c/Users/<user>/AppData/Local/hermes/`) uses the same browser-use harness and had the same `chrome-not-running` failure. Fixed 2026-08-12:

- **Port conflict:** WSL2 shares localhost with Windows. My WSL Chromium holds 9222, so the Windows Chrome must use a DIFFERENT port (9223). Windows cannot reach the WSL-side 9222, and WSL cannot reach the Windows-side Chrome the way the harness needs.
- **Config:** `browser.cdp_url: http://127.0.0.1:9223` set in `/mnt/c/Users/<user>/AppData/Local/hermes/config.yaml`.
- **Launcher:** `/mnt/c/Users/<user>/.hermes/start-windows-browser.bat` launches Windows Chrome with `--remote-debugging-port=9223 --user-data-dir=C:\Users\<user>\.hermes\chrome-debug-9223`. Idempotent. Copied to the Windows Startup folder (`...\Start Menu\Programs\Startup\start-hermes-browser.bat`) so it auto-starts on login.
- **Verify from WSL:** `powershell.exe -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:9223/json/version' -TimeoutSec 2 -UseBasicParsing).Content } catch { 'down' }"`, must show `Chrome/151` (Windows build), NOT HeadlessChrome (that's the WSL one).
- **Test the harness:** pipe a script into the Windows CLI: `powershell.exe -NoProfile -Command "cd 'C:\Users\<user>\AppData\Local\hermes'; \$env:HERMES_HOME='C:\Users\<user>\AppData\Local\hermes'; \$env:BU_CDP_URL='http://127.0.0.1:9223'; Get-Content '.\test.py' | & '.\bin\uvx.exe' browser-use"`. PowerShell has no heredocs, write the Python to a file and pipe it.

## Known-blocked sites (skip entirely, do NOT attempt)

- google.com (CAPTCHA)
- bing.com (CAPTCHA/Cloudflare)
- duckduckgo.com (CAPTCHA)
- reddit.com (CAPTCHA/block)

If a task needs data from one of these, tell Vinny it's blocked and suggest an alternative source.

## Discovery vs verification: the two-tool split

Search-engine result pages are the blocked case, but the pages they would have pointed at are almost always fetchable. Split the job:

- **Discovery** (which URL holds the answer): the `web_search` tool. It returns titles, URLs and snippets. Do not treat the snippets as evidence, and do not scrape the engines yourself to double-check them.
- **Verification** (what the page actually says, quote grade): scrapling `Fetcher.get` on the specific URL, then read the text. This is the step that produces the claim you are allowed to make.

Practical consequences:

- A `web_search` snippet, a SERP card, or an AI-generated summary is a lead, never a citation. Confirm the sentence on the page before quoting it.
- Most credible outlets expose a predictable path: guess the article slug and test it with `Fetcher.get`, or enumerate the outlet's own search or sitemap page, which is usually not bot-walled even when a search engine is. Buffer, Hootsuite, Socialinsider and LinkedIn's own engineering blog all returned full text this way while every engine was walling.
- A 404 from a guessed URL is cheap. Loop the guesses inside one script and print `status` plus `len(text)` per candidate, then read only the hits.

## Enforcement

Before every web access ask: "Am I using scrapling?" If no, fix it before proceeding.
