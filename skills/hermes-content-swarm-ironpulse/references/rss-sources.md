# IronPulse — RSS Sources, Extraction, and Fallbacks

Loaded on demand by the ironpulse SKILL.md when a feed needs to be located, parsed, or replaced by a browser fallback.

## RSS Feed Sources (Primary — Use First)

**HARD RULE: RSS feeds are the PRIMARY data source. Browser scraping is the LAST resort.**

Every major AI news source publishes RSS/Atom feeds. These are structured, machine-parseable, and don't get blocked:

| Source | RSS Feed URL | Notes |
|--------|-------------|-------|
| TechCrunch AI | `https://techcrunch.com/category/artificial-intelligence/feed/` | Reliable, fresh stories with timestamps |
| The Verge AI | `https://www.theverge.com/rss/ai-artificial-intelligence/index.xml` | Fresh stories, structured data. The old `/ai-artificial-intelligence/rss.xml` path 404s. |
| WIRED AI | `https://www.wired.com/feed/tag/ai/latest/rss` | Good for investigative/policy stories |
| Ars Technica AI | `https://arstechnica.com/ai/feed/` | Engineering-focused AI coverage |
| MIT Tech Review | `https://www.technologyreview.com/feed/` | Academic/research AI stories |
| Hacker News | `https://hnrss.org/frontpage?count=30` | AI/ML trending stories from HN |
| Google News AI | `https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en` | Widest diversity, catches stories across outlets |
| Fox News AI | `https://moxie.foxnews.com/feedburner/artificial-intelligence.xml` | MSM perspective |
| BBC Technology | `https://feeds.bbci.co.uk/news/technology/rss.xml` | MSM, filter for AI stories |
| Scientific American | `https://www.scientificamerican.com/artificial-intelligence/rss/` | Academic/research AI |

**Extraction technique (single curl per source):**
```bash
# Fetch RSS feed — one call gets you 20+ headlines, timestamps, and links
curl -sL "https://techcrunch.com/category/artificial-intelligence/feed/" | grep -oP '<title>[^<]*</title>' | sed 's/<[^>]*>//g' | head -20

# Get publish dates
curl -sL "https://techcrunch.com/category/artificial-intelligence/feed/" | grep -oP '<pubDate>[^<]*</pubDate>' | sed 's/<[^>]*>//g' | head -20

# Get article links
curl -sL "https://techcrunch.com/category/artificial-intelligence/feed/" | grep -oP '<link>[^<]*</link>' | sed 's/<[^>]*>//g' | head -20
```

For JSON feeds (some sources use JSON Feed format):
```bash
curl -sL "https://example.com/feed.json" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(i['title'], i['url'], i.get('date_published','')) for i in d.get('items',[])]"
```

