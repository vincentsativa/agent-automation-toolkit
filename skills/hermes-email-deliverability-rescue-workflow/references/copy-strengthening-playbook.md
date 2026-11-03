# Copy-strengthening playbook (subject lines and body)

Use when asked to review, critique, or strengthen the outreach email copy. The canonical copy lives in the code, not in this skill: read the live `TEMPLATE`, `SUBJECTS`, `OBSERVATION`, `ALLY`, `QUESTIONS`, and `CTAS` blocks from `~/money_ideas/outreach.py` in the same session before quoting any of it, because a remembered copy proves nothing. Do not describe a remembered version as current.

Deliverable shape when Vinny asks for the copy plus recommendations: one document (emailed via the IONOS SMTP skill, never pasted into chat) with Part 1 = the exact current copy (subjects, template, openers, questions, CTA, ally line) and Part 2 = recommendations.

## What is protected (do not touch without a direct order)

- The per-defect specificity. Every subject is literally true and names the domain; that is the moat and the anti-spam tell.
- The invoice/forgery angle. It ties a DNS record to money, which is the right nerve.
- The ally line's non-salesy framing and the "Reply stop" opt-out exactly as written.

## Subject line rules (honest but high-open)

1. Under 60 characters where possible; longer subjects truncate in Gmail mobile preview and bury the payoff.
2. Lead with the consequence to THEIR money or customers (invoices, customers, bouncing, spoofed), never with the protocol name (SPF, DKIM, DMARC). Owners know invoices, not acronyms.
3. Never put spam trigger words (free, urgent, act now, guarantee) in the subject; "free" belongs in the body CTA only.
4. Keep the question format where curiosity is the hook (the dmarc subjects); when the stakes are concrete, a statement of consequence outperforms a question.
5. The personal domain stays in every subject, always.
6. ONE copy set, no A/B arm. Vinny's order (2026-09-29): the approved copy goes to 100 percent of the list. An A/B split on the same approved change put the retired old subjects on half the batch, which is a directive violation, not a test. Test variants only when he orders the test.
7. The auditor test: if a subject sounds like a note from an auditor or a warning label, cut it again. It must create immediate loss, fear, or curiosity in under 6 seconds and read like something an owner says out loud.
8. Not every current subject has a better rewrite. When every variant tried is vaguer than the current line (dkim_revoked, no_reporting), keep the current line and say so; a weak rewrite is worse than a strong original.
9. Measure the set before recommending it. The character budget that matters belongs to the domain, not to the line, so render every subject against a 16, 21, and 25 character domain, print the counts, and report the max per domain length. A set that fits at 16 characters routinely breaks at 25, the longest domain pushes several lines 20 or more characters past the cutoff, and a recommendation that quotes one domain's length is guessing.

## Body recommendations (strength order)

1. Preheader swap: the first ~90 chars after the subject are the preheader. Front-load the business consequence, then the record detail, rather than opening with "I checked the mail records".
2. First body line is ABSOLUTE: the exact business consequence and nothing else, no warmup. Locked order: consequence, then exact scan detail (proof), then record detail (mechanism). Proof before mechanism.
3. Ally line to one sentence; two reads like a preamble.
4. Reveal the price after the CTA, two sentences max ("$500 flat, one domain, done within a day. I show you the before and after so you can see exactly what moved."). Cut all process language (delivery sequence, ninety minutes) until the prospect asks.
5. One exact scan detail per observation, mandatory, no exceptions: a count, hostname, policy token, qualifier, or key state pulled from the scan row. Absence defects (no SPF, no DMARC) carry no token to name; the sentence must still read correctly with the proof slot empty.
6. ONE CTA only, never rotate as a default posture. "Want the free findings sheet for {domain}? Reply and I will send it today." Rotating phrasings triples the testing volume needed to learn anything; rotate only if data shows the single CTA losing.
7. Closing questions: kill the leading "So", and name a concrete object (invoices, replies, customer trust) every time. Abstractions like "authentication" are banned unless immediately tied to mail landing.
8. Plain-language layer for the non-technical owner: after the mechanism sentence, add one short sentence saying what the record failure means in the reader's own words, with the why-it-matters inside it. Working register: a system that watches for fakes and blocks none of them; no approved-sender list, so nothing checks who is using your name; a list longer than the system will read, so it errors out; a signature whose key was taken away, so it proves nothing; a security camera with no recording. Cap it at 25 words and about 15 words of growth in the body. Placement is fixed: consequence, proof, mechanism, plain meaning, ally line. It never opens the email, because a cold reader decides in the first line whether the mail was written for him, and it never replaces the mechanism sentence, because the exact record detail is what proves the finding is real.

## Building value for the flat fee (the Socratic move)

A stated price with nothing in front of it asserts value, and an assertion gets argued with. Put the buyer's own number next to the fee instead of arguing for it.

