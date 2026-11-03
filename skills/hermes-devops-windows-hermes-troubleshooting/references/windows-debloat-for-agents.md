# Windows Debloat for Agent Hosting

When running agent software (Hermes, OpenClaw, etc.) on Windows, Windows Defender and other built-in bloat actively interfere. Agent software spawns child processes, reads/writes files, hooks into system processes, and compiles code — all behaviors Defender treats as malicious.

## The Problem

| Windows Feature | Why It Breaks Agents |
|----------------|---------------------|
| Windows Defender Real-Time Protection | Flags agent binaries, compiled scripts, and spawned processes as threats. Quarantines or kills them mid-operation. |
| Windows Defender Antimalware Service (MsMpEng.exe) | Constant disk I/O scanning every file the agent touches. Slows everything to a crawl. |
| OneDrive integration | Syncs agent working directories, causes file locks and sync conflicts. |
| Windows Search Indexer | Indexes agent temp directories, holds file locks. |
| Background App Telemetry | Consumes CPU/bandwidth, competes with agent processes. |
| Windows Update | Reboots mid-cron-run. Downloads updates during critical operations. |
| Xbox Game Bar / Xbox Live | Unnecessary services consuming resources. |
| Copilot / Windows Copilot | Background AI processes competing for GPU/CPU. |

## The Solution: Automated Debloat Script

The user maintains a script (stored on a Raspberry Pi / backup server) that runs on any fresh Windows install to strip all of the above. The script:

1. **Disables Windows Defender permanently** — registry hacks + group policy + service disable. Not just "turn off real-time protection" (which re-enables on reboot), but a full kill.
2. **Removes bloatware** — uninstalls Xbox, OneDrive, Copilot, News, Weather, and other pre-installed garbage via PowerShell.
3. **Kills telemetry** — disables diagnostic data collection, feedback frequency, and connected user experiences.
4. **Disables Windows Update** (or sets to manual-only) — prevents surprise reboots.
5. **Strips unnecessary services** — Windows Search, Print Spooler (if no printer), Xbox services, etc.

## Why This Matters for Agent Hosting

Without this script, a Windows machine running Hermes or OpenClaw will:

- Have agent binaries quarantined mid-session
- Experience 2-3x slower file operations due to real-time scanning
- Randomly reboot for updates, killing long-running cron jobs
- Have degraded performance from background services competing for resources

With the script applied, the Windows machine runs lean enough to host agents effectively — though still not as fast as native Linux.

## Deployment

The script is pre-positioned on the user's Pi and can be copied to any Windows machine via:

```powershell
# From the Pi or any network-accessible storage
copy \\pi-share\tools\windows-debloat.ps1 C:\tools\
powershell -ExecutionPolicy Bypass -File C:\tools\windows-debloat.ps1
```

After running, reboot once. The machine is now agent-ready.

## Pitfalls

- **Defender re-enables after major Windows updates.** The script needs to be re-run after feature updates (not just cumulative patches).
- **Windows Security Center may show "no antivirus"** — this is expected. The user accepts the trade-off for agent performance.
- **Some enterprise-managed machines block the registry changes.** This script is for personal machines the user controls.
- **Do NOT run this on a machine that needs Defender** (shared family PC, client workstations, etc.). This is for dedicated agent hosts only.
