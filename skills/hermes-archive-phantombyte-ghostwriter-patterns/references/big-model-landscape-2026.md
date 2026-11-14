# Big-Model Landscape (Aug 16, 2026)

When Vinny reaches for a larger model, the two candidates are DeepSeek V4 Pro 0813 and GLM-5.3. Both dropped within 48h of each other (Pro 0813 on Aug 12-13, GLM-5.3 on Aug 14), both are post-training plays on existing bases, both claim "narrowing the gap with Fable 5."

## DeepSeek V4 Pro 0813
- The GA release that took Pro out of preview (same API name, `deepseek-v4-pro` now serves 0813).
- Agent capabilities jumped from "basically unusable" in preview to rivaling Claude Fable 5: DeepSWE 12.8→62.7, NL2Repo 38.5→61.5, DSBench-Hard doubled to 67.2.
- Competitive with Opus 4.8, weaker than Fable 5, ~20x cheaper.
- 1.6T total / 49B active MoE, 1M context, 384K max output.
- Caveats: independent benchmarks (OpenRouter/AA index ~45.3) don't match the official "catches Fable 5" narrative; weights still withheld (only April preview builds on HF); API output phrasing reads stiff vs web end.
- Use for: 1M context + heavy agentic scale.

## GLM-5.3 (Zhipu/Z.ai)
- ~700B total, all post-training on the GLM-5.2 base (no new architecture).
- Terminal-Bench 3.0 4.6→28.3, DeepSWE 46.2→66.9, ExploitBench doubled to 54.4%, CyberGym 84.5% (edges GPT-5.6 Sol).
- Zhipu's positioning: "not cheapest, but strongest at reasoning", structured chain-of-thought, math, correctness-critical work.
- Weights release ~2 weeks after launch (safety hardening, offensive cyber grew "faster than expected").
- API now forces thinking on across three effort levels (low/high/max), breaking change for apps that ran thinking off.
- Use for: correctness-critical reasoning at low thinking cost.

## Ollama Pro Billing Implication (GPU time + size, NOT tokens)
- GLM at ~700B is cheaper to serve than Pro's 1.6T before the thinking dial.
- GLM low thinking = minimal GPU time. Vinny almost always runs low.
- So GLM is Vinny's big-model default for cheap reasoning; Pro only earns its slot for 1M context or agentic scale.

## Flash 0731 Is the Standout
- Vinny's take: Flash 0731 is the most impressive model of the recent crop; the race is narrowing.
- His framing: the preview was "more confident than capable," but 0813's capability finally matches the confidence, "it just feels better, better tooling."
- He tests models by giving them REAL work (articles, keyword research), not benchmarks.
- First Flash-written article passed Gemini with nothing to revise, the quality bar.
- Flash is consolidating: took over article writing AND keyword research from Kimi/Gemma, ~98% of usage.
