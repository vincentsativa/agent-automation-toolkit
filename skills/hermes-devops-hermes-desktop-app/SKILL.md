---
name: hermes-desktop-app
description: Build, package, and install the Hermes Electron desktop app on Windows/macOS/Linux. Covers the Vite + electron-builder pipeline, shortcut creation, and common failure modes.
---

# Hermes Desktop App — Build & Install

## When to Use
- User reports "desktop dashboard broken", "icon missing", or "desktop app won't launch"
- Fresh clone needs a working desktop build
- After pulling updates that touch `apps/desktop/`
- Packaging installers (NSIS, MSI, DMG, AppImage)
- User asks about a desktop-app feature (e.g. the HUD) and whether it works outside the desktop app

## Features: the HUD is a desktop-app surface, not a model

The HUD ("HUD mode") is a chrome-free, frameless, always-on-top floating chat window that sits over whatever app the user is working in, so Hermes can be driven without leaving that app. Key facts to answer questions about it:
- It is a **desktop-app-only** surface. It does not exist on the CLI, TUI, or any gateway platform (Telegram, Discord, etc.).
- It is **not a model** — it renders the real chat surface and uses whatever model the backend is configured with (e.g. deepseek-v4-flash via Ollama Cloud).
- It is not Windows-specific in code: the desktop app supports it on macOS and Linux too (windowing layer handles cocoa, win32, and Wayland/X11). On a given machine it only works when the desktop app is running there.
- Entering HUD mode hides the main window; leaving is a handoff that re-resumes the session the HUD was on.
- Source lives under `apps/desktop/electron/hud-*.ts` (overlay, windowing, geometry, ipc) and `apps/desktop/src/app/hud/`; the per-turn prompt note is `hud_surface_note()` in `agent/prompt_builder.py`.

## Prerequisites
- Node.js 20.19+ or 22.12+ (per `engines` in `package.json`)
- npm 10+ (corepack-managed)
- Python 3.11+ (for `node-pty` native build)
- Windows: Visual Studio Build Tools / Emscripten for native deps
- **Electron must exist in the repo root `node_modules/electron/dist`** — the desktop `package.json` references `../../node_modules/electron/dist`

## Build Commands (run from `apps/desktop/`)

```bash
# Development (hot-reload renderer + Electron)
npm run dev

# Production build only (renderer → dist/)
npm run build

# Build + package unpacked app (win-unpacked/, mac/, linux/)
npm run pack

# Build + create distributable installers
npm run dist          # all platforms
npm run dist:win      # Windows NSIS + MSI
npm run dist:win:nsis # NSIS only
npm run dist:win:msi  # MSI only
npm run dist:mac      # macOS DMG + ZIP
npm run dist:linux    # AppImage, deb, rpm
```

## Shortcut Creation (Windows)

Two PowerShell scripts exist in `HERMES_HOME` (typically `%LOCALAPPDATA%\hermes\`):

| Script | Target |
|--------|--------|
| `make-desktop-shortcut.ps1` | `%USERPROFILE%\OneDrive\Desktop\Hermes.lnk` |
| `make-shortcut.ps1` | `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Hermes.lnk` |

Both point to `HERMES_HOME\hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe` with working directory `HERMES_HOME`.

Run after a successful `npm run pack`:

```powershell
powershell -ExecutionPolicy Bypass -File "make-desktop-shortcut.ps1"
powershell -ExecutionPolicy Bypass -File "make-shortcut.ps1"
```

## Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `electronDist does not exist: .../node_modules/electron/dist` | Electron not installed in repo root | `cd <repo-root> && npm install electron@<version> --save-dev` (version from `apps/desktop/package.json`) |
| `node-pty` rebuild fails | Missing Python / VS Build Tools | Install Python 3.11 + "Desktop development with C++" workload |
| `assert-root-install.cjs` fails | Not running from repo root | Always run npm commands from `apps/desktop/` (scripts check `../../package.json`) |
| White flash on launch | Theme not pre-painted | `dist/index.html` already has inline script reading `localStorage` theme keys — ensure renderer writes them on theme change |
| Shortcut created but app won't start | Wrong target path | Verify `win-unpacked/Hermes.exe` exists; shortcuts are hardcoded to that path |

## Key Files

```
apps/desktop/
├── package.json              # Build config, electron-builder config, scripts
├── vite.config.ts            # Vite + React + Tailwind 4 config
├── electron/
│   ├── main.cjs              # Electron main process (240 KB — god file)
│   ├── preload.cjs           # Context bridge
│   └── session-windows.cjs   # Multi-window session management
├── src/                      # React renderer (TypeScript)
├── scripts/
│   ├── assert-root-install.cjs
│   ├── stage-native-deps.cjs   # Copies node-pty to build/native-deps
│   ├── write-build-stamp.cjs   # Git commit → build/install-stamp.json
│   ├── before-pack.cjs         # electron-builder hook
│   ├── after-pack.cjs          # Copies icon.ico to resources
│   └── set-exe-identity.cjs    # Stamps .exe with icon + metadata (rcedit)
├── assets/icon.ico             # App icon (used by electron-builder + rcedit)
└── dist/                       # Vite output (created by build)
```

## Verification

```bash
# 1. Unpacked app exists
ls -la apps/desktop/release/win-unpacked/Hermes.exe

# 2. Version flag works (times out after showing stamp — normal)
apps/desktop/release/win-unpacked/Hermes.exe --version

# 3. Shortcuts exist
ls -la "%USERPROFILE%\Desktop\Hermes.lnk"
ls -la "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Hermes.lnk"
```

## References
- `references/troubleshooting.md` — detailed error transcripts and fixes
- `references/electron-builder-config.md` — annotated `package.json` build section