# x-algorithm sync archive (October 3, 2026 back through September 25, 2026)

Historical record moved out of SKILL.md to keep the main file under the size limit. These entries are chronology, not current constants. The CURRENT values are the tables in SKILL.md; when this archive disagrees with SKILL.md, SKILL.md wins.

## Sync sections

**October 3, 2026 sync (`last sync 2026-10-02T16:00:41Z`, commit b412112), NO action weight changed.** The whole action-weight block, including the three Sept 30 2026 moves, is unchanged. The changes are all non-weight. New params in `home-mixer/params/param.rs` (quoted exactly, type and trailing default):

| Param | Type | Value |
|---|---|---|
| `EnablePhoenixOonReplies` | bool | `false` |
| `EnableSidSource` | bool | `false` |
| `SidSourceMaxResults` | u32 | `800` |
| `SidSourceMaxSeeds` | usize | `50` |
| `SidSourceMaxPerSeed` | u32 | `100` |
| `SidSourceMinPrefixDepth` | u32 | `3` |
| `EnablePopularPostsSource` | bool | `false` |
| `PopularPostsTopAuthors` | u32 | `1000` |
| `PopularPostsMaxResults` | u32 | `500` |
| `PopularPostsMaxPerAuthor` | u32 | `3` |
| `PopularPostsMaxRepliesRepostsPerAuthor` | u32 | `0` |
| `VMRankerSendPacingInputs` | bool | `false` |
| `EnableAdsAuthorBrandSafetyFallback` | bool | `false` |
| `AuthorExplorationBonus` (in `vm-ranker/params.rs`) | f64 | `0.0` |

Changed defaults at this sync:

| Param | Old | New |
|---|---|---|
| `EnableAdsBrandSafetyVerdictV2` | `false` | `true` |
| `FeedSurveyFatigueHours` | `24` | DELETED, replaced by `FeedSurveyFatigueMinutes` = `1440` |

`AuthorExplorationBonus` is added to each post's weighted score by the new `add_exploration_bonus` in `xai-value-model/scoring.rs` before `adjust_base_scores` and the multipliers run. Its default is `0.0`, so it changes nothing in production today, but it is now the one f64 score knob outside the action-weight block. `EnablePhoenixOonReplies` gates a new `OONRetweetReplyFilter` behavior: at HEAD the filter reads the param and keeps out-of-network replies found by Phoenix home retrieval instead of dropping them, whereas before it dropped every out-of-network reply unconditionally. New candidate sources landed in `phoenix_candidate_pipeline.rs` (`PopularPostsSource` and `SidSource`), both behind their `Enable*` gates, which are `false` by default, plus a `PhoenixReplyAncestorsHydrator` and a `SimClustersAnnCacheClient`.

**October 6, 2026 sync (`last sync 2026-10-06T16:00:58Z`, commit 78460ca), ONE ACTION WEIGHT CHANGED.** `PostUnexploredWeight` was cut from `0.02` to `0.015` in `home-mixer/params/param.rs`. Note the two files now DISAGREE: `vm-ranker/params.rs` still carries `PostUnexploredWeight` `0.02`. Every other action weight, including the three Sept 30 2026 values (`ClickWeight` 0.3, `ContClickDwellTimeWeight` 0.4, `NotInterestedWeight` -47.52), is unchanged in both files.

Three NEW f64 action-weight-style params landed in `vm-ranker/params.rs`, all defaulting to `0.0`, so they score nothing in production today but are the knobs to watch:

| Param (in `vm-ranker/params.rs`) | Type | Value |
|---|---|---|
| `VideoContinuationWeight` | f64 | `0.0` |
| `UserVideoContinuationWeight` | f64 | `0.0` |
| `ProfileVisitSecsWeight` | f64 | `0.0` |
| `PostUnexploredIncludeOutOfNetwork` | bool | `false` |

They are wired as products, not single scores: `xai-value-model/scoring.rs` adds `video_open_score × home_video_continuation_secs`, `video_open_score × user_video_continuation_secs`, and `profile_click_score × home_profile_visit_secs`, plus a new `set_user_video_continuation` pass that averages open-weighted continuation seconds across the request's candidates. `weights_mut` in `xai-value-model/weights.rs` grew from 25 to 28 entries. `PostUnexploredIncludeOutOfNetwork` (false) now gates the `PostUnexploredWeight` in-network-only condition in `compute_weighted_score`; the old code applied the weight only when `candidate.in_network == Some(true)`, the new code applies it for out-of-network too when the flag is true. `vm-ranker/params.rs` grew from 44 to 49 params.

Changed and removed non-weight params in `home-mixer/params/param.rs`:

| Param | Old | New |
|---|---|---|
| `RetrievalCandidatesKafkaMaxCandidates` | `200` | `100000` |
| `VMRankerClusterId` | `"Experiment6"` | `"Experiment1"` |
| `EnablePopularPostsSource` | `false` | `true` |
| `PopularPostsTopAuthors` | `1000` | DELETED |
| `PopularPostsMaxPerAuthor` | `3` | DELETED |
| `PopularPostsMaxRepliesRepostsPerAuthor` | `0` | DELETED |
| `EnableHomeExcursionScores` | did not exist | ADDED, `false` |
| `EnableUnderTheHood` | did not exist | ADDED, `false` |

