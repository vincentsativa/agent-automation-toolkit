---
name: x-algorithm-post-optimization
description: "Write X posts tuned to the open For You feed signals."
version: 0.3.15
author: Hermes
metadata:
  hermes.tags: [X, Twitter, Social-Media, Ranking, Algorithm]
---

# X Algorithm Post Optimization

Write X (Twitter) posts and non-Pinterest social posts that align with the engagement signals the open-source xAI For You feed algorithm (`github.com/xai-org/x-algorithm`) actually scores, filters, and ranks on. This skill does NOT cover Pinterest. Use it any time the user asks for an X post, tweet, thread, or "social post" unless they explicitly say it is for Pinterest.

The algorithm is a Grok-based transformer with NO hand-engineered relevance features. It predicts probabilities for engagement actions and combines them into a weighted score. As of the **August 13, 2026 release**, the actual weight values are public, so this skill encodes the REAL constants, not guesses. Re-verified against `home-mixer/params/param.rs`, `vm-ranker/params.rs`, `xai-value-model/`, the pipeline source, `home-mixer/filters/`, and `visibility-filtering/` at repo HEAD on **November 11, 2026** (`last sync 2026-11-10T16:00:31Z`, commit f06f45a, two commits 660cd74 and f06f45a past 3b6919f). NO ACTION WEIGHT MOVED: `weights_mut` in `xai-value-model/weights.rs` is still 30 entries, `home-mixer/params/param.rs` grew from 225 to 237 params (twelve additions, no removals), `vm-ranker/params.rs` has NO diff and stays 59 params, and `home-mixer/params/config.rs` and `README.md` have NO diff (see "November 11, 2026 sync"). The only reach-relevant move is that `NewUserMinEngagementFilterUseRatio` flipped `false` to `true` and `NewUserMinEngagementThreshold` moved `0.0` to `0.004`. The prior sync, November 7, 2026 (`last sync 2026-11-06T16:00:45Z`, commit 3b6919f, four commits b508926, 021afa4, 2e2295b and 3b6919f past b220448). SEVEN ACTION WEIGHTS MOVED, the first such move since October 13 2026, and a THIRTIETH scored action landed: `FavoriteWeight` `0.66` to `0.708`, `ClickWeight` `0.3` to `0.274`, `ShareWeight` `2.0` to `2.118`, `VideoOpenWeight` `0.02` to `0.0`, `ContDwellTimeWeight` `0.006` to `0.0075`, `ContClickDwellTimeWeight` `0.4` to `0.385`, `NotInterestedWeight` `-52.272` to `-53.07`, plus new `GrokAnalyzeWeight` (`0.0`). `weights_mut` in `xai-value-model/weights.rs` is now 30 entries and `weighted_terms` in `xai-value-model/scoring.rs` is `[(&'static str, f64); 30]`. `home-mixer/params/param.rs` grew from 218 to 225 params and `vm-ranker/params.rs` from 58 to 59, and `PhoenixAggregationType` moved to `DENSE_WITH_LONG_DWELL_HOME_EXCURSION` with `EnableHomeExcursionScores` flipped `false` to `true` (see "November 7, 2026 sync"). The prior sync, November 3, 2026 (`last sync 2026-11-02T16:00:39Z`, commit b220448, one commit past 9106e9f), changed NO action weight VALUE: `weights_mut` was still 29 entries, `vm-ranker/params.rs` still 58 params, with one gated-off video-carousel risk knob, `AdsBlenderType` reverted `"slot_spread"` to `"multi_risk"` (ad accounting only), and `xai-value-model/scoring.rs` refactored the weighted sum into a named `weighted_terms` array with no change to any coefficient. Before that, October 31, 2026 (`last sync 2026-10-30T22:59:56Z`, commit 9106e9f, three commits 606b254, 7fef3ba and 9106e9f past 5ed7963), also changed NO action weight VALUE: its only action-weight-family change was a RENAME, `ReactWithVideoWeight` to `PostVideoWeight` (still `0.0` in both files), alongside an ads blender default, a page-logging default, two new video-carousel scoring knobs, and `VIDEO_CAROUSEL_EXTRA_CANDIDATES` migrating out of `config.rs` into `param.rs` as `VideoCarouselExtraCandidates`. Before that, October 28, 2026 (`last sync 2026-10-27T16:00:37Z`, commit 5ed7963), also changed NO action weight: it DELETED `Brazil2026ElectionFilter`, appended two gated-off scorers, and added a page-decode/page-RL param family. Before that, October 23, 2026 (`last sync 2026-10-23T16:00:34Z`, commit 6258a15), also changed NO action weight: it added four params, flipped `EnableFairShareRanking` `false` to `true`, and inserted a gated-off `NewUserSoftNsfwFilter`. Before that, October 20, 2026 (`last sync 2026-10-20T16:00:34Z`, commit 7f2ca2b), changed NO action weight either: it added eight params, removed `EnablePhoenixRetrievalFallback`, and appended a gated-off `FairShareRankingFilter`. The prior sync, October 16, 2026 (`last sync 2026-10-16T16:00:32Z`, commit 862a123), added a `ZeroFavCodivertFilter` and turned on the video-carousel dedupe knobs. Before that, October 14, 2026 (`last sync 2026-10-13T16:00:30Z`, commit 17c96bf), moved FOUR action weights, the first such move since Oct 6 2026: `FavoriteWeight` `0.5` to `0.66`, `VideoOpenWeight` `0.07` to `0.02`, `ContDwellTimeWeight` `0.004` to `0.006`, and `NotInterestedWeight` `-47.52` to `-52.272`, all in `home-mixer/params/param.rs` while `vm-ranker/params.rs` kept the old values. Also new: `ReactWithVideoWeight` (`0.0`, both files), `PhoenixOonRepliesRootOnly` (`false`), `EnableVideoCarouselAuthorDedupe` (`false`), `VideoCarouselSemanticIdDedupeLevels` (`0`), `TopicDppEnabled` (`false`), an `AncestorVideoFilter` in the post-selection lineup, and a widened `VideoFilter`. See "Params added or changed since Aug 13 2026".

## When to Use

- User asks for "an X post", "a tweet", "a thread", or a "social post" and does NOT say Pinterest.
- A cron job (IronPulse, BlogWatcher, Larry Weekly News, tutorial writing, ghostwriter terminal, article blaster) generates X/social posts as part of its output.
- User asks to "optimize this post for X" or "make this tweet rank better".
- User asks for LinkedIn, Reddit, or Facebook post copy (the same multi-signal engagement logic transfers).

## Prerequisites

- None. This is a reasoning skill, not a script. No env vars, no installs.
- Load `phantom-byte-writing-style` for voice rules when writing for Vinny.
- Load `vinny-constitution` for governance rules when operating in Vinny's sessions.

## How to Run

Apply the procedure below inline when generating any X/social post. There is no script to invoke. For cron jobs that already produce X posts, attach this skill to the job's `skills` array so it loads before the job prompt runs.

## THE REAL WEIGHTS (from `home-mixer/params/param.rs`, Aug 13 2026 release)

These are the actual production default values. Final Score = Σ (weight × P(action)). Positive actions push up, negative actions crush.

### Positive weights (ranked by value)
| Action | Weight | Note |
|---|---|---|
| **Share via copy link** | **20.0** | THE highest positive weight. About 28.2× a favorite at the Nov 7 2026 favorite weight of 0.708. |
| **Reply** | **5.0** | Tied 2nd. |
| **Quote** | **5.0** | Tied 2nd. |
| **Share via DM** | **5.0** | Tied 2nd. |
| **Follow author** | **4.0** | |
| **Share** | **2.118** | Was 2.0 through Nov 3 2026; raised to 2.118 on Nov 7 2026, which is 3.0× a favorite. |
| **Retweet** | **1.0** | |
| **Favorite** | **0.708** | Was 0.5 through Oct 9 2026 and 0.66 from Oct 13 2026; raised to 0.708 on Nov 7 2026. |
| Click | 0.274 | Was 0.4 through Sept 25 2026 and 0.3 from Sept 30 2026; lowered to 0.274 on Nov 7 2026. |
| Open link | 0.2 | |
| Photo expand | 0.05 | |
| Dwell | 0.05 | Re-enabled Aug 25 2026. Was 0.0. |
| Quoted click | 0.05 | |
| Post unexplored | 0.015 | Was 0.02 through Oct 3 2026; cut to 0.015 on Oct 6 2026 in `home-mixer/params/param.rs` (vm-ranker still 0.02). |
| **Video open** | **0.0** | Was 0.07 through Oct 9 2026 and 0.02 from Oct 13 2026; cut to `0.0` on Nov 7 2026, so a video open scores nothing at all today. |
| VQV (video quality view) | 0.0 | |
| Profile click | 0.0 | |
| Quoted VQV | 0.0 | |
| Cont dwell time | 0.0075 | Continuous dwell time, per unit. Was 0.004 through Oct 9 2026 and 0.006 from Oct 13 2026; raised to 0.0075 on Nov 7 2026. |
| Cont click dwell time | 0.385 | Was 0.0 through Sept 25 2026 and 0.4 from Sept 30 2026; cut to 0.385 on Nov 7 2026. |
| Post video | 0.0 | Renamed from `ReactWithVideoWeight` on October 31, 2026 (`PostVideoWeight`, key `rust_home_mixer_post_video_weight`, in both `param.rs` and `vm-ranker/params.rs`); default `0.0`, so it scores nothing today. |
| Grok analyze | 0.0 | NEW on Nov 7 2026 (`GrokAnalyzeWeight`, key `rust_home_mixer_grok_analyze_weight`, in both `param.rs` and `vm-ranker/params.rs`). The thirtieth scored head, and the knob to watch. |

### Negative weights (massive, one can wipe out many positives)
| Action | Weight |
|---|---|
| **Report** | **-234.0** |
| **Mute author** | **-58.8** |
| **Not interested** | **-53.07** | Was -47.52 through Oct 9 2026 and -52.272 from Oct 13 2026; deepened to -53.07 on Nov 7 2026. |
| **Block author** | **-31.2** |
| Not dwelled | -0.02 |

### Bidirectional follow boost (NEW, huge)
`BidirectionalFollowReplyWeightBoost` = **15.0**. A reply from a user who follows you back is worth 15× the base reply weight. Replies from mutuals are the single most valuable engagement you can earn. `BidirectionalFollowDwellWeightBoost` = 0.0.

### Params added or changed since Aug 13 2026 (verified November 11, 2026)

**November 11, 2026 sync (`last sync 2026-11-10T16:00:31Z`, commit f06f45a, two commits 660cd74 and f06f45a past 3b6919f, checked November 11, 2026), NO ACTION WEIGHT MOVED, twelve params added, two new-user engagement defaults flipped on.** Every action weight VALUE in `home-mixer/params/param.rs` is byte-identical to its Nov 7 2026 value: `FavoriteWeight` `0.708`, `ClickWeight` `0.274`, `ShareWeight` `2.118`, `VideoOpenWeight` `0.0`, `ContDwellTimeWeight` `0.0075`, `ContClickDwellTimeWeight` `0.385`, `NotInterestedWeight` `-53.07`, `GrokAnalyzeWeight` `0.0`, `ShareViaCopyLinkWeight` `20.0`, `ReplyWeight` `5.0`, `QuoteWeight` `5.0`, `ShareViaDmWeight` `5.0`, `FollowAuthorWeight` `4.0`, `RetweetWeight` `1.0`, `DwellWeight` `0.05`, `PhotoExpandWeight` `0.05`, `QuotedClickWeight` `0.05`, `PostUnexploredWeight` `0.015`, `PostVideoWeight` `0.0`, `ProfileClickWeight` `0.0`, `QuotedVqvWeight` `0.0`, `VqvWeight` `0.0`, `ReportWeight` `-234.0`, `MuteAuthorWeight` `-58.8`, `BlockAuthorWeight` `-31.2`, `NotDwelledWeight` `-0.02`, `BidirectionalFollowReplyWeightBoost` `15.0`, `BidirectionalFollowDwellWeightBoost` `0.0`. `weights_mut` in `xai-value-model/weights.rs` is still `[(&'static str, &mut f64); 30]`, so no new scored action exists. `home-mixer/params/param.rs` grew from 225 to 237 params (twelve additions, no removals). `vm-ranker/params.rs` has NO diff at all this sync, still 59 params with its older values. `home-mixer/params/config.rs` has NO diff (`FEED_MODULE_SLOTS` still `5`, `RESULT_SIZE` still `35`, `TOP_K_CANDIDATES_TO_SELECT` still `50`, carousel min/max still `3`/`5`, `MAX_POST_AGE` still `48 * 60 * 60`) and `README.md` has NO diff.

