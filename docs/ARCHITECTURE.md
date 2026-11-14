# Architecture

Two harnesses, six agents, one cron layer that makes them all do scheduled work without
a human in the loop.

```
                        ┌──────────────────────────────┐
                        │  Messaging surface            │
                        │  (Telegram)                   │
                        └───────────┬──────────────────┘
                                    │ commands / reports
        ┌───────────────────────────┴───────────────────────────┐
        │                                                       │
┌───────▼───────────┐   ┌────────────────┐   ┌─────────────────▼───┐
│  Pi harness       │   │  Hermes harness │   │  Hermes harness     │
│                   │   │                 │   │                     │
│  Windows Pi       │   │  WSL Hermes     │   │  Windows Hermes     │
│  (workstation)    │   │  (Linux dev box)│   │  (workstation)      │
│                   │   │  skills/ cron/  │   │  skills/ cron/      │
│  InstaBox Pi      │   │  Frank, agent 2 │   │  Karma, agent 3     │
│  (cloud VM)       │   ├─────────────────┤   ├─────────────────────┤
│                   │   │  fifi profile   │   │  InstaBox Hermes    │
│                   │   │  (Windows, own  │   │  (cloud VM)         │
│                   │   │   cron + backup)│   │                     │
└─────────┬─────────┘   └────────┬────────┘   └─────────┬───────────┘
          │                      │                      │
          └──────────────────────┴──────────────────────┘
                                 │
                   ┌─────────────▼─────────────┐
                   │  Shared script layer      │
                   │  scripts/ (this repo)     │
                   │  deterministic, no LLM    │
                   └───────────────────────────┘
```

Each of the six agents has its own home directory, skills and cron table. They share
conventions and this repository, not state. Each backs up to its own private git remote.

## The split that matters

**Judgement belongs to the model. Fact belongs to a script.**

Anything an agent can get wrong by being optimistic is a script. Whether a job posting is
still live, whether an attachment arrived intact, whether a DNS record now points where it
should, whether a report's numbers describe the pool it claims to describe, all of that is
checked by code that exits non-zero, not by a model saying it looks fine.

The pipeline shape that follows from this is always the same:

```
collect  →  filter  →  verify  →  (model judges)  →  deliver  →  validate
   script    script     script        model            script     script
```

`scripts/job-search/` is the fullest example: `run.py` drives the scripted stages, the
model reads the packed candidates and writes `selected.json`, `report.py` renders, and
`validate_delivery.py` refuses to send a report that does not describe the final verified
pool. The model never sets the count.

## Why skills exist as a layer

A recurring failure mode of an agent with tools is re-inventing a procedure from scratch
every session and re-learning the same traps. A skill is the procedure written down once,
loaded only when that class of work starts:

- preconditions and the exact interpreter/env to use
- the ordered commands, with the flags that mattered
- the pitfalls already paid for, written as a prohibition and the evidence for it
- the verification step that proves the work landed

`skills/` in this repo is the accumulated version of that. See `pi-*` skills for deploy
procedures and `software-development-*` / `behavioral-*` for the working rules.

## Cron layer

Two runner types, deliberately:

| Runner | Use | Why |
| --- | --- | --- |
| `deterministic-script` | Backup, cleanup, re-arm | Runs a script. No tokens spent, no variance, a failure is an exit code |
| `agent-prompt` | Inbox processing, content generation, research | Needs judgement; the prompt carries the procedure and the delivery rule |

A job that can be made deterministic is made deterministic. There is one live job table
per agent, all exported in `crons/`: `hermes-cron-jobs.json` (36 jobs, WSL Hermes),
`windows-hermes-cron-jobs.json` (10 jobs, Windows Hermes), `fifi-cron-jobs.json` (2 jobs,
fifi profile) and `instabox-cron-jobs.json` (3 jobs, InstaBox Hermes).

Two cron jobs in the Windows table exist only to make another job reliable: `PANEL RE-ARM`
arms a polling window that a later failure could leave disarmed, and `PANEL STALE CLEANUP`
clears state left behind by an interrupted run. Watchdog jobs are cheaper than diagnosing
a silently dead schedule.

## Backup and restore

`scripts/devops/hermes-backup.py` snapshots an agent home to a private git remote on a
nightly schedule: config, skills, memories, cron definitions. It is pure Python rather
than Bash because the cron runner resolves relative script paths to Windows absolute paths
and hands them to Bash, where `\U`, `\D`, `\A` are read as escape sequences and the path is
destroyed, exit code 127, every night, with the job reporting "ok". That trap and its
evidence are recorded in the corresponding skill.

## What is not in this repo

Credentials, delivery targets, personal paths and the security tooling that guards them.
Every script here reads secrets from environment variables or a local file that is not
committed.
