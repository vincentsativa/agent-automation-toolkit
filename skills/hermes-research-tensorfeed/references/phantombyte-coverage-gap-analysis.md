# PhantomByte Coverage Gap Analysis — Site-Specific Extraction

## Site Structure (as of July 2026)

The PhantomByte site at https://articles.phantom-byte.com uses `<article>` tags in the main archive listing area. The standard JS extraction pattern:

```javascript
Array.from(document.querySelectorAll('main article h3 a')).map(a => a.innerText)
```

**works** for extracting archive article titles. However, the category sidebar uses `<li>` elements, not `<article>` tags — so `querySelectorAll('article')` returns nothing for the sidebar.

## Working Extraction Patterns

### Method 1: Snapshot-based category counting (most reliable)

Navigate to the site, then use `browser_snapshot(full=true)` and manually parse the category sidebar. The sidebar lists every category with its article count:

```
CATEGORIES
▸ All Notes 122
▸ AI & Investing 1
▸ AI & Society 2
▸ AI Agents 2
▸ AI Collaboration 1
▸ AI Engineering 20
▸ AI Ethics 1
▸ AI Industry 13
▸ AI Infrastructure 51
▸ AI News 1
▸ AI Policy 6
▸ AI Privacy 2
▸ AI Research 3
▸ AI Security 14
▸ AI Strategy 1
▸ Cloud Infrastructure 1
▸ Industry News 1
▸ Industry Report 1
```

These counts are visible in the snapshot from `browser_navigate` — no scrolling needed.

### Method 2: Console extraction of archive titles (for dedup)

The archive listing uses `<article>` elements in the main content area, but the sidebar categories are `<li>` elements. To extract archive article titles:

```javascript
// Extract archive article titles from the main content area
Array.from(document.querySelectorAll('main article')).map(a => ({
  title: a.querySelector('h3')?.innerText?.trim(),
  link: a.querySelector('a')?.href
})).filter(x => x.title)
```

This works for the archive listing but NOT for the sidebar categories.

### Method 3: Category counts from sidebar (for coverage gap analysis)

```javascript
// Extract category names and counts from the sidebar
Array.from(document.querySelectorAll('[class*="category"] li, aside li')).map(li => ({
  text: li.innerText?.trim()
})).filter(x => x.text && x.text.includes('▸'))
```

## Coverage Gap Analysis Workflow

1. Navigate to https://articles.phantom-byte.com
2. Use `browser_snapshot(full=true)` to get the full page including the category sidebar
3. Manually extract category names and counts from the snapshot text
4. Identify gaps by comparing against the current news themes.
   **Key gap pattern to watch for:** categories with high article counts that have a sub-topic with near-zero coverage. Example: AI Infrastructure has 51 articles but AI Agents has only 2 — the agent infrastructure angle is a massive gap hiding inside a well-covered category.
5. Cross-reference the latest PhantomByte article (pinned at top under "// LATEST") to avoid suggesting a topic just covered

## Current Category Snapshot (July 15, 2026)

| Category | Count | Gap Assessment |
|----------|-------|----------------|
| All Notes | 130 | — |
| AI & Investing | 1 | Near-zero |
| AI & Society | 2 | Near-zero |
| AI Agents | 6 | **Growing but still a gap** — up from 2, but still low vs 54 in AI Infrastructure |
| AI Collaboration | 1 | Near-zero |
| AI Engineering | 21 | Well-covered |
| AI Ethics | 1 | Near-zero |
| AI Industry | 14 | Moderate |
| AI Infrastructure | 54 | Heavily covered |
| AI News | 1 | Near-zero |
| AI Policy | 6 | Moderate |
| AI Privacy | 2 | Near-zero |
| AI Research | 3 | Low |
| AI Security | 14 | Moderate |
| AI Strategy | 1 | Near-zero |
| Cloud Infrastructure | 1 | Near-zero |
| Industry News | 1 | Near-zero |
| Industry Report | 1 | Near-zero |

## Gap Prioritization (for article recommendations)

When ranking article ideas, prioritize gaps in this order:

1. **AI Agents infrastructure** — 51 articles on AI Infrastructure but only 2 tagged AI Agents. The agent infrastructure layer (isolation, telephony, grounding, review gates) is the single biggest uncovered topic. This is the #1 gap to recommend.
2. **AI Research** — Only 3 articles. Good for paper-summary pieces.
3. **AI Policy** — 6 articles. Good for geopolitics/regulation pieces.
4. **Near-zero categories** (AI & Investing, AI Ethics, AI Strategy, etc.) — These are gaps but may be intentionally low because they're less aligned with the site's engineering audience. Only recommend if the news strongly supports it.

## Known Pitfalls

- The `document.querySelectorAll('article')` pattern returns empty for the sidebar — the sidebar uses `<li>` elements, not `<article>`.
- The site is a static site (likely Astro or similar) — no JS rendering issues, but the DOM structure is non-standard.
- The "// LATEST" pinned article at the top is the most recent — check its title before recommending to avoid suggesting a topic just published.
- Category counts in the sidebar are accurate and up-to-date — trust them over any cached data.
- **Counts drift over time** — the reference table above is a snapshot from a specific date. Always re-fetch fresh counts from the live site during each report session rather than relying on the cached table. The table serves as a baseline for trend detection, not a substitute for live data.
