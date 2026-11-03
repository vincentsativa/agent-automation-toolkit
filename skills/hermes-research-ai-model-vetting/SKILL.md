---
name: ai-model-vetting
description: "Vet AI model claims: size, origin, benchmarks, build efficiency."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [models, benchmarks, efficiency, usage, ollama]
    related_skills: [hermes-provider-configuration, model-tuning-optimization]
---

# AI Model Vetting

## Trigger
Use when Vinny asks about a model's size, who made it, whether it's actually good, whether a benchmark/launch claim holds up, or how much more efficient one build is than the previous one and whether it is using less of his account. Especially stealth/anonymous releases (e.g. OpenRouter `stealth/*` models) and dated provider build tags.

## Core Principle
**"Does it do the work?" is the only question that matters.** Size-adjusted bragging rights ("impressive for a 30B") are a lab's problem, not a user's. A model that fumbles simple tasks is a model you bail on, regardless of parameter count. Vinny's real-world test (two simple script tasks) beats any benchmark.

## Read-Only Research Rule (applies before every other step)
A question about a model is a research question, and it is answered from published sources. It never requires touching Vinny's machine.

- **Never pull, install, or remove a model to inspect it.** `ollama pull` writes gigabytes to his disk and changes his store. Size, context, modalities and origin are published on the vendor's model page and API docs.
- **Never create a virtualenv or pip install anything to complete a lookup.** Building an environment is a machine change he has to order, and it is not part of answering a question.
- **Never read a credential file to authenticate a lookup.** `~/.hermes/config.yaml` is not a research input, and his API keys are never sent to a third party so you can fetch a public page.
- **Never sweep his home directory, Ollama store, or session logs to "check" something** as part of a model question. That reads as rummaging and it is not the task.
- **If the fetch library is not importable in the active interpreter, use the fetching CLI on PATH or the search and extract tools.** Do not build an environment to enable one path.
- **The one exception is a build he is already running and wants measured.** Then the provider's live catalog and usage API are the point, and that is the metering section below. Those commands exist to measure his own account, never to answer "how big is model X".

## Benchmark Skepticism
- **Always check sample size.** A headline score on a tiny subset is marketing. Example: Ox Alpha's "80% DeepSWE, beats Claude/GPT" was a 10-task slice of a 113-task benchmark, one task moves the score ~10 points. The full-set independent run was ~63%, mid-pack.
- **Subset vs full-set is the single most common hype mechanism.** Ask: how many tasks, out of how many total?
- **Community-reported numbers are unverified.** Treat them as estimates, not specs.
- **A version bump is not a license to carry numbers forward.** Before reusing a prior build's benchmark/hallucination figures for a new release, establish whether it's the SAME weights re-post-trained (numbers roughly carry) or a ground-up architecture redesign (they do NOT, no published figure exists until someone re-runs it). DeepSeek V4 Flash 0731 was a re-post-train of the April weights; V4.1 Flash was a new architecture. Don't assume the 84% hallucination rate of 0731 applies to V4.1, that's inference, not measurement. Say "no published number yet" rather than guessing.
- **Hallucination rate and accuracy are separate axes on AA-Omniscience.** A model can cut its hallucination rate (better at saying "I don't know") while raw accuracy stays flat, that's a calibration/hedging gain, NOT a knowledge gain. DeepSeek V4 Flash 0731 dropped hallucination 96%→84% with accuracy unchanged at 37%. When a vendor touts a "reduced hallucination" improvement, check whether accuracy moved too; if it didn't, the model learned to refuse, not to know.

## Estimating Model Size (when architecture is undisclosed)
- **Active-params ratio is the tell.** Real MoE models run ~5–15% active (GLM-4.6: 355B total / 32B active, ~9%). If a model reports ~40B active, total is almost certainly 400–800B, NOT 120B. A 120B model with 40B active isn't a MoE, it's a dense model with a weird label.
- **Decoding speed is a fingerprint.** Matching a known large MoE's speed (within ~6%) is the signature of *being* a large MoE. A small dense model would be *faster*, not within a few percent.
- **"Didn't have enough compute" → undertrained, NOT smaller.** A compute-constrained lab produces a big model trained on too few tokens (big params, mid performance), not a small model. "It stinks" is consistent with both; it doesn't discriminate. Speed and tokenizer do.

