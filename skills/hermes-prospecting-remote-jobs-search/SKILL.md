---
name: remote-jobs-search
description: "Use when Vinny wants verified remote job leads emailed. The search is built from his resume in references/resume and scored against it; the report ships direct-apply leads whose posted pay lands in or can reach his $1,000 to $2,500 band, across writing, technical writing, content, SEO and AI-evaluation work."
version: 1.2.0
platforms: [windows]
metadata:
  hermes:
    tags: [jobs, remote, job-search, screening, 1099, contract, verification]
    category: prospecting
---

# Remote Jobs Search

Vinny's standing job spec lives in `config/rules.json` in this skill directory. The Desktop file it was originally transcribed from, `job-search-parameters-2026-10-17.txt`, is no longer on disk, so do not try to read it; `rules.json` is the live spec and the scripts read it directly. This skill turns that spec into a runnable pipeline: cheap scripts do the collecting, filtering and liveness proof, and the model does only the parts that need judgment, which is choosing the leads and judging whether each one is real, still open and a fit.

The deliverable of a run is twenty verified leads, emailed to him as an attachment, plus a Telegram notification. Twenty is the count every single run. The only reasons a row is not shippable are that the employer page is not live or that it carries no direct employer apply path. Any other shortfall is a supply defect in the run, and the answer is to widen collection and re-select until the list holds twenty, not to ship fewer and explain it.

## What the October 21, 2026 run got wrong

That run shipped four leads: a Renewals Manager, a Solutions Consultant, a Junior Data Solutions Architect and a salaried Senior Content Writer. He asked for twenty and got four, all salaried, all above his band, all in job families he does not apply to. The pool was not the whole problem and the prose was not the problem. Three defects in code were, and they are fixed in this version:

- **`classify_path()` read the word "contract" anywhere in the body.** Nearly every salaried posting says contract somewhere ("contract renewals", "contract negotiations"), so salaried W-2 roles were tagged `high_pay_1099` or `band_flexible_1099`, which silently disabled both the salaried-above-band cap in `prefilter.py` and the band-mix gate in `report.py`. Engagement now comes from the structured engagement fields plus explicit self-employment markers only.
- **Source supply was eleven aggregator feeds and one ATS adapter pointed at big product companies.** The work he applies to (part-time and contract writing, editing, SEO, AI evaluation) lives on employer-hosted application pages, and the pipeline had no adapter for any of them. Workable and Alignerr were added here and supplied most of a full list for a week; Vinny excluded Alignerr outright on October 25, 2026 (blocklisted in `rules.json`, disabled in `sources.json`), and SmartRecruiters was added the same morning as the replacement direct-apply surface.
- **The selection step was entirely hand-written.** `select.py` now writes a deterministic baseline list from the rules, and `run.py` calls it when no `selected.json` exists, so a run cannot drift back to whatever looked plausible in a pack.

## The resume is part of this skill

His resume lives in `references/resume/RESUME_Vincent_Barreca_AI_Systems_Builder.pdf` with a text copy beside it, and every run scores candidates against it. Until October 21, 2026 nothing in the pipeline had read it, which is why a technical writer with 190 long-form engineering articles, a 210-page technical SEO property and a production agent fleet was being sent "English Writing Generalist", "Search Quality Evaluator" and "Virtual Assistant".

```bash
$PY311 build_resume_profile.py            # rebuild config/resume.json from the in-skill PDF
$PY311 build_resume_profile.py <new.pdf>  # after he hands over a new resume
```

`config/resume.json` holds the title phrases the resume is written for (technical writer, technical content, developer documentation, content strategist, SEO/GEO, AI content, email deliverability, AI automation), the body vocabulary that shows he can answer the posting (agents, orchestration, prompt injection, inference, SPARK/DKIM/DMARC, sitemap, long-form), and the hard anti-signals (mechanical, physics, clinical, legal, WMS/ERP, transcription, video, packaging).

Three rules come out of it and are enforced in code:

- **A hard anti-signal drops the row whatever else it says.** "Mechanical Engineering Expert - AI Content Specialist" matches "AI content" and is still a job for a mechanical engineer.
- **A soft anti-signal drops it unless the title names one of his roles.** Transcription, healthcare, legal, video, support and assistant work cannot win on a stray keyword in the body.
- **The resume fit is the first tie-break inside a pay tier**, so among work he can take he sees the rows his record actually answers, and every lead in the report carries a `Resume match:` line naming the title phrase and the posting's own vocabulary that matched.

When he changes the resume, rebuild the profile before the next run. Do not hand-edit `config/resume.json`; edit the PDF or the curated lists in `build_resume_profile.py`.

## How pay is ranked and printed

He reads the printed number, not the theory. Three states, computed by `common.band_state()`:

- **`in_band`**: the monthly figure as posted lands inside $1,000 to $2,500.
- **`capable`**: hourly or per-task work above the band at a full week, where the rate reaches the band at a part-time week he sets. For these the report prints the rate and the paid hours that land in the band, never a 40-hour month. Printing "$3,464 to $10,392 per month" on sixteen of twenty leads was the October 21, 2026 complaint, and it was fair.
- **`above`**: salaried work priced above the band. These carry the insurance flag and are capped at `max_above_band_at_assumed_hours` (4).

A fourth group, `unrated`, is work on a direct-apply employer page whose pay the public feed does not return. Those ship only with a strong resume match, capped at `max_unpaid_picks` (3), marked "confirm the rate before applying", and excluded from the in-band share. Workable and Greenhouse hide pay in a field the API does not expose, and throwing those rows away is why his lists had almost no content-writing jobs.

The report's `Composition:` line states all four counts, and `report.py` refuses to render when fewer than `min_stated_band_share` (60 percent) of the paid picks are `in_band` or `capable`.

## The apply-path rule (his standing rule)

He got a list where every lead routed through a board that wanted a fifteen-minute account signup and data collection before it would show the employer's form. His words: jobicy.com is a disgrace, do NOT give me any more from this website, and he is not spending thirty minutes to an hour creating accounts so he can collect spam later.

Three hard rules follow, and the scripts enforce them rather than trusting the prose:

- **Jobicy is banned outright.** `config/sources.json` has it disabled and `config/rules.json` blocklists `jobicy.com`, so even a stray link is dropped. Do not re-enable it and do not add another board with an account wall.
- **Every lead must carry a direct apply path: the employer's own page, an ATS form hosted for that employer, or a direct application email.** A board listing URL is not an apply path. `common.has_direct_apply()` decides, `verify.py` resolves the employer link from the listing when the feed row lacks one, and `report.py` refuses to render a pick without a direct path.
- **Email is the preferred path when the posting offers one.** It is not required; an employer ATS page is equally fine. An account wall is never fine.

When these gates leave fewer than twenty leads, ship fewer and state the shortfall in the summary. Padding with board links is the failure he complained about, and it is worse than a short list.

