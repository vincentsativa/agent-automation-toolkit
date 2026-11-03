# Contact priority and the role rule

## The rule (Vinny, 2026-09-29): a shared role mailbox is NEVER mailed

`outreach.py` drops every role-shaped address before the dedupe on every run. A
role shape is decided by `find_contacts.address_shape`, which reads the local
part (`info@`, `sales@`, `service@`, `office@`, `hello@`, `contact@`, `support@`,
`admin@`, `billing@`, `noreply@`, `webmaster@`, `marketing@`, ...). It is a rule,
not a flag.

Consequence: the old send order is retired, because it ranked boxes that are now
dropped before anything composes.

- The `HELLO_AND_INFO` tier (`hello@`, `contact@`, `contactus@`, `office@`,
  `info@`, `enquiries@`, `team@`, `general@`) is dead: every one is a role shape
  and is dropped.
- Tier `C` (`sales@`, `support@`, `customerservice@`, ...) is dead for the same
  reason.
- What remains is `A` (person-shaped matching the printed name) and `B`
  (person-shaped, no name). Only those are sendable.

`--allow-role` is the sole override and exists for tests. `--person-only` is a
deprecated no-op: dropping role mailboxes is the default now.

## Why the rule replaced the old greeting-first order

The old design sent `info@`/`office@` first on the theory that a broken-records
small business does not mind its greeting inbox, so `info@` reaches the owner.
That is retired. On 2026-09-29 Vinny made "never mail a role box" the rule, after
a `service@` bounce in the run. A role mailbox is not where this offer is
decided, and a function box is a desk, not the owner.

Do not re-rank it back. Do not re-introduce a greeting tier.

## What still ranks, and how (A before B)

`find_contacts.prospect_tier` still returns a tier; the send path keeps only
person shapes, so the live ordering is `A` before `B`. Sort by explicit rank,
never by the tier string:

```python
TIER_RANK = {"A": 0, "B": 1, "HELLO_AND_INFO": 2, "C": 3, "": 9}
rows.sort(key=lambda r: TIER_RANK.get(tier_of(r), 9))
```

Verify by printing the ordered list and reading it, never by reading the sort
expression.

## Pitfall: a stem test is what catches the compound recruiting desk

`prospect_fit.is_target` drops function mailboxes by exact match and by the text
before the first separator. That misses the compound form, because splitting
`hrrecruiting` on separators leaves the whole string intact, so the desk sails
through classified as a person. Match the stems `career`, `recruit`, and
`employment` as SUBSTRINGS instead. The three never occur inside a person's name,
which is what keeps the substring test from deleting a real owner.

`media@` and `press@` stay KEPT by the fit filter; the role rule above drops them
anyway when they are a clear role shape.

## Re-ranking an existing list

The harvest writes one row per domain with `kind` and `person`; the tier is
computed from the ROW, so a ranking change never requires re-harvesting. Re-run
the tier pass over the existing CSV and rewrite the write-list.

```python
import find_contacts as fc, prospect_fit as pf
RANK = {"A": 0, "B": 1, "HELLO_AND_INFO": 2, "C": 3, "": 9}
ranks = pf.load_tranco("tranco_top1m.tsv")
kept = [r for r in rows if pf.is_target(r["domain"], r["email"], ranks)[0]]
```
