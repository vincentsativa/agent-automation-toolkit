---
name: research-data-collection
description: Operational patterns for running automated data collection scripts (pytrends, API scrapers, web data extraction), timeout handling, stale data prevention, result verification, and retry strategies. Companion to keyword-research-seo for the execution layer.
trigger: "running pytrends collector, data collection script times out, stale results file, need to verify collected data, API rate limiting during research, free endpoint returns 429/504 or reports zero results (Overpass, Nominatim, scraped search backends), a search or scrape source coming back empty"
---

# Research Data Collection, Operational Patterns

## When to Use

- Running any data collection script that writes to a fixed output file
- pytrends collector times out or returns stale data
- Need to verify collected data matches the current query before building a report
- API rate limiting (429) during batch collection
- A free shared endpoint (Overpass, Nominatim, scraped search) returns 429/504, or
  a source reports zero results you suspect is a throttle rather than an empty query

## Core Pattern: Stale Data Prevention

Data collection scripts that write to a fixed filename (e.g. `trends_results.json`) create a **stale data trap**: if the script times out, the file on disk may contain results from a **previous run** for a completely different topic. Reading that file and building a report from it produces a report for the wrong subject.

### Prevention

1. **Delete stale output before every run:**
   ```bash
   rm -f ~/trends_results.json
   ```
   Or use a unique filename per run:
   ```python
   collect_batched(batches, output_file='trends_results_[shortname].json', delay=5)
   ```

2. **Wrap the collector with a timeout:**
   ```bash
   timeout 90 .venv/bin/python3 trends_collector.py
   ```
   If it times out, retry immediately, the second attempt on a fresh connection typically completes in under 30 seconds.

3. **Verify data after a timeout:**
   After a timeout, read the JSON file and check that the first term matches what you actually queried. If it shows terms from a different article, delete the file and retry.

4. **Do NOT read stale results:**
   If the collector timed out, the file on disk may be from a previous session. Never proceed with data you haven't verified matches the current query.

## pytrends-Specific Patterns

### Timeout Recovery
- First attempt can hang past 120s (especially on cold start or rate-limited IP)
- Second attempt on a fresh connection typically completes in under 30 seconds
- Always use `timeout 90` in the terminal command, not the default 180s
- **Critical: after a timeout, verify the output file contains data for the CURRENT query, not stale data from a previous run.** Read the file and check the first term matches what you queried. If it doesn't, delete the file and retry.
- **Do not over-engineer the script when it times out.** If a script has worked 100+ times without issue, the problem is environmental (hot IP, connection state), not the code. Retry with a clean connection rather than adding complexity.

### 429 Rate Limiting
- Batched calls (5 terms per `build_payload`) reduce API calls from 30 to 3 for 15 terms
- On 429, the template falls back to individual terms with 8s delays
- If individual terms also 429, the template waits 60s and continues
- On a fresh/cold IP, all batches succeed on the first try

#### Geopolitical Strategy Article Batch Design

For articles about geopolitical dynamics, policy analysis, and CTO decision frameworks (e.g., "Your AI Stack Is a Geopolitical Bet"):

- **Batch 1, Core Strategy Concepts:** The article's umbrella term (e.g., "AI stack"), the coined risk term (e.g., "cloud catalogue risk"), strategic framing terms (e.g., "sovereign AI", "geopolitical AI"), ecosystem term (e.g., "open-weight models")
- **Batch 2, Named Models & Technical Terms:** All specific model names mentioned (Kimi K3, Qwen 3.8, GLM 5.2, Soofi S), the technical debate term (e.g., "model distillation")
- **Batch 3, Ecosystem & Policy Terms:** Broader ecosystem terms (e.g., "Chinese AI models", "open source AI"), decision-intent terms (e.g., "AI model selection", "AI infrastructure strategy"), policy terms (e.g., "AI regulation")

Trend interpretation for this article type: coined risk terms show mean 0.0 (expected, zero competition), new model names show mean 0.0 with rising trend (brand new, 2-4 week window), high-volume umbrella terms (40+) are SEO metadata hooks not primary content targets.

## Two-Pass Strategy (Multi-Source Synthesis Articles)

For articles that synthesize 4+ heterogeneous sources (blog essays + news articles + Substack + vendor benchmarks) into a unified argument, a single pass of 15 terms may miss important umbrella terms. Use a **two-pass strategy**:

**Pass 1 (3 batches, 15 terms):** Specific terms from the article's sources, coined terms, source names, specific model names, niche concepts. These are the high-value first-mover targets.

