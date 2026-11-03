---
name: x-algorithm-post-optimization
description: "Write X posts for the open-source xAI For You feed ranker."
version: 0.2.0
author: Hermes
metadata:
  hermes.tags: [X, Social-Media, Ranking, xAI, Algorithm]
---

# X Algorithm Post Optimization

Apply the signals from xAI's open-source For You feed ranker (github.com/xai-org/x-algorithm) to every X post or social media question you write. The ranker is a Grok-based transformer that predicts engagement probabilities per post and combines them into a single score: `Final Score = Σ (weight_i × P(action_i))`. Positive actions lift the post, negative actions bury it. This skill tells you how to write posts that maximize the positive weighted sum and avoid the negative ones.

As of the **August 13, 2026 release**, the actual production weight values are public in `home-mixer/params/param.rs`. This skill encodes the REAL constants, not guesses.

This skill does NOT replace `writing-style`. It layers on top of it. Load `writing-style` first for voice, punctuation, and the 190-char limit. Then load this skill for algorithmic optimization. Pinterest is explicitly out of scope: when the user specifies Pinterest, ignore this skill entirely and follow the Pinterest rules in `writing-style`.

## When to Use

- User asks for an X post, Twitter post, or social media post (not Pinterest).
- User asks for social media questions or engagement hooks for X.
- The "SOCIAL MEDIA QUESTIONS - 5PM" cron job runs.
- User asks to "apply the X algorithm" to a draft post.
- User asks why a post underperformed and wants a rewrite.

## Prerequisites

- Load `writing-style` first. This skill assumes the 190-char limit, no em dashes, fact-first structure, and ranked delivery are already in effect.
- No external dependencies. Pure authoring guidance.

## THE REAL WEIGHTS (from `home-mixer/params/param.rs`, Aug 13 2026 release)

These are the actual production default values. Final Score = Σ (weight × P(action)). Positive actions push up, negative actions crush.

### Positive weights (ranked by value)
| Action | Weight | Note |
|---|---|---|
| **Share via copy link** | **20.0** | THE highest positive weight. 40× a favorite. |
| **Reply** | **5.0** | Tied 2nd. |
| **Quote** | **5.0** | Tied 2nd. |
| **Share via DM** | **5.0** | Tied 2nd. |
| **Follow author** | **4.0** | |
| **Share** | **2.0** | |
| **Retweet** | **1.0** | |
| **Favorite** | **0.5** | Baseline. Lowest-differentiator positive. |
| Click | 0.4 | |
| Open link | 0.2 | |
| Photo expand | 0.05 | |
| Video open | 0.05 | |
| VQV (video quality view) | 0.05 | |
| Quoted click | 0.05 | |
| Post unexplored | 0.02 | |
| Dwell | 0.0 | Binary dwell is worth nothing alone. |
| Profile click | 0.0 | |
| Quoted VQV | 0.0 | |
| Cont dwell time | 0.004 | Continuous dwell time, per unit. |
| Cont click dwell time | 0.0 | |

### Negative weights (massive — one can wipe out many positives)
| Action | Weight |
|---|---|
| **Report** | **-234.0** |
| **Mute author** | **-58.8** |
| **Not interested** | **-43.2** |
| **Block author** | **-31.2** |
| Not dwelled | -0.02 |

### Bidirectional follow boost (NEW, huge)
`BidirectionalFollowReplyWeightBoost` = **15.0**. A reply from a user who follows you back is worth 15× the base reply weight. Replies from mutuals are the single most valuable engagement you can earn. `BidirectionalFollowDwellWeightBoost` = 0.0.

### Scoring adjustments (after the weighted sum)
1. **Author Diversity**: each post after an author's first in a batch is multiplied by `AuthorDiversityDecay` (0.5) down to `AuthorDiversityFloor` (0.25). Posting repeatedly in a short window halves each subsequent post's score.
2. **Out-of-Network Discount**: posts from accounts the viewer does NOT follow are multiplied by `OonWeightFactor` (0.75). Replies and reposts from non-followed accounts are also discounted. To reach non-followers you must be semantically retrievable by the Phoenix Two-Tower model.
3. **New-Author Boost**: posts from authors below `ColdStartImpressionThreshold` (1000 impressions) are lifted toward a target position. New accounts get a boost.
4. **VMRanker (DPP)**: after scoring, a determinantal point process (`VMRankerDppTheta` 0.65, max selected rank 150) reorders posts to reduce similarity between neighbors. Similar posts from the same author get spread apart.

