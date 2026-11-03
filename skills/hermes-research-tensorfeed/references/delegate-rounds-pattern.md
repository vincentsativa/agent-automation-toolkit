# Multi-Round DelegateTask Pattern for TensorFeed Reports

Proven in production (June 8, 2026): 3 rounds × 3 stories = 9 browsed articles in ~190s total.

## Round Structure

**Round 1, Broad news (top stories from headlines list)**
Pick the 3 most prominent non-arXiv stories that anchor the report.

**Round 2, Thematic/papers (deep content for theme construction)**
Pick arXiv papers + deep dives that will form the engineering/architecture theme.

**Round 3, Fill remaining coverage gaps**
Any stories still missing detailed summaries, or for a 24 story report.

## Goal Template

Every `delegate_task` goal uses this exact format, tested and reliable:

```
"Browse {URL} and return a detailed 5-8 sentence summary covering: the core claim, key data points, and implications."
```

For arXiv papers, also include:
```
Extract the full abstract from the page.
```

## Toolsets

Always `["browser"]`, subagents only need to navigate + read.

## Constraints

- Max 3 tasks per `delegate_task` call (configurable via delegation.max_concurrent_children)
- Wait for all to complete before starting next round
- Each round takes ~15-70s depending on page complexity and navigation depth

## CRON SESSIONS: Do NOT Use This Pattern

Delegate_task subagents deliver their results as new messages that re-enter the parent conversation. In cron sessions, the session may not persist long enough to receive these messages, the parent process exits or the session is closed before the subagents finish. The subagents' work is silently discarded.

**In cron sessions, use sequential browsing instead:**
- browser_navigate + browser_snapshot for each article
- Or curl-to-file + Python extraction for heavy JS sites
- Sequential browsing of 6-8 key articles takes ~2-3 minutes total
- Focus browsing on articles that will anchor your themes