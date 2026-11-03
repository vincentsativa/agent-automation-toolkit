# Source Health for FINAL Consolidated Reports

## Last Verified: June 15, 2026

When building a 20-story FINAL consolidated report from Google News search results, most article URLs from non-TechCrunch and non-Verified sources will return 404, paywalls, or bot challenges. Use this guide to know which sources are worth navigating to vs. which ones force summary-from-metadata.

## RELIABLE (navigable, full article accessible)

| Source | Quirk | Summary Strategy |
|--------|-------|-----------------|
| TechCrunch | Article URLs from category page work. Old URLs may 404. | Navigate directly, extract full article content |
| The Verge | Article URLs work from category page | Navigate directly, extract full content |
| Breaking Defense | Direct navigation works | Navigate directly |
| Johns Hopkins / University press | Direct navigation works but may land on archive page | Navigate directly |
| YaleNews / CMU News | University press sites generally work | Navigate directly |
| ASU News / Virginia Tech News | University press, accessible | Navigate directly |
| PBS / C-SPAN | Government/educational, accessible | Navigate directly |

## UNRELIABLE (blocked, bot detection, or 404)

| Source | Failure Mode | Fallback Strategy |
|--------|-------------|-------------------|
| Politico | Cloudflare bot challenge at article URL | Use Google News snippet + headline only |
| Business Insider | 404 on article URLs (page not found) | Use the image/headline visible on the 404 page + Google News snippet |
| PYMNTS | All article URLs return 404 | Use Google News snippet + headline only |
| CalMatters | Article URLs return 404 | Use Google News snippet + headline only |
| CSO Online / CIO / InfoWorld / Network World | All FoundryCo sites return 404 | Use Google News snippet + headline only |
| inc.com | DataDome device check blocks | Use Google News snippet + headline |
| Washington Post | Paywall blocks full access | Use Google News snippet + headline only |
| New York Times | Paywall blocks full access | Use Google News snippet + headline only |
| The Economist | Paywall or 404 on article URLs | Use Google News snippet + headline only |
| Tom's Hardware | Article URLs often redirect to 404 | Try searching for correct URL, fallback to snippet |
| The Motley Fool | Investment site, paywalled | Use Google News snippet + headline |
| Yahoo Finance | Republished content, accessible | Navigate directly but content is usually a repost |

## EXTRACTION WORKFLOW

1. **Google News first.** Navigate to Google News AI search. Immediately call `browser_console(expression='document.body.innerText.substring(0, 50000)')` to bypass snapshot truncation. Extract headlines, source names, and timestamps.

2. **TechCrunch for depth.** Navigate to TechCrunch AI category for articles with full extractable text. TechCrunch articles are reliable sources for 5-6 sentence summaries.

3. **The Verge for depth.** Navigate to The Verge AI section. Also reliable for full extraction.

4. **Build story pool to 25-30 candidates.** Because 10-15 of your Google News results will be from blocked/unreliable sources, you need more candidates than 20 to find 20 fresh, summarized stories.

5. **Summarize blocked sources from metadata.** For blocked sources, write a concise 5-6 sentence summary using:
   - The headline (which contains key information)
   - The Google News snippet (usually 1-2 sentences visible)
   - The source's editorial reputation
   - Context from related stories in the data files
   - Label stories from blocked sources as having limited detail