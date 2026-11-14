---
name: model-evaluation
description: Use when Vinny asks if an LLM fits a task. Evidence first.
version: 1.0.0
author: Vinny Barreca
license: MIT
metadata:
  hermes:
    tags: [models, evaluation, benchmarks, ollama, research]
    related_skills: [nvidia-free-model-selector, model-tuning-optimization, llama-cpp]
---

# Model evaluation

## When to Use

- "Is <model> good at coding / writing / X?"
- "How does <model> compare to <model> for my use case?"
- "What is <model>'s real size / spec?" (e.g. Ollama says one number, the site says another)
- Any request to judge a model's fitness for a task before using it.

Procedure when Vinny asks "is model X good at task Y" or "how is X for Z":

1. **Verify the model's identity and specs first (primary sources only).**
   - Official model card / library page / technical report for parameter counts, context window, architecture, pricing.
   - Local truth: `ollama show <model>` or `POST http://127.0.0.1:11434/api/show` returns `general.parameter_count`, this metadata can disagree with the published total for MoE models (it counts tensors present in the serving checkpoint, not the advertised total). Report both numbers when they differ; do not silently pick one. See `references/verifying-model-specs.md`.
   - Third-party indexes (routing sites, leaderboards, aggregate trackers) routinely list wrong sizes, a 1.02T model shown as "116B" in one index. Never cite an aggregate index for specs.
   - When he asks which number is **actually true** (not just what each source says), report-both is not the finish, run the three primary-source checks in `references/verifying-model-specs.md` (HF safetensors total, config.json arithmetic, artifact-size cross-check) and name the verdict with its evidence.
2. **Gather two evidence classes: independent hands-on reviews FIRST.**
   - Real-user reports: forums, Reddit, YouTube testers running the model on actual work ("worse than Qwen in my tests", "3-5x slower", refusal behavior). These carry more weight with him.
   - Benchmarks second, clearly labeled as benchmark numbers, always paired with any independent result that contradicts them.
3. **Map the findings onto HIS stated use case, not the generic category.** He asked about coding → tie to agent coding / SEO content pipelines; asked about writing → tie to social posts, hooks, article drafts, brandable frameworks. Name which sub-metrics matter for that use (hooks for posts, length adherence for character limits, originality for scroll-stopping takes) and which don't.
4. **Give the practical try-it cost.** Most are cheap ($0.14-0.28/M tokens); the honest closing is that running it on his real work for a week costs nothing meaningful.

## Rules

- **Benchmarks are one input, never the verdict.** He has stated plainly that he does not trust benchmark scores. Lead with hands-on/real-task evidence; cite benchmarks only as secondary context, labeled as such. If a benchmark and a hands-on test disagree, the hands-on test wins the sentence.
- **One claim, one check.** No capability claim leaves the reply without the source that supports that exact claim (paper, measured API output, named reviewer's test). Estimates labeled as estimates.
- **No unsolicited recommendations about what he should run or switch to.** Answer what was asked: what it does well, where it's weak, for the task named. The "try it yourself" line comes only after he engages on fit.
- Direct, no preamble, no capability hedging. When a number can't be verified, say what could not be checked instead of guessing.
- **Speed/capability reports are serving-path dependent.** Published hands-on results ("3-5x slower") come from whatever route and quant the reviewer used; his own run on a different serving path can legitimately contradict them. State which path produced which observation, never argue his direct experience against a report.
