---
name: scrapling
description: "High-performance web scraping framework with stealth fetchers (bypass Cloudflare/Turnstile), adaptive parsing (auto-heal broken CSS selectors), and full crawling toolkit (CrawlSpider, SitemapSpider, LinkExtractor, ShopifySpider). Trigger when Vinny says 'scrapling', 'stealth scrape', 'scrape [url]', or any task requiring anti-bot, self-healing scrape, or crawling. Package: scrapling[fetchers] v0.5. Test script: /mnt/c/Users/<user>/workspace/scripts/test_scrapling.py"
trigger: "user says 'scrapling', 'stealth scrape', 'scrape [url]', or needs to fetch a protected or layout-labile site. Also trigger on: Google Trends, keyword research, SEO research, any task that needs live search-volume data from bot-protected sites."
---

# Scrapling — Stealth + Adaptive Web Scraping

## Access
- **Package:** `scrapling[fetchers]` (live version must be read from the binary, never from this line: `scrapling --version`. It was 0.5 as of the last check)
- **Install:** `pip install scrapling[fetchers]` (or `--force-reinstall` to refresh binaries/fingerprints)
- **Import:** `from scrapling.fetchers import Fetcher, StealthyFetcher`
- **Spider imports:** `from scrapling.spiders import CrawlSpider, SitemapSpider, LinkExtractor, Spider`
- **Test script:** `/mnt/c/Users/<user>/workspace/scripts/test_scrapling.py` (exists and runs; it targets httpbin.org — note httpbin returns 503 to stealth fetches, use example.com for StealthyFetcher smoke tests)
- **More than one install exists per machine, and they upgrade separately.** WSL has the Hermes venv plus `~/.local/bin/scrapling`. Windows has the global Python copy on PATH (`C:\Users\<user>\AppData\Local\Programs\Python\Python311\Scripts\scrapling.exe`) plus the Hermes venv copy under `installs\*\environments\*\venv\Scripts\`. They can sit on different major versions, where the same subcommand name means a different fetcher, so resolve each one (`which -a scrapling`, `where.exe scrapling`) and run `<path> --version` before trusting a command from any note. Upgrade the Windows global install with `& 'C:\Users\<user>\AppData\Local\Programs\Python\Python311\python.exe' -m pip install --upgrade 'scrapling[fetchers]'`, then verify the CLI help, the `dir(scrapling.fetchers)` export list, and one live fetch. Check `pip show certifi` before and after so a dependency bump does not drag the shared certifi pin with it.

## Two Fetchers

### Fetcher — Basic
Use for simple, non-protected targets.
```python
from scrapling.fetchers import Fetcher

f = Fetcher()
page = f.get("https://target-site.com/page")
print(page.status)
print(page.text[:500])
```

### CLI — use this when the Python import is unavailable

The CLI works even when `from scrapling.fetchers import ...` fails with `ModuleNotFoundError` from the default interpreter, which is the common case in agent runs. The `scrapling` binary lives at `~/.local/bin/scrapling` and ships its own working environment. Reach for the CLI rather than installing anything:

```bash
SCRATCH=$(mktemp -d /tmp/hermes-cron-XXXXXX)
scrapling extract get "https://target.com/page" "$SCRATCH/out.txt"
scrapling extract fetch "https://protected.com/page" "$SCRATCH/out2.txt"   # StealthyFetcher (0.5 renamed the subcommand)
```

- Subcommands (0.5): `extract get`, `post`, `put`, `delete`, `fetch`. `fetch` IS the StealthyFetcher, the browser fetch with anti-bot handling. The `stealthy-fetch` subcommand was REMOVED in 0.5 and the `DynamicFetcher` class was removed from the Python API too, so any call naming either one fails.
- **After ANY scrapling version bump, re-read the CLI surface before trusting a note.** Run `scrapling extract --help` and each subcommand's `--help`, then compare against the commands and flags written here and in every other skill that fetches with scrapling (`web-data-extraction`, `scrapling-or-death`, `article-syndication`, `fact-checking-pattern`). 0.5 renamed `stealthy-fetch` to `fetch`, dropped `DynamicFetcher`, and moved `--timeout` to milliseconds on `fetch`, and the old notes kept failing silently until corrected. An upgrade is not complete until those notes match the binary. The full sweep procedure, including which directories count as live and which to leave alone, is in `references/version-upgrade-note-sweep.md`.
- It prints `Fetched (200) <GET url>` and the saved path. Check that line, then read the file.
- Write output into this run's unique `mktemp` dir, never a fixed path, so a later run is not blocked by the stale-overwrite guard.
- Loop several URLs in one shell call to batch a multi-source fetch; the fetches run back to back.
- Check the saved file's size before concluding a fetch failed. A page behind an overlay or behind bot detection can still return its full body to the CLI.
- **The CLI refuses any output filename that does not end in `.md`, `.html`, or `.txt`** (`ValueError: Unknown file type: filename must end with ...`). Save a sitemap or an XML/JSON feed as `sitemap.txt`, never `sitemap.xml`. The content comes back fine either way; only the extension is rejected, so do not read the error as a fetch failure.

### StealthyFetcher — Anti-Bot
Use for Cloudflare, Turnstile, CAPTCHA-protected, or high-detection sites.
```python
from scrapling.fetchers import StealthyFetcher

