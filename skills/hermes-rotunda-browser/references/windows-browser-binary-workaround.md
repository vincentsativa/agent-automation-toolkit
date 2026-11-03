# Rotunda Browser Binary on Windows

## Problem

Rotunda's GitHub releases only ship browser binaries for Linux (x86_64 + arm64) and macOS (arm64). There is no Windows build. The v0.5.1 release assets are exactly `rotunda-154.0.1-0.5.1-lin.arm64.zip`, `rotunda-154.0.1-0.5.1-lin.x86_64.zip`, and `rotunda-154.0.1-0.5.1-mac.arm64.zip`. The `rotunda fetch` command on Windows syncs 0 versions and cannot download a browser binary. The Python library installs and imports fine, but the browser binary is unavailable.

## Symptoms

- `rotunda fetch` outputs: "No versions found for channel 'official/stable'"
- `rotunda list` shows: "No versions installed"
- `rotunda version` shows: "Current browser: Not installed"
- `NewBrowser(playwright, ...)` raises `rotunda.exceptions.MissingRelease: No matching release found for Rotunda 0.5.1 on win x86_64. Please update the Python library.`

## The Copied-WSL-ELF Workaround DOES NOT WORK

**Disproven by direct test on 2026-09-25.** An earlier version of this file claimed you could copy the Linux binary from the WSL cache to the Windows cache path and launch it through Playwright on Windows. That is false. The copy succeeds and the file is present, but Playwright cannot spawn it:

```
Error BrowserType.launch: Failed to launch: Error: spawn C:\Users\<user>\.cache\rotunda\browsers\official\0.5.1-154.0.1\rotunda ENOENT
```

The binary is a Linux ELF (`ELF 64-bit LSB pie executable, x86-64, ... interpreter /lib64/ld-linux-x86-64.so.2`). Windows has no ELF loader, and WSL's `binfmt_misc` interop does not extend to Playwright's process-spawn path, so the file is reported as not found. Copying it wastes time and leaves a cache directory that looks correct while launching nothing.

Do not present this workaround, and do not report a Windows Rotunda launch as working.

## Actual Workaround: Stock Playwright Firefox

Windows has no working Rotunda browser. Use stock Playwright Firefox, the same engine family without the Rotunda patches:

```powershell
python -m playwright install firefox
```

```python
from playwright.sync_api import sync_playwright with sync_playwright() as p:
    browser = p.firefox.launch(headless=True)
    context = browser.new_context(no_viewport=True)
    page = context.new_page()
    page.goto('https://example.com')
    print('Stock Firefox OK:', page.title())
    browser.close()
```

Verified 2026-09-25 on the Windows agent: `Stock Firefox OK: Example Domain`. Playwright Chromium and Patchright Chromium also load pages there. Resolve the Windows interpreter from `installs/<key>/facts.json` (`packages.venv.environment` + `\Scripts\python.exe`); the old `hermes-agent\venv` path does not exist.

`no_viewport=True` is harmless with stock Firefox but is only strictly required for the Rotunda binary (Juggler protocol quirk). See pitfall #9 in the main skill.

## Cleanup

A dead Linux cache copied to Windows in a previous attempt can be deleted safely:

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.cache\rotunda\browsers\official"
```

That directory can never provide a working browser on Windows.
