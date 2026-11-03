# News Timeline Reconstruction via HN Algolia

Extracted from the "Fable 5 re-release" research session (June 22, 2026). When search engines are all CAPTCHA-blocked, HN Algolia can reconstruct a complete news timeline from story titles alone.

## The Problem

Search engines (Google, DuckDuckGo, Bing) all CAPTCHA-block cloud IPs. You cannot search for news the normal way. But HN Algolia is never blocked and has excellent coverage of AI/tech news.

## The Technique

### Step 1: Broad story search

```
curl -s "https://hn.algolia.com/api/v1/search?query=Fable+5+Anthropic&tags=story&hitsPerPage=50"
```

This returns up to 50 story titles with timestamps. For a hot topic, this alone can reconstruct the full timeline.

### Step 2: Sort chronologically from the results

The API returns results by relevance by default, but each hit has a `created_at` field. Extract and sort them mentally (or with a quick script) to build the timeline.

### Step 3: Identify key inflection points from titles

Story titles on HN are often descriptive enough to identify:
- Release dates ("releasing tomorrow")
- Jailbreak events ("jailbroken to bypass guardrails")
- Government actions ("US ban", "government directive to suspend")
- Company responses ("pulled Fable 5", "confident of re-enabling")
- User sentiment ("refusing innocuous prompts", "weak at flagging prompts")

### Step 4: Fetch the most important story for details

```
curl -s "https://hn.algolia.com/api/v1/items/STORY_ID"
```

Returns the full story + top-level comments. Use this for the article URL and initial community reaction.

### Step 5: Fetch the article itself (if accessible)

The story URL is in the `url` field. Try curl with a browser UA. If it's paywalled, the HN story title + comments may be sufficient context.

## What This Session Demonstrated

For the Fable 5 story (June 2026), a single HN Algolia query with `hitsPerPage=50` returned 34+ relevant stories spanning June 8-20. From titles alone I reconstructed:

| Date | Event |
|------|-------|
| June 8 | "Claude Fable 5 by Anthropic, releasing tomorrow" |
| June 9 | Official release + system card |
| June 10 | Jailbroken within 24 hours |
| June 11 | "refusing innocuous prompts" backlash |
| June 13 | US government directive to suspend access |
| June 13 | Anthropic disables Fable 5 and Mythos 5 |
| June 16 | Pulled for *everyone* over "fix this code" |
| June 16 | Anthropic at odds with White House |
| June 18 | Exec says "may return in coming days" |
| June 18 | Trump admin blocking re-release unless no jailbreaks |
| June 20 | China will have Fable 5-class model before next year |

No search engine was needed. No article was read in full. The timeline came entirely from HN story titles.

## When to Use This

- Any breaking AI/tech news story where you need a quick timeline
- Search engines are blocked (common from cloud IPs)
- The topic is HN-relevant (AI models, startups, tech policy, open source)
- You need to answer "what happened" without reading 10 articles

## Limitations

- Only works for topics that hit HN front page. Niche or non-tech topics won't have coverage.
- Story titles can be editorialized. Cross-check with the linked article when possible.
- No comment analysis by default, use `tags=comment` for that.
- Timestamps are submission time, not event time. Events that happened hours before submission will appear slightly delayed.
