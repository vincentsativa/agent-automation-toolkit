# List cleaning and harvest speed (2026-09-29)

## clean_prospects.py - build the sendable list from a harvest

New one-pass cleaner. Applies the SAME rules the send path enforces, so the
stored list and the send list stop disagreeing:

```
cd ~/money_ideas
python3 clean_prospects.py --contacts contacts_<batch>_final.csv \
        --scan scan_<batch>_results.csv --state state.json --out prospects_<batch>
```

Order: no-address -> scan-qualified -> ROLE RULE (drop every role shape) ->
suppressed/dead -> already-contacted (domain OR address) -> buyer-fit -> dedupe
(domain AND address). Writes `prospects_<batch>_clean.csv` (sendable) and
`prospects_<batch>_dropped.csv` (domain,email,reason). Idempotent; re-run any
time the harvest grows. Nothing is sent, nothing is edited in place.

Measured on the union of every batch so far (`contacts_master.csv`, 2,942 rows):
**577 sendable person addresses**, 2,364 dropped - 1,093 no address, 1,006 role,
149 not qualified, 54 not buyer, 47 already contacted, 12 duplicate, 3 suppressed.
Because the role rule removes every role box, the sendable list is person-shaped
only; that is the number that caps the daily send.

## Harvest speed: a short connect timeout

`find_contacts.py` now uses a `(connect, read)` timeout tuple, connect **5s**,
read **12s** (was a flat 15s). Dead small-business hosts were the single biggest
time sink, and a host that has not opened a socket in 5s is not the one that pays
off. Retries are on READ/status only, never connect, so a dead host fails fast
instead of being retried. Connections are pooled. No change on live sites.

## Async harvest option (find_contacts.py --workers N)

`find_contacts.py --workers N` harvests with N threads (thread-local requests
sessions), default 1 = the proven single-threaded order. It stacks with
`harvest.sh --workers 4` (4 processes x N threads), so raise it deliberately:
prove it on a known list first, and watch for a host rate-limiting. The
single-threaded default is unchanged.

## Role detection now catches fused / plural role boxes (2026-09-29)

`address_shape()` matched a role word only as a PREFIX followed by a separator, so
fused forms (`bawinfo@`, `dudainfo@`, `churchadmin@`), plurals (`teams@`,
`socials@`), and compounds (`clientsupport@`, `marketingteam@`, `contactus@`)
were classified person-shaped and mailed. It now also matches a role word as an
exact token, a plural token, or the END of a token, using only role words of
length >= 4 so a real name is never dropped on a fragment (`chris@` contains
"hr" but does not end in it, so it stays a person). Effect on the master clean:
role drops 1,006 -> 1,045, sendable 577 -> 547. `test_outreach.py` still 153 / 0.
