# Checkpointed Cron Pipeline (Design Pattern)

Vinny's architecture for building self-running automations with cron. Distinct from the
common "one-off reminder / single task" use of cron. This is a **design pattern**, not a
troubleshooting topic, load it when building a new multi-step automation, not when fixing a broken job.

## Core idea

Treat cron not as "run this one thing on a schedule" but as a **state machine / pipeline**:
a series of steps where each cron job is a checkpoint, and the whole thing is a loop that
runs itself.

## Why it works (the four advantages)

1. **Context clearing**, each step starts a fresh session. The model isn't carrying a
   bloated, drifting context from step one. Clean slate per step = better instruction
   following and lower token cost.
2. **Checkpoint inspection**, each step is a natural place to check the work before the
   next step fires. If a step is wrong, correct that one step instead of redoing the whole
   automation.
3. **Error containment**, a failure at one checkpoint doesn't cascade; you fix the step and
   continue, rather than restarting the entire pipeline.
4. **Shared data layer (double-dipping)**, the data collection that's part of the cron is
   reused by all downstream consumers (social posts, reports, etc.). One collection, many
   consumers. This is what turns a linear pipeline into a system.

## How to build one

- Each cron job = one step in the pipeline. Its output (data file, artifact) is the input
  to the next step.
- Use `context_from` to chain jobs: job B injects job A's most recent output as context.
- Use a shared data file (e.g. `~/.hermes/cron/output/<job_id>/` or a project data file)
  that multiple jobs read from, the "double-dipping" data layer.
- Design each step to be independently inspectable and re-runnable, so a single bad step
  can be corrected without redoing the whole loop.
- Keep each step's prompt self-contained (cron jobs run in fresh sessions with no
  current-chat context).

## Why most people miss this

The default mental model of cron is "run one thing on a schedule." The people building the
platforms ship the pieces (chaining, context injection, data files) but don't show how to
string them into a self-running checkpointed loop. The insight is assembling those pieces
into a pipeline with checkpoints and a shared data layer, the "putting two and two
together" that most users never do.

## Related

- `hermes-cron-troubleshooting` SKILL.md, for when a job in the pipeline fails (duplicate
  run, missed run, gateway restart ordering).
- `cronjob` tool `context_from` parameter, chain job outputs.
