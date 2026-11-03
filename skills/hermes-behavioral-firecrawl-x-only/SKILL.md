---
name: firecrawl-x-only
description: Use when choosing search backend. Firecrawl is X-only.
---

# Firecrawl Is X-Only

Vinny's rule: **Firecrawl is ONLY used for X (Twitter) and JS-heavy pages that
Keenable cannot render.** Never default to Firecrawl.

## Default = Keenable

- For ANY web search, use `web_search` (Keenable backend) first.
- Keenable is keyless and free. Use it for everything by default.

## When Firecrawl is allowed (and only then)

Firecrawl MCP tools (`firecrawl_scrape`, `firecrawl_search`, etc.) are used
ONLY when:
1. The target is X.com / Twitter, OR
2. The page is JS-rendered and Keenable returns empty/blocked content.

If Keenable works, Firecrawl is not used. Period.

## Prohibition

- Do NOT use Firecrawl for normal web search, news, docs, or any page Keenable
  can fetch.
- If in doubt, use Keenable. Firecrawl is the exception, not the default.

## Finding what is trending on X (`firecrawl_search` + `firecrawl_scrape`)

Run these in this order. Each step feeds the next.

1. **`firecrawl_search` with `site:x.com` and `tbs: "qdr:d"`.** That is the only
date window that reliably means "today". Query by topic, not by "trending":
`"AI site:x.com"` and `"OpenAI OR Anthropic OR Grok OR Nvidia site:x.com"`. The
hits come back with a one-line snippet, an author, and a relative timestamp, so
read them as a ranked candidate list before scraping anything.

2. **`firecrawl_scrape` the individual status URLs** (`https://x.com/<user>/status/<id>`).
Each scrape returns, in markdown: `Author`, `Posted` (ISO timestamp), `Likes`,
`Retweets`, the full post text, any quoted thread post, and up to three
`Top Comments`. Those engagement counts are the ranking signal; sort candidates
by likes before writing.

3. **For trending terms rather than posts**, scrape
`https://trends24.in/united-states/`. It returns the last 24 hours of US trends
in numbered `[term](twitter.com/search?q=...)` blocks, timestamped per snapshot.
Parse with a regex over `\d{2}\. \[([^\]]+)\]` and `collections.Counter` if you
need per-term frequency across snapshots.

**Pick the topic for the audience, not the loudest term.** The US trending list
is dominated by sports and entertainment; for an AI/tech brand the trend list
almost never contains the topic. Treat trends24 as a context check and let the
`qdr:d` X search supply the actual subject.

**Two URL shapes the X engine will not return content for.** `x.com/explore/tabs/trending`
and `x.com/i/article/<id>` both come back "we do not support this site". Do not
retry them. Get the topic from the search snippet, then scrape a plain status
URL from the same thread, or verify the claim outside X (vendor blog, repo
README, filing coverage) with `web_search`.

**Verify before you write.** A post trading today may be resurfacing
months-old reporting. Confirm the underlying event date and the numbers at a
primary source, and compute any derived ratio in code rather than in your head
(16.3 / 1.1 rounds to 15x, not 16x), so the post's fact stanza survives a reply
from someone who read the filing.
