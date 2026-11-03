---
name: web-data-extraction
description: Techniques for extracting structured data (tables, benchmarks, leaderboards, article bodies) from web pages. Covers console-based JS extraction, curl-to-file + Python extraction, browser snapshot extraction, and API-based approaches. Use when you need to pull data from a page that browser_snapshot truncates, curl misses due to JS rendering, or where the data is in a structured table format.
trigger: "need to extract a table, benchmark, leaderboard, or structured data from a web page; browser_snapshot(full=true) is too large; curl returns nav-heavy content; page is JS-rendered"
---

# Web Data Extraction, Techniques for Structured Content

## When to use this skill

- You need to extract a table, benchmark, leaderboard, or structured data from a web page
- `browser_snapshot(full=true)` returns truncated output (too many elements)
- curl-to-file + Python extraction returns nav-heavy boilerplate with the data buried
- The page is JS-rendered (SPA, dynamic content loaded via XHR)
- You need the full dataset, not just a summary
- You are verifying claims against cited URLs (fact-check work) and need the cheapest path to the body text

### Confirm the block is real before escalating

Most article pages are not gated. A plain HTTP fetch (scrapling `Fetcher().get(url)`) returns the full body for TechCrunch, The Verge, Axios, The Next Web, KPBS, Yahoo News, and vendor newsrooms such as the NVIDIA blog, all verified on first attempt. Adblocker overlays and bot walls hit *browser navigations*, which are a different path, so a failed browser attempt is not evidence the page is blocked. Escalate in this order: plain HTTP fetch → alternate URL form (`?p=<id>` WordPress post-ID, `www.` prefix, trailing slash, sitemap-canonical URL) → stealth fetcher → archives → browser. Starting at the browser costs minutes on pages step 1 answers in a second.

Note that `get_all_text(strip=True)` on nav-heavy sites returns 3-10 KB of menus, newsletter prompts, and related-link rails before the prose. Use it to confirm the page exists and to grep for the specific number or quote you are verifying; do not treat it as clean copy.

## Scrapling CLI: one-shot fetch without writing Python

The `scrapling extract` subcommands fetch a URL and write it straight to a file. For a single page this is faster than importing the API, and it is the concrete form of the scrapling-first rule.

```bash
# The output format is chosen by the file EXTENSION, and only three are accepted:
#   .html   .md   .txt
scrapling extract get            URL OUT.txt   # plain HTTP
scrapling extract fetch          URL OUT.txt   # StealthyFetcher (browser, anti-bot)
scrapling extract post           URL OUT.txt   # also: put, delete
```
Scrapling 0.5 removed the old stealth-fetch subcommand entirely; calling it now exits with `No such command`. `fetch` is the stealth browser fetch now, so use `fetch` anywhere an older note names a separate stealth command.

`get` accepts `--timeout` (seconds), `-s/--css-selector` (return only matching nodes), `-H "Key: Value"` (repeatable), `--cookies`, `--proxy`, `--impersonate chrome,firefox`, and `--ai-targeted` (main content only, hidden elements stripped). `fetch` accepts `--timeout` (MILLISECONDS), `-s/--css-selector`, `-H/--extra-headers`, `--proxy`, `--headless`, `--network-idle`, `--wait`, `--solve-cloudflare`, `--executable-path`, and `--ai-targeted`, but NOT `--cookies` or `--impersonate`; passing those to `fetch` aborts with an option error. Scrapling 0.5 also removed the `DynamicFetcher` class, so `from scrapling.fetchers import DynamicFetcher` raises ImportError; the module now exports `Fetcher`, `FetcherSession`, `AsyncFetcher`, `StealthyFetcher`, `StealthySession`, `AsyncStealthySession`.

**Prefer `.txt` over `.md` for the output file.** The `.md` path routes through `markdownify` in `scrapling/core/shell.py`; when that module is absent the command completes the HTTP request successfully and only then dies at write time with `ModuleNotFoundError: No module named 'markdownify'`, leaving a 0-byte file. `.txt` returns the rendered text content and needs nothing extra, so a `.md` failure wastes a page fetch that already succeeded.

