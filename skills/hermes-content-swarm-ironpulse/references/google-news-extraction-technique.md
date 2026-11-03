# Google News AI Story Extraction Technique

## Why This Exists

Standard CSS selector queries (`document.querySelectorAll('article')`, `document.querySelectorAll('time')`, etc.) frequently return empty arrays on Google News because the page uses non-standard element structures. The `a` elements that contain story data don't use `<article>` tags, and `<time>` elements may be absent or hidden in shadow DOM.

## Proven Fallback: `document.body.innerText`

When `browser_console` with CSS selectors returns empty results, use this:

```javascript\ndocument.body.innerText.substring(0, 30000)\n```

This dumps all rendered text on the page as a single string. Google News renders search results as text blocks with the format:

```
[Source Name]
More - [Description]
[Actual Headline]
[Time Ago]
By [Author]
```

Example from actual extraction:
```
Medical Xpress
More - A new AI model enables more efficient analysis of colorectal cancer samples
A new AI model enables more efficient analysis of colorectal cancer samples
22 minutes ago
By Marc Levy
```

Key pattern: The actual headline appears as the line immediately before the time stamp, and is also duplicated in the "More - [Description]" line above it.

Each story cluster has: source name, headline, relative timestamp, and byline — all as sibling text nodes. Parse this by:

1. Scanning for "hours ago", "minutes ago", "ago" patterns
2. Reading 1 line above for the headline (verify it matches the line after "More - ")
3. Reading 2 lines above that for the source/organization
4. Reading 1 line below for the author (if it starts with "By ")

## Curl-Based Fallback (When Browser Is Unavailable)

When `browser_navigate` fails, use curl to extract Google News AI stories:

### Step 1: Fetch the Page

```bash
curl -sL "https://news.google.com/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en"
```

### Step 2: Extract Story Metadata from aria-labels

Google News renders each story as an `<a>` tag with an `aria-label` attribute containing the full story metadata in a single string:

```bash
curl -sL "https://news.google.com/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en" | grep -oP 'aria-label="[^"]*"' | head -20
```

Each aria-label follows the format:
```
aria-label="[Headline] - [Source] - [Time ago] - By [Author]"
```

Example:
```
aria-label="AI models capable of devastating attacks on governments and business months away, rare Five Eyes statement warns - The Guardian - 13 hours ago - By Sarah Basford Canales"
```

### Step 3: Parse the Results

Split each aria-label on " - " to extract:
- Position 0: Headline
- Position 1: Source name
- Position 2: Time ago (e.g., "13 hours ago", "1 hour ago")
- Position 3: Author (if present, starts with "By ")

### Step 4: Filter by Recency

Filter results to only include stories with "hour" or "minute" in the time-ago field. Exclude "Yesterday", "day ago", "days ago".

### Pitfalls

- Google News uses obfuscated relative URLs (e.g., `./read/CBMi...`). These cannot be navigated to directly — they require Google's session context. Extract story content from the aria-label metadata only.
- The first 3-5 results may be dominated by a single breaking story across multiple sources. Deduplicate by headline similarity.
- Google News returns results from many outlets including some that are blocked by bot detection (Reuters, CNN, CNBC). The aria-label text is the only reliable content source for those articles.

## Full Extraction Workflow

```
1. browser_navigate('https://news.google.com/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en')
2. browser_scroll('down') — trigger lazy loading (do this 1-2 times)
3. browser_console(expression="document.body.innerText.substring(0, 30000)")
4. Parse the raw text for headlines with " ago" timestamps
```

## Pitfalls

- Google News lazy-loads stories. Always scroll at least once before extracting.
- The first result may include promoted/sticky content. Scroll past it.
- Relative timestamps like "18 hours ago" vs "Yesterday" vs "5 days ago" — filter to only include stories with "hour" or "minute" in their timestamp text.
- Stories marked "Yesterday" or with day counts (e.g. "2 days ago") are outside the 24-hour window.
- "1 hour ago", "2 hours ago" etc. all contain "hour" — simple substring check works.
