# Harness Implications for Non‑Anthropic Models

## Overview
When using models that are not Anthropic‑native (e.g., `nemotron-3-nano`), Hermes Agent can run them, but behavior is heavily influenced by the execution harness.

## Key Points from User Environment
- **Log entry (2026‑04‑21 16:35:44)** – “They are both running on ollama, the only difference is the harness.”
- **User comment (2026‑04‑21 16:49:41)** – “I don’t know my harness is “buggy” as much as it may not be compatible, with k2.”
- **Migration guides** repeatedly note that OpenClaw’s harness provides token‑pricing awareness and context‑length tuning that improve stability for open models like Nano.

## Practical Impact
- **Token‑pricing & cost control** – OpenClaw automatically surfaces pricing tiers and can throttle based on budget.
- **Context‑length handling** – OpenClaw adjusts the effective context window for open models, preventing silent truncation.
- **Compatibility quirks** – Certain transport‑level behaviours (e.g., how tool calls are wrapped) differ; testing in the target harness is required.

## Recommendation
For non‑Anthropic models such as Nano, prefer the OpenClaw harness when:
- Token cost is a concern.
- You need predictable context‑length handling.
- You want built‑in safeguards around tool‑call approvals.

If you remain in the native Hermes harness, be aware that some quirks (e.g., missing token‑pricing signals) may surface, and you should verify behavior with direct API calls before relying on automated workflows.