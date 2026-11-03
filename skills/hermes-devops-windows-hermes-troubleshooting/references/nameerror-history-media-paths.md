# NameError: `_history_media_paths` Not Defined

## Symptoms

Every message to the gateway succeeds (agent responds) but is immediately followed by:

> "Sorry, I encountered an unexpected error. Try again or use /reset to start a fresh session."

Gateway logs show:

```
ERROR gateway.run: Agent error in session agent:main:...
NameError: name '_history_media_paths' is not defined
```

## Root Cause

A code bug in `gateway/run.py` at the `already_sent` media-delivery path. The variable `_history_media_paths` is referenced at line ~14612 but was never defined in that method (`_handle_message_with_agent`). It's only defined in a different method (`_process_message_background` at line ~22033).

## Fix

Add the missing variable definition before the reference:

```python
# In gateway/run.py, inside the `if agent_result.get("already_sent")` block:
if agent_result.get("already_sent") and not agent_result.get("failed"):
    if response:
        _media_adapter = self._adapter_for_source(source)
        if _media_adapter:
            # Add this line:
            _history_media_paths: set = _collect_history_media_paths(agent_messages)
            await self._deliver_media_from_response(
                response, event, _media_adapter,
                history_media_paths=_history_media_paths,
            )
```

## Apply to Multiple Installs

The same bug exists in every Hermes install running the same version:

| Install | Path |
|---------|------|
| WSL/Linux | `~/.hermes/hermes-agent/gateway/run.py` |
| Windows | `C:\Users\<username>\AppData\Local\hermes\hermes-agent\gateway\run.py` |

From WSL, the Windows path is at:
`/mnt/c/Users/<username>/AppData/Local/hermes/hermes-agent/gateway/run.py`

Apply the same patch to each.

## Restart After Fix

The gateway cannot restart itself from inside the gateway process (SIGTERM propagates to child processes and kills the command). Use one of these methods:

- **From a separate terminal:** `hermes gateway restart`
- **Force-kill the PID** (systemd auto-restarts): `kill <MainPID>` then verify new PID with `systemctl --user show hermes-gateway --property=MainPID,ActiveState`
- **On Windows:** Kill the process from Task Manager or `taskkill /F /IM python.exe` and restart

## Verification

After restart, check logs for no NameError:

```bash
tail -20 ~/.hermes/logs/gateway.log | grep -i "error\|NameError"
```

Should return nothing.
