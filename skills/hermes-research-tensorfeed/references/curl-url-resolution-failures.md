# Curl URL Resolution Failures, Known Sites

## The Problem

TensorFeed API returns article URLs that may be stale, have different path structures, or redirect to 404 pages when fetched via `curl -sL`. This is a **separate failure mode** from the browser timeout/paywall issue documented in the main skill.

## Sites That Consistently Return 404 When Curled

| Site | Failure Pattern | Observed |
|------|----------------|----------|
| ZDNET | Returns ZDNET homepage/nav with "Page Not Found" in body | July 9, 2026 |
| The Verge | Returns 404 page with "That page does not exist" | July 9, 2026 |
| NVIDIA Blog | Returns "404 - Page Not Found" | July 9, 2026 |
| Google Blog (The Keyword) | Returns "Error 404 (Not Found)!!!" | July 9, 2026 |
| MIT Technology Review | Returns "404 - Page not found" (requires JS) | July 9, 2026 |

## Sites That Block Curl With Bot Detection (Different Failure Mode)

These sites have valid, live URLs that curl can reach, but they return a bot-detection wall instead of article content. The browser tool renders them fine (VentureBeat articles were read in full via browser_navigate on July 17, 2026).

| Site | Failure Pattern | Observed |
|------|----------------|----------|
| VentureBeat | Vercel Security Checkpoint, "We're verifying your browser" page returned instead of article | July 17, 2026 |

**Key difference from 404 sites:** These URLs are valid. The browser tool works. Only curl is blocked. Use browser_navigate for VentureBeat articles, not curl-to-file extraction.

## Sites That Work With Curl Extraction

| Site | Works? | Notes |
|------|--------|-------|
| Ars Technica | Yes | Full article text extracted cleanly |
| WIRED | Partial | May work but paywall-gated content is limited |
| Hugging Face Blog | Yes | Clean HTML, easy extraction |
| arXiv | Yes | Abstract pages work, use console extraction |

## Root Cause

The TensorFeed API appears to cache URLs at fetch time, and these URLs may become stale or the sites may rotate their URL structures. The 404s are not a curl-vs-browser issue, the same URLs would 404 in a browser too. The API's `snippet` field is often the only reliable content source for these sites.

## Workaround

When a curl extraction returns 404:

1. **Use the snippet field** from TensorFeed's API response. It's often 200-500 characters and sufficient for a 5-sentence summary when combined with the headline and source reputation.
2. **Do NOT retry with browser_navigate**, these same URLs will also 404 in the browser. The issue is the URL, not the tool.
3. **For critical stories** from these sources, search for an alternative URL (e.g., search the headline on Google News) rather than retrying the same broken URL.
4. **Accept the limitation**, for daily cron reports, the snippet + headline + source context is usually enough for a solid summary. The deep browse is a nice-to-have, not a requirement.

## Detection Pattern

After curling a URL, check for these signals in the extracted text:
- "Page Not Found" (ZDNET, NVIDIA)
- "404" in the first 500 chars
- "That page does not exist" (The Verge)
- "Error 404" (Google)
- "You need to enable JavaScript" (MIT Tech Review, JS-required site)

If any of these appear, fall back to snippet-only summarization immediately rather than retrying.
