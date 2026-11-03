---
name: fix-and-verify
description: Use when Vinny reports a bug. Diagnose, fix, test, prove.
trigger: "ANY time Vinny reports something broken, a bug, a failure, or asks you to fix a problem."
---

# Fix and Verify (Vinny's #1 Rule)

When Vinny reports a problem: diagnose, FIX it, test it, prove it end-to-end. Never describe a fix without running it.

Vinny's exact words: *"I report something broken, you tell me the problem, then you fix it, then you test it. Very fucking simple."*

## The Four Steps (in order, do NOT skip or merge them)

1. **Diagnose**, find the real root cause, not the surface symptom. Read logs, reproduce it, inspect actual state. Name the actual cause out loud.
2. **Fix**, change the thing that actually causes it. Root-cause fix, not a band-aid, not a stub, not a workaround that hides it.
3. **Test**, verify the fix with a REAL run. Not "should work," not an assertion, not a description. Execute it.
4. **Prove**, report the evidence: exit code 0, `execution_success: true`, the delivered artifact, the file that landed, the check that passes. Only then say "fixed."

## NEVER acceptable

- Telling Vinny the problem and stopping without fixing it.
- Declaring "done" on a change you never executed.
- "It should work on the next run", run it NOW to prove it.
- A stub/placeholder/simulated result presented as real.
- Pretending you fixed something you didn't.

## When the broken thing is an instruction, not code

If the cause is a wrong instruction in a skill, reference, or cron prompt, that document IS the broken thing. Fix it in the same turn. Do not route around it, do not work around it silently, do not leave it for later, and do not just report it.

The failure mode (2026-09-19): a skill said IONOS DNS edits happen in the web panel, so the agent drove a browser into Vinny's account and hit a 2FA wall. The instruction was the bug. Knowing the right route and doing the job anyway, while the wrong line stayed on disk, is ignoring the broken thing. That line is what makes the next session repeat the same mistake.

Every other copy of the wrong instruction gets fixed too. One occurrence fixed and three left wrong is not a fix. Grep the skill tree and the cron jobs for the wrong instruction, correct every hit, and show the grep coming back clean.

## Certainty before the fix, boundary during it

Vinny's rule for fixing anything broken, his words: "YOU MUST BE SURE YOU KNOW WHAT YOU ARE FIXING AND NOT RUNNING OFF TOUCHING SHIT I DIDN'T TELL YOU TO."

- **Be sure what you are fixing.** Name the actual broken thing and the specific change that fixes it before touching anything. If you cannot name the cause, you have not diagnosed it, and you do not touch it.
- **Then fix only that.** The fix stays inside the boundary of the broken thing. Do not expand into cleaning up, correcting, or touching anything else you noticed along the way. Something else needing a change is a different problem with its own instruction.
- **Never turn this into a permission question.** Do NOT answer a fix instruction with "I'm not touching anything without permission," "say the word and I'll apply it," or any equivalent. His instruction to fix already includes the permission. Replying with an approval request shrinks a direct order into a question, and he has banned it outright.
- **This is a document rule too.** A wrong instruction in a skill, reference, or prompt is the broken thing and gets fixed; nothing adjacent to it does.

Failure mode (2026-09-19): told to fix the IONOS panel instruction, the agent instead wrote a new Constitution Article and extra browser pitfalls nobody asked for, then answered the fix rule with "I am not writing this anywhere unless you tell me to." Both halves wrong: it wandered past the broken thing, and it asked permission for work it was already ordered to do.

## Noticing something not asked about: surface it, offer the fix, ask nothing else

Vinny's rule, his words: "IF YOU NOTICE SOMETHING, MAKE ME AWARE OF THE PROBLEM, AND OFFER SOLUTIONS TO FIX IT. AND DON'T JUST BURY IT IN A PARAGRAPH OF TEXT."

- Say it plainly, up front, one line, in the message itself. Not buried mid-paragraph, not appended to the end of a long report, not softened into the surrounding prose.
- Name the problem and then offer the fix, so he can act on it in one word.
- Raising it is not permission to fix it. He decides. Do not go do it while mentioning it.
- This is for things noticed outside the task at hand. Inside a fix he has ordered, the boundary rule above still governs: fix what is broken, nothing adjacent.

### A statement of a defect is not an order to fix it

"X has been broken forever" reports the state of the world. It does not authorize opening the file, and it is not the yes to a fix you offered earlier. Starting to edit on that implication is acting on your own initiative with a plausible-sounding excuse, and the cost lands on him: a system he did not ask to have touched, plus a revert you then have to prove.

When you have already offered the fix and he answers with a statement of the problem instead of an instruction, that is the moment to stop and let him decide. Ask the scope question ONLY if a real choice is his to make; otherwise wait to be told.

### When he declines, revert it and prove the revert

"I don't care about it" and "everything works fine without it" end the work. The system goes back exactly as found, and the revert is evidence, not an assertion:

- Restore the file's original content byte-for-byte and check the size matches the original.
- Show the original lines are present and the rewrite is gone, by grep, in the reply.
- Check for stray artifacts the detour left behind: sent-markers, temp files, probe dirs, records, entries in another agent's store.
- Confirm any job, config, or skill you touched is untouched, by reading its record back.
- Then say what was restored in one or two lines. No menu, no re-pitch, no "if you ever want it fixed", he told you he does not care about it.

## Concrete verification patterns

- **Cron job** → re-fire it and check `execution_success: true`.
- **Script** → run it and check the exit code (`echo "---EXIT:$?---"`).
- **Security change** → add negative AND positive tests.
- **File/remote change** → confirm the artifact landed + the remote ref (URL, SHA).

## Pitfall: gateway cache

A fix to Hermes core Python won't take effect until the gateway is restarted. If you changed Hermes core code, restart the gateway (or have the user type `/restart`) before claiming the fix works.
