# WSL + Windows Fleet-Wide Bot Mode Setup

Connecting Vinny's WSL Hermes Desktop (the relay) to his Windows Hermes agent so
both machines' bots appear in one roster and can @mention each other.

## Architecture
- WSL Desktop is the relay. It owns every socket to every registered connection.
- Two loops: roster loop (60s) pushes each gateway the union of agents on the
  OTHER connections; drain loop (4s) delivers queued messages on the target
  machine's socket and posts the reply back.
- The relay moves MESSAGES, not knowledge. Skills/memory do NOT auto-sync.
- Same physical box = trusted LAN, so username/password auth is correct. No
  Tailscale needed.

## Prerequisites
- Both machines on a recent build with the multi-connection stack. Stale build
  shows: "Update Hermes Desktop to chat with agents on other connections."
- Windows Hermes must be a FULL install with `hermes serve` available (not
  Desktop-only). Confirm this first.

## Step 1, Update both sides
- WSL: `hermes update`
- Windows: update Hermes Desktop there too

## Step 2, Run `hermes serve` on Windows
```
hermes serve --host 0.0.0.0 --port 9119
```
Keep it running (process manager so it survives logout/reboot).

Set credentials in Windows `.env` (`%LOCALAPPDATA%\hermes\.env`):
```
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=[REDACTED]
HERMES_DASHBOARD_BASIC_AUTH_SECRET=<random value>
```
The SECRET line matters: without a stable value you get logged out on every
restart. Generate with `openssl rand -base64 32`.

## Step 3, Register Windows from WSL Desktop
1. Settings → Gateways (or plug button in profile rail).
2. Add connection → Remote gateway.
3. Name: `Windows` (must be unique, case-insensitive).
4. Gateway URL: `http://<windows-host-ip>:9119`
   - From WSL, the Windows host IP is the default route's gateway:
     `ip route show default` → the third field. Was `172.23.176.1` on Vinny's box.
5. Sign in → username/password from Step 2.
6. Save, then Test → wait for "Reachable".

## Step 4, Verify
Bots tab shows WSL bots AND the Windows agent. Same-named profiles become
`@name-windows`.

## Gotchas
- "Connection test failed" = backend not reachable. Check `hermes serve` running,
  port 9119 open, token current.
- "Agent shows but won't open" = WebSocket leg failing (proxy/firewall blocking
  `/api/ws`). Re-run Test.
- Windows agent's chats/sessions/memory/routines live on the Windows machine.
  Clicking it in the roster does NOT hop the window over; @mention it or seat it
  in a group chat.
- Never expose a password-protected backend to the open internet. If a machine
  leaves the LAN, switch to OAuth (Nous Portal) or put it behind Tailscale.

## Sources
- https://hermes-agent.nousresearch.com/docs/user-guide/multi-connection-desktop
- https://hermes-agent.nousresearch.com/docs/user-guide/desktop (remote backend section)
- https://hermes-agent.nousresearch.com/docs/user-guide/bot-mode
- Commit d3e087f "feat(bot-mode): bots on every Desktop connection can message each other"