**`EnablePopularPostsSource` flipped to `true`.** The `PopularPostsSource` candidate path is now ON by default, per the README ("a shared list of popular recent posts, initially from the most-followed active accounts"). A rewritten `home-mixer/sources/popular_posts_source.rs`, plus `home-mixer/util/popular_posts.rs`, `home-mixer/popular_posts_job.rs`, and a `PopularPostsCache`/`ManhattanPopularPostsStore` pair back it. The three deleted `PopularPosts*` caps are gone from `param.rs`, so the out-of-network pool is now bounded by `PopularPostsMaxResults` (500) and the new `RetrievalCandidatesKafkaMaxCandidates` ceiling. This matters for reach: the shared popular-posts list is a new out-of-network discovery path in the default lineup.

**Under the Hood transparency tool added.** A new `under-the-hood/` tree (with serving code and `under-the-hood/jetfuel/`) and `home-mixer/util/under_the_hood.rs` build a per-account report of the visibility-limiting labels applied to an account and its posts (page at `x.com/i/jf/under_the_hood`), gated by `EnableUnderTheHood` (`false`). The README now describes visibility filtering as returning one of FOUR answers, adding NOTICE (`SoftIntervention`) alongside ALLOW, INTERSTITIAL and DROP.

**Visibility filtering.** `Verdict::unresolved_author()` was replaced by `Verdict::not_found()` (`by: "not_found"`) and `Verdict::lookup_failed()` (`by: "lookup_failed"`), and a new `Evaluation` enum (`Complete`, `Partial { fail_open_defaults }`, `NotFound(Lookup)`, `Failed(Lookup)`) wraps them. A `Shown` verdict now carries `notice: Option<Decided<SoftIntervention>>` (a `SoftIntervention` holding an `AppealablePolicy` plus `level`, `proactive`, `appeal_submitted`). An unresolved author id is still a hard DROP. New files: `visibility-filtering/clients/article_client.rs`, `clients/trusted_friends_client.rs`, `hydration/community_source.rs`, `hydration/decode/article.rs`, `rules/safety_level.rs`, and golden-corpus fixtures for article and community. `visibility-filtering/params.rs`, `params/client_switches.rs`, and `params/limited_actions_policy.rs` are byte-identical to Oct 3 2026.

**Pipeline filter lineup unchanged.** The pre-scoring and post-selection filter vectors in `home-mixer/candidate_pipeline/phoenix_candidate_pipeline.rs` are identical to Oct 3 2026, and the `home-mixer/filters/` diff at this sync is empty. No filter file was added or removed.

**September 30, 2026 sync (`last sync 2026-09-29T17:02:52Z`, commit 77d431a), THREE ACTION WEIGHTS CHANGED.** This is the first sync since Aug 13 2026 that moved an action weight. Quoted exactly from `home-mixer/params/param.rs`:

| Param | Old (Aug 13 to Sept 25 2026) | New (Sept 30 2026) |
|---|---|---|
| `ClickWeight` | `0.4` | `0.3` |
| `ContClickDwellTimeWeight` | `0.0` | `0.4` |
| `NotInterestedWeight` | `-43.2` | `-47.52` |

All three changes also landed identically in `vm-ranker/params.rs`. Every other action weight (`FavoriteWeight` 0.5, `ReplyWeight` 5.0, `QuoteWeight` 5.0, `ShareViaDmWeight` 5.0, `ShareViaCopyLinkWeight` 20.0, `FollowAuthorWeight` 4.0, `ShareWeight` 2.0, `RetweetWeight` 1.0, `OpenLinkWeight` 0.2, `PhotoExpandWeight` 0.05, `VideoOpenWeight` 0.07, `VqvWeight` 0.0, `QuotedClickWeight` 0.05, `QuotedVqvWeight` 0.0, `PostUnexploredWeight` 0.02, `DwellWeight` 0.05, `ProfileClickWeight` 0.0, `ContDwellTimeWeight` 0.004, `NotDwelledWeight` -0.02, `BlockAuthorWeight` -31.2, `MuteAuthorWeight` -58.8, `ReportWeight` -234.0, `BidirectionalFollowReplyWeightBoost` 15.0, `BidirectionalFollowDwellWeightBoost` 0.0) is unchanged.

Note: `ContClickDwellTimeWeight` at 0.4 is now equal to `ClickWeight`, so a viewer who clicks a post and keeps dwelling on the opened content scores the same as the click itself. The click path plus the continuous click-dwell path together are worth 0.7, well above a favorite at 0.5, making a link or post that provokes an actual click-and-read the strongest mid-tier positive available.

**Non-weight params added or removed Sept 30 2026:**
| Param | Old | New |
|---|---|---|
| `ColdStartImpressionThreshold` (home-mixer) | `1000` | `200` |
| `ColdStartFollowerCap` (home-mixer) | `1000` | `50000` |
| `ColdStartMaxPostAgeSecs` (home-mixer) | `172800` | `7200` |
| `LowImpressionsMaxPositionRatio` (home-mixer) | `0.85` | `0.97` |
| `EnableColdStartThompsonSampling` (home-mixer) | `false` | `true` |
| `PhoenixColdStartMaxResults` (home-mixer) | `0` | `200` |
| `UseEngagementCounterViewCountForImpressionBoost` (home-mixer) | `true` | DELETED |
| `PhoenixRetrievalExcludeSeenPosts` (home-mixer) | did not exist | ADDED, `false` |

**Unchanged in `home-mixer/params/param.rs` at the Sept 30 2026 check:** `PhoenixMoeColdStartMaxResults` (200), `PhoenixMOEMaxResults` (0), `EnablePhoenixMOESource` (false), `PhoenixRetrievalMOEInferenceClusterId` ("Experiment2Memy04"), `SimclustersMaxCandidateAgeHours` (48), `RetrievalCandidatesKafkaSamplePercent` (5.0), `RetrievalCandidatesKafkaMaxCandidates` (200 at this check; raised to 100000 on Oct 6 2026), `MinVideoDurationMs` (10_000). `MAX_POST_AGE` lives in `home-mixer/params/config.rs` and is still `48 * 60 * 60`.

