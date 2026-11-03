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
