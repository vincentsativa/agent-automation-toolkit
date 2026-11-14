---
name: disk-cleanup
description: Use when disk fills up or Vinny says to free space here.
---

# Disk cleanup

Reclaim space on this box only on Vinny's order, then prove the result with numbers. Two filesystems exist: `/` (root, 16G) and `/data` (20G, holds `/data/home`, `/data/workspace`). The dashboard's "MB free" warning tracks the `/data` volume, so start there: `df -h /data`.

## Procedure

1. **Measure before.** `df -h /data` and record free/used. Every claim at the end compares against this line.
2. **Find where it went.** `du -x -h --max-depth=1 /data/home` first, then descend into the two or three largest directories. Budget time: a bare `du` over `/data/home` can exceed a 60s terminal timeout, so run depth-limited `du` with `timeout=300` or higher, and never pipe a full-tree `du` into a slow sort.
3. **Classify before deleting.** Three buckets: (a) caches, safe to purge; (b) stale artifacts of an upgraded tool, safe once proven unreferenced; (c) live state, hands off. Name which bucket each candidate falls in and say so in the report.
4. **Purge caches with the tool's own command**, not `rm`: `pip cache purge` (reports files and MB freed), `npm cache clean --force` (the `--force` warning line is normal). Caches under `~/.cache`, `~/.npm`, `~/.hermes/cache` regenerate on demand.
5. **Prove staleness for anything versioned** (see the Playwright recipe in `references/browser-builds.md`: cross-check the revision each installed package declares before removing a build directory).
6. **Measure after and verify function.** `df -h /data` again, report the delta in GB and the new use%, then run one real smoke test of anything touched (e.g. launch a headless browser and load a page). Report what was removed, what was kept and why, and both df lines.

## Always-on rules

- Vinny's order is the authorization for the whole chain; do not stop after the diagnosis to ask which targets to clear.
- Never delete inside `~/.hermes/installs`, `~/.hermes/tools`, `~/.hermes/hermes-agent`, `~/.pi`, or a live service's state dir as "cleanup": installs and tools are the running system, not copies. Check for actual duplicates (same content, multiple dirs) before calling anything redundant.
- Report only numbers produced by the commands: files/MB freed per cache and the df before/after. Estimated savings are not results.

## Pitfalls

- The dashboard warning number equals free space on `/data`, not `/`; clearing root-side space will not move it.
- Deleting a browser or runtime build that some installed package still references does not fail loudly, it fails at the next launch of that tool. Ownership must be read from the packages' own manifests before any `rm`.
- A directory's mtime shows when it was written, not which version wants it: an older build can be newer on disk than the current one after a reinstall, so match revisions, not dates.