**September 25, 2026 sync (commit 4c5cfe8), NO action weight changed.** What moved was WHERE the non-weight params live and how the arithmetic is wired.

**Gating params removed from `home-mixer/params/param.rs` (22 total).** They were duplicate entries; the same values live on in `vm-ranker/params.rs`, which was byte-identical before and after this commit (44 params). Removed names and their surviving values: `EnableAuthorDiversity` (true), `AuthorDiversityDecay` (0.5), `AuthorDiversityFloor` (0.25), `OonWeightFactor` (0.75), `TopicOonWeightFactor` (0.5), `NewUserOonWeightFactor` (0.00001), `NewUserAgeThresholdSecs` (0), `EnableOonRescoreForInNetworkRepliesRetweets` (true), `MultiplierPreOffset` (false), `WeightPerturbationSigma` (0.0), `WeightPerturbationSalt` (""), `VMRankerComputeValueModel` (false), `VMRankerDppTheta` (0.65), `VMRankerDppMaxSelectedRank` (150), `VMRankerSendValueModelInputs` (false), `CachedPostsReuseWeightedScore` (false), `EnableVMRanker` (true), `EnableMultiplicativePostUnexplored` (false), `MultiplicativePostUnexploredAlpha` (0.0), `PostUnexploredWeightInNetworkOnly` (true), `EnableCdwellOnImpr` (false), `ContActiveSecs5mResidualNormWeight` (0.0).

**Renamed in `vm-ranker/params.rs` (same values, new names).** Use the new names when reading the repo: `VMRankerDppTheta` is now `DppTheta` (0.65), `VMRankerDppMaxSelectedRank` is now `DppMaxSelectedRank` (150), `VMRankerComputeValueModel` is now `ComputeValueModel` (false). `DppEnabled` (bool, true) is the DPP on/off gate, keyed `rust_home_mixer_vm_ranker_dpp_enabled`.

**Superseded Sept 30 2026, read the Sept 30 table above first.** The old "still in `home-mixer/params/param.rs` and unchanged" list of Sept 25 2026 said the action-weight block and `ColdStartImpressionThreshold` (1000) were unchanged; the Sept 30 2026 sync changed the click and click-dwell weights and cut `ColdStartImpressionThreshold` to 200. Still unchanged at Sept 30: `MinVideoDurationMs` (10_000, and the VQV eligibility threshold: QVQV only fires above it when `EnableQuotedVqvDurationCheck` is on, and there is a `MAX_FOLLOWERS_THRESHOLD` of 10_000 that suppresses VQV weight for very large accounts), `SimclustersMaxCandidateAgeHours` (48), `RetrievalCandidatesKafkaSamplePercent` (5.0), `RetrievalCandidatesKafkaMaxCandidates` (200 at this check; now 100000), `PhoenixMoeColdStartMaxResults` (200), `PhoenixMOEMaxResults` (0), `PhoenixRetrievalMOEInferenceClusterId` ("Experiment2Memy04"), `EnablePhoenixMOESource` (false).

**Changed defaults:**
| Param | Old | New |
|---|---|---|
| `VMRankerClusterId` | `"Experiment3"` | `"Experiment6"` |

**Code moved, same arithmetic.** `home-mixer/scorers/ranking_scorer.rs` (1255 lines) was deleted. The weighted sum now lives in the new `xai-value-model/` crate (`scoring.rs`, `weights.rs`, `inputs.rs`, `phoenix_scores.rs`), called from `home-mixer/scorers/value_model.rs` and `vm-ranker/scoring/value_model.rs`. The README's link for the arithmetic now points there. One real constant in the new location: `NEGATIVE_SCORES_OFFSET` = 0.001 in `xai-value-model/weights.rs`, used to keep negative scores ordered below positive ones. The scorers list is now `[PhoenixScorer, VMRanker]` only.

**Cold-start arm gating REVERSED on Sept 30 2026.** Superseding the Sept 25 2026 note: `home-mixer/scorers/author_cold_start.rs` at commit 77d431a deleted `apply_moe_ranking_policy` and the `author_policy_zeroed` field entirely. Arm-gated retrieval candidates (`ForYouPhoenixRetrievalMoe` and `ForYouPhoenixRetrievalCold`, returned by `is_arm_gated_retrieval`) are no longer zeroed for holdout or control viewers; they keep their score in every arm, and `ViewerArm::Holdout` now returns `true` for `cold_start_corpus_eligible`. `xai-value-model/scoring.rs` `apply_cold_start_decisions` dropped the `author_policy_zeroed` zeroing and starts from `scores.to_vec()`.

## Check-by-check chronology from the Pitfalls section

