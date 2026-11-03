---
name: hermes-install-patch-durability
description: Use when patching the Hermes install tree.
---

# Local Patches to the Hermes Install, and Getting Them Upstream

A local edit to `~/.hermes/hermes-agent` is a patch with a finite life. This skill is the
lifecycle: confirm the bug is upstream's to fix, decide whether to patch locally, keep the
patch through updates, land it upstream, and cover the window in between.

## When to Use

Load this skill when:

- You are about to edit a file inside the Hermes install tree (not config, not skills, not
  `~/.hermes/scripts`).
- The user asks whether a fix will survive the next `hermes update`.
- A recurring failure traces to Hermes scheduler, agent, or CLI code rather than to job config.
- You need to open a PR or an issue against the Hermes repo.

## Order of operations: search upstream BEFORE writing a line

The Hermes repo carries a large cluster of overlapping open PRs on popular bug classes. A
fresh PR on a crowded topic is noise, and it may duplicate work already merged into a branch
you have not fetched. Do these reads first, in this order:

```bash
cd ~/.hermes/hermes-agent
git fetch --quiet origin
git log --oneline HEAD..origin/main -- <area>/      # already fixed upstream?
git rev-list --count HEAD..origin/main              # how far behind your tree is
git grep -n '<symbol or line>' origin/main -- <path>  # is the fix in the remote tree
```

`git grep` against `origin/main` beats reading files one at a time: it answers "does the
remote already read this line" in one call. Always pass `-- <path>`; without a path limiter
the repo's auto-gc prints `Auto packing the repository...` between results and buries them.

Then search BOTH trackers, because a feature with open implementing PRs usually has a
spec issue that says so:

```bash
gh search issues --repo NousResearch/hermes-agent '<terms>'
gh search prs --repo NousResearch/hermes-agent --state open '<terms>'
```

Pitfall: `gh search prs --state all` is REJECTED (valid values are `open|closed`). Omit
`--state` entirely to search every state.

When you find a candidate PR, confirm it is the same change before treating it as the fix:

```bash
gh pr view <n> --repo NousResearch/hermes-agent \
  --json title,state,author,createdAt,mergeable,files,additions,deletions
gh pr diff <n> --repo NousResearch/hermes-agent | head -60
```

Check the `files` list for the exact function you are about to touch. A PR whose title matches
the symptom but whose diff touches a different module is not your fix. Read the diff and
confirm it changes the line your evidence points at.

**Finding an open PR for the same bug means your action is to support it, not to open a
ninth copy.** Say which PR is canonical, and if the issue thread asks a human to pick among
candidates, say that too.

## What `hermes update` actually does to a local edit

Do not repeat the folk claim that an update clobbers local edits. Read the behavior:

- The updater auto-stashes dirty tracked files and untracked files before checking out or
  pulling. The stash is named `hermes-update-autostash-<UTC YYYYMMDD-HHMMSS>`.
- Interactive terminal updates prompt before restoring that stash.
- **Non-interactive** updates (gateway, desktop, or `--yes`) follow
  `updates.non_interactive_local_changes` in config.yaml: `stash` restores local source
  edits after a successful pull; `discard` drops the stash. Check it before promising
  anything:
  ```bash
  grep -n -A4 '^updates:' ~/.hermes/config.yaml
  ```
- The restore is validated. Restored Python files are syntax-checked and critical modules
  are import-checked; on failure the stash is parked, not applied, with a printed notice.
- The stash is also parked when the update added a file where you had an untracked file of
  the same name, to avoid discarding your copy.

So a normal pull preserves the patch. The narrow real risk is a CONFLICT: if upstream edits
the same region, the restore parks the stash, the patch silently vanishes, and the bug
returns on the next scheduled run. That window, not the pull itself, is what needs cover.

## Prove the patch before reloading it

A gateway patch lives in two places: the file on disk, and the module the running process already imported. Only the disk copy is yours to change; the process copy stays stale until a reload. So verify the DISK copy by driving the real function in-process, which is possible without a restart.

The recipe (scratch dir, real module, real validator, a control that reproduces the pre-fix failure) is in `references/verify-a-live-patch.md`. Rules that matter every time:

- Call the patched function and assert its RETURN VALUE. Reading the edited line back proves only that the editor worked.
- Drive the same function the production path drives. If the fix sits in a method that needs `self`, bind the sibling helper as a `staticmethod` on a stub rather than reimplementing the logic in the test.
- Assert the control case too: the pre-fix input shape must still return the old failure. A check that has only ever been green is indistinguishable from a broken one.
- `python -m py_compile <file>` on every touched file before you claim anything, and confirm the diff is only your hunks with `git diff --stat -- <paths>`.

## Reload: the running gateway never picks the patch up by itself

Gateway core and plugin modules are imported once at process start. A patched adapter, envelope, or runner keeps its old behaviour until the process restarts, and the restart cannot come from inside: shell commands that restart, stop, or uninstall the gateway (including a `systemd-run` timer that wraps one) are refused by the runtime, because the gateway would SIGTERM its own child before it finished.

Do not try to launder the restart through a detached script, `nohup`, or an indirect wrapper. That is fighting the guard, and the guard is right.

Finish everything else, then hand over the reload in one line:

- In a chat session, the user sends `/restart` (the gateway re-execs itself gracefully and reloads every module).
- In a shell outside the gateway: `hermes gateway restart`.

