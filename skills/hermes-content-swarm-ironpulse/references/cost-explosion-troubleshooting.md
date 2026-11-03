# IronPulse Cost Explosion — Troubleshooting Guide

## Incident: May 5, 2026

**Reported:** IronPulse went from ~0.1% of credit pool per run to ~1% — 10x increase.

## Root Cause

The IronPulse cron jobs (`be35316ef6c6` morning, `f6237acd0039` afternoon) have **no model override** in their cron config. They inherit whatever model is the default in Hermes at scheduling time.

The user had been running DeepSeek V4 Flash via custom provider for interactive sessions. When IronPulse cron fired, it ran on that expensive model instead of the original cheap model (Gemini 3 Flash Preview).

## Diagnosis Path

```python
# Step 1: List cron jobs — check if model/provider columns are populated
# If blank, the job inherits the interactive model
hermes cron list

# Step 2: Check what model interactive Hermes is using
hermes config | grep -i model
# or
hermes model

# Step 3: Check model costs
hermes config | grep -i model
```

## The Cost Lever

| Lever | Effect | Fix |
|-------|--------|-----|
| **Model choice** | DeepSeek V4 Flash vs Gemini 3 Flash Preview — the difference in cost-per-token can be 10x or more for multi-turn tasks | Pin model at cron creation time (see ironpulse skill's "Cost Discipline" section) |

## How to Verify a Fix

1. `hermes cron list` — confirm model/provider show pinned values
2. Let the next scheduled run happen, then check: `hermes insights --days 1` for token usage
3. Or trigger manually: `hermes cron run <job_id>` and watch for cost
