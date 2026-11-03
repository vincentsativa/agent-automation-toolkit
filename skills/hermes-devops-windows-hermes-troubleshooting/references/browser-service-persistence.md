# Making the Hermes Browser Survive Updates

## Symptom / Root Cause

After every `hermes update` (and on reboots), the agent's browser tools fail with "browser not running". The update.log shows the gateway restarting at the same timestamp the browser dies.

Root cause: the dedicated CDP Chromium is launched as a **plain background process that sits inside the gateway's process tree**. When `hermes update` restarts the gateway, the browser is torn down with it. Nothing relaunches it, so it stays dead until someone manually starts it.

The browser must be its own managed service, fully detached from the gateway's lifecycle.

## WSL side (Linux/systemd)

Working unit — `~/.config/systemd/user/hermes-browser.service`:

```ini
[Unit]
Description=Hermes WSL Browser (Chromium CDP on 9222)
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
ExecStart=/usr/bin/xvfb-run -a --server-args="-screen 0 1920x1080x24" ~/.cache/ms-playwright/chromium-1217/chrome-linux64/chrome --remote-debugging-port=9222 --user-data-dir=~/chrome-debug --no-first-run --no-default-browser-check --disable-gpu --disable-software-rasterizer --no-sandbox about:blank
WorkingDirectory=~
Restart=always
RestartSec=5
ExecStartPre=/bin/sh -c 'rm -f ~/chrome-debug/SingletonLock'
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30

[Install]
WantedBy=default.target
```

Two mandatory flags explained:
- `xvfb-run` — WSL has no real display; without a virtual X server Chromium exits with `Missing X server or $DISPLAY`.
- `--disable-gpu --disable-software-rasterizer --no-sandbox` — the WSL GPU environment crashes Chromium with `GPU process isn't usable. Goodbye` then SIGABRT.

Enable + start:
```bash
systemctl --user daemon-reload
systemctl --user enable hermes-browser.service
systemctl --user start hermes-browser.service
```

Verify:
```bash
curl -s http://127.0.0.1:9222/json/version          # must return Chrome version
systemctl --user is-active hermes-browser.service   # active
# Auto-restart test: kill the cgroup, confirm systemd relaunches it
systemctl --user kill hermes-browser.service; sleep 6
systemctl --user is-active hermes-browser.service   # still active
```

Caveat: the exact chromium binary path (`chromium-1217`) can change if playwright's browser rev is bumped by an update. If the service fails to start after an update, re-locate the current binary with `ls ~/.cache/ms-playwright/` and update `ExecStart`.

## Windows side (scheduled task)

Mirror the existing `Hermes_Gateway` scheduled task. There is already an idempotent launcher at `C:\Users\<user>\.hermes\start-windows-browser.bat` that starts Chrome on port 9223 (and does nothing if already listening).

Create the task from WSL via a `.ps1` file (write to `/mnt/c/...`, run with `powershell.exe -ExecutionPolicy Bypass -File`):

```powershell
$action = New-ScheduledTaskAction -Execute 'C:\Users\<user>\.hermes\start-windows-browser.bat'
$trigger = New-ScheduledTaskTrigger -AtLogOn -User <user>
$settings = New-ScheduledTaskSettingsSet `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'Hermes_Browser' `
    -Action $action -Trigger $trigger -Settings $settings `
    -Description 'Start dedicated Windows Chrome on 9223 for the Hermes browser-use harness; restarts if it dies.' `
    -Force | Out-Null
```

Run it and verify from the WINDOWS side (WSL cannot reach Windows `127.0.0.1` loopback due to asymmetric WSL2 networking):

```powershell
powershell.exe -NoProfile -Command "try { \$r = Invoke-WebRequest -Uri 'http://127.0.0.1:9223/json/version' -TimeoutSec 4 -UseBasicParsing; Write-Output \$r.Content } catch { Write-Output 'DOWN: ' + \$_.Exception.Message }"
```

Must show a Windows build (`Chrome/151 ... Windows NT`), NOT HeadlessChrome.

## Pitfalls

- The gateway restarting is NOT the browser failing — it's the browser living inside the gateway's tree. Detach it.
- Don't conflate the two ports: WSL = 9222, Windows = 9223 (9223 avoids the WSL-held 9222 on the shared localhost).
- Do not touch Pi's box. The Windows browser on 9223 belongs to the windows hermes agent (see SKILL.md "Agent Topology").
