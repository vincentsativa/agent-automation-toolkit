# Industry-classified prospect collection (added 2026-09-24)

## The tool

`osm_industry_prospects.py` in `~/money_ideas/`. Same Overpass
sourcing route as `osm_prospects.py` (ODbL 1.0, one public API, no key), with
two differences:

- It keeps each element's tags, so every domain carries the industry Vinny
  named. `industry_source` records which rule fired, `tag:craft=electrician`
  or `name-pattern`, so the list never implies a tag classification it does
  not have.
- It screens out every domain named in `ALREADY_SCANNED_FILES` (plus each
  apex), so a new batch never re-scans or re-mails anyone worked before. Add
  each new batch's output files to that list as you go.

It appends with flush plus fsync and resumes from its own output.

```
python3 osm_industry_prospects.py --out prospects_1000_industry.csv \
    --metros osm_metros.txt --max-domains 1000
```

`osm_metros.txt` is `name|south,west,north,east`, one metro per line, ordered
by expected yield.

## Measured, 2026-09-24

- 1,000 domains from three metros: Orlando 158, Jacksonville 219, Miami 623.
  Roughly 1,000 kept out of 13,943 elements carrying a website or email tag.
- Per-industry split came back heavily weighted to ecommerce_retail, 424 of
  1,000, because OSM tags far more shops than agencies or MSPs. Read a thin
  industry bucket as OSM tag coverage, not as a shortfall in the market.
- Tampa returned HTTP 504 from Overpass while the other metros returned. The
  runner logs the failure and moves on rather than dying, so retry a failed
  metro in a later run instead of treating it as a dead source.
- Scan: 805 of 1,000 qualified, an 80.5 percent defect rate, consistent with
  the 81 percent the skill already records.
- Contact harvest: 334 reachable addresses from 805 qualified domains, so
  41.5 percent, at the top of the range the skill records for a batch carrying
  OSM addresses. Broken out: 161 osm, 125 role, 48 person.
- Buyer-fit filter dropped 29 of 334 reachable rows.
- Send-ready total: 305.

## Run the contact harvest in parallel chunks

`find_contacts.py` is single-threaded and was walking about 85 seconds a
domain on dead and slow small-business hosts, which is close to 20 hours for
805 domains. Split the todo list into six files and run six processes:

```
for i in 0 1 2 3 4 5; do
  nohup python3 find_contacts.py --file "$CH/part$i.txt" --out "$CH/out$i.csv" \
      --osm-emails osm_emails_1000.csv > "$CH/log$i.txt" 2>&1 &
done
```

Then merge by domain keeping the first row seen per domain. That turns a day
into about an hour.

**Do not stop one with `pkill -f find_contacts`.** The pattern matches the
calling shell and kills the session. Kill by PID from
`pgrep -f "find_contacts.py --file"`.

## Pre-send verification that was run

- `test_email_scan.py`: 63 passed, 0 failed, against live DNS.
- `test_outreach.py` with the mail env sourced: 133 passed, 0 failed.
- All 305 rows rendered through the real `build_message`: 305 of 305 clean, no
  literal braces, no em or en dashes, no spaced hyphens, the prospect's own
  domain named in the body, no duplicated subject line.
- Offer page `https://phantom-byte.com/email-deliverability-rescue` returned
  HTTP 200.

## Files this produced

- `send_ready_1000.csv` and `send_ready_1000_emails.txt`: the 305.
- `scan_1000_industry_results.csv`: all 1,000 scans.
- `prospects_1000_industry.csv`: the 1,000, industry classified.
- `contacts_1000.csv`: the contact harvest.
- `PROSPECT_BUILD_REPORT_2026-09-24.txt`: the report emailed to Vinny.
