# Multi-Model Article Panel Voting

Vinny evaluates article drafts using a multi-model panel rather than reviewing them himself. This removes his own bias from the selection process.

## Panel Composition

Current models in rotation (switched depending on task and harness):
- Grok 4.3 — wildcard/spicy takes
- Gemini — measured, institutional read (trained on same data as Google Search ranking)
- GPT-5.5 — institutional/balanced read
- Kimi K2.6 — efficiency/engineering perspective
- DeepSeek V4 Pro — punch/voice
- DeepSeek V4 Flash — synthesis of Pro's punch + Kimi's restraint

## Voting Rules

- All models on the panel get a vote
- Models that wrote the drafts also get a vote
- Vinny does NOT vote — he executes whatever the panel consensus picks
- He switches which models are on the panel depending on the task and harness

## Historical Pattern

Flash almost always wins the vote. It's the synthesis: Pro's punch with Kimi's restraint. No rough edges. Pro drafts are consistently strong but rarely beat Flash — the room values polish over raw voice.

"Flash is the safe bet but not a foregone conclusion — depends on the material."

## Key Insight: The Harness Matters

Same model family, different interface, different vote. Example: DeepSeek Pro in Hermes picked Pro draft; DeepSeek Pro in the DeepSeek chatbot picked Flash. The harness filters everything — context size, system prompt, whether the model thinks it's a chatbot or an agent.

When even the same model flips its pick depending on the wrapper, raw consensus across diverse setups is the only signal worth trusting.

## Why It Works

- Removes Vinny's own bias
- Multi-architecture convergence is a strong signal
- Gemini's vote carries implicit SEO signal (same training data as Google's ranking infrastructure)
- "I found the right AI, and asked it the right question, and it helped me identify the issue" — model-aware problem solving
