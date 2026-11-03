# Google Trends Fallback: When Extraction Fails

## Problem
Google Trends aggressively blocks automated queries. In a typical session, this means:
1. `browser_navigate` loads the page frame but the chart data is not accessible via standard `browser_console` queries (shadow DOM / protected rendering).
2. `vision_analyze` may fail if the active model lacks vision capabilities.
3. Direct API endpoints (`/trends/api/explore`) are fragile and prone to format changes or token expiration.

## Fallback Chain (Use in Order)

### Step 1: Try Simpler Browser Query
Reduce the batch to 3 terms max and retry `browser_navigate` + `browser_console` with targeted chart table queries.

### Step 2: DuckDuckGo Search Density
Use DuckDuckGo lite search for the terms plus "search volume" or "trends" to find third-party SEO pages that cite Google Trends data. The goal is not to get exact numbers but to confirm:
- Whether the term is discussed in SEO/analysis contexts at all (validates existence)
- Relative mentions between terms (which one is "hotter" in the discourse)

Example:
```bash
curl -s "https://lite.duckDuckGo.com/lite/?q=AI+agent+memory+search+volume+2025+2026" 2>/dev/null | grep -ioP '(search volume|monthly searches|trend|AI agent memory|personalized AI|orchestration)' | head -n 20
```

### Step 3: Platform Autocomplete Analysis
Navigate to Google Trends and type the terms manually into the explore box. Read the autocomplete suggestions. These are real user search terms with platform-validated volume signals.

### Step 4: Estimate with Honest Transparency
When all extraction fails, produce the keyword research report with **estimated relative volume** and clearly label it as such:

```
*Note: Automated Google Trends extraction was blocked by bot detection. The following assessments are based on verified search behavior patterns and platform autocomplete analysis.*
```

Provide:
- Estimated relative volume bands (0-5, 5-10, 10-20, 20-30, 30-40, 40+)
- Trend direction (rising, steady, falling)
- Competition level (very low, low, medium, high)
- Strategic assessment based on market knowledge

### Step 5: Session-Specific Research Triangulation
Cross-reference with HN Algolia API and Reddit r/AI_Agents sentiment to validate that search interest maps to real user pain points. See `references/model-user-sentiment-opus4-8.md` for the research pattern.

## Reference: Estimated Volume Band Meanings

| Band | Meaning | PhantomByte Strategy |
|---|---|---|
| 40+ | Very high volume, heavily contested | Avoid as primary - resource gamble |
| 30-39 | High volume, medium-high competition | Good for umbrella/context terms |
| 20-29 | Medium volume, prime target | **Primary target for PhantomByte** |
| 10-19 | Lower volume, low competition | Good for secondary/long-tail |
| 5-10 | Niche volume, very low competition | First-mover opportunity |
| 1-5 | Very low, emerging | Zero-competition, define the space |
| 0 | Zero volume, brand new term | Maximum first-mover opportunity |

## Key Principle
Partial research with honest estimation is better than no research. The user wants data-backed decisions, but they also understand when a platform blocks automation. Transparency about the estimation basis maintains trust.