## Pipeline filters that kill reach (from `home-mixer/filters/`)

**Pre-scoring (in order):**
- `DropDuplicatesFilter` — same post from multiple sources
- `CoreDataHydrationFilter` — posts whose text/metadata failed to load
- `AgeFilter` — posts older than **48 hours**
- `SelfTweetFilter` — your own posts
- `OONRetweetReplyFilter` — reposts/replies from non-followed accounts, replies with missing parent
- `OONNsfwSimclustersFilter` — SimClusters posts from adult-flagged authors (non-followed)
- `RetweetDeduplicationFilter` — repeated reposts of the same post
- `IneligibleSubscriptionFilter` — subscriber-only posts you can't access
- `PreviouslySeenPostsFilter` / `PreviouslySeenPostsBackupFilter` — already shown
- `PreviouslyServedPostsFilter` — already served this session
- `MutedKeywordFilter` — viewer's muted keywords
- `AuthorSocialgraphFilter` — blocked/muted accounts
- `VideoFilter` — video posts when request excludes video
- `TopicIdsFilter` — outside requested topics
- `NewUserMinEngagementFilter` — for new accounts, OON posts below engagement threshold
- `InventoryHoldoutFilter` — configured % of posts

**Post-selection:**
- `VFFilter` — posts visibility-filtering dropped
- `AncillaryVFFilter` — posts whose parent/quoted/reposted post was dropped
- `DedupConversationFilter` — extra branches of the same conversation

## Visibility filtering (NEW — separate from ranking)

Ranking decides ORDER. `visibility-filtering/` decides whether a post can be SHOWN AT ALL. Three answers: ALLOW, INTERSTITIAL (behind a tap-through, e.g. adult/graphic), DROP. Labels come from: `grox` (spam/adult/violence classifiers), `agatha` (account labels from blocks/reports), `bdsm` (inauthentic behavior), `user-cred-v2` (PageRank over follow/engagement graph), `media-model-proxy` + `clip` (image/video models), `abuse-enforcement-service` (suspension), `scarecrow`/`botmaker` (event rules). A post can be DROPPED entirely regardless of how well it scores. Avoid anything that triggers spam, adult, violence, or inauthentic-behavior labels.

## Procedure

1. Write the post following `writing-style` rules: 190-char hard limit, fact-first, no em dashes, no rhetorical self-answering questions, ranked best-to-worst in batches of 10.

2. Score each draft against the predicted actions. For each post, ask: which positive actions does this post likely trigger, and which negative actions does it risk?

3. Maximize the high-signal positive actions in this priority order (driven by the REAL weights):
   - **Share via copy link (20.0)** — the #1 signal. Write something a person copies and pastes to a specific friend or group. "Send this to someone who needs it" framing, or content so specific/valuable it gets forwarded. This is 40× a favorite.
   - **Reply from mutuals (5.0 × 15.0 boost = 75 effective)** — the single highest-value engagement. End with a question, a stake, or a claim that invites a reply from people who follow you back. A question the reader feels compelled to answer beats a question that answers itself.
   - **Quote (5.0) and Share via DM (5.0)** — make it quotable (self-contained, opinionated) and DM-worthy. Posts that invite additive commentary, not just agreement.
   - **Follow author (4.0)** — posts that signal "this account is worth following for more of this." Consistent angle, not one-off takes.
   - **Share (2.0) and Retweet (1.0)** — make it shareable as-is. Contrarian takes, named hypocrisy, specific numbers, and "I didn't connect this until now" patterns drive reposts.
   - **Favorite (0.5)** — the floor. Concrete, verifiable facts earn favorites. Vague hot takes do not. A post that only gets likes is leaving 40× on the table.
   - **Dwell** — continuous dwell time (0.004/unit) is the only dwell that scores. A specific number, a named event, or a contradiction in the first clause makes the reader stop scrolling. Do not front-load the punchline if the setup is what creates dwell.
   - **Click** — only if a link is present. For question posts, this is near zero and that is fine.

4. Minimize the negative actions. These are catastrophic (real weights):
   - **P(report) (-234.0)** — never. No violence, no gore, no targeted harassment. One report can nuke a post. The VFFilter removes these before they ever rank.
   - **P(mute_author) (-58.8)** — repeated low-value posts train the model to mute you. Every post should earn its slot.
   - **P(not_interested) (-43.2)** — triggered by generic AI discourse, recycled takes, "hot take" framing with no substance. Be specific or be silent. Also: do not bait-and-switch the hook; if the body doesn't deliver on the first line, users hit Not Interested.
   - **P(block_author) (-31.2)** — avoid personal attacks, name-calling, or pile-ons. Attack the pattern, not the person.

