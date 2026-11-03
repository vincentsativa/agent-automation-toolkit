# Auxiliary Tasks — Provider Configuration (May 24, 2026)

Vinny runs Hermes with **Ollama.com** as his exclusive provider (`custom:ollama.com`). He does **not** use OpenRouter or Google for any auxiliary task — never has, never will.

## The Dashboard Issue

Hermes dashboard showed **1 override · 10 auto** for auxiliary tasks. "Auto" means Hermes tries fallback backends (OPENROUTER_API_KEY, GOOGLE_API_KEY). Vinny has neither, so auto tasks silently underperform.

## The Fix

All 13 auxiliary tasks set to `ollama-com` / `deepseek-v4-flash`:

```bash
hermes config set auxiliary.<task>.provider ollama-com
hermes config set auxiliary.<task>.model deepseek-v4-flash
```

Tasks: vision, web_extract, compression, skills_hub, approval, mcp, title_generation, triage_specifier, kanban_decomposer, profile_describer, curator, session_search, flush_memories

## Rules

- **Never suggest or default to OpenRouter** — Vinny called this out explicitly.
- **Never leave auxiliary tasks on `auto`** — triggers fallback providers he has no keys for.
- **DO NOT touch these configs without being asked.** The setup is stable. Vinny manages his own provider config. This reference exists so you know the state — not so you act on it.
- The `hermes-agent` skill's troubleshooting section mentions OpenRouter/Google as fallbacks — ignore that for Vinny. His fix is Ollama.com config, not API key setup.

## Status (May 24, 2026)

All 13 auxiliary tasks set to `ollama-com` / `deepseek-v4-flash`. Dashboard shows 11 overrides (UI excludes some tasks like triage_specifier, flush_memories) and 0 auto. This is the final, stable state — do not modify.
