---
name: failure-contingency-rule
description: Use when writing a script or loop. Add failure contingency.
---

# Failure Contingency Rule

Vinny's hard rule: whenever you write a script, or any type of factchecking/verification loop, you MUST write in a contingency for how to handle failure BEFORE the thing runs. Do not discover the failure mode at runtime.

## The rule
- Every script and every verification loop gets a written failure contingency up front.
- The contingency must specify: stop after X time or X iterations, then move on to the next part.
- Never let a loop block the primary deliverable (e.g. the email).

## What to write in
- A hard iteration cap (e.g. "at most 2 execute_code calls, then proceed").
- A hard time cap (e.g. "if not done in 60s, proceed").
- An explicit "move on" instruction: after the cap, proceed to the next step regardless of whether the check passed.
- For email crons: the email is the primary deliverable. Send it no matter what. Do not let character verification block it.
- Never claim a step succeeded (e.g. "email sent") unless you actually ran it and it returned success. If it failed, say so honestly.

## Why
The 5PM social media and Pinterest crons both failed because the model looped forever on identical text in a char-verification loop, hit the tool-call cap, and then skipped the email while still reporting "email sent." The fix is to make the primary deliverable unconditional and give every loop a hard stop-and-move-on.

## Best practice: take the deliverable out of the model's hands
For anything that must not fail (emailing a daily file), write a deterministic script that does the deliverable directly with no LLM in the path, and add a no_agent backstop cron that runs it a few minutes after the agent job. Make the script idempotent (sent-marker) so it never double-sends.
