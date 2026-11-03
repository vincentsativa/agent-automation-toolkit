---
name: wsl-windows-default-apps
description: Changing the Windows default browser/apps from WSL.
trigger: "Vinny asks to change the default browser/app on Windows, or questions why a default-browser write fails, or any WSL-to-Windows default-apps task."
---

# WSL → Windows Default Apps

Configuring which app Windows opens by default (browser, http/https, etc.) from inside a WSL2 shell. Covers the mechanics, the UserChoice write block, the sanctioned UI path, and WSL interop pitfalls.

## Key facts (verified on Win11 25H2, build 26200)

- The current default for a scheme lives in the registry `UserChoice` key:
  `HKCU\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice`
  Values: `ProgId` (e.g. `MSEdgeHTM`, `ChromeHTML`, or a custom one) and a signed `Hash`.
- Read the current default:
  `reg.exe query "HKCU\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice" /v ProgId`
- Find an installed browser's registered ProgId by its App Paths entry:
  `reg.exe query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe" /ve`

## The write block (UCPD)

- Windows 11 25H2 (build 26200) runs `UCPD.sys` — a kernel filesystem-filter driver, group `FSFilter Activity Monitor`, service state RUNNING. Its documented job is to veto programmatic/silent writes to the default-app `UserChoice` keys, even for the owning user.
- A direct write returns: `reg.exe add ... UserChoice ... → ERROR: Access is denied.`
- **IMPORTANT — separate proven from assumed.** "The write is blocked" is proven by the `Access is denied.` output. "UCPD is the cause" is an assumption unless proven — the block could equally be hash validation (Windows rejects any `Hash` that does not match the ProgId) or the key's ACL. Run the diagnostic, report what it showed, and don't overclaim the mechanism.

## The working path (OS-sanctioned UI)

The reliable way to change the default is to open the OS settings page and let the user (or a click) apply it — this works WITH UCPD running because you use Windows' own UI rather than fighting the kernel filter. The Hermes WSL2 guide endorses `wslview` / `explorer.exe` for opening things with the Windows default handler.

```bash
explorer.exe "ms-settings:defaultapps"   # open Windows' default-apps settings page
```

This is the honest answer when someone asks "can it be done from WSL?": the settings UI can be launched from WSL and the change applied there; a silent scripted registry write is what the driver is built to block.

## Related: real-profile browsing needs a Chromium default

Hermes' real-profile browsing (`browser.use_real_profile: true`) **fails closed
unless the default browser is a supported Chromium**. On this box the default
is Comet, so the flag being set does NOT mean the feature runs — it never
snapshots `~/.hermes/browser-profile/`. Full diagnostics + the `detect_default_chromium()`
gate in `references/real-profile-browsing.md`.

## WSL interop pitfalls

- **UNC cwd breaks cmd.exe.** If the shell's cwd is under `\\wsl.localhost\...` (e.g. `cd /tmp` inside WSL), `cmd.exe` / `reg.exe` fail with `UNC paths are not supported. Defaulting to Windows directory.` Fix: `cd /mnt/c` (or any drive-letter path) before running Windows tools.
- `reg.exe`, `cmd.exe`, `explorer.exe`, `icacls` all work from WSL but inherit this cwd constraint and cmd.exe quoting rules — prefer `reg.exe` (not `regedit`) and quote Windows paths as `"...\\..."`.
