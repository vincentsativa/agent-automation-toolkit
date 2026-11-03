# Outreach volume, the warm-up ramp, and list lifecycle

## The send ramp is deliberate, and never call it a quota limit

The plan is 20/day, then 50/day, then 100/day, then a climb toward 500/day over
weeks. That progression is a domain warm-up, not a workaround for a host limit.

**Account age is not sending history.** A mailbox that is months old but has
only been sending for a week still has almost no reputation, so the age of the
account says nothing about what volume is safe. Read the CADENCE for the
strategy and never report the ramp as a constraint the user is stuck under. When
a doubling ladder is visible in the send history, that is a warm-up pattern.

Each step doubles and holds roughly a week, which gives the receiving side a
history to read before the next step. A jump to a higher volume belongs in weeks,
not days.

## The host limit is nowhere near the plan

IONOS Mail Basic and Mail Business, for domains over 30 days old: 500 emails per
hour. The younger bands are lower (400 at 15 to 30 days, 100 at 8 to 14, 50 at 0
to 7), but past 30 days the allowance is flat at 500/hour.

One email every two minutes is 30/hour, which is **6 percent** of the 500/hour
allowance, and 100 sends take about 3.3 hours. Even 500 a day stays under it.
So the host quota is a non-issue at every volume being planned, and raising it as
a risk is inventing a problem.

## Weekends are off, and that is two good decisions at once

No sends Saturday or Sunday. Cold mail that lands Saturday morning sits under
Sunday's mail by Monday and reads as automated. A five-day cadence that pauses is
also a cooldown a seven-day heartbeat never gives you.

All runway arithmetic uses a **five-day week**, never seven. A rate quoted per
calendar week overstates consumption by 40 percent.

## What protects the reputation (all already built)

- **One email per address, ever.** The permanent dedupe is what stops escalation.
  Multiple reports from the SAME address are what actually moves a reputation;
  a single complaint from one person is noise. Because an address is mailed once,
  it can report once at most, which makes the escalation path structurally
  impossible.
- **Never ask permission to do a thing already ordered, and never hand back a menu.** When the user orders a fix, fix it, test it, and report only what real output proved. Presenting options on an order reads as stalling.
- **State a number only from a run or a computed script; never from mental arithmetic.** Recompute every quoted figure in code, especially percentages, runway, and totals.
- **When a fix is ordered, apply it in the same turn and verify it with real output.** Diagnosis alone is not the deliverable.
- Addresses come only from what the business published itself. No name-pattern
  guessing, which is the dictionary-attack line in 15 USC 7704(b)(1)(A).
- Every message carries the opt-out line and a `List-Unsubscribe` header.
- Real SPF, DKIM, and DMARC on the sending domain.
- The mail states a true finding about the recipient's own mail records, so it is
  a diagnosis rather than a blast.

## Compliance is the default, not a checklist item

Standing instruction: **always assume what we do MUST be compliant.** Hold every
part of the pipeline to that bar, the sourcing method, the message content, the
opt-out, how the list is stored, and what happens if the list is ever sold.
Raise a compliance problem BEFORE something ships, never after. The user has
been in email since before CAN-SPAM and knows the mechanics; the value added is
checking the bookkeeping and the fields, not re-explaining the principle.

## Two different lists that must not be merged

- **The suppression list.** People who unsubscribed or asked to stop. This is the
  law-required do-not-send, it is permanent, and it never resets for any offer.
- **The contacted history.** Every domain already mailed. This is the dedupe that
  stops a double send, and the user's stated intent is that it can reset after
  enough time or for a different offer.

Merging them is the failure: the accidental re-mail then lands on exactly the
person most likely to report, and the record stops being sellable because
"contacted" and "opted out" are no longer distinguishable.

**The contacted list is also an asset, not just a cost.** It is a set of
businesses with a confirmed mail defect, which is pre-qualified market
intelligence for any later mail-adjacent offer, and the user intends to sell it.
A list is only worth something if every row is complete, so field accuracy is
the thing that decides its value: real address, real domain, industry, metro, the
defect found, and a trustworthy contacted date.

**Known gap to close before that list is a product.** As of the 2,000-domain
build, `state.json` holds one bucket: statuses are `sent`, `scheduled`, and
`draft` only, with no opt-out, bounce, or do-not-contact status anywhere, and
some `sent` rows carry an empty email field. So a raw "contacted" count
overstates what was actually sent, because `scheduled` and `draft` rows are not
sends. Fix the statuses before quoting the list as a deliverable.

## Never total batches without checking the overlap

Batches harvested from overlapping geographies or industries share addresses, so
a naive sum double-counts and overstates the pool.

Measured: 305 plus 547 looked like 852, but **247 addresses appeared in both**,
making the true unique total **605**. That is a 40 percent overstatement, and it
was reported in a delivered summary before it was caught.

Compute it as a **set union on the lowercased email column across every
send-ready file**, and report the union, never the sum. When a total in an
already-delivered report is wrong, correct it explicitly so the wrong number
does not keep circulating.

## Sizing: what the volume needs and what it produces

**Contacts are consumable.** A contacted domain is spent for that offer, so
runway counts only UNCONTACTED addresses. State the runway as weeks of sending,
not as a raw contact count.

Measured yield, which every calculation rests on: **39.1 percent** of qualified
domains carry an address, and **6.3 percent** carry a named person, one per 16
domains.

Refill, per five-day sending week:

| Send rate | Sends/week | Qualified domains | Sites to scan |
|---|---|---|---|
| 100/day | 500 | 1,279 | 1,548 |
| 500/day | 2,500 | 6,394 | 7,741 |

At 100 a day a fresh build roughly the size of an existing batch lasts about a
week, which is why sourcing must stay ahead of the send cadence. Running dry
mid-ramp breaks the very cadence the warm-up is building.

**Throughput is not the constraint, sourcing is.** Measured harvest rate on four
workers: **1,852 domains per hour**. The send side at 500 a day consumes about
7,741 sites a week, which is roughly 4.2 hours of harvesting. Eight hours a day
would produce about 10x more supply than the send side can absorb. So the
machine and the harvest guards are never what limits the plan, the supply of
fresh uncontacted domains is.

Two real ceilings to name when this comes up:

- **The public Overpass endpoint throttles first.** It returns 429 and 504 under
  repeated or parallel sourcing, which is what fails before any CPU limit does.
  A local regional extract, or a self-hosted query layer, is the fix that makes
  high-volume sourcing real rather than theoretical.
- **Raising worker count returns less than the multiple suggests.** The harvest
  is network-bound, spending its time on 15-second timeouts from dead hosts, so
  going from four workers to sixteen is not 4x. The wire and the remote hosts are
  the limit, not the cores. The measured 4x came from the first split, one
  process to four.

## The target math

One sale per week is **the floor, not the goal**. At 500 a day and a five-day
week, 2,500 sends at a 1 percent reply rate is 25 replies, so closing one sale
needs only a 4 percent close rate; at a 2 percent reply rate, only 2 percent. At
2 percent reply and 10 percent close it is 5 sales a week. If a week lands one
sale, that is a signal to diagnose the copy, the subject line, or the targeting,
not that the model is broken.

**Tweak the copy against real reply data, and never change the whole message as
one blob.** Track reply rate PER SUBJECT LINE. Run at 100/day first so a bad
subject line costs a week of sends rather than a month at 500, make the changes
against measured replies, then climb. Scaling to 500 before measuring scales
whatever is weak along with what works.
