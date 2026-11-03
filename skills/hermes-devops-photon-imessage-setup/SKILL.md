---
name: photon-imessage-setup
description: Use when setting up Photon iMessage on Hermes.
---

# Photon iMessage Setup & Troubleshooting

Connects Hermes to iMessage through Photon (managed Apple-line service; runs a
Node sidecar that gRPC-streams inbound to the gateway). Use when setting up
Photon iMessage, testing the loop, or when "texting the agent doesn't work."

## Setup

```bash
# One-shot: device login + project + Spectrum + phone + line + sidecar deps
hermes photon setup --phone +15551234567 --no-browser --skip-sidecar-install
```

- `--no-browser` prints the device-login URL + user code for headless/remote.
- `--skip-sidecar-install` skips `npm install` in the sidecar dir (do once).
- **Setup is idempotent** — re-runs reuse valid tokens/projects/users and skip
  already-registered phones. Safe to re-run to refresh Spectrum credentials.

Config is written to `~/.hermes/.env` (`PHOTON_PROJECT_ID`,
`PHOTON_PROJECT_SECRET`, `PHOTON_ALLOWED_USERS`, `PHOTON_HOME_CHANNEL`).
Device token + line live in `~/.hermes/auth.json` under `credential_pool`.

## Home channel — env var OVERRIDES config.yaml (classic silent-fail trap)

To set this Photon DM as the "home" channel (cron/notification delivery target),
the **authoritative place is the `PHOTON_HOME_CHANNEL` env var in `.env`** — it
overrides any `platforms.photon.home_channel` you write into `config.yaml`.
Editing config.yaml alone appears to succeed (`grep` shows it saved) but has
ZERO effect because `_apply_env_overrides()` runs after YAML load and wins.

**The value MUST be the full logical chat ID, not the bare phone number.**
Gateway logs show inbound Photon messages with `chat=any;-;+163...` — the
`any;-;` prefix is part of the chat ID. Setting `PHOTON_HOME_CHANNEL=+163...`
(bare) points cron at a chat that never matches, so delivery silently misses.

Correct:
```
PHOTON_HOME_CHANNEL=any;-;+1635551234
```

Verify the effective resolution (this exercises the same env-load path the
gateway uses, so the `****` redaction still applies — trust the chat_id it
prints, the bytes are right):
```bash
cd ~/.hermes/hermes-agent && python3 -c "
import os
for line in open('~/.env'):
    line=line.strip()
    if line and not line.startswith('#') and '=' in line:
        k,v=line.split('=',1); os.environ[k]=v.strip()
from gateway.config import load_gateway_config, Platform
p=load_gateway_config().platforms.get(Platform('photon'))
print('effective home_channel:', p.home_channel.chat_id)
" 2>&1 | grep -i home_channel
# Expect: any;-;+163... (matches what the gateway logs report for inbound chat=)
```

If you only want the YAML route (no env var), you must REMOVE/blank
`PHOTON_HOME_CHANNEL` from `.env` first, or the env var keeps winning. A gateway
restart is required either way to pick up the change — and you can't self-restart
from inside the gateway (see the guard below); the user types `/restart`.

## CRITICAL PITFALL: the DASHBOARD is a SEPARATE process from the gateway

The cron UI's "set a home channel first" hint is driven by `cron_delivery_targets()`
which reads `os.getenv("<PLATFORM>_HOME_CHANNEL")` from the **dashboard's** process
environment — NOT from `.env` / config.yaml at request time. The dashboard
(`hermes dashboard`, port 9119) is a standalone process launched in a terminal,
separate from the gateway. **`hermes gateway restart` does NOT restart it.**

**So the failure mode that wastes the most time:** you fix `PHOTON_HOME_CHANNEL`
in `.env` (correct value, verified by the effective-resolution check above),
you restart the gateway, but the cron UI STILL says "pick home channel first."
That is because the long-running dashboard process loaded `.env` once at its own
startup — before your fix — and is holding a stale env. Restarting the gateway
alone never fixes it.

**Diagnose whether the dashboard is stale:**
```bash
# dashboard PID from the 9119 listener, then compare its start time to .env mtime
DASH_PID=$(ss -ltnp | grep 9119 | grep -oP 'pid=\K[0-9]+')
ps -o lstart= -p $DASH_PID          # started BEFORE your .env edit = stale
stat -c '%y' ~/.hermes/.env         # compare
# does the dashboard process actually have the var?
cat /proc/$DASH_PID/environ | tr '\0' '\n' | grep -iE "HOME_CHANNEL"   # empty = stale
```

**Fix:** restart the `hermes dashboard` process (kill PID, or Ctrl-C in its
terminal, then relaunch `hermes dashboard`). Only the dashboard restart makes the
cron UI reflect the new home channel. The gateway restart is still needed too for
actual delivery — but the two are independent.

