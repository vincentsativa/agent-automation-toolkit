# Send cadence, list economics, and the three buckets

## The cadence is a deliberate warm-up, not a ceiling

The ramp is 20/day, then 50/day, then 100/day, then a climb toward 500/day over
weeks, with weekends off for a cooldown. Each step doubles and holds for a week
so the receiving side has a read on the sender before the next step.

- Read the send history as his strategy, never as a limit imposed from outside.
- Do the arithmetic before raising any volume or reputation concern. At 100/day,
one send every two minutes is 30/hour, about 6 percent of the IONOS 500/hour
allowance for a domain past 30 days old. Account age alone also is not the
signal; the cadence is.
- Weekends are off. Weekday mornings are the send window.

## Runway and refill arithmetic (5-day sending week)

Contacts on hand: 605 unique. Measured yield: 39.1 percent of qualified domains
carry an address, 82.6 percent of sourced sites carry a defect.

| Rate | Per week | Runway at 605 |
|---|---|---|
| 20/day | 100 | 6.0 weeks |
| 50/day | 250 | 2.4 weeks |
| 100/day | 500 | 1.2 weeks |
| 500/day | 2,500 | 0.2 weeks |

Refill: 100/day needs 500 contacts a week, about **1,279 qualified domains or
1,550 sites scanned**. 500/day needs 2,500 contacts, about **6,394 qualified
domains or 7,741 sites**. Harvest throughput is measured at 1,852 domains/hour
on four workers, so refill volume is hours of machine time and never the
constraint.

**The real constraint is that a domain is contacted once, ever.** So refill
volume is brand-new uncontacted domains, and the pipeline cannot be fed from
anything already contacted. That is a sourcing question, not a throughput one.
Vinny's answer stands: the pool is the internet, not the batches run so far,
so it is a question of how fast he chooses to build out.

## Never sum two batches without measuring the overlap

Measured failure: one build produced 305 send-ready, the next produced 547, and
the report stated 852 in total. **247 addresses appeared in both files**, so the
true unique pool was **605**. An overstatement of 247 on a 605-row list is a 41
percent error.

- Dedupe the two files on the address, lowercased, and report the union.
- Treat any "X plus Y" total as unverified until the overlap is measured.
- Run the check before stating the number, not after publishing it.

## Three buckets that share one history but are not one list

`state.json` / `outreach_log.csv` feed three different purposes, and merging
them breaks whichever one is not being served.

1. **Already contacted** - the permanent dedupe that stops any second send.
Reset would mean mailing a stranger twice.
2. **Law-required suppression** - a reply saying stop is entered immediately and
never resets for any offer, ever. This is the statutory list.
3. **The contacted set as an asset** - the businesses found, with the defect
found, kept for a later different offer or for resale. Its value is entirely in
row completeness.

## The distinct send-ready total, three batches in (2026-09-27)

Do not add the batch figures. The batches overlap, so the sum overstates the list:

| Set | Domains |
|---|---|
| Batch 1 (2026-09-24) | 305 |
| Batch 2 (2026-09-26) | 547 |
| Batch 3 (2026-09-27) | 570 |
| Batch 1 and batch 2 shared | 247 |
| Batch 3 shared with either | 0 |
| Union of all three | 1,175 |
| Less the contact history | 1,125 distinct send-ready addresses |

The arithmetic to run: union the three send-ready CSVs keyed on domain AND address, then drop every row whose domain, apex, or address is in `state.json`'s `contacted` set. Report that one number. The 852 quoted for the first two batches was the sum, and the real figure for those two was 605.

Measured gaps in the current `state.json` that would block bucket 3 today: of
408 entries, 267 are `sent`, **121 are `scheduled` and 20 are `draft`** - those
141 are not sent at all - and some `sent` rows carry an empty `email`. Never
present that count as a contacted list without splitting it by status first.

A hard opt-out and a contacted-this-offer row are not the same thing. If they
are ever collapsed into one bucket, the accidental re-mail lands on exactly the
person most likely to report it.