sf = StealthyFetcher()
page = sf.fetch("https://target-site.com/page", headless=True, network_idle=True)
print(page.status)
print(page.text[:500])
```
Options:
- `headless` — run browser headless (default True)
- `network_idle` — wait until network settles (recommended for JS-rendered content)
- `timeout` — seconds before giving up

## Spider Toolkit (NEW in 0.4.8)

The 0.4.8 release added a full crawling framework with templates, link extraction, and
session management.

### CrawlSpider
Define crawl rules — automatically follows links matching patterns, no boilerplate.

```python
from scrapling.spiders import CrawlSpider
from scrapling.spiders.templates import CrawlRule

class MySpider(CrawlSpider):
    start_urls = ["https://example.com/blog/"]
    rules = [
        CrawlRule(
            link_extractor=dict(allow=r"/blog/\d+"),
            callback="parse_article",
            follow=True,
        ),
        CrawlRule(
            link_extractor=dict(allow=r"/category/\w+"),
            follow=True,
        ),
    ]

    def parse_article(self, response):
        yield {"title": response.css("h1::text").get()}
```

### SitemapSpider
Crawl sites from their sitemap.xml — discovers all URLs automatically.

```python
from scrapling.spiders import SitemapSpider

class MySitemapSpider(SitemapSpider):
    sitemap_urls = ["https://example.com/sitemap.xml"]
    # Optional: filter by patterns
    sitemap_rules = [("/blog/", "parse_blog")]

    def parse_blog(self, response):
        yield {"url": response.url, "h1": response.css("h1::text").get()}
```

### LinkExtractor
Standalone URL extractor from a response with full allow/deny control.

```python
from scrapling.spiders import LinkExtractor

le = LinkExtractor(
    allow=r"/articles/",
    deny=(r"/tag/", r"/author/"),
    restrict_css="article.post",
    deny_extensions=True,
)
links = le.extract_links(response)
for link in links:
    print(link.url, link.text)
```

Parameters: `allow`, `deny`, `allow_domains`, `deny_domains`, `restrict_css`,
`restrict_xpath`, `tags` (default a/area), `attrs` (default href), `canonicalize`,
`keep_fragment`, `deny_extensions`, `process` (callable for custom filtering).

### Running a Spider
```python
from scrapling.spiders import CrawlerEngine

engine = CrawlerEngine(spider=MySpider())
results = engine.run()
for r in results:
    print(r)
```

## CSS Parsing
Both fetchers return an Adaptor object with full CSS selector support:
```python
# Single value
title = page.css("h1::text").get()

# All matches
paragraphs = page.css("div p::text").getall()

# Attribute extraction
links = page.css("nav a::attr(href)").getall()
img_src = page.css("img::attr(src)").get()
```

## Adaptive Parsing (Auto-Heal)
Scrapling's core differentiator — if a CSS selector breaks because the site changed layout, scrapling can auto-recover using structural patterns instead of dying outright:

```python
# Works best with semantic selectors (h1, h2, article) over fragile div class soup
```

**v0.4.8 change:** Adaptive relocation now defaults to a 40% similarity threshold (was 0).
This makes auto-healing much more reliable. If it fails, the error tells you the top
score it found so you can tweak the manual threshold higher/lower. Pass
`adaptive_threshold=0.6` to override (range 0.0–1.0).

## Practical Example (from test script)
```python
from scrapling import __version__
from scrapling.fetchers import Fetcher, StealthyFetcher

print(f"Scrapling v{__version__}")

