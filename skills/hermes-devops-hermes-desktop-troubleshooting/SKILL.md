---
name: hermes-desktop-troubleshooting
description: Use to diagnose Hermes desktop app CPU spikes or won't-launch.
trigger: "Hermes desktop app has high CPU usage, won't launch, or crashes."
---

# Hermes Desktop Troubleshooting

Diagnose Hermes desktop app CPU spikes / won't-launch.

## Key Facts

- Desktop spawns its OWN backend (`hermes serve` on a random localhost port, look for `HERMES_BACKEND_READY port=N`) — does NOT reuse the gateway. Two backends on a failing cloud endpoint stack load.
- Logs:
  - `~/.hermes/logs/desktop.log` (model API calls, 401/500, retry loop).
  - `~/.hermes/logs/gui.log` (`event loop stalled Xs (GIL pressure suspected)`).
- Check log mtimes — can go stale.

## Cause A (check first): stale build stamp + corrupted node_modules

Rebuild loop. Fix: remove corrupted package dir(s), reinstall, `hermes desktop --build-only` once, verify `~/.hermes/desktop-build-stamp.json` shows `build_needed` false.

## Cause B: spawned backend hammering a failing model endpoint

Fix: point desktop at local Ollama, don't run desktop while gateway is up, verify API key.

## Config

- `config.yaml` is write-protected from direct edits — use `hermes config set model.default "..."` / `hermes config get`.
- `:cloud` model suffix is cosmetic — stripped by `_strip_ollama_cloud_suffix()`, doesn't change routing.
