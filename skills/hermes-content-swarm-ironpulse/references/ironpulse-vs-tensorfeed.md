# IronPulse vs TensorFeed, Critical Distinction

## The Rule
Tool name takes absolute precedence over pattern matching. If Vinny specifies a tool by name, execute that tool regardless of what the rest of the request sounds like.

## IronPulse (this skill)
- **Trigger word:** "ironpulse", ALWAYS execute this workflow
- **Type:** RSS-first daily AI news research workflow (browser fallback only)
- **Sources:** TechCrunch AI RSS, The Verge AI RSS, Google News AI RSS, Fox News AI RSS, fetched via curl
- **Output:** Ranked top 20 stories, 4-sentence summaries

## TensorFeed (different tool, NOT this skill)
- **Trigger word:** "tensorfeed", NEVER substitute IronPulse for TensorFeed
- **Type:** API-based news via Python client
- **Sources:** HN, ZDNet, The Verge, WIRED, MIT Tech Review, via API
- **Skill:** `research/tensorfeed/SKILL.md`

## NEVER DO THIS
- User says "ironpulse" → do NOT run TensorFeed
- User says "tensorfeed" → do NOT run IronPulse
- The trigger word determines the workflow, not the apparent content similarity