## No single-source lists

Selecting twenty rows from one board is lazy and he called it out directly. Three limits are enforced in code and apply to every run:

- **The list holds twenty picks. There is no per-source cap, no per-company cap and no source-spread floor.** Selection fills twenty from the verified pool in quality order: in-band paid work first, then hourly and flexible work, then salaried roles above the band, then rows with no stated pay. A run that returns fewer than twenty because of a cap in this file is a defect, not a result.
- `config/params.json` also caps how many candidates any one source may contribute (`max_candidates_per_source`), so verification budget is not spent on one board's listings.
- `select.py` fills the list round-robin by source rank, reserving one slot per contributing source before any board gets a second pick.

If a board genuinely carries most of the usable supply, the answer is more sources, not a fatter slice from the same one. Name the mix in the summary paragraph.

## The money rule (his own words)

Two paths, both live, and the scripts tag every lead with the one it lands on:

- **Primary, the majority of every list: $1,000 to $2,500 a month gross.** That band protects his wife's SSI and her medical coverage while he rebuilds. Most leads should live here, and the way that band is actually reachable is hourly and part-time work where he sets the hours, or short 1099 engagements priced per project or per task.
- **Second path: $80,000 a year or more, shaped as 1099, contract or freelance, with no background check, or from an employer that hires felons.** He said plainly that he will take that, and he accepts the coverage tradeoff at that level. Do not treat a high-paying 1099 role as a problem to talk him out of. Name the tradeoff once, in one line, and move on.
- **What stays flagged:** salaried W-2 above the band. There the tradeoff is a real decision rather than something he has already accepted, so those leads carry the insurance flag and he decides.

`common.classify_path()` does the mechanical tagging (`primary`, `band_flexible_1099`, `high_pay_1099`, `above_band_w2`, `unrated`), and the model can override it per lead by setting `path` in `selected.json`, which is the better choice whenever the script's read of the posting is obviously wrong. `config/rules.json` holds the paths, the thresholds and the `second_chance_signals` list.

How it decides, because this is where the October 21, 2026 list went wrong:

- **Engagement shape comes from structured fields, never from a bare word in the prose.** `employment_type`, plus explicit markers (1099, independent contractor, freelance, contract position, per task, per project), plus an hourly, daily, weekly or per-piece pay period. A salaried marker (full-time, W-2, salaried) vetoes the contract read unless the explicit 1099 language is present. Reading "contract" out of a body tagged Eve's Renewals Manager and Gainsight's project manager as 1099 work, which disabled every cap below.
- **Hourly and task work shaped part-time is `primary`.** The rate is fixed and the hours are his, so the band is reached by working fewer hours, and the report prints how many paid hours a month reach it (`Band hours:`). Hourly prompt work at $40-$120/hr is the case the October 17, 2026 list priced at "25-63 paid hours a month". A 40-hour hourly job is not that and falls through to the contract tests.
- **Freelance and task postings with no stated hours are computed at 20 hrs/week**, not 40, for the same reason.

The mix is ordered in code, not left to prose. `prefilter.py` holds salaried above-band rows to `max_above_band_share` of the candidate pool (0.35, so verification effort goes to work he can take) and ranks his job families and in-band work up. Selection then fills twenty in quality order: in-band paid work first, hourly and flexible work next, salaried roles above the band after that, rows with no stated pay last. Hourly, part-time, contract and freelance work therefore sits at the top of every list by construction, and the list still holds twenty.

Two things to be honest about inside this rule. A "no background check" line in a posting is a claim, not a finding: it still has to be a real company, with real stated pay and a working apply path, and the background-check tier is still reported. And 1099 never means "no checks" on its own, so never promise him a job skips screening.

When he asks for twenty and the in-band pool cannot fill them, "close to my parameters" means near-band hourly work rather than salaried seats: hourly, part-time or 1099 roles that land between about $2,600 and $4,700 a month at full hours are usable filler, and the report states that split at the top. A salaried W-2 role at the same figure is not the same thing and stays capped by `max_above_band_picks`.

## Layout

- `references/resume/` - Vinny's resume, PDF and a text copy. The search is built from this file.
- `config/resume.json` - the resume profile: title phrases, body vocabulary and hard anti-signals, built by `scripts/build_resume_profile.py`. Rebuild it when the resume changes.
- `config/sources.json` - the source registry, one entry per board with its adapter, URL and notes.
- `config/companies.json` - employer ATS boards read directly through Greenhouse, Ashby and Lever, one slug per company. This is the direct-apply source class: no board account wall and the employer's own application URL on every row.
- `config/rules.json` - Vinny's standing rules: the permanent exclusions, the blocked phrases, the geo lists, the title weights, the band, the target count. Change only when he changes the spec.
- `config/params.json` - per-run knobs the model rewrites before a run: search terms, age window, volume caps, hours assumption.
- `scripts/collect.py` - stage 1, pulls raw postings from every enabled source into `raw.jsonl`. The Himalayas adapter pages deep by offset up to `himalayas_max_offset` (30,000 is the production setting), because the feed carries over 128,000 postings and its first 40 pages are under one day of them.
- `scripts/prefilter.py` - stage 2, applies the hard rules, dedupes, ranks, writes `candidates.jsonl` and `dropped.jsonl` with a named reason per drop.
- `scripts/verify.py` - stage 3, fetches each lead's own application page and classifies it live, dead, blocked or unknown.
- `scripts/payfix.py` - stage 3b, re-opens live leads that carry no pay figure and pulls the salary line from the employer's page.
- `scripts/build_resume_profile.py` - reads the resume PDF (default is the in-skill copy) and writes `config/resume.json`. Stdlib plus pypdf, deterministic.
- `scripts/pack.py` - stage 4, compresses verified leads into small packs for the model to read cheaply.
- `scripts/topup.py` - stage 4c, called by `run.py` after selection. If the baseline holds fewer picks than the target it widens the direct-apply supply in three rounds - Workable at search depth (which itself falls back to the employer boards while the search endpoint is banned), SmartRecruiters paged deeper, then the forced Workable employer-board fallback - re-filtering, re-resolving, re-verifying and re-selecting with `--force` between rounds. It never relaxes a cap: if the count still cannot reach the target it prints the pool arithmetic and the run reports that, because the alternative is padding. On October 22, 2026 the first pass left twelve in-band leads and the list went out at nineteen; widening supply produced an eighth in-band role and the twenty closed.
- `scripts/select.py` - stage 4b, writes a deterministic baseline `selected.json`: live rows with a direct apply path, his job families first, in-band and hourly work before salaried work above the band, one lead per company and role, source caps respected, twenty picks or the honest short list. `run.py` calls it when no `selected.json` exists and never overwrites one the model has edited.
- `scripts/report.py` - stage 5, renders the unwrapped report from the model's picks, computes the composition and source-mix lines itself, and enforces the count, apply-path, source-spread, money-floor, band-mix and in-band-mix gates.
- `scripts/resolve_employer.py` - stage 2b, gives every candidate a direct employer apply path. Deterministic ATS lookup first (Greenhouse, Lever and Ashby queried directly with slug variants plus a title match), open-web search second, and it writes the resolved URL back into `candidates.jsonl`. Wired into `run.py` between prefilter and verify.
- `scripts/run.py` - one command for stages 1 to 4b (collect through baseline selection).
- `scripts/common.py` - shared helpers: fetching, HTML stripping, pay parsing, monthly math, hours detection, apply-target extraction.
- `scripts/probe_ats_slugs.py` - probes candidate employer slugs across Greenhouse, Lever and Ashby concurrently and prints live posting counts plus JSON-ready arrays for `config/companies.json`.
- `scripts/pull_himalayas_deep.py` - pages the Himalayas feed deep by offset in parallel, dedupes by guid and writes incrementally, so a run is not limited to the newest day of inventory.
- `references/employer-apply-resolution.md` - how to find and verify the employer's own job page for a board row whose Apply button is a signup wall, including the Bing redirect-decode recipe and what counts as a verified page.
- `scripts/seed_ledger_from_document.py` - seeds the cross-day ledger from a job list that was delivered outside `report.py`, then re-reads the ledger to prove every key is stored.
- `references/adding-a-source.md` - the probe recipe for testing a candidate board before it enters the registry, the normalized record contract every adapter must fill, and the pay phrasings and freshness traps each board brings.
- `references/apply-path-and-sources.md` - what counts as a direct apply path, how the resolver finds the employer link behind a board, which boards gate applications, and the Greenhouse, Ashby and Lever API recipes for adding employers.

