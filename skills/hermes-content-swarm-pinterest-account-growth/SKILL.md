---
name: pinterest-account-growth
description: Pinterest cadence, index lag, reactivating dormant accounts.
tags: []
related_skills: [social-board-seo, phantombyte-publishing]
toolsets: [web]
---

# Pinterest Account Growth & Re-Activation Strategy

Strategy-level rules for growing a Pinterest account and reactivating one with
dormant history. Covers cadence, the long-tail compounding asset, buyer intent,
and where to learn Pinterest SEO. Board-level metadata/keyword work lives in the
`social-board-seo` skill (pinned), this skill is the growth-strategy layer on top.

## Re-Activated (Dormant) Accounts

The canonical case: an account that had big views ~7 years ago, was abandoned, and
came back. Vinny's PhantomByte account: ~10M views/mo ~7 years ago, abandoned ~2019,
revived March 2026, still getting views from 2019 pins today.

- **Old history does NOT auto-prioritize you.** After long dormancy Pinterest treats
  you as a re-activation risk. Flooding new pins right away = throttle/shadowban risk.
- **The old authority is still real and helps**, the crawler knows the account, so new
  pins index/push faster than a brand-new account. But it unlocks only after you show
  consistent fresh activity again.
- **Cadence: 3-5 fresh pins/day.** Below ~2/day loses momentum; above ~10/day on a
  re-activated account trips spam filters.
- **Ramp:** weeks 1-2 = 2-3/day; weeks 3-6 = 3-5/day; after ~6 clean weeks can push
  5-10/day if saves/impressions hold or grow.
- **Consistency beats volume, always.** Daily 3 >> weekend burst of 30.

## Index Lag & The Long Tail (the compounding asset)

- **~4-month index lag.** A pin posted today doesn't get pushed until ~4 months out.
  Worst for fresh/low-authority accounts; better for accounts with history.
- **Decade-long tail.** Unlike Google (which buries old content), Pinterest keeps paying
  back on old pins for years. This is the core long-game advantage: plant once, compound.
- **Practical math:** posting now compounds before most accounts' pins even index.
  Post 3-5/day now; don't touch the strategy while it cooks.

## Buyer Intent (why it's a real funnel channel)

- Pinterest is a **visual search engine with purchase intent**, not a social feed.
  Saves = "I'm going to build/buy this later", a warm signal.
- Buyers + decade tail + transferable Google-style SEO skill = a rare combo worth
  treating as a first-class funnel channel (feeds the Sovereign AI Stack funnels).

## The "Pinterest Bible" (comprehensive framework)

Foundation:
1. One board = one keyword/search intent. No mashing topics.
2. Title front-loads keyword (left-to-right crawl, first 3-4 words matter).
3. Description first 50 chars = search snippet; put primary keyword there.
4. Board description = landing page for that keyword (SEO copy, not caption).
5. Claim/confirm website domain → unlocks rich pins + analytics.

