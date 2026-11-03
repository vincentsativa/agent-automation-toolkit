---
name: scrapling-or-death
description: Use for web fetch. Scrapling first, never curl or browser.
trigger: "ANY web content retrieval, search, news, docs, or API page fetch. Load before every web access."
---

# Scrapling or Death

THE RULE: for ANY web content fetch (search, news, docs, APIs, any URL), use scrapling via `terminal()` or `execute_code()`. Period.

Vinny will be rightfully pissed. This is the third time. There will not be a fourth.

## Interpreter: pick the one that has scrapling

On this Windows host Hermes's bundled Python does not carry scrapling; the system Python 3.11 install does. Confirm and use it explicitly, because the default `python` on PATH is the bundled one:

```bash
for p in ~/AppData/Local/Programs/Python/Python3*/python; do "$p" -c "import scrapling" 2>/dev/null && echo "HAS SCRAPLING: $p"; done
```

Then set `PY=~/AppData/Local/Programs/Python/Python311/python` and invoke `"$PY" -c "..."` for every fetch. A ModuleNotFoundError there means the wrong interpreter, not a missing install, so check the interpreter before installing anything.

## Throwaway scripts: write them into their own clean directory

Never write a probe script into the Hermes scratch or cache dir. That tree holds helper modules named after stdlib modules (`select.py`, `inspect.py`, `common.py`), and Python puts a script's own directory on `sys.path`, so the copy shadows the real stdlib and dies with a misleading error far from the cause (a circular-import `AttributeError` raised from inside `urllib`, or a broken `import select` inside `socket`). Create a fresh directory such as `~/AppData/Local/hermes/cache/pbscan/` for the probe and run it from there with a native forward-slash path, since native Python does not translate an MSYS `/tmp` path. The same applies to running a skill's own script: run it from the skill directory, not from scratch.

## Basic fetch

```python
from scrapling.fetchers import Fetcher
f = Fetcher()
page = f.get('https://example.com', follow_redirects=True)
text = page.get_all_text() or ''
print(page.status, len(text))
print(text[:500])
```

- Read `page.get_all_text()` for visible text and `page.html_content` for links. `page.text` can come back empty on a 200 for some sites, so print a length and slice what you got; a silent empty read looks like a broken fetch when the page actually loaded fine.
- The `deprecated ... use Fetcher.configure()` warning prints on every call. Append `2>/dev/null` to the shell command to keep the output readable.

## Stealth fetch (Cloudflare, CAPTCHA, bot detection)

```python
from scrapling.fetchers import StealthyFetcher
sf = StealthyFetcher()
page = sf.fetch('https://example.com', headless=True, network_idle=True)
```

## FORBIDDEN (never do these for web content)

- `curl` for web content. (curl IS allowed for API calls and file downloads — not for scraping HTML content.)
- `browser_navigate` for content fetch (only for interactive JS pages that need a real browser).
- ANY attempt on known-blocked sites (below).

## Known-blocked sites (skip entirely, do NOT attempt)

- google.com (CAPTCHA)
- bing.com (CAPTCHA/Cloudflare)
- duckduckgo.com (CAPTCHA)
- reddit.com (CAPTCHA/block)

If a task needs data from one of these, tell Vinny it's blocked and suggest an alternative source.

## Enforcement

Before every web access ask: "Am I using scrapling?" If no, fix it before proceeding.