Run artifacts live in `~/job-search/YYYY-MM-DD/`, one folder per day, so a run is reproducible and the counts can be checked against what was asked.

## Which interpreter to use

Run everything with the Python 3.11 install, because that is where scrapling lives and `verify.py` uses it for pages that refuse a plain fetch:

```bash
PY311="~/AppData/Local/Programs/Python/Python311/python"
cd "~/AppData/Local/hermes/skills/prospecting/remote-jobs-search/scripts"
$PY311 run.py
```

Standard library only otherwise, so plain `python` also works if scrapling is not needed.

## The run, step by step

### 1. Plan the run (model)
Rewrite `config/params.json` for today: search terms aimed at his direction (writing, content, SEO, marketing, design, AI and automation, operations, customer success, support, VA), the age window, and the volume caps. Leave `config/rules.json` alone; it is his spec, not a knob.

If a source has gone dead or a new one is worth adding, change `config/sources.json` and say so in the report.

### 2. Collect, filter, verify, pack (scripts)
```bash
$PY311 run.py                    # collect -> prefilter -> resolve -> verify -> pack -> select (baseline)
$PY311 run.py --only workable    # one source only; appends instead of wiping raw.jsonl
$PY311 payfix.py --limit 40      # fill in missing pay from the employer's pages
$PY311 select.py --force         # rebuild the baseline picks after a rules change
$PY311 verify.py --only-source himalayas --headless --merge   # stealth browser for a blocked host
```
`run.py` prints a per-source line, the drop reasons with counts, the verdict counts and the pack paths. Read those numbers; they are the honest record of the run. It also runs `topup.py` after selection, so a thin first pass is widened before the list is judged rather than after it has shipped short. If `topup` reports that it still could not reach the target, the shortfall is supply and the pool arithmetic is what the summary states.

Keep `require_pay` true in `config/params.json`. Every shipped lead has to state pay, as in the list he held up as better, and a no-pay row cannot be band-checked at all. `payfix.py` fills a missing figure from the employer's page before anything is dropped for it.

### 2b. Audit the pool before you judge the picks

Never decide that selection was the problem from the report alone. Count the verified pool by money path, then compare it to the picks:

```bash
$PY311 - <<'PY'
import json, collections, os, sys
sys.path.insert(0, os.getcwd())
import common as C
rules = C.config("rules.json")
rows = [json.loads(l) for l in open(os.path.join(C.run_dir(), "verified.jsonl"), encoding="utf-8")]
print(collections.Counter(C.classify_path(r, rules)[0] for r in rows))
PY
```

Read it as a decision, not a status line. If `primary` plus `band_flexible_1099` is already smaller than the target, the shortfall is **supply**, and the fix is more or better sources; promoting salaried rows or padding is not a fix.

Count only candidates that are also usable. An in-band row that fails a hard gate (all-day phone work, residency limited to one state, five-plus years, offshore only, no named employer, a pay line the body contradicts) does not count toward the target no matter what its money path says. The only ceiling on the list is the number of rows that are live and carry a direct employer apply path. Count those, then fill twenty from them. When that pool holds fewer than twenty, the run has not finished collecting: widen the sources, re-resolve, re-verify and re-select. Never ship seventeen and explain it. If the pool holds twenty but the picks do not, the picks are the defect and the selection has to be rebuilt. The same audit on the picks tells you what the report will look like before `report.py` says it: the first picks should be the in-band and hourly work, and the salaried roles come after.

### 3. Judge and select (model, on top of the script's baseline)

`run.py` has already written a baseline `selected.json` from the rules in step 2. Open it, then read the packs in `~/job-search/<date>/packs/` and improve it. The baseline guarantees the count, the job families, the ordering and the source spread; your job is the judgment the scripts cannot do.

Do not replace the baseline with picks from outside `candidates.jsonl`. On October 21, 2026 the picks were chosen by hand from the packs and came back as four salaried roles while the pool held content, writing and AI-evaluation work. If you drop a baseline pick, put a better row from the same source and family in its place.

For each pick decide:

- Is it real? A live employer page with a working apply path, stated pay, and a public web presence.
- Is the apply path direct? Check `apply_url` and `apply_email` on the verified row. A board host, a careers index page (`https://employer.com/careers/` is not a job), or an empty pair means the lead is not applicable no matter how good the job looks, and `report.py` will refuse it. Prefer a posting that gives an application email.
- Is it a scam or a trap? Pay-to-apply, signup walls, talent pools, commission-only, crypto-only payment, an email domain unrelated to the company, or a pay figure that is absurdly high for the work.
- Does it survive his hard gates? No mandatory degree, no five-plus years, no recorded video step, no clearance, US-eligible, free to apply, fresh, no phone-heavy work.
- Is it in his job families? Writing, editing, copywriting, content, SEO/GEO, technical writing, AI training and evaluation, prompt work, email marketing and deliverability, social media, design and video, virtual assistant and admin, data entry, customer support. A Solutions Architect, Renewals Manager, Underwriting Analyst or QA Engineer is not his direction even when it pays well, and the prefilter now blocks those families outright.
- Re-read the full description of every pick before it ships. The prefilter regex and the pack snippet both only see the opening of a posting, and mandatory-gate wording hides further down: a role quoting an attractive hourly rate can still require a degree in its "what we are looking for" block. A gate you did not read is a gate you did not check, and one disqualified lead among the twenty costs the whole list its credibility.
- Is it a fit he can actually land? Lead with his proof, name the honest gap, and flag stretch fits next to the lead.

