---
name: scrapling-fallback-rule
description: Scrapling first for web extraction. Browser only for interactive pages.
trigger: "ANY web research, scraping, content extraction, or site access task. Load at session start."
---

# Scrapling First, Browser Only for Interactive Pages

This is a hard rule, not optional. Pinned — the curator cannot archive or delete it.

## Step 1: Scrapling Fetcher FIRST (default tool, not fallback)

For ALL content fetching, use scrapling Fetcher first. This is the default tool, not a last resort.

```python
from scrapling.fetchers import Fetcher, StealthyFetcher

# Default: basic fetcher
f = Fetcher()
page = f.get("https://example.com")
print(page.status, page.text[:500])

# Protected sites: StealthyFetcher
sf = StealthyFetcher()
page = sf.fetch("https://x.com/someuser", headless=True, network_idle=True)
```

## Step 2: Browser tools ONLY for interactive pages

Browser tools (`browser_navigate`, `browser_click`) ONLY for:
- Interactive pages: forms, login flows, JS-heavy SPAs.
- Visual verification (CAPTCHA via browser_vision).

Not for plain content retrieval — use scrapling.

## Step 3: If scrapling Fetcher gets blocked

Try `StealthyFetcher`.

## Step 4: If StealthyFetcher gets blocked

Launch **Rotunda** (Firefox fork with Juggler protocol, evades automation detection, humanizes keystroke cadence/mouse path).

Playwright Firefox with:
```
executable_path=~/.cache/rotunda/browsers/official/0.3.5-150.0.1/rotunda
headless=True
no_viewport=True
```

## Step 5: Combine

Use Rotunda for the session, feed resulting HTML back into scrapling's `Adaptor` parser for adaptive extraction.

## Step 6: Track blocked sites

When a site blocks you, note it and avoid wasted retries.

## Known-blocking sites (now populated)

- google.com (CAPTCHA)
- bing.com (CAPTCHA/Cloudflare)
- duckduckgo.com (CAPTCHA)
- reddit.com (CAPTCHA/block)

## Priority

Scrapling first, always. Only fall back to browser tools if scrapling fails AND you've moved through the ladder (Fetcher → StealthyFetcher → Rotunda). Matches the scrapling-or-death enforcement.