**Pass 2 (3 batches, 15 terms):** Broader umbrella terms that the first pass missed, architectural concepts, security terms, cost/economics terms, vendor product lines. These are the SEO metadata hooks and secondary targets.

**Why two passes:** The first pass's term selection is biased toward what the article specifically discusses. The second pass catches adjacent terms that searchers use but the article doesn't explicitly name. Example: an article about "Library-Librarian pattern" might not include "AI system design architecture" in its term list, but that's a high-volume (40.5) umbrella term that belongs in the SEO metadata.

**When to use two passes:**
- Article synthesizes 3+ sources from different domains
- Article has a security, cost, or architecture angle that spans multiple sub-topics
- The coined term is a named pattern (not a descriptive phrase), broader umbrella terms are needed for SEO context

**When one pass is sufficient:**
- Single-source article (one paper, one benchmark)
- Tutorial or how-to guide with a narrow technical focus
- Breaking news article with a single event-specific term

## Batch Design
- Batch 1: Core article concepts (umbrella terms, coined terms, paper names)
- Batch 2: Adjacent/benchmark terms (cited benchmarks, vendor names, frameworks)
- Batch 3: Hardware/ecosystem terms (infrastructure, standards, platforms)
- Max 5 terms per batch (pytrends limit)

## Verification Checklist

Before building a report from collected data, verify:

- [ ] The output file exists and is non-empty
- [ ] The terms in the output match what you queried (not stale data)
- [ ] No terms show errors (429, timeout, etc.), if so, retry those batches
- [ ] Trend direction is derived from the last 4 weeks of 12-month data (not a separate API call)
- [ ] Coined terms showing "mean: 0.0" are expected, not errors

## Throttled Endpoints Report as Empty, Not as Errors

A free, shared, rate-limited endpoint (Overpass, Nominatim, a scraped search backend)
answers the first request, then returns `429 Too Many Requests` or `504` while the
calling client still reports "0 results" or "no matches." The failure is silently
indistinguishable from a genuinely empty result set, because these clients do not
retry and **do not cache failures**, so nothing on disk records what happened.

This makes a throttle the one failure mode where retrying is actively harmful: each
attempt spends a slot on the shared limit and returns less. It is also the failure
mode most likely to be misdiagnosed as "no data exists for this query," which then
produces a confidently wrong conclusion.

Rules:

- **Pace requests to shared free endpoints.** One at a time, spaced, never a probe
  loop and never a burst of retries "to see if it works now."
- **Cap retries at two attempts on the same host.** After the second failure, stop
  and report which host is throttled, which HTTP reason it returned, and what still
  works. A retry wrapper around a throttled endpoint hides the loop rather than
  fixing it.
- **Read the engine's own error surface before concluding anything.** When a
  collection run prints or logs the failing host and HTTP reason, that line is the
  diagnosis. Silence plus a zero count is not evidence the source is empty.
- **Distinguish throttle from empty in the output.** "0 results, endpoint throttled"
  and "0 results, query matched nothing" are different findings and must not be
  written up as the same one.

A retry helper is legitimate for a source that fails intermittently at normal human
pacing. It is not a substitute for pacing, and it must not be pointed at a host that
is already refusing requests.

## A Hardcoded Client Timeout Looks Exactly Like a Throttle

Throttling is not the only thing that reports zero. A client that stamps a short
server-side timeout into its own query gets the same `504` and reports the same
"0 results," even though the endpoint answered the same request fine when asked
with a longer timeout. Distinguish the two before concluding anything about the
query or the area.

Measured on a dense metro: a tool whose query carried `[timeout:25]` returned
`HTTP 504` and `0 leads` for a whole-city search, twice, while the identical
query issued directly with `[timeout:180]` and a tighter bounding box returned
400 elements, 386 distinct domains, and 55 published contact addresses in a
single call. The city was never empty. The timeout was.

Rules:

- **Before reporting a dense area as empty, re-issue the query yourself with a
  long timeout and a real bounding box.** A whole-city bbox in a dense metro is a
  bigger and slower query than the same category in a small city, so it is the
  first thing to hit a short timeout.
- **A tightened bounding box is a legitimate second attempt, not a workaround.**
  Querying one borough or district instead of the whole city reduces the response
  size and usually completes where the full-city query timed out.
- **Read the client's own timeout value before blaming the server.** If the
  timeout is a hardcoded constant in the client, that constant is the finding.
- **A `504` and a `429` are different failures with different fixes.** `429`
  means pace requests and back off. `504` on a dense query means ask for less at
  once, or ask with more patience.

See `references/targeting-open-datasets.md` for the larger fix: loading an
unthrottled local extract of the same dataset so no query ever waits on a shared
server, and for keeping control of the category filter instead of borrowing the
client's built-in one.

