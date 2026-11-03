# Parallel Browsing Pattern for Article Summaries

Use this pattern when the editorial brief workflow requires browsing 3-6 articles in depth for rich summaries. This is faster than sequential browsing (2 rounds of 3 concurrent tasks completes in ~30-40 seconds vs 3-5 minutes sequential).

## When to Use

- Stories that will anchor an unwritten theme (need accurate claims to support the angle)
- Stories with controversial or surprising claims (verify they're real, not editorialized headlines)
- Stories from sources you don't have context for (new domains, niche outlets)
- Stories you're going to write a detailed X post about

## When to Skip Browsing

- Stories from well-known beats covered by multiple sources
- arXiv papers (abstract alone is sufficient)
- Incremental product updates
- Stories where the headline + source reputation gives enough context for the summary

## Concurrency Limit: 3 Tasks Per Call

The system enforces `max_concurrent_children=3` for this user. A single `delegate_task(tasks=[...])` call with 4+ items will be rejected. To browse 6-9 articles, dispatch in rounds of 3:

### Round 1 (3 most important stories)

```python
delegate_task(tasks=[
    {
        "goal": "Browse this article and return a 5-8 sentence factual summary with key claims, data points, and quotes. Article: <URL>",
        "toolsets": ["browser"]
    },
    {
        "goal": "Browse this article and return a 5-8 sentence factual summary with key claims, data points, and quotes. Article: <URL>",
        "toolsets": ["browser"]
    },
    {
        "goal": "Browse this article and return a 5-8 sentence factual summary with key claims, data points, and quotes. Article: <URL>",
        "toolsets": ["browser"]
    },
])
```

### Round 2 (next 3 stories — while writing summaries from Round 1)

```python
delegate_task(tasks=[
    {
        "goal": "Browse this article and return a 5-8 sentence factual summary with key claims, data points, and quotes. Article: <URL>",
        "toolsets": ["browser"]
    },
    {
        "goal": "Browse this article and return a 5-8 sentence factual summary with key claims, data points, and quotes. Article: <URL>",
        "toolsets": ["browser"]
    },
    {
        "goal": "Browse this article and return a 5-8 sentence factual summary with key claims, data points, and quotes. Article: <URL>",
        "toolsets": ["browser"]
    },
])
```

### Round 3 (final 3 — if needed)

Same pattern as above. Three rounds of 3 = 9 articles browsed in parallel.

## What Each Subagent Returns

Each subagent returns a structured summary containing:
- The article's central claim or news event
- Key data points, statistics, and named entities
- Direct quotes from named sources
- Context about why the story matters
- Any caveats or counterpoints mentioned in the article

## Pitfalls

- **Do not browse every headline.** Pick 3-6 anchor stories. The remaining ~10 headlines can be summarized from headline + source reputation alone.
- **WIRED articles often require scrolling** to reveal full content past paywall elements. The subagent handles this automatically with browser_scroll.
- **TechCrunch and The Decoder** usually load full content in a single browser_navigate call — no scrolling needed.
- **Each subagent gets its own browser session** — they don't interfere with each other.
- **Total time:** ~15-20 seconds per round of 3, so 2 rounds = ~30-40 seconds total.

- **CRITICAL: Subagent results are NOT guaranteed to return before you finish the brief.** Subagents run in the background and their results re-enter the conversation as new messages when they complete. There is no blocking mechanism. Write summaries from your own knowledge of the headline + source context first. Treat subagent browsing results as optional enhancements that arrive later — do NOT block on them or structure your output around them. If you need summaries to complete the brief, write them yourself from available knowledge and let subagent results be a bonus.
