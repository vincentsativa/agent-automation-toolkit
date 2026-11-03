# PhantomByte Category Counts (Aug 8, 2026)

Fetched via curl + `data-cat` regex counting on https://articles.phantom-byte.com.

## Totals
- Total cards: 156
- AI Infrastructure: 66
- AI Engineering: 23
- AI Security: 22
- AI Industry: 16
- AI Agents: 6
- AI Policy: 6
- AI Research: 3
- AI & Society: 2
- AI Privacy: 2
- AI & Investing, AI Collaboration, AI Ethics, AI News, AI Strategy, Cloud Infrastructure, Industry News, Industry Report: 1 each

## Zero-article gaps (unchanged from prior weeks)
- AI Hardware: 0
- AI Energy: 0
- Model Architecture: 0
- Open Source AI: 0

## Title-catalog extraction (the reliable method this week)
`re.findall(r'<h3[^>]*>\s*<a[^>]*>([^<]+)</a>', data)` returned 154 titles.
The `#\d+\n([^\n]+)` regex returned 0 matches on this build. See the SKILL.md body for the corrected pattern.

## Drift vs. prior reference
Aug 6 file: 154 total, AI Infrastructure 64, AI Engineering 23, AI Security 22, AI Industry 16.
Aug 8: 156 total, AI Infrastructure 66 (net +2), others flat. AI Engineering, AI Security, and the four zero-article gaps unchanged, the strongest recommendation targets are still the empty Open Source AI / AI Hardware / Model Architecture / AI Energy categories.

Use THIS reference for article-recommendation gap analysis; the Aug 6 and Aug 5 files are superseded (keep only for drift comparison).
