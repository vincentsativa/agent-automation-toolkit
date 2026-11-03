---
name: hermes-gateway-troubleshooting
title: Hermes Gateway Troubleshooting
description: Diagnostic and repair patterns for Hermes Gateway failures, especially credential and connectivity issues.
version: 1.0.0
created: 2026-04-14
---

# Hermes Gateway Troubleshooting

## Token/Credential Rejection Errors

### Symptoms
- Gateway service shows `startup_failed` state
- Error: "token was rejected by the server"
- Logs show token appears masked/truncated (e.g., `858018...fmxU`)
- Systemd service entering failed state after retry exhaustion

### Root Cause
Credentials file (`~/.hermes/.env`) contains corrupted, truncated, or masked tokens. Common causes:
- Copy-paste truncated the token
- Previous masking/encryption left partial value
- Manual editing introduced ellipsis or placeholders

### Diagnostic Steps

```bash
# 1. Check gateway status and error
hermes gateway status

# 2. Read the error log
tail -30 ~/.hermes/logs/gateway.log

# 3. Check what's actually in the env file
grep TOKEN ~/.hermes/.env | grep -v "^#"

# 4. Test token directly with API
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
# Should return: {"ok":true,"result":{...}}
# If 404/InvalidToken: token is corrupted
```

### Critical: Masked Output != Corruption

**False positive trap**: read_file and log output display `858018...fmxU` even when the actual file contains the full token. This happens due to built-in credential masking.

**ALWAYS verify token validity with:**
```bash
cat ~/.hermes/.env | sed -n 'LINENUMBERp' | xxd
# Shows actual bytes, not masked display

curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
# ONLY this proves if token is valid
```

