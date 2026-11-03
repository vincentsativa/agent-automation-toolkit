---
name: hermes-telegram-silent-notifications
description: Use when Telegram messages arrive muted despite config all.
version: 1.0.0
author: Frank
license: MIT
metadata:
  hermes:
    tags: [hermes, telegram, notifications, silent, muted, gateway]
---

# Hermes Telegram Silent Notifications

## Trigger
Vinny reports Telegram messages arriving muted/silent even though `display.platforms.telegram.notifications: all` is set in `~/.hermes/config.yaml`. This has recurred since June 2026.

## Root Cause (the bug)
In `~/.hermes/hermes-agent/plugins/platforms/telegram/adapter.py`, `_resolve_notifications_mode()` read config through `load_gateway_config()` (returns a `GatewayConfig` **dataclass**) passed to `cfg_get()`, which calls `.get()` on it. A dataclass has no `.get()`, so it raises AttributeError, which the `try/except` silently swallows, and the mode falls back to `"important"`, which sends every message with `disable_notification=True`. Result: config value `all` NEVER takes effect; everything is silent regardless of config.

## The Fix (applied 2026-08-09; RE-APPLIED 2026-08-26)
Replace the broken config read with the raw dict loader:

```python
# OLD (broken):
from gateway.config import load_gateway_config
from gateway.run import cfg_get
_gw_cfg = load_gateway_config()
_raw = cfg_get(_gw_cfg, "display", "platforms", "telegram", "notifications")

# NEW (fixed), use the canonical loader already in this file (~line 10375):
from hermes_cli.config import load_config_readonly
_config = load_config_readonly()
_raw = (
    _config.get("display", {})
    .get("platforms", {})
    .get("telegram", {})
    .get("notifications")
)
```

`load_config_readonly()` returns the raw `config.yaml` dict, so `.get()` works correctly.

## REGRESSION WARNING (recurring since June 2026)
This bug has recurred TWICE (June 2026, then again Aug 2026). The fix at
`~/.hermes/hermes-agent/plugins/platforms/telegram/adapter.py` gets overwritten
when the hermes-agent repo updates/reinstalls. Treat it as a regression you must
re-check after every gateway update. Fast check:
`grep -n "cfg_get(_gw_cfg" ~/.hermes/hermes-agent/plugins/platforms/telegram/adapter.py`
- if it returns the dataclass line, the bug is live again → re-apply the patch.

## Steps
1. Confirm config value: `grep -n -A3 "notifications" ~/.hermes/config.yaml` → should show `notifications: all` under `display.platforms.telegram`.
2. Confirm the bug is present: `grep -n "load_gateway_config\|cfg_get(_gw_cfg" ~/.hermes/hermes-agent/plugins/platforms/telegram/adapter.py`, if it still uses the dataclass path, the bug is live.
3. Apply the patch above (use `patch` tool, replace the broken block).
4. Verify compile: `cd ~/.hermes/hermes-agent && venv/bin/python -m py_compile plugins/platforms/telegram/adapter.py`
5. Restart gateway from a SEPARATE shell (the guard blocks restart from inside the gateway session): `hermes gateway restart`
6. Have Vinny send a test message and confirm he gets a push notification.

## Pitfalls
- **Cannot restart gateway from inside the gateway session**, the terminal guard blocks `hermes gateway restart` and any python against the hermes source (SIGTERM propagates). Tell Vinny to run it from a separate shell.
- **Cannot introspect live adapter**, the guard also blocks running python to check `_notifications_mode` at runtime. The only real proof is a test message.
- **Verify timing**, confirm the gateway process start time is AFTER the patch mtime, else the running process loaded stale code.
- The `disable_notification=True` at `gateway/run.py:20315` is for pinning the System topic only, NOT regular sends, don't confuse it with this bug.
