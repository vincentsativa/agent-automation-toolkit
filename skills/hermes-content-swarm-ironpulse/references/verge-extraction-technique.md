# The Verge AI, Story Extraction Technique

## Why This Exists

The Verge uses a custom DOM structure where `document.querySelectorAll('article')` consistently returns **0** despite visible article content. Standard CSS selectors fail because the page uses generic `<div>` and `<generic>` elements (from the accessibility tree) rather than semantic HTML5 tags. This reference documents what works.

## Working Extraction Strategies

### Strategy 1: Snapshot + Link Text (Most Reliable)

1. `browser_navigate('https://www.theverge.com/ai-artificial-intelligence')`
2. `browser_snapshot(full=true)`, the full snapshot renders story headlines as `<a>` links with timestamps in the `<time>` elements next to them
3. Scan the snapshot text for:
   - The top featured story (first block after the AI section header, has a large image, headline, summary, and "X MINUTES AGO" timestamp)
   - The "LATEST IN AI" section, stories appear as `<article>`-like blocks (class `duet--article--*` even though they don't match `article` selector)
   - Each story block contains: link text (headline), author name, `<time>` element, summary paragraph, and optional tags like `[ANTHROPIC]`

### Strategy 2: Broad Anchor Extraction

The snapshot contains anchor elements linking to story URLs. Extract them with:

```javascript
// Extract all links inside the main content area
document.querySelectorAll('main a[href*="/2026/"]');
```

Filter results to exclude navigation links, "Comments", "Subscribe", "SIGN IN", and other UI elements.

### Strategy 3: Body Text Dump (Fallback, Primary Technique for Full Coverage)

This is the most reliable way to extract ALL stories when the snapshot is truncated (which is most of the time, The Verge's LATEST IN AI section runs 200+ lines deep).

```javascript
document.body.innerText.substring(0, 15000)
```

Use **15000 chars minimum**, 8000 is too small and misses stories further down the LATEST IN AI section. The snapshot truncation cutoff typically hits around the 8th-9th story, while body text at 15000 chars covers 20+ stories.

Parsing yields story clusters like:
```
Mira Murati tells the court that she couldn't trust Sam Altman's words
OpenAI's former CEO testified under oath that Altman lied to her.
JAY PETERS
9 MINUTES AGO
```

**Why this beats snapshot navigation:** The Verge article URLs always return 404 when navigated to directly (May 2026, the numeric ID in the URL is unpredictable). The body text dump + category page parsing avoids wasting tool calls on 404 navigation attempts. Extract everything you need from the category page itself.

### Strategy 4: Browser Snapshot Deep Dive

The Verge's accessibility tree renders each story as:
```
- generic
  - image "[headline text]"
  - link "[headline text]"
    - StaticText "[headline text]"
  - paragraph
    - StaticText "[summary text]"
  - generic
    - StaticText "[AUTHOR NAME]"
    - time
      - StaticText "X MINUTES AGO"
```

Parse this by extracting `link` text followed by `time` > `StaticText` patterns. The full snapshot (`browser_snapshot(full=true)`) captures the entire LATEST IN AI section including stories further down.

## Timestamp Verification

The Verge shows relative timestamps:
- "9 MINUTES AGO" → within last hour
- "8 HOURS AGO" → within 24 hours
- "MAY 5", "MAY 4" → check if these are within 24h based on current date

The `<time>` elements use `datetime` attributes. Extract with:
```javascript
document.querySelectorAll('time');
Array.from(times).slice(0,15).map(t => t.textContent?.trim() + ' | ' + (t.getAttribute('datetime') || ''));
```

## Known Pitfalls

- **No `<article>` tags**, `document.querySelectorAll('article')` returns 0 every time
- **Lazy loading**, The LATEST IN AI section may not fully load on first visit. Scroll before extracting.
- **Ad insertion**, Advertisement divs are interleaved between story blocks. Filter them out.
- **Non-story links**, The navigation, footer, and "Related" sections also contain headlines. Only use the main content area.
- **The Verge URL structure causes 404s on direct navigation (CRITICAL, May 2026):** Article URLs follow `https://www.theverge.com/2026/M/D/NUMERIC_ID/SLUG` where the numeric ID (e.g., `25066492`) is NOT predictable from date alone. Do NOT attempt to construct or navigate to The Verge article URLs directly, all attempts to `theverge.com/2026/M/D/...` style URLs returned 404 in practice. Extract article content by snapshotting the category page and reading from there, not by navigating to article URLs.
- **Duplicate content risk:** The Verge featured story at the top of the AI page is often the same story running on TechCrunch. Always cross-check with TechCrunch to avoid duplicate rankings.

## Curl-Based Fallback (When Browser Is Unavailable)

When `browser_navigate` fails, use curl to extract Verge AI stories:

### Step 1: Extract Story URLs from the Category Page

```bash
curl -sL "https://www.theverge.com/ai-artificial-intelligence" | grep -oP 'href="/[^"]*"[^>]*>' | grep -v 'static\|rss\|favicon\|font\|next\|css\|legal\|auth' | grep '^href="/[a-z]' | sort -u | head -30
```

This extracts all story links. Filter for AI-specific paths (`/ai-artificial-intelligence/`) to get only AI-section stories.

### Step 2: Get Headlines and Timestamps

The Verge's Next.js page renders story metadata in JSON within the HTML. Extract headlines from `<h1>` tags and timestamps from `datetime` attributes:

```bash
# Get headline
curl -sL "https://www.theverge.com/ai-artificial-intelligence/953183/the-atlantic-searchable-database-music-ai-training-data" | grep -oP '<h1[^>]*>.*?</h1>' | sed 's/<[^>]*>//g'

# Get timestamp
curl -sL "https://www.theverge.com/ai-artificial-intelligence/953183/the-atlantic-searchable-database-music-ai-training-data" | grep -oP 'datetime="[^"]*"' | head -1
```

### Step 3: Get Article Body Text

The Verge stores article content in JSON-LD structured data within the page. Extract the full body text:

```bash
curl -sL "https://www.theverge.com$url" | sed -n '/<p class="duet--article--article-body-component[^>]*>/,/<\/p>/p' | sed 's/<[^>]*>//g' | head -6
```

If the class-based selector fails, the JSON-LD block contains the full article text in `paragraphContents` arrays. Extract with:

```bash
curl -sL "https://www.theverge.com$url" | grep -oP '"paragraphContents":\[.*?\]' | head -1
```

### Step 4: Filter by Recency

The Verge's `publishedAt` field appears in ISO format within the JSON-LD: `"publishedAt":"2026-06-20T18:46:48+00:00"`. Stories within the last 24 hours are valid.

### Pitfalls

- **The Verge article URLs always return 404 when navigated to directly** (confirmed May-June 2026). The numeric ID in the URL is NOT predictable from the date. However, curl-based extraction of the article page itself DOES work, the 404 issue was specific to browser navigation. Curl fetches the raw HTML which contains the full article data in JSON-LD blocks.
- **The category page HTML is sparse**, most content is rendered client-side by Next.js. The `grep` approach above extracts only server-rendered links. For full story lists, you may need to combine with Google News results.
- **Story timestamps are in the JSON-LD `publishedAt` field**, not in visible `<time>` elements in the HTML (those are client-side rendered).

## Alternative Extraction Method: Duplicate Line Technique

When standard selector-based extraction fails, an alternative method is to look for duplicate consecutive lines in the text where the headline appears twice in sequence, followed by the author name and timestamp.

Pattern to look for:
- Line N: Headline text
- Line N+1: Same headline text (duplicate)
- Line N+2: Author name
- Line N+3: Timestamp (e.g., "TWO HOURS AGO", "12:08 PM EDT")

This works because The Verge's accessibility tree renders each story headline as both an image alt text and a link text, which appear as consecutive duplicate lines in the text extraction.

Example from actual extraction:
- Line 39: 'Charles’s new model is more ‘honest’ when it messes up'
- Line 40: 'Charles’s new model is more ‘honest’ when it messes up'
- Line 41: 'Jay Peters'
- Line 42: 'TWO HOURS AGO'

Steps:
1. Get full text via `browser_snapshot(full=true)`
2. Split into lines and look for consecutive duplicate lines where:
   - Line[i] == Line[i+1]
   - Line[i] has substantial length (>15 characters)
   - Line[i+2] looks like an author name (reasonable length, not containing typical UI text)
   - Line[i+3] contains time indicators ("AGO" or timestamp format)
3. Extract Line[i] as headline, Line[i+2] as author, Line[i+3] as timestamp

This method can serve as a backup when other extraction strategies fail or when dealing with dynamically loaded content.
