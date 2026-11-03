# Provider Transport Architecture & Model Fit

## Core Principle

**The model that works best is the one whose native API format matches what the framework was built to drive.**

Hermes Agent is built around the Anthropic messages API format at its core. Models that expose Anthropic-native APIs integrate more cleanly than those retrofitted onto OpenAI chat completions shims.

---

## Transport Layer by Provider

| Provider | Transport | Notes |
|---|---|---|
| `minimax` | `anthropic_messages` | Dedicated OAuth flow (`minimax-oauth`), explicit think-block state machine |
| `minimax-oauth` | `anthropic_messages` | OAuth external, base_url `https://api.minimax.io/anthropic` |
| `minimax-cn` | `anthropic_messages` | China region variant |
| `deepseek` | `openai_chat` | OpenAI compatibility shim — may introduce friction at edges |
| `kimi` | `openai_chat` via `kimi-for-coding` | Works well via aliasing |
| `stepfun` | `openai_chat` | OpenAI transport |
| `glm` | OpenAI transport (Anthropic-compatible internally) | Solid performance in Hermes |

---

## Why Transport Matters

### Anthropic-native models in Hermes
- Multi-turn context handled natively
- Image inputs (base64) flow through first-class code paths
- Tool use schemas parsed by matching code
- Streaming state machine already understands their output format

### OpenAI-compat models in Hermes
- Fighting a layer of impedance mismatch
- Edge cases: streaming deltas, image handling, context window management may behave differently than expected
- Works fine when compat layer is solid — but breaks silently in subtle ways

---

## Think-Block Handling

MiniMax emits inline `<think>...</think>` blocks in its stream. Hermes has dedicated infrastructure for this:

- `agent/think_scrubber.py` — state machine that suppresses reasoning blocks at the stream level
- `gateway/stream_consumer.py` — same suppression in gateway streaming path

DeepSeek does not appear in these code paths.

---

## Practical Implications

**Changing default model to MiniMax (or GLM, Kimi) after using DeepSeek:**
1. First session will feel noticeably cleaner — streaming, tool calls, image handling
2. This is not a quality judgment on DeepSeek — it's an API format mismatch
3. DeepSeek V4 Flash is excellent in OpenClaw (OpenAI-native) but fights the layer in Hermes

**When to use which:**
- OpenClaw: DeepSeek, GPT-4o, models with strong OpenAI compat
- Hermes: MiniMax, GLM-5, Kimi, StepFun — models designed for Anthropic-format integration
- Claude Code: Same pattern as Hermes — Anthropic-native models fit best

---

## Key Files

- `hermes_cli/providers.py` — `HermesOverlay` definitions with `transport` field
- `agent/model_metadata.py` — `_PROVIDER_PREFIXES`, context length metadata, URL→provider mapping
- `agent/think_scrubber.py` — streaming think-block suppression state machine
- `gateway/stream_consumer.py` — `_filter_and_accumulate` for think-block filtering