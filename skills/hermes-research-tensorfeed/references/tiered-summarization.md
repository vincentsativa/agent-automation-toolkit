# Tiered Summarization for 30-50 Article Reports

When the daily report produces 50 articles, you cannot browse every one. Use a three-tier approach proven in production (June 10, 2026: 50 articles, 15 deep summaries, 35 shorter + headlines).

## The Three Tiers

### Tier 1 — Deep 5-Sentence Summaries (12-15 stories)

Pick the stories that will anchor your themes. These are typically:

- Frontier model releases (Anthropic Fable 5/Mythos 5)
- Major infrastructure/architecture news (NVIDIA+Apple PCC, Inferoa caching)
- Industry-shaping predictions (TechCrunch cheap models)
- Real-world deployments at scale (Google Gemini World Cup)
- Key arXiv papers that support the engineering theme (context engineering, memory, verification)
- Any story that will be cited in the theme analysis as a signal

**Method:** 3 rounds of `delegate_task` × 3 stories each = up to 9 deep summaries. Fill remaining from browser if time permits.

Each `delegate_task` goal template:
```
"Browse {URL} and return a 5-8 sentence detailed summary covering the core claim, key data points, and implications."
```

**Known timeout risks for delegate_task browsing:**
- WSJ articles consistently time out the browser subagent (60s+). Skip these for deep browsing and use snippet + headline only.
- WIRED articles are partially behind a paywall. The lede and first section are usually accessible; the full body is not. Use what's available.
- BBC articles work but need cookie consent handling. The browser snapshot + console extraction pattern works after accepting cookies.
- CNBC article URLs from Google News nearly always return 404. Use Google News snippet text only.

### Tier 2 — Paragraph Summaries (12-15 stories)

For stories that are interesting but won't anchor themes. Use the existing TensorFeed data (title, source, snippet, categories) plus your own knowledge of the story context to write a 3-5 sentence summary. No browsing needed. These stories come from:

- Community/Show HN projects that are interesting but not thematic
- ZDNet/WIRED/Verge coverage that is consumer-oriented
- arXiv papers that are tangential to the themes
- Repeat coverage of the same story from multiple sources (consolidate)

### Tier 3 — Headlines Only (remaining ~20 stories)

The rest get listed with title, source, and a single-sentence description. No browsing, no deep analysis. Just enough information to show coverage breadth.

### Selection heuristic for Tier 1 vs Tier 2

| Signal | Action |
|--------|--------|
| Story appears in 3+ sources | Tier 1 (it's a major story) |
| Story involves a concrete number (97.8%, 91.6%, $10/M tokens) | Tier 1 (data-driven content) |
| Story directly supports an identified theme | Tier 1 |
| Story is a Show HN with 0 comments | Tier 3 (community project, unproven) |
| Story is arXiv but doesn't connect to themes | Tier 2 or 3 |
| Story is product review/consumer advice | Tier 2 or 3 |

## Producing the Report

Write the report document in this order — it's faster than jumping around:

1. Dump all 50 article snippets into a scratch buffer
2. Assign tiers while scanning (this takes ~30 seconds mentally)
3. Launch delegate_task rounds for Tier 1 stories (parallel)
4. While waiting for delegation results, write Tier 2 and Tier 3 entries using the scraped data
5. When delegation results arrive, insert Tier 1 summaries
6. Write the three themes analysis
7. Do PhantomByte coverage gap check (navigate to home page, read snapshot inline — no JS required)
8. Write article recommendations
9. Save to file
10. Email