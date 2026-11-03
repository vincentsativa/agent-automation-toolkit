---
name: hermes-shell-hook-guards
description: Use when a text rule must be enforced structurally.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, hooks, enforcement, cron, file-writes]
    related_skills: [hermes-config-editing, hermes-agent]
---

# Hermes Shell Hook Guards

## When to use this

A rule that MUST hold in every run, including scheduled ones, and that has already been violated more than once while living only in prose (a skill paragraph, a constitution article, a memory entry).

Text rules are advisory: an agent that never loaded the text cannot follow it. A `pre_tool_call` hook rewrites or blocks the tool call itself, so the rule holds no matter which model, skill, or cron run is in play. Reach for a hook when the rule is mechanical and checkable (file shape, path, payload content) and the prose version has already failed twice.

Do NOT reach for a hook when a skill, a template, or a `no_agent` script already covers the case, and never when the rule needs judgment rather than a predicate.

**A hook is a change to the user's live system and needs a direct order naming it.** It does not become authorized because a prose rule keeps failing, because the failure was real, or because fixing it is obviously right. Registering one edits `config.yaml` and the hook allowlist, and both change the behavior of every session that follows, including runs that are not yours. "Fix X and look into how to prevent it" authorizes the fix and the investigation, not the build. Report the mechanism you found, name what you would build, and let the user order it.

Before building: ask whether the user asked for a guard, or asked for a diagnosis. If the answer is diagnosis, the deliverable is the finding.

This skill is about building a guard. Where the guard's own content lives is a separate decision; for text deliverables the rule is that no body paragraph is ever hard-wrapped to a column width, verified with:

```bash
awk '{ if (length($0) > m) m = length($0) } END { print m }' <file>
```

A longest line of 80 to 120 characters means the file is hard-wrapped and wrong; the longest line must run to several hundred.

## Procedure

### 1. Confirm the rule is actually being missed, and where

Before writing a guard, prove the prose rule is not reaching the run. Check what recent runs actually received:

```bash
~/.hermes/hermes-agent/venv/bin/python -c "
import sqlite3
con=sqlite3.connect('file:~/state.db?mode=ro',uri=True)
rows=con.execute('select id, system_prompt from sessions order by started_at desc limit 20').fetchall()
for sid,sp in rows:
    print(sid, '| rule present:', bool(sp) and 'RULE SNIPPET HERE' in sp)
"
```

Run Hermes-internal Python with the repo venv interpreter (`~/.hermes/hermes-agent/venv/bin/python`). The plain `python3` on this box cannot import Hermes modules; its path lacks `yaml` and `ruamel`.

An interactive session carrying the rule text while scheduled sessions do not is the signature that the rule needs structural enforcement rather than better wording. Do not stop at diagnosis: the guard is the deliverable.

### 2. Write the guard script

Place it under `~/.hermes/scripts/`. Keep the docstring shape the other guards use: WHY it exists (the measured failure), WHAT it does, scope limits (what it deliberately never touches), and the wire contract.

Read the payload from stdin as JSON and print the response to stdout as JSON. Never write a helper to a fixed scratch path; if the guard needs a temp file, use a fresh `mktemp -d` directory.

### 3. Wire the contract

The payload is serialized by `agent/shell_hooks.py::_serialize_payload`:

```
stdin  {"hook_event_name": "pre_tool_call", "tool_name": "write_file",
        "tool_input": {...the tool's own args...}, "session_id": "...",
        "cwd": "...", "profile": "...",
        "extra": {"turn_id": "...", ...}}
```

Accepted stdout for `pre_tool_call`:

- `{"action": "block", "message": "..."}` stops the call and hands the model the message.
- `{"action": "modify", "args": {...}}` REPLACES the tool's arguments and lets the call proceed. Use this when the fix is to rewrite content rather than refuse it.
- Exit code 2 with stderr text also blocks.

`fail_closed` applies only to `pre_tool_call`; on any other event it is ignored. Emit nothing on stdout to mean "no opinion, proceed".

### 4. Register it, then allowlist it

Two separate steps, and the second one is easy to forget:

1. Add the entry to the `hooks:` block. `config.yaml` is write-protected against the `patch` and `write_file` tools, so use the config Python API:

```bash
cd ~/.hermes/hermes-agent && ./venv/bin/python -c "
from hermes_cli.config import load_config, save_config
cfg = load_config()
pre = cfg.setdefault('hooks', {}).setdefault('pre_tool_call', [])
entry = {'command': 'python3 ~/scripts/<guard>.py',
         'matcher': 'write_file', 'timeout': 15, 'fail_closed': False}
if not any(isinstance(e, dict) and e.get('command','').endswith('<guard>.py') for e in pre):
    pre.insert(0, entry)
save_config(cfg)
"
```

2. Approve the command once, or the hook is silently skipped with only a log warning:

```bash
cd ~/.hermes/hermes-agent && ./venv/bin/python -c "
from agent.shell_hooks import _record_approval
_record_approval('pre_tool_call', 'python3 ~/scripts/<guard>.py')
"
```

The allowlist is `~/.hermes/shell-hooks-allowlist.json`. A non-TTY run (cron, gateway) can never satisfy the interactive consent prompt, so an un-allowlisted hook does nothing there.

### 5. Verify in four layers, then restart

1. Unit probe: pipe a synthetic payload into the script and assert the exact stdout. Include the real failing input, not a convenient one.
2. Live dispatch: register from config and call the real dispatcher, asserting the arguments came back modified:

