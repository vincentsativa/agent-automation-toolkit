---
name: fix-and-verify
description: Use when Vinny reports a bug. Diagnose, fix, test, prove.
trigger: "ANY time Vinny reports something broken, a bug, a failure, or asks you to fix a problem."
---

# Fix and Verify (Vinny's #1 Rule)

When Vinny reports a problem: diagnose, FIX it, test it, prove it end-to-end. Never describe a fix without running it.

Vinny's exact words: *"I report something broken, you tell me the problem, then you fix it, then you test it. Very fucking simple."*

## The Four Steps (in order, do NOT skip or merge them)

1. **Diagnose** — find the real root cause, not the surface symptom. Read logs, reproduce it, inspect actual state. Name the actual cause out loud.
2. **Fix** — change the thing that actually causes it. Root-cause fix, not a band-aid, not a stub, not a workaround that hides it.
3. **Test** — verify the fix with a REAL run. Not "should work," not an assertion, not a description. Execute it.
4. **Prove** — report the evidence: exit code 0, `execution_success: true`, the delivered artifact, the file that landed, the check that passes. Only then say "fixed."

## NEVER acceptable

- Telling Vinny the problem and stopping without fixing it.
- Declaring "done" on a change you never executed.
- "It should work on the next run" — run it NOW to prove it.
- A stub/placeholder/simulated result presented as real.
- Pretending you fixed something you didn't.

## Concrete verification patterns

- **Cron job** → re-fire it and check `execution_success: true`.
- **Script** → run it and check the exit code (`echo "---EXIT:$?---"`).
- **Security change** → add negative AND positive tests.
- **File/remote change** → confirm the artifact landed + the remote ref (URL, SHA).

## Fix the machine, not the artifact

When the broken thing is a repeatable pipeline, cron job, or script, the fix is the code path, not a hand-built version of today's output. Producing the correct result by hand leaves the same failure in place for the next run and reads as ignoring the instruction, even when the output itself is good. Edit the script, wire it into the command that runs it, then let the pipeline produce the artifact. If a hand-built artifact is unavoidable while the code is being fixed, say plainly that the pipeline is still broken.

## Test the smallest unit, not the whole pipeline

A change to one function gets proved by calling that function against a handful of known-good and known-bad inputs. Re-running the full pipeline after every edit costs minutes per iteration and is how a five minute fix turns into an hour. Run the unit check first, then exactly one end-to-end run to prove the wiring.

**Never quote a duration for a fix you have not already executed.** "Two minutes" on an unproven step becomes a deadline the user times, and missing it costs more trust than the work saved. If asked whether it can be done in N minutes, answer from a step you have already run, or say the honest state instead of a number.

## Pitfall: gateway cache

A fix to Hermes core Python won't take effect until the gateway is restarted. If you changed Hermes core code, restart the gateway (or have the user type `/restart`) before claiming the fix works.