Then rewrite the `fit`, `gap`, `legit`, `risk` and `effort` fields in `selected.json` with the real evidence, keep the `url` values copied from the verified file, and add the screened-out roles with the exact disqualifier. Keep this shape:

```json
{
  "picks": [
    {"url": "<must match the verified row url>", "path": "primary|band_flexible_1099|high_pay_1099|above_band_w2",
     "fit": "why it fits, with the proof point",
     "gap": "none" or "the specific gap", "risk": "LOW|LOW-MODERATE|MEDIUM|HIGH",
     "effort": "quick apply" or "standard ATS" or "heavy ATS",
     "engagement": "1099 contract|part-time|W-2 full-time",
     "legit": "the evidence it is a real employer", "stretch": false}
  ],
  "rejects": [{"title": "...", "company": "...", "reason": "the exact disqualifier"}],
  "summary": "one paragraph; the composition and source mix are printed by report.py, so do not restate them here"
}
```

Never edit a `url` by hand. If you need a different pick, copy its url out of `verified.jsonl`.

### 4. Render (script)
```bash
$PY311 report.py
```
It refuses to render unless there are 20 picks (the honest-count rule), then refuses again if any pick lacks a direct apply path, is not live-verified, breaks the source-spread limits, breaks the money floor, or fails the band-mix and in-band-mix gates. It prints the longest line as the unwrapped check and writes `report-<date>.txt`. When supply genuinely cannot fill twenty under those gates, `--allow-short` ships the short list with the shortfall stated in the summary; never pass it to rescue a padded list.

The report computes its own `Composition` block (how many leads are hourly or flexible, how many sit inside the band as posted, how many reach it at chosen hours, how many are salaried above it) and its own `Source mix` line. Do not write either by hand in `selected.json`; a computed line cannot contradict the leads underneath it, which is the defect he caught on October 21, 2026. It also prints an `APPLICATION PRIORITY` block in pick order, so keep the strongest lead first when you reorder.

**Proving a renderer change without touching a delivered run.** Render a finished day into a scratch folder by pointing `common.run_dir` at a copy, so the real report file and the ledger are never rewritten:

```bash
$PY311 -c "
import os, shutil, sys
src = os.path.expanduser('~/job-search/<date>')
dst = r'<scratch>/render-test'
os.makedirs(dst, exist_ok=True)
for f in ('verified.jsonl','selected.json','raw.jsonl'):
    shutil.copy(os.path.join(src,f), os.path.join(dst,f))
sys.path.insert(0, os.getcwd())
import common as C
C.run_dir = lambda run_date=None, create=True: dst
sys.argv = ['report.py','--date','<date>','--no-ledger']
import report
report.main()
"
```

Then check the output structurally, not by eye: every lead carries all five section headers, no line holds two pipe-separated facts, every rule is exactly 80 characters, and the longest line is in the hundreds. A revert is proven the same way, by diffing the fresh render against the file he already received with the re-check timestamps and pool count normalized out.

### 5. Deliver (email-sender skill)
Attach the report and keep the body brief. Write the mailer under a fresh dated name, `send_email_jobs_<YYYY-MM-DD>.py`, so a previous run's script is never overwritten; if that filename already exists, add a `-v2` suffix. Never write to a bare `send_email_jobs.py`, because a file of that name from an earlier run may already exist and the write tool will refuse to clobber it. Verify delivery by reading the message back over IMAP before telling him it landed. Print the attachment byte count from the readback, not just the subject line.

Before any send, confirm the artifacts agree with each other, because a run that re-collects or re-verifies after rendering leaves a report that looks finished and is not:

- `verified.jsonl` must not be newer than `report-<date>.txt`. If it is, the picks were built against an earlier pool. Rebuild `selected.json` from the final verified rows and re-render.
- Every pick URL must still exist in `verified.jsonl`. A pick that no longer matches the verified file is a leftover, not a lead, and the report may be describing rows that no longer exist.
- `selected.json` must carry the rejects as well as the picks. An empty screened-out section beside a summary that names disqualified roles is a completeness defect: fill the rejects with the exact disqualifier for each named role before rendering.

Then notify him on Telegram, in the same turn, and do not paste the report into chat.

## Cross-day dedupe (the ledger)

A daily cron that runs all week will see the same postings over and over inside the freshness window, so the pipeline keeps a ledger at `~/job-search/ledger.jsonl`. Every lead that ships is appended there by `report.py` with the day it shipped.

`prefilter.py` reads it and holds out anything reported on an earlier day, by URL and by company-plus-role key, with the drop reason naming the day it went out. Two deliberate behaviours:

- **Same-day entries are not held.** Re-running a day re-examines that day's leads instead of returning an empty list, and `report.py` will not double-record the same lead for the same day.
- **`applied-jobs.md` is honoured too.** If Vinny keeps that file at `~/job-search/applied-jobs.md`, on the Desktop or in OneDrive Desktop, any URL in it is excluded as already applied. Nothing creates that file for him; it is his record.

Useful flags: `prefilter.py --include-seen` ignores the ledger for one run, and both `prefilter.py` and `report.py` take `--ledger <path>` so dedupe can be tested against a throwaway file without disturbing the real ledger.

For a document delivered outside the pipeline, run `scripts/seed_ledger_from_document.py <document> --date <ship date>`; it parses the company-and-title headings, builds the ledger keys, appends them, and then re-reads the ledger to prove every seeded key is held.

Two operational notes. Seed the ledger when the skill goes live mid-stream: if a report shipped before the ledger existed, record those leads once with `C.ledger_append(rows, reported_on="<that date>")` so the first scheduled run does not hand them straight back. And remember the ledger is written at render time only, so a report that fails the count check records nothing and cannot poison the next day.

**A list delivered outside `report.py` is invisible to the ledger and will come back.** Any hand-built list, alternate document, or emailed attachment produced in a manual session has to be seeded before the next scheduled run: parse company and title from the document, set `url` to its apply URL or a unique `doc://` marker, build `key` with `C.lead_key`, and append with `reported_on` set to the day it shipped. Verify the seed by calling `C.ledger_held(today=...)` and checking the company-plus-role keys rather than the URLs, because the delivery document usually carries the board URL while the pipeline resolves a different ATS apply URL, so URL matching alone reports a false miss. `ledger_held` returns `(urls, keys, when)`, and `lead_key` strips punctuation, so `AI/SEO` is stored as `ai seo`. A report paragraph claiming nothing was carried over is only true against whatever the ledger knows; check delivered documents too before writing that sentence.

## What the report contains

