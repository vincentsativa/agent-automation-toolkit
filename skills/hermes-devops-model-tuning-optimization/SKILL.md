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

## Implementation (config.yaml example)
```yaml
custom_providers:
  - name: "Ollama.com"
    model: "nemotron-3-nano:30b-cloud"
    temperature: 0.15
    reasoning_effort: "low"
    max_context: 4000
```

## Verification
*   Check if the model returns JSON immediately when requested.
*   Verify if the response length is appropriate (no unnecessary filler).