Changed defaults in `home-mixer/params/param.rs`:

| Param | Old (Nov 7 2026) | New (Nov 11 2026) |
|---|---|---|
| `NewUserMinEngagementFilterUseRatio` | `false` | `true` |
| `NewUserMinEngagementThreshold` | `0.0` | `0.004` |
| `AdsBlenderType` | `"multi_risk"` | `"slot_spread"` |
| `EnableVideoCarouselMediumRiskFilter` | `false` | `true` |
| `EnableVideoCarouselSeenFilter` | `false` | `true` |

**`NewUserMinEngagementFilter` is now live with a ratio threshold, and that is the one change in this sync that touches reach.** `NewUserMinEngagementFilterUseRatio` flipped `true` and `NewUserMinEngagementThreshold` moved `0.0` to `0.004`, so the filter now keeps or drops a candidate on a RATIO against the viewer's own engagement baseline rather than an absolute count, cutting out-of-network posts from new or resurrected accounts whose ratio falls under `0.004`. New accounts posting out-of-network content see a stricter bar than before. The filter's own account-age window (`NewUserMinEngagementFilterMaxAccountAgeSecs`) is unchanged.

New params in `home-mixer/params/param.rs` (quoted exactly, type and trailing default):

| Param | Type | Value |
|---|---|---|
| `EnableShuffledHistoryRetrieval` | bool | `false` |
| `VMRankerSendPostTopics` | bool | `false` |
| `PostTopicsMaxCandidates` | usize | `200` |
| `PostTopicsTimeoutMs` | u64 | `80` |
| `RecentViewsRows` | usize | `64` |
| `RecentViewsSequenceLength` | u32 | `256` |
| `EnableUnderTheHoodFrame` | bool | `false` |
| `EnableJetfuelFrameGrokbotSuggestedTasks` | bool | `false` |
| `JetfuelFrameGrokbotSuggestedTasksFatigueHours` | u32 | `6` |
| `EnableVideoCarouselHeaderIcon` | bool | `false` |
| `EnableVideoCarouselTakeFromFeed` | bool | `false` |
| `VideoCarouselNotInterestedWeight` | f64 | `0.0` |

**New retrieval source, new viewer-interest hydrator, new VMRanker inputs, all inert or additive.** `home-mixer/sources/shuffled_history_phoenix_source.rs` (`ShuffledHistoryPhoenixSource`) is added to the Phoenix source vec and gated by `EnableShuffledHistoryRetrieval` (`false`), so a shuffled-history retrieval path exists but does not run. `home-mixer/query_hydrators/recent_views_query_hydrator.rs` (`RecentViewsQueryHydrator`, fed by `RecentViewsRows` `64` and `RecentViewsSequenceLength` `256`) is inserted after `RetrievalSequenceQueryHydrator`, so recent views are now a hydrated viewer signal. `VMRankerSendPostTopics` (`false`) with `PostTopicsMaxCandidates` (`200`) and `PostTopicsTimeoutMs` (`80`) threads post topics into the vm-ranker request only when it is on and `query.recent_views` is non-empty. The For You pipeline also gained a `JetfuelDirectFrameSource` backed by a new `JetfuelClient`; the Grok Bot suggested-tasks frame is gated by `EnableJetfuelFrameGrokbotSuggestedTasks` (`false`).

**Video carousel risk and seen filters are now ON, the carousel itself is still OFF.** `EnableVideoCarouselMediumRiskFilter` and `EnableVideoCarouselSeenFilter` both flipped to `true`, and `home-mixer/filters/video_carousel_filter.rs` gained `EnableVideoCarouselTakeFromFeed` (`false`): when it is on, the carousel pool starts at `VideoCarouselPosition` (`6`) minus one instead of at `RESULT_SIZE` (`35`), and posts the carousel shows are removed from the main feed so nobody sees the same video twice. `EnableVideoCarousel` is still `false`, so none of it runs in production. One consequence worth recording: with `EnableVideoCarouselHighRiskFilter` and `EnableVideoCarouselMediumRiskFilter` now BOTH `true`, an unlabeled carousel candidate (`brand_safety_verdict` `None`) is dropped, where the Nov 3 2026 note described it as kept while only one gate was on.

**`ShadowTrafficPhoenixClusterRates` grew from four clusters to nine**, adding `Experiment24Fou` through `Experiment28Fou` at `0.3` each alongside `Experiment18Fou`, `Experiment19Fou`, `Experiment22Fou` and `Experiment23Fou`. More scoring variants are being compared against production. Not an action weight.

**Filters were refactored onto `FilterResult::partition` with no behavior change.** `video_filter.rs`, `fav_holdout_filter.rs`, `inventory_holdout_filter.rs`, `fair_share_ranking_filter.rs`, `new_user_soft_nsfw_filter.rs`, `new_user_min_engagement_filter.rs` and `oon_nsfw_simclusters_filter.rs` were all rewritten as `FilterResult::partition(candidates, |c| !drop(c))`, and `oon_nsfw_simclusters_filter.rs` gained a test. Same predicates, same order, same memberships. No filter was added to or removed from the pre-scoring or post-selection vecs, and the scorers vec is still `[PhoenixScorer, ImmersiveVideoScorer, VMRanker, PageDecodeRerankScorer, PageRlExplorationScorer]`.

**Visibility filtering: no verdict, reason, or country-list change.** `LimitedEngagementReason` is still FOURTEEN variants, `TombstoneReason` still five, `SCALA_FILES` still 7, and the five country lists are unchanged. `visibility-filtering/params.rs` only reworked DDG impression logging (`Experiments::serving` now returns a null impressor unless `crate::config::logs_ddg_impressions()`), and `treatment.rs` was split into `treatment/thrift.rs`, `treatment/rpc.rs` and `treatment/proto.rs`. None of it moves an organic action weight.

**November 7, 2026 sync (`last sync 2026-11-06T16:00:45Z`, commit 3b6919f, four commits b508926, 021afa4, 2e2295b and 3b6919f past b220448, checked November 7, 2026), SEVEN ACTION WEIGHTS MOVED AND A THIRTIETH SCORED ACTION LANDED.** This is the first action-weight move since October 13 2026 and the largest one yet. `weights_mut` in `xai-value-model/weights.rs` is now `[(&'static str, &mut f64); 30]` and `weighted_terms` in `xai-value-model/scoring.rs` is `[(&'static str, f64); 30]`, because `grok_analyze` was added as a scored head. `home-mixer/params/param.rs` grew from 218 to 225 params (seven additions, no removals); `vm-ranker/params.rs` grew from 58 to 59 (the same `GrokAnalyzeWeight` only, and it still carries the older `FavoriteWeight` `0.5`, `ClickWeight` `0.3`, `ShareWeight` `2.0`, `VideoOpenWeight` `0.07`, `ContDwellTimeWeight` `0.004`, `ContClickDwellTimeWeight` `0.4` and `NotInterestedWeight` `-47.52`).

Changed action weights in `home-mixer/params/param.rs`:

| Param | Old (Nov 3 2026) | New (Nov 7 2026) |
|---|---|---|
| `FavoriteWeight` | `0.66` | `0.708` |
| `ClickWeight` | `0.3` | `0.274` |
| `ShareWeight` | `2.0` | `2.118` |
| `VideoOpenWeight` | `0.02` | `0.0` |
| `ContDwellTimeWeight` | `0.006` | `0.0075` |
| `ContClickDwellTimeWeight` | `0.4` | `0.385` |
| `NotInterestedWeight` | `-52.272` | `-53.07` |

New scored action in BOTH `home-mixer/params/param.rs` and `vm-ranker/params.rs`: `GrokAnalyzeWeight` (`f64`, `0.0`, key `rust_home_mixer_grok_analyze_weight`). It is wired as `("grok_analyze", apply(scores.grok_analyze_score, weights.grok_analyze))` in `xai-value-model/scoring.rs`, with a new `grok_analyze_score: Option<f64>` field carried through `xai-value-model/phoenix_scores.rs`, `xai-value-model/proto.rs`, `home-mixer/scorers/value_model.rs` and `vm-ranker/scoring/value_model.rs`. Default `0.0`, so it scores nothing today; when it moves, asking Grok to analyze a post becomes a scored action.