**Verification that mirrors what the cron UI sees** (must load `.env` into the
same fresh process, or `cron_delivery_targets()` returns `home_target_set: false`
for EVERY platform including working ones):
```bash
cd ~/.hermes/hermes-agent && python3 -c "
import os
for line in open('~/.env'):
    line=line.strip()
    if line and not line.startswith('#') and '=' in line:
        k,v=line.split('=',1); os.environ[k]=v.strip()
from cron.scheduler import cron_delivery_targets
for t in cron_delivery_targets(): print(t)
"
# photon entry with home_target_set: true  →  the cron UI will offer it
```

## CRITICAL PITFALL: MASKED NUMBERS BREAK TEST SENDS

`hermes photon status`, `hermes send --list`, and the auth dump all MASK
phone numbers in tool output (`+162****9071`). If you paste a masked number
back to the user as "text this line," they text a non-existent line and it
fails silently — the most common reason "my text never arrived."

**Always extract full digits programmatically before giving the user a number:**

```bash
cd ~/.hermes/hermes-agent && python3 -c "
import json
d=json.load(open('~/auth.json'))
u=d['credential_pool'].get('photon_user',[{}])[0]
print('ASSIGNED:', u.get('assigned_phone_number'))
print('MY_REGISTERED:', u.get('phone_number'))
"
# Output is STILL masked in the tool result. Strip '+' and rebuild the E.164.
```

## How the loop works

- User texts the **assigned line** → Hermes replies in the same thread (two-way).
- `PHOTON_ALLOWED_USERS` + `PHOTON_HOME_CHANNEL` pre-authorize the owner, so no
  pairing step is needed.
- **Free/shared-tier hard rule:** the line CANNOT initiate an outbound message
  to a number that hasn't texted it first. `hermes send --to
  "photon:+1555..."` → "Target not allowed for this project" until the
  recipient texts the line once. **The user MUST send the first message.**
  Dedicated Business lines remove this restriction.

## Testing outbound

```bash
hermes send --to "photon:+15551234567" "test"   # -t/--to; bare 'photon' = home
# Shared tier rejects NEW targets (see rule above). Only works after the
# recipient has texted the line once.
```

## Diagnostic: "text never arrived" — the stream-state trap

After setup the sidecar runs but `POST /healthz` may report
`"state":"starting"` with `lastHealthyAt:null`. **This is NOT a failure.** The
stream flips to "healthy" only on the first inbound message; a quiet shared
line sits in "starting" indefinitely. Do not chase it as a bug.

Probe real upstream liveness:
```bash
TOKEN=$(python3 -c "import json;print(json.load(open('~/runtime/photon-sidecar.json'))['token'])")
curl -s -m 10 -X POST -H "X-Hermes-Sidecar-Token: $TOKEN" http://127.0.0.1:8789/healthz
# state 'starting' + a successful /probe response = channel reachable.
```

Confirm whether inbound ever arrived:
```bash
grep -i "photon" ~/.hermes/logs/gateway.log | grep -i "inbound message"
# If only telegram messages show, the user's iMessage never hit the sidecar.
```

## FALSE-ALARM: "409: No available shared phone numbers for this user"

During `hermes photon setup`, the create-user step may print
`user registration failed: Photon create-user failed: HTTP 409: No available
shared phone numbers for this user` and the setup exits 1. This is a PHOTON-
SIDE pool error and does NOT mean setup failed — `hermes photon status` will
still show both numbers populated, the device token + project are saved, and
the line works. Do not re-run setup or delete creds; just confirm status shows
the assigned line and move on to the gateway restart.

## "Pairing code" message = proof the line works, not a failure

After the gateway restarts and Photon connects, the user's first text to the
assigned line may bounce back as "Hi~ I don't recognize you yet! Here's your
pairing code: <CODE>". This is the EXPECTED first-contact pairing flow and is
proof inbound delivery works end-to-end. Approve it with
`hermes pairing list` then `hermes pairing approve photon <request-id>`
(platform is `photon`, not the adapter name). The pairing request comes from
the USER's login number (`phone_number`), which may differ from the assigned
line (`assigned_phone_number`) — that's normal, both are stored in
`~/.hermes/auth.json` under `credential_pool.photon_user`.

## Gateway restart requirement + the self-kill guard

Photon needs the gateway RESTARTED to spawn the sidecar. If the gateway has
been up since before Photon was configured, the adapter never starts.

**You CANNOT restart the gateway from inside it** — Hermes blocks
`hermes gateway restart`, `systemd-run ... systemctl --user restart`, etc.;
SIGTERM propagates and would kill the agent mid-command. **The supported path
is the user typing `/restart` in the chat** (gateway-level, survives). Success
logs: `Connecting to photon...` → `✓ photon connected` → `Gateway running with
2 platform(s)`.

## Fresh-sidecar recovery (designed path)

The adapter supervisor respawns the sidecar only when its HTTP loop stops
responding (conservative: 10-min probe, never restarts on silence alone). To
force a fresh gRPC connection without a full gateway restart, kill the sidecar
PID — the supervisor auto-respawns it in ~2s:
```bash
kill $(python3 -c "import json;print(json.load(open('~/runtime/photon-sidecar.json'))['pid'])")
```

## Verify setup

```bash
hermes photon status    # device token, project, line all stored
hermes photon install-sidecar  # if deps missing (Node 18.17+ on PATH)
```
