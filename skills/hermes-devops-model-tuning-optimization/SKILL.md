---
name: model-tuning-optimization
description: Optimization patterns for smaller/cloud models (Nemotron, Kimi, Qwen) to ensure high performance on Hermes vs other platforms.
---

# Model Tuning Optimization

This skill captures the specific configuration patterns that make smaller models (like `nemotron-3-nano`) and cloud models (`nemotron-3-super`, `kimi-k2.5`) perform effectively in the Hermes environment.

## Logic Overview
Models that might feel "lousy" or inconsistent on other platforms often perform better on Hermes due to specific parameter steering.

## Configuration Patterns

### 1. Temperature & Sampling
*   **Target:** 0.1 - 0.2
*   **Reason:** Forces deterministic, reliable output. Prevents the "hallucination" or "fluff" often seen with provider defaults (0.7+).

### 2. Reasoning Effort

**Standard models** (Qwen, Gemini Flash, MiniMax, Nemotron, Llama):
*   **Target:** `none`
*   **Reason:** These models don't natively reason — enabling thinking wastes tokens and adds latency with no quality improvement.

**GLM-5.1** (validated stack):
*   **Target:** `low`
*   **Reason:** GLM-5.1 actually performs better with thinking: low than with none. When set to `none`, it can fall into memory-loop/spiral behavior on simple interactions. `low` keeps it stable and responsive without wasting tokens. This is a validated exception — not all "standard" models behave the same. Test before assuming `none` is optimal.

**Reasoning-native models** (DeepSeek V4, o-series, Kimi K2 thinking, Grok thinking):
*   **Target:** `low`
*   **Reason:** These models depend on an internal thinking phase for output quality. `none` suppresses their core capability and degrades responses. `high`/`xhigh` wastes tokens — they already reason natively and higher efforts don't proportionally improve output. `low` keeps thinking enabled but conservative.

**Smaller models** (nemotron-3-nano, <30B params):
*   **Target:** `low` or `none`
*   **Usage:** Explicitly set for sub-agent tasks.
*   **Reason:** Prevents smaller models from wasting compute on internal deliberation that they aren't fully optimized for, focusing them on direct completion.

### 3. Context Management
*   **Threshold:** ~4,000 tokens for "nano" models.
*   **Action:** Trim system prompts and conversation history aggressively.
*   **Reason:** Stay within the model's high-coherence window to avoid truncation or loss of instruction following.

### 4. System Prompting
*   **Style:** Concise, direct, "exact-format" instructions.
*   **Avoid:** Generic or overly verbose personas that dilute the directive.

## Diagnostic Patterns for Cloud Models

### Config Was Reverted — Check Snapshots

**Signal:** A model you set as default keeps reverting to a different one.

**Root cause:** Hermes auto-updates can write a fresh `config.yaml`, clobbering user changes. Snapshots capture the config pre-update.

**Verification:**
Look for pre-update snapshots under `state-snapshots/*pre-update/config.yaml` in the Hermes data directory. Read the `model.default` field to confirm what was set before the update.

**Fix:** Re-apply the model change after the update completes, or pin the config file against overwrites.

### Load-Induced Model Degradation ("Confused" Behavior)

**Signal:** A model that normally performs well suddenly gives incoherent, forgetful, or "foggy" responses — hallucinating more, losing thread of conversation, ignoring constraints.

**Root cause:** Cloud provider capacity congestion. Under heavy traffic, providers may route to quantized/distilled variants, aggressively batch, or throttle KV cache quality. This manifests as apparent "confusion" — the model seems dumber mid-session.

**Diagnostic check:**
1. **Switch models** on the same provider. If a different model (e.g. Gemma 4) works fine on the same provider while DeepSeek-V4-Flash is "confused", the issue is provider capacity for that specific model — not a general provider outage.
2. **Start a fresh session** — clean context sometimes helps if the issue is KV-cache related.
3. Check provider status pages for known incidents before assuming a config or code bug.

**Known pattern:** DeepSeek-V4-Flash on Ollama Cloud degrades noticeably under peak traffic while Gemma 4:31b on the same provider remains stable. This is a capacity allocation issue, not a model defect.

**Mitigation:**
- Switch to a less congested model on the same provider during peak hours.
- Configure `fallback_providers` or a secondary `default` model so the agent auto-rotates.
- Be more explicit/redundant with instructions during peak usage — degraded models benefit from tighter guidance.

### Provider-Level vs. Model-Level Issues

| Symptom | Likely cause | Action |
|---------|-------------|--------|
| One model "confused", others fine on same provider | Model-specific capacity congestion | Switch models |
| All models on a provider fail/timeout | Provider outage | Check status page, switch providers |
| Model works in new session but degrades mid-chat | KV cache degradation under load | Start fresh session |
| Model refuses or ignores constraints suddenly | Throttled quality tier under high load | Wait, or switch to less loaded model |

## Implementation (config.yaml example)
```yaml
custom_providers:
  - name: "Ollama.com"
    model: "nemotron-3-nano:30b-cloud"
    temperature: 0.15
    reasoning_effort: "low"
    max_context: 4000
```

## Desktop App Display Pitfall: Model Picker Shows Wrong Reasoning Effort

The desktop app's model picker (composer pill and dropdown) shows **"Med"**
for every model by default, **even when** `agent.reasoning_effort: low` is
set in `config.yaml`. Your actual sessions run at the configured `low` —
the label is purely a UI bug.

**Do NOT change your config based on the picker display.** The picker has
its own fallback chain that defaults to `medium` when no per-model preset
is saved, completely ignoring the global config. Three code sites in
`apps/desktop/src/` drive this behavior.

See `references/desktop-model-picker-display.md` for the full code trace
and fix approach.

### 5. Writing Density vs. Accuracy Trade-off
*   **Symptom:** Smaller models (e.g., <15B) produce "thin" writing (generic, lacking nuance). Larger models (70B+) provide high density but are more prone to "confident hallucinations" (filling gaps with plausible-sounding lies).
*   **The 31B Transition:** Models in the 30B range often act as a bridge—offering significantly more density than small models while maintaining better factual stability than massive ones.
*   **Mitigation for High-Density Writing:**
    *   **The Skeleton Method:** Use the large model to generate a detailed, factual outline/claims list first. Verify the facts, then expand the skeleton into a full piece.
    *   **RAG / Grounding:** Provide explicit source text to anchor the model, leveraging its density/style without relying on its internal (and potentially faulty) memory.
    *   **Temperature Control:** Reduce temperature (0.2 - 0.3) for high-parameter models to prioritize the most probable (factual) tokens over creative (hallucinatory) ones.
    *   **Iterative Expansion:** Instead of asking for a "comprehensive" piece in one go, ask for a draft and then specifically prompt to "increase density" in a particular section by adding technical details or challenging assumptions.