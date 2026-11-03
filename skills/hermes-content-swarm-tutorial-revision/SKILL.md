---
name: tutorial-revision
description: Revise a tutorial so it does exactly what it claims.
trigger: "Vinny asks to revise/fix a tutorial, or a tutorial overclaims what its code does."
---

# Tutorial Revision

## Core Principle

A tutorial must do what it claims, at any price point. That is the only way to
earn repeat buyers. If the text says "you can run this against your own traffic"
but the code does not actually do that, the tutorial is broken regardless of how
good the prose reads.

When Vinny points out a problem with an outline or tutorial, state the issue
clearly and directly first, so it can be fixed. Do not bury it in hedge language.
Name the defect, then fix it.

## When to Load

- Vinny asks to revise or fix a tutorial
- A tutorial's prose overclaims what the shipped code actually does
- A tutorial's code and its own explanatory sections contradict each other
- Reviewing a tutorial before delivery and finding the claim does not match reality

## The Two Standard Defects to Hunt For

Most tutorial breakage falls into one of two buckets. Check both on every revision:

### 1. The Fake Signal

The tutorial claims the code uses a real mechanism, but the code substitutes a
proxy that does not work the same way.

Classic example (Stop Burning Tokens v1): the prose said confidence routing on a
real signal. The code used a length heuristic (`eval_count / len(text)`) that
pinned nearly every response to ~0.675 regardless of task difficulty, so routing
decisions above that threshold were arbitrary.

Fix pattern: replace the proxy with the real mechanism the prose claims. For
confidence routing, that means self-assessment (model returns its answer plus a
confidence number in a structured JSON field) or real logprob access, not a
length ratio.

### 2. The Incomplete Ledger

The tutorial's reporting/dashboard undercounts or misstates savings because some
code path does not write the fields the dashboard reads.

Classic example: the ACCEPT_TIER1 branch returned without writing the frontier
baseline and savings figures, so the dashboard only showed savings on escalated
requests. The "savings" headline was understated and the tutorial claimed
measurement on every request.

Fix pattern: make every branch write the same ledger fields the dashboard
aggregates. Every logged request must carry the baseline, actual cost, and
savings, not just the expensive branch.

## Revision Workflow

1. **Read the tutorial and the code together.** The prose is the contract. The
   code is the deliverable. Find every place the prose promises something the
   code does not deliver.

2. **Verify the code actually runs and behaves correctly.** Do not trust a
   re-read. Execute the parser or core logic with representative inputs: a
   valid case, a malformed case, and an out-of-range case. Confirm the safe
   default (escalate on malformed, clamp out-of-range values) actually fires.

3. **Fix the root cause, not the symptom.** The fix is in the code, then the
   prose is aligned to the corrected code. Never fix the prose to describe the
   broken code.

4. **Align the copy.** Update the tutorial sections that describe the mechanism
   so they match what the corrected code does. Remove internal contradictions
   (e.g. Section 2 claiming logprobs when the code uses self-assessment).

5. **Re-check the price logic against the skill `paid-product-pricing-model`.**
   A tutorial that genuinely ships working code earns the cheap full-build tier.
   A tutorial that overclaims does not. Decide whether the price stays or moves
   based on what the corrected tutorial honestly delivers. Default to keeping
   the price if the code now matches the claim.

6. **Check no em dashes.** Run a search for the em dash character (U+2014).
   Vinny rejects them in all writing. Count must be zero.

7. **Email the revised copy** via the `email-sender` skill (IONOS SMTP to
   hello@phantom-byte.com) with the file attached. Confirm on Telegram with a
   short list of what changed. Do not paste the document into chat.

## Pitfalls

### Rewriting Without Running the Code
Never ship a revised tutorial whose logic you have not executed. A parser that
"looks right" can still return None on a valid input. Run it.

### Fixing the Copy to Match Broken Code
If the prose overclaims and the code is weak, the fix is to strengthen the code,
not to soften the prose so the tutorial "only claims what it has." The whole
point is that the reader gets a working thing.

### Forgetting the Ledger
The dashboard and the router are one system. If the router does not write a
field on every branch, the dashboard is lying. Check both sides of the log
format together.

### Price as an Afterthought
Whether the tutorial is free or $100, it must do what it says. Price is a
separate decision made after the code is honest. Do not change the price to
compensate for a bug; fix the bug.

### Em Dashes Sneaking Back In
The revision is a fresh write. Run the em dash sweep on the final file, not
just the changed sections.

## Related

- `tutorial-writing`, the writing skill (concept vs blueprint)
- `paid-product-pricing-model`, pricing the cheap full-build vs build-for-you tiers
- `email-sender`, IONOS SMTP delivery to hello@phantom-byte.com
- `phantom-byte-writing-style`, the voice rules for any published copy
