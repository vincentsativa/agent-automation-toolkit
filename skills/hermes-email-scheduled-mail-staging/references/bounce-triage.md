# Bounce Triage for Cold Outreach

Use when Vinny asks why a share of a cold send did not go out. The answer comes from the account's own INBOX, not from the sending script, because the sending script only knows what it handed to the provider.

## Read the failure notices over IMAP

The account is the ground truth. Log in to the same address the mail went out from, select `INBOX`, list `ALL`, and filter in Python on the subject. Failure notices arrive one per dead message, so the count of matching subjects IS the failure count.

Two subject families cover almost everything: the provider's own "mail delivery failed" notice, and an upstream "Delivery Status Notification (Failure)" relayed back. Search for both, or you will undercount. Filtering on subject alone is fragile because providers change subject text, so treat the subject as a prefilter and confirm each hit by reading the body.

Fetch bodies with `BODY.PEEK[]` and parse with the `email` module. Only the body carries the failing address and the reason; the subject is identical for every one of them.

## Two parsing traps that silently undercount

**A permanent failure is not always coded `550`.** Providers relay real, undeliverable notices whose body reads "multiple delivery attempts failed" or "Relay access denied" with no SMTP status anywhere, and an upstream admin can block a message for "a delivery loop was detected" with no code at all. A classifier that only greps for `55[0136]` finds well under half the real bounces and reports a comfortable number, which is worse than finding none because it reads as a clean bill of health. Classify on the CODE **or** on the prose, and treat the notices only the prose path finds as the check on the code path: if the two counts disagree, the classifier is wrong, not the mailbox.

**Cut the original-message block before extracting any address.** Providers append the full headers of the message that was sent, including its real `From` and `Reply-To`. A regex that sweeps the whole body for addresses therefore finds the sending account's own address as a failed recipient, and a suppression list built that way suppresses the sender. Truncate the body at the original-message delimiter before pulling addresses out of it.

## Classify before diagnosing

Every notice is one of four things, and they call for different responses:

- `550 5.1.1` / "user doesn't exist" / "address not found" — hard bounce, the mailbox does not exist.
- "delivery loop detected" / "Message blocked" — the address is real but the mail never reaches a human. Treat as hard.
- "the group you tried to contact may not exist" — the address is a distribution list or Google Group, not a person. Treat as hard, and exclude group addresses from the candidate pool.
- 4xx, greylist, mailbox full, rate limit — soft. Retry later, do not count against the sender.

**A hard-bounce cluster that is all `info@`, `contact@`, or `hello@` is a list-verification problem, not a deliverability problem.** Those are the three conventional role guesses, and if that is the shape of the failures, the addresses were guessed rather than verified. Say so, because the fix belongs before the send, not in the sending settings.

Never diagnose a bounce rate without the soft/hard split. A 12% failure count that is all soft is a non-event, and the same 12% that is all hard will get the domain throttled.

## Turn the triage into a fix, not just a report

Diagnosis alone leaves the next batch to repeat itself. The durable repair is a suppression list: harvest the failed addresses out of the notices, append them one per line to a file the sending pipeline reads before it composes, and never re-mail a listed address. Two rules make that list trustworthy.

- **Append, never rewrite.** A crash mid-run must not be able to truncate a list that already exists, and a repeated address must not produce a second line. Check membership before writing.
- **Seed it by hand from a verified read of the inbox before trusting the harvester.** A classifier bug then cannot empty the protection: the known-dead addresses are already listed, and the harvester only has to catch the next batch.

The pre-send check worth building is the one you can actually prove runs. Probe a known-good live address and at least one known-dead one before wiring any verifier into the send path. A verifier whose network path is silently dead returns UNKNOWN for everything and still prints a clean summary, which is worse than having no check at all. If a check cannot be shown to return a positive result, do not ship it as a gate.

## The check that changes the diagnosis

A bounce rate is only alarming relative to the volume behind it. Count the sent folder over the same window. Sent 105, delivered 92, and every failure hard, is a healthy sender reputation with a weak list. A 12% rate on 20 sends is noise.

Always report sender reputation alongside the bounce rate: no throttling notices, no blocklist warnings, and no complaints in the Sent/Spam pair means the sending configuration is fine and the list is the defect. That distinction is what stops the wrong fix being applied to the sending path.

## Cross-check the queue while you are in there

A bounce audit is also the cheapest moment to confirm the scheduled folder is healthy. Select `Scheduled`, read the `X-OX-Date-To-Send` header off each message, and check the `From` identity is present. See Rule 2 and Rule 8 in SKILL.md: a queued message with no `From` dies silently at its send slot and generates a bounce notice indistinguishable from a bad address.
