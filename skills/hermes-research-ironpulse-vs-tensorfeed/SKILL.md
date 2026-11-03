---
name: ironpulse-vs-tensorfeed
description: "Critical distinction: IronPulse and TensorFeed are two completely different AI news workflows. NEVER substitute one for the other."
trigger: "When Vinny says 'ironpulse' or 'tensorfeed' — execute the correct workflow based on the named trigger, not the request pattern"
---

# IronPulse vs TensorFeed — Critical Distinction

## The Rule
Tool name takes absolute precedence over pattern matching. If Vinny specifies a tool by name, execute that tool regardless of what the rest of the request sounds like.

## IronPulse (the skill)
- **Trigger word:** "ironpulse" (always)
- **Type:** Full browser-based daily AI news research workflow
- **Sources:** TechCrunch AI, The Verge AI, Google News AI, Fox News Tech — browsed directly, no API
- **Output:** Ranked top 12 stories (best to worst), 4-sentence summaries, Pinterest titles, X.com posts (190 chars), saved to `~/.hermes/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt` + copied to Windows Desktop
- **Delivery:** File path first in Telegram, then inline analysis. Email attachment to hello@phantom-byte.com.
- **Includes:** Social content generation, themes analysis, article ideas for phantom-byte.com
- **Skill file:** `skills/content-swarm/ironpulse/SKILL.md`

## TensorFeed (a different tool entirely)
- **Trigger word:** "tensorfeed" (always)
- **Type:** API-based news via `tensorfeed_client.py` script at `/mnt/c/Users/<user>/workspace/scripts/`
- **Sources:** Hacker News AI, ZDNet, The Verge, WIRED, MIT Tech Review, arXiv — via Python API client
- **Output:** Raw article list with snippets, benchmark data, trending repos
- **Delivery:** Save to file, email as attachment, reply with file path only
- **Skill file:** `skills/research/tensorfeed/SKILL.md`

## NEVER DO THIS
- Vinny says "ironpulse" → do NOT run TensorFeed
- Vinny says "tensorfeed" → do NOT run IronPulse
- Map his explicit trigger word to whatever you think is equivalent = failure

## If Confused
Ask. Do not guess. Do not substitute.