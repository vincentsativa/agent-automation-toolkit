# Plan Review Checklist

Applied when another agent's plan is being critiqued and rebuilt. The output is one replacement document, not a critique with a fix list on the end.

## Cut these on sight

- **Scope that cannot be delivered cold.** A check that needs dashboard access, a credential, or the customer's cooperation is not part of a cold audit. Split the list into what is measurable now and what is confirmed after authorization, and say on the offer page which is which. Selling undeliverable scope loses the first customer and every referral after them.
- **Unbounded build phases.** Any phase that says "handle the JavaScript builders" or "support every platform" is a week. Narrow it to the cases the tool actually handles, mark the rest unverifiable, and drop them. Naming what you refuse to build is part of the design.
- **Invented conversion arithmetic.** A revenue projection built on placeholder rates answers a question nobody asked and gets repeated as if it were data. Delete it. Replace with the rate set that can be measured from the first batch (qualified, reply, positive reply, close, take rate) and the diagnostic rule for each bad number, for example: positive reply rate high plus close rate low means the first line of the offer is not landing.
- **The fixed-day plan.** A seven-day plan that hides the real build in day one is a lie about effort. Put the build first, then a gate, then everything else.
- **Self-hedges and agent authorship notes.** A line admitting a section was added without instruction makes the reader distrust the rest; rebuild it as the document's own position.

## Add these

- **One sentence definition of success that is stricter than the obvious signal.** For a delivery product, an HTTP 200 is not delivery; success is the handler's documented success payload. Write the strict definition because it is the thing a buyer can check.
- **An explicit line of what will never be claimed.** Every offer whose value comes from a measurement must name its blind spot in public copy. It costs nothing and it is what makes the rest credible.
- **A go or no-go gate with a pass test.** Cheap build first, then a hand-picked test set that includes one known-good case, one known-bad case, and one edge case. If the tool catches all three, proceed; if not after two working days, stop. State the stop.
- **Kill criteria written before launch**, so the decision is not made from hope: gate failure, no positive replies in the first batch, positive replies with no sales, recurring revenue that never sells. Each criterion needs a stated batch size and unit or it cannot be read; see Validation gate design below.
- **A parallel test when the real question is which of two businesses to do.** Both run for one window, compare close rate, the winner gets the budget. A sequential choice answers nothing until the first one is finished.
- **Price with a launch tier and a standard tier.** A launch number for the first N sales and the standard number after keeps the option to raise without rewriting page copy. Keep the number in one place.
- **Scope guardrails on the page itself**: per additional unit, and a cap for the full-site version. State them before the first client asks.

## Validation gate design

A gate that reads three variables at once cannot say which one broke, so it gets argued with on sight and it fails as a decision rule. Build it as stages, each reading one variable, each with its own action.

- **Sending health first, before any judgment of the offer.** Bounce rate and spam placement over the first handful of sends. A fresh sending domain can land in spam and produce zero replies behind a perfect offer, so nothing downstream is measurable until deliverability is clean. Failing this stage means fix the sending setup, never the message.
- **Replies next, counted as humans, not as buyers.** Count any reply, including a hostile one: a negative reply still proves the email reached a person and the named defect was legible. Zero replies across a clean batch is a list or deliverability finding, not a price finding.
- **Money last, at a sample big enough to read.** One sale in one batch is noise, so the paid gate sits after two batches, not one.
- **Fulfillment time is its own gate, read only once a job exists.** A slow first job is a template or scope problem and triggers a process fix, never a stop. Folding minutes into the sales gate lets one slow day kill an offer that sells.

State the unit of every batch and never pool units. When the test is per category (per vertical, per channel, per list source), each category is a separate batch with its own denominator, its own single defect type, and its own block in the tracker. Pooling two categories into one running total destroys the only signal the batch buys, and mixing defect types inside one batch turns it into two half-sized tests. Hold the offer constant while the unit changes, and touch the offer only after two or three clean batches all read zero with deliverability confirmed; one weak batch is not evidence about an offer.

Choose the batch size for what it can distinguish, and say so out loud. Thirty sends cannot separate a two percent reply rate from a five percent one, so a zero there is unreadable and a single good reply is luck. State the size, the inspection minutes per prospect, and the total hours before the first send, because a batch that quietly costs two working days per category is a budget decision and belongs to him, not to the plan.

Never write a gate whose failure text guesses at the cause. Where the diagnosis is available for free, make asking it the instruction. Positive replies with no sales is a question for the people who replied, not an inference from a count.

Say in the gate itself what switches and what does not. A gate whose failure reads as "stop the plan" will be read that way, so name the variable that moves (category, wording, price) and the one that stays.

## Judging a test checklist

A lead-path or contact-path plan earns its keep on the silent failures: a form that accepts a submission and confirms nothing, and a form that rejects it with no error. Both cost the owner real inquiries and both are invisible from the outside, so a plan that only checks visible breakage (dead links, untappable phone numbers, broken layout) will find nothing wrong on most sites and cannot justify its fee. Score a checklist by whether it catches those two, then by whether the confirmation reaches the stated inbox including spam.

## Rebuild mechanics

Before writing, restate the request's own noun phrase in one line at the top of your notes and score every section against it. A rebuild that keeps the subject but improves the rigor is the assignment; a rebuild that swaps the subject for a validation plan is the failure the user names as "this was supposed to be about X." Also enumerate the live cron jobs and script headers first, so nothing you recommend already exists.

Write body paragraphs as single unwrapped lines and verify with `awk '{ if (length($0) > m) m = length($0) } END { print m }' file`, because a wrapped document is rejected on sight. Spell-check the whole document before it leaves, using the checker pattern in the `email-sender` skill, and expect it to flag only proper nouns and jargon. When he says email it, send it as a real attachment and verify arrival over IMAP; do not paste the document into the chat.

End the document with the decision he actually asked about, not a summary of what changed. A "what I changed and why" block belongs at the top, three or four sentences, so the reasoning is auditable without reading the whole thing again.