# Basic fetch
f = Fetcher()
page = f.get("https://httpbin.org/ip")
print(page.status, page.text.strip())

# Stealth fetch
sf = StealthyFetcher()
page2 = sf.fetch("https://httpbin.org/get", headless=True, network_idle=True)
print(page2.status, page2.text[:250])

# Parse
page3 = f.get("https://httpbin.org/html")
h1 = page3.css("h1::text").get()
divs = page3.css("div p::text").getall()
print(f"H1: {h1}, Paragraphs: {len(divs)}")
```

## When to Use
| Scenario | Fetcher |
|----------|---------|
| Public site, no anti-bot | `Fetcher` |
| Cloudflare/Turnstile/CAPTCHA | `StealthyFetcher` |
| Sites with frequent layout changes | `StealthyFetcher` |
| JS-rendered content | `StealthyFetcher` |
| High-stealth competitor tracking | `StealthyFetcher` |

## v0.4.15 — MCP Rework + RAG-Ready Markdown (2026-08-23)

**What's new:**
- **Reworked MCP server** — cleaner tool surface for MCP-driven scraping
- **RAG-ready Markdown in one line** — `Response.markdown()` returns clean Markdown for embedding/retrieval pipelines
- **Improved Cloudflare Turnstile solver** — better success rate on Turnstile-protected pages
- **Browser tabs stay open and get reused across requests** — persistent tab reuse cuts per-request overhead

**Also bumped alongside 0.4.15 (verified 2026-08-28):** Playwright 1.59.0 → 1.62.0, Patchright 1.61.2 → 1.62.1, curl_cffi 0.16.0 → 0.16.2. Refresh browser binaries after upgrading: `python -m playwright install chromium firefox` and `python -m patchright install chromium`.

- **Known non-blocking conflict:** Rotunda's `playwright<=1.59.0` pin now conflicts with the 1.62.0 that Scrapling 0.4.15 requires. This is a soft pin — Rotunda's core imports and direct-binary launch both work fine under 1.62.0 (verified 2026-09-25 at rotunda 0.5.1). Do not downgrade Playwright to satisfy it; re-pin 1.62.0 after any Rotunda install.

## v0.4.9 — Maintenance Update (2026-06-07)

**What changed:**
- **Updated all browsers and fingerprints** — run `scrapling install --force` after updating to refresh them
- **Added `--version` flag** to the CLI
- **Bug fixes:** proxy argument no longer silently ignored in HTTP sessions; browser navigations with `init_script` + `user_data_dir` now work; encoding detection fixed for quoted charset values; adaptive relocation `IndexError` with `auto_save` fixed; spider checkpoint/cache saving fixed on Windows; `find_similar` scoring fixed for mismatched attribute counts

## v0.4.11 — ShopifySpider + Faster Parsing (2026-07-12)

**What's new:**
- **`ShopifySpider`** — first platform spider template. Extract every product from any Shopify-powered store through its JSON API without touching the website's HTML:
  ```python
  from scrapling.spiders import ShopifySpider

  class MyStore(ShopifySpider):
      target_website = "example.com"

  result = MyStore().start()
  ```
- **`--executable-path` on CLI fetch commands** — accept a custom Chromium-compatible browser executable, with `SCRAPLING_EXECUTABLE_PATH` env var fallback (parity with MCP server). Historical 0.4.x entry: an earlier release listed two browser-fetch subcommands; only `extract fetch` exists in 0.5
- **`find_by_text` and `find_by_regex` up to ~2x faster** when `first_match=True` (default) — wraps elements lazily so search stops at first match

**Bug fixes:**
- Fixed MCP server fetch tools crashing on pages containing XML-incompatible control characters

## v0.4.10 — Scrapy Integration + Bug Fixes (2026-07-04)

**What's new:**
- **Scrapy integration** — use Scrapling's parsing API inside existing Scrapy projects. Decorate any spider callback with `@scrapling_response` and the response becomes a Scrapling `Response` while Scrapy handles crawling:
  ```python
  import scrapy
  from scrapling.integrations.scrapy import scrapling_response

  class QuotesSpider(scrapy.Spider):
      name = "quotes"
      start_urls = ["https://quotes.toscrape.com"]

      @scrapling_response
      def parse(self, response):
          first_quote = response.find_by_text("The world as we have created it", partial=True)
          for quote in [first_quote, *first_quote.find_similar()]:
              yield {"text": quote.get_all_text(strip=True)}
  ```
- **MCP server** now accepts `--executable-path` or `SCRAPLING_EXECUTABLE_PATH` env var for custom Chromium-compatible browser
- **Updated all browsers and fingerprints** — run `scrapling install --force` after updating

**Bug fixes:**
- Fixed garbled text (mojibake) from browser fetchers on non-UTF-8 websites
- Fixed `LinkExtractor` not filtering compound file extensions like `.tar.gz`
- Fixed paused crawls losing in-flight requests from checkpoints on resume
- Fixed spiders calculating wrong crawl delays from robots.txt `Request-rate` directives

## WordPress Post-ID Bypass (Adblocker-Blocked Sites)

When a WordPress site (like TechCrunch) blocks automated browsers with adblocker-detection overlays or truncates article slugs with `...` in search results, bypass via the post ID:

1. **Find the post ID** from search results: `grep -oP 'post-[0-9]+'` from the search page HTML
2. **Access directly**: `curl -sL "https://site.com/?p=3140971"` — this uses WordPress's core routing primitive, often skipping the adblocker-detection hook
3. **Extract content**: `grep -oP '<p[^>]*>.*?</p>'` for article text

See `references/wordpress-adblocker-bypass.md` for the full technique.

## Pitfalls
- `StealthyFetcher` requires Playwright browser installed: `playwright install chromium`
- If `headless=False` and it still fails, Cloudflare may require full browser mode
- Adaptive parsing works best with semantic HTML (h1, article, section) not div-heavy class soup
- `network_idle=True` adds latency — only use when page is JS-rendered
- Status 403/429 means detected — try `StealthyFetcher` with longer timeout
- Some sites block all automation — fallback is Rotunda browser (see complementary skill)
- **After upgrading, refresh browser binaries:** `scrapling install --force` tries to run `playwright install-deps` which requires sudo and fails in WSL. Instead, just run `playwright install chromium` — that updates the browser binary without needing root.
- **Both agents now run from PM-managed environments, not inline venvs (verified 2026-09-25).** Each install holds a versioned Python generation under `installs/<key>/environments/<hash>/venv`. The hash changes on rebuild, so NEVER hardcode it; resolve the live interpreter first. WSL: `python3 -c "import json,glob;print(json.load(open(sorted(glob.glob('~/installs/*/facts.json'))[-1]))['packages']['venv']['environment'])"` then append `/bin/python`. Windows, from WSL: run the same one-liner against the glob `/mnt/c/Users/<user>/AppData/Local/hermes/installs/*/facts.json` and append `\Scripts\python.exe`. `hermes doctor` prints the active environment on either side ("Runtime venv staged (...) (active in this process)"). Install with `uv pip install --upgrade "scrapling[fetchers]" --python <resolved interpreter>`.
- **These paths are DEAD, do not use them.** WSL `~/.hermes/hermes-agent/venv/` is a legacy leftover that still exists but is not what the running agent imports; Windows `C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\` does not exist at all, its venv was quarantined to `backups/legacy-venv-cp311-quarantine-20260924/` on 2026-09-24. Installing into either one changes nothing for the live agent.
- **Verify imports from a neutral cwd.** A directory named `rotunda` in the current working directory becomes a namespace package and shadows the real one. Run any import check from `/tmp`, not from `~`.
- **`StealthyFetcher.afetch()` removed in v0.4.11** — the async `afetch()` method was dropped. Use sync `sf.fetch()` instead. If you need async, wrap it in `asyncio.to_thread()`.
- **`StealthyFetcher` import crash on Chrome 149 hardcode (v0.4.12) — CRITICAL (2026-08-08):** scrapling 0.4.12 hardcodes `chrome_version = 149` / `chromium_version = 149` in `scrapling/engines/toolbelt/fingerprints.py`. This makes `from scrapling.fetchers import StealthyFetcher` raise `ValueError: No headers based on this input can be generated` at import time IF `apify-fingerprint-datapoints` is < 0.15.0 (0.14.0 data only has Chrome up to 141; 0.15.0 adds Chrome 149). **Fix:** `pip install apify-fingerprint-datapoints==0.15.0` (or newer) in EACH live environment (WSL and Windows; resolve each interpreter from `installs/*/facts.json`). Do this on any fresh install or after a scrapling upgrade. Verify: `python -c "from scrapling.fetchers import StealthyFetcher; print('OK')"`. After fixing the import, `StealthyFetcher` will also need the patchright chromium browser: `python -m patchright install chromium` (scrapling 0.4.12+ uses patchright, NOT stock playwright). Smoke test: `sf.fetch('https://example.com', headless=True)` → 200. NOTE: httpbin.org returns 503 to stealth fetches — use example.com for smoke tests.
- **v0.4.13/0.4.14 (2026-08-10/14):** 0.4.13 added XMLFeedSpider/CSVFeedSpider, MCP SDK v2, unpinned Playwright/Patchright (browser UA now matches installed Chromium version), and fixed the browserforge ValueError. 0.4.14 is a maintenance fix for `uv` refusing 0.4.13 (prerelease curl_cffi dep). **After upgrading to 0.4.13+:** reinstall patchright chromium (`python -m patchright install chromium`) AND stock playwright browsers (`python -m playwright install chromium firefox`) since Playwright bumps to 1.62.0. **Playwright 1.62.0 note:** Rotunda's `NewBrowser`/`NewContext` API hits the `viewport.isMobile` Juggler quirk under 1.62 — use the direct-binary method (`p.firefox.launch(executable_path=ROTUNDA_BIN)` + `no_viewport=True`) instead. Scrapling's own StealthyFetcher is unaffected.
- **Rotunda's `playwright<=1.59.0` pin vs Scrapling's `playwright>=1.62.0`** — a genuine conflict (verified live 2026-09-25 at rotunda 0.5.1 / scrapling 0.4.15), but the pin is SOFT. Installing Rotunda pulls Playwright down to 1.59.0 and breaks Scrapling's `fetchers` extra, so re-pin `playwright==1.62.0` after any Rotunda install. Never downgrade Playwright to satisfy Rotunda. Note the API consequence: `NewBrowser`/`NewContext` import but `NewContext()` fails under 1.62.0 with the `viewport.isMobile` Juggler error — use the direct-binary method.
- **Raw HTML data extraction (individual product pages):** Some sites (e.g. a single Gumroad product page) embed full JSON product data in raw HTML with escaped quotes (`\\u0026quot;`). A `curl` fetch yields it. See `references/html-escaped-json-extraction.md` for the proven pattern.
- **Storefront and marketplace ROOTS are a JS shell; escalate to a real browser render.** A Gumroad profile or storefront root returns only its display name (roughly 16 bytes) to BOTH `scrapling extract get` and `scrapling extract fetch`, and `curl` returns a 28KB HTML shell with no product JSON and no product names. Rendering it works: open the URL in the browser tool, wait a few seconds, then read `document.body.innerText`, which gives the full product list with names and prices. Rule of thumb: when the CLI-saved file comes back containing only a name or a shell, stop fetching harder and go straight to the browser render, extract `innerText`, then parse from that.
- **TechCrunch: try the direct CLI fetch first.** `scrapling extract get` on the article URL returns the full body even though the adblocker-detection overlay blocks browser-based access and despite this skill's earlier note. Only if the saved file comes back small or empty, fall back to the WordPress post-ID route: search the site, extract the numeric post ID from the CSS class (`post-<id>`), then fetch `?p=<id>`. See `references/wordpress-adblocker-bypass.md`.

## Pair with Rotunda Browser
Scrapling + Rotunda form a **tiered scraping stack**:
1. **Try Scrapling first** — `StealthyFetcher` handles 90%+ of Cloudflare/Turnstile targets with minimal overhead.
2. **Fallback to Rotunda** — when Scrapling gets 403/429/CAPTCHA, Rotunda's Firefox-Juggler pipeline evades detection that Playwright-based automation can't. Use Rotunda's Python API (`NewBrowser`/`NewContext`) for the browsing session, then pipe HTML back into Scrapling's `Adaptor` parser if you need its adaptive CSS selectors.
3. **Together** — Rotunda handles the browser session (fingerprint-evading navigation, humanized input, CAPTCHA solving), Scrapling handles data extraction and crawling logic (CSS selectors, link extraction, spider framework). Combine both when a site is both protected AND has complex/nested page structures.

## Known-blocking sites (skip entirely, do NOT attempt with any tool)
- google.com (CAPTCHA)
- bing.com (CAPTCHA/Cloudflare)
- duckduckgo.com (CAPTCHA)
- reddit.com (CAPTCHA/block)

If a task needs data from one of these, tell Vinny it's blocked and suggest an alternative source. See the `scrapling-or-death` behavioral skill — scrapling is the DEFAULT web-fetch tool for ALL content, not a fallback.