Header, then the leads, then an `APPLICATION PRIORITY` list in the same order, then the screened-out list with exact disqualifiers, then how every lead was verified. The header carries the applicant and target line, the computed `Composition` block and the computed `Source mix` line.

**Layout is a block per lead, and it lives in the renderer.** `report.py` writes each lead as a boxed block: a rule of 80 `=`, the lead number and title, another rule, a blank line, then the labelled sections `Role`, `Pay`, `Coverage` (only when a flag applies), `Apply`, `Fit`, `Verification`, each header alone on its own line with its fields indented two spaces beneath it, one blank line between sections and two between leads. `Role` holds company, source, posted date and age, engagement, application effort and background-check tier. `Pay` holds the rate as posted, then `Band hours` or `Monthly math`, then `Money path`. `Apply` holds the URL on its own line, or `Email:` for a direct application address; a board URL never appears there and neither does a careers index page. `Fit` holds the resume match, why it fits and the gap. `Verification` holds the live check evidence and the legitimacy line. `Composition` is four counted lines, not one sentence. `APPLICATION PRIORITY` and the screened-out list put the title on its own line with the company and pay, or the exact disqualifier, indented beneath it. Body paragraphs stay one unwrapped line each; never hard-wrap them to a column.

The flag on a lead branches on its money path, and `report.py` does that branching rather than leaving it to the prose. A lead in the band gets no flag. A lead on the $80k-plus 1099 path gets one coverage-tradeoff line stating the number and reminding him to confirm the replacement plan before he starts, because he has already accepted that tradeoff. A salaried W-2 lead above the band gets the full insurance flag: income over about $2,500 a month risks his wife's SSI and her medical coverage, and that decision is his to make fresh. Never flatten the three into one warning, and never let a lead's prose claim a band it does not have: when the fit text and the printed math disagree inside the same lead, the lead reads as unchecked.

The summary paragraph at the top of the report states the composition of the list outright: how many leads are contract, hourly or per-task engagements where the hours are his to set, and how many are salaried and above the band. His spec makes the majority-in-band rule binding, so the mix is the first thing he checks, and inferring it from twenty entries is work he should not have to do. When the mix falls short of that rule, the summary says so in plain words there, and the run does not pad, reweight or quietly redefine the band to hide it.

Unwrapped text only. One paragraph per physical line, no columns, no tables, no em dashes. Verify with the longest-line check before sending:

```bash
awk '{ if (length($0) > m) m = length($0) } END { print m }' report-<date>.txt
```
A long figure in the hundreds is correct; a file whose longest line is under 100 characters is wrapped and wrong.

## Sources that work, verified on this machine

Probe a candidate board before it goes in `config/sources.json`: `references/adding-a-source.md` holds the probe recipe and the signs of a board that has quietly stopped carrying listings.

| Source | Adapter | What it gives | Notes |
|---|---|---|---|
| Workable job board | `workable` | JSON search API over every employer hosted on Workable, with `workplace=remote` and `location=us` applied server-side | Added October 21, 2026 and the single best source for his families: part-time and contract content, SEO, copywriting, editing, marketing, social, VA and support work, from real employers, with the employer's own application form behind each job page. Pay sits in the description or benefits block and is parsed from there. The search endpoint rate-limits by IP for hours at a time (October 23-25, 2026); when it refuses, `collect.py` falls back to polling the cached employer boards in `config/workable-boards.json` (43 boards), every row carrying `application_url`. |
| SmartRecruiters | `smartrecruiters` | Public search over every employer hosted on SmartRecruiters, one keyword per request, plus a per-posting detail read for pay and engagement type | Added October 25, 2026, the morning Alignerr was excluded and the Workable search was banned. Every row is the employer's own application page (careers.<company> / jobs.smartrecruiters.com/<company>), the same direct-apply class as Workable and the employer ATS boards. The endpoint ignores paging parameters, so depth is keyword breadth: the baseline walks the term lists and the top-up round expands them with modifiers. Rows are filtered to fully remote US postings in his job families inside the freshness window before any detail read. |
| Alignerr | `alignerr` | DISABLED, DO NOT RE-ENABLE | Excluded by Vinny, October 25, 2026: he does not want jobs from Alignerr. The host is blocklisted in `rules.json` (`blocklist_hosts`) and disabled in `sources.json`, so no Alignerr row can pass prefilter even if it reaches raw.jsonl through another path. |
| Employer ATS boards | `ats` | Greenhouse, Ashby and Lever APIs from `config/companies.json` | The direct-apply class. Every row carries the employer's own apply URL and there is no account wall. Remote rows only, `ats_per_company` cap. Verified live: 132 remote rows from seven boards, 18 of 26 sampled candidates live. Add companies by slug after checking the slug returns jobs. Agency and flex-creative boards added October 19, 2026 after probing live: Greenhouse `asg`, `boldly`, `motus`, `newsweek`; Lever `silverbackstrategies`, `lwolf`, `seerinteractive`. Agencies are the better bet for hourly and contract creative work than the big product companies. |
| RemoteOK | `remoteok` | JSON, fresh, salary fields on some rows | Its `/l/<id>` apply link redirects straight back to the same listing, so it is not a path off the board. Only rows whose API carries a real `apply_url` survive verification |
| Remotive | `remotive` | JSON, salary and candidate location | The public endpoint returns a small set now, roughly 13 rows, so treat it as low volume |
| Jobicy | `jobicy` | DISABLED, DO NOT RE-ENABLE | Excluded by Vinny: every job page demanded an account signup and data collection before the employer form, and its listings shipped as signup links. The host is blocklisted in `rules.json` as well as disabled in `sources.json`. |
| Himalayas | `himalayas` | JSON, richest pay data and US location restrictions | Treat it as a pay and location source, not an apply-path source. The API returns no `applicationLink` on most rows, and a 980-row pull produced zero rows carrying one, so every Himalayas candidate arrives with `apply_url` empty. Its own job pages sit behind a Cloudflare challenge and its Apply button is `himalayas.app/signup/talent`, which is an account wall. **The feed carries over 128,000 live postings; `himalayas_pages` reads 40 pages of it, which is under one percent and only the newest day. Set `himalayas_max_offset` (30,000 in production) so `collect.py` pages deep by offset before concluding the market is thin.** `scripts/pull_himalayas_deep.py` is the standalone puller for the same job. Then resolve each in-band row to the employer's own page with `references/employer-apply-resolution.md`. A resolver hit on a careers index (`employer.com/careers/`) is not an apply path and is now rejected by `common.is_apply_index()`. |
| We Work Remotely | `wwr` | RSS, root feed only, carries `expires_at` and region fields | Category feeds are 403 and parse errors, disabled on his order October 18, 2026. Listings that are not fully open show "Create an account to view full job details" and Apply points at `/job-seekers/account/register`, so only postings whose feed body carries the employer link survive the apply-path gate |
| Working Nomads | `workingnomads` | JSON, company, tags, location, date | No pay field, so pay has to come from the page or be flagged |
| Arbeitnow | `arbeitnow` | JSON with a remote flag | Europe-weighted, low yield for US-remote work |
| NoDesk | `nodesk` | RSS, curated | Low volume, occasional good fit |
| HN job feed | `hnrss_jobs` | RSS | Mostly stale by the time it lands |
| HN Who is hiring | `whoishiring` | The current monthly thread's comments | Best source for contract and founder-direct work, but the thread ages: check each comment's own date against the freshness rule |