**The extension is mandatory.** Omitting it, or passing any other extension such as `.xml`, fails before the request with `ValueError: Unknown file type: filename must end with '.md', '.html', or '.txt'`. To read an XML or JSON endpoint (sitemap, RSS, arXiv API query), save it as `.txt` and grep the raw text.

**A failed write still logs `INFO: Fetched (200)`.** The log line reports the HTTP layer, not the file. Confirm the output is non-empty (`ls -la OUT.txt` or `wc -c`) before parsing it.

## Measuring a delivered document's parts (length targets, char caps)

When a deliverable has a length target or a per-field character cap (article body against a word range, social post against a platform cap, SEO title against a 60-80 char window), measure each part against its own boundary, not the whole file. One `wc -w` on the file counts the title, byline, body, sources list, and social block together, so a piece that is correctly sized reads as over budget and gets cut for no reason.

Isolate a section by its heading line and count only that:

```bash
# Body word count: everything above the SOURCES heading
awk '/^SOURCES$/{exit} {print}' FILE.txt | wc -w

# Character count of a titled block (X post, SEO title, meta description)
awk '/^X POST$/{f=1;next} /^PINTEREST TITLE$/{f=0} f&&NF' FILE.txt | tr -d '\n' | wc -c
```

Strip newlines with `tr -d '\n'` before counting characters, otherwise each line's terminator inflates the total and a post one char under the cap measures as over it. Report the measured number, and when a target is a RANGE (60-80 chars), landing under the floor is a miss just like going over the ceiling.

## Technique 1: Console-Based Table Extraction (preferred for JS-rendered tables)

Use `browser_console` with a JS expression targeting the main content area. This runs in the page context after full JS execution and returns the rendered DOM as text.

### Pattern

```javascript
// Best: target the main content element directly
document.querySelector('main')?.innerText

// Fallback: entire body
document.body.innerText

// For pages with a specific table container
document.querySelector('.benchmark-table')?.innerText

// For pages where the table is inside an article
document.querySelector('article')?.innerText
```

### Why this works

- Runs in the page context after full JS execution, sees the rendered DOM, not raw HTML
- Returns the result as a string directly in the tool output, not truncated like snapshot
- Bypasses nav/header/footer noise that curl extraction struggles with
- Faster than `browser_snapshot(full=true)` for large pages

### Real example: Wolfram LLM Benchmark (200+ model table)

The Wolfram benchmark page at `https://www.wolfram.com/llm-benchmarking-project/` contains a table of 200+ models. The page is nav-heavy and the table is deep in the DOM.

**Working extraction:**
```javascript
document.querySelector('main')?.innerText || document.body.innerText
```

This returned the full sorted table (200+ rows) as clean text, including the header description, the table data, and the footer links, all in one string.

**What didn't work:**
- `browser_snapshot(full=true)`, returned a truncated snapshot (3000+ lines, cut off)
- curl-to-file + Python extraction, returned nav-heavy text where the table was buried under 5000+ chars of navigation boilerplate

### When NOT to use

- Pages where the table is paginated or loaded on scroll (use multiple console calls or scroll-then-extract)
- Pages where the table is inside an iframe (need to switch context first)
- Pages where the data is in a `<canvas>` or SVG (not accessible as text)

## Technique 2: curl-to-file + Python Extraction (for static HTML pages)

Use when the page is not JS-rendered but the browser stack times out (paywalls, heavy ad infrastructure).

### Pattern

```python
from hermes_tools import terminal

# Download all articles in parallel
urls = [
    ("/tmp/article1.html", "https://..."),
    ("/tmp/article2.html", "https://..."),
]
for path, url in urls:
    terminal(f"curl -sL --max-time 15 '{url}' -o {path}")

# Then extract each one
import re, html as h
for path in ["/tmp/article1.html", "/tmp/article2.html"]:
    with open(path) as f:
        data = f.read()
    data = re.sub(r'<script[^>]*>.*?</script>', ' ', data, flags=re.DOTALL)
    data = re.sub(r'<style[^>]*>.*?</style>', ' ', data, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', data)
    text = h.unescape(text)
    text = re.sub(r'\\s+', ' ', text).strip()
    print(text[:3000])
```

