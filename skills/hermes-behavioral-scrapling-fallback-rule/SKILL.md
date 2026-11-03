---
name: scrapling-fallback-rule
description: "HARD RULE: scrapling on block. Track blocked sites."
trigger: "ALWAYS active. Hard behavioral rule for every web access attempt — browser_navigate, web_search, web_extract, curl, or any tool that fetches from an external website."
---

# HARD RULE: Scrapling First, Browser Only for Interactive Pages

## The Rule

This is a **non-negotiable behavioral rule**. Follow it on every web access attempt without exception.

### Step 1: Use Scrapling FIRST for ALL content fetching

For ANY web content fetch — search results, news articles, blog posts, documentation, API responses, any URL — use **scrapling Fetcher** via `terminal()` or `execute_code()` as the DEFAULT tool. Do NOT reach for browser_navigate first.

```python
from scrapling.fetchers import Fetcher

f = Fetcher()
page = f.get('https://example.com', follow_redirects=True)
print(page.status)
# CSS selectors work
title = page.css('h1::text').get()
text = page.css('body::text').getall()
links = page.css('a::attr(href)').getall()
```

Run via: `cd ~/.hermes/hermes-agent/venv && python3 -c "..."`

### Step 2: Only use browser tools for interactive pages

Browser tools (`browser_navigate`, `browser_click`, etc.) are ONLY for:
- Pages that require JavaScript interaction (forms, login flows, JS-heavy SPAs)
- Pages that need clicking, typing, or scrolling
- Visual verification (CAPTCHA solving via browser_vision)

### Step 3: If scrapling Fetcher gets blocked, try StealthyFetcher

```python
from scrapling.fetchers import StealthyFetcher
sf = StealthyFetcher()
page = sf.fetch("URL", headless=True, network_idle=True)
```

### Step 4: Escalate to Rotunda when StealthyFetcher gets blocked

If StealthyFetcher returns 403/429/CAPTCHA, launch **Rotunda** — a Firefox fork with Juggler protocol that evades automation detection and humanizes input (keystroke cadence, mouse path prediction, natural typing speed).

```python
import os
from playwright.sync_api import sync_playwright
ROTUNDA_BIN = os.path.expanduser(
    '~/.cache/rotunda/browsers/official/0.3.5-150.0.1/rotunda'
)
with sync_playwright() as p:
    browser = p.firefox.launch(headless=True, executable_path=ROTUNDA_BIN)
    context = browser.new_context(no_viewport=True)
    page = context.new_page()
    page.goto('https://example.com')
    # Use standard Playwright methods for interaction
    text = page.locator('h1').first.inner_text()
    browser.close()
```

Rotunda makes you look human without lying about your fingerprint — real GPU, real OS, real IP from your home network. It only removes automation signatures.

### Step 5: Combine both for maximum effectiveness

Use Rotunda for the browser session (fingerprint-evading navigation, humanized input, CAPTCHA resolution) and feed the resulting HTML back into Scrapling's `Adaptor` parser for adaptive CSS extraction and crawling.

### Step 6: Track Blocked Sites

Maintain this list. When a site blocks scrapling, add it here.

## Known Blocking Sites

- google.com (CAPTCHA on search)
- bing.com (CAPTCHA/Cloudflare)
- duckduckgo.com (CAPTCHA on automated requests)
- reddit.com (CAPTCHA/block on automated requests)

## Verification

After adding a site to the blocked list, verify the rule works by using scrapling first on the next access attempt to that domain.