- Add the price-against-pain question as the second closing question, directly between the diagnostic question and the CTA, so the fee answers a number he just produced himself. Working line: "What is one invoice that never got a reply worth to you, and how many went quiet this year?"
- The recurring-loss framing is the whole mechanism: one lost invoice repeats every week for as long as he owns the domain, and the fix happens once. Do not write the word value and do not add a benefits list.
- It is a question, not a claim, so it must not contain its own answer. The claim version (the records get fixed once and every invoice, quote, and reply is protected from then on) is a weaker instrument; hold it as the A/B fallback, never as the default.
- It reuses the line already proven on the offer page, so the cold email and the page make the same argument in the same way.
- Ordering inside the body stays locked: observation, ally, diagnostic question, price-against-pain question, CTA, link, price line. The price line itself keeps its wording, because "done within a day" matches the turnaround promised on the offer page.

## Implemented copy architecture (v5: ONE copy for every send)

**No A/B split. No control arm. No old lines. `SUBJECTS_NEW` and `BARE_OPENERS` are deleted from `outreach.py`.** `build_message` reads `SUBJECTS`, `OBSERVATION`, `PLAIN`, `QUESTIONS`, `CTAS`, `VALUE_QUESTION`. Its `variant` argument remains only so existing callers do not break; it changes no word of the output.

- **Vinny's order, 2026-09-29: a single version of the approved copy goes to 100 percent of the list.** He approved a change; an A/B split shipped with it and half the batch went out on the old copy. Do not reintroduce an A/B arm, a control group, or a "half the batch" split without a direct order that names it.
- **A recommendation inside a document is not authorization to build the optional part of it.** When the deliverable contains a test that could be run, ship the change and say the test is available as a separate step Vinny can order. Wiring a test into the live send path on the strength of "make your recommended changes" is the failure, not thoroughness.
- **"Implement the change" means all of it, everywhere it appears.** A partial implementation (new subject set on half the sends, new body on all of them) is worse than no change: it looks done and it ships the old version to half the list.

Fixed body order, locked by test: greeting, observation (consequence, proof, mechanism), the plain-terms line, ally, diagnostic question, the value question, CTA, link, price, signature, opt-out. The plain line never opens the email, because a cold reader decides in line one whether the mail was written for him.

- **`PLAIN` must carry a key for every kind `pick_template` can return, including `generic`.** A missing key is a KeyError at compose time, not a missing sentence, so add the key with any new defect variant.
- **The plain-terms line is the non-technical translation, and the why-it-matters lives inside it.** Write it in the owner's words (invoices, customers, a lock, a list, a camera) and never repeat the protocol name.
- **Value is built Socratically, never asserted.** The `$500` line states what is covered; the value question before the CTA makes the owner price the problem himself, in his own units, so the fee answers a number he just produced. `VALUE_CLAIM` is the recorded fallback.
- **Verify a copy change by rendering the whole matrix, not one sample.** Loop every defect kind through `build_message`, and check each body for: no literal brace survives, the new sentences are actually present, and the paragraph order matches the intended order by index comparison rather than by eye. A single sample render (one defect, one variant) passes while another kind raises at compose time, which is exactly how a missing dict key ships. Then run the gate suite (`test_outreach.py`) and read its pass count out of the run.
- **Prove single-copy with the index check.** Render six consecutive send indexes for every kind and assert the output is byte-identical across all of them. That is what catches a surviving alternation branch; a render at variant 0 alone cannot.
- Test suite: run with the mailer env sourced (`set -a; . ~/.config/phantombyte/mailer.env; set +a`) or the postal-address and SMTP-pass refusal tests fail spuriously; run with the system `/usr/bin/python3`, not the Hermes-bundled interpreter, which lacks the pipeline's `requests` install.
- If a known-answer test asserts an old copy sentence verbatim, update the assertion to the new truth the copy still carries (e.g. it names p=none), not the old phrasing.

## Copy review deliverable rules

- Recommendations are recommendations: do not apply them to outreach.py unless Vinny orders the change.
- Deliver as one emailed attachment, one long unwrapped-line document, current copy first.
- Part 1 is the exact current copy, and exact means every block that feeds a message: `SUBJECTS`, `TEMPLATE`, `ALLY`, `OBSERVATION`, `PLAIN`, `QUESTIONS`, `CTAS`, `VALUE_QUESTION`, and the price line.
- Render the live bodies through `build_message(row, offer_url, person, email)` with one synthetic scan row per defect carrying the columns `proof_detail` reads, instead of reading the dicts by eye. There is no variant branch any more; the render shows the `{proof}` slot filled, which a dict read cannot. Run that render with the system `/usr/bin/python3`.
- Report the measured facts in Part 1 (body word count per variant, subject character counts per domain length, the worst-case subject) so Part 2's recommendations answer something measurable rather than taste.
- Say plainly in Part 2 what was not touched and why, and state that no edit was applied in this session.
