# pi Telegram bridge: who runs what, state map, logs

## Processes

- `pi-telegram.service` (systemd user, enabled, `Restart=always`) runs `bash -c "sleep infinity | /data/home/.local/bin/pi --mode rpc"` with `WorkingDirectory=/data/workspace`. Its stdin is that `sleep`, so nothing outside the unit can write `/telegram-connect` into the pipe; the extension instead auto-starts polling on its own once it acquires the leader lock.
- `~/.pi/agent/bin/telegram-bridge.cjs` with `start-telegram-bridge.cjs` is the older detached launcher: it spawns `pi --mode rpc` itself, writes `/telegram-connect` to its stdin after 6s, and logs to `~/.pi/agent/tmp/telegram-bridge.log`. The systemd unit is the current host, so launcher logs being stale is not a fault.
- Only one instance may own the bridge. `lockState: "active here"` in state.json means this process is the leader; a second pi started in the same cwd sees the lock held.

Restart with `systemctl --user restart pi-telegram.service`. After any extension install or update the restart is what makes the new code serve Telegram: the rpc process reads its extensions once, at spawn.

## state.json map (`~/.pi/agent/tmp/pi-telegram/state.json`)

- `profiles.default.transport.pid`: owning pi process, must be live in `/proc`.
- `profiles.default.runtime.runtime.pollingActive`: Telegram long-poll running, healthy value `true`.
- `...polling.phase`: healthy value `long-poll`. A `stopped` phase carrying `stopReason: not-started` is the pre-auto-start window, roughly the first 17s after start.
- `...lockState`: healthy value `"active here"`.
- `...diagnostics.syncState.*`: `unknown` right after a restart is a reset artifact, not an error.
- `profiles.default.transport.busSecret` and `profiles.default.admission.profileKey`: credentials or fingerprints over the bot token. Read them in code, never print them.

The file is rewritten on a snapshot cadence, so read it once, wait, and read again rather than polling in a tight loop.

## Logs

- `/data/workspace/pi-telegram-rpc.log` (unit stdout/stderr, append): raw rpc lines including `extension_ui_request` `setStatus` events for `telegram connected` / `error` / `disconnected`. No timestamps, tail is newest, and the file spans restarts, so statuses from earlier runs sit above the current ones.
- `~/.pi/agent/tmp/pi-telegram/logs.jsonl`: timestamped structured events (`lock`, `bus`, `new-session`, `reset`) with `at` in epoch ms. This is where auto-start duration, event-loop stalls, and capability probe failures land, so use it for timing questions.
- `~/.pi/agent/tmp/telegram-bridge.log` and `telegram-bridge.out.log`: the detached launcher's own log, relevant only if that launcher is running.

## Verification order

1. `systemctl --user is-active pi-telegram.service`
2. Sleep ~20s if the service was just restarted.
3. Read state.json: pid alive, `pollingActive` true, phase `long-poll`, lock `active here`.
4. Tail the rpc log for a final `telegram connected` setStatus.
5. Live `getMe` with the token from `~/.pi/agent/telegram.json`, printing only `ok` and the bot username.

`python3 <skill_dir>/scripts/verify-telegram-bridge.py` performs steps 1, 3 and 5 and exits non-zero with the failing checks listed.

## Model consistency

`ollama launch pi --model <id>` and the `defaultModel` in `~/.pi/agent/settings.json` are set independently. Bridge sessions follow `defaultModel`, the launch line follows its own flag, and an update touches neither, so keep them equal when the launch line names a model.
