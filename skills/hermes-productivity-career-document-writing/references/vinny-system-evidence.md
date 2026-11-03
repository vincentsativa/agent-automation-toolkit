# Verifiable Evidence Inventory (re-run before every use)

Numbers drift. Every figure below carries the command that produces it. Run the command, use the live output, and discard the number in this file — it is a starting point, not a source. A resume claim that cannot be reproduced by one of these queries does not go in the document.

## Automation fleet (scheduled jobs running unattended)

```bash
python3 -c "import json;d=json.load(open('~/cron/jobs.json'));print(len(d['jobs']))"
python3 -c "import json;d=json.load(open('~/cron/jobs.json'));[print(j['name'],'|',j['schedule'].get('expr')) for j in d['jobs']]"
```

Proves the job count and lets you name the categories honestly: research collection, article generation, outline selection, social publishing, inbound email processing, backup, health monitoring. Count the enabled ones separately if asked for "running" versus "configured."

## The script-only versus agent split (the answer to "does a model do all of this")

```bash
/usr/bin/python3 - <<'EOF'
import json
d = json.load(open('~/cron/jobs.json'))
s = [j for j in d['jobs'] if j.get('script')]
a = [j for j in d['jobs'] if not j.get('script')]
print('total', len(d['jobs']), 'script', len(s), 'agent', len(a))
print('no_agent true among script jobs', sum(1 for j in s if j.get('no_agent')))
for j in s: print('  script:', j['name'], '->', j['script'], '| no_agent', j.get('no_agent'))
EOF
```

Run this before claiming any split. The durable shape is that a large share of the scheduled work is shell and Python with no model in the loop (refills, prefill, click harvest, health checks, backups, report backstops, pruning) while the rest are agent jobs where judgment is required. Quote both halves: the script count proves engineering discipline, and saying it plainly is stronger than implying an agent handles everything, which a technical screener will probe.

## Per-job model and provider (proof the harness is customized, not stock)

```bash
/usr/bin/python3 -c "import json,collections;d=json.load(open('~/cron/jobs.json'));print(collections.Counter((j.get('model'),j.get('provider')) for j in d['jobs']).most_common())"
/usr/bin/python3 -c "import json;d=json.load(open('~/cron/jobs.json'));[print(j['name'],'->',j.get('skills') or j.get('skill')) for j in d['jobs'] if (j.get('skills') or j.get('skill'))]"
```

Model, provider and the skill documents a job loads are set per job, so the same fleet runs several models at once and each stage loads only its own rules. That is the concrete evidence behind any claim about taming context bloat by splitting a large task into scheduled stages.

## Published technical pages

```bash
python3 - <<'EOF'
import urllib.request, re
d = urllib.request.urlopen(urllib.request.Request(
    'https://articles.phantom-byte.com/sitemap.xml',
    headers={'User-Agent': 'Mozilla/5.0'}), timeout=25).read().decode('utf-8','ignore')
locs = re.findall(r'<loc>(.*?)</loc>', d)
mods = re.findall(r'<lastmod>(.*?)</lastmod>', d)
print('pages', len(locs), 'earliest', min(mods), 'latest', max(mods))
EOF
```

This is the strongest number in the document because it is independently checkable: a reader can open the sitemap. It also yields the publishing span, which replaces a vague "since 2026" with a dated claim.

## Original long-form articles written

```bash
ls ~ | grep -cE "^ARTICLE"
ls ~ | grep -oE "ARTICLE[_ ]?[0-9]+" | grep -oE "[0-9]+" | sort -n | tail -3
```

The highest article number is the floor for "more than N original articles." Use "more than N" phrasing so the claim stays true as the number grows.

## Runtime and toolchain versions

```bash
hermes --version
ls ~/skills | wc -l
```

Useful for the TOOLING block and for a version-accurate line about the orchestration layer.

## Multi-host agent fleet

A primary Linux agent runtime handles systems and orchestration work, a separate Windows agent handles desktop and GUI-bound tasks, and an independent remote coding agent handles engineering work, with state synchronized back. This is architectural, not a count, so it does not need re-verification — but verify the hosts still exist before claiming live operation.

## Email-driven task queue

An agent inbox is polled on a short interval and inbound mail is converted into work items with a defined schema, then executed and answered without a human in the loop. Confirm the interval from the job list (the email task processor entry) rather than stating it from this file.

## Paid technical products

```bash
ls ~ | grep -iE "tutorial|guide" | grep -iE "\.pdf$"
```

Names the shipped implementation guides that back the "published technical tutorials as paid digital products" line.

## Codebase scale (what the automation actually is, in lines)

```bash
wc -l ~/money_ideas/*.py | sort -n | tail -12
git -C ~/money_ideas log --oneline | wc -l
git -C ~/money_ideas log --oneline | head -8
```

The largest modules are the gate chain, the mailbox probe, the contact finder and the bounce harvest. Quote the real number with the qualifier "about," and pair the main module with its test module when one sits beside it: a script with a suite the same size as the code is the single most persuasive line available for a QA or automation role. The commit count is the audit trail; the recent subjects describe the specific defects fixed, which is better interview material than any adjective.

The whole pipeline is larger than its biggest module, and that is the better claim for a data-collection or bulk-processing role: count the modules and the total lines, not just the top file, and check the test modules separately.

```bash
ls ~/money_ideas/*.py | wc -l
cat ~/money_ideas/*.py | wc -l
ls ~/money_ideas/test_*.py | wc -l; cat ~/money_ideas/test_*.py | wc -l
/usr/bin/python3 -c "import glob,re;[print(f.split('/')[-1]) or print(re.search(r'\"\"\"\s*(.*)', open(f).read(), re.S).group(1).split(chr(10))[0].strip()) for f in sorted(glob.glob('~/money_ideas/*.py'))]"
```

Every module carries a docstring naming its single job, so the stage breakdown for an answer is available from the code instead of from memory. Name the real script per stage (sourcing, scanning, contact discovery, verification, sending, proof) and never invent one.

## Execution ledger (proof the scheduled work actually runs)

```bash
python3 - <<'EOF'
import sqlite3
c = sqlite3.connect('~/cron/executions.db')
print([r[1] for r in c.execute("PRAGMA table_info(executions)")])
print('rows', c.execute('SELECT COUNT(*) FROM executions').fetchone()[0])
for r in c.execute('SELECT job_id, status, started_at, finished_at, error, delivery_outcome FROM executions ORDER BY rowid DESC LIMIT 5'):
    print(r)
EOF
```

Columns are `job_id, source, process_id, pid, status, claimed_at, started_at, finished_at, error, delivery_outcome`. This is what backs any claim about monitoring, throughput, or failure tracking: per run status, error text, timing and delivery outcome, all queryable. The sibling `deliveries.db` holds `deliveries` and `delivery_tombstones`, so a suppressed message can be accounted for rather than described as sent. The `executions` row count is the honest answer to "how many scheduled runs are on record."

Note `jobs.json` is `{"jobs": [...], "updated_at": ...}`, so index `d['jobs']` before slicing a job dict. A bare `d[...]` on the list raises `KeyError: slice(None, 30, None)`, which looks like a corrupt file and is not.

## What is NOT verifiable from the machine

Revenue figures for services, client names and counts, and conversion rates. Do not estimate these. State the omission to Vinny in one line and add them only if he supplies the real numbers himself.
