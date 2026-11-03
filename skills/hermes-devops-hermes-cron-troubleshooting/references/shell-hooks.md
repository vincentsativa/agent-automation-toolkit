# Declarative shell hooks (config.yaml `hooks:`)

Scripts Hermes runs on lifecycle events, wired from `~/.hermes/config.yaml`. Their
value is that they are **deterministic**: they fire whether or not the model
cooperates, which makes them the right tool for a guard, a hard gate, or a cleanup
that must happen every time. Prefer them over a prompt instruction when the behavior
is mandatory.

## Config block

```yaml
hooks:
  pre_tool_call:
    - command: python3 ~/scripts/<name>.py
      matcher: write_file        # regex; honored ONLY for pre_tool_call / post_tool_call
      timeout: 15                # default 60, max 300
      fail_closed: false         # true = spawn error/timeout BLOCKS the action
```

`matcher` is ignored (with a warning) on any other event, and the hook then fires on
every instance of that event.

## The allowlist gate, why a correct hook can silently never run

Registration requires an entry in `~/.hermes/shell-hooks-allowlist.json` keyed by
`(event, command)`. The gateway has **no TTY**, so it cannot prompt. An unapproved
hook is skipped with only a log line: no error, it just never fires.

Approval comes from one of:
- `hooks_auto_accept: true` in config.yaml
- `HERMES_ACCEPT_HOOKS=1`
- an interactive TTY prompt
- writing the allowlist entry directly (the normal route for a headless/gateway setup)

```python
import sys; sys.path.insert(0, "~/hermes-agent")
from agent.shell_hooks import _record_approval
_record_approval("pre_tool_call", "python3 ~/scripts/<name>.py")
```

**mtime drift silently disables the hook.** The entry stores
`script_mtime_at_approval`; editing the script afterwards invalidates consent and the
hook stops firing. **Re-approve after every edit to the hook script.** This is the
most common cause of "I fixed the hook and it still does nothing".

## Wire format, the key-name trap

stdin is JSON:

```json
{"hook_event_name": "pre_tool_call", "tool_name": "write_file",
 "tool_input": {"path": "...", "content": "..."},
 "session_id": "...", "cwd": "...", "profile": "...", "extra": {}}
```

Tool arguments arrive under **`tool_input`**. But `hermes hooks test --payload-file`
merges your JSON over a built-in default that spells the same thing **`args`**. A
script that reads only one of the two will pass the CLI test and do nothing on a real
fire. Read both:

```python
for key in ("tool_input", "args"):
    val = payload.get(key)
    if isinstance(val, dict):
        return val
```

stdout is parsed only for events that have a response channel:
- `{"action": "block", "message": "..."}`, block the tool call
- `{"action": "modify", "args": {...}}`, replace the tool's arguments
- exit code `2` also blocks a `pre_tool_call`, even with no JSON

Print **nothing** when the hook is not acting; stray stdout on a `fail_closed: true`
hook reads as a malformed gate response. Put diagnostics on stderr, that reaches the
log, not the parser.

## Restart requirement

Hooks register **at gateway / CLI startup only.** Editing config.yaml or the allowlist
does not affect an already-running gateway. Note that `hermes gateway restart` is
blocked from inside a gateway session (the SIGTERM would kill the command), so it must
come from a separate terminal or from the user.

## Inspecting and testing

```bash
hermes hooks list                                   # configured + consent status
hermes hooks doctor                                 # exec bit, allowlist, mtime drift, synthetic run
hermes hooks test pre_tool_call --for-tool write_file --payload-file p.json
hermes hooks revoke "python3 /path/hook.py"        # drop allowlist entries
```

`doctor` is the fastest end-to-end health check, but it does NOT catch the key-name
trap: it validates and runs the hook, not whether the hook understood the payload.
Always test with the REAL `tool_input` shape as well.

**Liveness proof.** The only proof a hook is actually live in the running gateway is
firing a real tool call through it: make the tool call the hook is meant to rescue and
confirm it now succeeds. A passing `hermes hooks test` on a freshly restarted process
is not that proof until the real path is exercised.

## Choosing the response for a "repair the input" hook

When the hook exists to stop a known-bad argument from reaching a tool, there are three
shapes and only the third removes the failure:

| Shape | Effect |
|---|---|
| `block` | The call still fails. If a verifier footer reports failed mutations, the symptom remains. |
| `modify` the argument | The write lands, but anything that later references the ORIGINAL path breaks. |
| fix the cause, then allow | The call succeeds at the intended path. Preferred. |

For a stale-file collision that means **move the stale file aside**
(`os.replace(path, path + ".stale-<utcstamp>")`) so the intended write creates the file
fresh at the same path. Rename, never delete: if the write then fails for an unrelated
reason, nothing was lost. Prune asides by count so they do not grow unbounded.

Keep the hook's scope narrow and explicit: match on exact parent directories and file
extensions, never touch a directory, and verify the hook **cannot act on its own
script**, a naive directory-wide rule will move the guard itself.
