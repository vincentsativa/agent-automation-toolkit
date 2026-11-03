---
name: x-account-strategy
description: "Strategic layer for X account growth — posting cadence, mute penalty recovery, engagement velocity, and the three-layer daily workflow. Complements x-algorithm-post-optimization (which covers individual post writing) with the account-level operating rhythm."
version: 0.1.0
author: Hermes
metadata:
  hermes.tags: [X, Social-Media, Account-Strategy, Growth, Cadence]
---

# X Account Strategy

This skill covers the **account-level operating rhythm** for X — how often to post, how much to reply, how to recover from a mute penalty, and why engagement velocity matters more than follower count. It complements `x-algorithm-post-optimization` (which covers how to write individual posts for the ranker) with the strategic layer of how to run the account day to day.

Load `x-algorithm-post-optimization` first for post-writing rules, then load this skill for cadence and recovery strategy.

## When to Use

- User asks how often to post on X.
- User asks how many replies to make per day.
- User asks why their posts aren't getting traction despite decent content.
- User asks about the mute penalty or how to recover from it.
- User asks why large accounts can post 4x/hour but they can't.
- User asks for a daily X workflow or strategy.
- User asks what P(reply) or any of the 15 algorithm signals mean.
- User asks about the relationship between follower count and algorithm performance.
- User describes a pattern of high posting volume with low engagement — this is the diagnostic trigger.

## Recommended Daily Cadence

- **3 posts** — one morning, one midday, one evening. Gives the OON Scorer enough surface area for discovery without triggering the Author Diversity penalty. A fourth is acceptable only if it genuinely adds something new.
- **10 outbound replies** — replies to other people's posts, spread across different accounts and conversations. Each must add a specific fact, a contradiction, or a named connection. Short agreement ("this") or generic takes train P(not_interested) against you.
- **Respond to everyone who replies to your posts** — community management, not outbound. Deepens thread engagement, signals conversation value, builds Follow_author signal. A post with 5 replies where you responded to all 5 is worth more than a post with 20 replies where you ghosted.

## Recommended Posting Times

Based on Sprout Social's 2026 analysis of nearly 2 billion engagements across 307,000 profiles, the peak windows for X are:

- **Mondays:** 2-3 p.m. and 5 p.m.
- **Tuesdays, Wednesdays, Thursdays:** 12-6 p.m.
- **Worst days:** Weekends and early mornings.

