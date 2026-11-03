# Ghostwriter Research Playbook

Fast verification of facts claimed in an outline. No open-ended research. Targeted checks only.

## Check targets in priority order
1. arXiv papers named in outline / daily data files
2. Vendor reports referenced in data files (if URL works)
3. Daily data files (TensorFeed, Claude reports, etc.) for corroborating detail
4. Hacker News or tech news sources for vendor announcements that lack formal papers

## arXiv verification (fastest)
1. **Check TensorFeed / daily data files first.** The data files often contain verified arXiv abstracts, author lists, and key numbers already extracted. If the outline claims match the data-file abstract exactly, that is your verified source. Skip the browser trip unless the data file contradicts the outline or omits a number you need.
2. If the data files are silent or incomplete, navigate directly to `https://arxiv.org/abs/<id>`.
3. Look for the expected title and submission date. Click through to the abstract page for authors, abstract, and metadata.
4. Record: authors, submit date, DOI, and any numbers quoted in abstract (runs, models, mechanisms, etc.). For long abstracts that truncate in the snapshot, use `browser_console` with `document.querySelector('blockquote')?.innerText` to extract the full abstract text.
5. Cross-check hard numbers from the outline against the abstract. Parameter counts, benchmark scores, and release dates in outlines frequently drift from the source paper by the time of writing. Use the arXiv number, not the outline number.
6. If no match: try title-word queries, author names, or broader keyword queries.

## Parallel browsing pitfall
- The browser tool does not handle multiple simultaneous `browser_navigate` calls well. Fire them sequentially, or batch them inside an `execute_code` script that loops over URLs and extracts snapshots programmatically. Do not expect parallel browser calls to return clean, readable output.

## Search-engine CAPTCHA fallback
When browser-based search hits a CAPTCHA or bot block on Google, Bing, or DuckDuckGo, do not stall. Switch immediately to API and curl fallbacks:
- **Hacker News Algolia API**: `curl -sL "https://hn.algolia.com/api/v1/search?query=<term>&tags=story" -o /tmp/hn.json` returns story hits with `title` and `url`. This is the fastest path for verifying tech news claims.
- **Direct curl extraction**: `curl -sL <article_url> | grep -i "<keyword>"` can confirm a headline, date, or key phrase from raw HTML without rendering JavaScript.
- **curl + python3 pipeline**: Safer than `curl | python3` direct pipe. Write JSON to a file, then read it with Python.
These fallbacks avoid the parallel-browser pitfall and bypass CAPTCHA walls entirely.

## Failed vendor URLs
- If a claimed vendor blog URL returns 404 or redirect, treat it as unverified.
- Check daily data files for the same report summarized by your research pipeline. If a data file contains the same claims with source attribution, treat the data file as the verified source and cite it as "reported via [data feed name]."
- Do NOT fabricate a working URL or guess the correct path.

## Daily data files
- Path pattern: `~\OneDrive\Desktop\TODAYS DATA FILES\`
- Read ALL relevant files in the folder. The daily dump may contain multiple formats (tensorfeed_report_YYYY-MM-DD.md, blogwatcher-dump-YYYY-MM-DD.txt, ironpulse-YYYY-MM-DD.txt, and exclusion lists). A story, quote, or number may appear in one file but not another. Cross-referencing across files builds stronger verification when a primary source URL fails.
- Read relevant files (TensorFeed, Claude reports, blogwatcher, ironpulse) for numbers, quotes, and source links.
- Do NOT copy their social posts or Pinterest descriptions into your article -- use the raw facts only.

## Fact-check rule
- Opinions and theories from the outline are fine as written, no verification needed.
- Hard numbers from the outline MUST be verified against the source (arXiv abstract, verified report, data file) before inclusion.
- If a number cannot be verified, state the claim with the source name as attribution (e.g. "AgingBench authors report...") rather than as absolute fact.
- If a source is completely unverifiable, flag to Vinny for clarification rather than silently dropping it.