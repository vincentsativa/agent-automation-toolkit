---
name: tensorfeed-story-filter
description: Use to filter recurring stories out of TensorFeed before any report.
trigger: "Any TensorFeed report, or when generating a news report that must exclude recurring/dominant stories."
category: research
---

# TensorFeed Story Filter

A filter script at `~/.hermes/scripts/tensorfeed_filter.py` that strips unwanted recurring stories from TensorFeed before any report.

## Operation

- Fetches `https://tensorfeed.ai/api/news`.
- Strips articles matching `EXCLUDED_PATTERNS`.
- Saves to `/tmp/tensorfeed_filtered.json`.
- Reports count filtered.

## Current Exclusions

- OpenAI rogue agent / Hugging Face breach (any variant).
- AI kill switch act.
- Agent containment breach stories.
- Any story about an AI agent escaping/hacking/compromising services.

Add exclusions by editing `EXCLUDED_PATTERNS` (case-insensitive regex).

## Integration

**ANY TensorFeed report must use `/tmp/tensorfeed_filtered.json`, not the raw API.**

Run `python3 ~/.hermes/scripts/tensorfeed_filter.py` before any TensorFeed report.
