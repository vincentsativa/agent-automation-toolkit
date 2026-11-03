---
name: ollama-roi-strategy
description: Selection strategy for Ollama cloud models based on GPU-time ROI and task complexity.
---

# Ollama Model Selection & ROI Strategies

Strategy for optimizing GPU-time consumption on Ollama Pro ($20/mo) based on model architecture and parameter count.

## Core Strategy: Tiered Intelligence
Always route tasks to the smallest model capable of performing them to maximize the $20/month budget.

| Tier | Model Examples | GPU-Time Cost | Use Case |
| :--- | :--- | :--- | :--- |
| **Budget (Workhorse)** | Nemotron-3-Nano (4B-30B MoE) | ~0.1 - 0.2x | High-volume tasks, simple summaries, basic Q&A, formatting. |
| **Value (Daily Driver)** | Gemini-3-Flash | 1.0x (Baseline) | Routine logic, standard coding, moderate reasoning, daily assistant tasks. |
| **Premium (Specialist)** | Gemma-4 (31B), Nemotron-3-Super (120B MoE), Qwen-3.5 (122B) | 5x - 30x | Deep reasoning, multi-step planning, complex debugging, agent orchestration. |

## Selection Heuristics
1. **Nano First:** Start all bulk processing (RSS fetching, text cleanup) with Nano.
2. **Flash for Routine:** Use Flash for coding and logic that requires consistent accuracy but not deep "thinking."
3. **Super for Bottlenecks:** Escalate to Super/31B models only when a task involves >3 interdependent variables or requires multiple logical steps that smaller models fail to chain.

## Pricing Math Reference
- **Active GPU Time:** Billing is based on time the GPU is active.
- **Size Penalty:** Larger models take longer to "prefill" context and "decode" tokens.
- **Efficiency Boost:** MoE (Mixture of Experts) models like Nemotron-3-Super activate only a fraction of weights (e.g., 12B of 120B), making them more efficient than dense models of the same total parameter count.

## Pitfalls
- **Thinking Mode:** Avoid long-reasoning "thinking" modes on premium models for trivial tasks; it can multiply GPU-time consumption by 3-5x.
- **Context Bloat:** Large context windows (>8k) on heavy models significantly increase processing time per token.