Chronology of the checks: the Sept 18, 2026 commit (8b25829) removed the entire `DwellRegret*` gate family and `value_model_gate.rs` while leaving every weight constant untouched; the Sept 22, 2026 sync (commits 3aa0fa3 and 1b3fec2) left every weight constant untouched again; the Sept 25, 2026 sync (commit 4c5cfe8, `last sync 2026-09-25T16:24:28Z`) again changed NO action weight, but deleted 22 non-weight params from `home-mixer/params/param.rs` (they survive in `vm-ranker/params.rs`), renamed `VMRankerDppTheta` to `DppTheta`, `VMRankerDppMaxSelectedRank` to `DppMaxSelectedRank`, and `VMRankerComputeValueModel` to `ComputeValueModel`, changed `VMRankerClusterId` from "Experiment3" to "Experiment6", and moved the weighted-sum arithmetic out of the deleted `home-mixer/scorers/ranking_scorer.rs` into the new `xai-value-model/` crate; the Sept 30, 2026 sync (commit 77d431a, `last sync 2026-09-29T17:02:52Z`) changed THREE action weights for the first time since Aug 13 2026 (`ClickWeight` 0.4 to 0.3, `ContClickDwellTimeWeight` 0.0 to 0.4, `NotInterestedWeight` -43.2 to -47.52), cut `ColdStartImpressionThreshold` from 1000 to 200, raised `ColdStartFollowerCap` from 1000 to 50000, cut `ColdStartMaxPostAgeSecs` from 172800 to 7200, raised `LowImpressionsMaxPositionRatio` from 0.85 to 0.97, flipped `EnableColdStartThompsonSampling` to true, raised `PhoenixColdStartMaxResults` from 0 to 200, deleted `UseEngagementCounterViewCountForImpressionBoost`, added `PhoenixRetrievalExcludeSeenPosts` (false), reversed the cold-start arm-gating zeroing, deleted `home-mixer/util/composition.rs`, and reworked the visibility-filtering verdict model and country lists; the October 3, 2026 sync (commit b412112, `last sync 2026-10-02T16:00:41Z`) again changed NO action weight and only added non-weight retrieval, ads and survey params plus `AuthorExplorationBonus` (0.0); and the October 6, 2026 sync (commit 78460ca, `last sync 2026-10-06T16:00:58Z`) cut `PostUnexploredWeight` from 0.02 to 0.015 in `home-mixer/params/param.rs` (vm-ranker still 0.02), added `VideoContinuationWeight`, `UserVideoContinuationWeight` and `ProfileVisitSecsWeight` (all 0.0) plus `PostUnexploredIncludeOutOfNetwork` (false) to `vm-ranker/params.rs`, raised `RetrievalCandidatesKafkaMaxCandidates` from 200 to 100000, changed `VMRankerClusterId` from "Experiment6" to "Experiment1", flipped `EnablePopularPostsSource` to true and deleted its three caps, added `EnableHomeExcursionScores` (false) and `EnableUnderTheHood` (false), added the `under-the-hood/` tool, and reworked the visibility-filtering `Verdict`/`Evaluation` model; and the October 9, 2026 sync (commit cb45b550, `last sync 2026-10-08T16:00:35Z`, two commits 35650fb and cb45b55) changed NO action weight and left `vm-ranker/params.rs` untouched, adding only a gated-off video carousel (`EnableVideoCarousel` false, `VideoCarouselFatigueMinutes` 60, `VideoCarouselPosition` 6), a new `VideoCarouselFilter` in the post-selection lineup, `FEED_MODULE_SLOTS` 4 to 5, and a `community_tweet.yml` visibility config plus a `CommunityViewerRemovedLimits` client switch. A sync that changes no weights is still the normal case; say so rather than inventing a change. The October 13, 2026 sync (commit 17c96bf, `last sync 2026-10-13T16:00:30Z`) moved FOUR action weights in `home-mixer/params/param.rs` (`FavoriteWeight` 0.5 to 0.66, `VideoOpenWeight` 0.07 to 0.02, `ContDwellTimeWeight` 0.004 to 0.006, `NotInterestedWeight` -47.52 to -52.272) while `vm-ranker/params.rs` kept the old values, added `ReactWithVideoWeight` (0.0) to both files, `PhoenixOonRepliesRootOnly` (false), `EnableVideoCarouselAuthorDedupe` (false) and `VideoCarouselSemanticIdDedupeLevels` (0) to param.rs, `TopicDppEnabled` (false) to vm-ranker/params.rs, an `AncestorVideoFilter` to the post-selection lineup, and widened `VideoFilter` to drop quotes of video posts; and the October 16, 2026 sync (commit 862a123, `last sync 2026-10-16T16:00:32Z`, checked October 17 2026) changed NO action weight and left `vm-ranker/params.rs` and `xai-value-model/weights.rs` (still 29 entries) untouched, adding ten params to `home-mixer/params/param.rs` (181 to 191: the three `*ZeroFavCodivert*` buckets, `EnablePostEngagers`, and six video-carousel params including f64 `VideoCarouselVideoOpenWeight` `1.0` and `VideoCarouselImmersiveVqvWeight` `0.0`), flipping `EnableAdsAuthorBrandSafetyFallback` false to true, `EnableVideoCarouselAuthorDedupe` false to true and `VideoCarouselSemanticIdDedupeLevels` 0 to 3, inserting a gated-off `ZeroFavCodivertFilter` second in the pre-scoring lineup, and adding an `ImmersiveVideoScorer` between `PhoenixScorer` and `VMRanker` behind the still-false `EnableVideoCarousel`; and the October 20, 2026 sync (commit 7f2ca2b, `last sync 2026-10-20T16:00:34Z`, two commits 74d49a4 and 7f2ca2b, checked October 21 2026) changed NO action weight and left `vm-ranker/params.rs` and `xai-value-model/` entirely untouched, adding eight params to `home-mixer/params/param.rs` (191 to 198: `ShadowTrafficPhoenixClusterAggregationTypes`, `RetrievalValueModelWeights`, `VMRankerSendHistoryTopics`, `HistoryTopicsEnabled`, `HistoryTopicsWindowDays` `28`, `EnableSerendipityStatsExperimentBucket`, `EnableVideoCarouselCandidatesLogging`, and `EnableFairShareRanking`), removing `EnablePhoenixRetrievalFallback`, appending a gated-off `FairShareRankingFilter` last in the pre-scoring lineup, renaming `VideoAspectRatioHydrator` to `VideoMediaHydrator`, and growing `visibility-filtering` `SCALA_FILES` from 6 to 7 with `soft_nsfw.yml` plus a new `TombstoneReason::Bounced`; and the October 23, 2026 sync (commit 6258a15, `last sync 2026-10-23T16:00:34Z`, three commits 989fb91, 07d159b and 6258a15 past 7f2ca2b, checked October 24 2026) changed NO action weight and left `vm-ranker/params.rs` untouched and `weights_mut` at 29 entries, adding four params to `home-mixer/params/param.rs` (198 to 202: `EnableRecentSearchQueriesHydration` `false`, `EnableNewUserSoftNsfwFilter` `false`, `NewUserSoftNsfwFilterMaxAccountAgeSecs` `86400`, `EnableAdsFunnelTrace` `true`), flipping `EnableFairShareRanking` `false` to `true` so `FairShareRankingFilter` is now LIVE in production, flipping `EnableVideoCarouselCandidatesLogging` `false` to `true`, setting `ShadowTrafficPhoenixClusterRates` from `vec![]` to `vec!["Experiment18Fou:0.3".to_string()]`, inserting a gated-off `NewUserSoftNsfwFilter` between `CoreDataHydrationFilter` and `AgeFilter`, adding `RecentSearchQueriesQueryHydrator` and its store client, and adding a thirteenth `LimitedEngagementReason` (`NonCompliant`) plus new notification filtering in `visibility-filtering/filter_notifications.rs`.

