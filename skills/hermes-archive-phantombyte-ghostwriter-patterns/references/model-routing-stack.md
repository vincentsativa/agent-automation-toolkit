# Model Routing Stack (Aug 2026)

Vinny's content pipeline is a multi-model routing stack, not a single model. Know which model does what:

- **Outline selection committee**, five models weigh in on which outline direction to pick: GPT Luna, Grok 4.6, Gemini 4.7, Gemma 4, and DeepSeek V4-Flash.
- **Outline writing**, GLM (5.2/5.3) writes the final outline. This is the reasoning tier doing the strategic thinking.
- **Article writing**, DeepSeek V4-Flash 0731. As of Aug 2026 Vinny switched article writing AND keyword research from Kimi/Gemma to Flash. Flash is ~98% of his model usage (5,000+ requests/week vs low hundreds for everything else).
- **Judging/QA**, Gemini is the arbiter. A Flash-written article passing Gemini with "nothing to revise" is the quality bar. First Flash-written article cleared it on the first try (Aug 2026).

## Ollama Pro Billing Model (critical)

Vinny pays GPU time + model size, NOT per token. This invalidates the "model X produces 5x more output so it's more expensive" argument entirely, output volume doesn't touch his bill. Cost reasoning must be based on:

- **Model size:** Flash 284B/13B active vs Pro 1.6T/49B active vs GLM ~700B. Smaller weights = cheaper to serve.
- **Thinking level:** GLM low thinking = minimal GPU time. Vinny almost always runs low.

Flash is structurally cheaper for DeepSeek to operate, so it stays the value king even after API price hikes (which land on the expensive-to-run Pro first).

## Routing Rule of Thumb

- Flash for the 98% daily grind.
- Rare big-model moments: GLM at low thinking for cheap reasoning/correctness-critical work.
- Pro only when 1M context or heavy agentic scale is needed.
