---
name: hermes-skill-install
description: Install Hermes skills; recover when install fails.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, skills, install, troubleshooting]
    related_skills: [hermes-agent, hermes-config-editing]
---

# Hermes Skill Install

Install skills from the skills hub and recover when the standard path fails.

## When to Use

- Installing a skill from the hub: `hermes skills install <id>`.
- `hermes skills install` fails with "Could not fetch ... from any source" even
  though `hermes skills search` finds the skill.
- `hermes skills repair-official <name>` reports "Official optional skill not
  found".

## Standard install

```bash
hermes skills search <query>      # find the identifier
hermes skills inspect <id>        # preview without installing
hermes skills install <id>        # e.g. official/web-development/har-derived-api-client
```

## When `hermes skills install <id>` fails

Symptom: the skill shows up in `hermes skills search` (so it exists in the hub),
but `hermes skills install` returns:

```
Fetching: <id>
Error: Could not fetch '<id>' from any source.
```

**Root cause (most common): the local Hermes repo checkout is behind
`origin/main`, and the skill only exists on the newer main.** Official skills
are seeded from `optional-skills/` in the repo; if your checkout predates the
skill's addition, the install has nothing to fetch locally.

### Diagnose

```bash
cd ~/.hermes/hermes-agent
git fetch origin
git status -sb | head -1        # e.g. "## main...origin/main [behind 60]"
# Does the skill exist on origin/main but not in your checkout?
git ls-tree origin/main --name-only -r optional-skills/ | grep -i <skillname>
```

If it's listed on `origin/main` but absent from your local `optional-skills/`,
you're behind. Two fixes:

### Fix A, update Hermes (cleanest, restores the normal path)

```bash
hermes update
```
Then `hermes skills install <id>` works normally. Do this when you're many
commits behind anyway.

### Fix B, extract the skill from origin/main and install manually (no update)

The `git checkout` of a live source tree is **blocked** by Hermes (it would mix
module versions in the running process), so pull the files read-only with
`git show` and write them into `~/.hermes/skills/`:

```bash
cd ~/.hermes/hermes-agent
# 1. Dump each file from origin/main
git show origin/main:optional-skills/<cat>/<name>/SKILL.md > /tmp/skill.md
git show origin/main:optional-skills/<cat>/<name>/scripts/<file>.py > /tmp/<file>.py
# ... repeat for every file under the skill dir (git ls-tree -r to enumerate)

# 2. Create the skill dir and write the files
mkdir -p ~/.hermes/skills/<cat>/<name>/scripts
# write SKILL.md and each script into place (write_file tool)

# 3. Make scripts executable and verify
chmod +x ~/.hermes/skills/<cat>/<name>/scripts/*.py
hermes skills list | grep -i <name>     # should show enabled
```

Verify the skill loads cleanly with `skill_view(name)`, confirm the
`linked_files` (scripts/references) are all present and `readiness_status` is
`available`.

## Pitfalls

- **`hermes skills repair-official <name>` fails with "Official optional skill
  not found"** when the checkout is behind, it only backfills from the local
  `optional-skills/`, which doesn't have the skill yet. Same root cause; update
  or use Fix B.
- **`git checkout origin/main -- <path>` is blocked** on the live Hermes source
  tree ("would rewrite Hermes's live source checkout"). Use `git show` to read
  files out read-only instead; never force the checkout.
- **Enumerate every file** under the skill dir with
  `git ls-tree origin/main --name-only -r optional-skills/<cat>/<name>/`, a
  skill is more than its SKILL.md (scripts, references, templates). Missing a
  support file leaves the skill half-installed.
- **Manual installs are `local` source, not `official`.** They won't get hub
  update tracking. Prefer Fix A (update) when you want the skill to stay
  current; use Fix B for a one-off.

## Related skills
- `hermes-agent` (bundled), full `hermes skills` CLI reference.