## Archived sync blocks moved out of SKILL.md on November 11, 2026 (October 9 through October 20, 2026 syncs)

**October 20, 2026 sync (`last sync 2026-10-20T16:00:34Z`, commit 7f2ca2b, two commits 74d49a4 and 7f2ca2b, checked October 21, 2026), NO ACTION WEIGHT CHANGED.** Every action weight in `home-mixer/params/param.rs` is byte-identical to its Oct 13 2026 value (`FavoriteWeight` `0.66`, `ClickWeight` `0.3`, `ContClickDwellTimeWeight` `0.4`, `ContDwellTimeWeight` `0.006`, `VideoOpenWeight` `0.02`, `NotInterestedWeight` `-52.272`, `ShareViaCopyLinkWeight` `20.0`, and all the rest), `vm-ranker/params.rs` has NO diff at all this sync, and `weights_mut` in `xai-value-model/weights.rs` is still 29 entries, so no new scored action exists anywhere. `home-mixer/params/param.rs` grew from 191 to 198 params: eight additions, one removal.

New params in `home-mixer/params/param.rs` (quoted exactly, type and trailing default):

| Param | Type | Value |
|---|---|---|
| `ShadowTrafficPhoenixClusterAggregationTypes` | `Vec<String>` | `vec!["Experiment16Fou:DENSE_WITH_LONG_DWELL_HOME_EXCURSION".to_string()]` |
| `RetrievalValueModelWeights` | `String` | `""` |
| `VMRankerSendHistoryTopics` | bool | `false` |
| `HistoryTopicsEnabled` | bool | `false` |
| `HistoryTopicsWindowDays` | i64 | `28` |
| `EnableSerendipityStatsExperimentBucket` | bool | `false` |
| `EnableVideoCarouselCandidatesLogging` | bool | `false` |
| `EnableFairShareRanking` | bool | `false` |

Removed param: `EnablePhoenixRetrievalFallback` (bool, was `false`, key `rust_home_mixer_phoenix_retrieval_enable_fallback`). The `PredictionDispatch` and `RetrievalDispatch` egress structs lost their `prod`/`paths`/`enable_fallback_key` fields in the same work, so the xDS shadow-traffic path is gone from the request wiring and the Phoenix client is now the only client a scorer holds (`dispatch.client`, `max_retries_key` `rust_home_mixer_phoenix_xds_max_retries`).

**New `FairShareRankingFilter` is now the LAST pre-scoring filter.** `home-mixer/filters/fair_share_ranking_filter.rs` (170 lines) is appended after `FavHoldoutFilter`, so the pre-scoring vec now ends `..., InventoryHoldoutFilter, FavHoldoutFilter, FairShareRankingFilter`. It is gated by `EnableFairShareRanking` (`false` at this sync; SUPERSEDED October 23, 2026, when the gate flipped to `true` and the filter went live) and is also inert when `query.has_cached_posts`, when `query.scoring_sequence` is `None`, or when the Phoenix ranker kill-switch decider is enabled. When on, it groups candidates by `served_type` (falling back to the first `retrieval_sources` entry) and allocates each group a proportional share of the `PhoenixScoresResultSize` budget (`2800`), dropping the overflow with a largest-remainder rounding pass. The same filter is also appended to `PhoenixScoresPipeline` after `CoreDataHydrationFilter`.

**`VideoAspectRatioHydrator` renamed to `VideoMediaHydrator`.** `home-mixer/candidate_hydrators/video_media_hydrator.rs` replaces `video_aspect_ratio_hydrator.rs` in the post-selection hydrator lineup; the carousel still needs `video_aspect_ratio < 1.0`, so nothing behavioral changed.

**New side effects.** `SerendipityStatsSideEffect` (`home-mixer/side_effects/serendipity_stats_side_effect.rs`) is added to the Phoenix candidate pipeline side-effect vec, and `VideoCarouselCandidatesKafkaSideEffect` plus its `video_carousel_candidates` field are added to the `ForYouCandidatePipeline` wiring, both behind their own params. `home-mixer/util/shadow_scores.rs` is new and `phoenix_experiments_side_effect.rs` was reworked to take a Redis client and the user-action-aggregation client.