## Long Runs: Announce Completion From a Process-Name Watcher

When a collection run takes tens of minutes and the user says "let me know when it is
done," the deliverable is a single completion notice with the final count. Watch it
from a background watcher that:

- counts live processes by NAME (`pgrep -f "<script>.py"`), never a captured PID, a
  run relaunched in a different shape (one process split into N parallel part files)
  has a new PID, so `kill -0 <old_pid>` reports false while the work is still running
  and the watcher announces a false completion;
- sums the row count across every output file by glob (`*_part*.csv` plus the base
  name), since a split run leaves the single original path frozen at a stale count;
- carries its own no-progress cap and reports STALLED with the live process count and
  rows so far, so a hung job notifies someone instead of waiting forever;
- is syntax-checked (`bash -n`) before launch, because a broken background watcher
  fails silently and the job finishes unobserved.

Launch the watcher loop AS the background command. Never wrap it in `nohup bash -c '...' &`
inside a `background=true` call: the backgrounded shell returns immediately, so the
completion notification fires for the shell that started the watcher rather than for
the job. Report the live process count, the summed row count across all output files,
and the finish time, a watcher exit code of 0 means the watcher ended, not that the
collection succeeded.

Full recipe: `references/background-job-completion-monitoring.md`.

## Parallelize a Large Per-Input Harvest

A per-domain network fetch is the whole cost, so wall time scales with input count.
A list in the hundreds to low thousands runs as N parallel workers over split input
lists. One process over the same list is the bottleneck, and the gap is not marginal:
measured, a single process wrote 21 rows in 6 minutes while four workers over the
same 1,652 domains finished in about 54 minutes with 646 addresses.

```bash
split -n l/4 -d --additional-suffix=.txt domains.txt domains_part
for i in 1 2 3 4; do
  nohup python3 collector.py --file domains_part$i.txt \
      --out out_part$i.csv --osm-emails local_index.csv >> part$i.log 2>&1 &
done
```

Rules:

- **Confirm the previous runner is gone before starting the split.**
  `pgrep -f "<script>.py"` must return nothing. A single-process run left alive
alongside the split reprocesses the overlapping rows and writes them twice:
  measured, 21 domains landed in both the base file and a part file, 84 excess rows
  over 1,652 domains. Merge the part files on the input key, never by raw
  concatenation, so a duplicate cannot inflate the final count.
- **Load whatever local index the collector accepts before it fetches anything.**
  A pre-loaded key-to-address map costs nothing and beats the network: 302 of the
  646 addresses found (47%) came from it, ahead of every page fetched. It was the
  single largest contributor to the run.
- **Sum row counts across every output file for progress**, by glob including the
  base filename. A split run freezes the original single-file path at a stale count.

Full recipe, merge code, and measured yield table: `references/domain-list-harvest.md`.

## Measure Yield and Size the Next List From It

Record the hit rate at the end of every run, because it is what sizes the next input
list. Measured on a list of domains already confirmed to carry a defect: **39.1%** of
domains published any usable address, and a **named person** was **6.3%**, about one
per 16 domains. Budget roughly 16 domains per named contact, and do not quote the raw
input count as the reachable count.

Yield is not uniform and the run should report it split by source, because the split
is what tells you where to spend the next hour. Measured ordering, best first: a local
dataset's own address tags, then page-printed role addresses (`info@`, `sales@`), then
named persons. A run that reports only a total hides that the cheapest source did the
most work.

## A Harvest Count Is Not a Sendable Count

Downstream stages cut the list after the harvest: chain and brand blocklists, dedupe,
tier grading, address validation. Run or check that stage before reporting a sendable
number, and report the post-filter count as the answer, naming the raw count and what
was dropped. Measured: a chain blocklist took 646 harvested addresses down to 547, and
every drop was a national brand with an IT department rather than an owner reading his
own mail.

When asked "how many are ready to stage," the sendable number is the deliverable. A
raw harvest total quoted as the stageable total is wrong, even when the harvest itself
was clean.

## Pitfalls

- **Stale data is the #1 failure mode.** A previous run's `trends_results.json` sitting on disk will be read after a timeout, producing a report for the wrong article. Always delete or use unique filenames.
- **Exit code 0 means the script ran, not that data is fresh.** The script can complete successfully with stale data if it read from a pre-existing file. Always verify the terms match.
- **pytrends can hang indefinitely.** Always wrap with `timeout 90`, don't rely on the terminal tool's default timeout.
- **Do not fall back to domain-knowledge estimates.** If data collection fails after retries, report the failure. Never invent numbers.