Say plainly that the code is fixed and verified on disk but the live process is still old until that one command runs, then ask for the message to be retried.

## Verify the patch is still present

```bash
cd ~/.hermes/hermes-agent
git status --porcelain -- <path>        # ' M <path>' means the edit is still on disk
git stash list | grep hermes-update-autostash   # a parked stash means it is NOT applied
grep -n '<the line you added>' <path>
```

A parked autostash older than a few days is a forgotten fix. `git stash list` is the first
place to look when a patched bug reappears after an update, before re-diagnosing anything.

## Landing the fix upstream

1. Confirm the working tree change is a clean, isolated diff of exactly the fix:
   ```bash
   git diff -- <path>
   ```
   If unrelated local edits exist in the same file, the PR carries them too. Separate them
   first, or the review is about your tree and not your fix.
2. A PR needs a branch on a FORK. Push there, never to the upstream repo (you will have
   `pull` permission and not `push`):
   ```bash
   gh api repos/<owner>/<repo> --jq '.permissions'   # expect push:false
   ```
3. **Fork creation is a known credential wall.** A fine-grained personal access token
   CANNOT create a fork of a repo you do not own: GitHub requires `administration=write` on
   the PARENT repo, which cannot be granted for someone else's repository. The refusal is
   specific and diagnosable:
   ```bash
   gh api -i -X POST repos/<owner>/<repo>/forks 2>&1 | grep -i 'HTTP/\|x-accepted-github-permissions\|message'
   # HTTP 403, X-Accepted-Github-Permissions: administration=write,
   # {"message":"Resource not accessible by personal access token"}
   ```
   A classic token with the `public_repo` scope works. A fine-grained token fundamentally
   cannot, so do not keep reshaping the request.
4. When that wall is hit, STOP and name it in one line: what is blocked, what was proven,
   and that it needs the user's identity. Do not spend the turn retrying token variants.
5. The fallback that needs no fork: hand the user a ready-to-paste PR comment or issue body
   containing the repro, the evidence, the confirming read of the existing diff, and the URL.
   Reproduce the failing state, quote the exact assertion, and note the sibling PR cluster so
   a maintainer can pick the canonical one.

## Cover the gap until it lands

A nightly `no_agent` cron probe is the right shape: zero tokens, silent when healthy, alerts
only on regression. On this box it is `~/.hermes/scripts/update_health_check.py`, job
"Hermes Update Health Check". Add a check that DRIVES the real function and asserts the
returned value, so a dropped patch is caught the same night instead of at the next failure.

Rules for that probe, all of which have been violated by a rushed version:

- **Probe the resolved VALUE, not the source text.** A regex over the patched line breaks on
  any reword or reformat and is blind to a fix that landed but does not run. Call the real
  function and assert what it returned.
- **The module import is the integrity signal; the value assertion is the regression check.**
  A dropped patch cannot import-crash, so a passing import proves nothing on its own.
- **Assert the inherit path beside the override path.** A probe that only checks "per-job
  value wins" passes on a fix that raises every job to that value. Both cases, every run.
- **Prove the probe can fail.** Revert the patch, confirm the right message fires, restore it.
  A checker that has only ever been green is indistinguishable from a broken one.
- **Never add an advisory check that fires on a healthy night.** "These jobs look unbudgeted"
  is a finding for the user, not a nightly alert. A check that speaks every night destroys the
  silent-success contract and gets ignored, which is worse than not having it.
- **Prove it through the real job, not an ad-hoc run.** `hermes cron run <job_id>`, then read
  the newest `~/.hermes/cron/output/<job_id>/*.md` and confirm `Status: silent (empty output)`.

For the interpreter, the stdlib-only trap, and the dependency bootstrap a cron script needs,
see the `no_agent` sections of the `hermes-cron-troubleshooting` skill. For the specific
per-job cron turn-budget probe, that skill ships
`scripts/probe_cron_job_turn_budget.py`; do not write a second one.

## Pitfalls

- **Do not state that an update clobbers local edits without reading the updater.** The
  autostash-and-restore path is the norm; the conflict-park is the exception. Getting this
  backwards sends a user to re-apply a patch that was never lost.
- **Do not open a PR for a bug that already has an open implementing PR.** Search both
  trackers first. The correct contribution on a crowded bug is support and disambiguation,
  not another branch.
- **Do not report "fixed" for a local patch.** A patch on one machine is not a fix. Say
  plainly which copy the user is running and where upstream stands.
- **Do not call a gateway patch live before the process has reloaded.** The reply that says
  "fixed" while the running process still holds the old module is a false report, even though
  the file is correct. Name the reload as outstanding, in one line, with the command.
- **Never route the reload through a background or delayed command to dodge the self-restart
  guard.** The guard exists because the gateway kills the child that would restart it. The
  supported paths are `/restart` from the chat and `hermes gateway restart` from a shell
  outside the process.
- **A config-only workaround is not the fix.** Raising a global setting to route around an
  unread per-job field changes behavior for every caller of that setting, and leaves the
  defect in place. Name it as a stopgap with its blast radius, never as the repair.
- **Keep the local patch as a clean diff.** An isolated `git diff -- <path>` is what can be
  re-applied by hand, turned into a PR, or moved to a new machine. Mixed in with unrelated
  edits it is none of those.