Dead or unusable, do not add and do not research again: ProBlogger, whose board at problogger.com/jobs is live but gate every application behind candidate registration, which is an account wall and fails his rule (its RSS also returns zero items), JobSpresso feeds return zero items, BloggingPro and Remote.co refuse or hang, Reddit blocks the JSON endpoint, Wellfound is JS-walled, We Work Remotely category pages return 403 and parse errors (root feed only), YC Work at a Startup is login-walled, The Ladders is stale, FractionalJobs.io is executive-skewed, HireMyMom is paywalled, and Upwork, Terac, Jooble, FlexJobs, Contra and micro1 are permanently excluded by his orders. All of these hosts are blocklisted in `rules.json`, so anything that leaks through from another feed is dropped rather than shown.

## Pitfalls, learned the hard way

- **The renderer owns the report layout, and it gates on it.** A spacing or legibility complaint is fixed in `report.py`, never by reflowing the file by hand, never by instructing a cron agent to reformat the output, and never by a prompt that asks for a layout the code does not produce: a prompt is a hope, the renderer is the guarantee. The layout gate refuses to write the file when any lead is missing one of the `Role`, `Pay`, `Apply`, `Fit`, `Verification` sections or when any line packs two facts together with a pipe, so a flattened report cannot be produced at all. If a layout change is ever made, prove it by rendering a finished day's data into a scratch folder and checking every lead carries all five section headers, that there are no pipe lines, and that the longest line is still in the hundreds.
- **A layout order authorizes the layout and nothing else.** Fixing spacing does not license touching pay formatting, date formatting, grammar, or any other field in the same file. Those are separate changes and need their own instruction; bundling them in is how a one-line request becomes a rewrite he did not ask for.
- **The picker must tier with the same function the renderer enforces, and it must spread across boards.** On October 22, 2026 `select.py` tiered picks with `band_state()` while `report.py` tiered them with `classify_path()`. Inizio's $16.10-$29.90/hr role and Blueprint's $50-$55/hr role read as in-band in one and as salaried above band in the other, so selection spent the in-band supply and then handed the renderer six above-band leads against a cap of four, and the render died. The same file also filled strictly by rank, so a target-count list clustered on three boards and failed the four-source gate even though the pool held 78 usable rows across twelve. Both are fixed: `tier()` calls `classify_path`, and `fill()` takes the board that has contributed least before any board gets a second pick.
- **An employer homepage is not an apply path, and `is_apply_index()` used to miss it.** The check normalized a root path to `/`, which is not in `APPLY_INDEX_PATHS`, so `https://www.complex.com/` and `https://blueprintprep.com/` shipped as verified leads on October 22, 2026. The path now normalizes to `""`, which is in the tuple. Add a bare root to the same test whenever a resolver is changed.
- **The scripts directory contains `select.py`, which shadows the standard library `select`.** Any module that imports socket with that directory on `sys.path` dies with `partially initialized module 'socket'` and a circular-import trace. `pull_himalayas_deep.py` now strips its own directory from `sys.path` before importing requests. Do the same in any new standalone fetcher, or the deep pull cannot run.
- **Do the count arithmetic in this order, before selecting.** The verified pool is the only ceiling. Count the usable rows that are live and carry a direct employer apply path, then fill twenty from them in quality order. If that pool holds fewer than twenty, the run has not finished collecting: widen the sources, re-resolve, re-verify and re-select. `topup.py` does the widening automatically, and the Workable employer boards are the fallback when the Workable search endpoint rate-limits. A remaining gap is supply to be closed against the boards, never a reason to ship seventeen.
- **Fixing the pipeline means editing the scripts, not hand-building the day's list.** When he says the run is broken, the deliverable is the changed code path that produces tomorrow's list. Hand-assembling twenty leads from feeds and browser searches leaves the same bug in place and reads as ignoring the instruction, however good the resulting file looks. Build the artifact only after the scripts produce it.
- **Test a resolver change on a handful of known rows, never by re-running the pipeline.** A full collect, filter, resolve and verify cycle costs minutes, so three design iterations priced at full runs is how a small edit consumes a session. Call the one function against five known-good and five known-bad rows, confirm the decisions, then run the pipeline once. Do not quote a duration for a fix you have not already executed; an unproven "two minutes" is a promise he times, and the miss costs more than the work saved.
- **A web-search resolver is best-effort, not the dependable path.** Bing's RSS output and DuckDuckGo Lite both degrade automated queries, returning dictionary pages or a challenge page after a burst, so a resolved count that collapses often means the search backend rather than missing employer pages. Ask the ATS APIs directly (Greenhouse, Lever, Ashby) by company slug and title first, treat open-web search as the fallback, and the browser sweep as the last resort.
- **A cron status of ok is not a delivery.** The scheduler reports the process exit, not the email. A run that hits its tool-call limit mid-pipeline can come back "ok" with no report rendered, no mail sent and no notification, and its own final message may describe a state that contradicts the files on disk. Check the run folder, the report timestamp, and the inbox readback before telling him it shipped.
- **A lead that shipped before will come back if the ledger only stores the feed row url.** On October 19, 2026 four leads from the previous day's report reappeared, because `report.py` recorded only rows it could match by row url, so email-only picks were never written. The ledger now stores `apply_url` and `apply_email` too, `prefilter.py` holds on any of the three identities, and `ledger_held()` also reads earlier days' report files and `selected.json` files, so a gap in the ledger can no longer repeat a lead.
- **Bare "Remote" on an employer's own ATS board is a US posting.** Vendors publish `Remote` with no country, and the strict geo rule was dropping US agencies on their own Greenhouse, Lever and Ashby boards. Those rows are accepted with the basis recorded; bare "Remote" from an aggregator still fails the geo gate.
- **Lever publishes pay in `salaryRange`, not in the description.** The adapter now reads `min`, `max` and `interval` and builds the pay line, which is how Silverback's $90,000 to $103,000 SEO Manager reaches the report instead of being dropped as no-pay.
- **A share cap computed from the pre-cull count never binds.** Capping a subset to a fraction of `len(kept)` uses the length before the cull, so the cap equals the number of rows that survive and nothing is removed. Count the rows that are **not** being capped first, then take `ceiling = others * share / (1 - share)`; that lands the final pool on the intended share instead of one row short of useless.
- **A missing report at the scheduled minute is usually a run still in flight, not a skipped job, and the diagnosis is two calls, not ten.** A full run takes roughly eight to twenty minutes, so when he asks why nothing arrived, spend at most two read-only calls: `cronjob_manage action=list` for `last_run_at` and `next_run_at`, then one query at `~/AppData/Local/hermes/cron/executions.db` (`SELECT status, claimed_at, started_at, progress_at, pid FROM executions WHERE job_id='<id>' ORDER BY rowid DESC LIMIT 3`). A row still `running` with a fresh `progress_at` means the job is alive, and the answer goes to him in that same turn: running since the fire time, this far along, nothing sent yet. Do not keep grepping logs, do not open the pipeline, do not run a probe before answering. Once the run ends, the delivered text is in `~/AppData/Local/hermes/cron/output/<job_id>/<date>_<time>.md`, which is the record to quote. `~/AppData/Local/hermes/logs/process-results/proc_*.json` names the exact sub-processes the run launched (each carries `owner_task_id` of `cron:<jobid>:<execution>`), which is the fastest way to say where the run actually is, e.g. a deep collect still going. Never call a job skipped from the job list alone while the clock sits inside its run window.
- **The one-board share ceiling is a fraction of the final pick count, so a legitimately short list can fail it while every pick is honest.** `report.py` tests `picks from that board / len(picks) > 0.45`, not picks against the target. Eight Workable picks out of fourteen is 57 percent and the render refuses even though eight of twenty would have passed. Fix it by swapping the over-ceiling picks for the next-best rows from other sources (they keep the count and the spread, and the cap arithmetic is unchanged), or by dropping picks until the ratio holds, never by reordering or by shipping the refusal as the answer. Do the division yourself before running the render, because the refusal arrives as one line that names the board and not the arithmetic.
- **The in-band supply count is fixed the moment collection ends, so compute it before promising a number.** `payfix.py` cannot recover pay from Workable rows: it fetches the page fine and reports "no pay statement found" on essentially every one, because Workable hides rate in a field the public page does not render. Those rows stay `unrated` no matter how many times it runs, so they can only ever fill the three no-pay slots and never the in-band target. And an in-band row that clears the band but lands on a hard anti-signal (structural or mechanical engineering, clinical, legal) is not usable in-band supply and has to be dropped before the arithmetic. Count in-band rows that are live, direct-apply and in his families, add 4 and 3, and that sum is the honest ceiling for the day; anything above it is padding and he reads it as padding.
- **Write the `selected.json` builder to a scratch script file and run the file; never inline a long heredoc full of prose and apostrophes.** A `<<'PY'` block carrying dozens of `fit` and `gap` sentences dies with a shell quoting error mid-write, and the failure looks like a Python problem when it is the shell. `write_file` the builder to the scratch directory, assert every URL against `verified.jsonl` inside it, print each added row's source and company as it goes, then run it with the 3.11 interpreter.
- **A stale render is worse than no render.** If verification ran again after the report was written, the report is describing a pool that no longer exists. Compare file timestamps and pick URLs against `verified.jsonl` before sending; rebuild rather than patching prose around the mismatch.
- **A board listing is not an apply path.** The old `record()` fell back to the board's own URL when a posting carried no external link, which is how a report full of signup pages got delivered. The fallback is gone: no employer link and no application email means the lead is unverified and cannot ship.
- **Remote is a location fact, not a word in the body.** ATS postings for San Francisco or New York still say "remote" somewhere in the benefits, so a body-only check passes city roles. `prefilter.remote_confirmed()` requires remote/anywhere/worldwide in the location, a country-wide location, or explicit fully-remote wording. Applied October 18, 2026 it cut 94 live leads to 56 genuinely remote ones.
- **Junk mailboxes are not application emails.** `security@`, `abuse@`, `privacy@`, `legal@`, `accommodations@` and free-mail domains (gmail, yahoo, outlook) do not count as the apply path. The first run under the new gates shipped `user@example.com` three times before this filter existed.
- **A board's apply button can be an account wall in disguise.** RemoteOK's `/l/<id>` redirect returns to the same listing; WWR's Apply points at its own registration page. Resolve the target and check the final host before believing the apply path is direct.
- **A direct application email satisfies the path rule by itself,** and he prefers it. Feed the address as `Apply by email` in the report rather than inventing a URL.
- **A dead page with a contact email is still dead.** The email shortcut must not upgrade a posting whose own page says it is closed.
- **Twenty is a target, not a licence to pad.** With the apply-path and source-spread gates in place, a thin day ships a short list that says so. A padded list gets rejected outright.
- **Never ask him which constraint to relax, and never stop under the target while the pool can fill it.** On October 22, 2026 the run shipped 16 of the 20 he ordered, and when he said that was not 20 the model asked him to choose which rule to bend. He called the question itself the failure, and he was right: the count is the deliverable and the tradeoff arithmetic is the agent's job. Before selecting, enumerate every live direct-apply row by money path, add the caps that actually bind, and if that sum is under the target go back to the pool and the sources until it is filled. The shipped shortfall that day was not supply, it was the caps stacking: `max_unpaid_picks` 3, `max_above_band_picks` 4 and eight per source, against a pool that held 78 live direct-apply rows.
- **Judge the in-band share over the picks that state pay.** Both share gates divided the in-band count by every pick including unpaid ones, so a list carrying its full unpaid allowance could not clear 60 percent however much in-band work it also carried. Unpaid picks are capped on their own line; the share is computed on paid picks only.
- **A short list is the end of the diagnosis, not the diagnosis itself.** Before shipping five when he asked for twenty, state which of the two numbers caused it: the usable in-band supply, or `max_above_band_picks`. He reads a five-lead file as the pipeline failing, so the message that ships it must carry the pool arithmetic and the one decision that would change it. On October 21, 2026 the report explained its four leads well and was still the wrong deliverable: the pool was thin because the sourcing was wrong, and the fix was two new sources, not a better apology.
- **A repeat is a repeat even when the URL is new.** Dedupe on company plus role across every delivery channel, not just the ledger, or a role he already saw comes back under a fresh apply link and reads as carelessness.
- **The money floor is code, not prose.** On October 20, 2026 the report shipped a $5-6.50/hr medical VA and a $7/hr customer service role with the disqualifier written next to them, because the floor lived in the flag text and nothing in the pipeline rejected a low rate. `prefilter.evaluate()` now drops any hourly rate whose stated ceiling is under `wage_floor_hourly` ($17.00, the NY minimum wage) and any lead whose monthly ceiling is under `band_min_monthly` unless it is the $80k-plus 1099 path, and `report.py` refuses to render either case even when `selected.json` was built by hand. The floor is applied to the top of a stated range, not its bottom: a posting that says "$20 to $40 an hour" can pay above the floor, and testing the minimum threw away every honest range, which is how hourly work is priced. Never annotate a sub-floor lead and ship it: a lead that needs a pay apology does not belong on the list. Vinny's record is an access constraint, never a reason to lower his price.
- **A pay line can be a revenue line.** "$500,000+ per month in revenue" and "$1M/month in ad spend" both parsed as salaries on October 22, 2026 and put a copywriting role in the report at $41,667 a month. A bare dollar figure with no unit now only counts when a pay label sits beside it and no revenue, spend, sales, funding or budget wording does; `max_plausible_annual` ($400,000) then drops anything that still reads as a business number. The `$70,000k-$80,000k` typo is also read as $70,000 to $80,000 instead of $70 million.
- **A careers index is not a job page.** `https://www.mercor.com/careers/` resolves fine, returns HTTP 200 and passes every liveness check, but it is the employer's job index: the reader still has to find the role. `common.is_apply_index()` now rejects bare `/careers`, `/jobs`, `/openings` and similar paths in `has_direct_apply()`, `verify.py` and `report.py`, so a resolver that only found the careers page produces an unverified lead rather than a shipped one.
- **The same role posted per city is one lead.** A virtual-assistant employer published "Virtual Assistant - Omaha", "- Tulsa", "- Milwaukee" and six more, identical apart from the city, and eight of them reached the pool. `common.dedupe_key()` strips a trailing location that matches the row's own location, plus city and metro acronyms and working-arrangement notes in parentheses.
- **Titles name the job family, so block the wrong families by title.** The old include list accepted `manager`, `analyst`, `specialist`, `consultant`, `research`, `integration`, `implementation` and `ops`, which is how Renewals Managers, Underwriting Managers, Policy Analysts and DevOps Engineers (the `ops` token) reached a job list about writing. The include list is now the families he applies to, the block list names the families he does not, and `strong_title_patterns` / `adjacent_title_patterns` carry the ranking weights. `allow_title_patterns` exists only so "Prompt Engineer" is not caught by the generic engineer block.
- **A blocked page is not a verified lead.** `403` and `429` mean the check failed, not that the job is closed. `verify.py` retries once through scrapling and once more through the stealth browser with `--headless`, which takes about a minute per page, so use it on a shortlist and not on the whole run.
- **Rate limits are self-inflicted.** Four workers is the default for a reason. Bursts of six parallel fetches get `429`s from most boards, and the same host answers fine seconds later.
- **Pay hides in odd phrasings.** Jobicy prints `$106,000 US market range (per year)`, HN posts print `$3,500-$5,000 USD/month`, and per-task work prints `US$1,000 per task`. `find_pay_in_page` handles these; do not "simplify" it back to a single regex.
- **`US$1,000` and `$1,000` are different strings.** The currency-prefixed form needs the trailing unit to name the shape of the work, so `task`, `gig`, `video`, `post`, `deliverable` and `batch` are all units.
- **The RSS entity trap.** Feeds carry HTML entities that strict XML parsers reject. `clean_xml` converts them to numeric references without touching the five XML built-ins or escaped markup; do not replace it with a blanket `html.unescape`, which unescapes `&lt;p&gt;` and breaks the parse.
- **HN comments are not job pages.** A Who is hiring comment is verified through its own apply link or its direct application email, which is why `verify.py` accepts a stated application email as a working apply path.
- **Freshness kills more leads than anything else.** 310 of 1,505 postings were dropped as stale on the first real run, and monthly HN threads produce comments that are weeks old. Always check the comment or post date, not the thread date.
- **The geo rule is strict on purpose.** His words are that unconfirmed US eligibility is a disqualifier, not a caveat, so a bare "Remote" from an aggregator with no US signal in the posting gets dropped. The one exception is an employer's own ATS board, where a bare "Remote" is that employer's own US posting. `us_eligibility_signals` exists to recover the ones whose description does confirm US eligibility.
- **Feed rows can arrive missing the fields the report quotes.** Askable and iMerit type rows come through with no company name at all, and a pay figure can land in the row with no record of where it came from. Fill both from the URL and from the row before rendering, because every line of prose beside a lead is checked against the record and never against the posting: `document-delivery-formatting` carries the general form of that rule under its document-shape section.

