# Enforcing a Per-Turn Tool-Call Ceiling

The recipe for Rule 5. Read this when an overrun has to be stopped structurally
rather than re-resolved by intention.

## Why the Built-In Guardrails Do Not Cover It

`tool_loop_guardrails` has three failure-based thresholds (`exact_failure`,
`same_tool_failure`, `idempotent_no_progress`) and a `loop_caps` section. None of them
trip on a long turn that makes many DIFFERENT calls SUCCESSFULLY, the pipeline
overrun. `loop_caps` only bounds `max_web_searches` and `max_subagents`. A missing
per-turn ceiling is not a config mistake; it does not exist, and the block has to come
from a hook.

## The Three Settings

Apply config through the Python config API (see `hermes-config-editing`), never by
editing YAML directly:

```python
cfg["agent"]["max_turns"] = <ceiling>          # iterations per turn, forces a wrap-up
cfg["tool_loop_guardrails"]["hard_stop_enabled"] = True
cfg["hooks"]["pre_tool_call"].append({
    "command": "python3 ~/scripts/turn_tool_cap_guard.py",
    "timeout": 10,
    "fail_closed": False,
})
```

Omit `matcher` to count every tool call, adding one narrows the hook to named tools
and defeats the purpose.

## The Hook Contract

A shell `pre_tool_call` hook receives the tool name, its args, the session id, and the
turn id. To block, print JSON to stdout:

```json
{"action": "block", "message": "..."}
```

A process exit code of 2 also blocks, with stderr as the message. `fail_closed: false`
is correct here: a crashed guard should let the tool call proceed rather than brick the
agent, and `hermes hooks doctor` is the check that the script did not silently die.

Count in a state file keyed on session plus turn id so each turn starts fresh. Fall
back to a time-bucketed key when no turn id is present, and prune the directory by age
and count so the state cannot grow without bound.

## Required Wiring Steps

1. Write the hook script and mark it executable.
2. Add it to `hooks.pre_tool_call` and verify it survived a re-load by reading the
   config back from disk.
3. **Allowlist it.** An unapproved `(event, command)` pair is SKIPPED with a warning,
   so the guard installs cleanly and silently never runs. Record approval, then
   confirm with `hermes hooks list` that the entry shows as allowed.
4. `hermes hooks doctor`, must report exists, executable, allowlisted, unchanged
   since approval.
5. Fire it through the production path, not just as a bare script, so the JSON is
   proven to parse into a directive:

```python
from agent.shell_hooks import ShellHookSpec, run_once
spec = ShellHookSpec(event="pre_tool_call", command=CMD, timeout=10, fail_closed=False)
run_once(spec, {"tool_name": "terminal", "args": {}, "session_id": SID,
                "task_id": "t", "tool_call_id": "c", "turn_id": TURN})
# r["parsed"] must be {"action": "block", "message": ...}
```

6. Seed the state file at the cap so the next synthetic call must block, then also
   test just below the cap and on a cron-shaped session id to prove it stays out of
   the way there.

## Current Installed Values

On this machine the guard is `~/scripts/turn_tool_cap_guard.py`, wired as
an unmatchered `pre_tool_call` hook, with `INTERACTIVE_WARN = 20`,
`INTERACTIVE_CAP = 80`, and `CRON_WARN = 40` with no cap. Read the constants out of the
script before quoting them; a raise ordered later makes any remembered number wrong. The cap
values were raised at the user's direction (50, then 60, then 80) after real turns hit the
ceiling and lost their final step.

**A cap-value change needs no reload; a config or hook-list change does.** The hook spawns
the script fresh on every tool call, so editing `INTERACTIVE_CAP` in place is live
immediately. Only adding or removing the hook entry, or changing `agent.max_turns`, is read
at startup and needs `/restart`. Do not ask for a restart to raise a number.

Verify a change by driving the real script, not by reading the constant: feed it synthetic
`pre_tool_call` payloads for one session and turn id, count up past the cap, and assert that
the calls just below it pass and the first call past it returns
`{"action": "block", ...}`. A bash loop piping JSON into the script per iteration is enough,
and it proves the threshold rather than the constant. Clear the state file for the synthetic
turn before and after, so the probe cannot leave a count behind for a real turn.

## Sizing and Exempting

Read the ceiling off measured percentiles (`state.db`, one turn = a `user` message
followed by `tool` rows). Cap interactive sessions where the tail begins; exempt cron
sessions from blocking entirely, because a mid-report block truncates a report with no
warning. Exempting by session-id prefix plus a cron env flag keeps scheduled work
unaffected.

## Applying the Change

Config and the hook list are read at gateway startup, so a settings change is inert
until the process reloads. The reload cannot be triggered from inside the running
gateway, Hermes blocks it deliberately, because the restart SIGTERMs the child that
requested it. Do not spend calls trying to route around that: finish the work, verify
it, then tell the user to run `/restart` in chat and name that as the one remaining
step.