**What the seven moves change for copy.** The hierarchy the guidance above rests on is intact: copy link (`20.0`) is still 28.2× a favorite, replies and quotes and DMs are still `5.0`, the mutual-reply boost is still `15.0` (a mutual's reply is still 75.0 effective), and the negative family still dwarfs everything (`Report` `-234.0`, `MuteAuthor` `-58.8`, `BlockAuthor` `-31.2`). Three things did move in a way that matters. First, a favorite (`0.708`) now OUTWEIGHS the whole click path: click `0.274` plus click-dwell `0.385` is `0.659`, so opening a post and reading the opened content is worth less than one like. Second, plain `ShareWeight` rose to `2.118`, nearly three favorites, so a repost-ready post is worth more than it was. Third, `VideoOpenWeight` is now `0.0`, so a video open earns nothing at all and posting video for that reason is pointless until the knob moves.

Changed defaults in `home-mixer/params/param.rs`:

| Param | Old (Nov 3 2026) | New (Nov 7 2026) |
|---|---|---|
| `PhoenixAggregationType` | `"DENSE_WITH_LONG_DWELL"` | `"DENSE_WITH_LONG_DWELL_HOME_EXCURSION"` |
| `EnableHomeExcursionScores` | `false` | `true` |
| `ShadowTrafficPhoenixClusterRates` | `vec!["Experiment18Fou:0.3", "Experiment19Fou:0.3"]` | the same two plus `"Experiment22Fou:0.3"` and `"Experiment23Fou:0.3"` |

`PhoenixAggregationType` now names the same home-excursion aggregation the shadow traffic has carried since October 20 2026, and `EnableHomeExcursionScores` is on, so retrieval now aggregates on long-dwell-with-home-excursion behaviour rather than plain long dwell. Four shadow clusters now carry 30% of traffic each, up from two, so more scoring variants are being compared against production than before. Neither is an action weight.

New params in `home-mixer/params/param.rs` (quoted exactly, type and trailing default):

| Param | Type | Value |
|---|---|---|
| `GrokAnalyzeWeight` | f64 | `0.0` |
| `EnableAdsHistoryXdcCacheWrite` | bool | `true` |
| `AdsHistoryCacheTtlSecs` | u64 | `300` |
| `EnableVideoCarouselCtrModel` | bool | `false` |
| `VideoCarouselCtrModelName` | String | `"lr_v8_search_video_1_2026-11-03_no_high_risk"` |
| `EnableVideoCarouselSeenFilter` | bool | `false` |
| `VideoCarouselVideoContinuationWeight` | f64 | `0.0` |

**Video carousel gained a CTR model and a seen-filter, and is still gated off.** `home-mixer/util/video_carousel.rs` `CarouselScoring` now carries `video_continuation_weight` and an `Option<Arc<CtrModel>>`; when a CTR model is present `score()` returns `model.score(video_open_score, video_embedding)` and skips the linear sum entirely, and otherwise adds the term `video_continuation_weight × video_open_score × home_video_continuation_secs`. Both new weights default to `0.0`/`false`. `home-mixer/filters/video_carousel_filter.rs` now also skips any candidate where `video_carousel::was_seen(&query.seen_carousel_video_ids, candidate)`, fed by a new `VideoCarouselSeenQueryHydrator` (`home-mixer/query_hydrators/video_carousel_seen_query_hydrator.rs`) gated by `EnableVideoCarouselSeenFilter` and backed by a `redis-global.video-carousel-seen-cache` client that falls back to a no-op on failure. A new `VideoCarouselCtrModelQueryHydrator` plus `home-mixer/util/video_carousel_ctr_model.rs` and a `vm-ranker/carousel_model.rs` back the CTR path. `EnableVideoCarousel` is still `false`, so none of it runs in production.

**Ads history cache write is new and on.** `EnableAdsHistoryXdcCacheWrite` (`true`) and `AdsHistoryCacheTtlSecs` (`300`) back a reworked `home-mixer/ads/following_ad_blender.rs` and `served_ad_history_cache_side_effect.rs`. Ad accounting only.

**Pipeline vecs are unchanged.** Pre-scoring, post-selection and scorers are all identical to November 3 2026, `home-mixer/params/config.rs` has NO diff (`FEED_MODULE_SLOTS` still `5`, `RESULT_SIZE` still `35`, `TOP_K_CANDIDATES_TO_SELECT` still `50`, carousel min/max still `3`/`5`, `MAX_POST_AGE` still `48 * 60 * 60`), and `README.md` has NO diff this sync. `self_tweet_filter.rs` and `previously_served_posts_filter.rs` were refactored onto `FilterResult::partition` with behaviour unchanged (both diffs are almost entirely new tests), and `home-mixer/candidate_pipeline/` gained a `performance_params.json` (`224` lines) plus `performance_tests.rs` (`647` lines) that benchmark existing stages without changing a score.

**Visibility filtering: `LimitedEngagementReason` gained a FOURTEENTH variant, and the verdict model was reshaped.** `visibility-filtering/models/verdict.rs` added `DynamicProductAd` (wire string `dynamic_product_ad`) after `CommunityTweetViewerRemoved`, so the enum now reads fourteen variants. `Verdict` gained a top-level `Fosnr(Decided<Notice>)` variant and `Verdict::Shown`'s `notice` field was renamed `label_interstitial`; the `Notice` enum lost its `LabelInterstitial` variant and its `is_whole_verdict`/`limited_engagement_reason` helpers, replaced by `kind()`. A new `VerdictAction` enum (`Allow`, `Drop`, `Tombstone`, `Interstitial`, `LimitedEngagement`, `TweetInterstitial`, `SoftIntervention`, `Appealable`) plus `rules/action_kind.rs` plumbing lets `Verdict::decided()` report which action fired and which rule id decided it. `visibility-filtering/params.rs` changed only to wire `LabelCacheSwitches` from the reloadable feature-switch engine into `safety-label-source`, which also grew a `dragonfly.rs` (`2566` lines) and reworked `remote.rs`/`source.rs`. `TombstoneReason` is unchanged at five, the five country lists are unchanged, and no new `DropReason` or `FilteredReason` variant landed. None of it moves an organic action weight.


**November 3, 2026 sync (`last sync 2026-11-02T16:00:39Z`, commit b220448, one commit past 9106e9f, checked November 3, 2026), NO ACTION WEIGHT MOVED, one gated-off carousel risk knob added, `AdsBlenderType` reverted.** Every action weight VALUE in `home-mixer/params/param.rs` is byte-identical to its Oct 31 2026 value (`FavoriteWeight` `0.66`, `ReplyWeight` `5.0`, `QuoteWeight` `5.0`, `ShareViaCopyLinkWeight` `20.0`, `ClickWeight` `0.3`, `ContClickDwellTimeWeight` `0.4`, `ContDwellTimeWeight` `0.006`, `VideoOpenWeight` `0.02`, `PostUnexploredWeight` `0.015`, `NotInterestedWeight` `-52.272`, `ReportWeight` `-234.0`, `MuteAuthorWeight` `-58.8`, `BlockAuthorWeight` `-31.2`, `BidirectionalFollowReplyWeightBoost` `15.0`, and all the rest), and `weights_mut` in `xai-value-model/weights.rs` is still `[(&'static str, &mut f64); 29]`, so no new scored action exists anywhere. `home-mixer/params/param.rs` grew from 217 to 218 params (one addition, no removals). `vm-ranker/params.rs` has NO diff at all this sync (still 58 params, still the older `FavoriteWeight` `0.5` and `VideoOpenWeight` `0.07`). `home-mixer/params/config.rs` has NO diff (`FEED_MODULE_SLOTS` still `5`, `RESULT_SIZE` still `35`, `TOP_K_CANDIDATES_TO_SELECT` still `50`, `MAX_POST_AGE` still `48 * 60 * 60`). `README.md` has NO diff this sync.

Changed default in `home-mixer/params/param.rs`:

| Param | Old (Oct 31 2026) | New (Nov 3 2026) |
|---|---|---|
| `AdsBlenderType` | `"slot_spread"` | `"multi_risk"` |

Ad blending is back on the multi-risk blender after one sync on slot spread. Ad accounting only, not an organic ranking signal.

New param in `home-mixer/params/param.rs` (quoted exactly, type and trailing default):

| Param | Type | Value |
|---|---|---|
| `EnableVideoCarouselMediumRiskFilter` | bool | `false` |

**`VideoCarouselFilter` now also drops medium-risk carousel candidates, and drops unlabeled ones whenever either risk gate is on.** The inline predicate became a `match` on `candidate.brand_safety_verdict`: `Some(BrandSafetyVerdict::HighRisk)` is kept only while `EnableVideoCarouselHighRiskFilter` (`true`) is off, `Some(BrandSafetyVerdict::MediumRisk)` is kept only while `EnableVideoCarouselMediumRiskFilter` (`false`) is off, any other verdict is kept, and `None` is kept only when BOTH gates are off. That is a real change beyond the new knob: with the high-risk filter on and the medium-risk filter off, an UNLABELED carousel candidate (`brand_safety_verdict` `None`) is now dropped, where the old predicate kept it. `EnableVideoCarousel` is still `false`, so the carousel does nothing in production, and none of this touches organic ranking.

**`xai-value-model/scoring.rs` refactor: `compute_weighted_score` is now a sum over a named `weighted_terms` array.** The 29 per-head terms moved into `pub fn weighted_terms(...) -> [(&'static str, f64); 29]` and `compute_weighted_score` maps it and sums. Every coefficient, the `vqv_eligible` branch, and the `weights.reply_weight_for(candidate)` and `weights.dwell_weight_for(candidate)` calls are unchanged, so the score arithmetic is identical. `vm-ranker/scoring/value_model.rs` and `home-mixer/scorers/vm_ranker.rs` changed alongside it (the vm_ranker scorer now carries the named terms), and `home-mixer/scorers/vm_ranker_request.rs` plus `home-mixer/models/candidate.rs` picked up small field plumbing. Nothing here adds a weight or changes an existing one.

**Visibility filtering: a new `Deletion` enum and `Evaluation::Deleted` variant, no verdict-reason change.** `visibility-filtering/models/verdict.rs` added `Evaluation::Deleted(Deletion)` with `Deletion { Deleted, BounceDeleted }`, and both `verdict()` and `into_verdict()` map `Deleted` to the same `NOT_FOUND` verdict as `NotFound`. `LimitedEngagementReason` is unchanged at THIRTEEN variants and `TombstoneReason` is unchanged at five, so no post becomes droppable or limited for a new named reason. `visibility-filtering/params.rs` and `visibility-filtering/params/client_switches.rs` have NO diff. The rest of the sync is visibility-filtering hydration and `verdict_gate.rs` work plus a large Phoenix model and Python pass; the pre-scoring vec, post-selection vec and scorers vec are all unchanged this sync.

**October 31, 2026 sync (`last sync 2026-10-30T22:59:56Z`, commit 9106e9f, three commits 606b254, 7fef3ba and 9106e9f past 5ed7963, checked October 31, 2026), NO ACTION WEIGHT MOVED, but `ReactWithVideoWeight` IS RENAMED `PostVideoWeight`.** Every action weight VALUE in `home-mixer/params/param.rs` is byte-identical to its Oct 28 2026 value (`FavoriteWeight` `0.66`, `ReplyWeight` `5.0`, `QuoteWeight` `5.0`, `ShareViaCopyLinkWeight` `20.0`, `ClickWeight` `0.3`, `ContClickDwellTimeWeight` `0.4`, `ContDwellTimeWeight` `0.006`, `VideoOpenWeight` `0.02`, `PostUnexploredWeight` `0.015`, `NotInterestedWeight` `-52.272`, `ReportWeight` `-234.0`, `BidirectionalFollowReplyWeightBoost` `15.0`, and all the rest), and `weights_mut` in `xai-value-model/weights.rs` is still `[(&'static str, &mut f64); 29]`, so no new scored action exists anywhere. `home-mixer/params/param.rs` grew from 212 to 217 params (five additions, no removals). `vm-ranker/params.rs` is still 58 params and its only diff is the same rename. `README.md` has NO diff this sync.

**`ReactWithVideoWeight` is now `PostVideoWeight`.** The param and its feature-switch key both moved: `ReactWithVideoWeight` / `rust_home_mixer_react_with_video_weight` became `PostVideoWeight` / `rust_home_mixer_post_video_weight`, value still `0.0`, in BOTH `home-mixer/params/param.rs` and `vm-ranker/params.rs`. The score field moved with it: `react_with_video_score` is now `post_video_score` in `xai-value-model/phoenix_scores.rs`, `xai-value-model/proto.rs`, `xai-value-model/scoring.rs` (`compute_weighted_score` now does `apply(scores.post_video_score, weights.post_video)`) and `home-mixer/scorers/value_model.rs`, and the `ValueModelWeights` struct field `react_with_video` is now `post_video`, with a `("post_video", self.post_video)` entry in the serialization map. `weights_mut` still lists 29 heads. Still `0.0`, so it scores nothing in production today. When reading older commits or notes, search for `PostVideoWeight`, not `ReactWithVideoWeight`.

Changed defaults in `home-mixer/params/param.rs`:

| Param | Old (Oct 28 2026) | New (Oct 31 2026) |
|---|---|---|
| `EnablePageLogging` | `false` | `true` |
| `AdsBlenderType` | `"multi_risk"` | `"slot_spread"` |
| `EnableAdsBrandSafetyVerdictV2` | `true` | `false` |
| `EnableVideoCarouselHighRiskFilter` | `false` | `true` |

New params in `home-mixer/params/param.rs` (quoted exactly, type and trailing default):

| Param | Type | Value |
|---|---|---|
| `PageDecodeRewardHead` | u32 | `0` |
| `VideoCarouselEmbeddingVersion` | String | `"v8_search_1"` |
| `VideoCarouselOpenTimesImmersiveDwellWeight` | f64 | `0.0` |
| `VideoCarouselWeightedScoreWeight` | f64 | `0.0` |
| `VideoCarouselExtraCandidates` | usize | `30` |

**`VideoCarouselExtraCandidates` replaces the `config.rs` constant.** `home-mixer/params/config.rs` lost `pub const VIDEO_CAROUSEL_EXTRA_CANDIDATES: usize = 30;` and the same `30` now lives in `param.rs` as the runtime param `VideoCarouselExtraCandidates`. `config.rs` otherwise has NO change: `FEED_MODULE_SLOTS` still `5`, `RESULT_SIZE` still `35`, `TOP_K_CANDIDATES_TO_SELECT` still `50`, `MAX_POST_AGE` still `48 * 60 * 60`.

**Video carousel ranking is now a four-term `CarouselScoring` struct, carousel still gated off.** `home-mixer/util/video_carousel.rs` gained `CarouselScoring { video_open_weight, immersive_vqv_weight, open_times_immersive_dwell_weight, weighted_score_weight }`, built by `CarouselScoring::from_query`, and `home-mixer/filters/video_carousel_filter.rs` now passes `&CarouselScoring::from_query(query)` into `select_videos` instead of two loose weights. The score is `video_open_weight × video_open_score + immersive_vqv_weight × immersive_vqv_score + open_times_immersive_dwell_weight × video_open_score × immersive_dwell_time + weighted_score_weight × candidate.weighted_score`. The two new terms are `0.0`, so today the carousel still ranks on `VideoCarouselVideoOpenWeight` (`1.0`) times Phoenix `video_open_score` plus `VideoCarouselImmersiveVqvWeight` (`0.0`). A new `needs_immersive_scores()` skips the immersive path unless one immersive term is non-zero. `EnableVideoCarousel` is still `false`, so the carousel does nothing in production. `EnableVideoCarouselHighRiskFilter` flipped `true`, but it only bites inside the still-off carousel: carousel-extra candidates with `brand_safety_verdict` `BrandSafetyVerdict::HighRisk` are excluded before `select_videos`.

**Ads work is the bulk of the sync and none of it touches organic ranking.** `AdsBlenderType` moved `"multi_risk"` to `"slot_spread"`, backed by new `home-mixer/ads/slot_spread_blender.rs` (272 lines), `home-mixer/ads/least_movement_blender.rs` (485 lines), `home-mixer/ads/neighbours.rs` (267 lines) and `home-mixer/ads/health_metrics.rs` (131 lines), with `multi_risk_blender.rs` cut by 124 lines. `EnableAdsBrandSafetyVerdictV2` flipped back to `false`. Ad accounting only.

**`EnablePageLogging` is now `true`** (was `false`), and `PageDecodeRewardHead` (`0`) is new. The page-decode and page-RL gates `EnablePageDecodeRerank` and `EnablePageRlExploration` are still `false`, so both page scorers remain inert.

**Pipeline lineup and filters unchanged.** Pre-scoring vec, post-selection vec, and scorers vec are identical to Oct 28 2026 (`scorers` is still `[phoenix_scorer, immersive_video_scorer, vm_ranker, PageDecodeRerankScorer, PageRlExplorationScorer]`). The only changed file under `home-mixer/filters/` is `video_carousel_filter.rs`, and that is the `CarouselScoring` refactor above. No filter added or removed.

**Visibility filtering: no verdict, reason, or country-list change.** `visibility-filtering/params.rs` has NO diff (`SCALA_FILES` still 7, five country lists unchanged) and `visibility-filtering/models/verdict.rs` has NO diff (`LimitedEngagementReason` still THIRTEEN variants, `TombstoneReason` still five). `visibility-filtering/params/client_switches.rs` is a rework carrying the same switch keys (`age_verification_*`, `community_tweet_viewer_removed_limited_actions_rules_enabled`, `freedom_of_speech_not_reach_*`, `media_visibility_treatments_*`, `stale_tweet_limited_actions_rules_enabled`). What did change: `NotificationKind` in `visibility-filtering/models/mod.rs` grew from two variants to five, adding `Mention`, `Reply` and `MediaTagged` alongside `Follow` and `FollowRequestAccepted`, `models/viewer.rs` gained `ClientSwitch` / `ClientSwitchSet`, and `rules/` was reworked (`levels.rs`, `engine.rs`, `tweet_rules.rs`, plus a new `golden_corpus/post_notifications.rs`). None of it moves an organic action weight.

**October 28, 2026 sync (`last sync 2026-10-27T16:00:37Z`, commit 5ed7963, two commits 2f25214 and 5ed7963 past 6258a15, checked October 28, 2026), NO ACTION WEIGHT CHANGED, but `Brazil2026ElectionFilter` IS DELETED and two scorers are appended.** Every action weight in `home-mixer/params/param.rs` is byte-identical to its Oct 23 2026 value (`FavoriteWeight` `0.66`, `ReplyWeight` `5.0`, `QuoteWeight` `5.0`, `ShareViaCopyLinkWeight` `20.0`, `ClickWeight` `0.3`, `ContClickDwellTimeWeight` `0.4`, `ContDwellTimeWeight` `0.006`, `VideoOpenWeight` `0.02`, `PostUnexploredWeight` `0.015`, `NotInterestedWeight` `-52.272`, `ReportWeight` `-234.0`, `BidirectionalFollowReplyWeightBoost` `15.0`, and all the rest), and `weights_mut` in `xai-value-model/weights.rs` is still `[(&'static str, &mut f64); 29]`, so no new scored action exists anywhere. `home-mixer/params/param.rs` grew from 202 to 212 params (eleven additions, one removal) and `vm-ranker/params.rs` from 51 to 58 (seven additions, all inert). `home-mixer/params/config.rs` has NO diff: `FEED_MODULE_SLOTS` still `5`, `RESULT_SIZE` still `35`, carousel min/max still `3`/`5`, `VIDEO_CAROUSEL_EXTRA_CANDIDATES` still `30`, `MAX_POST_AGE` still `48 * 60 * 60`.

**`Brazil2026ElectionFilter` removed from For You.** `home-mixer/filters/brazil_2026_election_filter.rs` (297 lines) was DELETED, its `pub mod` line was removed from `home-mixer/filters/mod.rs`, and it was removed from the pre-scoring vec in `phoenix_candidate_pipeline.rs`, so `AuthorSocialgraphFilter` is now followed directly by `VideoFilter`. The README's October 26th 2026 entry reads: "With the 2026 Brazilian elections over, we have removed `Brazil2026ElectionFilter` from For You. Posts from the accounts it covered are no longer filtered out because of it." Do NOT cite this filter as a live For You signal any more.

**Two scorers appended to the scorers vec.** The vec in `phoenix_candidate_pipeline.rs` now reads `[phoenix_scorer, immersive_video_scorer, vm_ranker, PageDecodeRerankScorer, PageRlExplorationScorer]`. `home-mixer/scorers/page_decode_rerank_scorer.rs` (290 lines) is gated by `EnablePageDecodeRerank` (`false`) and reorders a pool of `PageDecodePoolN` (`200`) candidates through `PageDecodeSteps` (`64`) decode steps at `PageDecodeTemperature` (`0.0`), passing the EXISTING action weights to a `RankingScoreWeights` struct (`favorite`, `reply`, `retweet`, `click`, `profile_click`, `vqv`, `share`, `quote`, `cont_dwell_time`, `not_interested`, `report`, `not_dwelled`, `min_video_duration_ms`). `home-mixer/scorers/page_rl_exploration_scorer.rs` (285 lines) is gated by `EnablePageRlExploration` (`false`) and samples a Plackett-Luce order at `PageRlExplorationTemperature` (`0.2`) over `PageRlExplorationTopK` (`64`). Both gates are off, so production ranking is unchanged today, and neither adds a weight.

Changed defaults in `home-mixer/params/param.rs`:

| Param | Old (Oct 23 2026) | New (Oct 28 2026) |
|---|---|---|
| `NewUserSoftNsfwFilterMaxAccountAgeSecs` | `86400` | `604800` |
| `VMRankerSendDebiasInputs` | `false` | `true` |
| `ShadowTrafficPhoenixClusterRates` | `vec!["Experiment18Fou:0.3".to_string()]` | `vec!["Experiment18Fou:0.3".to_string(), "Experiment19Fou:0.3".to_string()]` |

New params in `home-mixer/params/param.rs` (quoted exactly, type and trailing default):

| Param | Type | Value |
|---|---|---|
| `EnablePageLogging` | bool | `false` |
| `PageLogTtlSeconds` | u64 | `3600` |
| `EnablePageDecodeRerank` | bool | `false` |
| `PageDecodePoolN` | u32 | `200` |
| `PageDecodeSteps` | u32 | `64` |
| `PageDecodeTemperature` | f64 | `0.0` |
| `EnablePageRlExploration` | bool | `false` |
| `PageRlExplorationTemperature` | f64 | `0.2` |
| `PageRlExplorationTopK` | usize | `64` |
| `NewUserSoftNsfwFilterMaxScoringSeqLength` | u64 | `100` |
| `EnableVideoCarouselHighRiskFilter` | bool | `false` |

Removed param in the same file: `ThunderClusterId` (String, was `"amp"`, key `rust_home_mixer_thunder_cluster_id`).

New params in `vm-ranker/params.rs` (all inert at their defaults):

| Param | Type | Value |
|---|---|---|
| `UserDebiasEnabled` | bool | `false` |
| `UserDebiasAlpha` | f64 | `0.0` |
| `UserDebiasClipLogit` | f64 | `2.0` |
| `UserDebiasHeads` | String | `""` |
| `UserDebiasHeadAlpha` | String | `""` |
| `UserDebiasHeadClipLogit` | String | `""` |
| `UserDebiasMaxArtifactAgeSecs` | f64 | `3600.0` |

`NewUserSoftNsfwFilter` gained a second gate. It still requires `EnableNewUserSoftNsfwFilter` (`false`) and a non-topic `ForYou` request from an account younger than `NewUserSoftNsfwFilterMaxAccountAgeSecs` (**now `604800`, i.e. 7 days**, up from `86400`), and it now also requires the request's `scoring_sequence` length to be below `NewUserSoftNsfwFilterMaxScoringSeqLength` (`100`, with `0` meaning no limit) via `below_max_scoring_seq_length`. Default off, so production behavior is unchanged today.

`VideoCarouselFilter` gained a high-risk drop. When `EnableVideoCarouselHighRiskFilter` (`false`) is on, carousel-extra candidates whose `brand_safety_verdict` is `BrandSafetyVerdict::HighRisk` are excluded before `select_videos`. `EnableVideoCarousel` is still `false`, so the carousel still does nothing in production.

**README added two behavioral notes that matter for post copy.** October 13th 2026: "Phoenix retrieval is now also trained to surface posts that people read all the way through." October 8th 2026: "The Phoenix ranking model now does a better job of estimating how long you'll spend on each post." Read-through and time-on-post are now supervised training targets, which raises the value of a post that holds a reader to the last line instead of one that front-loads a hook and then trails off.

**Visibility filtering: no verdict, reason, or country-list change.** `SCALA_FILES` is still 7, the five country lists are unchanged, `LimitedEngagementReason` is unchanged at THIRTEEN variants, and `TombstoneReason` is unchanged at five. `LimitedActionType` (still 26 variants, `Reply` through `ViewPostEngagements`) moved out of `params/limited_actions_policy.rs` into `models/verdict.rs`, `Evaluation::into_verdict` became `#[cfg(test)]`, and `params.rs` plus `params/client_switches.rs` were replumbed from `StatsReceiverExt` to a `Metrics` handle with no switch semantics changed. New files: `visibility-filtering/verdict_gate.rs` (467 lines, a gRPC gate that runs a case file against a live VF service), `visibility-filtering/ingress.rs` (260 lines), and `visibility-filtering/rules/defaults.rs`. The bulk of the sync is an `abuse-enforcement-service` rework (`action_control.rs`, `safety_checks.rs`, `confidence.rs`) plus Phoenix model work (page-decode and page-RL heads, `value_heads.py`, `follow_data_end.py`, the `gen_recs`/`sid_retrieval` config families deleted), none of which moves an organic action weight.

**October 23, 2026 sync (`last sync 2026-10-23T16:00:34Z`, commit 6258a15, three commits 989fb91, 07d159b and 6258a15 past 7f2ca2b, checked October 24, 2026), NO ACTION WEIGHT CHANGED, but `EnableFairShareRanking` FLIPPED ON.** Every action weight in `home-mixer/params/param.rs` is byte-identical to its Oct 13 2026 value (`FavoriteWeight` `0.66`, `ReplyWeight` `5.0`, `QuoteWeight` `5.0`, `ShareViaCopyLinkWeight` `20.0`, `ClickWeight` `0.3`, `ContClickDwellTimeWeight` `0.4`, `ContDwellTimeWeight` `0.006`, `VideoOpenWeight` `0.02`, `NotInterestedWeight` `-52.272`, `ReportWeight` `-234.0`, and all the rest), `vm-ranker/params.rs` has NO diff at all this sync, and `weights_mut` in `xai-value-model/weights.rs` is still 29 entries, so no new scored action exists anywhere. `home-mixer/params/param.rs` grew from 198 to 202 params: four additions, no removals. `README.md` had no diff this sync.

New params in `home-mixer/params/param.rs` (quoted exactly, type and trailing default):

| Param | Type | Value |
|---|---|---|
| `EnableRecentSearchQueriesHydration` | bool | `false` |
| `EnableNewUserSoftNsfwFilter` | bool | `false` |
| `NewUserSoftNsfwFilterMaxAccountAgeSecs` | u64 | `86400` |
| `EnableAdsFunnelTrace` | bool | `true` |

Changed defaults in the same file:

| Param | Old (Oct 20 2026) | New (Oct 23 2026) |
|---|---|---|
| `EnableFairShareRanking` | `false` | `true` |
| `EnableVideoCarouselCandidatesLogging` | `false` | `true` |
| `ShadowTrafficPhoenixClusterRates` | `vec![]` | `vec!["Experiment18Fou:0.3".to_string()]` |

**`EnableFairShareRanking` is now ON, so `FairShareRankingFilter` is LIVE in the default For You lineup.** This is the one behavioral change that matters for reach this sync. The filter still sits LAST in the pre-scoring vec (after `FavHoldoutFilter`) and still allocates each `served_type` group a proportional share of the `PhoenixScoresResultSize` budget (`2800`) by largest-remainder rounding, dropping the overflow. Practical effect: no single retrieval source can fill the result set, so a post's discovery now depends more on how many distinct retrieval paths find it than on volume from one path. It is still inert when `query.has_cached_posts`, when `query.scoring_sequence` is `None`, or when the Phoenix ranker kill-switch decider is enabled.

**New `NewUserSoftNsfwFilter` inserted into pre-scoring, between `CoreDataHydrationFilter` and `AgeFilter`.** `home-mixer/filters/new_user_soft_nsfw_filter.rs` (154 lines) is gated by `EnableNewUserSoftNsfwFilter` (`false`), only on `RequestType::ForYou` requests that are not topic requests, and only while the viewer's own account is younger than `NewUserSoftNsfwFilterMaxAccountAgeSecs` (`86400`, i.e. 24 hours). When on, it drops any candidate where `in_network == Some(false)` AND `soft_nsfw == Some(true)`: out-of-network posts carrying the soft-NSFW label are withheld from day-one accounts. It is fed by a new `home-mixer/candidate_hydrators/new_user_soft_nsfw_label_hydrator.rs` (`NewUserSoftNsfwLabelHydrator`, 270 lines) which hydrates `soft_nsfw` from the VF safety-label client. Default off, so production behavior is unchanged today.

**New `RecentSearchQueriesQueryHydrator`.** `home-mixer/query_hydrators/recent_search_queries_query_hydrator.rs` (122 lines) plus `home-mixer/clients/recent_search_queries_store_client.rs` (`RecentSearchQueriesStoreClient` / `ProdRecentSearchQueriesStoreClient` / `MockRecentSearchQueriesStoreClient`) are added to the query-hydrator vec after `UserInstalledAppsQueryHydrator`. Gated by `EnableRecentSearchQueriesHydration` (`false`); the prod constructor falls back to the mock client with a warning if the store is unavailable. This is a new viewer-interest input, not a ranking weight change.

**New ads funnel tracing, on by default.** `EnableAdsFunnelTrace` is `true`, backed by `home-mixer/side_effects/funnel_trace_side_effect.rs` (233 lines). Ad accounting and logging only, not organic ranking. A `scored_stats_side_effect.rs` (60 lines) also landed.

**`ShadowTrafficPhoenixClusterRates` now shadows 30% of traffic to `Experiment18Fou`.** The `ShadowTrafficPhoenixClusterAggregationTypes` value is unchanged (`vec!["Experiment16Fou:DENSE_WITH_LONG_DWELL_HOME_EXCURSION".to_string()]`), so the shadow aggregation still names `Experiment16Fou` while the shadow rate names `Experiment18Fou`. Worth watching: a shadow cluster is where a new scoring variant is being compared against production before it gets a weight.

**`home-mixer/params/config.rs` has NO diff this sync.** `FEED_MODULE_SLOTS` is still `5`, `RESULT_SIZE` still `35`, carousel min/max still `3`/`5`, `VIDEO_CAROUSEL_EXTRA_CANDIDATES` still `30`, `MAX_POST_AGE` still `48 * 60 * 60`.

**Scorers vec unchanged: `[PhoenixScorer, ImmersiveVideoScorer, VMRanker]`.** `EnableVideoCarousel` is still `false`, so `ImmersiveVideoScorer` and `VideoCarouselFilter` remain inert. Post-selection is still `VFFilter, AncillaryVFFilter, AncestorVideoFilter, DedupConversationFilter, VideoCarouselFilter`.

**Visibility filtering: `LimitedEngagementReason` gained a THIRTEENTH variant, `NonCompliant`, and notification filtering is new.** `visibility-filtering/models/verdict.rs` now reads `NonCompliant, ConversationControl, ReadonlyViewer, BlockedViewer, RootAuthorBlockedViewer, StaleTweet, CommunityTweetHidden, CommunityTweetMemberRemoved, CommunityTweetCommunityNotFound, CommunityTweetCommunityDeleted, CommunityTweetCommunitySuspended, CommunityTweetViewerRemoved, LocalTweet`; `NonCompliant` maps to the wire string `non_compliant` and is the fallback reason for emergency dynamic labels. `TombstoneReason` is unchanged at five variants. New files: `visibility-filtering/filter_notifications.rs` (697 lines) filters `Follow` and `FollowRequestAccepted` notifications against `SafetyLevel::NotificationsFollow` and `SafetyLevel::NotificationsWriterV2` and returns `vf_pb::NotificationDropReason`; `visibility-filtering/result_label.rs`; `visibility-filtering/pinned.rs`; `visibility-filtering/rules/author_rules.rs`; `visibility-filtering/hydration/store/key_origin.rs`. `filter_notifications.rs` plus `visibility-filtering-client/notifications.rs` mean visibility filtering now also governs whether a follow notification is DELIVERED, which is a separate surface from ranking. `visibility-filtering/params/client_switches.rs` changed one line: `limited_actions_policies` now chains `.in_language(language)`, so limited-action prompt copy is language-matched. `SCALA_FILES` stays 7 (`age_verification.yml`, `community_tweet.yml`, `country_specific_nsfw_content_gating.yml`, `freedom_of_speech_not_reach.yml`, `media_visibility_treatments.yml`, `soft_nsfw.yml`, `stale_tweet.yml`), the country lists are unchanged, and `visibility-filtering/params.rs` only lost dead test helpers (`codes`, `CountryLists::from_codes`). The bulk of the sync is an `abuse-enforcement-service` rework (a new `head_guard.rs`, `action_control` levels, sliding windows) plus Phoenix model work, none of which moves an organic action weight.

**Syncs from October 9, 2026 through October 20, 2026 are archived in `references/sync-archive.md`.** None of them contradicts the tables above. The only action-weight move in that window is already reflected in them: the October 13, 2026 move of `FavoriteWeight` `0.5` to `0.66`, `VideoOpenWeight` `0.07` to `0.02`, `ContDwellTimeWeight` `0.004` to `0.006` and `NotInterestedWeight` `-47.52` to `-52.272`. Still live from that window: `FairShareRankingFilter` (added October 20 2026, switched ON October 23 2026), `AncestorVideoFilter` (added October 13 2026), the widened `VideoFilter` that also drops a quote of a video post, `EnablePageLogging` `true`, and the gated-off page scorers plus video carousel.
**Syncs from October 3, 2026 back through September 25, 2026 are archived in `references/sync-archive.md`.** None of them left a value that contradicts the tables above; the only action-weight move in that window was `PostUnexploredWeight` `0.02` to `0.015` on October 6, 2026, already reflected in the table.

### Scoring adjustments (after the weighted sum)
1. **Author Diversity**: each post after an author's first in a batch is multiplied by `AuthorDiversityDecay` (0.5) down to `AuthorDiversityFloor` (0.25), gated by `EnableAuthorDiversity` (true). These params now live in `vm-ranker/params.rs`; the values are unchanged. Posting repeatedly in a short window halves each subsequent post's score.
2. **Out-of-Network Discount**: posts from accounts the viewer does NOT follow are multiplied by `OonWeightFactor` (0.75). Topic requests use `TopicOonWeightFactor` (0.5). Replies and reposts from non-followed accounts are also discounted when `EnableOonRescoreForInNetworkRepliesRetweets` (true) applies. To reach non-followers you must be semantically retrievable by the Phoenix Two-Tower model. Note the new-viewer case: a viewer under `NewUserAgeThresholdSecs` (0) with at least `NEW_USER_MIN_FOLLOWING` (5) follows gets `NewUserOonWeightFactor` (0.00001) instead.
3. **New-Author Boost**: posts from authors below `ColdStartImpressionThreshold` (**200** impressions as of Sept 30 2026, down from 1000) are lifted toward a target position, now under Thompson sampling (`EnableColdStartThompsonSampling` true, was false), with the lift allowed as high as position ratio `LowImpressionsMaxPositionRatio` 0.97 (was 0.85). Eligibility also widened: `ColdStartFollowerCap` is 50000 (was 1000) and `ColdStartMaxPostAgeSecs` is 7200 (was 172800). Far more accounts now qualify for the cold-start lift, and a brand-new account should expect its first posts to be pushed near the top of the feed for a window of up to two hours after posting.
4. **VMRanker (DPP)**: after scoring, a determinantal point process (`DppEnabled` true, `DppTheta` 0.65, `DppMaxSelectedRank` 150, in `vm-ranker/params.rs`; these were named `VMRankerDppTheta` and `VMRankerDppMaxSelectedRank` before Sept 25 2026) reorders posts to reduce similarity between neighbors. Similar posts from the same author get spread apart.

## Pipeline filters that kill reach (from `home-mixer/filters/`)

This is the exact order in the Phoenix For You candidate pipeline (`home-mixer/candidate_pipeline/phoenix_candidate_pipeline.rs`, verified November 11, 2026, commit f06f45a; the filter vecs are unchanged since the October 28, 2026 check). Pre-scoring reads `DropDuplicatesFilter, ZeroFavCodivertFilter, CoreDataHydrationFilter, NewUserSoftNsfwFilter, AgeFilter, SelfTweetFilter, OONRetweetReplyFilter, OONNsfwSimclustersFilter, RetweetDeduplicationFilter, IneligibleSubscriptionFilter, PreviouslySeenPostsFilter, PreviouslySeenPostsBackupFilter, PreviouslyServedPostsFilter, ViewerMutedKeywordFilter, AuthorSocialgraphFilter, VideoFilter, TopicIdsFilter, NewUserMinEngagementFilter, InventoryHoldoutFilter, FavHoldoutFilter, FairShareRankingFilter`. `Brazil2026ElectionFilter` was REMOVED from this vec on October 26, 2026 (the filter file is deleted), so `AuthorSocialgraphFilter` now hands straight to `VideoFilter`. `ZeroFavCodivertFilter` is gated off by `ViewerZeroFavCodivertIsTreatment` (`false`); `NewUserSoftNsfwFilter` (added Oct 23 2026, between `CoreDataHydrationFilter` and `AgeFilter`) is gated off by `EnableNewUserSoftNsfwFilter` (`false`); `FairShareRankingFilter` is now ON because `EnableFairShareRanking` flipped to `true` on Oct 23 2026. The `VideoFilter` behavior changed Oct 13 2026, its position did not. Post-selection reads `VFFilter, AncillaryVFFilter, AncestorVideoFilter, DedupConversationFilter, VideoCarouselFilter`; the last entry is gated off by `EnableVideoCarousel` (`false`). The scorers vec is `[PhoenixScorer, ImmersiveVideoScorer, VMRanker, PageDecodeRerankScorer, PageRlExplorationScorer]`, with `ImmersiveVideoScorer` inert unless the carousel is enabled and both page scorers gated off by `EnablePageDecodeRerank` and `EnablePageRlExploration` (`false`).

**Pre-scoring (in this order):**
- `DropDuplicatesFilter`, same post from multiple sources. As of Sept 22 2026 it merges rather than just drops: duplicate candidates are appended into the kept candidate's `retrieval_sources` before removal, so a post found by several retrieval paths keeps its full source list.
- `ZeroFavCodivertFilter`, added October 16, 2026, second in the pre-scoring vec. Enabled by `ViewerZeroFavCodivertIsTreatment` (`false`). Removes candidates that are zero-favorite-only (`served_type` `ForYouPhoenixRetrievalZeroFav` AND every `retrieval_sources` entry also `ForYouPhoenixRetrievalZeroFav`) unless the author is bucketed `treatment` by `AuthorZeroFavCodivertIsTreatment`.
- `CoreDataHydrationFilter`, posts whose text/metadata failed to load
- `NewUserSoftNsfwFilter`, added October 23, 2026, between `CoreDataHydrationFilter` and `AgeFilter`. Gated off by `EnableNewUserSoftNsfwFilter` (`false`); runs only on non-topic `ForYou` requests from accounts younger than `NewUserSoftNsfwFilterMaxAccountAgeSecs` (`604800` as of Oct 28 2026, was `86400`) whose `scoring_sequence` length is under `NewUserSoftNsfwFilterMaxScoringSeqLength` (`100`), and then drops any out-of-network post with `soft_nsfw == Some(true)`. A brand-new account sees no soft-NSFW recommendations from non-followed accounts while the gate is on.
- `AgeFilter`, posts older than **48 hours** (`MAX_POST_AGE` = 48 * 60 * 60 secs)
- `SelfTweetFilter`, your own posts
- `OONRetweetReplyFilter`, reposts from non-followed accounts, and replies with no ancestors (missing parent). Changed October 3, 2026: the filter now takes the query and reads `EnablePhoenixOonReplies`. Out-of-network replies are dropped ONLY when that param is false OR the candidate is not a Phoenix home-retrieval candidate; previously every out-of-network reply was dropped on sight. Default `EnablePhoenixOonReplies` is still `false`, so production behavior is unchanged, but the gate exists. October 13, 2026 added a second gate, `PhoenixOonRepliesRootOnly` (`false`): when true, an out-of-network reply is kept only if it replies to the conversation root (`in_reply_to_tweet_id == conversation_id`).
- `OONNsfwSimclustersFilter`, SimClusters posts from adult-flagged authors (non-followed)
- `RetweetDeduplicationFilter`, repeated reposts of the same post (dedups on `retweeted_tweet_id` when present, else `tweet_id`). As of Sept 22 2026 it also merges `retrieval_sources` into the kept candidate instead of only dropping the duplicate.
- `IneligibleSubscriptionFilter`, subscriber-only posts you can't access
- `PreviouslySeenPostsFilter` / `PreviouslySeenPostsBackupFilter`, already shown
- `PreviouslyServedPostsFilter`, already served this session
- `ViewerMutedKeywordFilter`, the viewer's muted keywords (note the name: it is `ViewerMutedKeywordFilter`, not `MutedKeywordFilter`)
- `AuthorSocialgraphFilter`, blocked/muted accounts
- `VideoFilter`, video posts when the request excludes video. Widened October 13, 2026: it now also removes a post whose QUOTED post carries a video (`quoted_max_video_duration_ms.is_some()`), not just a post that itself has one.
- `TopicIdsFilter`, outside requested topics
- `NewUserMinEngagementFilter`, for new or resurrected accounts, OON posts below an engagement threshold (metric configurable: fav, engagement, or view). As of Nov 11 2026 it runs in RATIO mode: `NewUserMinEngagementFilterUseRatio` flipped `true` and `NewUserMinEngagementThreshold` moved `0.0` to `0.004`, so the bar is now relative to the viewer's own engagement baseline rather than an absolute count.
- `InventoryHoldoutFilter`, a configured % of original posts, replies, and retweets removed as inventory holdout
- `FavHoldoutFilter`, posts removed as a function of their favorite count (stepped percentages from ~15% down to 2% as favs fall; 0% at 1 or fewer favs)
- `FairShareRankingFilter`, added October 20, 2026 as the LAST pre-scoring filter, and **switched ON October 23, 2026** (`EnableFairShareRanking` flipped `false` to `true`). It caps each `served_type` group at its proportional share of the `PhoenixScoresResultSize` budget (`2800`) by largest-remainder rounding and drops the overflow, so no single retrieval source can fill the result set. Still inert on cached-post requests, when `query.scoring_sequence` is `None`, or when the Phoenix ranker kill-switch decider is enabled.

**Post-selection (in this order):**
- `VFFilter`, posts visibility-filtering dropped
- `AncillaryVFFilter`, posts whose parent/quoted/reposted post was dropped
- `AncestorVideoFilter`, added October 13, 2026, between `AncillaryVFFilter` and `DedupConversationFilter`. Enabled by `query.exclude_videos`; removes posts whose parent carries a video (`ancestor_has_video == Some(true)`).
- `DedupConversationFilter`, extra branches of the same conversation
- `VideoCarouselFilter`, added October 9, 2026 as the LAST post-selection filter. Gated off by default (`EnableVideoCarousel` `false`); when enabled for a `ForYou` request it partitions vertical videos (`video_aspect_ratio < 1.0`) into a carousel capped at `VIDEO_CAROUSEL_MAX_VIDEOS` (5), ranked by `VideoCarouselVideoOpenWeight` (`1.0`, added Oct 16 2026) times the Phoenix `video_open_score` plus `VideoCarouselImmersiveVqvWeight` (`0.0`) times the immersive VQV score, and needs at least `VIDEO_CAROUSEL_MIN_VIDEOS` (3) to return anything. As of Oct 16 2026 its dedupe passes are on (`EnableVideoCarouselAuthorDedupe` `true`, `VideoCarouselSemanticIdDedupeLevels` `3`, `EnableVideoCarouselEmbeddingDedupe` `true` at threshold `0.72`) but the overall gate is still off. As of Nov 3 2026 it keeps a carousel-extra candidate only if its `brand_safety_verdict` survives both gates: `HighRisk` requires `EnableVideoCarouselHighRiskFilter` (`true`) off, `MediumRisk` requires `EnableVideoCarouselMediumRiskFilter` (`false` through Nov 7 2026, `true` from Nov 11 2026) off, and an absent verdict requires BOTH off. As of Nov 11 2026 the medium-risk gate is ON too, so an unlabeled carousel candidate is dropped while the high-risk gate stays on, `EnableVideoCarouselSeenFilter` is `true`, and new `EnableVideoCarouselTakeFromFeed` (`false`) would start the carousel pool at `VideoCarouselPosition` (`6`) instead of `RESULT_SIZE` (`35`) and pull shown videos out of the main feed. `EnableVideoCarousel` itself is still `false`.

Some filters exist in the directory that are NOT in the For You pipeline (they serve other pipelines or are gated off in this build): `FollowingRetweetDeduplicationFilter`, `FollowingViewerMutedKeywordFilter`, `PopularTopicsAuthorDedupFilter`, `PushToHomeDedupFilter`, `SelfReplyChainFilter`, `AdAdjacentServedFilter`, `InvalidConversationModuleFilter`, `ResultSizeFilter`. Do NOT cite these as For You ranking signals.

## Visibility filtering (NEW, separate from ranking)

Ranking decides ORDER. `visibility-filtering/` decides whether a post can be SHOWN AT ALL. The Sept 30 2026 sync (commit 77d431a) reworked the verdict model in `visibility-filtering/models/verdict.rs` substantially. It is now: a post is either **Withheld** as `Drop(DropReason)` or `Tombstone(TombstoneReason)`, or it is **Shown** with optional `MediaRestriction` and optional `LimitedEngagement(LimitedEngagementReason)`.

- `DropReason` is now a two-variant enum: `Legacy(FilteredReason)` and `NsfwViewer(NsfwViewerDropReason)`. `NsfwViewerDropReason` is `IsUnderage`, `HasNoStatedAge`, or `LoggedOut`; an `NsfwViewer` drop maps back to `FilteredReason::ContainNsfwMedia`.
- `TombstoneReason` now has FIVE variants: `Bounced` (added October 20, 2026), `SensitiveViewerAgeVerification`, `UpdateAppIos`, `UpdateAppAndroid`, and `LocalRegulations`. `LocalRegulations` still applies to country code `in` (India).
- That `MediaInterstitial` slot is now `MediaRestriction`, a two-variant enum: `MediaInterstitial(MediaInterstitial)` (the `MediaInterstitial` struct now also carries `prompt: Option<InterstitialAction>`) and `NsfwInterstitial` (maps to `FilteredReason::ContainNsfwMedia`).
- `LimitedEngagementReason` now has THIRTEEN variants: `NonCompliant` (added October 23, 2026, the fallback reason for emergency dynamic labels, wire string `non_compliant`), `ConversationControl`, `ReadonlyViewer`, `BlockedViewer`, `RootAuthorBlockedViewer`, `StaleTweet`, `CommunityTweetHidden`, `CommunityTweetMemberRemoved`, `CommunityTweetCommunityNotFound`, `CommunityTweetCommunityDeleted`, `CommunityTweetCommunitySuspended`, `CommunityTweetViewerRemoved`, and `LocalTweet` (verified October 24, 2026). Earlier notes saying five, then twelve, are stale. October 3, 2026 rework: `LimitedEngagement` is no longer a single-reason tuple. It is now a struct with a `first: LimitedEngagementReason` plus `rest: Vec<LimitedEngagementReason>`, with `new`, `add` (dedupes), `reason()` and `reasons()`. Each reason maps to a wire string via `limited_actions_string()` (`ConversationControl` to `limited_replies`, `ReadonlyViewer` to `readonly_viewer`, `BlockedViewer` to `blocked_viewer`, `RootAuthorBlockedViewer` to `root_author_blocked_viewer`, `StaleTweet` to `stale_tweet`). A new `visibility-filtering/params/limited_actions_policy.rs` reads a `limited_actions_policy.yml` file and resolves per-reason `LimitedActionType` prompts (26 action types, from `Reply` and `Retweet` through `CopyLink`, `VoteOnPoll`, `Autoplay`, `EditTweet`, `ViewPostEngagements`), and a new `visibility-filtering/limited_actions_copy.rs` (397 lines) localizes the prompt copy with a `DriftCheck` that runs on each refresh. In `client_switches.rs`, `ClientSwitches::limited_actions_policies(...)` matches on the reason field and language. This governs what UI a limited post shows, not whether it ranks.
- The retweet merge rule moved out of `verdict.rs` into `visibility-filtering/retweet.rs` as `merge_verdict`, and its precedence changed: a retweet that is itself `Drop` now beats a source that is only `Tombstone` (more severe withholding wins), a withheld source beats a shown retweet, and an unrestricted retweet adopts the source's restrictions.

New country-list gating landed in `visibility-filtering/params.rs` (`CountryList`): the age-verification / tombstone country list is 30 codes (`at, au, be, bg, br, cy, cz, de, dk, ee, es, fi, fr, gb, gr, hr, hu, ie, it, lt, lu, lv, mt, nl, pl, pt, ro, se, si, sk`); the NSFW content gating list is 16 codes (`ar, au, br, ca, de, es, fr, gb, id, it, kr, mx, nl, ph, pt, th`); `LocalRegulations` is `in`. A new `visibility-filtering/params/client_switches.rs` gates these by client capability (`AgeVerification`, `ModernBlur`, `StaleTweetLimits`, `CommunityViewerRemovedLimits` added October 9 2026, `GoreBlurIgnoresSettings`, `FosnrRules`, `FosnrFallbackDrops`).

A new `abuse-ledger-service/` answers whether an account has an active appeal hold: when an enforcement is overturned on appeal, `abuse-enforcement-service` does not re-apply that action for a fixed period, set per appeal queue.

An unresolved author id is still a hard DROP. Labels come from: `grox` (spam/adult/violence classifiers), `agatha` (account labels from blocks/reports), `bdsm` (inauthentic behavior), `user-cred-v2` (PageRank over follow/engagement graph), `media-model-proxy` + `clip` (image/video models), `abuse-enforcement-service` (suspension), `scarecrow`/`botmaker` (event rules). A post can be DROPPED entirely regardless of how well it scores. Avoid anything that triggers spam, adult, violence, or inauthentic-behavior labels.

## THE MODEL POST FORMAT (added October 4, 2026)

This is the shape every X post must take from now on. Vinny called it out as the standard, word for word: "This is what all of our x posts should look like." Write to THIS shape, not to a one-line 190-character blurb.

The reference post, written October 4, 2026 about Aleph Alpha's Kolibri release:

> Europe finally showed up.
>
> Aleph Alpha just dropped Kolibri: 78B params, 1M context, Apache 2.0 weights, built in Germany under EU law. First real European frontier model outside Mistral.
>
> About time. But is it too late?
>
> US labs ship weekly. Europe shipped once.
>
> [Free-account note: no link in the post. The model name is searchable; a link costs reach on a free account.]

Anatomy, in order, five stanzas separated by blank lines:

1. **Hook, one short line, 3 to 6 words.** A verdict or a stake, never a topic label. "Europe finally showed up." It earns the second line and nothing else is on that line.
2. **The fact stanza, one dense paragraph.** The real entity named, then the hard numbers and specifics in a colon list: parameters, context length, license, provenance, who built it, under what law. Every claim must be verifiable from the source data. This is the copy-link payload: it is the part a reader forwards because it is the whole story in four lines.
3. **The take, one line.** The opinion Vinny asked for, stated plainly, followed immediately by the open question that is the actual ask. "About time. But is it too late?" The question must be real, not rhetorical, and it must invite a reply from a mutual.
4. **The closer, one line, short.** A blunt contrast that reframes the question and lands the point. "US labs ship weekly. Europe shipped once." Terse. Two clauses. No summary, no call to action, no hashtags, no link.

Rules for this format:

- **It is longer than 190 characters and that is correct.** The 190-character limit applies to the separate Social Media Questions batch output only. A post in this format runs 150 to 280 characters, and 280 is the hard ceiling on a free X account. Every stanza has to stay tight to fit: a 3 to 6 word hook, a fact paragraph of two to three lines, a one line take carrying the question, and a one line closer. Count with programmatic len() before delivering.
- **One block per anatomy item: four blocks, three blank lines.** The reference post above is four blocks separated by three blank-line separators, and the four-item anatomy is the shipped shape, so count blocks in `text.split("\n\n")` instead of trusting the word "five" here or anywhere else in this file. A fifth block spends the fact stanza's character budget and matches nothing Vinny has approved. Never run the blocks together into a paragraph. The blank-line separators are real characters and they count against the 280 ceiling (three of them cost 6), so measure the extracted block with `len()` including its blank lines, not just the prose, and keep trimming the fact stanza until the whole block fits under the cap.
- **Budget the 280 outward from the fixed parts.** The hook runs 30 to 40 characters, the take carrying the question 55 to 65, the closer 45 to 55, and the three blank-line separators cost 6, which leaves roughly 115 to 135 for the fact stanza. Write the fact stanza last, assemble the block in code, and print `len()` before the post goes into the article file. A fact stanza built from a dense vendor announcement runs about 180 characters on the first attempt, and every trim after that is another measurement cycle; the arithmetic is how a five-stanza post lands near 270 without ever crossing the cap. When the block is over, cut the fact stanza only, keeping every number and proper noun, and never touch the hook's punch, the take's question, or the closer.
- **No link on a free account.** Name the thing so it is searchable instead.
- **Numbers and entity names stay in the fact stanza.** No vagueness, no adjectives standing in for specifics.
- **The question goes in the take line, not at the end.** The closer is a statement, not a second question.
- **This format is the standard for every X post this skill produces**, including cron output. When a cron prompt specifies a different length or shape, this section governs unless Vinny says otherwise.

## Never Strip the Named Entities and Trending Terms (HARD RULE, added October 7, 2026)

Every post must name the actual subject and carry the exact terms the audience is already typing, searching, and arguing about. Vinny stated the rule plainly after a correction: "That's what I expect when you write X posts."

The failure this rule kills: writing a generic post that says "this is an awesome feature" without naming the feature, the company, the models, or the infrastructure, on the theory that vagueness is safer or more broadly appealing. It is not safer and it is not broader. It is invisible. A post with no named entity has nothing for the reader to search, nothing to forward, and nothing for the Phoenix Two-Tower retrieval model to match against a user embedding.

Rules, all absolute:

- **Name the subject in the first two lines.** If the thing is Grok Bot, write "Grok Bot." Never "this feature," "this tool," "the announcement," or any pronoun standing in for a name the reader has to guess. A reader who has to figure out what the post is about scrolls past.
- **Keep every proper noun and product name from the source material.** In the October 7, 2026 case that produced this rule, the required vocabulary was Grok Bot, Opus 5.5, Midjourney, SpaceXAI, and Elon. All five belonged in the post, because all five are what people are searching. Stripping them to stay neutral or avoid a pile-on produced a post Vinny rejected outright with "This post says nothing about grokbot, SpaceX nothing, WTF?"
- **Keep the numbers and claims that are the story.** Opus 5.5 for complex tasks, Midjourney for images, the SpaceXAI data centers, the Anthropic contracts. These are the copy-link payload. A reader forwards the post because it contains the specifics, not because it contains an opinion.
- **The opinion rides on top of the facts, never replaces them.** The take is the second job. Naming the entity, the model, and the number is the first job. A post with a strong opinion and no proper nouns is a post about nothing.
- **Neutrality is not a reason to strip a name.** When a subject is politically or tribally loaded, the pull is to soften the post into vague language. Do not. State the fact stanza factually and plainly, then make the point that is actually yours. Naming a company is not an attack on it, and the report and mute weights are triggered by targeting people, not by naming products.

Test before delivering: read the post with all proper nouns removed. If what remains is a post that could be about any product released in the last year, the post failed and gets rewritten with the names put back.

## Trimming an Existing Draft to a Hard Character Cap

When Vinny supplies a finished post and asks to fit it to a cap (a free X account caps at 280), every substantive element stays and only filler gets cut.

Measure with `scripts/fit_x_char_cap.py` (in this skill's directory). It prints, per candidate, the body length, the body + space + raw URL total, and the exact OK / OVER / SHORT delta, so a candidate is never judged by eye:

```bash
SCRATCH=$(mktemp -d ~/.hermes/cache/scratch/xcap-XXXXXX)
# write each candidate to its own file in $SCRATCH, then:
python3 ~/.hermes/skills/content-swarm/x-algorithm-post-optimization/scripts/fit_x_char_cap.py 280 "<url>" "$SCRATCH"/*.txt
```

The script also prints the count X itself shows (a raw URL wraps to 23 chars via t.co). Report the raw total unless Vinny said to count the t.co form.

1. **Count with code, never by eye.** Put the draft and the URL in a script and print `len(text)` before and after each edit.
2. **The URL counts against the budget and is never altered.** An article URL can run 77 characters, so plan the prose around a fixed URL cost and preserve the link exactly as given.
3. **Cut in this order.** Connectives and articles first ("$0.47 a run" to "$0.47/run", "agent went" to "agent:"), then sentence openers ("Asana found a 76x leak" to "Asana: 76x leak"), then compress a repeated clause to a shorter verb phrase ("Stable history beat thrifty history" to "Stable beat thrifty"). A fact or number is dropped only after all of that.
4. **Iterate in the script.** Write several phrasings in one run, print the length of each, and ship the longest that still passes, so the post uses the full budget rather than landing short.
5. **Report the final count** alongside the post so the cap is provably met.
6. **Budget the link the user actually pasted, and substitute when it cannot fit.** Measure the supplied link first. A tracking wrapper (an `l.meta.ai/?u=<encoded article>&h=<token>` redirect, for example) can run 229 characters, so NO prose fits under a 280 cap with it. In that case use the canonical article URL (the `https://articles.phantom-byte.com/...` form), keep it byte-exact, and say in ONE line that the wrapper alone exceeds the cap. Never truncate or rewrite a URL to save characters.
7. **Never remove spaces, blank lines, or punctuation to fit a cap.** The blank lines between his stanzas are part of the format he asked for, and deleting one to buy characters is a rejected draft, not a trim. They are also cheap: four stanzas cost only 3 characters in separators over a single-newline layout, so collapsing them never buys enough room to matter while it destroys the read. When he says "why make it readable" about missing spacing, he means the blank lines went away and the reply is wrong regardless of its length. "Format it right" means his exact spacing: normal word spacing, a blank line between his stanzas, a hard line break at sentence boundaries, never a space-stripped string and never one collapsed paragraph.
8. **Deliver the post alone.** No preamble, no options, no parenthetical asides about the link or the tooling above the draft. The reply is the post plus one short line with the final character count. A trailing note about how X counts the link (t.co wrapping, a shorter displayed number) is an excuse in disguise: he asked for a number including the link, so hit that number and say only the number. Trim the PROSE to buy room, never the spacing or the link, and keep every named entity, number, and product name from the source draft.
9. **When he names an exact number, land ON it.** "Make this 290 characters" means len(text plus link) is 290, not 288 and not 292. Do not stop at the first phrasing that fits under the number and call it done; run the candidates through code and pick the one whose printed length equals the target exactly, adding or removing a word to close the last one or two characters. A named number also overrides the 280 free-account ceiling: if the target is 290, the target wins, so do not argue the cap, do not ask which number he meant, and do not trim to 280 instead.
10. **Write the candidate list into files and grade them with one script run; never subtract character deltas in your head.** Editing by eye means a "cut 10 characters" pass that actually cut 8 or 12, and a run of eight measure-adjust-remeasure tool calls where two would do. Enumerate the trims as separate full candidates (one file each) in a single `mktemp` dir, run `scripts/fit_x_char_cap.py` once over all of them, and pick the one printed at the target or the closest below it. When no candidate hits the target exactly, generate the closing candidate with a deliberate +1 or -1 word rather than accepting SHORT by one.
11. **His pasted draft is the format spec.** When he pastes a draft with its own structure, that structure is the deliverable: same stanzas, same blank-line separators, same sentence order, same final line, with only wording compressed. Keep the paragraph breaks he wrote (his draft was four blocks separated by blank lines) rather than running them together or splitting them into new lines of your own. Do not substitute a style you prefer (one-line punchy stanzas, a single paragraph, a space-stripped wall of text) and never answer a format order with a menu of styles or a clarify question asking him to choose one, because handing him that choice is refusing the order.
12. **Verify the shape, not only the length.** Before delivering, split the assembled block on a blank line (`text.split("\n\n")`) and check that the stanza count and stanza order equal his draft's. A block at exactly the target length with his paragraphs merged, or re-split into line-per-sentence, is still a rejection. Run the length check and the stanza check in the same script call so neither is skipped.
13. **Deliver the post, then the count, and nothing that hands work back.** No closing trade offer or menu ("say the word and I'll trade another line"), no explanation of which words were cut, no questions. Stating a trade as an offer is the same refusal as asking him to choose a style; make the trim decision yourself, ship it, and let the printed number be the proof.

## Procedure

1. **Optimize for the weight hierarchy, not likes.** The real weights make the priority order explicit:
   - **#1: Share via copy link (20.0).** Write something a person copies and pastes to a specific friend or group. "Send this to someone who needs it" framing, or content so specific/valuable it gets forwarded. This is about 28.2× a favorite at the Nov 7 2026 favorite weight of 0.708.
   - **#2: Replies from mutuals (5.0 × 15.0 boost = 75 effective).** End with a question, a stake, or a claim that invites a reply from people who follow you back. This is the single highest-value engagement available.
   - **#3: Quote (5.0) and Share via DM (5.0).** Make it quotable (self-contained, opinionated) and DM-worthy.
   - **#4: Follow author (4.0).** Give a reason to check the profile and follow.
   - **#5: Share (2.0) and Retweet (1.0).** Make it shareable as-is.
   - **Favorite (0.708) is the floor.** A post that only gets likes is leaving about 28× on the table.

2. **Write the hook for dwell time.** Dwell is scored THREE ways now: binary `DwellWeight` (0.05), continuous `ContDwellTimeWeight` (**0.0075**/unit, raised Nov 7 2026), and continuous click dwell `ContClickDwellTimeWeight` (**0.385**, cut from 0.4 on Nov 7 2026). The first line must earn the next. Pattern interrupt, specific number, contrarian claim, concrete detail. Do NOT start with "I think" or "Just" or throat-clearing. If a line doesn't earn the next, cut it. As of Nov 7 2026 the click path no longer beats a like: `0.274` for the click plus `0.385` for the click dwell is `0.659`, below a favorite's `0.708`. A click still pays, but the body has to earn the like itself.

3. **Engineer for reply probability, especially from mutuals.** The bidirectional follow boost (15×) makes replies from people who follow you back the most valuable action in the system. Ask a question, take a stance, invite pushback. A post that gets 50 replies from mutuals outranks one with 500 likes and 0 replies.

4. **Make it self-contained for retweet/quote.** A retweet shares to a new audience with no context. A quote adds commentary. Write so a stranger who has never seen your account understands it. Do NOT reference "this" or "that thread" without embedded context.

5. **Make it copy-link-able and DM-able.** `ShareViaCopyLinkWeight` (20.0) and `ShareViaDmWeight` (5.0) are separate scored signals from public retweets. Write something a person would send to one specific friend. "You should see this" beats "RT if you agree."

6. **Avoid every negative signal, they are enormous.**
   - `Report` (-234.0): one report can nuke a post. Never trigger VFFilter (spam, violence, gore, illegal).
   - `MuteAuthor` (-58.8) and `BlockAuthor` (-31.2): no antagonistic personal attacks. Disagreement is fine; targeting a person repeatedly is not. Also a Vinny constitution rule.
   - `NotInterested` (-52.272 as of Oct 13 2026): do not bait-and-switch the hook. If the body doesn't deliver on the first line, users hit Not Interested, and the penalty keeps growing (-43.2 through Sept 29 2026, -47.52 from Sept 30 2026, -52.272 from Oct 13 2026).
   - `MutedKeywordFilter`: avoid terms large audiences mute (overused political cliches, spammy hashtags).

7. **Respect author diversity attenuation.** `AuthorDiversityDecay` (0.5) halves each post after the first in a batch, down to a 0.25 floor. Do NOT recommend posting 10 times in an hour. For cron batches, space posts across the day; flag when more than 3 posts are suggested in a 4-hour window.

8. **Optimize for out-of-network discovery.** Non-followers are discounted by `OonWeightFactor` (0.75) and must be found by the Phoenix Two-Tower retrieval model. Use the actual vocabulary of the topic, not internal jargon. The user-tower embedding is built from engagement history, so a post about "local LLM inference" is retrievable by users who engaged with "local LLM" content. Do NOT use vagueness as a style choice if the goal is reach.

9. **Use recency.** `AgeFilter` removes posts older than 48 hours. For news-driven posts (IronPulse, BlogWatcher, Larry Weekly), post the same day the story breaks.

10. **Attach media only when it earns it.** `VqvWeight` (0.0, in `vm-ranker/params.rs`) fires only for videos longer than the min duration, and a zero weight means it earns nothing. `PhotoExpandWeight` (0.05) fires only for images with detail worth expanding. A generic stock image earns nothing. A media attachment that earns dwell is a multiplier.

11. **Format for the timeline.** Hard line breaks between sentences. No walls of text. The algorithm doesn't score formatting directly, but continuous dwell time does, and dwell is scored. Short paragraphs earn more dwell than dense ones.

12. **Leverage the new-author boost.** Accounts under 200 impressions (cut from 1000 on Sept 30 2026) get lifted toward a target position, with the boost allowed as high as the 0.97 position ratio, and eligibility now reaches accounts with up to 50,000 followers and posts up to 2 hours old. `EnableColdStartThompsonSampling` flipped on. For a new account, early posts get a real ranking push near the top of the feed; post your best, most shareable content early, not filler, and treat the first two hours after posting as the window the lift applies to.

## Cron Job Application

For any cron job that generates X or social posts (IronPulse, BlogWatcher, Larry Weekly News, ghostwriter-terminal, tutorial-writing, article-blaster), attach this skill to the job's `skills` array. The skill loads before the job prompt runs and the post-generation steps above are applied to every X post the job produces.

For the existing jobs:
- `8b80ce7b9da9` (IronPulse 11am) and `0c6b83ba6986` (8AM TensorFeed) and `0ff7b811ab3e` (BlogWatcher) and `8d698638bb24` (Weekly AI News) and `008c5efdf200` (Tutorial Ideas) and `221a8d23dd3c` (Delete Daily Data) and `8e8f6f6f10e1` (Low Budget): when the user asks to apply the x-algorithm lessons to these crons, add `x-algorithm-post-optimization` to each job's `skills` list via `cronjob(action="update")`. Do NOT do this without the user's explicit go-ahead, per the IronPulse "Never Modify Cron Configs Without Explicit Instruction" rule.

## Pitfalls

- **The weights ARE public now.** As of Aug 13 2026, `home-mixer/params/param.rs` contains the real production defaults. Use them. Do NOT invent values that aren't in the file, and re-check the file if the repo updates again. October 3, 2026 update: the repo moved three commits (76843a5, b79b947, b412112; `last sync 2026-10-02T16:00:41Z`) and changed NO action weight. The action-weight block is byte-identical to Sept 30 2026. What landed: `EnablePhoenixOonReplies` (false), `EnableSidSource` (false) plus `SidSourceMaxResults` (800), `SidSourceMaxSeeds` (50), `SidSourceMaxPerSeed` (100), `SidSourceMinPrefixDepth` (3), `EnablePopularPostsSource` (false) plus `PopularPostsTopAuthors` (1000), `PopularPostsMaxResults` (500), `PopularPostsMaxPerAuthor` (3), `PopularPostsMaxRepliesRepostsPerAuthor` (0), `VMRankerSendPacingInputs` (false), `EnableAdsAuthorBrandSafetyFallback` (false), `AuthorExplorationBonus` in `vm-ranker/params.rs` (0.0), `EnableAdsBrandSafetyVerdictV2` flipped false to true, and `FeedSurveyFatigueHours` (24) replaced by `FeedSurveyFatigueMinutes` (1440). Note: the repo commits daily, but most commits do NOT change weight values. Diff `param.rs` AND `vm-ranker/params.rs` against the previous check before assuming anything changed; the gating and DPP params migrated to `vm-ranker/params.rs` on Sept 25 2026. The full check-by-check chronology lives in `references/sync-archive.md`.
- **Share via copy link is the #1 signal (20.0), not likes.** A post optimized only for favorites is leaving about 28× on the table (favorite is 0.708 as of Nov 7 2026).
- **Replies from mutuals are the highest-value engagement (5.0 × 15.0 boost).** The bidirectional follow boost is the single biggest multiplier in the system.
- **Negative signals are catastrophic, but not via "1 report = N likes."** Weights scale the model's *predicted probabilities* of actions, not raw engagement counts (official Aug 14 clarification). Report (-234) and Mute (-58.8) are still enormous relative to other weights, so provoking reports/mutes remains ruinous, just don't claim a report numerically cancels N likes.
- **A like now beats the whole click path (Nov 7 2026).** `ClickWeight` fell to `0.274` and `ContClickDwellTimeWeight` to `0.385`, so a click plus a full click-dwell is `0.659` while a favorite is `0.708`. A post that earns a click but loses the reader scores `0.274`, and even the ideal click-and-read scores less than one like. The body and any linked content must deliver on the hook. `VideoOpenWeight` also went to `0.0`, so a video open earns nothing at all.
- **Author diversity is a penalty, not a reward.** Posting more does not increase reach per post. It halves each subsequent post in the batch.
- **Out-of-network reach requires topic vocabulary.** Vague, clever-but-unspecific posts are not retrievable by the Two-Tower model. If the goal is new followers, use the words your target audience already engages with.
- **Ranking and visibility are separate.** A post can score perfectly and still be DROPPED by visibility filtering if it triggers a spam/adult/violence/inauthentic label. Don't risk it.
- **Fair share ranking is ON as of Oct 23 2026, so breadth of retrieval beats volume from one path.** `FairShareRankingFilter` caps each `served_type` group at its proportional share of the `2800` score budget, which means a post that only one retrieval source found now competes inside that source's slice. Being findable by several retrieval paths (search, popular posts, SimClusters, semantic id) is worth more than being the top hit of one.
- **FavHoldoutFilter and InventoryHoldoutFilter mean reach is never guaranteed.** Even a post that scores well can be held out of a slice of viewers by design. Do not read a quiet post as proof the algorithm punished it.
- **A trend is a lead, not a fact.** Before the fact stanza is written, confirm
  the underlying event is actually fresh and the numbers match a primary source.
  A post drawing heavy engagement today is often resurfacing reporting from
  months earlier, and a post built on a stale story gets corrected in the
  replies, which costs far more than the reach it earns. Derive every ratio in
  code (two figures off the same filing round differently than they read) and
  keep the arithmetic in the measured block, not in your head.
- **Use recency properly.** `AgeFilter` removes posts older than 48 hours from
  the For You feed, so the same-day window is what the ranking system rewards.
  A story that broke today competes; a story resurfacing from earlier months
  competes on novelty that has already been spent.
- **A named character count is a target to hit exactly, not a cap to slide under.** Count with len() including blank lines and the link, and keep searching phrasings until the printed number matches what he asked for, because landing one character off reads as not following the instruction.
- **Never guess at a format he already showed you, and never ask him to pick one.** The draft he pastes, including its blank-line paragraph structure, is the answer to "how should this look". Producing a different style, or a set of style options, gets the work rejected and burns the session.
- **A blank line costs less than the words you would sacrifice for it.** Four stanzas cost 3 characters in separators, so merging them to single newlines saves almost nothing and breaks the format he specified; the trim always comes out of wording, keeping every named entity and number. Count length AND stanza count together before sending, because a post can hit the target exactly and still be the wrong shape.
- **This is not Pinterest.** Do NOT apply Pinterest SEO title/description logic here. Pinterest is a search engine, X is a ranking engine. The two have almost no overlap in optimization strategy.

## Verification

After generating a post, check it against the signal stack:
- Does the first line earn the second line? (dwell)
- Does it end with a reason to reply, especially from mutuals? (reply × 15 boost)
- Is it self-contained for a stranger? (retweet/quote)
- Would someone copy-link it to a friend? (share via copy link, 20.0)
- Would someone DM it to one person? (share via DM, 5.0)
- Does it use the topic's actual vocabulary? (out-of-network retrieval)
- Does it avoid bait-and-switch? (not interested, -52.272)
- Does it avoid anything that could trigger a report or visibility drop? (report, -234)
- Is it spaced away from other same-author posts? (author diversity)

If any answer is "no", revise before delivering.