**`VideoCarouselFilter` now dedupes against the main feed.** `select_videos` takes the first `RESULT_SIZE` kept candidates as `main_feed` and uses them for the author/semantic/embedding dedupe passes. `EnableVideoCarousel` is still `false` and `home-mixer/params/config.rs` has no diff this sync (`FEED_MODULE_SLOTS` still `5`, `RESULT_SIZE` still `35`, carousel min/max still `3`/`5`).

**Visibility filtering: `SCALA_FILES` 6 to 7, a new tombstone verdict, DDG experiment bucketing.** `visibility-filtering/params.rs` now loads seven Scala configs (`SCALA_FILES: [&str; 7]`), adding `soft_nsfw.yml` alongside `age_verification.yml`, `community_tweet.yml`, `country_specific_nsfw_content_gating.yml`, `freedom_of_speech_not_reach.yml`, `media_visibility_treatments.yml`, and `stale_tweet.yml`. `TombstoneReason` gained a FIFTH variant, `Bounced`, now first in the enum before `SensitiveViewerAgeVerification`, `UpdateAppIos`, `UpdateAppAndroid`, and `LocalRegulations`. `client_switches.rs` gained a `soft_nsfw_new_user_drop` switch keyed `soft_nsfw_tweet_label_new_user_rule_enabled` (default `false`, looked up per viewer id and country), and the feature-switch engine behind visibility filtering now runs on a reloadable abdecider store with DDG experiment bucketing (`DdgExperimentBucketsChooser`, Kafka bucket impressions). `Decided<T>` now also carries a `RuleId` (`id`), so every verdict names the rule that produced it. Country lists are unchanged (age-verification/tombstone 30 codes, `LocalRegulations` `in`), and `LimitedEngagementReason` is unchanged at twelve variants. Most of the sync is a large rework of the visibility-filtering rule engine, hydration, quote handling (`visibility-filtering/quote.rs`, 989 lines new), and the abuse-enforcement backfill service; no `FilteredReason` variant was added and no ranking behavior changed.

**October 16, 2026 sync (`last sync 2026-10-16T16:00:32Z`, commit 862a123, checked October 17, 2026), NO ACTION WEIGHT CHANGED.** Every action weight in `home-mixer/params/param.rs` is byte-identical to its Oct 13 2026 value (`FavoriteWeight` `0.66`, `ClickWeight` `0.3`, `ContClickDwellTimeWeight` `0.4`, `ContDwellTimeWeight` `0.006`, `VideoOpenWeight` `0.02`, `NotInterestedWeight` `-52.272`, and all the rest), and `vm-ranker/params.rs` has NO diff at all this sync (still 51 params, still the older `FavoriteWeight` `0.5` and `VideoOpenWeight` `0.07`). `weights_mut` in `xai-value-model/weights.rs` is still 29 entries, so no new scored action exists anywhere. `home-mixer/params/param.rs` grew from 181 to 191 params; all ten additions are below.

New params in `home-mixer/params/param.rs` (quoted exactly, type and trailing default):

| Param | Type | Value |
|---|---|---|
| `ViewerZeroFavCodivertIsTreatment` | bool | `false` |
| `AuthorZeroFavCodivertIsTreatment` | bool | `false` |
| `AuthorZeroFavCodivertIsControl` | bool | `false` |
| `EnablePostEngagers` | bool | `false` |
| `EnableVideoCarouselEmbeddingDedupe` | bool | `true` |
| `VideoCarouselEmbeddingDedupeThreshold` | f64 | `0.72` |
| `VideoCarouselVideoOpenWeight` | f64 | `1.0` |
| `VideoCarouselImmersiveVqvWeight` | f64 | `0.0` |
| `VideoCarouselImmersiveClusterId` | String | `"Experiment3Fou"` |
| `VideoCarouselImmersiveAggregationType` | String | `"IMMERSIVE_LONG_DWELL"` |

Changed defaults in the same file:

| Param | Old (Oct 13 2026) | New (Oct 16 2026) |
|---|---|---|
| `EnableAdsAuthorBrandSafetyFallback` | `false` | `true` |
| `EnableVideoCarouselAuthorDedupe` | `false` | `true` |
| `VideoCarouselSemanticIdDedupeLevels` | `0` | `3` |

**New `ZeroFavCodivertFilter` added to the pre-scoring lineup.** `home-mixer/filters/zero_fav_codivert_filter.rs` (110 lines) is inserted immediately after `DropDuplicatesFilter` and before `CoreDataHydrationFilter`, and is enabled by `ViewerZeroFavCodivertIsTreatment` (`false`). When on, it keeps a candidate whose `served_type` is `ServedType::ForYouPhoenixRetrievalZeroFav` AND whose every `retrieval_sources` entry is also `ForYouPhoenixRetrievalZeroFav` (a zero-favorite post found only by the zero-fav retrieval path) only when the author is bucketed `treatment` by `AuthorZeroFavCodivertIsTreatment` via `AuthorRulesEvaluator`; `control` and `unbucketed` authors lose those candidates. It emits a `ZeroFavCodivert` metric labeled by `author_bucket`. Default off, so production behavior is unchanged.

