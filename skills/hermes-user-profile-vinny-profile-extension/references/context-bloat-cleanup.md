# Context Bloat Cleanup Procedure

## Diagnosis
If models behave stupidly in Hermes but work fine in other tools (OpenClaw, Pi, Claude Code), the cause is almost always context bloat, too much injected into the system prompt before the model sees the user's message.

## What Bloats the Prompt
1. **Skills list**, Each enabled skill adds a name + description line to the system prompt. 114 skills = 114 lines of noise on every turn.
2. **Memory files**, `~/.hermes/memories/MEMORY.md` and `USER.md` are injected every turn. ALL-CAPS instructions are counter-productive (they waste tokens and don't change behavior).
3. **Persona file**, Loaded every turn. Keep it minimal.
4. **Tool descriptions**, Every enabled toolset adds descriptions. Disable unused toolsets via `hermes tools`.

## Cleanup Steps

### 1. Trim Memory Files
Location: `~/.hermes/memories/MEMORY.md` and `USER.md`

- Strip ALL-CAPS instructions, they don't work and just eat tokens
- Keep only declarative facts about the user
- Good: "Runs Hermes via Telegram in WSL. Prefers event-driven solutions."
- Bad: "YOU ARE NOT ALLOWED TO ADD ANYTHING TO THIS FILE. STAY OUT OF MEMORY."

### 2. Disable Unused Skills
Config location: `skills.disabled` list in `~/.hermes/config.yaml`

```yaml
skills:
  disabled:
    - skill-name-1
    - skill-name-2
```

Check what's enabled: `hermes skills list`
Re-enable later: `hermes skills config` or edit `config.yaml` directly

### 3. Disable Unused Toolsets
```bash
hermes tools list          # See what's enabled
hermes tools disable NAME  # Disable a toolset
```

Changes take effect on `/reset` (new session).

### 4. Measure Impact
Before and after, compare:
- Skill count: `hermes skills list | grep enabled | wc -l`
- Memory file sizes: `wc -c ~/.hermes/memories/*.md`
- Observed model behavior: Does the model answer directly or go investigating?

## Results from May 2026 Cleanup
- Skills: 114 → 26 active (88 disabled)
- Memory/USER.md: 970 chars → 394 chars
- Memory/MEMORY.md: 193 chars of ALL-CAPS junk → 0 chars (deleted)
- User confirmed immediate behavioral improvement after model switch