# Fetching Pinterest's Official SEO / Academy Docs

Validated 2026-08-02. When a task needs Pinterest's own rules (SEO, distribution,
content best practices), pull from the official sources below.

## Authoritative Source URLs
- **Creator Academy / Fundamentals** — `https://create.pinterest.com/fundamentals/`
  (three-pillar framework: Make a Plan / Create Impactful Content / Optimize for Success)
- **Pin performance & distribution** — `https://help.pinterest.com/en-gb/business/article/pin-performance-and-distribution`
  (the current authoritative SEO/discovery doc — carries Pinterest's own keyword and
  content-quality rules)
- **DEAD URL:** `help.pinterest.com/en/business/article/pinterest-seo` returns a 404.
  The old help-center SEO article is gone; use the Pin performance doc instead.

## Fetch Technique (JS-rendered React — scrapling does NOT work here)
- Both `create.pinterest.com` and `help.pinterest.com` are React/JS-rendered.
- `scrapling.fetchers.Fetcher` returns HTTP 200 but an **empty body** (length 0).
- `scrapling.fetchers.StealthyFetcher` may throw `Page.goto: Timeout Nms exceeded`
  (it misinterprets the timeout arg as milliseconds and gives up after 3 attempts).
- **Working path: `browser_navigate` + `browser_snapshot`.** These are NOT anti-bot
  sites — just JS-only — so the browser is the right (and constitution-sanctioned)
  fallback for interactive-JS pages.
- In-body links (e.g. the "best practices" link) are often NOT plain `<a>` anchors in
  the DOM — `document.querySelectorAll('a')` returns nothing useful. If you need a
  linked sub-page, find it via `web_search` instead of scraping the anchor hrefs.

## Source-Authority Note
The fine-grained SEO formatting (front-load pin title, primary keyword in first ~50
chars of description, ~450-500 char description, 2:3 ratio) is layered best-practice
on top of the official docs, not verbatim Pinterest text. When citing, keep that
distinction: the algorithm/distribution rules are official; the formatting specifics
are operational practice. The `pinterest-academy` skill holds the consolidated ruleset.
