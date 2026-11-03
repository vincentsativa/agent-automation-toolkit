# Skill Authoring Guide

## Overview

There are two places a SKILL.md can live:

1. **User-local:** `~/.hermes/skills/<maybe-category>/<name>/SKILL.md`, personal, not shared. Created via `skill_manage(action='create')`.
2. **In-repo:** Part of the Hermes Agent source tree under `skills/`, installed from the hub or bundled with the agent itself. Authored as part of a PR to the main repo.

This reference covers **in-repo** skill authoring (option 2). For user-local skill creation, use the `skill_manage` tool, it auto-generates valid frontmatter.

## Skill Structure

```
<name>/
├── SKILL.md              # Required, the skill itself
├── assets/               # Optional, images, resources
├── references/           # Optional, reference docs, glossaries
├── templates/            # Optional, starter files
└── scripts/              # Optional, reusable action scripts
```

## Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Lowercase with hyphens. Max 64 chars. |
| `description` | Yes | One-line summary shown in skill lists. |
| `version` | Recommended | Semver for tracking updates. |
| `author` | Recommended | Who wrote it. |
| `license` | Recommended | SPDX identifier. |
| `platforms` | If platform-specific | `[linux, macos, windows]`, omit if all. |
| `tags` | Recommended | Array of keywords for search. |
| `related_skills` | Optional | Array of skill names this complements. |
| `triggers` | Optional | Human-friendly trigger phrases for when to load. |
| `toolsets` | Optional | Required toolset names. |

## Validator

Run the validator before merging:
```bash
python -m tests.test_skills --skills <name>
```

## Best Practices

- Keep `description` under 120 chars, it's the summary line
- Use `references/` for detail too long for SKILL.md
- Use `templates/` for files the user copies and modifies
- Use `scripts/` for statically rerrunnable tools
- Tag with `related_skills` to establish cross-links the dispatcher can follow
- Don't put session-specific detail in SKILL.md; put it in a reference file