All times are Local Time (the user's timezone, not UTC).

### The 9 / 12 / 3 Schedule

For a 3-post daily cadence, use these specific times:

| Time | Post Type | Rationale |
|------|-----------|-----------|
| **9:00 a.m.** | Quick engagement starter / hot take | Catches the morning commute crowd. Spaced before the peak window opens. |
| **12:00 p.m. (noon)** | **Article / long-form link post** | Lunchtime scroll is prime for click-through content. Drops right as the Tue-Thu 12-6 p.m. peak opens. |
| **3:00 p.m.** | End-of-day closer / observation | Solidly inside the peak window. Catches the afternoon mental-break crowd. |

The article always goes at noon. This is non-negotiable — lunchtime is when people actually click through to read. The 9 a.m. and 3 p.m. slots are for shorter, engagement-first posts.

See `references/sprout-social-2026-x-times.md` for the full research data.

## The Three-Layer Strategy

1. **3 posts** — your own content, the surface area for discovery.
2. **10 outbound replies** — you go to them, not waiting for them to come to you. Highest-leverage action for breaking a mute penalty because it directly trains P(reply) and puts you in front of new audiences.
3. **Respond to everyone who replies to you** — deepens threads, signals conversation value, builds Follow_author.

## The Mute Penalty (P(mute_author))

P(mute_author) is a rolling average of your account's perceived value. It rises when you post too frequently without enough engagement velocity (replies, reposts, favorites per post). Once elevated, the ranker shows your posts to fewer people, which means less engagement, which reinforces the penalty.

**How to unwind it:** Drop to the 3-post, 10-reply cadence for 2-3 weeks. Every post must independently trigger at least one positive signal (reply, repost, favorite, quote, share, dwell). The average shifts as the model sees posts that actually get engagement. You earn your way out.

## What P(reply) Actually Is

P(reply) is the ranker's predicted probability that a user will reply to a given post. It is one of 15 predicted actions the Grok-based transformer estimates per candidate post. The full set:

- **Positive signals:** P(favorite), P(reply), P(repost), P(quote), P(click), P(profile_click), P(video_view), P(photo_expand), P(share), P(dwell), P(follow_author)
- **Negative signals:** P(not_interested), P(block_author), P(mute_author), P(report)

Final Score = Σ (weight_i × P(action_i)). Positive actions get positive weights, negative actions get negative weights. The higher the weighted sum, the higher the post ranks.

P(reply) is the strongest positive signal because a reply is the highest-friction engagement — it takes more effort than a like or repost. A post that drives replies signals genuine conversation value, so the model weights it heavily. This is why replying to others is the single highest-leverage action for your own account's reach: it directly trains the model that your account drives conversation.

## Engagement Velocity vs. Account Size

The same 15-signal formula applies to every account regardless of follower count. The algorithm does not know or care how many followers you have. It only sees the engagement probabilities. What changes is **engagement velocity** — the rate at which replies, reposts, and favorites arrive in the first minutes after posting.

Large accounts (100k+ followers) get 1,000+ replies in 3 minutes. The ranker sees P(reply) spiking in real time and boosts the post further. This creates a feedback loop that lets them post 4x/hour without penalty — each follower sees a different slice due to the "previously served" dedup, and the Author Diversity Scorer is per-feed, not per-account.

Smaller accounts (under 50k) do not have this velocity. Posting at high frequency without it trains P(mute_author) and P(not_interested) because each additional post with low engagement dilutes the account's average. The constraint is not account size itself — it's the engagement velocity that size enables. If a small account somehow got 1,000 replies in 3 minutes on every post, they could post 4x/hour too. That just doesn't happen.

**Do not copy what large accounts do.** Their frequency works because of their audience, not despite it.

## Diagnostic: The "Everything Wrong at Once" Pattern

This is the most common failure mode for accounts with 5k-50k followers. The user in this session had 19k followers and was doing:

- **7+ posts per day** — trained the Author Diversity Scorer to attenuate and the Mute predictor to flag.
- **30+ outbound replies per day** — high volume, low depth. P(not_interested) flagged the account as noise.
- **Zero community management** — all engagement was on other people's posts. No replies to their own commenters, so the algorithm saw low P(reply) on their own content and stopped showing it.

The result: the account was muted. The algorithm learned to predict low value because every signal said "this account broadcasts and comments everywhere but doesn't hold a conversation."

**How to diagnose this in a user's account:**
1. Ask about post volume (5+ is a red flag).
2. Ask about reply volume (20+ outbound is a red flag).
3. Ask where their engagement happens (if they can't name recent replies on their own posts, that's the biggest red flag).

The fix is always the same: cut volume in half (or more), redirect saved time to your own comment section, and let each interaction breathe.

## Warning Signs You're Overposting

- 5+ posts per day: triggers the Author Diversity penalty and trains the mute predictor.
- 20+ outbound replies per day: looks like noise. P(not_interested) catches high-volume, low-depth commenting.
- All engagement is on other people's posts, none on your own: you're running outreach without building your own surface area. Redirect time to your own comment section.

## Pitfalls

- **Cadence advice is for accounts under 50k followers.** Above that threshold, engagement velocity changes the dynamics. Do not apply the 3-post, 10-reply cadence to large accounts without adjusting for their velocity.
- **Do not confuse outbound replies with community management.** Replying to people who comment on your own posts is not the same as replying to other people's posts. Both are important but serve different purposes. Outbound drives discovery. Community management drives retention and thread depth.
- **The mute penalty is a rolling average, not a permanent ban.** It unwinds over 2-3 weeks of consistent, high-signal posting. Do not tell the user their account is permanently damaged.
- **Do not claim the algorithm has hard frequency caps.** The Author Diversity Scorer attenuates repeated author scores per feed, but there is no published "max 3 posts per day" rule. The 3-post recommendation is derived from the architecture, not from a published limit.
