---
name: trending-news-digest
description: Use when Vinny asks what's trending, on any topic.
version: 0.1.0
author: Vinny Barreca, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [news, politics, digest, research, formatting]
    related_skills: [competitor-news-monitor, writing-style]
---

# Trending News Digest Skill

Builds the daily news digest Vinny asks for, on whatever topic he names, defaulting to news and politics when he names none: today's actual stories, one bold heading per story, a blank line between every section. It composes from web_search results and cites credible outlets only. This is the format he approved on Nov 12, 2026, after rejecting a run-together week-in-review as slop.

## When to Use

- "what's trending in the news", "what's trending in news/politics today"
- "what's in the news today", "today's headlines", "what's happening in politics"
- Any "what's trending in <topic>" request: politics, AI, markets, sports, whatever he names.
- Don't use for: monitoring a named company (competitor-news-monitor), summarizing a URL or transcript he handed over (use plain web_extract or youtube-content), or a week-in-review he asked for by name.

## Topic Selection

He always names the topic when he has one. "Political stories" means every section is politics, "AI stories" means every section is AI: filter the queries, the section list, and the ranking to that beat, and do not pad it with other beats. When he names no topic, default to the general news and politics digest specified here. Section count, spacing, and format are identical either way.

## Procedure

1. Establish the real current date with `terminal(command="date")`. Sessions can start on a different day than they run, and every query below depends on the actual date. Completion: today's date known to the day.
2. Batch three `web_search` calls in one turn, built around the named topic and the live date: `<topic> news today <Month D YYYY>`, `<topic> breaking today <weekday>`, `"<Month D> <YYYY>" <topic> headlines`. When no topic was named, use the default set: `news today <Month D YYYY>`, `politics news today <weekday> Trump Democrats Congress latest`, `"<Month D> <YYYY>" breaking news headlines`. Completion: results from at least two independent major outlets.
3. Filter to stories dated today or broken today that fall inside the named topic (or the default news and politics mix when he named none). A week-old item may appear only as one line of context inside the story it belongs to. Completion: every section maps to a today item in the requested topic, or is explicitly labeled as context.
4. Rank by what concretely happened today: firings, votes, arrivals, crashes, rulings, money moving. Commentary and takes rank below events. Completion: the lead section is an event, not an opinion piece.
5. Compose to the Format Spec, then run the Verification checks before sending.

## Format Spec

- One section per story: a **bold heading line** naming the story, then a blank line, then that story's paragraphs.
- A blank line between every section, always. Sections running together with no space is the exact failure Vinny called slop. This is the core rule of the skill.
- 1 to 3 short paragraphs per story. Plain sentences, no bullet walls, no nested lists.
- First paragraph of each story states what happened; following paragraphs carry detail, numbers, and reaction.
- Numbered headings or plain bold headings both work. Spacing is what matters, not the numbering.
- When he named no topic, include at least one major non-politics story of the day: a market shock, a disaster, a big business story. When he named a topic, every section stays on that topic.
- Never use the em dash character anywhere. Use a comma, colon, semicolon, or a separate sentence.
- Telegram markdown: `**bold**` headings, no tables, links as [title](url) only when a source link is wanted.

## Sources

Credible outlets only, per vinny-constitution Article 9: wire services, established newsrooms with named journalists, official statements, government data. No SEO aggregators, no AI content farms, no unnamed-author blogs. Any claim resting on a single outlet gets opened with `web_extract` and corroborated before it becomes a section.

## Pitfalls

- Answering a "today" question with a week-in-review. The date filter is the deliverable; past-week analysis is context only.
- Answering a topic request with the default mix, or padding a named topic with stories from other beats. He named the topic, so every section is that topic.
- Writing sections without blank lines between them. Re-read the draft as rendered before sending.
- Running queries without the live current date, which silently pulls stale results.
- Treating a search snippet as sufficient evidence for a quoted claim. Open the source first.
- Padding with takes and framing when there are more concrete events than fit. Cut commentary before cutting stories.

## Verification

Before sending, confirm all five: every section has a bold heading with a blank line above it; every section is a today story or labeled context; every section is inside the topic he named, or the default news and politics mix when he named none; no em dash characters exist anywhere in the reply; at least one query used the live current date. Count the sections and confirm the spacing by re-reading the draft as it will render.
