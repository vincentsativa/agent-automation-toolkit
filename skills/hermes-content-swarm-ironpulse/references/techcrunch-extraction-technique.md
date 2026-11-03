# TechCrunch AI, Story Extraction Technique

## Why This Exists

TechCrunch's AI category page renders stories in a `<list>` element with `<listitem>` children. The DOM is structured around `<h3>` headings inside list items, with `<time>` elements for timestamps. Standard `document.querySelectorAll('article')` works partially but `h3` selectors are more reliable for headline extraction.

## Reliable Extraction Workflow

### Step 1: Navigate and Snapshot

```javascript
browser_navigate('https://techcrunch.com/category/artificial-intelligence/')
browser_snapshot()
```

The snapshot reveals all top stories. Each story block contains:
- An optional category label (`IN BRIEF`, `AI`, `ROBOTICS`, `APPS`, `HARDWARE`, `FUNDRAISING`, etc.)
- An `<h3>` heading with the headline as a child `<a>` link
- Author name
- `<time>` element with relative timestamp ("36 minutes ago", "2 hours ago")

### Step 2: Extract All Headlines

```javascript
// Best approach, grab all h3 elements that contain links
document.querySelectorAll('h3').forEach(h => {
  const a = h.querySelector('a');
  if(a && a.textContent.trim().length > 10) headlines.push(a.textContent.trim());
});
```

This consistently returns 30-40 headlines including sponsored content. Filter out:
- Sponsored posts (labeled "SPONSORED")
- TechCrunch Disrupt event promotions (contain "Disrupt" or "ticket")
- Already-seen duplicates (TechCrunch may render the same headline in multiple sections)

### Step 3: Get Timestamps

```javascript
// Extract datetime attributes from time elements
document.querySelectorAll('time');
```

Each story's `<time>` element has a `datetime` attribute in ISO format (`2026-05-06T10:23:08-07:00`) and displays relative text ("36 minutes ago").

### Step 4: Read Individual Articles

**CRITICAL, Do NOT guess article URLs.** TechCrunch does NOT use date-based URL patterns that can be reverse-engineered from headlines. Navigating to a guessed URL returns 404. Always navigate to the article by:
1. Clicking the story link from the category page snapshot, OR
2. Using `browser_navigate` with the exact permalink as it appears in the feed

If you see a story on the category page and try to construct the URL yourself, you will get a 404 and waste time. Extract the URL from the DOM link element, don't reconstruct it.

After navigating to an article, call `browser_snapshot(full=true)` and parse the snapshot text for the full story content.

## Curl-Based Fallback (When Browser Is Unavailable)

When `browser_navigate` fails (e.g., missing agent-browser binary), use curl to extract TechCrunch stories:

### Step 1: Extract Article URLs

```bash
curl -sL "https://techcrunch.com/category/artificial-intelligence/" | grep -oP 'href="https://techcrunch\.com/2026/[^"]*"' | sort -u | head -20
```

This extracts all article permalinks from the category page. TechCrunch uses date-based URLs (`/2026/06/22/slug/`) that are reliably extractable from the HTML.

### Step 2: Get Headlines and Timestamps

For each article URL, fetch the page and extract the `<h1>` and `datetime` attribute:

```bash
curl -sL "https://techcrunch.com/2026/06/22/example-slug/" | grep -oP '<h1[^>]*>.*?</h1>' | sed 's/<[^>]*>//g'
curl -sL "https://techcrunch.com/2026/06/22/example-slug/" | grep -oP 'datetime="[^"]*"'
```

### Step 3: Get Article Body Text

TechCrunch article body paragraphs use class `wpds-c-cPSKzG` (or similar dynamic class). Extract with:

```bash
curl -sL "$url" | sed -n '/<p class="wpds-c-[^"]*"[^>]*>/,/<\/p>/p' | sed 's/<[^>]*>//g' | head -8
```

If the class-based selector fails, fall back to extracting all `<p>` tags in the article content area.

### Step 4: Filter by Recency

TechCrunch timestamps use ISO 8601 format: `datetime="2026-06-22T13:13:58-07:00"`. Stories from today or yesterday with a time within the last 24 hours are valid. Stories dated 2+ days ago are outside the window.

## Timestamp Verification

TechCrunch shows relative timestamps for today's stories:
- "36 minutes ago" → verify within 24h
- "2 hours ago" → within 24h
- "3 hours ago" → within 24h

Stories with dates like "Apr 29, 2026" are outside the 24-hour window.

## Pitfalls (Browser + Curl)

- **Scrolling required (browser)**, The initial snapshot only shows ~6-8 stories. Scroll down to load more (TechCrunch has infinite scroll).
- **Sponsored content**, Look for "SPONSORED" labels and skip them.
- **Event promotions**, TechCrunch Disrupt ticket ads appear as h3 elements. Filter with `.includes('Disrupt')` or `.includes('ticket')`.
- **Duplicate headlines**, The same story may appear in "Latest News" sidebar AND main feed.
- **404 on direct link**, Some TechCrunch URLs generated from h3 text may not be the actual permalink. Navigate to the story from the main feed rather than guessing the URL.
- **`browser_console` errors**, If you get "Identifier '...' has already been declared", use a different variable name or wrap in an IIFE.
- **Curl: some article URLs return 404** even when they appear in the category page feed. TechCrunch occasionally removes articles without updating the feed. Skip these and move on.
- **Curl: category page shows ~15-20 stories** but only ~8-12 are from the last 24 hours. Filter by checking each article's datetime.
- **Curl: event promotions** (TechCrunch Disrupt, Founder Summit) appear as article cards. Skip these by checking for "Disrupt", "ticket", "Founder Summit" in the headline.
