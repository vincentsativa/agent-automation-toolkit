# Domain-List Contact Harvest

The worked procedure for turning a list of confirmed-defect domains into a staged
contact list. The class of task: the input is domains, the output is addresses printed
by the sites themselves, and the run is long enough that it needs parallel workers and
a completion watcher.

## The collector's rules (keep all of them)

- **Only addresses printed on the page are emitted.** Never guess an address from a
  name pattern. That is the CAN-SPAM line on harvesting by dictionary attack, and it is
  why the output carries a `source_url` for every row.
- **One request per path, a real user agent, a fixed short path list, no crawling**
  beyond the contact paths of the site being checked. Measured: widening the path list
  from 9 to 18 recovered 0 further addresses in 35 attempts. Extra fetching buys
  nothing and only burns time on dead hosts.
- **A role address is used only when no person is named.** The outreach is a personal
  heads up, so a named person is the target; the role address is the fallback.
- **Brand and chain domains are dropped.** A domain in the global top-100k traffic
  list has an IT department, not an owner reading his own email, and a small fixed-fee
  repair does not land there. Measured on a regional list this dropped 30 of 243 rows
  and every one was a chain.
- **Append and flush row by row, and skip inputs already present in the output CSV.**
  Resume is then free: a kill costs nothing, because the next launch continues from
  where it stopped. This is why a long run is low-risk and does not need a checkpoint
  file.

## Run it as parallel workers

```bash
cd <workspace>
split -n l/4 -d --additional-suffix=.txt domains.txt domains_part
pgrep -f "collector.py"          # must be empty first
for i in 1 2 3 4; do
  nohup python3 collector.py --file domains_part$i.txt \
      --out out_part$i.csv --osm-emails local_index.csv >> part$i.log 2>&1 &
done
```

Then watch it to completion using
`references/background-job-completion-monitoring.md` (poll by process name, sum the
row count across the part glob, stall cap, syntax-check the watcher).

## Merge the parts; never trust a concatenation

```python
import csv, glob
FIELDS = ['domain', 'email', 'person', 'kind', 'source_url', 'note']
ORDER  = {'person': 0, 'role': 1, 'osm': 2, 'none': 3}

seen = {}
for f in sorted(glob.glob('out_part*.csv')):
    with open(f) as fh:
        for row in csv.DictReader(fh):
            key = row['domain'].strip().lower()
            if key in seen:            # first writer wins; parts overlap
                continue
            seen[key] = {k: row.get(k, '') for k in FIELDS}

rows = sorted(seen.values(), key=lambda r: (ORDER.get(r['kind'], 9), r['domain']))
with open('contacts_final.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)
```

Verify three things against the artifact before reporting:

- merged row count equals the **unique** input count (every input accounted for, none
  missing, none duplicated);
- every non-empty address matches a basic mailbox regex (no truncated or malformed
  strings);
- unique address count is reported separately from the row count in case two rows
  resolve to the same mailbox.

## Measured yield, use it to size the next list

Input list of 1,652 domains, all already confirmed to carry a mail defect:

| Outcome | Count | Share |
|---|---|---|
| Named person | 104 | 6.3% |
| Role address | 240 | 14.5% |
| Local-dataset tag address | 302 | 18.3% |
| Any usable address | 646 | 39.1% |
| No address printed anywhere | 1,006 | 60.9% |

Wall time: about 54 minutes on four workers; the same list on one process wrote 21
rows in 6 minutes. Excess rows from overlapping runs: 84, from 21 domains processed
twice.

Two sizing consequences:

- Roughly **16 domains per named contact**. A named-contact target of 500 is a
  ~8,000-domain input list.
- Report the reachable count, never the input count, as the number of contacts.

## After the harvest

The harvest output is not the send list. The brand/chain filter, dedupe, and any
validation stage run on top of it before a number is quoted as stageable. Check
whether that stage has already produced a downstream CSV, and if it has, quote its
count as the answer, naming what it dropped and why.

## Counting questions are system questions

"How many do we have," "is that everything," and "what did that last scrape add" are
completeness questions. Enumerate the whole artifact and answer with arithmetic, in the
same turn:

- addresses harvested, after dedupe, and by kind;
- the same set restricted to addresses never present in the previous run's files, when
the question is what was added, computed as a set difference against every earlier
contact and send file, not by eye;
- the post-filter stageable count.

Never answer a count question from a partial look, and never answer it from memory of
the run. Read the CSVs and compute.