### Pitfalls

- Some sites return a "Please enable JS" page (Reuters, WSJ), these need the browser stack
- Twitter/X pages return minimal content via curl, use browser_navigate for social media
- Check for "Page Not Found", "404", "That page does not exist" in the first 500 chars, the URL may be stale

## Technique 3: browser_snapshot(full=true) (for text-heavy pages)

Use when the page is text-heavy and not too large. Good for article bodies, documentation, and blog posts.

### Pattern

```python
browser_navigate(url)
snapshot = browser_snapshot(full=true)
# The snapshot is returned as text; if truncated, a file path is provided
# Read the file with read_file() to get the full content
```

### Pitfalls

- Pages with 3000+ elements get truncated, switch to Technique 1 or 2
- Paywalled pages may show only the lede, switch to Technique 2

## Technique 4: Firecrawl (when available as MCP tool)

When firecrawl is available (check tool_search or tool_describe for `mcp__firecrawl__firecrawl_*` before assuming it is absent), prefer it over scrapling/browser for scraping individual URLs and for search-based discovery.

### Why firecrawl first (when present)
- `firecrawl_search` returns ranked web results AND can attach scrapeOptions to fetch page content in the same call, discovery and extraction in one step.
- `firecrawl_scrape` handles JS-rendered pages, returns markdown/HTML/links/screenshot, and has proxy options (basic/stealth/enhanced/auto) for bot-walled sites.
- `firecrawl_parse` handles document formats (PDF, Word, RTF, spreadsheets) that scrapling/browser cannot.

### Order of tool preference when firecrawl is present
1. `firecrawl_search`, for discovery queries (find pages, news, trending topics)
2. `firecrawl_scrape`, for fetching a known URL's content
3. scrapling `Fetcher`, for plain HTTP fetches when firecrawl is not needed
4. browser, last resort for JS-heavy / interactive / login-gated pages

### Pitfall: do not claim a tool is unavailable without checking
Before telling the user a tool is unavailable, or deciding not to use it, verify it exists. Run `tool_search` or `tool_describe` for the tool name. Claiming "no tool called X" when X is in the deferred tool catalog is a credibility failure, the tool was there, you just did not look. The deferred tool catalog (45 tools) is loaded at session start; check it before defaulting to the always-available tools.

## Decision Tree

```
Does the source have an RSS/Atom feed?
  ├── Yes → Is this breaking news (last hour)?
  │         ├── Yes → Use browser first. RSS has 15-60min refresh lag.
  │         └── No  → Fetch the feed via curl. RSS is structured, no bot blocking, one call per source.
  │                   Parse XML/JSON for headlines, dates, links, descriptions.
  │                   Only fall back to browser if you need full article body text.
  └── No  → Is the data in a structured table/benchmark/leaderboard?
            ├── Yes → Is the page JS-rendered?
            │         ├── Yes → Technique 1 (console-based)
            │         └── No  → Technique 1 or 2 (whichever is faster)
            └── No  → Is the page text-heavy (article, blog post)?
                      ├── Yes → Technique 3 (browser_snapshot)
                      └── No  → Technique 2 (curl + Python)
```

## Official statistics: download the bulk file, do not scrape the release page

Agency news releases (BEA, BLS, Census, EIA) carry only the highlights the agency chose
to name; the full table is always published separately as a zipped CSV or xlsx. Fetch
the release page as **HTML** and grep its raw `href` list for `zip|xlsx|csv` to find the
bulk file, then take the single `*__ALL_AREAS__*.csv` member rather than per-region files.

**Validate the geographic key before sorting anything.** Geo tables interleave states,
the US total, and large multi-state regions in one file. Sorting BEA state GDP on value
alone puts the *Southeast region* at #1 ahead of California, with Far West and Mideast
next. Filter to the 51 valid state FIPS codes (50 states + DC) first, on `LineCode == 1`
only, then sort. A filtered state list must count 51 rows.