If `curl getMe` returns `ok:true`, the token is correct. The real issue is typically:
1. Stale systemd failed state (service won't restart after 5 failures)
2. Lingering zombie gateway processes
3. Missing environment vars like TELEGRAM_ALLOWED_USERS

### Fix Pattern

**Identify the corrupted line:**
```bash
grep -n "TELEGRAM_BOT_TOKEN" ~/.hermes/.env
# Note the line number (e.g., line 392)
```

**Replace with full token:**
```bash
# Using sed with line number
sed -i '392s/.*/TELEGRAM_BOT_TOKEN=YOUR_FULL_TOKEN_HERE/' ~/.hermes/.env

# Verify
source ~/.hermes/.env
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
```

### Gateway Restart After Fix

```bash
# Clear failed state (systemd blocks after 5 failures)
systemctl --user reset-failed hermes-gateway.service

# Kill any lingering processes
pkill -f 'hermes gateway'

# Start in tmux for monitoring
tmux new -s gateway -d 'export $(grep -v "^#" ~/.hermes/.env | xargs) \&\& hermes gateway run --replace'

# Verify
sleep 5 \&\& hermes gateway status
```

## Inbound Message Refused: `invalid_params: <clause>`

### Symptom

A user reports a warning reply they never sent to anyone: `Hermes refused this message (invalid_params: <clause>), so it was not saved or answered`. The turn is dropped whole. Nothing reached the agent, so the agent has no memory of the content.

### Read the refusal before touching anything

```bash
grep -a -n "Native admission refused" ~/.hermes/logs/gateway.log | tail -5
grep -rn "'<clause>'" --include="*.py" gateway/session_envelope.py
```

Use `grep -a`: `gateway.log` contains binary bytes and plain grep prints `binary file matches` instead of the line. The log line names the platform, chat, and message id, which is how you line it up with the messages cached just before it.

`gateway/session_envelope.py` `_media_clause()` returns the clause name, checked in order (`media_urls`, `media_types`, `media_text_inlined`, then the two length checks). A length clause means the lists disagree, not that the data is bad.

### The invariant behind every media length clause

`media_urls`, `media_types`, and `media_text_inlined` are index-aligned coordinate lists for ONE event. Any merge lane that extends `media_urls` must extend the other two in step. An adapter merge that appends URLs without the flags hands the envelope 3 URLs and 1 flag, and the honest gate refuses a message the user did send.

Albums are the usual trigger: each file arrives as its own event carrying `media_text_inlined=[True]` (text injected) or `[False]` (binary, path only), and the group merger concatenates the URLs.

See `references/native-admission-refusals.md` for the clause table, the merge lanes to audit, and how to recover what was dropped.

### Fix shape

One alignment helper used by every lane: truncate the flag list to `len(media_urls)`, then pad with `None` to the same length. Truncation matters as much as padding, because a lane that replaced `media_urls` can leave more flags than URLs. Do not patch only the lane in the report; the same omission usually exists in the text-batch lane too.

### Tell the user what was lost

A refused turn is not queued, so the message has to be retried. Name the cached files (their paths are in the log lines immediately above the refusal) so nothing is thought lost, and ask for the send again after the reload. A patch on disk does nothing until the gateway process reloads.

## Systemd Service Failures

When service fails with "start request repeated too quickly":
```bash
systemctl --user reset-failed hermes-gateway.service
```

Then investigate the underlying error before restarting.

## Gateway State File

If the gateway crashes, stale state may prevent restart:
```bash
rm -f ~/.hermes/gateway_state.json
```

## Credential Security Note

For security, `.env` files may be "protected" - direct file writes may be rejected. Use terminal/shell commands to edit:
```bash
sed -i 'LINENUMs/old/new/' ~/.hermes/.env
```

## Verification Checklist
- [ ] Token passes API test (`curl getMe` returns ok:true)
- [ ] Allowed users configured (`TELEGRAM_ALLOWED_USERS`)
- [ ] Systemd failed state cleared
- [ ] Old gateway processes killed
- [ ] Gateway status shows Active (running)

## Gateway Restarts Kill In-Flight Cron Jobs

**Critical behavior (documented May 5-6, 2026):** The cron scheduler runs inside the same gateway process. ANY gateway restart — model switch, `hermes gateway restart`, config reload, or systemd bounce — terminates all in-flight cron worker processes immediately. Jobs appear as `last_run_at: null` with no completion status even though the cron ticker fired them successfully.

**Detection:** Agent log shows `[cron_JOBID_TIMESTAMP]` prefix with initialization lines but no completion. Output files for that date do not exist.

**Impact:** Time-sensitive cron-based delivery is unreliable during periods of active gateway usage (model switches, config changes, WSL sleep/wake). External scheduling (systemd timer + `hermes task`) is the only reliable cron path.

## Telegram Notifications: Silent Delivery by Default

### Symptoms
- Bot messages arrive visually (you see them in the chat) but with NO sound/vibrate
- OpenClaw bot (or other Telegram bots) makes sound, but Hermes does not
- Telegram chat notifications are confirmed ON in both app settings and OS-level notification channels
- Only gateway messages affected — CLI/terminal sessions not relevant

### Root Cause

Hermes' Telegram adapter defaults to `_notifications_mode = "important"`, which sends **every** message with `disable_notification=True` unless the message's metadata explicitly requests notification.

```python
# In gateway/platforms/telegram.py:
self._notifications_mode: str = "important"

def _notification_kwargs(self, metadata):
    if self._notifications_mode != "important":
        return {}
    if (metadata or {}).get("notify"):
        return {}
    return {"disable_notification": True}   # ← this is the cause
```

Rationale: per-tool-call push notifications were too noisy for Telegram users, so the default setting suppresses all but "important" messages (final responses, approvals, slash confirmations).

### Fix

Change notification mode to `"all"` so every message triggers a push notification:

```bash
hermes config set display.platforms.telegram.notifications all
```

Then restart the gateway:

```bash
hermes gateway restart
```

### Options

| Value | Behavior |
|-------|----------|
| `important` (default) | Only final responses, approvals, and slash confirmations trigger notifications. Status updates, progress messages, and tool output delivered silently. |
| `all` | Every message sent by the bot triggers a push notification. |

### Verification

After changing the setting and restarting, send a test message to the bot. If it arrives with sound, the fix worked. If still silent, the issue is on the Telegram/OS client side — check per-chat notification settings and OS-level notification channels.

### Note: Not a Client-Side Issue

When the user says notifications are ON in the Telegram chat settings and the OpenClaw bot (different bot) makes sound, the problem is NOT client-side. Start here — check the Hermes gateway config — before asking the user to retest their phone settings.

### Pitfall: Config Set Correctly But Still Silent

**Symptom:** `notifications: all` is confirmed in `config.yaml` under `display.platforms.telegram.notifications`, the gateway was restarted, but messages still arrive silently.

**Root cause (code bug):** `_resolve_notifications_mode()` in `plugins/platforms/telegram/adapter.py` calls `load_gateway_config()` which returns a `GatewayConfig` dataclass object, then passes it to `cfg_get()` which expects a plain dict. The `display` key doesn't exist on `GatewayConfig` — it only has gateway-specific fields (`platforms`, `streaming`, etc.). So `cfg_get` returns `None` every time, and the mode always falls back to `"important"` regardless of what's in config.yaml.

**Second bug — cron delivery never sets `notify=True`:** Even if the mode were correctly read, the cron delivery path in `cron/scheduler.py` passes `route_metadata = {"job_id": job["id"]}` with no `"notify": True`. In `"important"` mode, `_notification_kwargs()` returns `{"disable_notification": True}` unless `metadata.get("notify")` is truthy. So cron deliveries are always sent with `disable_notification=True` in the default mode, regardless of the setting. This is a separate code path from the adapter's `send()` method.

**Combined effect:** Two independent bugs stack — the mode can't be read from config, AND cron deliveries don't request notification even if it could. Fixing only one leaves cron silent.

**Diagnostic — confirm the config-reading bug:**

```bash
cd ~/.hermes/hermes-agent
python3 -c "
from gateway.config import load_gateway_config
from hermes_cli.config import cfg_get
cfg = load_gateway_config()
result = cfg_get(cfg, 'display', 'platforms', 'telegram', 'notifications')
print('cfg_get result:', repr(result))
# Should be None even when config.yaml has 'all'
"
```

**Fix (applied 2026-06-26):** Replaced the `cfg_get` call with direct YAML file reading in `_resolve_notifications_mode()`:

```python
# In plugins/platforms/telegram/adapter.py, the cfg_get block was replaced with:
import yaml
from hermes_cli.config import get_hermes_home
_cfg_path = get_hermes_home() / "config.yaml"
if _cfg_path.exists():
    with open(_cfg_path, encoding="utf-8") as _f:
        _raw_cfg = yaml.safe_load(_f) or {}
    _raw = (
        _raw_cfg.get("display", {})
        .get("platforms", {})
        .get("telegram", {})
        .get("notifications")
    )
    if _raw not in {None, ""}:
        mode = str(_raw).strip().lower()
```

**Second fix (cron notify):** In `cron/scheduler.py` `_deliver_result()`, add `"notify": True` to `route_metadata` when the notification mode is `"all"`, so cron deliveries request push notification even in `"important"` mode.

**User preference — don't attempt these fixes unless asked:** The user considers these bugs too trivial to risk breaking the gateway. Do not propose or apply code patches for Telegram notification behavior unless the user explicitly requests it. Document the workaround (env var `HERMES_TELEGRAM_NOTIFICATIONS=all` as a stopgap) instead.

After patching, restart the gateway from a separate terminal (not from inside the gateway session, which would kill itself). The terminal tool refuses a gateway restart issued from inside the gateway, including a delayed `systemd-run` wrapper, so do not try to route around it: ask the user to send `/restart` in chat, or run the command from a shell outside the gateway.

```bash
hermes gateway restart
```

---

## Telegram Model Picker Configuration

The `/model` command in Telegram shows providers/models configured in `custom_providers`.

### How Grouping Works

Hermes groups `custom_providers` by the `name` field. Multiple entries with the same `name` appear as ONE picker row that expands to show model choices:

```yaml
custom_providers:
- name: Ollama.com          # Same display name
  base_url: https://ollama.com/v1
  model: kimi-k2.5
- name: Ollama.com          # Same display name = grouped together
  base_url: https://ollama.com/v1
  model: minimax-m2.7:cloud
- name: Ollama.com
  base_url: https://ollama.com/v1
  model: qwen3.5:cloud
```

### Quick Fix Pattern

To add a model so it appears in Telegram:

```bash
# 1. Find where custom_providers starts
grep -n "custom_providers:" ~/.hermes/config.yaml

# 2. Add entry by appending to the list
# Edit the file to add another - name: entry with same provider name
# Each unique model = one entry in the grouped picker

# 3. Restart gateway to pick up changes
hermes gateway restart
```

If only one model shows up, check that you have multiple entries with the same `name` but different `model` values.

## Model Provider Resolution Failures

### Symptoms
- Session banner shows wrong provider (e.g., `xai` instead of your custom provider)
- Model appears to work but routes through the wrong API endpoint
- You set up a custom provider but Hermes ignores it and falls back to a built-in one

### Root Cause
Hermes resolves which provider handles a model by checking the `models:` list in each provider config. If that list is missing or malformed, the model isn't matched to your custom provider, and Hermes falls back to whichever built-in provider it associates with that model name (often `xai` for models it doesn't recognize).

### The `models:` Field Must Be a YAML List

**Wrong** — stored as a string (happens when `hermes config set` writes a JSON-encoded value):
```yaml
providers:
  ollama-com:
    base_url: https://ollama.com/v1
    api_key: YOUR_KEY
    models: '["minimax-m2.7"]'   # ← STRING, not a list — Hermes can't read it
```

**Correct** — proper YAML list:
```yaml
providers:
  ollama-com:
    base_url: https://ollama.com/v1
    api_key: YOUR_KEY
    models:
    - minimax-m2.7              # ← YAML list — Hermes can match the model
```

### Pitfall: `hermes config set` Serializes Lists as Strings

Using `hermes config set providers.ollama-com.models '["minimax-m2.7"]'` writes a JSON string, not a YAML list. The value ends up as `'["minimax-m2.7"]'` in the YAML file, which Hermes treats as an opaque string and cannot iterate.

**Fix**: Edit `config.yaml` directly with `patch` or a text editor to ensure `models:` is a proper YAML list.

### Verification

```bash
# 1. Check the raw YAML — models should be a list, not a quoted string
grep -A2 'models:' ~/.hermes/config.yaml | head -5

# 2. Confirm provider shows up correctly
hermes config show | grep -A5 'Model'
```