# pre_tool_call wire contract and verification

Depth for step 3 and step 5 of the skill. Everything here was read from the live tree; re-check against the source before relying on a detail.

## Source of truth

`agent/shell_hooks.py` in `~/.hermes/hermes-agent/`. Read these specific symbols rather than the whole file:

- `_serialize_payload` builds the stdin payload.
- `_payload_fields` lists the top-level keys; anything not in `_TOP_LEVEL_PAYLOAD_KEYS` lands under `extra`.
- `_parse_pre_tool_call` is the response parser, and it accepts two dialects.
- `_evaluate_result` decides block versus proceed, including the exit-code-2 path and fail-open behavior.
- `register_from_config` is the registration path and shows the allowlist gate.
- `_BLOCKING_EVENTS` is the set of events whose directives are honored downstream.

## stdin payload

```json
{
  "hook_event_name": "pre_tool_call",
  "tool_name": "write_file",
  "tool_input": { "path": "/abs/path.txt", "content": "..." },
  "session_id": "cron_<job>_<stamp>",
  "cwd": "~",
  "profile": "default",
  "extra": { "turn_id": "...", "task_id": "...", "tool_call_id": "..." }
}
```

`tool_input` carries the tool's own argument dict, so a `write_file` guard reads `path` and `content` from it. Tolerate a missing `tool_input` by also checking `args`, which is how the CLI test path delivers them.

## stdout responses

| Response | Effect |
|---|---|
| `{"action": "block", "message": "..."}` | Tool call is refused; the message is shown to the model as the tool result. |
| `{"action": "modify", "args": {...}}` | The argument dict is replaced wholesale and the call proceeds. Return the full args, not a partial patch. |
| `{"action": "approve", "message": "..."}` | Escalates to the human approval gate. Hermes-only; not part of the Claude-Code dialect. |
| nothing on stdout, exit 0 | No opinion. The call proceeds untouched. This is the correct output when the guard decides the payload is fine, and it is what `hooks doctor` reports as "observer-only". |

`{"decision": "..."}` is accepted as a Claude-Code-compatible alias for `action`, with `tool_input` as the modify payload key instead of `args`. Prefer the Hermes `action` shape in guards you write.

Exit code 2 blocks when stderr (or a stdout block directive) supplies the message. Any other non-zero exit is logged as a warning and the stdout is still parsed, so a guard that fails should still prefer printing nothing over printing garbage.

## Verification commands

Synthetic probe, the layer that catches a guard whose predicate is wrong:

```bash
/usr/bin/python3 ~/.hermes/scripts/<guard>.py <<'JSON'
{"hook_event_name": "pre_tool_call", "tool_name": "write_file",
 "tool_input": {"path": "/tmp/probe/report.txt", "content": "line one, a,\nline two continues here\n"}}
JSON
```

Live dispatch through the real hook chain (register first, or the dispatch sees zero hooks):

```bash
cd ~/.hermes/hermes-agent && HERMES_ACCEPT_HOOKS=1 ./venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from hermes_cli.config import load_config
from agent.shell_hooks import register_from_config
print([s.command for s in register_from_config(load_config())])
from hermes_cli.plugins import _dispatch_pre_tool_call_hooks
block, args = _dispatch_pre_tool_call_hooks('write_file', {'path': '/tmp/probe.txt', 'content': 'WRAPPED SAMPLE'}, task_id='t', session_id='probe', tool_call_id='c')
print('block:', block)
print('after:', repr(args.get('content')))
"
```

Status and consent:

```bash
hermes hooks list          # configured hooks with matcher, timeout, consent status
hermes hooks doctor        # exec bit, allowlist, mtime drift, JSON validity, run timing
hermes hooks revoke CMD    # drop allowlist entries after editing an approved script
```

## Regression sweep shape

Drive the guard over real files it must not modify and assert zero modifications. Feed each file's current content through the script and count the responses that are not empty:

```python
for path in corpus:
    text = open(path, encoding='utf-8', errors='replace').read()
    out = probe_guard(path, text)
    if out:
        print('WOULD MODIFY', path)
```

Any hit on a file that is already correct means the predicate is too loose. Inspect the diff before shipping the guard: an over-eager rewrite silently corrupts documents nobody re-reads.

## Pitfalls specific to the wire

- A registration whose command is not allowlisted is skipped with a log warning and no error. Non-TTY surfaces (cron, gateway) cannot answer the consent prompt at all, so approve the command at install time.
- `hook_event_name` is checked by the guards, not by the framework alone. Guard scripts that skip that check fire on every event they are wired for.
- Return the complete argument dict from a `modify` response. Returning only the changed key drops the rest of the tool call's arguments.
- Registering from config is idempotent per process; a second `register_from_config` call will not duplicate the hook, so a repeated registration is not proof it is wired.
