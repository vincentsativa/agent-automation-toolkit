# Scaling the bulk prospect build (2,000-domain batch, 2026-09-26)

Measured on the 2,000-website request across nine industries. Use these numbers to size a run instead of projecting.

## Parallelize the contact harvest when the batch is in the thousands

A single `find_contacts.py` process harvests about 25 to 30 domains a minute, so 1,652 qualified domains is roughly an hour of wall clock. Split the qualified list into 4 equal parts and run one harvester per part:

```
find_contacts.py --file qualified_<batch>_partN.txt --out contacts_<batch>_partN.csv --osm-emails osm_emails_<batch>.csv
```

- Four processes finished 1,652 domains in about 50 minutes. No rate limiting from the sites touched.
- Seed every part file with the same existing contacts CSV if one exists, so the resume logic skips what is already done.
- **Always pass `--osm-emails`.** OSM tags hand over a published address with no page fetch. On this run 354 domains carried an OSM email, 306 of them qualified, and 261 of the final 547 addresses came from the tag rather than a page. One API call replaces nine page fetches per domain.
- Reassemble the parts with `prospect_fit.is_target` and `find_contacts.prospect_tier` applied in one pass, then dedupe against `state.json`'s `contacted` dict by domain, apex, AND address.

## Measured rates

| Stage | Number |
|---|---|
| Domains sourced (7 metros) | 2,000 |
| Qualified, confirmed defect | 1,652 (82.6 percent) |
| Reachable addresses | 642 |
| Dropped, not a buyer (fit filter) | 49 |
| Dropped, already contacted | 50 |
| Final send-ready | 547 |

Defect mix across the qualified set: DMARC_MISSING 909, SPF_SOFTFAIL 694, DMARC_P_NONE 499, SPF_MISSING 466, DMARC_NO_REPORTING 373, SPF_ALL_OPEN 31, SPF_OVER_LIMIT 30, NULL_MX 12, SPF_NO_ALL 2, SPF_VOID_LIMIT 1.

Sourcing yield: Tampa 398, Orlando 157, Jacksonville 188, Miami 706, Fort Lauderdale 269, West Palm Beach 214, Atlanta 68 (the batch closed at 2,000 mid-Atlanta). OSM tag classification fired on 1,587 rows, the name-pattern fallback on 413.

## Report the counts as separate sentences

A report that says "547 ready" and a report that says "642 reachable, 547 ready after the buyer filter and the contact-history dedupe" are different documents. Say which number is which, and never let a reachable count stand in for a sendable one.

## Batch 3, 2026-09-27 (the second 2,000, four new metros)

Metros: Charlotte, Raleigh, Nashville, Dallas. Measured rates: 2,000 sourced, 1,725 qualified (86.3 percent), 629 reachable, 57 dropped by the buyer-fit filter, 570 final send-ready. Defect mix: DMARC_MISSING 980, SPF_SOFTFAIL 694, SPF_MISSING 546, DMARC_P_NONE 521, DMARC_NO_REPORTING 392, SPF_ALL_OPEN 32, SPF_OVER_LIMIT 29, NULL_MX 10, SPF_NO_ALL 5. Address sources of the reachable set: 252 OSM, 270 role, 107 person.

- **`ALREADY_SCANNED_FILES` must gain each batch's OUTPUT files, not just its input lists.** After the 1,000- and 2,000-domain builds the only new files listed were input lists, which are far smaller than the batch's own prospect CSV: `prospects_1000_industry.csv` and `prospects_2000_industry.csv` together held 970 of the 1,000 batch's domains. A third run over the same metros would have re-sourced and re-mailed those people. A fresh metro list is a weaker guard than the file list, because the next batch may reuse a metro. Add the batch's prospect CSV, its domain text file, its qualified list, and its send-ready CSVs the moment the batch finishes.
- **Never add two batches together to report a total.** Batch 1 (305) and batch 2 (547) shared 247 addresses, so the pair is 605 distinct, not 852, and a previous report said 852. Compute the union on domain AND address, subtract the contact history, and only then quote a number. The three batches together are 1,125 distinct send-ready addresses; batch 3 shared zero with either earlier batch.
- **`email_scan.py` is single-threaded; split the domain list into 4 parts and run one scan per part**, the same way the harvest is split. 2,000 domains finished in about 8 minutes wall clock with four workers.
- **One address can appear on two domains.** This batch produced `maynard_crossing@att.primecomms.com` on both `att.primecomms.com` and `primecomms.com`, and a carrier store is not a buyer. Keep a hand filter for carrier and franchise-service domains that the Tranco blocklist and the fit filter both pass.

## Run order that worked

1. `test_email_scan.py` first, read the pass/fail out of the run (63 passed, 0 failed here).
2. `osm_industry_prospects.py --max-domains 2000` to source and classify.
3. `email_scan.py --resume` over the domain list.
4. Split qualified into 4, harvest in parallel with `--osm-emails`.
5. Reassemble, fit-filter, dedupe against history, write the final list and report.
