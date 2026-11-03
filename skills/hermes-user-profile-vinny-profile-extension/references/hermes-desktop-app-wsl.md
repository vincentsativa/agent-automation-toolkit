# Hermes Desktop App vs WSL Hermes

## The Core Fact

The **Hermes Desktop app** (native Windows/macOS installer from nousresearch.com) is a **self-contained local install**. It runs its own Hermes instance on the host OS. It is NOT a remote client or control panel for a Hermes agent running elsewhere (e.g., in WSL).

## What This Means for Vinny's Setup

Vinny runs Hermes in **WSL** (`~/`). The Hermes Desktop Windows app cannot connect to or control that WSL Hermes instance. They are separate installs with separate configs, sessions, skills, and memory.

## What DOES Work to Control WSL Hermes from Windows

| Method | How |
|--------|-----|
| **Web dashboard** | Run `hermes dashboard` in WSL, open `http://localhost:9119` in Windows browser |
| **Telegram gateway** | Run `hermes gateway run` in WSL, connect to Telegram, use Windows Telegram desktop app to message the agent |
| **Discord/Slack gateway** | Same pattern — gateway in WSL, native Windows chat app as client |
| **CLI via WSL terminal** | Open Windows Terminal → WSL tab → `hermes` |

## What the Hermes Desktop App Actually Is

- A native Windows/macOS Electron app that bundles its own Hermes install
- Includes a GUI for chat, session management, and config
- Installs to the host OS filesystem (e.g., `C:\Users\<user>\AppData\...` on Windows)
- Has its own `~/.hermes/` equivalent on the host
- Cannot be pointed at a remote Hermes instance (WSL, SSH, VPS, etc.)

## If Vinny Wants a Native Windows GUI for His WSL Hermes

Options in order of practicality:
1. **`hermes dashboard`** — web UI, works from any Windows browser, no extra install
2. **Telegram gateway** — best UX, works from Windows Telegram desktop app
3. **Install Hermes natively on Windows** — separate instance, not connected to WSL config/sessions

## Session Context (July 13, 2026)

Vinny asked 4 times whether he could "point" his WSL Hermes agent to the Windows desktop app. The answer is no — the Desktop app is not a remote client. The confusion came from the word "desktop" implying a control panel, when it's actually a standalone local install.
