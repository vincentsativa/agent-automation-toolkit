---
name: pi-coding-agent
description: Use when updating pi coding agent or its Telegram bridge.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [pi, coding-agent, npm, systemd, telegram, updates]
    related_skills: [hermes-agent, vinny-constitution]
---

# pi coding agent: update, verify, bridge

## When to Use

Load this when Vinny says update pi, update my coding agent, check the pi extensions, or asks whether pi is connected to Telegram. Also load it when a pi session or its Telegram bot behaves oddly and the bridge state needs reading.

Pi is Vinny's second coding harness, launched on this box as `ollama launch pi --model deepseek-v4.1-flash:1017-cloud` and exposed to Telegram through a long-lived RPC bridge. Maintenance has three moving parts: the core binary, the extension packages, and the bridge process. Update all three in one pass, then prove the live state, because a version bump on disk is not a running update.

## Layout

- Binary: `~/.local/bin/pi`, global npm package `@earendil-works/pi-coding-agent` under `~/.local/lib`.
- Agent state: `~/.pi/agent/`. `settings.json` holds `defaultModel`, `telegram.json` holds the bot token and allowed chat id, `models.json` the model catalog.
- Extensions: their own npm project at `~/.pi/agent/npm` (package.json named `pi-extensions`).
- Bridge host: systemd user unit `pi-telegram.service`, unit file `~/.config/systemd/user/pi-telegram.service`, RPC log `/data/workspace/pi-telegram-rpc.log`.

## Procedure

1. Read the before state: `pi --version` and `pi list`.
2. Core and catalogs: `pi update self`, then `pi update` (model catalogs). Re-check `pi --version`.
3. Extensions: run `npm outdated` inside `~/.pi/agent/npm`, bump every listed package with `npm install <pkg>@latest` in that directory, then `pi update --extensions` and `npm ls --depth=0` to confirm what is installed.
4. Restart the bridge: `systemctl --user restart pi-telegram.service`. This is mandatory after any extension bump: the unit runs one long-lived `pi --mode rpc` that loaded its extensions at spawn, so on-disk updates change nothing for the process that is already serving Telegram.
5. Verify live, wait included. Sleep ~20s first (the Telegram loop auto-starts about 17s after the process comes up), then check in this order:
   - `systemctl --user is-active pi-telegram.service`
   - `state.json`: `transport.pid` is a fresh pid that exists in `/proc`, `runtime.runtime.pollingActive == true` with `polling.phase == "long-poll"`, `lockState == "active here"`
   - last `setStatus` lines in `/data/workspace/pi-telegram-rpc.log` read `telegram connected`
   - live `getMe` against the token in `telegram.json`; print only `ok` and the bot username, never the token
   - Or run `scripts/verify-telegram-bridge.py`, which does all four checks and exits non-zero when unhealthy.
6. Report proven numbers only: core version, extension versions, bridge pid plus polling state, bot username.

## Pitfalls

- `npm update` in `~/.pi/agent/npm` never crosses a 0.x minor: a `^0.58.3` range excludes `0.59.0`, so it reports nothing to do while a newer minor exists. `npm outdated` shows the real gap; `npm install <pkg>@latest` is the bump.
- `pi update` deliberately skips extensions (it prints "Extensions are skipped"). Run `pi update self`, `pi update`, and `pi update --extensions` as three commands; "pi is already up to date" says nothing about the extension packages.
- Reading `state.json` immediately after a restart shows `pollingActive: false, phase: stopped, stopReason: not-started`. That is the pre-auto-start window, not a failure; re-read after the wait instead of reporting a dead bridge.
- `runtime.diagnostics.syncState.*` values of `unknown` right after a restart are reset artifacts, not faults. Judge health by `pollingActive`, `lockState`, and the final `setStatus`.
- The launch-line `--model` and `settings.json.defaultModel` are independent. Updating pi rewrites neither, so keep them equal or Telegram sessions and the launch command drift onto different models.
- `telegram.json` tokens and the `busSecret` in `state.json` are credentials: read them in code, print only verification outcomes.

## Support files

- `references/telegram-bridge.md`: who runs what, the state.json and log map, restart semantics.
- `scripts/verify-telegram-bridge.py`: one-shot health probe for the bridge and the bot.
