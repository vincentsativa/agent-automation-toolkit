# Hermes Gateway Troubleshooting

## Token/Credential Rejection Errors

### Symptoms
- Gateway service shows `startup_failed` state
- Error: "token was rejected by the server"
- Logs show token appears masked/truncated (e.g., `858018...fmxU`)
- Systemd service entering failed state after retry exhaustion

### Root Cause
Credentials file (`~/.hermes/.env`) contains corrupted, truncated, or masked tokens.

### Diagnosis
```bash
# Check gateway logs
grep -i "token\|credential\|error" ~/.hermes/logs/gateway.log | tail -20

# Verify .env has full tokens (not truncated)
grep -v "^#" ~/.hermes/.env | grep -v "^$"

# If .env looks correct, test the credential directly via API
curl -s -X POST "https://api.openai.com/v1/models" \
  -H "Authorization: Bearer $(grep OPENAI_API_KEY ~/.hermes/.env | cut -d= -f2)" \
  --max-time 10 | head -5
```

### Fixes

1. **Re-enter the credential**, edit .env with the full un-truncated token
2. **Restart gateway**: `hermes gateway restart`
3. **If systemd fails**: `systemctl --user reset-failed hermes-gateway && systemctl --user restart hermes-gateway`

### Prevention
- Never copy tokens from truncated UI displays
- After any .env edit, run `hermes doctor --fix` to validate

## Gateway Dies on SSH Logout

**Fix:** Enable systemd user linger:
```bash
sudo loginctl enable-linger $USER
```

## Gateway Dies on WSL2 Close

**Fix:** Set `systemd=true` in `/etc/wsl.conf`, or use PowerShell task scheduler to start `hermes gateway` on Windows boot.

## Gateway Crash Loop

```bash
systemctl --user reset-failed hermes-gateway
```

## Discord Bot Silent

Check **Message Content Intent** in Bot → Privileged Gateway Intents (Discord Developer Portal).

## Slack Bot Only Works in DMs

Must subscribe to `message.channels` event in Slack app config.

## Windows HTTP 400 "No models provided"

Config file has BOM (byte order mark). Save as UTF-8 without BOM.

## Full Gateway Log Access

```bash
less ~/.hermes/logs/gateway.log
journalctl --user -u hermes-gateway --no-pager -n 50
```