## Supply: where the leads come from now

**Before calling any shortfall a supply problem, prove the run actually read the market.** A feed's page cap is not its inventory: Himalayas reports `totalCount` over 128,000 and the default 40-page adapter pull reads under one percent of it, which then reads as "there are no in-band jobs today." Compare rows pulled against `totalCount`, and page deeper with `scripts/pull_himalayas_deep.py` before telling him the work does not exist. He does not accept a scarcity claim from a run that only skimmed a feed, and he is right not to.

**The supply problem is an apply-path problem first, and the ATS adapter is the fix.** Jobicy, RemoteOK and WWR all route their apply buttons through an account wall. RemoteOK's `/l/<id>` redirect lands back on its own listing, WWR's Apply lands on `/job-seekers/account/register`, and Jobicy demands a signup before the employer form. The `ats` adapter answers that directly: it reads employer boards straight from Greenhouse, Ashby and Lever, so every row carries the employer's own apply URL. On its first test it returned 132 remote postings from seven boards, and every apply link was the employer's own. Growing `config/companies.json` is now the primary supply lever; run `python probe_ats_slugs.py <slug> [<slug> ...]` to see which vendor serves a company and how many postings it carries before adding the slug, and keep it to companies that hire remote in the US. Agencies and flex-creative shops are worth more than big product companies here, because they post hourly, part-time and project work instead of one salaried band per role. `references/apply-path-and-sources.md` holds the full recipes and the board-by-board gating notes.

