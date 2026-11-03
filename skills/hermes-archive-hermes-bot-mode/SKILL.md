---
name: hermes-bot-mode
description: Use when asked about Hermes Bot Mode or the bots feature.
---

# Hermes Bot Mode

## What it is (critical: name collision)
When Vinny says "the bots feature" or "Bot Mode," he means **Bot Mode for Hermes Desktop** — the announced feature where agent profiles become named Bots. This is NOT the same as "Telegram Managed Bots" (Bot API 9.6, @BotFather-less bot creation via QR). Those are unrelated. On Aug 19 2026 I guessed Telegram Managed Bots and was wrong. Ask which one he means if ambiguous; if he says "Introducing Bot Mode," it's the desktop one.

## Core model
Hermes Profiles already give isolated brains (own model, memory, skills, soul, tools). Bot Mode is a visual orchestration layer on top: profiles become named Bots with:
- Name, title, description, avatar/profile picture
- Specialized role + own model, memory, skills, tools
- Persistent conversation you can open and inspect
- Agent-to-agent communication / handoffs (Research → Critic → Editor style)
- Recurring scheduled jobs per bot
- Clone a bot from an existing profile

One-liner: "Profiles give you multiple isolated brains. Bot Mode gives those brains faces, rooms, and a team interface."

## Status & limitations (as of Aug 2026)
- **Beta** desktop plugin. Handoffs are per-invocation and can fail; a receiving bot may respond later; no parallel-execution guarantee, no deterministic routing, no automatic failure recovery/retry. A documented demo hit a real failed handoff that needed a manual retry instruction.
- NOT a full workflow engine. For structured multi-task with dependencies, use Kanban instead.
- Profiles = specialization. Bot Mode = persistent specialists + communication. Kanban = structured task orchestration. Three different tools.

## Mapping to Vinny's stack
Vinny runs a model-panel pipeline: GLM outlines, Flash writes + keyword research, Gemini judges. That maps directly onto a bot roster:
- Keyword Research bot → Flash (keyword-research + SEO skills)
- Outline bot → GLM
- Writer bot → Flash (ghostwriter + writing-style skills)
- Judge bot → Gemini (final word)
Each PhantomByte property / funnel machine can get its own bot with the right skills attached. Build a specialist once, reuse it forever.

## Two-machine split (WSL + Windows)
Vinny has TWO agents:
- **Hermes Desktop runs in WSL** (his primary; profiles, skills, cron, Bot Mode all on one filesystem).
- **A separate Windows agent does keyword research.** A dedicated Keyword Research bot naturally lives there.

PITFALL: memory and skills do NOT auto-sync between the WSL and Windows agents. A bot's specialist knowledge lives where it was built. If a bot needs cross-agent context (e.g. PhantomByte writing style or SEO conventions on the Windows side), those skills/memory must be cloned there or pulled via portable profile export — decide this seam at build time.

## Portability (shipped alongside Bot Mode)
Portable profiles: `/export` saves an entire profile as one file (credentials stripped; skills, memory, persona, crons, plugins, settings, themes included). `/import` restores anywhere. This lets a full bot roster move between WSL, a VPS, or a machine at Joe's place in one file — no half-day rebuild. Relevant to hermes-state-migration workflows.

## Practical notes
- First step when Vinny wants to start: confirm the Bot Mode plugin is present/enabled in the WSL install (it's a desktop plugin; WSL Desktop is not a blocker).
- He wants to "take it and create whatever with it" — build-once specialist roster is the goal. Expect more questions; answer with verified docs, not guesses.

## Sources
- Nous Research X post "Introducing Bot Mode for Hermes Desktop."
- dev.to walkthrough (3-agent Research→Risk Analyst→Thesis Editor demo, beta failure).
- Sylt.ing v0.20.1 breakdown (portable profiles, Bot Mode roadmap).
