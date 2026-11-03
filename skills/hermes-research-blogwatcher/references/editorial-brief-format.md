# Editorial Brief Format (Blogwatcher)

Use this exact structure when producing a blogwatcher editorial intelligence brief.

## Header
```
PHANTOMBYTE EDITORIAL BRIEF
============================
Blogwatcher Intelligence Scan
Date: YYYY-MM-DD
Generated: Hermes Agent

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Headlines Section
Number each headline sequentially [1], [2], etc. Each entry has:

```
[N] HEADLINE
    Source: Blog Name
    URL: https://...

    Summary: 4-5 sentences. Lead with the most important fact, then context/impact.

    X Post: One tweet-length post. Include the URL. No tags/emojis unless thematically appropriate.
```

## Deep-Summary Browsing Strategy

For the 6-9 anchor stories that drive your unwritten themes or are the biggest news of the day:

**Use `delegate_task` with parallel browser tasks**, chain 2-3 rounds of 3 concurrent tasks each. This completes 6-9 full-article summaries in ~60-90 seconds total instead of sequential browsing which takes 3-5 minutes.

```python
# Round 1: 3 most important stories
delegate_task(tasks=[
    {"goal": "Browse article A, return 5-8 sentence factual summary with key claims and data points", "toolsets": ["browser"]},
    {"goal": "Browse article B, return 5-8 sentence factual summary with key claims and data points", "toolsets": ["browser"]},
    {"goal": "Browse article C, return 5-8 sentence factual summary with key claims and data points", "toolsets": ["browser"]},
])

# Round 2: next 3 stories (while writing summaries from Round 1)
delegate_task(tasks=[...])
```

**Pick stories to browse in depth**, not every headline needs browsing. Criteria:
- Stories that will anchor an unwritten theme (need accurate claims to support the angle)
- Stories with controversial or surprising claims (verify they're real, not editorialized headlines)
- Stories from sources you don't have context for (new domains, niche outlets)
- Stories you're going to write a detailed X post about

**Skip browsing for:** stories from well-known beats covered by multiple sources, arXiv papers (abstract alone is enough), incremental product updates, and stories where the headline + source reputation gives enough context for the summary.

## Unwritten Themes Section
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

UNWRITTEN THEMES, NOT ON PHANTOMBYTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Theme N: "PROVOCATIVE ARTICLE TITLE"

Angle: 3-4 sentence pitch explaining the article concept, angle, and why it matters now.

Supporting sources:
- Headline (Source)
- Headline (Source)

Why it hasn't been covered: Cite the closest existing PhantomByte article, the date it was published, and explain how this angle is different.
```

## Footer
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

END OF BRIEF
Generated YYYY-MM-DD by Hermes Agent, Blogwatcher Intelligence
```

## Source Filtering Notes
- The Python `--all` date-pass already includes all sources. Wired Ideas produces many non-AI articles (Dyson vacuums, soccer physics, home battery reviews, EV interviews), they'll appear in the pool but can be filtered out.
- The Decoder is a dedicated AI/tech news source. Every article it publishes is relevant, do not skip it.
- Never run per-blog `--blog` calls just to confirm source freshness. The `--all` Python pass already gives you that data.