**New `ImmersiveVideoScorer` added between `PhoenixScorer` and `VMRanker`.** The scorers vec now reads `[phoenix_scorer, immersive_video_scorer, vm_ranker]`. `home-mixer/scorers/immersive_video_scorer.rs` is enabled only when `!query.has_cached_posts` AND `video_carousel::is_enabled(query)` AND `video_carousel::ranks_by_immersive_scores(query)` AND the query carries an `immersive_columnar_scoring_sequence` (new `home-mixer/query_hydrators/immersive_scoring_sequence_query_hydrator.rs`), so it is inert while `EnableVideoCarousel` is `false`. It writes `candidate.immersive_scores` from a Phoenix prediction request sent to `VideoCarouselImmersiveClusterId` (`"Experiment3Fou"`).

**Video carousel dedupe knobs turned on, carousel still gated off overall.** `video_carousel::select_videos` now also takes `VideoCarouselVideoOpenWeight` (`1.0`), `VideoCarouselImmersiveVqvWeight` (`0.0`) and an optional `Option<f64>` embedding-dedupe threshold (`VideoCarouselEmbeddingDedupeThreshold` `0.72`, passed only when `EnableVideoCarouselEmbeddingDedupe` is `true`), fed by a new `home-mixer/candidate_hydrators/video_embedding_hydrator.rs` backed by `ManhattanPostV8SearchEmbeddingClient` (falls back to a no-op client when unavailable). `EnableVideoCarousel` itself is still `false`, so the carousel still does nothing in production.

**New hydrator and client wiring.** A new `home-mixer/candidate_hydrators/post_engagers_hydrator.rs` plus `PostEngagersClient` / `ProdPostEngagersClient` / `MockPostEngagersClient` back the new `EnablePostEngagers` param (`false`). `home-mixer/params/config.rs` is unchanged this sync (`FEED_MODULE_SLOTS` still `5`, `VIDEO_CAROUSEL_MAX_VIDEOS` `5`, `VIDEO_CAROUSEL_MIN_VIDEOS` `3`, `VIDEO_CAROUSEL_EXTRA_CANDIDATES` `30`, `RESULT_SIZE` `35`).

**Visibility filtering: no rule, verdict, or country-list change.** `visibility-filtering/params.rs` gained only helper methods on `CountryList` (`names_by_default`, `listed_by_default`) plus module moves; `limited_actions_copy.rs` and `limited_actions_policy.rs` moved under `params/`. The bulk of the sync is a rework of the visibility-filtering rule engine (`rules/engine.rs`, `rules/rule_spec/features/*`, `rules/legacy_table.rs`, `hydration/`) that added no verdict variant, no `LimitedEngagementReason`, and no `FilteredReason`. One model change worth knowing: `Evaluation::Complete { verdict }` now also carries `fail_open_defaults: Hydrators`, so a Complete evaluation can name hydrators that failed open, and `LimitedEngagement::add` returns a `bool` for whether the reason was newly added. All five country lists are byte-identical to Oct 13 2026 (age-verification/tombstone 30 codes, NSFW gating 16 codes, `LocalRegulations` `in`), and `SCALA_FILES` is still 6.

**October 13, 2026 sync (`last sync 2026-10-13T16:00:30Z`, commit 17c96bf), FOUR ACTION WEIGHTS CHANGED.** `home-mixer/params/param.rs` moved four production weights, the first action-weight change since Oct 6 2026:

| Param (in `home-mixer/params/param.rs`) | Old (Oct 9 2026) | New (Oct 13 2026) |
|---|---|---|
| `FavoriteWeight` | `0.5` | `0.66` |
| `VideoOpenWeight` | `0.07` | `0.02` |
| `ContDwellTimeWeight` | `0.004` | `0.006` |
| `NotInterestedWeight` | `-47.52` | `-52.272` |

Note the two files now DISAGREE on these four: `vm-ranker/params.rs` still reads `FavoriteWeight` `0.5`, `VideoOpenWeight` `0.07`, `ContDwellTimeWeight` `0.004` and `NotInterestedWeight` `-47.52`, so `home-mixer/params/param.rs` is the file that moved. `ClickWeight` (0.3), `ContClickDwellTimeWeight` (0.4), `PostUnexploredWeight` (0.015 in home-mixer, 0.02 in vm-ranker) and every other action weight are unchanged.

New f64 action-weight-style param in BOTH `home-mixer/params/param.rs` and `vm-ranker/params.rs`: `ReactWithVideoWeight` `0.0` (key `rust_home_mixer_react_with_video_weight`). It is wired into `compute_weighted_score` in `xai-value-model/scoring.rs` as `apply(scores.react_with_video_score, weights.react_with_video)`, and `weights_mut` in `xai-value-model/weights.rs` grew from 28 to 29 entries. Default `0.0`, so it scores nothing in production today; it is the knob to watch.

New params in `home-mixer/params/param.rs`: `PhoenixOonRepliesRootOnly` (bool, `false`), `EnableVideoCarouselAuthorDedupe` (bool, `false`), `VideoCarouselSemanticIdDedupeLevels` (u32, `0`). New param in `vm-ranker/params.rs`: `TopicDppEnabled` (bool, `false`, key `rust_home_mixer_vm_ranker_topic_dpp_enabled`). `vm-ranker/params.rs` grew from 49 to 51 params.

**New `AncestorVideoFilter` added to post-selection.** `home-mixer/filters/ancestor_video_filter.rs` is inserted between `AncillaryVFFilter` and `DedupConversationFilter`, so the post-selection vec now reads `VFFilter, AncillaryVFFilter, AncestorVideoFilter, DedupConversationFilter, VideoCarouselFilter`. It is enabled by `query.exclude_videos` and removes any candidate whose `ancestor_has_video == Some(true)` (a post whose parent carries a video). A new `home-mixer/candidate_hydrators/ancestor_video_hydrator.rs` (172 lines) hydrates that field.

