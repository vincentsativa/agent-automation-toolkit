---
name: windows-hermes-browser-fix
description: Fix Windows Hermes browser via cdp_url 9223.
---

# Windows Hermes Agent Browser Fix

Fix the Windows Hermes agent's browser when it fails with `chrome-not-running: no supported browser is running and none could be launched`. This is the same root cause as the WSL-side fix but with a critical port difference.

## CRITICAL BOUNDARY RULE

**The Windows Hermes agent is Pi. I am NEVER allowed to touch Pi's box, config, processes, or files. Vinny will NEVER authorize this, it is an absolute, permanent boundary.** This skill exists only to document the fix so Vinny or Pi can apply it themselves. I do not apply it to Pi's machine, ever, under any circumstances. If the Windows agent's browser breaks, I hand the fix to Vinny or Pi to apply, I do not reach in.

## WSL-SIDE BROWSER FIX (port 9222)

This is MY OWN browser (Frank, WSL/Linux, `cdp_url: http://127.0.0.1:9222`). Two failure modes, both fixed at launch time:

### Crash 1: GPU process dies (`GPU process isn't usable. Goodbye` + SIGABRT)
WSL's GPU env is broken for Chromium. Launch with `--disable-gpu --disable-software-rasterizer --no-sandbox`.

### Crash 2: `Missing X server or $DISPLAY`
There is no real display in WSL. Wrap launch in `xvfb-run`:
```bash
xvfb-run -a --server-args="-screen 0 1920x1080x24" \
  ~/.cache/ms-playwright/chromium-1217/chrome-linux64/chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=~/chrome-debug \
  --no-first-run --no-default-browser-check \
  --disable-gpu --disable-software-rasterizer --no-sandbox about:blank
```
Clear a stale `SingletonLock` in the profile dir first if it won't bind. Run as a background daemon (it never exits). Verify with `curl http://127.0.0.1:9222/json/version`.


## Root Cause

The browser-use harness daemon only auto-detects Chrome in standard profile dirs. A Chrome on a non-default profile is running but invisible to the daemon, so it refuses to connect. The fix is the documented `browser.cdp_url` override pointing at a dedicated automation Chrome.

## Port Conflict (CRITICAL)

WSL2 shares localhost with Windows. The WSL-side Hermes holds port 9222. So the Windows Chrome MUST use a different port: **9223**.

- Windows cannot reach the WSL-side 9222.
- WSL cannot reach the Windows-side Chrome the way the harness needs.
- Verify the Windows Chrome is the Windows build (Chrome/151, Windows NT), NOT HeadlessChrome (that's the WSL one).

## The Fix (already applied 2026-08-12)

### 1. Config

Set in `/mnt/c/Users/<user>/AppData/Local/hermes/config.yaml`:

```yaml
browser:
  cdp_url: http://127.0.0.1:9223
```

### 2. Launcher script

`/mnt/c/Users/<user>/.hermes/start-windows-browser.bat`:

```bat
@echo off
set PORT=9223
set CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe"
set PROFILE=C:\Users\<user>\.hermes\chrome-debug-9223
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:%PORT%/json/version' -TimeoutSec 2 -UseBasicParsing) | Out-Null; exit 0 } catch { exit 1 }"
if %errorlevel%==0 (
    echo browser already running on :%PORT%
    exit /b 0
)
start "" %CHROME% --remote-debugging-port=%PORT% --user-data-dir="%PROFILE%" --no-first-run --no-default-browser-check about:blank
echo browser started on :%PORT%
```

### 3. Auto-start

Copied to the Windows Startup folder so it runs on login:
`C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\start-hermes-browser.bat`

## Verification

### Check the Windows Chrome is up (from WSL)

```bash
powershell.exe -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:9223/json/version' -TimeoutSec 2 -UseBasicParsing).Content } catch { 'down' }"
```

Must show `Chrome/151` (Windows build). If it shows HeadlessChrome, that's the WSL browser on the wrong port.

### Test the harness (from WSL)

PowerShell has no heredocs, write the Python to a file and pipe it:

```bash
# write test.py containing: print(page_info())
powershell.exe -NoProfile -Command "cd 'C:\Users\<user>\AppData\Local\hermes'; \$env:HERMES_HOME='C:\Users\<user>\AppData\Local\hermes'; \$env:BU_CDP_URL='http://127.0.0.1:9223'; Get-Content '.\test.py' | & '.\bin\uvx.exe' browser-use"
```

A dict with `url`/`title` means it works. Then test real navigation with `new_tab("https://example.com")`.

## Pitfalls

- **Port 9222 is taken by WSL.** Never point the Windows config at 9222, it will hit the WSL Chromium or fail to bind.
- **Chrome merges into existing session** if the profile dir is already in use. Use a dedicated profile dir (`chrome-debug-9223`) and a fresh one if it won't bind.
- **PowerShell has no heredocs.** Always write the test Python to a file and pipe it with `Get-Content ... | uvx browser-use`.
- **`--doctor` shows `daemon alive` FAIL** even when Chrome is running, the daemon auto-starts on first real exec, so run an actual browser-use call to force it, not just `--doctor`.
- **Clean up temp test files** after verifying (`rm -f .../tmp_bu_test.py`).
- **Do NOT touch Pi, ever.** Vinny will never authorize it. Hand the fix to Vinny or Pi to apply; never reach into Pi's machine.