**Name the basis in the answer.** Nominal (current dollars) and real (chained dollars)
rank the tail of the list differently, and adjacent ranks can sit within a rounding error
of each other, so check whether the ordering holds in the newest quarter before presenting
a top ten as settled.

Full recipe, BEA table/zip map, CSV column shape, and the FIPS filter:
`references/official-statistics-data-files.md`.

## Linked Reference Files

- `references/official-statistics-data-files.md`, Bulk data files from government statistical agencies (BEA, BLS, Census, EIA): locating the zip from a release page, BEA regional GDP table map, CSV column shape, the state-FIPS filter that keeps region rows out of a ranking, and reporting nominal vs real. Use when a question needs official numbers rather than a news summary.
- `references/domain-email-recon.md`, Trace an email address or domain back to its owner. Covers SSL-fallback curl, browser-console email extraction, DNS resolution, and cross-referencing aliases against site footers. Use when investigating who owns a domain or who's behind an email address.

## Technique 7: Next.js / React Server-Component catalogs, parse the flight payload, not the DOM

Some JS-heavy catalog and directory sites (model hubs, marketplaces, docs indexes) render EVERYTHING client-side from a JSON payload embedded in the HTML. On these pages `get_all_text()` returns only nav, footer, and filter labels, no rows, and `page.text` may be empty while the real data sits in the HTML as React flight chunks.

### Diagnose first

Grep the fetched HTML for the marker before choosing a technique:

- `__NEXT_DATA__` present → plain `json.loads` of that script tag; done.
- `self.__next_f.push` present → React Server Components. The data is escaped JSON inside numbered push calls. Parse the flight payload (below); CSS selectors and `get_all_text` will not reach it.

### Extract the payload

```python
import re, json

h = page.html_content or decode(page)   # see Technique 6 for the byte-decode fallback
chunks = re.findall(r'<script>self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', h, re.S)
blob = "".join(chunks).encode().decode("unicode_escape")

# Then bracket-match the array you want out of the blob
i = blob.find('"resources":[')
seg = blob[i + len('"resources":'):]
depth = 0
for j, c in enumerate(seg):
    if c == "[":
        depth += 1
    elif c == "]":
        depth -= 1
        if depth == 0:
            rows = json.loads(seg[:j + 1])
            break
```

`scripts/nextjs-flight-extract.py` is a re-runnable version of this that takes a URL and an array key and prints the parsed rows.

### Pitfalls

- Concatenate ALL push chunks before decoding. Chunks split mid-JSON-string, so parsing one chunk alone fails; the escaped text only becomes valid JSON after the join plus `unicode_escape` decode.
- Search the decoded blob for `"<field>":[` and bracket-match to the close. Do not regex for `\{.*?\}`: nested objects terminate the match early and silently drop rows.
- Rows are often more than the visible list, read `"resultTotal"` and `"resultPageTotal"` from the blob and compare against what you parsed. A mismatch means you read one page of a paginated payload, not the whole catalog.
- **Filter URLs that the site's own UI produces may be ignored server-side.** A `?filters=<field>:<value>` query parameter can return either 0 results or the unfiltered full total, because the filtering happens in client code after hydration. When the count looks wrong in either direction, stop varying the filter syntax: enumerate `?page=1..N` and filter the parsed rows yourself. This also makes the result independent of the site's filter naming.

### Report counts from the enumeration

When the deliverable is a list, state the totals you actually enumerated (total rows found, rows matching the label). A count scraped from the site's filter sidebar is a UI claim, not a verified number.

## Technique 5: arXiv Abstract Extraction via Curl (Cron-Optimized)

arXiv abstract pages are static HTML that curl extracts cleanly, no browser needed. This is the fastest and most reliable approach for academic paper extraction, especially in cron sessions where browser_navigate is slow and delegate_task may not complete.

### Pattern

```bash
curl -sL --max-time 20 'https://arxiv.org/abs/2607.18246' -o /tmp/arxiv.html
```

Then extract the abstract from the cleaned HTML:

```python
import re, html as h
with open('/tmp/arxiv.html') as f:
    data = f.read()
data = re.sub(r'<script[^>]*>.*?</script>', ' ', data, flags=re.DOTALL)
data = re.sub(r'<style[^>]*>.*?</style>', ' ', data, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', ' ', data)
text = h.unescape(text)
text = re.sub(r'\s+', ' ', text).strip()
# Find abstract, reliably within first 2000 chars after "Abstract" marker
idx = text.find('Abstract')
if idx > 0:
    abstract = text[idx:idx+2000]
    print(abstract)
```

### Performance

- 10 arXiv papers: ~3 seconds total (parallel curl downloads) + ~0.3 seconds extraction
- 20 arXiv papers: ~6 seconds total
- Zero failures on static HTML pages (verified on 10 papers, July 23, 2026)

### When to use

- Cron sessions (always, faster and more reliable than browser_navigate)
- Interactive sessions with 5+ papers to extract
- Any arXiv abstract extraction, the static HTML is trivial to parse

### When NOT to use

- Papers behind paywalls or requiring JS (arXiv never requires JS for abstracts)
- Papers where you need the full PDF text (use the PDF URL instead)

### Find a paper by title or keyword: use the API, not the search page

Scraping an arXiv search results page gives you truncated abstracts, an unstable layout, and a "More" link that the browser tools choke on. The export API returns the full abstract, the canonical ID, the authors, and the submission date in one request:

```bash
scrapling extract get "http://export.arxiv.org/api/query?search_query=all:%22EXACT+TITLE+PHRASE%22&max_results=10" out.txt --timeout 25
```

URL-encode the phrase and wrap it in `%22` quotes for an exact match. The response is Atom XML; grep it for `<id>`, `<title>`, `<published>`, and the abstract body. This is also the cheapest way to answer the two questions a fact-check actually asks: does this paper exist under this name, and does the abstract support the claim the outline made about it. Cross-check the returned ID against the URL the outline or data file cited; a mismatch means the outline's attribution is wrong and should be corrected before publishing.

## Batch verification fetches: one script call, write to files, grep for the claims

When a task requires verifying N cited URLs (fact-checking an article, checking a source list), do NOT fetch them one per tool call and do NOT print the pages into context. One script call fetches every URL and writes each page to a file; the numbers are read back with `search_files` or `grep -n`.

```python
import os
from scrapling.fetchers import Fetcher

out = os.path.join(os.environ.get("SCRATCH", "/tmp"), "out")
os.makedirs(out, exist_ok=True)
f = Fetcher()
for key, url in targets.items():
    try:
        p = f.get(url, timeout=45)
        open(f"{out}/{key}.txt", "w").write(p.get_all_text(strip=True))
        print(key, p.status, len(p.get_all_text(strip=True)))
    except Exception as e:
        print(key, "FAIL", type(e).__name__, str(e)[:150])
```

Then `grep -n -i "<number or phrase>" $SCRATCH/out/*.txt`. This keeps context small, lets a claim be re-checked without re-fetching, and means a retry hits only the URL that failed rather than the whole list. It also leaves room in the turn's tool-call budget for the actual deliverable, which is the usual thing to get cut when research sprawls.

Plain `Fetcher` is sufficient for Hugging Face blog posts, TechCrunch, ZDNet, and InfoWorld; escalate to `StealthyFetcher` only for a URL that actually fails.

## Technique 6: Scrapling `page.text` Empty → Use `page.html_content` (Cron-Safe)

When scrapling's `Fetcher` returns `page.text` empty (length 0) even on HTTP 200, the rendered text extraction failed. Two reliable fallbacks:

**1. `page.html_content` (cron-safe, first choice):** holds the raw HTML and is usually populated, regex-extract the `<p>` tags:

```python
import re
# page = Fetcher().get(url)  # status 200 but page.text == ''
html = page.html_content  # usually populated
paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, flags=re.DOTALL)
text = ' '.join(re.sub(r'<[^>]+>', '', p) for p in paragraphs)
```

**2. `page.body` byte-decode (most robust, verified on phantom-byte.com properties 2026-08-29):** if `.html_content` is also not populated (or you need `re.findall` over the whole doc, e.g. counting article links in an `/href="[^"]+\.html"/` scan), decode `.body` bytes manually with an encoding fallback loop:

