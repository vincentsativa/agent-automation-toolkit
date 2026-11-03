# Breaking Rumor Verification — "I saw this on X, is it true?"

## The class of task
Vinny sees a claim on X/Twitter (an acquisition, a release, a deal) and asks
"is this true? find out for me." This is a recurring, high-stakes task: the
answer must be a clear verdict, not a source dump, and the crux is correctly
labeling **reported vs confirmed**.

## The core distinction (the whole job)
- **Reported** = a news outlet citing anonymous sources ("The Information
  reported, citing a person familiar with the deal"). This is NOT confirmation.
- **Confirmed** = an official statement from one of the parties (press release,
  company blog, CEO statement, regulatory filing).

The single most important discipline: **do not let "agreed to buy" from an
anonymous-sourced report become "confirmed" in your answer.** The word "agreed"
in a headline is the outlet's framing of one source's claim, not a done deal.

## The workflow (what worked Aug 2026, NVIDIA/Hugging Face)
1. **Search broadly first** — two parallel queries (e.g. "NVIDIA acquire
   Hugging Face confirmed" + "NVIDIA buys Hugging Face news") to map the
   landscape and catch both the rumor and any confirmation.
2. **Extract the actual reporting, not just headlines.** Headlines say "agreed
   to buy"; the body says "citing a person with knowledge" and "did not
   respond to requests for comment." The body is where the sourcing lives.
3. **Check the companies' own channels directly** — official blog, changelog,
   CEO's X account. Silence there is a signal. (Hugging Face's blog and
   changelog had nothing; Delangue was publicly silent.)
4. **Note the escalation timeline.** Rumors escalate fast: "exploring a sale"
   → "in serious talks" → "agreed to buy" over days. Track the dates and
   report the trajectory — that's often what the user is sensing ("I think
   that recently changed").
5. **Deliver ONE verdict with the specific gap named.** e.g. "Likely real but
   unconfirmed. The reporting is credible and fits the pattern, but it traces
   to a single anonymous source and neither company has confirmed. Treat it
   as a strong rumor until one of them announces." Name exactly what would
   constitute confirmation.
6. **Offer to keep watching** — the user may want a flag the moment a party
   breaks silence.

## Pitfalls
- **Headline-as-fact.** "Nvidia agrees to buy Hugging Face for $12.9B" is a
  headline; the sourcing is one anonymous person and Reuters "could not
  immediately verify." Read the body before you commit.
- **"No comment" ≠ denial.** Both companies declining comment is not a
  confirmation and not a denial — it's the absence of confirmation. Say that.
- **Escalation ≠ confirmation.** A story moving from "talks" to "agreed" over
  three days is the rumor maturing, not the deal closing. The deal can still
  crumble ("still being finalized and may still crumble").
- **Don't over-hedge into mush.** The verdict should be decisive about the
  *status* ("unconfirmed as of now") even while the *outcome* is uncertain
  ("likely real"). Vinny wants a clear read, not a shrug.

## Worked example (NVIDIA / Hugging Face, Aug 26 2026)
- Aug 23: Business Insider — Hugging Face exploring a sale at $13B+, hired a
  bank, no buyer named.
- Aug 26: Business Insider — Nvidia in "serious talks" at more than $13B;
  Microsoft had met but was no longer active.
- Aug 26: The Information — Nvidia has "agreed" to buy for $12.9B, citing one
  person with knowledge.
- Reuters picked it up but "could not immediately verify." Neither company
  responded to comment requests. Nothing on Hugging Face's blog/changelog;
  CEO Delangue publicly silent.
- Correct verdict: **likely real, unconfirmed.** Credible reporting, fits the
  pattern (Nvidia was already an investor; HF had rejected a $500M Nvidia
  investment at $7B in January on governance grounds, then reportedly
  reversed course at $12.9B). But it traces to anonymous sourcing and no
  official statement. Confirmation = Nvidia or Hugging Face announcing.
