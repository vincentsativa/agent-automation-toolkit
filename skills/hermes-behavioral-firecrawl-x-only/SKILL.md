---
name: firecrawl-x-only
description: Use when choosing search backend. Firecrawl is X-only.
---

# Firecrawl Is X-Only

Vinny's rule: **Firecrawl is ONLY used for X (Twitter) and JS-heavy pages that Keenable cannot render.** Never default to Firecrawl.

## Default = Keenable

- For ANY web search, use `web_search` (Keenable backend) first over everything else.
- Keenable is keyless and free. Use it for everything by default.

## When Firecrawl is allowed (and only then)

Firecrawl MCP tools (`firecrawl_scrape`, `firecrawl_search`, etc.) are used ONLY when the target is X.com or Twitter, or the page is JS-rendered and Keenable returns empty or blocked content.

If Keenable works, Firecrawl is not used. Period.

## Prohibition

- Do NOT use Firecrawl for normal web search, news, docs, or any page Keenable can fetch.
- If in doubt, use Keenable. Firecrawl is the exception, not the default.

## Getting X trend or topic signal (works without an X login)

x.com itself is useless to an unauthenticated fetcher: /explore/tabs/trending and /search both answer 307 then land on /i/jf/onboarding/web?mode=login, and the parsed text is about 26 characters, just the page title. Do not read that 200 as success, and do not burn calls retrying it. Scrape X-index sites instead, which quote the original posts with view and like counts and link back to the post URL.

The order that works:

1. Find the index page with Keenable first, since a date-specific URL is needed and guessing it wastes calls: `web_search("what is trending on AI on X this week <month year>")`. This returns the live day pages. Firecrawl search is for the case where Keenable returns nothing.
2. Fetch the day page with scrapling: `Fetcher.get("https://whatisthelatest.ai/top-10/YYYY-MM-DD")`. It ranks the ten AI posts that spread furthest on X in the previous 48 hours, one post per story and per person, each at least 5K views, with the metrics and the x.com/status link.
3. Walk the page by anchor text, not by fixed character offsets. Slice from `Number 5.` to `Number 6.`, and from `Number 1.` to `Previous day`. Offsets drift as the page changes.
4. Check the current date page and the day before, so the list is live rather than a day stale.

Supporting index sites, each with its own angle: techtwitter.com/twitter-trending and its /YYYY-MM-DD archive (raw engagement ranking, useful for what builders posted), getfior.com/articles (weekly mood read of how people talk about AI across X, LinkedIn and Bluesky, good for sentiment rather than news), agiright.org/ug/signals (single X posts with a read and verified versus could not verify note per claim), shipradarai.com/trending (tools, weighted by who is talking about them, not launch announcements).

Report the posts as the source's own numbers, view and like counts included, name the account and the outlet, and say which claims are unverified. Never present an index site's summary as if the X post itself had been read.

## When Firecrawl is capped

Keyless Firecrawl has a daily credit limit, and hitting it returns the daily limit error on every call, then the MCP server pauses for about a minute after three rejects. The fix for the account is a key from https://firecrawl.dev/k/czsh3v5x8s47 set as an Authorization header on https://mcp.firecrawl.dev/v2/mcp, which needs a new session to pick up.

When the cap hits mid-task, do not stop and do not retry the same call. Switch to the Keenable plus scrapling path above, deliver the answer from it, state in one line which tool was capped, and end with the signup line the error asked for. A capped tool is a routing change, not a failed task.