Other levers, in order of value:

The standing spec wants the majority of every list inside his $1,000 to $2,500 a month band, and the free aggregators do not deliver that supply: a full run on October 17, 2026 pulled 1,505 postings from ten sources and produced roughly 136 live leads, of which only a handful were hourly, part-time or 1099. The fix is sourcing mix, not rules, and the second money path points at exactly where to look:

- 1099 and contract platforms, and contract-shaped postings buried in the salaried boards. Filter for `1099`, `contract`, `contractor`, `freelance`, `independent contractor`, `per task` and `per project` in the posting text.
- Second-chance and no-background-check employers. The boards that cover this (Honest Jobs, Jobs for Felons Hub, and similar) are mostly login-gated or publish blog content instead of listings, which was tested on this machine: `jobsforfelonshub.com/feed/` returns articles, not jobs, and `honestjobs.com/jobs` returns 404. So the practical lever is `second_chance_signals` run against posting text on the sources that already work, plus company-level research into known second-chance employers.
- Reject the scam end of it: a posting that advertises "no background check" and also asks for a fee, a crypto deposit, a Telegram or WhatsApp contact, or pays in commission only is a trap, not an opportunity. The pay-to-apply and upfront-fee exclusions still apply without exception.

Do not pad the list to fake the composition, and do not silently reweight the band math to make a salaried role look in-band.
