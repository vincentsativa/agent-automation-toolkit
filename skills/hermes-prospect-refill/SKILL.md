---
name: prospect-refill
description: >-
  Top up the cold-outreach prospect pool when it runs low (below 100 sendable
  person addresses). Use when the "PROSPECT POOL REFILL" cron says REFILL
  NEEDED, or when Vinny says "refill the prospects", "top up the pool", "get
  more leads", "we're running out of contacts". The pipeline scripts and hard
  rules live in email-deliverability-rescue-workflow; this is the refill runbook.
trigger: Prospect pool below threshold / "refill the prospects" / cron says REFILL NEEDED.
---

# Prospect pool refill (WSL, `~/money_ideas/`)

The daily job draws sendable **person** addresses from `contacts_master.csv` +
`scan_master.csv`. Refill when the clean sendable count drops **below 100**.

**Threshold was 200 until 2026-10-11.** It came down with the buyer channel's
rate: the buyer side was throttled 100 -> 30 staged/day so the agency/partner
channel could take the volume (see `hermes-outreach-cron` and the partner plan of
record). At 30/day a 200 threshold fired this heavy refill every single night;
100 sendable is roughly three days of buffer. `refill_check.sh` defaults to 100
too, so the cron and this runbook agree.

**This is the heavy half.** The "PROSPECT POOL REFILL" cron runs
`refill_check.sh` (cheap) and only when it prints `REFILL NEEDED` do you run the
four steps below. The full pipeline reference (measured yields, flags, hard rules)
is `email-deliverability-rescue-workflow` — read it if a step is unclear, and do
not duplicate its rules here.

## Step 0 - confirm

**Every python command below runs as `$PY`, never bare `python3`** (2026-10-30).
Set it once in the same shell:
```bash
PY=/usr/bin/python3
```
The cron environment resolves bare `python3` to the Hermes-managed Python 3.14,
which has no `requests`, so every script that imports the pipeline died at
import. That is what made `refill_check.sh` report a stale count for eight
nights and let the pool drain to 10. `/usr/bin/python3` imports the whole chain.

```bash
cd ~/money_ideas
REFILL_AT=100 bash ~/.hermes/scripts/refill_check.sh    # prints the current sendable count
```
Proceed only on `REFILL NEEDED`.

## Step 1 - SOURCE new domains (OpenStreetMap Overpass; free; terms permit it)
```bash
ONLY="$(grep -v '^#' TARGET_INDUSTRIES.txt | grep -v '^$' | tr '\n' ',' | sed 's/,$//')"
"$PY" osm_industry_prospects.py --out "prospects_refill_$(date +%F).csv" \
    --metros osm_metros.txt --only-industries "$ONLY" --max-domains 2000
NEW="prospects_refill_$(date +%F).csv"
cut -d, -f1 "$NEW" | tail -n +2 | sort -u > "domains_refill_$(date +%F).txt"
wc -l "domains_refill_$(date +%F).txt"
```
Use fresh metros not already in `ALREADY_SCANNED_FILES` (workflow skill, sourcing section).

> **GetLeadSnap (evaluated 2026-09-30, NOT usable - do not wire it in):**
> `getleadsnap.pro` free packs were downloaded and checked. For every
> local-service industry the "website" column is a `bbb.org` profile link,
> not the business's own site, and the email column is empty. Only the
> agency/software packs carry a real domain, and those are not our buyers.
> The adapter `getleadsnap_source.py` exists but rejects aggregator hosts and
> yields ~0 usable domains. OpenStreetMap Overpass remains the only domain
> source. If a future pack carries real domains, the adapter is ready.

## Step 2 - SCAN, then write the qualified list from the scanner's own column
```bash
DAY="$(date +%F)"
"$PY" email_scan.py --file "domains_refill_${DAY}.txt" --csv "scan_refill_${DAY}.csv" --resume
"$PY" - "scan_refill_${DAY}.csv" "qualified_refill_${DAY}.txt" <<'PY'
import csv, sys
src, out = sys.argv[1], sys.argv[2]
doms = [r["domain"] for r in csv.DictReader(open(src))
        if (r.get("qualified") or "").strip().lower() == "yes"]
open(out, "w").write("\n".join(doms) + ("\n" if doms else ""))
print(len(doms), "qualified")
PY
```

## Step 3 - HARVEST contacts (parallel; auto-loads the OSM email sidecar)
```bash
./harvest.sh --file "qualified_refill_${DAY}.txt" --out "contacts_refill_${DAY}" --workers 4
```

## Step 4 - MERGE into the master pool, then re-clean
```bash
DAY="$(date +%F)"
tail -n +2 "contacts_refill_${DAY}_final.csv" >> contacts_master.csv
tail -n +2 "scan_refill_${DAY}.csv"           >> scan_master.csv
"$PY" clean_prospects.py --contacts contacts_master.csv --scan scan_master.csv \
        --state state.json --out prospects_master
```
`clean_prospects.py` dedupes on domain AND address, so the append is safe. The
ROLE RULE drops every role box automatically; never re-add one.

## Step 5 - verify and report
```bash
REFILL_AT=100 bash ~/.hermes/scripts/refill_check.sh
```
Must now print `POOL HEALTHY`. If still below 100, repeat Steps 1-4 with a fresh
metro. Then report in two or three lines: new sendable count, batch size, any failure.

## Hard rules (from the workflow skill - do not violate)
- Never mail a role box; the cleaner enforces it. Never pass `--allow-role` on a real run.
- Never sum two batches; the cleaner's dedupe IS the union.
- Run inside WSL, LF endings. Prove by reading a fresh run's output, never a remembered count.