**When to fall back to browser:**
- A source has no RSS feed (rare — nearly every major site does)
- The RSS feed returns empty or stale data
- You need full article body text for a specific story (RSS gives headlines + descriptions, not full text)
- The feed is blocked (also rare — RSS readers don't trigger bot detection)

## Browser Fallback Sources (Last Resort)

Only use these when RSS feeds fail for a specific source:
- TechCrunch AI section: https://techcrunch.com/category/artificial-intelligence/ — reliably has stories from last 24h (shows relative times like "17 hours ago")
- The Verge AI: https://www.theverge.com/ai-artificial-intelligence — excellent for very fresh stories (minutes/hours old); timestamps show as "MAY 3", "25 MINUTES AGO", etc.
- Google News AI: https://news.google.com/search?q=artificial+intelligence — **best source for diverse within-24-hour stories** from many outlets in one view. Shows relative timestamps ("1 hour ago", "24 minutes ago", "8 hours ago") and source attribution.
- Fox News Tech: https://www.foxnews.com/category/tech/artificial-intelligence — MSM source, has fresh AI stories
- The Hacker News: https://thehackernews.com/ — **excellent for AI security stories** (Agentjacking, supply chain attacks, model vulnerabilities) that often don't appear on mainstream tech outlets. Fresh within-24h cybersecurity reporting with direct relevance to AI agent security. Scroll past the first few stories to find latest entries.
- Ars Technica AI: https://arstechnica.com/ai/ — **CAUTION: stories are often 2-5 days old**, not within 24h. Check timestamps carefully via browser_console before including.
- Scientific American: https://www.scientificamerican.com/artificial-intelligence/ — academic/research-focused AI stories. Cookie consent gate: reject optional cookies first, then extract via `browser_console`. See `references/scientific-american-extraction.md` for the exact pattern.
- Hacker News: https://news.ycombinator.com — check for AI/ML trending stories

**MSM sources (WORKING):**
- BBC Technology: https://www.bbc.com/technology (filter for AI) — **WARNING**: BBC article URLs use non-intuitive IDs and the homepage-linked AI articles often return 404 when navigated to directly. The BBC does have AI-related feature stories but they tend to be evergreen/feature content, not breaking news. Navigate to the Artificial Intelligence sub-page: `https://www.bbc.com/technology` → click "Artificial Intelligence" link in sub-navigation.
- Fox News Tech: https://www.foxnews.com/category/tech/artificial-intelligence
- The New York Times (via Google News AI results) — often has within-24h AI policy stories

**UNRELIABLE - Often times out, blocked, or returns 404 for article URLs:**
- Associated Press AI: https://apnews.com/hub/artificial-intelligence — timed out May 2026; retry but don't count on it
- CNBC — while headlines appear in Google News results, direct article URL navigation nearly always returns a 404/not-found page (observed May 6, 2026). Google News snippet text is the only reliable content source for CNBC articles.
- Fox Business (foxbusiness.com) — links from Fox News AI category that point to foxbusiness.com reliably return 404. Only foxnews.com-hosted articles are accessible.

**BLOCKED - DO NOT USE:**
- Reuters - blocked by bot detection
- CNN - blocked by bot detection
- Bloomberg - blocked by robot verification
- Reddit (r/artificial, r/MachineLearning) - blocked by Cloudflare
- Twitter/X - requires authentication

## Site-Specific Extraction Notes

With RSS-first approach, most sources are covered by their feed URLs above. The following reference files exist for edge cases where RSS fails and browser fallback is needed:

- **TechCrunch** → `references/techcrunch-extraction-technique.md`
- **The Verge** → `references/verge-extraction-technique.md`
- **Google News** → `references/google-news-extraction-technique.md`
- **Scientific American** → `references/scientific-american-extraction.md`

**Do NOT load these unless RSS has failed for that specific source.**
| **IronPulse Weekly Variant** → `references/ironpulse-weekly-variant.md` — 7-day research mode for "this week's AI news" requests. Different output format, email delivery, themes analysis required. Use when user says "weekly," "this week," or "Larry weekly."
| **Final Consolidated Report Pattern** → `references/final-consolidated-report-pattern.md` — Cron-specific variant for producing a 20-story FINAL report from multiple pre-existing data sources with mandatory deduplication. Different output format (5 themes, 5-6 sentence summaries, exclusions). Use when user has multiple data files and wants a consolidated FINAL report excluding stories already covered.
| **Multi-Source Exclusion + Parallel Delegation** → `references/multi-source-exclusion-and-delegation.md` — Proven workflow for TensorFeed API bulk discovery + parallel browser delegation to build 20-story FINAL reports with deduplication against pre-existing data files.
| **Pre-Existing Data Consolidation (No Fresh Research)** → `references/pre-existing-data-consolidation.md` — Variant for when the user provides data files (blogwatcher, ironpulse, tensorfeed) and asks for a consolidated report FROM those files with exclusions. No browser research, no delegate_task. Used when user says "excluding the stories included in the following data files."

**Always load the relevant reference before extracting from a source you haven't visited this session.** These files prevent wasted tool calls on empty query results.

### RSS-First Extraction Strategy (July 2026)

**RSS feeds are the primary data source. Browser scraping is the last resort.**

The old approach (browser snapshot + console extraction) was fragile — sites blocked bots, snapshots truncated, console queries returned empty, article URLs returned 404. RSS sidesteps all of this:

- **One curl call per source** gets you 20+ headlines, publish dates, and article links
- **No bot blocking** — RSS readers don't trigger Cloudflare or CAPTCHAs
- **No fragile DOM selectors** — RSS is structured XML/JSON
- **No stale URLs** — the feed contains live article links

**Proven workflow:**
1. Fetch RSS feeds from 4+ sources via curl
2. Parse XML for headlines, timestamps, links, descriptions
3. For full article text on key stories, curl the article URL directly (not via browser)
4. Only use browser_navigate when a source has no RSS feed or the feed is broken

## Timestamp Verification Technique

To verify that stories are within the last 24 hours, use `browser_console` with a query that extracts `<time>` elements:

```javascript
// Get all article timestamps from a page
const times = document.querySelectorAll('time');
Array.from(times).slice(0,20).map(t => t.textContent?.trim() + ' | ' + (t.getAttribute('datetime') || ''));

// Or get headlines + timestamps from article elements
const arts = document.querySelectorAll('article');
Array.from(arts).slice(0,20).map(a => {
  const h = a.querySelector('h2, h3');
  const t = a.querySelector('time');
  return { headline: h?.textContent?.trim()?.substring(0,80), time: t?.getAttribute('datetime') || t?.textContent?.trim() || 'N/A' };
});
```

For sites that show relative times ("17 hours ago", "3 days ago"), use a wider selector to find all timestamp elements and check for "ago" patterns.

## Primary Data Sources — RSS First, Browser Fallback

**HARD RULE: RSS feeds are the PRIMARY data source. Browser scraping is the LAST resort.**

The primary sources in priority order, with their RSS feed URLs:

1. **TechCrunch AI** — `https://techcrunch.com/category/artificial-intelligence/feed/` — reliably has fresh stories, high editorial quality, good for business and funding angle.
2. **The Verge AI** — `https://www.theverge.com/rss/ai-artificial-intelligence/index.xml` — excellent for very fresh stories, strong policy and product coverage.
3. **Google News AI** — `https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en` — widest diversity of sources in one view.
4. **WIRED AI** — `https://www.wired.com/feed/tag/ai/latest/rss` — for specific investigative or policy-led stories.
5. **Ars Technica AI** — `https://arstechnica.com/ai/feed/` — engineering-focused AI coverage.
6. **Hacker News** — `https://hnrss.org/frontpage?count=30` — AI/ML trending stories.
7. **Fox News AI** — `https://moxie.foxnews.com/feedburner/artificial-intelligence.xml` — MSM perspective.
8. **Scientific American** — `https://www.scientificamerican.com/artificial-intelligence/rss/` — academic/research-focused AI stories.

**Hard rule:** Minimum 4 different source DOMAINS per report. RSS first, browser fallback only when RSS fails.
