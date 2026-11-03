# Ollama "Warning: client version is X" — What It Actually Means

## Source
GitHub issue #6369, PR #16716 (xy200303, June 2026)

## The Output
```
ollama version is 0.24.0
Warning: client version is 0.31.1
```

## What It Means
The CLI binary (`ollama.exe`) and the running server process are different versions. The server is still running the old binary. The warning is informational — it does NOT mean the server is "outdated" or broken. It means the versions are mismatched.

## The Fix
Restart the Windows Ollama service so it picks up the newer binary:
- Task Manager → Services → `Ollama` → Restart
- Or: `net stop ollama && net start ollama` (admin cmd)
- Or: Restart the Ollama tray app

## Why This Happens
Ollama's Windows installer updates the CLI binary but does NOT restart the running service. The service continues running the old binary until manually restarted. This is by design — the installer avoids disrupting running model loads.

## Related PR #16716 (Open, June 2026)
A PR titled "cmd: keep version output local when server is unavailable" aims to suppress the misleading warning when the server genuinely cannot be reached. It keeps the mismatch warning when the server IS reachable and versions differ — which is the correct behavior for the case above.
