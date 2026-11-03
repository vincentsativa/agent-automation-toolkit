# OpenClaw / OpenHarness — What We Know (May 2026)

## Summary

OpenClaw is an agent harness platform. OpenHarness ([thu-nmrc/OpenHarness](https://github.com/thu-nmrc/OpenHarness)) is a 24/7 autonomous execution framework that runs **on top of** OpenClaw. Hermes lists OpenClaw as a comparable framework in its own docs, but until this session we had no detail on what it actually is.

## Architecture Difference (Why Flash Works on OpenClaw but Not Hermes)

| | OpenClaw + OpenHarness | Hermes |
|---|---|---|
| **Prompt style** | Thin prompt + external validation scripts | Thick system prompt (memory, skills, tools, constraints all inline) |
| **Reliability model** | Mechanical constraints + external audit | Internal context + tool dispatch |
| **State management** | `heartbeat.md` breakpoint recovery, `mission.md` contracts, `harness_eval.py` external audit | Session transcripts, memory blocks, skill dispatch |
| **Entropy control** | `harness_cleanup.py` garbage collection | Context compression |
| **Trigger** | Cron-scheduled, fully unattended | Cron via hermes cron, gateway, or manual |

OpenHarness's design philosophy: **"Absolute Reliability over Emergent Intelligence."** It solves agent drift through external validation (the agent can't self-certify completion — a script checks it) and mechanical sandboxing (`progress.md` / `mission.md` contract constraints).

Hermes solves the same problems through internal mechanisms: memory, skills, context compression, tool enforcement. This means Hermes puts far more into the system prompt.

**Impact on model selection:** Flash-class models (2.0, etc.) handle OpenClaw's thin-prompt architecture fine but drown in Hermes's thick prompt — they start dropping constraints, hallucinating tools, and getting "confused." Claude and DeepSeek handle dense system prompts better. This is an **architectural difference**, not a model quality problem.

## Key OpenHarness Features

- **One-command start**: Describe task idea → framework auto-creates directory, contract, schedule, first run
- **Cross-session memory**: `heartbeat.md` — resumes from exact breakpoint regardless of interruptions
- **External validation loop**: `eval_criteria.md` + `harness_eval.py` prevents AI from self-certifying completion
- **Entropy control**: Built-in cleanup to prevent context bloat
- **Machine-verifiable contract**: Natural language → `mission.md` constraining AI behavior

## Installation (for reference)

```bash
mkdir -p ~/.openclaw/workspace/harness
git clone https://github.com/thu-nmrc/OpenHarness.git ~/.openclaw/workspace/harness
```

OpenClaw auto-recognizes the `SKILL.md` and equips the agent with harness capabilities.

## Relevance to Hermes

- Vinny uses both — OpenClaw for some tasks, Hermes for others
- The context-bloat dynamic (114 skills, dense memory, thick prompts) is the #1 cause of "model works fine elsewhere, sucks in Hermes"
- When a model underperforms in Hermes, the first diagnostic should be context density, not model/provider quality