5. Apply the Author Diversity Scorer rule: `AuthorDiversityDecay` (0.5) halves each post after the first in a batch, down to a 0.25 floor. When delivering a batch, do not repeat the same angle or the same target across multiple posts. Vary the target (company, person, paper, policy), the format (question, statement, contradiction), and the domain (models, policy, hardware, agents). Space posts across the day; flag when more than 3 posts are suggested in a 4-hour window.

6. Apply the OON Scorer rule: out-of-network reach depends on the post being topically retrievable by the Phoenix two-tower model, and non-followers are discounted by `OonWeightFactor` (0.75). Use the specific named entities (company names, model names, paper titles, person names) the reader's engagement history would match. Generic "the AI industry" language is not retrievable. "Anthropic's secret tracker on Chinese users" is.

7. Apply the Muted Keyword Filter rule: avoid the most commonly muted phrases in AI discourse. "Game changer," "AI revolution," "the future of work," "it's happening," and similar clichés are both muted by users and predicted as low-value by the model. Use the specific name instead.

8. Apply the DedupConversationFilter rule: do not pile onto the same conversation thread as everyone else. If 50 accounts are posting the same take on the same news, your post adds a new angle or it gets deduped in the reader's feed. Lead with the detail no one else has connected yet.

9. Apply the Candidate Isolation rule: each post is scored on its own merits, independent of what else you post that day. Do not write a "thread" hoping post 3 benefits from post 1. Write every post as if it is the only one the reader will see, because the ranker treats it that way.

10. Use recency: `AgeFilter` removes posts older than 48 hours. For news-driven posts, post the same day the story breaks.

11. Leverage the new-author boost: accounts under 1000 impressions get lifted toward a target position. For a new account, post your best, most shareable content early, not filler.

12. Verify the character count programmatically with `len(text)` before delivering. Re-verify after every edit. The 190-char limit from `writing-style` is non-negotiable.

## Pitfalls

- **The weights ARE public now.** As of Aug 13 2026, `home-mixer/params/param.rs` contains the real production defaults. Use them. Do NOT invent values that aren't in the file, and re-check the file if the repo updates again.
- **Share via copy link is the #1 signal (20.0), not likes.** A post optimized only for favorites is leaving 40× on the table.
- **Replies from mutuals are the highest-value engagement (5.0 × 15.0 boost).** The bidirectional follow boost is the single biggest multiplier in the system.
- **Negative signals are catastrophic.** Report (-234) alone outweighs ~470 favorites. One report or mute can destroy a post's score.
- **Author diversity is a penalty, not a reward.** Posting more does not increase reach per post. It halves each subsequent post in the batch.
- **Out-of-network reach requires topic vocabulary.** Vague, clever-but-unspecific posts are not retrievable by the Two-Tower model. If the goal is new followers, use the words your target audience already engages with.
- **Ranking and visibility are separate.** A post can score perfectly and still be DROPPED by visibility filtering if it triggers a spam/adult/violence/inauthentic label. Don't risk it.
- **Do not apply this to Pinterest.** Pinterest uses a different ranking system and different character limits. The user explicitly carved out Pinterest. Respect that.
- **Do not override `writing-style`.** Voice, punctuation, no em dashes, fact-first structure, and the 190-char limit all still apply. This skill adds algorithmic layering, it does not replace the voice.
- **The cron job "SOCIAL MEDIA QUESTIONS - 5PM" uses this skill.** When that cron runs, its skills array should include `writing-style` and `x-algorithm-post-optimization`. The final Telegram message is still only the brief confirmation the prompt specifies, per the `writing-style` cron delivery discipline rules. The questions themselves go in the email attachment.

## Verification

Before delivering a batch of posts or questions, run this check in `execute_code`:

```python
from hermes_tools import read_file
# After writing the posts file, verify each post:
posts = [...]  # your drafted posts
for i, p in enumerate(posts, 1):
    n = len(p)
    flag = "OK" if n <= 190 else "OVER"
    print(f"#{i:02d} [{flag}] {n} chars: {p[:60]}...")
```

Every post must read as 190 chars or fewer, contain no em dashes, lead with a specific named entity or number, and trigger at least one of: share via copy link, reply (ideally from mutuals), quote, share via DM, retweet, favorite, dwell. If a post triggers none of those, rewrite it.
