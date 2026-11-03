---
name: setup-telegram-bridge
description: How the Telegram bridge is installed and configured on this machine, so it can be reproduced on Vinny's InstaBox Pi coding agent. Use when he says "set up telegram on the box", "connect telegram on instabox", "same telegram setup on the cloud pi", "make the box's pi talk to telegram", or asks how the Telegram bridge was set up.
---

# Telegram Bridge Setup (pi-telegram)

Recorded 2026-10-31 from the working install on this Windows box. Every value below was read
off the live machine, not remembered.

## What it actually is

`npm:@llblab/pi-telegram` — a pi package (extension + bundled skills). It is **not** a service or
cron. The Telegram poller runs inside the pi process, pinned to that process id and session, so
Telegram only answers while a pi session is open. Closing the terminal stops the bridge; the next
pi session claims the lock and continues.

## Working install here

| Item | Value |
|---|---|
| pi version | 1.4.0 |
| Package version | `@llblab/pi-telegram` 0.58.3 |
| Agent dir | `~\.pi\agent` |
| Package registry | `settings.json` → `"packages": ["npm:@ollama/pi-web-search", "npm:@llblab/pi-telegram"]` |
| Config | `~/.pi/agent/telegram.json` → `profiles.default.botToken`, `profiles.default.allowedUserId: 123456789` |
| Runtime state | `~/.pi/agent/tmp/pi-telegram/state.json`, `logs.jsonl`, `sessions/<session-id>/inbox.json` |

`botToken` is stored in `telegram.json` (0600). Do not copy the token into any notes file — read it
from that file, or from `TELEGRAM_BOT_TOKEN` / `TELEGRAM_BOT_KEY` / `TELEGRAM_TOKEN` / `TELEGRAM_KEY`
env vars, which the extension accepts as aliases.

## Steps to reproduce (Linux, e.g. the InstaBox pi coding agent)

1. Install the package into that pi's agent dir:
   `pi install npm:@llblab/pi-telegram`
   (Git variant: `pi install git:github.com/llblab/pi-telegram`.) Restart pi afterwards so the
   package loads and its bundled skills appear.
2. Get a bot token from [@BotFather](https://t.me/BotFather) (`/newbot`). A **second, separate bot**
   if this Windows session keeps running — see the conflict note below.
3. Pre-seed the owner before connecting, so the first stranger to send `/start` cannot pair:
   write `~/.pi/agent/telegram.json`
   ```json
   { "profiles": { "default": { "botToken": "<token>", "allowedUserId": 123456789 } } }
   ```
   with `0600` permissions.
4. In a live pi session on the box: `/telegram-setup` (saves and validates the token), then
   `/telegram-connect` (acquires polling ownership). `/telegram-setup <name>` creates an extra
   named bot profile instead of overwriting `default`.
5. Send `/start` to the bot from the allowed account. Confirm the reply.
6. Verify, don't assume:
   - `~/.pi/agent/tmp/pi-telegram/state.json` → `profiles.<name>.transport.pid` is a live pid and
     `cwd` is the expected workspace.
   - `tail ~/.pi/agent/tmp/pi-telegram/logs.jsonl` shows inbound updates and replies.
7. Optional: in BotFather → bot → **Settings** (Mini App, "Open App"), enable **Threaded Mode** if
   you want per-topic parallel sessions. It is **off** on this Windows install
   (`state.json` → `workspace.bot.threadMode: "disabled"`,
   `lastReconcileAction: "startup-bot-topics-disabled"`), so this box runs classic single-owner DM
   mode. The bridge does not error when a BotFather capability is off; the feature just never fires.

## Conflict rule (this is the one that will bite)

Polling ownership is a per-profile singleton lock keyed to the process. Two machines cannot poll
the same bot token: ten consecutive `getUpdates` conflicts stop that instance's transport with a
`persistent-conflict` diagnostic, and it does not auto-retry — recovery is removing the competing
client and running `/telegram-connect` again. So on the box: use a different bot, or shut the
Windows session down first.

## Notes for the box, to confirm at that time (not verified from here)

- The box's pi agent dir may not be `~/.pi/agent`; check `PI_CODING_AGENT_DIR` before writing
  `telegram.json`.
- The box runs Linux, so paths and permissions are POSIX; the same files and commands apply.
- Whether the box's pi build loads npm packages the same way (it should; same package manifest).