## Forensic Attribution (who made it)
- **Tokenizer match is the strongest signal.** Vocabulary boundaries, byte-fallback behavior, merge rules, a 30/30 match is a fingerprint, not a coincidence. Two independent models don't accidentally share a tokenizer.
- **Error codes in stack traces** are hard evidence (e.g. GLM's error code 1214).
- **Secondary hard signals to collect alongside the tokenizer:** the ID format inside API responses, and how the gateway routes the slug (a stealth model listed in the same serving pool and naming scheme as a known lab's entry is that lab's stack). Same-gateway delta identity, matching counts against more than one generation the same lab serves, strengthens it further.
- **Self-identification is noise, always.** These models are told to stay anonymous, so they guess, and the guess is unstable: different languages produce different answers ("ChatGPT" in English, "Qwen" in Chinese), and an early "it admitted it was X" report is usually just that noise. Models are also trained on each other's outputs, so a self-report is worthless even when it sounds confident. Never cite self-ID as evidence in either direction.
- **Soft signals are weak:** "response style," "chain-of-thought cadence," "writing style" are hand-wavy and bs-adjacent. Don't lean on them.
- **"99% certain" from a researcher is still not proof.** Report the direction of evidence, not the confidence number.
- **State the caveat the fingerprinters state themselves.** A tokenizer or serving match proves whose stack answered, NOT whose brain is inside. Open-weight bases make that hole real: anyone can take an open base, extend or retrain it, and serve it on a compatible stack, and every fingerprint still lines up. When the base is open weights, say the serving setup points at the lab while remaining compatible with a third party building on the base.

## Provenance vs Quality (fingerprints measure the plumbing, not the thinking)
Provenance evidence and quality evidence answer different questions, and one never settles the other.
- **A tokenizer or routing match cannot prove a quality ceiling.** It says whose infrastructure served the tokens. It says nothing about how well the model reasons.
- **Vinny's hands-on read outranks the forensic consensus.** He tests the thing; the fingerprint threads never do. If he says it is too good to attribute to the implicated lab, that is a real data point the fingerprint crowd cannot see, and it points at the build-on-open-weights case rather than being a rebuttal to the fingerprint.
- **Reconcile, don't reverse.** When his read and the evidence pull apart, the answer is both true at once: same stack, higher-quality head. Do not walk back the evidence to agree with him and do not argue him out of what he used.
- **A quiet in-product launch days after a free anonymous run corroborates the data-play thesis** rather than refuting it. Vendors collect live-usage data under a codename, then ship the checkpoint under their own name with no model card. That is the pattern, not a coincidence.
- **Never present a community consensus as confirmation.** "Likely X, unconfirmed" is the honest frame until the vendor says so; most stealth slots never get a first-party reveal.

## Feature & Modality Verification (does it actually DO the thing)
Vetting a model includes its capabilities, not just its quality. Read them off the vendor's own API docs, never off assumption, the chat UI, or a legacy model name.
- **Check the vendor's feature table for the CURRENT model alias.** Vendor docs list per-model capability rows (Vision, Tool Calls, JSON Output, context length, pricing). That table is the spec.
- **Legacy model names are aliases, and alias capabilities go stale.** A retired model name is usually still accepted by the API but served by the newest model at the newest price. Never carry a capability claim (or its absence) from the legacy name forward, resolve what the alias maps to TODAY and read that row.
- **A capability difference between tiers is normal and worth stating explicitly.** In one vendor's lineup, Flash has vision while Pro does not; naming which tier has what prevents a wrong blanket answer.
- **Do not infer the session model's capabilities from how a runtime tool behaves.** An image tool can route to a different provider entirely from the session model, so "the tool used model X" says nothing about model Y. When asked whether a model has a feature, answer from the vendor docs, and treat the runtime's routing as a separate config question.
- **Verify against the docs before answering, even when confident.** One vendor doc fetch settles it; a hedge ("I can't confirm without testing") is the wrong answer when the spec is public.

## Stealth Deployment = Data Play
An anonymous free-week model with prompt retention is usually a **data-gathering run, not a product launch.** The lab is harvesting real-world interaction data to retrain/align before a formal release. The anonymity avoids PR/accountability, not attribution, they leave fingerprints in the tokenizer anyway.
- **"It stinks now" is the wrong tense.** It's a snapshot mid-development. But you still evaluate what it does *today*, not what it might become after retraining.
- **Retraining is a band-aid, not a fix** for pretraining-level compute starvation. Interaction data helps alignment, not the missing pretraining compute.

## Serving Capacity / Cost-to-Serve (a model nobody can run doesn't matter)
Quality is only half the vet. A model that's good but can't be served at scale is dead weight, no matter how smart. Kimi K3 (2.8T) is the canonical case: great on paper, but nobody has enough compute to run it.
- **A waitlist on a flagship is a capacity admission, not exclusivity.** You gate a model behind a waitlist because you can't handle demand. When the waitlist lifts, the symptom just changes name, the chatbot still returns "busy" on a basic greeting. Same problem, different symptom.
- **"Busy" on a trivial request (saying hello) is ground truth.** It beats any pricing page or benchmark. If you can't get a greeting served, the model isn't really serving anyone.
- **Check the price card against the efficiency leader.** Kimi K3 at $3/$15 per 1M tokens is ~5x input / 6x output of its own prior gen (K2.6 at $0.95/$4), while DeepSeek V4 Flash is $0.14/$0.28, undercutting every Kimi tier by a wide margin. A 4x efficiency gap on GPU time/model size (DeepSeek flash vs GLM flash) is a whole tier of cost, not a rounding error.
- **Self-host feasibility is part of the vet.** Open weights don't help if running them needs a 1.5TB-memory cluster. "Weights are out" ≠ "anyone can run it."
- **The winner isn't the smartest model, it's the one people can actually afford to run.** DeepSeek's lead is efficiency + availability (it answers when you call), not raw capability.

## Efficiency Measured Against the Meter That Actually Bills
"How much more efficient is this build than the last one" is a billing question, not a throughput question, and the two diverge. Establish the meter FIRST, then measure.

- **Resolve the model from the provider's live catalog before evaluating it.** This bullet is for a build Vinny already runs and asks about; when he asks about a model he has not run, read the vendor's published catalog on the web instead, never his local store. A build tag the user is actively running is real by definition; never open with doubt about its existence. `GET /v1/models` and `GET /api/tags` on the provider return the fields that decide the question: byte size, digest, context window, modalities, reasoning levels. Two tags with the SAME byte size and different digests are one model rebuilt, not a smaller or more efficient one, and no efficiency claim survives that comparison. Dated tags (`:1017`, `:0813`) are rebuild stamps, not versions.
- **Ask what the account meters before benchmarking anything.** A provider's usage endpoint can meter requests, tokens, GPU-seconds, or nothing visible. If it meters requests, a model that emits more tokens per answer costs the user nothing, and a benchmark of tokens-per-second answers a question nobody asked. Read the usage API's actual payload keys and quote only those.
- **Read daily buckets, never the period total, when the claim is "usage is down."** A 30-day total is dominated by pre-switch history and will read as "the old model is burning your account" even the day after a switch. Pull `group_by=model` with daily granularity, locate the date the active model changed (the new tag appears with near-zero counts, the old one stops), and compare the last few days on each side. Attribute the change to the switch, and say the request counts did not fall if they did not.
- **Separate response behavior from metered usage and label which one you measured.** Latency and completion tokens describe how the model answers; they are not the bill unless the provider says so. When a synthetic benchmark and the user's own observed usage disagree, the user's observation is data: name the confounders the metric explains (model switch, workload change, unreported reasoning tokens) and state plainly which part you cannot see.
- **Re-run the comparison at matched effort before claiming a build is slower or faster.** Reasoning effort (and whether reasoning tokens are billed/reported) swings output length more than a version bump does. Compare at the same effort setting and the same prompt set; if `completion_tokens_details` is absent, reasoning tokens are invisible and the token delta is not a clean throughput measure.
- **On a flat-rate or exempt plan, efficiency gains do not convert to money.** Say so in the same breath as the numbers, because the practical effect is speed and context headroom, not a lower bill. The only saving left is fewer requests for the same work, which is a workload property, not a model property.

Concrete endpoint recipes, payload keys, and the model-catalog commands: `references/provider-usage-metering.md`.

## Release Rumors ("V5 incoming"-type chatter)
- **Trace the rumor to its seed phrase before repeating it.** Most next-gen rumors are media extrapolation of one vague official line (e.g. a price-hike announcement saying "will develop stronger large models") stitched with supply-chain whispers. If the vendor never named the version or the date, say so, "September release" and benchmark-target claims are secondhand even when widely repeated.
- **A generation's age is measured by its lineup rollout, not the flagship's GA date.** A line is "just started" if variants (vision builds, experimental tiers, distills) are still landing on it. Labs fully milk a generation before replacing it; a next-gen rumor weeks after the current gen's GA contradicts the lab's own release rhythm, weight that rhythm over the rumor.
- **Two channels outrank all coverage.** For release facts, the vendor's official docs site and official social account beat every tracker, blog, and status page. Trackers can be useful for confirmed-vs-rumor tables, but they are secondary.

## Market/Competition Analysis (pricing strategy, not model quality)
When Vinny asks who's winning or how a market moves, answer from the pricing card plus release cadence, not vibes:
- **The cheap competent tier eats the flagship's lunch when the gap in real workloads is small.** If a Flash-tier model covers most workloads at 1/10 the price, the flagship tier survives on prestige and hardest-reasoning demand only. Frame market share from that axis.
- **A lab's refusal to match a price tier is structural, not stubborn.** Cost base (GPU fleets, payroll, investor margin promises) and a bundle/platform moat thesis explain it; the bet is "reframe the fight away from price." Predict which lab breaks ranks first from margin pressure, not from statements.
- **Watch for the strategy-change signal:** the first major closed-source provider matching the efficiency leader's per-token price. Until that happens, price talk from incumbents is marketing.

## Open-Weight Promise vs Open-Weight Release (verify at check time, not at announcement)
A vendor announcing "weights will be released on <date>" has shipped an API, not an open model. The gap between the two is where coverage goes wrong, and a promised date is routinely reported as a completed drop.
- **Verify on the vendor's own Hugging Face org page, not on search results.** Search snippets report a promised release as having already happened. The org's model list sorted by newest upload settles it: no repo, or a repo holding only a `.gitattributes` placeholder with no model card and no license, means the weights have not landed.
- **The org's newest upload timestamp is the tell.** If the most recent upload predates the announcement by months, nothing new shipped regardless of what coverage says.
- **No license named means no license.** An open-weight promise with no stated license is not an openness claim. Do not assume the lab's prior permissive license carries forward to the new checkpoint.
- **Until weights land, every benchmark number is vendor-reported and non-reproducible**, including the competitor rows. State that in the same breath as the score.
- **A weights release changes the price comparison entirely.** While a model is API-only the comparison is token price against token price. Once permissive weights exist the question becomes self-hosting cost, and a token price that looked steep can be cheap against owned hardware. Always name the pending date so the verdict is dated rather than absolute.

## Is It Worth Switching: the incumbent is the bar
When asked whether a model is worth using or worth paying for, the comparison that matters is against what Vinny already runs, not against the top of the chart.
- **A price premium over the incumbent is justified only by a clear performance win.** If the new model costs more per token or per task and wins only on an aggregate index by a few points, say the premium is not justified for most workloads. He reaches that conclusion himself anyway; reaching it first is the useful answer.
- **Lead with the rows that decide it:** cost per task, output speed, time to first token, end-to-end time, and whether weights are already public. Parameter counts and context length do not decide a switch.
- **Index points are not work.** A small index gain bought at a multiple of the price and roughly twice the wall-clock is a loss on his terms, and he has said he does not believe the benchmarks in the first place.
- **Name the one workload where the premium does pay**, if there is one, by benchmark family rather than in general. A usable verdict is narrow, not blanket.
- **Free access is temporary by default.** A preview-tier free endpoint is a promotion, not a pricing tier. Quote the paid list price as the number that will apply, and say the free window's terms are unconfirmed unless the vendor states a duration.

## Vinny's Standing Model Roles (content pipeline, verified against live benchmarks)
- GLM-5.3 (full) does research, fact-checking, and builds detailed outlines; DeepSeek V4.1 Flash writes the article from the outline; DeepSeek Flash is the coding/agent workhorse. Recommend switches only into roles the data supports, and only as experiments, the pipeline itself is confirmed correct per benchmark family.
- Writing skill is a separate axis that coding benchmarks never measure. A flash tier can lose every coding benchmark and still lead the flagship on prose (writing-Elo boards show it; hooks are usually the biggest gap, consistency the smallest). When his question concerns content work, pull writing-benchmark rows, not code-agent rows.

## Pitfalls
- **Don't convert a fact question into a machine audit.** Pulling the model to measure it, spinning a venv to enable a fetch, and grepping config for an API key all look like diligence and read as rummaging, and the answer was on the vendor page the whole time. A model question is answered with a search, full stop.
- Don't let "impressive for its size" reframe a mid model as notable. Size is only interesting if it's small AND good; the forensics usually point big.
- Don't confuse load-induced *slowness* with load-induced *dumbness*. Contention hits latency/throughput, not weights. The one way load degrades quality is silent routing to a smaller/quantized variant, possible but would break the tokenizer/speed fingerprint.
- Don't evaluate a model on what it might become. Unfalsifiable until they ship.
- Don't answer a "why is nobody talking about it" question with press coverage. Read the gateway's own usage table: if the token volume sits in coding agents rather than the timelines, the model is working, just out of the conversation. Traffic location explains the silence, not a quality problem.
- Don't treat an early outage as a verdict. Short-lived 5xx/empty payloads from a stealth model are worth one retry with a different client before you conclude anything; a raw JSON endpoint fetched through an HTML-oriented client can return a non-JSON body that looks like a model failure and is not one. Retry the probe rather than reporting the failure.
- **Read the effort qualifier inside a vendor comparison table before repeating the spread.** A lab that runs its own model at a middling effort setting while the rivals run at maximum manufactures a smaller gap than the harness difference. Check whether every row used the same effort level, and say so when it did not.
- **An accurate measurement of the wrong metric is still a wrong answer.** Token counts and tok/s are cheap to produce and easy to present as an efficiency verdict; they are the wrong axis when the user pays per request or per GPU-second. Confirm the meter first, and if you already answered on the wrong axis, say which axis the numbers actually describe rather than restating them louder.
- **A launch with great self-reported benchmarks and bad real-world feedback is not a contradiction.** Internal benchmarks run at max effort with no token limits measure capability in ideal conditions; community complaints usually expose the serving economics (quota burn, latency, cost-to-serve), which never appears in the launch table. Weigh both axes separately and expect the gap to be economic, not capability.
- **Do not accept an aggregated index as the whole comparison.** Two models a few index points apart usually separate sharply on individual benchmark families, and one of those families is the user's actual workload. Pull the per-benchmark rows.