Content engine:
6. Fresh images, not just repins (repins don't move the algorithm the same way).
7. 2:3 vertical (~1000x1500px), text overlay near-required for mobile feed.
8. Alt text is indexed, keyword in alt like image SEO for Google.
9. Every pin targets one keyword across title/description/alt/hashtags.

Cadence:
10. 3-5 fresh pins/day steady.
11. Multiple pins per article OK (different images/angles = more keyword surfaces),
    don't spam the same image.

Search signals:
12. Hashtags = keyword tags, not IG-style discovery. Keep relevant; irrelevant hurts.
13. No keyword-stuffing. Human copy that happens to include the keyword.

Long game:
14. 4-month lag is real, and so is the decade tail.
15. Consistency IS the strategy. Beaten per-pin competitors by never stopping.

One-line summary: "Pinterest is a search engine, not social media. Treat every board and
every pin like a Google landing page, post a little every day, let the decade tail compound."

## Best Sources (validated by search)

- **Tier 1 (authority):** Pinterest's own Creator Academy / Fundamentals, 
  `create.pinterest.com`. Pinterest teaching Pinterest; algorithm changes land here first.
  This is the primary source text, not blog rehashes.
  - **How to fetch these official docs** (both are JS-rendered React; scrapling fails,
    use browser): see `references/fetching-official-pinterest-docs.md`. Note the old
    `help.pinterest.com/.../pinterest-seo` URL is a 404, use Pin performance & distribution instead.

  ## Board Audit & Restructure (catch-all → keyword-focused boards)

  When asked to audit/optimize a board URL, diagnose the catch-all problem and split into
  one-keyword-per-board, see `references/board-audit-and-restructure.md` for the full
  workflow, the ordered launch plan, and a worked PhantomByte example with copy-paste-ready
  board metadata. Key points: bucket pins by intent, flag duplicate pins as the FIRST action
  item (spam risk), launch boards 1-2 at a time (never all at once), validate demand via
  `pinterest.com/search/pins/?q=<topic>` result density, and email the deliverable + one-line
  Telegram note (Vinny works from email).
- **Tier 2 (proven operators):** Tailwind (`tailwindapp.com`), Madpin Media
  (`madpinmedia.com`).
- **Tier 3 (case studies):** Medium "hit X monthly views on Pinterest" posts, real numbers.

## Behavioral Note (for Vinny)

When Vinny asks "what is a good resource/source online," he wants an ACTUAL external
source (a URL, a site, a person to learn from), NOT a plan for organizing/filing existing
info. Leading with a "knowledge base structure" answer to a "give me a source" question
reads as dismissive. Name the real source first, then (only if relevant) offer to save it.

## Behavioral Note: Direct Answers to Account Questions (Aug 2026)

When Vinny asks a direct question about his account (e.g. "what should my next board be?",
"what boards do I have?"), answer the question directly and briefly FIRST. State the verdict
in one or two sentences, then STOP. Do NOT bury the answer in keyword rationale, cluster
analysis, a recap of your process, or a trailing "want me to...?" offer. He is furious when
a simple question gets a rambling answer with the actual answer buried at the bottom. Give
the answer, then only if he asks, add the reasoning. Session proof: "what should my next
board be?" got a long keyword-dump answer instead of a one-line verdict, and he exploded
("ANSWER THE FUCKING QUESTION I ASKED YOU"). The board itself (AI Security) was right; the
presentation was wrong.

## Daily Social Media Posts Cron (10-post Pinterest document)

Vinny's recurring daily cron produces a document of 10 Pinterest titles + descriptions (ranked best to worst, #1 strongest, #10 most niche; evergreen post at #10). This is a distinct operational workflow from the strategy layer above. Full workflow, board slugs, board-assignment mapping, and verification pattern are in `references/daily-social-posts-cron.md`. Key points:

- Read stories from `~/Desktop/TODAYS DATA FILES/` (`20-AI-News-Stories-<date>.md` is primary).
- First visit Vinny's five Pinterest boards to avoid duplicate topics.
- Assign each post to exactly ONE board by topic: AI agents → ai-agents-automation-guide; AI tools/business/productivity → ai-tools-for-business-productivity-2026; AI for developers/coding/APIs → ai-for-developers-programming-ai-tutorials; AI security/agent security/prompt injection/sandboxing/least-privilege → agent-security-prompt-injection-sandboxing; everything else → ai-news-machine-learning-emerging-tech (default).
- MANDATORY: programmatic `len()` check on every title (max 100) and description (max 500) from a script, do not trust your own annotation. Titles/descriptions land at 450-520 when drafted naturally; iterate until all pass.
- Deliver: write `social-media-posts-<date>.txt` to the data folder, email as attachment to hello@phantom-byte.com (subject `Bill: Daily Social Media Posts For X and Pinterest`), notify Telegram with ONLY a brief "Email sent with today's social media posts" confirmation. No post content in Telegram.

### Board labels are Vinny's picker (Aug 2026)
Vinny reads the `BOARD:` labels in the text file to decide which posts to publish and
place into boards himself. His articles anchor the Main AI News board. So when the
day's data allows, spread posts across the non-news boards (AI Agents, AI Tools,
AI for Developers, Agent Security) so he has candidates to fill them. The day's data
is the hard constraint, never force a topic that has no story. Keep labels clean and
consistent so he can scan and pick fast.

### Adding a new board (Aug 2026)
When Vinny says he added a board, wire it into the CRON PROMPT itself (board list +
topic mapping + label), not just this reference file. The cron job loads `writing-style`,
NOT this skill, so it never sees the reference file. Session proof: the Agent Security
board was already in `references/daily-social-posts-cron.md` but missing from the cron
prompt, so tomorrow's run would have ignored it. Update the cron prompt via
`cronjob action=update` on job `9d9b840ce8e2` (DAILY Pinterest Posts 5:45PM).

## Pin Copy for a Store or Product Page (on-demand)

When asked for a Pinterest title and description promoting a specific URL, write the copy from the live page, not from what the store was believed to sell.

1. **Read the page first, and render it.** Gumroad storefront and profile roots are JS-rendered: `scrapling extract get` and `scrapling extract fetch` both come back with the display name only, and `curl` returns a shell with no product data. Open the URL in the browser and read `document.body.innerText` to get the real product names and prices, then ground the description in what is actually listed.
2. **Title: hard cap 100 characters, primary keyword in the first 3 to 4 words.** Pinterest crawls left to right.
3. **Description: hard cap 500 characters, primary keyword inside the first 50.** Name the concrete deliverables and product names from the page, put the URL at or near the end, and close with 3 or 4 topical hashtags. No keyword-stuffing: a human sentence that happens to carry the keyword indexes better.
4. **Verify both with a programmatic `len()` before delivering, never by eye.** Drafts naturally land over the cap, the 500-char description most often, so print `len(title)` and `len(description)` from a script and iterate until both pass. Report the counts with the copy.
5. Image, alt text, and hashtag mechanics are in the "Pinterest Bible" section above; do not restate them per pin.

## Pitfalls

- **Do not conflate this growth-strategy layer with board SEO.** The board keyword/title/
  description mechanics live in `social-board-seo` (pinned). This skill is cadence, index
  lag, reactivation, and sources.
- **Don't advise flooding a dormant account**, the re-activation risk throttle is real.
- **Don't treat Pinterest like a social feed**, it's a search engine with purchase intent.
