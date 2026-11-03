---
name: hermes-cron-troubleshooting
description: Diagnosis and repair of Hermes cron scheduler issues — duplicate runs, missed runs, gateway restart ordering, and the advance-vs-dispatch race. Load this skill when a cron job fires twice in one day, misses a scheduled run, or when you need to restart the gateway and want to ensure cron jobs are handled correctly.
version: 1.0.0
category: devops
---

# Hermes Cron Troubleshooting

## Triggering

Load this skill when:
- A cron job fires twice on the same day (duplicate run)
- A cron job misses its scheduled time and next_run_at is already in the future with no output
- You need to restart the gateway and want to check whether cron jobs are due
- A job's `last_status` is `error` with "Interrupted by shutdown before terminal completion" — confirm from the logs whether a shutdown actually happened before believing the label (Failure Mode #7)
- A job produces no output but last_status shows "ok" (silent vaporization)
- A cron job delivers its Telegram confirmation but the user reports the primary deliverable (email, file, API call) was never received — the model may have hit max_iterations without completing the work (see Failure Mode #0). If the job instead shows `last_status: ok` and the run died mid-pipeline, see Failure Mode #9 for the capped-run-reported-as-success signature.
- A job reports a later stage never happened (no email, no file at the destination) while every status field reads clean and the dashboard shows a successful run (Failure Mode #9)
- A job's `max_turns` in `jobs.json` is HIGHER than the ceiling its run actually died at (`max_iterations_reached(N/N)` with a smaller N), or a heavy job keeps dying exactly at the global `agent.max_turns`. The job record advertising a budget the resolver never reads is Failure Mode #9; confirm it before editing any prompt
- The user reports a notification that never arrived ("I was supposed to get two and got none") while the job's completion text exists in its output file — check the job's `deliver` field and the runs' `delivery_outcome` first; see the `cron-delivery-telegram` skill for the queries and the `suppressed` signature.
- Debugging the cron scheduler's thread pool behavior

## Reference: Editorial Brief with Themes (Cron Pipeline)

For the full pipeline of a cron-mode editorial brief with theme discovery (30-story report with 5 unwritten article themes, email delivery, cleanup), see `references/editorial-brief-with-themes-cron.md`.

For a run whose report arrived but whose ledger says failed — querying `executions.db` and `deliveries.db`, reading the error label as a code path, and separating local-fence from file-fence contention — see `references/cron-run-ledger-forensics.md`.

For declarative `pre_tool_call` / lifecycle shell hooks — the config block, the allowlist gate (an unapproved hook SILENTLY never fires), mtime drift invalidating consent, and the `tool_input` vs `args` wire-format trap — see `references/shell-hooks.md`. Reach for this whenever a fix must be deterministic rather than dependent on the model cooperating.

A packaged probe for the per-job turn budget lives at `scripts/probe_cron_job_turn_budget.py`: it drives the real `_resolve_cron_agent_setup` and asserts a job's own `max_turns` wins while an absent one still inherits the global. Run it under the install venv after any edit to that function.

## Gateway Restart Protocol (CRITICAL)

**NEVER restart the gateway without checking cron status first.**

Gateway restart vaporizes any cron job that is between `advance_next_run` (next_run_at bumped forward) and actual pool dispatch. If a job's next_run_at was advanced before the restart, the job is lost — no output, no error, no retry.

BEFORE `hermes gateway restart`:
```bash
# 1. Check if any jobs are due now or in the next 5 minutes
python3 -c "
import json
from datetime import datetime, timezone, timedelta
j = json.load(open('~/cron/jobs.json'))
now = datetime.now(timezone.utc).astimezone()
deadline = now + timedelta(minutes=5)
for job in j['jobs']:
    if not job.get('enabled', True) and job.get('state') != 'paused':
        continue
    nxt = job.get('next_run_at')
    if nxt:
        nxt_dt = datetime.fromisoformat(nxt)
        if now <= nxt_dt <= deadline:
            print(f'DUE SOON: {job[\"name\"]} at {nxt}')
    if job.get('running_at'):
        print(f'RUNNING NOW: {job[\"name\"]} since {job[\"running_at\"]}')
\"

# 2. If any jobs are due or running, WAIT or run them manually first
```

**If you already restarted and a job was lost:**
Set next_run_at back to now to trigger immediate re-fire:
```python
from cron.jobs import load_jobs, save_jobs
from hermes_time import now as hermes_now
jobs = load_jobs()
for j in jobs:
    if j['id'] == '<job_id>':
        j['next_run_at'] = hermes_now().isoformat()
save_jobs(jobs)
```

### Gateway Cannot Restart Itself

**Critical behavior:** The gateway blocks all `hermes gateway restart`, `systemctl --user restart hermes-gateway`, and `kill <PID>` commands issued from inside the gateway process. The SIGTERM would propagate to child processes and kill the command before it completes. This also blocks cron jobs that try to restart the gateway.

**Before restarting for an update, check whether upstream already fixed the bug.** A cron failure caused by a scheduler bug is usually already patched on `origin/main` and waiting in the commits your install does not have yet:
```bash
cd ~/.hermes/hermes-agent
git fetch --quiet origin
git log --oneline HEAD..origin/main -- cron/          # is there a fix for this symptom?
git rev-list --count HEAD..origin/main                # how far behind
git log -1 --format='%h %ci %s'                        # what the install is actually running
```
Read the candidate commit's diff before trusting it (`git show <sha> -- cron/`) and confirm it changes the line your evidence points at. If the fix is there, `hermes update` is the repair and it restarts the gateway, so run the due-job check above first and tell the user the window is clean before acting.

**Workarounds when you need to restart from inside a gateway session:**
1. **Force-kill the PID directly** — `kill -9 <MainPID>` (systemd auto-restarts with a new PID)
2. **Use a separate terminal** — open another shell and run `hermes gateway restart` from there
3. **Schedule via `at` or a delayed script** — but cron jobs are also blocked by the same safety check

**Verification after restart:**
```bash
systemctl --user show hermes-gateway --property=MainPID,ActiveState
# New PID = restart succeeded
```

### A fix gated behind a restart is NOT proven until the restart happens

Config-driven behavior (declarative hooks, plugins, platform settings) loads **at
startup only**. Editing the config or the hook script does nothing to the
already-running process, so every test run from inside that process still shows the OLD
behavior — easy to mistake for a failed fix.

State that the restart is pending and the fix is unproven until then; do NOT report
"fixed" on a passing offline test. The proof is **re-running the exact operation that
was failing** through the live process: reproduce the failure first, restart, then
repeat the identical call and show it now succeeds. A synthetic harness that passes on
a freshly started process proves the script loads, not that the real path is repaired.

## Diagnosis Protocol (CRITICAL — read before acting)

**NEVER assume a job missed based on `last_run_at` alone.** This is the #1 source of wrong conclusions and duplicate runs.

The agent's work (email send, file write, API call) can complete fully while the metadata save (`mark_job_run`) gets wiped by a gateway restart. A stale `last_run_at` with a future `next_run_at` does NOT mean the job didn't fire — it means the metadata didn't survive.

**Always follow this order:**

1. **Check agent.log FIRST when asked "is job X running?"** — `grep "<job_id>" ~/.hermes/logs/agent.log | tail -20`
   - This is the fastest way to see if a job fired, what it's doing, and whether it's still in progress.
   - Look for the cron session prefix like `[cron_<job_id>_<timestamp>]` — that confirms the job started.
   - Look for `delivered to telegram` or `delivery error` to confirm completion.
   - Do NOT check systemd, process lists, or jobs.json metadata first — those tell you nothing about whether the agent actually ran.
   - **Session proof (June 17, 2026):** User asked "is the 4pm cron running?" I checked systemd, ps aux, jobs.json — all showed nothing useful. The agent.log showed the job fired at 16:00:43 and was still processing at 16:13. The user had to say "check the fucking logs" because I was checking everything else first.

2. **Check output artifacts** — `ls -la ~/.hermes/cron/output/<job_id>/`
   - If there's an output file from today, the agent ran. Read it to confirm what was delivered.
   - If there's NO output file, the job genuinely didn't execute.

3. **Check external evidence** — email receipts, file system artifacts, API call logs. The job's prompt may tell it to write files, send emails, or hit endpoints. Verify those independently.

4. **Check gateway logs** — `grep <job_id> ~/.hermes/logs/gateway.log | tail -20`

5. **Only then check metadata** — `last_run_at`, `next_run_at`, `running_at` in the cron list.

**If metadata is stale but output artifacts exist:**
- Do NOT re-fire the job — it already ran. Re-firing creates a duplicate.
- The metadata will self-correct on the next successful tick (the original tick's `mark_job_run` may still complete on recovery).
- If you need to fix the metadata for monitoring purposes, manually set `last_run_at` in `jobs.json` to the output file's timestamp.

**If metadata is stale AND no output artifacts exist:**
- The job genuinely missed. Follow the recovery steps below.

### Read the job's PROMPT before describing what the job does

`hermes cron show` does not exist (`hermes cron --help` lists list, create, edit, run, remove, status, runs, incidents, notepad, doctor, tick). `hermes cron list` gives schedule, script and delivery; the prompt is only in the job record:

```bash
python3 -c "
import json
d = json.load(open('~/cron/jobs.json'))
j = [x for x in d['jobs'] if x['id'] == '<job_id>'][0]
print(j['prompt'])
"
```

Answer a "does this job do X" question from that text, never from the skill that governs the task, the job's name, or the script it runs. The governing skill states policy; the prompt is what actually executes, and the two drift. Then treat every identifier inside the prompt (paths, recipients, board names, model ids) as a claim to verify against the live system before repeating it.

### Judging the CORRECTNESS of a run, not just whether it ran

`~/.hermes/cron/output/<job_id>/<timestamp>.md` holds the run's injected prompt plus its
`## Response` section. That response is the run's own account of what it did and what it
read, and it is the fastest route to the cause when a deliverable came out WRONG: it names
the sources consulted, the counts and "latest" values it saw, and the files it claims to
have written. Read it before theorizing about the job's logic or re-firing anything.

It carries NO tool trace. Every number, count, or path in it is a claim to re-verify
against the live source, never a fact to quote. A run whose research step read a stale copy
typically confesses it in its own response (an old note count, an old "latest item"), and
that one line is the entire diagnosis.

Status fields are silent about correctness: `last_status: ok` says the process finished, and
a run can complete cleanly while acting on stale input. Diagnose a bad result from the
response text and the live source, never from the ledger.

**Pitfall — the duplicate run trap:** If you see stale metadata and re-fire without checking output files, you create a duplicate run. The user gets two emails, two files, two messages. This is worse than a missed run. Verify artifacts first, every time.

**Pitfall — do not read an error label as evidence.** Scheduler error strings are written by the code path that gave up, not by the thing that failed. "Interrupted by shutdown before terminal completion" is the generic label for a lost fire claim (`_OWNERSHIP_LOST_INTERRUPTED` in `cron/scheduler.py`) and is written with no shutdown involved. Before telling the user a restart caused the failure, confirm a restart actually occurred: compare `systemctl --user status hermes-gateway` uptime against the failure timestamp, and grep the exit/receipt logs for that date. A report that still arrived, plus a long-running gateway, means the label is wrong and the real cause is elsewhere.

## Telegram Notification Modes for Cron Delivery

**Symptom:** Cron job fires and delivers to Telegram, but the message arrives silently — no push notification on the phone. The user sees it only when they open Telegram.

**Root cause:** The Telegram adapter has two notification modes:

- `"important"` (default) — only final responses, approvals, and slash confirmations trigger push notifications. Everything else (including cron deliveries) is sent with `disable_notification=True`.
- `"all"` — every message triggers a push notification.

The adapter reads the mode from `display.platforms.telegram.notifications` in config.yaml, **not** from the top-level `telegram.notification` key. These are two different settings.

**Detection:**
```bash
# Check what the adapter is actually using
grep -A2 "notifications" ~/.hermes/config.yaml | head -10
# Look for display.platforms.telegram.notifications — if missing, mode is "important"
```

**Fix — Option A (config):**
```bash
hermes config set display.platforms.telegram.notifications all
hermes gateway restart
```

**Fix — Option B (env var override):**
Add to `~/.hermes/.env`:
```
HERMES_TELEGRAM_NOTIFICATIONS=all
```
Then restart the gateway. The env var takes priority over config.yaml.

**Verification:**
After applying, send a test cron delivery or any non-interactive message. It should arrive with a push notification on Telegram.

**Pitfall — two different config keys:** The top-level `telegram.notification: all` (line ~598 in config.yaml) controls a different behavior — it's the platform-level notification setting for the gateway, not the adapter's push notification mode. The adapter reads from `display.platforms.telegram.notifications`. Setting the wrong key has no effect on push notifications.

## Per-Job Model and Reasoning Configuration

**Symptom:** You want one cron job to use a specific model (e.g. GLM 5.2) with a specific thinking/reasoning level (e.g. medium), without changing the global defaults.

**Model and provider: pass them at creation with `hermes cron create`, not with the `cronjob` tool.** Read the tool schema before assuming it can carry a model. The `cronjob_manage` schema has `pinned` (a boolean that locks the CURRENT main model) but **no `model` or `provider` parameter at all**. A remembered `model={...}` argument on that tool is a claim with nothing behind it, and it fails silently into an unpinned job.

Create with the model pinned in one command:

```bash
hermes cron create "<schedule>" \
  --name "<NAME>" \
  --script <helper>.py --no-agent \
  --deliver telegram \
  --model <model> --provider <provider> --pin
```

- `--model` plus `--provider` names them explicitly; `--pin` locks them so a later `hermes model` or `/model` change never touches the job. Use `--pin` alone to lock whatever the main model is at that moment.
- `--no-agent --script <name>` makes the job a zero-token script job (see the `no_agent` section below).
- Confirm it landed by reading the job record back, not by the create command's exit code. `hermes cron list` shows Name, Schedule, Deliver, Script and Mode; for the model and provider, grep the record:

```bash
hermes cron list | grep -A10 "<job name>"
python3 -c "
import json
d=json.load(open('~/cron/jobs.json'))
j=[x for x in d['jobs'] if x['name'].startswith('<job name>')][0]
print(j['id'], j['model'], j['provider'], j['deliver'], j['script'], j['no_agent'], j['schedule']['run_at'])
"
```

`jobs.json` is `{"jobs": [ ... ], "updated_at": ...}` and each entry keys its id as `id`, not `job_id`. A one-shot job created by ISO timestamp stores it at `schedule.run_at`, and `repeat.times` is 1 with `repeat.completed` 0.

**Model change on an existing job: also the CLI.** The `cronjob` tool's `action="update"` has no model parameter either. To change a job's model after creation:

```bash
hermes cron edit <job_id> --model <new_model> --provider <provider>
```

Example: `hermes cron edit 50dcd9876b7b --model glm-5.2 --provider ollama-com`

### Bulk retag: "make every pinned job use model X"

**What `pinned` means.** In cron it is NOT a bookmark. It means the job carries its own
`model`/`provider`, and the list API derives it as `bool(job.get("model"))`
(`tools/cronjob_job_args.py`). Pinned SESSIONS are a different concept living in
`state.db`. When the user says "pinned" in a cron request, scope by the job's model field;
when the word could mean either, ask once rather than sweeping the wrong set.

**Enumerate into buckets before writing.** List every job with `include_disabled=True` and
split them: match / skip-list (the user's explicitly protected models) / paused-disabled /
no-model script jobs. A paused job that carries an old model still satisfies
`bool(model)`, so it appears in a model-derived "pinned" filter even though it can never
run. Rewrite only enabled jobs and REPORT the paused ones with their state; folding one
into the sweep is a change the user did not ask for and has to be undone.

**Bulk edits go through the store API, not the file.** One job can go through
`hermes cron edit`; twenty should not, and hand-editing `jobs.json` at that size is the
corruption risk the fallback above warns about. Use the install venv and the store's own
update path, which takes the lock and re-derives the record:

```bash
~/.hermes/hermes-agent/venv/bin/python <skill_dir>/scripts/retag_cron_models.py \
  --match deepseek --target <model> --provider <provider> --skip glm          # dry run
# add --apply to commit; it backs jobs.json up and verifies every write by reading back
```

Equivalent inline: `sys.path.insert(0, '~/.hermes/hermes-agent')`, then
`from cron.jobs import list_jobs, update_job` and `update_job(job_id, {"model": ..., "provider": ...})`.

**Prove the model string exists before the sweep, with a live completion.** Send a
one-token chat completion to the provider with the exact target id. A provider's
`/v1/models` list omits tag variants: a suffixed tag (a `-cloud` build, a dated build) can
be absent from the list and still complete fine. So list membership is neither proof nor
disqualification, and gating the sweep on it blocks a valid change. Never mass-write a
model id you have not completed against.

**Reconcile after the write.** Read back through `cronjob_manage action=list` (the live
store) and assert `retagged + left-alone + paused + no-model script jobs = total`. Report
the counts, the two protected jobs by name, and any paused job still on the old model, in
one short block. "All done" without the enumeration is the drip.

**Prompt change on an existing job: the CLI, same reason.** The `cronjob` tool's `action="update"` carries NO prompt field. Its `prompt` parameter is create-only plus a transient override for `action="run"`, so a permanent prompt edit has no path through that tool no matter how the payload is shaped. Use the CLI:

```bash
hermes cron edit <job_id> --prompt "$(cat /path/to/new_prompt.txt)"
```

Pass the prompt from a FILE with `"$(cat ...)"`, never as a quoted literal typed inline. Cron prompts run to ten thousand characters, and a shell literal that long is where truncated arguments and quoting bugs come from. Read the job back afterward (`hermes cron list`, or parse `jobs.json` for that id) and confirm the new text is present and the skills, schedule and model are untouched.

**Editing `jobs.json` by hand is the fallback, and it needs a blast-radius proof.** Some fields have no CLI flag at all, so the file is the only route. When you take it: back the file up first (`cp ~/.hermes/cron/jobs.json ~/.hermes/cron/jobs.json.bak.<date>_<reason>`), preserve the top-level shape exactly (`{"jobs": [ ... ], "updated_at": ...}` — dropping `updated_at` or re-ordering the list is a corruption the scheduler may not complain about), and after writing, diff backup against new job by job and assert that EXACTLY the one intended job id differs. A scheduler file edit that silently touches a second job is a much worse outcome than the edit you were making. Then re-read the job to confirm the change landed, because a write that returns success is not a write the scheduler loaded.

**Session proof (August 15, 2026):** Attempted to change a looping job's model via `cronjob(action="update")` alongside the prompt change. The prompt updated successfully but the model stayed as `deepseek-v4-flash:0731`. Had to use `hermes cron edit --model glm-5.2 --provider ollama-com` to actually change it.

**Fallback when the `cronjob` bridge tool will not accept a create call:** go straight to the CLI above. It takes the same arguments, creates the job, and prints the job id, schedule, script, mode and next run. Do not keep retrying the bridge with a reshaped payload; the CLI is the supported path for creation and it is one command.

**Reasoning effort pinning: NO.** No `reasoning_effort` field exists on any per-job model override.

**Workarounds:**
1. **Separate profile** — Create a second Hermes profile with `agent.reasoning_effort: medium` in its config.yaml, then create the cron job from that profile via `hermes --profile glm-profile cron create ...`. The cron job inherits the profile's reasoning_effort at creation time. Requires CLI, not chat (the cronjob tool has no `profile` parameter).
2. **Prompt-level instruction** — Put "Use medium reasoning effort" in the cron prompt. This is not a real API-level parameter — it relies on the model complying, which is unreliable.
3. **Feature gap** — This simply doesn't exist yet. The `delegation` config section has `reasoning_effort` as a sub-option, so the concept exists elsewhere in Hermes, but it hasn't been wired into the cronjob tool's model override.

**Source:** Official Hermes docs at https://hermes-agent.nousresearch.com/docs/user-guide/features/cron and the cronjob tool schema. Verified by reading the docs directly — do not guess at cron capabilities.

## Known Failure Modes

### 10. Notifications that were never routed — `deliver` is not Telegram

**Symptom:** The user reports he never received notifications he was owed (an ack, a
completion ping) while the job's output file plainly contains the message that should have
been sent. `last_status: ok`, no delivery error anywhere in the job record.

**Root cause:** The job's persisted `deliver` field is `local`, not `telegram`. A job's
prompt can instruct it to "notify me on Telegram" all it likes — the delivery target is a
job field, not a prompt instruction, and a local job writes its final response to
`~/.hermes/cron/output/<job_id>/` instead of sending it.

**Detection — the per-run verdict is definitive:**
```bash
python3 -c "
import sqlite3
c = sqlite3.connect('~/cron/executions.db')
for r in c.execute(\"select started_at, status, delivery_outcome from executions where job_id='<job_id>' order by started_at desc limit 10\"):
    print(r)
"
```
Every row reading `suppressed` on a job that is supposed to notify him is the bug; a
working Telegram job reads `delivered`. Compare against a known-good job on the same box
when in doubt. Then read `deliver` out of `jobs.json` for that job id to confirm.

**Fix:** `hermes cron edit <job_id> --deliver telegram`, then read the field back. Do not
re-fire the run to "test" it — a re-fire duplicates the actual deliverable (the email, the
file) that already went out.

**Pitfall — never grep the output file for "completed" or "[SILENT]".** The file carries
the injected prompt above the `## Response` section, and the prompt quotes those exact
tokens, so the grep matches every run in the directory. Slice after `## Response` and read
that block.

## Zero-Cost Health Checks — `no_agent` Script Jobs

When the user asks for a recurring check and cares about cost, the answer is usually
a `no_agent=True` cron job: **the script IS the job.** No model, no tokens, no agent
spin-up, no iteration budget. It is the right shape for any check that is pure logic
(file exists, config parses, a guard still behaves).

Semantics that make it good for monitoring:
- stdout is delivered verbatim to the delivery target
- **empty stdout is a silent success** — the job stays quiet
- a non-zero exit or timeout raises an error alert

So the contract is: **print nothing when healthy, print only the problems.** The user
hears from it exactly when something is wrong, which is what makes an always-on check
tolerable instead of noise.

### Fixed-text reminders are `no_agent` script jobs too

Any job whose entire output is one message the user already wrote belongs to this
same shape, and should NOT be an LLM run. A reminder, a "we start tonight" notice, a
standing instruction to repost verbatim: the model adds nothing, and giving it a
model means it can paraphrase, append commentary, add a summary, or answer a
question nobody asked, any of which corrupts a message the user wanted exact.

Write the text into a script under `~/.hermes/scripts/<name>.py` that prints it, then
create the job with `--script <name>.py --no-agent`. The stdout is delivered verbatim,
costs zero tokens, and the model field is then decoration.

Keep the text a plain print, and verify it by running the script directly once before
creating the job:

```bash
python3 ~/.hermes/scripts/<name>.py | head -5
hermes cron create "2026-09-25T12:00:00" --name "<NAME>" --script <name>.py --no-agent --deliver telegram
```

Two rules for the script body:
- **No date arithmetic for a one-shot.** Do not compute the next occurrence in Python;
  pass the absolute ISO timestamp to `hermes cron create` and let the scheduler hold
  it. The script only prints the message.
- **State the weekday explicitly in the text** ("Wednesday morning", not "this
  morning"). A message staged days ahead and read later cannot rely on the reader's
  sense of which day it is, and an off-by-a-day claim in a reminder is a wrong fact
  the user will act on.

Exit 0 even when problems are found. A problem you found and reported is a successful
check; exiting non-zero makes it read as a failed job and buries the message in a cron
error alert.

**A health check must be proven able to FAIL, or it is decoration.** A checker that has
only ever returned "ok" is indistinguishable from one with a broken condition. Test it
by deliberately breaking each thing it claims to catch, one at a time, confirming the
right message fires, then restoring. Test the healthy path too — its output must be
empty, not a cheerful "all good" line that becomes daily noise.

**Use it to catch silent regressions after `hermes update`.** An update can change a
guard, move a module, or invalidate a consent record, and the user finds out when a
report arrives with something wrong on it. A nightly `no_agent` check that probes the
behavior the setup depends on turns "found out at 8AM" into "told the same night".
Probe BEHAVIOR (call the guard and assert it still refuses) rather than grepping source
— a behavior probe survives a rename.

### A `no_agent` script runs under the gateway's OWN interpreter — keep it stdlib-only

`cron/scheduler_script.py::_script_argv` launches the script as
`sys.executable <script>` for any non-`.sh` file. `sys.executable` is the interpreter
that owns the running gateway, which on this box is the standalone managed toolchain
(`~/.hermes/tools/python-<ver>-<platform>/bin/python3`) whose site-packages holds only
`pip`. The project's dependencies (`yaml`, `ruamel.yaml`, and every Hermes package) live
in the install venv, a DIFFERENT interpreter that the cron script never gets.

So default to stdlib-only: `json`, `os`, `subprocess`, `sys`, `tempfile`, `datetime`,
`glob`. A script that does `import yaml` or imports a Hermes module with no bootstrap
crashes on its own environment and prints an alert that reads like a regression in the
thing it was checking.

**But stdlib-only is the fallback, not the only option.** When the probe genuinely needs
the project's dependencies, do NOT re-exec or hunt for an interpreter: have the script
put the install's committed dependency tree on `sys.path` itself, exactly the way every
Hermes entry point does at boot. `pm.environments.activate_dependencies(project_root)`
appends the selected environment's site-packages to `sys.path` WITHOUT changing
`sys.executable` and WITHOUT a second process:

```python
def _activate_project_dependencies() -> None:
    """Put the install's committed dependency tree on sys.path. Never raises."""
    src_root = os.environ.get("HERMES_PYTHON_SRC_ROOT")
    if not src_root or not os.path.isdir(src_root):
        candidate = os.path.join(HERMES_HOME, "hermes-agent")
        src_root = candidate if os.path.isdir(candidate) else None
    if not src_root:
        return
    if src_root not in sys.path:
        sys.path.insert(0, src_root)
    try:
        from pathlib import Path
        from pm.environments import activate_dependencies
        activate_dependencies(Path(src_root))
    except Exception:
        pass  # PM absent: fall back to whatever the interpreter already carries
```

Call it as the FIRST line of `main()`, before any probe. This is the durable fix for the
whole class: it makes `import yaml`, `import ruamel.yaml`, and `from tools.<module> import
<symbol>` work under the cron interpreter, so a behavior probe can call the real guard
instead of grepping source. Keep it non-raising and non-re-execing so a broken PM
degrades to the old behavior instead of bricking the check.

**Verify a dependency-bootstrapped script under every interpreter, side by side**, because
the bug was interpreter-specific and one green run proves nothing:

```bash
# 1. the managed toolchain python — exactly what cron uses (sys.executable of the gateway)
~/.hermes/tools/python-<ver>-<platform>/bin/python3 ~/.hermes/scripts/<check>.py
# 2. the install venv (~/.hermes/installs/*/facts.json -> packages.venv.environment)
"$ENV_VENV/bin/python3" ~/.hermes/scripts/<check>.py
# 3. the system python3 (last-resort PATH entry)
/usr/bin/python3 ~/.hermes/scripts/<check>.py
```
All three must print nothing and exit 0. Then prove it through the REAL job, not an
ad-hoc run, and read the artifact rather than the exit code:

```bash
hermes cron run <job_id>
cat "$(ls -t ~/.hermes/cron/output/<job_id>/*.md | head -1)"   # expect: Status: silent (empty output)
```

**Read `ModuleNotFoundError: No module named 'yaml'` / `'ruamel'` as a script-environment
fault, never as evidence about the guarded behavior.** The alert is the checker reporting
on its own interpreter. Verify the guarded behavior directly before believing any part of
the message.

Interpreter path for a MANUAL run (diagnosis, not the fix): never guess it — resolve the
one the install uses.

```bash
grep -o '"/[^"]*environments/[^"]*venv"' ~/.hermes/installs/*/facts.json
# facts.json -> packages.venv.environment is the interpreter with yaml + ruamel:
"$ENV_VENV/bin/python3" ~/.hermes/scripts/<check>.py
```
Run the script under both the toolchain python and the install venv side by side to tell
the two apart during diagnosis: the toolchain python prints the false alarm, the install
venv prints nothing (healthy). Do not ship that as the fix — a cron job runs the script
with the gateway's interpreter and cannot be pointed at the venv; bootstrap the path from
inside the script instead (above).

**Pitfall — the same gap affects any sibling cron script on this box, and a fallback path
can hide it.** A script may carry a stdlib-only fallback (a regex where a YAML parse would
go) precisely because of this interpreter gap, so it runs clean while never exercising the
code path it was written for. Audit every script in `~/.hermes/scripts/` for imports the
cron interpreter cannot satisfy before assuming the one you are fixing is unique:

```bash
for f in ~/.hermes/scripts/*.py; do echo -n "$(basename $f): "; \
  <toolchain-python> - "$f" <<'PY'
import ast,sys,importlib.util as u
mods=set()
for n in ast.walk(ast.parse(open(sys.argv[1]).read())):
    if isinstance(n,ast.Import): mods|={a.name.split('.')[0] for a in n.names}
    elif isinstance(n,ast.ImportFrom) and n.module and n.level==0: mods.add(n.module.split('.')[0])
missing=[m for m in sorted(mods) if u.find_spec(m) is None]
print("MISSING "+",".join(missing) if missing else "ok")
PY
done
```
Report the siblings you find; fix only the script you were ordered to fix. The packaged
probe covers every script in the dir at once — run it with the toolchain python:
`<skill_dir>/scripts/audit_cron_script_imports.py`.

**Pitfall — dating the regression.** A silent health check that ran clean for days and
then started alarming right after a `hermes update` is pointing at the interpreter, not
at the guard: the update can re-point `sys.executable` at a new toolchain that lacks the
packages. Walk the output history before touching anything:

```bash
for f in $(ls ~/.hermes/cron/output/<job_id>/*.md | sort); do
  printf '%s  ' "$(basename $f)"
  grep -q "silent (empty output)" "$f" && echo "SILENT (healthy)" || echo "ALERT"
done
```

The last SILENT file followed by the first ALERT file brackets the change; compare that
date against the install's mtime (`stat -c '%y %n' ~/.hermes/installs/<id>`) before
concluding anything about the guard.

### Backstop and prune jobs: `last_status: ok` is not delivery

Two zero-token job shapes that stop working while every status field reads clean.

**A backstop (a second emailer that exists to guarantee a primary's delivery) must prove the
primary did NOT deliver.** Rules:

- `ok` means the script exited 0, not that it did anything. Read the run's output TEXT. A
  backstop printing `SKIP: <file> already emailed` every day is dead, not healthy.
- An idempotency marker is evidence only about the process that wrote it. When the primary
  path (an agent run sending mail through a scratch SMTP script) never writes the marker,
  the marker says nothing about the primary at all. Prove "already delivered" from the
  DESTINATION: read the recipient's mailbox over IMAP for a message whose subject carries
  the item's date, and send only when nothing is there. The read-back recipe is in
  `email-sender/scripts/verify_delivery.py`.
- Never let a date-keyed job fall back to "the newest matching file". Today's file missing
  does not make yesterday's file today's: the fallback silently emails a stale artifact, or
  with a marker silently marks it handled forever. Act only on the exact date's artifact
  and report the missing one.
- Derive the date from the FILE NAME, not the clock, and key every check and every subject
  line off it. A path passed in by argument then carries its own date, so an older file can
  never be sent under today's date.
- Fixing the lookup without fixing the duplicate risk ships a new failure. A backstop whose
  lookup was broken enough to never find a file has never sent anything; the moment the
  lookup works it double-sends beside a primary that succeeded. Decide the duplicate
  question in the same edit as the lookup, or do not make the edit.

**A prune/retention job that deletes stale accumulating files is silent when nothing is stale.**

- Ask the retention window, and one-time-now vs recurring-forever, before deleting anything.
  An irreversible bulk delete with an unstated threshold is a real choice that is HIS to
  make, and that is the one case where asking is not shrinking an order into a question.
- Parse the date out of the filename and keep files dated within the window. Do not delete by
  directory mtime when the name carries the date. Delete only files matching the exact name
  pattern, and leave anything unrecognized in place with a note saying so.
- Print a one-line summary only when it actually deleted something; empty stdout stays silent,
  per the `no_agent` contract above. Exit 0 either way.
- Prove the delete logic against FAKE dated files in a fresh `mktemp -d` directory before
  pointing it at the real folder: create files straddling both sides of the cutoff plus one
  unrelated name, aim the script's pattern at the scratch dir, and assert that exactly the old
  dated files vanished and the unrelated one did not. The real run afterwards must delete
  nothing and print nothing, which is the healthy state.
- Point it at ONE directory. A sibling cleanup job already owning another location is not a
  reason to widen this one; clearing a folder another job clears is a duplicate that can
  delete what that job was about to process.

### 0. Model Iteration Loop — Job Burns All API Calls on One Tool, Never Reaches Delivery

**Symptom:** Cron job fires (confirmed in agent.log), `last_status` shows "ok", Telegram delivers the final response, but the user reports the primary deliverable (email, file, API call) was never received. The output file exists but the `## Response` section at the bottom is empty or contains only the brief Telegram confirmation message, not the full work.

**Root cause:** The model enters an infinite loop calling the same tool (typically `execute_code` for character-count verification) on every turn. Each call returns a small result (e.g., 401 chars) in milliseconds, but the model never progresses to the next step. It exhausts all 90 API calls (the `max_iterations` ceiling) on that one tool. The turn ends with `reason=max_iterations_reached(90/90)`. The final response is whatever the model last generated, usually the brief confirmation message the prompt asked for, delivered to Telegram as if the job succeeded.

**Detection — the definitive pattern in agent.log:**
```bash
# 1. Check how the turn ended
grep "<session_id>" ~/.hermes/logs/agent.log | grep "Turn ended"
# Look for: reason=max_iterations_reached(90/90)

# 2. Count tool calls by type
grep "<session_id>" ~/.hermes/logs/agent.log | grep "tool " | grep "completed" | sed 's/.*tool //' | sed 's/ completed.*//' | sort | uniq -c | sort -rn
# If one tool accounts for 85+ of 90 calls, it's an iteration loop

# 3. Compare with a known-good run of the same job
# A healthy run uses 10-15 API calls with diverse tools (read_file, write_file, terminal, execute_code)
# A looped run uses 87-90 calls, almost all the same tool
```

**Key diagnostic:** Compare the tool-call distribution against a previous successful run of the same job. If a prior run completed in 13 API calls with diverse tools (read_file, write_file, terminal, execute_code) and today's run used 90 calls all on execute_code, the model is looping.

**Distinguish an iteration loop from a heavy run that merely ran out of budget.** Both end at `max_iterations_reached(90/90)` and both can leave `last_status: ok` with the primary deliverable missing, so the tool histogram alone is not enough. Two more probes separate them:

- **Duration.** An iteration loop burns its calls in a few minutes on a tool that returns instantly (seconds per call). A legitimate heavy run (a large sourcing and scanning pass, a big multi-source research pull) spends its calls on slow work and takes tens of minutes. Rank the recent runs of that job by `finished_at - started_at` from `executions.db`; a run an order of magnitude longer than the job's own baseline is a real workload, not a spin.
- **Tool diversity.** A loop shows one tool at ~95 percent of calls. A heavy run spreads across `terminal`, `execute_code`, `write_file`, `read_file`, and browsing, with the slow ones dominating wall-clock time.

A heavy run cut off at the ceiling is a BUDGET problem, not a model-stability problem: raising the ceiling or splitting the work into checkpointed stages is the fix, and pinning a different model does nothing. A loop is a stability problem, and its fix is the model pin plus the prompt-level tool caps above. Read the run's `## Response` in `~/.hermes/cron/output/<job_id>/<timestamp>.md` before choosing: it usually names the finished steps and the unfinished ones in order, which tells you plainly whether the run was working or spinning.

**Fix — two-part:**

1. **Pin the job to a different, more reliable model** via CLI (the `cronjob` tool's `action="update"` has NO `model` parameter):
```bash
hermes cron edit <job_id> --model <new_model> --provider <provider>
```
Example: `hermes cron edit 50dcd9876b7b --model glm-5.2 --provider ollama-com`

2. **Add prompt-level guardrails that cap the LOOP without letting a correctness check be skipped:**
   - Specify an explicit step-by-step execution order (Step 1: read data, Step 2: write file, Step 3: run the check, Step 4: send email, Step 5: final response)
   - Cap the loop, not the check: "Use execute_code only for the Step N check. Run it, fix every violation, re-run until it reports zero. That is expected work, not a loop."
   - State the primary deliverable explicitly: "The email is the primary deliverable."
   - **NEVER write "send it anyway even if the check fails", "proceed to delivery regardless", "at most 2 calls total", or "do not re-verify" into a prompt that carries a correctness check.** That wording does not prevent a loop, it licenses the run to ship broken output: the model takes the escape hatch, delivers content that violates the constraint, and `last_status` still reads `ok`. The loop is prevented by making the check cheap, deterministic, and bounded (a script that prints a violation count, plus a rule that an offending item is rewritten from scratch rather than trimmed), not by allowing the deliverable through unchecked. Cap how many times an UNRELATED action may be retried; never cap the thing the constraint depends on.

**Why `last_status: ok` is misleading here:** The cron scheduler marks the job as "ok" because the agent process completed (it hit max_iterations and returned a final response). The scheduler does not inspect whether the agent actually performed the work the prompt requested. The Telegram delivery of the brief confirmation message further masks the failure, since the user sees "Social media questions are ready" and assumes the email was sent.

**Session proof (August 15, 2026):** The SOCIAL MEDIA QUESTIONS - 5PM job (50dcd9876b7b) ran twice in one day. Both runs used deepseek-v4-flash:0731. Run 1: 90 API calls, 87 on execute_code, ended with max_iterations_reached. Run 2 (manually re-fired): 90 API calls, all on execute_code, same termination. The model was stuck verifying 190-char limits on social media posts, calling execute_code every 5 seconds for 12+ minutes, never reaching write_file or the email-sending step. The previous day's run (Aug 14) completed successfully in 13 API calls with diverse tools. Fix: pinned to glm-5.2 and added prompt guardrails limiting execute_code to 2 calls max.

### 8. Deliverable arrives with "File-mutation verifier: N file edit(s) FAILED"

**Symptom:** The job's report and email land normally, but the delivered Telegram message carries a footer like ``⚠️ File-mutation verifier: 1 file edit(s) FAILED this turn — /tmp/extract_all.py — [write_file] Refusing to overwrite ...``. The work succeeded; one helper-script write did not.

**Root cause:** Hermes refuses `write_file` on an existing file the run never read (`tools/file_tools_write_guards.py::_stale_overwrite_blocker`). The job wrote its throwaway helper to a FIXED path (`/tmp/extract_all.py`, `~/send_email.py`). Run 1 creates it; every later run is a fresh task that never read it, so the overwrite is refused and the verifier footer is appended to the user-facing message. A second branch does the same: `file_state.check_stale` refuses when another task in the same process previously wrote that path.

**Detection:**
```bash
grep -rl "File-mutation verifier" ~/.hermes/cron/output/ | wc -l
grep -rh "• \`/" ~/.hermes/cron/output/ | grep "Refusing to overwrite" \
  | sed 's/.*\`\([^\`]*\)\`.*/\1/' | sort | uniq -c | sort -rn
```
The second command ranks the offending paths. A small hit count over many output files is normal; a path appearing repeatedly IS the bug.

**Fix, in order:**
1. Delete the stale leftovers so the next run starts clean: `rm -f /tmp/<helper>.py ~/send_*.py`. This alone stops tomorrow's collision but does not prevent it recurring.
2. Make the generating script write helpers into a fresh per-run dir: `SCRATCH=$(mktemp -d /tmp/hermes-cron-XXXXXX)`, then `write_file` to `$SCRATCH/helper.py` and `python3 $SCRATCH/helper.py`. A brand-new dir means no path can pre-exist, so the guard cannot fire. This is the durable fix and belongs in the job's skill.
3. As a deterministic backstop that needs no model cooperation, register a `pre_tool_call` shell hook that moves a stale scratch script aside before the write — see `references/shell-hooks.md` for the config block, the allowlist gate, and the wire-format trap.

**Pitfall — the same guard fires in an ordinary session, not just cron.** Any `write_file` on a file the current task has not fully read is refused with "this task has not seen its full current content", and that includes a file you read early in a long session and then edited with `patch` — the patch invalidates the earlier read. The fix is one `read_file` of the CURRENT content, then retry the write ONCE. Do not reformat the payload, do not retry the same call in a loop, and do not route around it with a heredoc or a shell redirect: the read is the entire requirement. Expect the same refusal on the next file in the turn and read it first rather than discovering it by failure.

**Pitfall — do NOT read the footer as a delivery failure.** The report, the file, and the email all landed. Say so plainly, and fix the colliding path rather than re-firing the job (a re-fire duplicates the email).

**Pitfall — a fixed path that "always worked" can break on an update.** This guard is not new-user-facing config; it can arrive with `hermes update`. When a cron that ran clean for months starts producing this footer, date the regression against the install history before touching the job's prompt:
```bash
cd ~/.hermes/hermes-agent && git reflog --date=iso | head -20
git show <sha_BEFORE>:tools/file_tools_write_guards.py | grep -c _stale_overwrite_blocker
git show <sha_AFTER>:tools/file_tools_write_guards.py  | grep -c _stale_overwrite_blocker
```
The guard being absent in the older tree and present in the newer one is the proof. The prompt did not change; the runtime did.

### 1. Duplicate Run (same job fires twice on same day)

**Symptom:** Two output files in `~/.hermes/cron/output/<job_id>/` on the same day, several hours apart. Cron expression is correct (e.g. `0 8 * * *`).

**Root cause:** Thread lock gap. `tick()` uses `fcntl.flock()` as its cross-process lock. Inside the same process, two threads (ticker thread + pool worker) can each hold independent fcntl file descriptors — each gets its own lock. The `advance_next_run` call and `_running_job_ids` set don't cover this edge.

**Fix:** Added `running_at` persistent stamp on the job record:
- `set_job_running(job_id)` stamps the job with current timestamp before execution
- `clear_job_running(job_id)` removes it on completion (both success and exception paths)
- Any tick that finds `running_at` less than 30 minutes old skips the job
- `set_job_running` returns False if another worker already set the stamp, causing the caller to skip
- Survives restarts — the stamp is in `jobs.json`, not in-memory

**Files changed:**
- `cron/jobs.py` — added `set_job_running()` and `clear_job_running()`
- `cron/scheduler.py` — `_process_job` calls both before/after `run_job`
- `tests/cron/test_scheduler.py`, `test_parallel_pool.py`, `test_cron_workdir.py` — patched all tick() tests with `set_job_running` mock

### 2. Missed Run (no output, next_run_at jumped ahead)

**Symptom:** A scheduled job that should have fired produced no output file and `next_run_at` shows tomorrow's date. `last_run_at` is from a previous day. No error in logs.

**Root cause:** The original code did `advance_next_run(job["id"])` at line 2016 in `tick()`, BEFORE dispatching the job to the thread pool. If the gateway restarted between the advance and the pool worker actually running the job, `next_run_at` was already bumped to the future — the run was silently lost.

**Fix:** Moved `advance_next_run` inside `_process_job` (the pool worker thread), after `set_job_running` succeeds:
```python
# tick() — removed the advance loop, replaced with pass + comment
for job in due_jobs:
    pass  # advance moved into _process_job

# _process_job — now does advance AFTER set_job_running
if not set_job_running(job["id"]):
    return False
advance_next_run(job["id"])
```

This ensures next_run_at only advances when the job *actually begins executing*, not when it's merely queued.

### 3. Job fired twice within seconds on gateway restart

**Symptom:** On gateway restart recovery, a cron job that was mid-execution fires again immediately.

**Root cause:** Missing persistence of in-flight state — `_running_job_ids` is a Python `set()` that dies with the process.

**Fix:** The `running_at` stamp (fix #1) covers this. Any job with a `running_at` timestamp less than 30 minutes old is skipped by `get_due_jobs` via `set_job_running()`.

### 4. Delegate Task Overload — Job Hangs Without Delivery

**Symptom:** Job fires (confirmed in agent.log) but never delivers. No "delivered to telegram" entry. No output file. Process is gone but no completion signal.

**Root cause:** The cron agent called `delegate_task` with more tasks than `max_concurrent_children` (default: 3). The error forced a recovery loop of individual subagent spawns, each taking ~10+ seconds. The job was killed mid-execution before reaching delivery.

**Fix:** Limit `delegate_task` calls to 3 tasks max per call in cron prompts. Use sequential batches for larger workloads. See `references/delegate-task-overload-cron-hang.md` for full reproduction and detection steps.

### 5. Delegate Task Results Never Arrive in Cron Sessions

**Symptom:** Job dispatches delegate_task subagents successfully (confirmed in agent.log), subagents complete (confirmed by checking their output), but their summaries never enter the conversation. The cron job proceeds without the subagent data and produces an incomplete report.

**Root cause:** delegate_task subagents run in the background and deliver their results as new messages that re-enter the parent conversation. In cron sessions, the session may not persist long enough to receive these messages — the parent process exits or the session is closed before the subagents finish. The subagents' work is discarded.

**Detection:**
- Check agent.log for delegate_task dispatch entries
- Check if the final report is missing the content the subagents were supposed to fetch
- The subagents' results are gone — they cannot be recovered from the current session

**Fix:** Do NOT use delegate_task for browsing or data fetching in cron prompts. Use sequential browsing (browser_navigate + browser_snapshot) or curl-to-file extraction instead. Sequential browsing of 6-8 key articles takes roughly 2-3 minutes total and is reliable in cron. Focus browsing on the articles that will anchor your themes, not every story.

**Applies to:** Any cron job that needs to fetch content from external URLs. The skill that governs the task (e.g. tensorfeed, ironpulse) should document this in its browsing section.

**Symptom:** Job fires (confirmed in agent.log) but never delivers. No "delivered to telegram" entry. No output file. Process is gone but no completion signal.

**Root cause:** The cron agent called `delegate_task` with more tasks than `max_concurrent_children` (default: 3). The error forced a recovery loop of individual subagent spawns, each taking ~10+ seconds. The job was killed mid-execution before reaching delivery.

**Fix:** Limit `delegate_task` calls to 3 tasks max per call in cron prompts. Use sequential batches for larger workloads. See `references/delegate-task-overload-cron-hang.md` for full reproduction and detection steps.

### 6. Provider Timeout — "Non-streaming API call timed out after 150s"

**Symptom:** Cron job fails with `RuntimeError: Non-streaming API call timed out after 150s with no response (threshold: 150s)`. The failure message suggests adding a fallback chain (`hermes fallback add`) or setting `cron.model` / `cron.model_provider`.

**Root cause:** The model API call hit the request-timeout ceiling with no response. The 150s is the **hardcoded default** that applies when the provider has no explicit timeout configured. It is NOT a config value in config.yaml by default — it lives in the code path `get_provider_request_timeout()` in `hermes_cli/timeouts.py`.

**Diagnosis order:**
1. Read the job's output file: `~/.hermes/cron/output/<job_id>/<timestamp>.md` — the `## Error` block at the bottom carries the exact timeout error.
2. Confirm the provider has no timeout set: `grep -n "request_timeout_seconds" ~/.hermes/config.yaml` — if nothing, the 150s default applies.
3. Check `fallback_providers` in config.yaml — if `[]`, there is no rollover when the primary stalls.

**Fix — raise the provider request timeout:**
```bash
hermes config set providers.<provider_id>.request_timeout_seconds 300
```
The timeout resolution order (from `hermes_cli/timeouts.py`): per-model `timeout_seconds` first, then provider-level `request_timeout_seconds`. So you can also set it per-model under `providers.<id>.models.<model>.timeout_seconds` if you only want to bump one model.

**What this does vs. does not:**
- DOES: gives a slow-but-alive model room to finish instead of being killed mid-thought.
- Does NOT: help if the provider is genuinely hung or down. For that you need a fallback chain — `fallback_providers` is empty by default. The belt-and-suspenders fix is both: raise the timeout AND add a fallback provider.

**Pitfall — don't confuse with terminal timeout:** The `terminal.timeout` (180s) and `TERMINAL_TIMEOUT` env var are unrelated to the model API request timeout. The 150s is the model-call ceiling, not a shell command timeout.

### 7. Fire-Claim Ownership Loss — "Interrupted by shutdown", With No Shutdown

**Symptom:** `last_status: error`, `last_error: Interrupted by shutdown before terminal completion.`, yet the job's output file and delivery exist and the run finished normally. Other jobs show the same label on unrelated days.

**Root cause:** The per-job fire fence is a re-entrant, cross-process lock (`_fire_job_lock` in `cron/jobs.py`, 30s acquisition timeout). Any code path that takes the same job's fence while the run's own terminal save/deliver phase holds it makes the heartbeat thread time out, declare ownership lost, and self-interrupt a live run. The work already completed, so the report arrives and only the ledger row is written as a failure. A heartbeat that wraps its own jobs-store write in the fence reproduces this exactly.

**Detection signature — the ordering is the tell:**
```bash
grep -a -n "fire fence\|fire claim ownership lost" ~/.hermes/logs/errors.log | tail -20
# ERROR cron.jobs: Timed out waiting for local fire fence <cron_dir>::<job_id>; failing closed
# WARNING __main__: Job '<job_id>': fire claim ownership lost; interrupting stale run
```
A timeout on the *local* fence (a thread lock inside one process) means self-contention, not a competing process. Cross-process contention reports the file path fence instead.

**Cross-check the run actually finished:** read the job's `## Response` in `~/.hermes/cron/output/<job_id>/<timestamp>.md`, then confirm the ledger disagrees with it:
```bash
python3 -c "
import sqlite3
c = sqlite3.connect('~/cron/executions.db'); c.row_factory = sqlite3.Row
for r in c.execute('select status,error,started_at,finished_at from executions where job_id=? order by rowid desc limit 3', ('<job_id>',)):
    print(dict(r))
"
```
`failed` in the ledger alongside `delivered` in `deliveries.db` confirms the work landed and only the bookkeeping was lost.

**Fix:** this is a scheduler bug, not job config — patch or update the install, do not re-fire the job. Re-firing duplicates a report that already went out.

### 9. Capped run recorded as a SUCCESS — the pipeline stops mid-stage and nothing flags it

**Symptom:** `last_status` is `ok`, `executions.db` says `status='completed'` with `delivery_outcome='delivered'`, and any dashboard reads a clean run — yet the user reports a later stage never happened: no email, no file at the destination folder, no cleanup. The delivered message may even say plainly that those steps did not run.

**Root cause:** A turn that ends at the iteration ceiling is salvaged by the scheduler as a "fallback response", stamped complete, and delivered. The status is written by the code path that ended the turn, not by whether the prompt's steps were performed, so one stage of four and four of four are recorded identically. The ceiling resolves in `cron/scheduler.py::_resolve_cron_agent_setup`, and the resolution order IS the trap: **the job record's own `max_turns` can be persisted by the job store and never read by the resolver.** When that function pulls the cap from `agent.max_turns` in `config.yaml` only, a job carrying `max_turns: 200` still runs on the global 90 and is cut off mid-pipeline while its own record claims a budget it never got. A configured-but-unread field is worse than no field, because it reads as done.

**Confirm which number took effect from the turn-end line, never from the job record.** `jobs.json` reports what the job store persisted; only the turn-end line reports what the run was actually given (the `Turn ended: reason=max_iterations_reached(N/N)` line in the Detection block below). A record saying `max_turns: 200` beside a turn ending at `(90/90)` means the field is not being read, and no prompt edit or story trimming will change that.

**The fix is three lines in `_resolve_cron_agent_setup`:** try `job.get("max_turns")` first, fall back to `_cfg["agent"]["max_turns"]`, then the legacy root `max_turns`, and pass the winner through `resolve_turn_limit`. A job without the field must still inherit the global unchanged. Prove both halves with the packaged probe — `scripts/probe_cron_job_turn_budget.py` — which drives the real resolver through a stub `jc` and asserts a per-job value WINS and an absent value still inherits. Run it after any edit to that function, before believing the fix.

**Detection — the three-line log signature:**
```bash
grep -aE "cron\.scheduler" ~/.hermes/logs/agent.log \
  | grep -aE "iteration limit|completed successfully|delivered to" | tail -12
# WARNING cron.scheduler: Job '<name>' reached the iteration limit but produced a final fallback response; delivering the response instead of failing the cron run
# INFO    cron.scheduler: Job '<name>' completed successfully
# INFO    cron.scheduler: Job '<id>': delivered to telegram:<chat> message_id=...
```
The `reached the iteration limit` warning next to `completed successfully` is the tell. Confirm the turn end with:
```bash
grep "<session_id>" ~/.hermes/logs/agent.log | grep "Turn ended"
# Turn ended: reason=max_iterations_reached(90/90) ... api_calls=90/90 tool_turns=90
```

**Rule — for a multi-stage job, verify every stage's ARTIFACT, never the job status.** A job that builds, files, emails, and cleans up has four artifacts; check each by its own evidence (the file present at its destination path, the sent-mail record, the DB row count before and after). `last_status: ok` is evidence about the process, not about the work. Report per-stage state; never say "the job ran".

**Rule — a "filed" or "sent" claim in an earlier run's response is not evidence; re-check the destination.** A run can report `Filed to: <path>` for a stage it never reached, because it reported its intent. Stat the destination path before repeating the claim — a filing reported for two consecutive runs and absent both times means the copy step itself is broken, not that one run was unlucky.

**This is NOT the loop in Failure Mode #0.** Both end at the same ceiling. A loop shows one tool at ~95 percent of calls over a few minutes; a heavy run spreads across the slow tools over tens of minutes (this one: 71 `terminal`, 18 `write_file`, 4 `read_file`, 2 `skill_view` over 12 minutes, context growing 20K to 170K tokens). A heavy run cut off is a budget problem, so the fix is consolidation and checkpointing, not a model pin.

**Fix — make the tail of the pipeline unstrandable.** When the delivery stages are a long tail of ad-hoc tool calls (copy, send, verify, clean up), the ceiling eats them last. Move every stage after the report is built into ONE script that does copy, send, and cleanup in a single call, and write the built artifact with one `write_file` rather than many. Then a cap can cost the run its tail at exactly one point, and that point is observable. See `references/checkpointed-cron-pipeline.md` for staging the work across runs.

**Fix — make the capped run's own status honest, in three seams.** The scheduler cannot know whether a prompt's stages ran, but it CAN know the turn hit the ceiling, and that fact must reach both the delivered message and the stored status. Three edits, in this order:

1. **Flag it where the cap is detected.** `cron/scheduler.py::_final_response_from_result` already branches on `is_max_iteration_handoff(result)` (predicate in `agent/turn_failure_copy.py`) to decide a capped turn is delivered rather than failed. Set a marker on the result in that same branch (`result["turn_capped"] = True`) next to the existing `logger.warning`. One detection, both consumers.
2. **Label the delivery in `run_job`.** After the `_final_response_from_result` call, prepend a fixed banner to the response when the marker is set, so no reader can mistake a checkpoint for a finished job. **Write it back into `result["final_response"], not just the local variable** — the empty-response guard further down re-reads `result["final_response"]`, so a local-only edit is invisible to it and to anything else downstream.
3. **Record a non-`ok` status at the terminal write.** In `_finish_completed_run`, pop the marker and set `mark_kwargs["status"] = "incomplete"` (overriding the `"ok"` that `_record_run_outcome` would otherwise derive), and set `d.error` if unset. `last_status` literals are a closed set read by the dashboard; a new literal needs its tone added or it falls through to the destructive/unknown branch.

**A per-job turn budget is the other half.** The global ceiling cannot serve both an interactive turn and a 36-story brief, so a heavy job needs to carry its own number. Add `max_turns` as a first-class job field: an entry in `_CREATE_FIELD_NORMALIZERS` and `_UPDATE_FIELD_NORMALIZERS` in `cron/jobs.py` (validate through `hermes_cli.config.resolve_turn_limit` so the job cannot store a value the runtime rejects), a keyword on `create_job`, a line in the optional-keys loop that persists it only when set — so pre-feature job records stay byte-identical and keep inheriting the global — and the per-job-first resolution order in `_resolve_cron_agent_setup` above.

**Pitfall — persisting the field is the easy half and the useless half on its own.** A job field that the resolver never reads is invisible: `jobs.json` shows the number, `hermes cron list` shows the job as configured, and the run dies at the global ceiling anyway. Whenever you add or touch a per-job override, the same change order applies: write the field, READ it where the run is constructed, then drive the real constructor and assert the value it returns. Editing only the job record is a no-op dressed as a fix.

**Verify a status/label fix by driving the real predicate, not by reading the diff.** Feed a synthetic capped result through `_final_response_from_result` and assert the marker is set, then feed a `completed=True` result and assert the marker is ABSENT — a marker set on every run would silently stamp healthy jobs as incomplete. Import `cron.scheduler` under the install venv to prove it loads clean.

## Key Code Paths

| File | Function | Purpose |
|------|----------|---------|
| `cron/jobs.py` | `set_job_running()` | Stamp job with `running_at` in jobs.json |
| `cron/jobs.py` | `clear_job_running()` | Remove `running_at` stamp after completion |
| `cron/jobs.py` | `advance_next_run()` | Bump `next_run_at` to next occurrence (now moved inside `_process_job`) |
| `cron/jobs.py` | `mark_job_run()` | Record completion, compute next `next_run_at` |
| `cron/jobs.py` | `_normalize_turn_limit()` | Validates the per-job `max_turns` field via `resolve_turn_limit` |
| `cron/scheduler.py` | `_final_response_from_result()` | Deliverable text from a run result; flags a capped turn as incomplete |
| `cron/scheduler.py` | `_finish_completed_run()` | Terminal `mark_job_run` + execution ledger row for a delivered run |
| `agent/turn_failure_copy.py` | `is_max_iteration_handoff()` | Shared predicate: a non-failed capped turn that still carries a summary |
| `cron/scheduler.py` | `tick()` | Main entry point — finds due jobs, partitions workdir/parallel, dispatches |
| `cron/scheduler.py` | `_process_job()` | Pool worker — now does set_running → advance → run_job → clear_running → mark |
| `cron/scheduler.py` | `_submit_with_guard()` | Checks `_running_job_ids` before dispatching |
| `cron/jobs.py` | `_fire_job_lock()` | Per-job fire fence; 30s timeout, fails closed |
| `cron/jobs.py` | `heartbeat_fire_claim()` | Refreshes the run's fire claim; must NOT hold the fire fence while writing the jobs store |
| `cron/scheduler.py` | `_record_fire_ownership_lost()` | Writes the misleading shutdown label after a lost claim |

## Verification

### A cron code edit needs no gateway restart — executions are separate processes

A cron execution runs in its OWN process, not in the gateway: `executions.db` records a
fresh `pid` per run (three runs of the same job inside two minutes carry three different
pids, none of them the gateway's `MainPID`). So a patch to `cron/scheduler.py` is live for
the next dispatch without a restart, and demanding one before proving the fix is wrong.
Confirm with the pid column rather than assuming either way:
```bash
python3 -c "
import sqlite3
c=sqlite3.connect('~/cron/executions.db'); c.row_factory=sqlite3.Row
for r in c.execute(\"select status,pid,started_at,finished_at from executions where job_id='<job_id>' order by rowid desc limit 4\"):
    print(dict(r))
"
```
This is the OPPOSITE of a config or hook edit, which loads at gateway startup only and is
inert until a restart. Decide per edit type: config/hook = restart required; `cron/*.py` =
next dispatch.

### Proving a per-job turn-budget fix

`scripts/probe_cron_job_turn_budget.py` drives the real `_resolve_cron_agent_setup` with a
stub `jc` and the provider/MCP gates neutralised, so it needs no config, network, or
provider. Four cases, all of which must pass:

```
job carries max_turns 200                      want=200  got=200  PASS
job carries max_turns 300                      want=300  got=300  PASS
job carries no max_turns (inherits global)     want=90   got=90   PASS
job carries None (inherits global)             want=90   got=90   PASS
```

The last two cases are the guard on the guard, and they are the point: a "fix" that raises
every cron job to the per-job value silently changes every other job on the box. Always
assert the inherit path alongside the override path. Run it under the install venv so the
import is real (`grep -o '"/[^"]*environments/[^"]*venv"' ~/.hermes/installs/*/facts.json`
to resolve the interpreter — never hardcode an install path).

The probe is a synthetic harness: it proves the resolution logic, not that tomorrow's run
succeeds. After the next real dispatch, read the turn-end line for that session and confirm
it now reports the job's own ceiling.

### After applying the `running_at` fix
```bash
# Run the full cron test suite
python3 -m pytest tests/cron/ -q

# Check a specific job's status
python3 -c "
import json
j = json.load(open('~/cron/jobs.json'))
for job in j['jobs']:
    if job.get('running_at'):
        print(f'STILL RUNNING: {job[\"name\"]} since {job[\"running_at\"]}')
    print(f'{job[\"name\"]}: next={job.get(\"next_run_at\",\"?\")} last={job.get(\"last_run_at\",\"?\")} status={job.get(\"last_status\",\"?\")}')
"
```