```python
def decode(p):
    b = p.body
    if isinstance(b, bytes):
        for enc in ('utf-8', 'utf-8-sig', 'latin-1'):
            try:
                return b.decode(enc)
            except Exception:
                pass
    return str(b)

txt = decode(p)   # use txt everywhere, e.g. re.findall(r'href="([^"]+\.html)"', txt)
links = re.findall(r'''href=["']([^"']+\.html)["']''', txt)
print("unique article pages:", len(set(links)))
```

Do NOT treat `len(page.text) == 0` as "the site returned nothing." On static HTML sites (phantom-byte.com and similar clean HTML) the body is fully present; only scrapling's internal encoding detection failed. `status == 200` plus a non-empty `.body` means the page loaded fine.

## Sitemap-first URL resolution for PhantomByte properties (and any static site)

Slugs guessed from a headline are usually wrong: titles drop words, so `"Your Data Center Is a Control Problem, Not a Generation Problem"` lives at `data-center-control-problem-not-generation-problem`. Never construct the slug from the title. Pull `/sitemap.xml` once, then grep it for a keyword from the title:

```python
p = Fetcher().get("https://articles.phantom-byte.com/sitemap.xml").get_all_text(strip=True)
import re
for m in re.finditer(r'https://articles\.phantom-byte\.com/[a-z0-9\-]+', p):
    if "control" in m.group(0):
        print(m.group(0))
```

**Sitemap entries are extensionless; the fetchable URL needs `.html`.** Entries appear as `https://articles.phantom-byte.com/<slug>` and requesting that form returns 404. Append `.html` and it returns 200 with the full article. Same pattern applies to any static site whose sitemap omits the file extension, when an extensionless sitemap URL 404s, try it with the page extension before escalating to the browser.

## Recovering URLs when a source list has none

Some aggregator dumps carry only `Source: <publication>` and no URL (IronPulse is the common case: `search_files` for `http` across a whole dump returns nothing). That is not an unverifiable claim, it is a missing link. Recover it with a `web_search` on the publication name plus the exact headline, then fetch the top hit. The headline is verbatim so retrieval is near-certain, and this is far cheaper than an open-ended topic search.

A **guessed slug** is the same class of problem, and the failure looks identical to a block: the request returns 200 with a few KB of navigation and no article body, so the page looks gated when only the URL was wrong. Diagnose it by checking whether the extract is nav-only (menu items, related links, no prose). If it is, the URL is wrong, not the site. Run one `web_search` for the exact headline plus the outlet, fetch the canonical URL it returns, and cite that. Search results also carry aggregator reprints of an outlet's story under a different domain; fetch and cite the outlet's own domain instead.

Sitemaps are also the right fallback when you need a canonical URL for a site whose HTML surface is gated: `/sitemap.xml` is almost never behind the WAF that protects article pages.

### Search engines
- **lite.duckduckgo.com/lite/?q=...**, works with a plain `Fetcher` (~4.7KB, clean). Parse directly.
- **search.brave.com/search?q=...**, returns ~200KB that is mostly CSS/JS. Run full `html_content` extraction plus a tag-strip fallback.

### Locating one row in a leaderboard
Loop with `find()` and print a window around the keyword:
```python
idx = text.find('keyword')
while idx != -1:
    print(text[idx:idx+500])
    idx = text.find('keyword', idx+500)
```
If a row genuinely isn't present, say so, do NOT fabricate it.

## Performance

| Technique | Setup time | Extraction time | Best for |
|-----------|-----------|----------------|----------|
| Console-based (T1) | 1-2s (page load) | Instant | JS-rendered tables, large datasets |
| curl + Python (T2) | 5-10s (parallel downloads) | 0.5s | Static HTML, paywalled sites |
| browser_snapshot (T3) | 1-2s (page load) | Instant | Text-heavy pages, articles |
| API (T4) | 0s | Instant | When available |
| arXiv curl (T5) | 0.3s per paper | Instant | arXiv abstracts, cron sessions |