**`VideoFilter` widened.** `home-mixer/filters/video_filter.rs` now removes a candidate when it has a video OR its quoted post does: `has_video` is `candidate.min_video_duration_ms.is_some() || candidate.quoted_max_video_duration_ms.is_some()`, so when a request excludes video a quote of a video post is now dropped too (new `quoted_max_video_duration_ms` field on the candidate).

**Video carousel dedupe added.** `home-mixer/util/video_carousel.rs` gained a `take_distinct` pass: `select_videos` now takes `dedupe_by_author` and `semantic_id_dedupe_levels` and skips videos that repeat an author (when `EnableVideoCarouselAuthorDedupe` is true) or that share a semantic-id prefix of the given depth (when `VideoCarouselSemanticIdDedupeLevels` is above 0). Both default off/zero, and `EnableVideoCarousel` is still `false`, so the carousel still does nothing in production.

**`OONRetweetReplyFilter` root-only gate added.** The filter now also reads `PhoenixOonRepliesRootOnly` (`false`): when it is true, an out-of-network reply is kept only if it replies to the conversation root (`in_reply_to_tweet_id == conversation_id`). Both gates off by default.

**Pipeline and visibility params otherwise unchanged.** `home-mixer/params/config.rs` is byte-identical this sync (`FEED_MODULE_SLOTS` still `5`, `VIDEO_CAROUSEL_MAX_VIDEOS` `5`, `VIDEO_CAROUSEL_MIN_VIDEOS` `3`), `visibility-filtering/params.rs` and the rest of `visibility-filtering/params/` have NO diff, and the pre-scoring filter list is unchanged. The `brazil_2026_election_filter.rs` account list was refreshed (README now says updated October 13, 2026); the bulk of the sync is an unrelated rework of `abuse-enforcement-service/`. Every value above is quoted exactly from `home-mixer/params/param.rs` at commit 17c96bf.

**October 9, 2026 sync (`last sync 2026-10-08T16:00:35Z`, commit cb45b550), NO action weight changed.** Two commits landed since the Oct 6 check (35650fb, cb45b55) and neither moved an action weight. The whole action-weight block in `home-mixer/params/param.rs` is byte-identical to Oct 6 2026, including `PostUnexploredWeight` `0.015` and the three Sept 30 moves, and `vm-ranker/params.rs` has NO diff at all this sync (still 49 params). The new work is a video carousel.

New params in `home-mixer/params/param.rs` (quoted exactly, type and trailing default):

| Param | Type | Value |
|---|---|---|
| `EnableVideoCarousel` | bool | `false` |
| `VideoCarouselFatigueMinutes` | u32 | `60` |
| `VideoCarouselPosition` | u32 | `6` |

New and changed constants in `home-mixer/params/config.rs`:

| Constant | Value | Note |
|---|---|---|
| `VIDEO_CAROUSEL_EXTRA_CANDIDATES` | `30` | new |
| `VIDEO_CAROUSEL_MAX_VIDEOS` | `5` | new |
| `VIDEO_CAROUSEL_MIN_VIDEOS` | `3` | new |
| `FEED_MODULE_SLOTS` | `4` | changed to `5` |

**New `VideoCarouselFilter` added to post-selection.** `home-mixer/filters/video_carousel_filter.rs` is appended as the LAST post-selection filter, after `DedupConversationFilter`, so that vec now reads `VFFilter, AncillaryVFFilter, DedupConversationFilter, VideoCarouselFilter`. It is gated by `video_carousel::is_enabled`: `EnableVideoCarousel` (false by default) AND a `ForYou` request AND `query.video_carousel_eligible`. When on, `home-mixer/util/video_carousel.rs` selects up to `VIDEO_CAROUSEL_MAX_VIDEOS` (5) vertical videos (`video_aspect_ratio < 1.0`) that are non-reply top-level posts carrying a Phoenix `video_open_score`, sorts them by that score, and returns nothing unless it finds at least `VIDEO_CAROUSEL_MIN_VIDEOS` (3). Supporting new files: `home-mixer/util/video_carousel.rs`, `home-mixer/candidate_hydrators/video_aspect_ratio_hydrator.rs`, `home-mixer/util/urt/video_carousel_marshaller.rs`, and a new `video_carousel_extra` field on the candidate. Default OFF, so it changes nothing in production today; it is the knob to watch if X starts surfacing a vertical-video carousel.

**Ad-side change.** `AdAdjacentServedFilter` now records `DroppedAd` entries into `query.ad_drops` (new `home-mixer/ads/drops.rs`) with `AdDropReason::ServedNeighbour` and `AdDropReason::Truncated`. This is ad accounting, not organic ranking.

**Visibility filtering.** `visibility-filtering/params.rs` grew `SCALA_FILES` from 5 to 6, adding `community_tweet.yml` alongside `age_verification.yml`, `country_specific_nsfw_content_gating.yml`, `freedom_of_speech_not_reach.yml`, `media_visibility_treatments.yml`, and `stale_tweet.yml`. `visibility-filtering/params/client_switches.rs` added a `CommunityViewerRemovedLimits` switch keyed `community_tweet_viewer_removed_limited_actions_rules_enabled` (field `community_viewer_removed_limits`), so a removed community tweet can now carry a limited-actions prompt. The `CountryList` country lists are unchanged. Rule internals were reworked (`rules/tweet_rules.rs`, `rules/registry.rs`, `rules/rule_spec.rs`, `treatment.rs`, `staging/recording.rs`) and a new golden-corpus file `rules/golden_corpus/local_tweet.rs` was added, but no verdict variant or `LimitedEngagementReason` was added.