```bash
cd ~/.hermes/hermes-agent && HERMES_ACCEPT_HOOKS=1 ./venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from hermes_cli.config import load_config
from agent.shell_hooks import register_from_config
register_from_config(load_config())
from hermes_cli.plugins import _dispatch_pre_tool_call_hooks
block, args = _dispatch_pre_tool_call_hooks('write_file', {'path': '/tmp/probe.txt', 'content': WRAPPED_SAMPLE}, task_id='t', session_id='probe', tool_call_id='c')
print(block); print(repr(args.get('content')))
"
```

3. `hermes hooks doctor` must be green for every entry: executable, allowlisted, unchanged since approval, and running clean.
4. Regression sweep: drive the guard over a corpus of real files it should leave alone and confirm zero modifications. A guard that rewrites files it was never meant to touch is worse than the problem it fixes.

Finally the running gateway must be restarted, because it holds the hooks registered at process start. Never restart the gateway from inside a gateway session: that kills the process mid-work. Finish everything else, then name the restart as the single remaining blocker and the exact command.

## Pitfalls

- Do not gate a content rewrite on a character-width band. Wrapped lines that actually reach a reader can run 95 to 101 characters wide (a source list wrapped at a wide column), so a 60 to 86 "looks wrapped" window misses exactly the failure you are fixing. Make the join predicate itself the gate, so only true continuations match.
- A comma-terminated line followed by a line starting alphanumeric is a wrapped list item, and it is the most common real case in delivered reports. Treat it as a continuation.
- Gate on the file extension before touching content. A guard that rewrites `.py`, `.json`, or `.yaml` payloads corrupts code and machine-readable state.
- Use `fail_closed: false` for any guard that rewrites content. A crash or timeout must leave the write untouched, never block it, or a broken guard bricks file writes.
- Protect structural lines explicitly: headings, separator rules, code fences, indented code blocks, table rows, and numbered list markers must never be joined onto a neighbour.
- `matcher` is a fullmatch regex against the tool name. Confirm it matches the tool you mean; an over-broad or misspelled matcher silently does nothing or fires everywhere.
- `hermes hooks revoke` then re-approve after editing an approved script, otherwise `hooks doctor` reports mtime drift and treats the entry as unreviewed.
- A guard that "looks configured" is not configured. Only the allowlist entry plus a green `hooks doctor` proves it will run.
- **Run every offline probe under the interpreter that has the project's packages.** Cron `no_agent` scripts and bare `python3` exec the standalone managed toolchain (`~/.hermes/tools/python-<ver>-<platform>/bin/python3`), whose site-packages holds only `pip`. A probe that imports Hermes modules or `yaml` dies there with `ModuleNotFoundError`, which reads exactly like a broken guard when the guard is fine. Resolve the real environment interpreter from the install record and probe under it:

```bash
ENV_VENV=$(grep -o '"/[^"]*environments/[^"]*venv"' ~/.hermes/installs/*/facts.json | tr -d '"' | head -1)
"$ENV_VENV/bin/python3" <probe.py>
```

  Then run the same probe under the toolchain python: it failing while the toolchain run succeeds is the proof the alert was about the interpreter, not the hook.
- **Confirm the hook still FIRES before believing any report about it.** A guard that exists but has drifted since approval is silently skipped, so check three things together: an allowlist entry for the exact `command` string, `script_mtime_at_approval` in `~/.hermes/shell-hooks-allowlist.json` equal to the script's current mtime to the second, and a synthetic payload that produces the expected stdout. Renaming a stale fixed-path file aside with exit 0 is what a working guard looks like; silence from a guard that should have acted is the failure.
- **A guard whose evaluation imports the project's own modules must re-exec that evaluation under the environment interpreter itself.** The hook is registered as `python3 <script>.py`, so at real dispatch it runs under the standalone toolchain python whose site-packages holds only `pip`. If the guard imports the project's code to evaluate a candidate (rendering a module, loading a config, parsing a record), the import raises `ModuleNotFoundError` inside the guard's own try/except, the guard emits nothing, and the dispatcher reads that as "no opinion, proceed". The guard is then a no-op that reports green in `hooks doctor`. Fix it inside the guard: resolve the environment interpreter from the install record, run the evaluation as a child process under it, and treat a non-zero child exit as an error you surface rather than silence. The offline probe cannot catch this, because a probe run under the right interpreter succeeds while dispatch still fails.
- **Test the block through the real dispatcher, and treat a not-blocked result as a failure to investigate, not a pass.** `_dispatch_pre_tool_call_hooks` collapses any hook crash into an empty result, so a payload that demonstrably blocks when piped directly into the script (`python3 <guard>.py < payload.json`) returning nothing through dispatch means the hook did not run as configured. Pipe the exact serialized payload into the script by hand first: if that blocks and dispatch does not, the fault is the interpreter or the matcher, not the guard logic.
- **Write the guard so its own internal error is never silent.** A guard that fails open on every exception cannot be distinguished from one that correctly had no opinion, and the failure surfaces only when the rule it was built for is violated again. Log the error to a file under `~/.hermes/logs/` or include it on stderr even while exiting 0, so a broken guard leaves a trace.

## References

- `references/pre-tool-call-wire.md` for the exact payload and response shapes, the dispatch entry points, and the verification commands to copy.
