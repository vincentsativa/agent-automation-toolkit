---
name: scraping-js-rendered-docs
description: "Fetch JS-rendered SPA docs via scrapling get_all_text."
trigger: "Fetching Google Search Central / developers.google.com docs, or any client-rendered SPA documentation, reference, or single-page-app site where basic scrapling Fetcher returns an empty body."
---

# Scraping JS-Rendered SPA Docs with Scrapling

Many modern documentation sites (developers.google.com, Google Search Central, ReadTheDocs SPA builds, Next.js docs) are **client-rendered single-page apps**. The article text is NOT in the raw HTML, it's rendered by JavaScript after load. This trips up basic scrapling and requires a specific approach.

## The symptom

- `Fetcher.get(url)` returns **HTTP 200 but empty bytes** for `page.body`.
- `StealthyFetcher.fetch()` returns 200 but `page.text` is `''` (empty string), while `page.body` IS full HTML (~200KB+) and `page.get_all_text()` returns the full rendered article text (~15–35KB).

## The fix, response object IS an Adaptor

Do NOT read `page.body` (raw bytes) and do NOT rely on `page.text`. The `StealthyFetcher` **response object itself is an Adaptor** with `css()` / `get_all_text()` directly callable:

```python
from scrapling.fetchers import StealthyFetcher

sf = StealthyFetcher()
p = sf.fetch(url, headless=True, network_idle=True, timeout=40000)
# Directly on the response object, NOT p.body, NOT p.text:
text = p.get_all_text(' ', strip=True)
# Or target the content node:
main = p.css('main')
h1 = p.css('h1::text').get()
```

This returns the full rendered article text even when `p.text` is empty.

## Pitfall, timeout is in MILLISECONDS

`StealthyFetcher.fetch(timeout=...)` takes **milliseconds**, not seconds. Passing `timeout=60` means 60ms and fails instantly with `Page.goto: Timeout 60ms exceeded` (retried 3x then raises `TimeoutError`). Always pass e.g. `timeout=40000` (40s) for real navigation.

## Pitfall, stdlib-shadowing module in cwd

If you `cd` into a directory containing a stray `inspect.py` (or other stdlib-shadowing file) before running a scrapling script, `import scrapling` breaks with `ImportError: cannot import name 'Fetcher' from partially initialized module ... (most likely due to a circular import)`. Run from a clean dir or delete the stray file.

## Workflow for fetching a docs article

1. Use `StealthyFetcher` (basic `Fetcher` returns empty for SPAs).
2. `timeout=40000`, `headless=True`, `network_idle=True`.
3. Extract via `p.get_all_text(' ', strip=True)` directly on the response.
4. Save the raw text to a file; then distill into the deliverable.
5. Verify the raw text file is non-empty and contains actual article content (check length, look for the article body, not just nav boilerplate).

## Reference

- See `references/google-search-central-fundamentals.md` for a distilled fundamentals summary produced from the three Search Central docs pages (a worked example of this workflow).
