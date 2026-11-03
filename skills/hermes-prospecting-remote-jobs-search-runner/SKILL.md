---
name: remote-jobs-search-runner
description: Run and deliver Vinny's verified remote-job pipeline.
version: 1.0.0
platforms: [windows]
metadata:
  hermes:
    tags: [jobs, remote, job-search, screening]
    category: prospecting
---

# Remote Jobs Search Runner

Deliver 20 new, verified remote job leads in priority order, every run. The live rules and resume profile are in `~\AppData\Local\hermes\skills\prospecting\remote-jobs-search\config\rules.json` and `config\resume.json`.

## Non-negotiable gates

- Use only an employer application page, employer ATS form, or genuine application email. Never use an account wall, board listing, generic careers index, or Jobicy.
- Alignerr is excluded by Vinny (October 25, 2026). Its rows are blocklisted in `rules.json` and its source is disabled; no Alignerr lead can ship and nothing here re-enables it.
- Keep the remote, US eligibility, freshness, resume-fit, duplicate, job-family and wage-floor rules.
- Twenty picks every run. Selection fills the list in quality order, in-band paid work first, then hourly and flexible work, then salaried roles above the band, then rows with no stated pay. There is no per-source, per-company or source-count cap standing between the verified pool and a full list.
- Never pad a report with a board listing or a dead page. Twenty means twenty rows that are live at the employer's own application page, which the verified pool already establishes.

## Run sequence

From `~\AppData\Local\hermes\skills\prospecting\remote-jobs-search\scripts`, run:

```powershell
python run.py --date YYYY-MM-DD
```

This command collects, filters, resolves employer apply paths, verifies pages, recovers pay from direct employer pages, selects a baseline, and runs bounded top-up collection (three widening rounds: Workable at depth, SmartRecruiters keyword expansion, the forced Workable employer-board sweep). It does not email anything.

If `selected.json` still holds fewer than 20 picks after `run.py` finishes, run the top-up once more and re-select:

```powershell
python topup.py --date YYYY-MM-DD
python select.py --date YYYY-MM-DD --force
```

That is the whole supply fix. Do not improvise. No ad-hoc harvest, probe, resolve or merge scripts, no manual `collect.py` runs outside `run.py`/`topup.py`, no scraping job boards by hand, no widening scripts of your own. On October 25, 2026 the run improvised for 75 minutes, the cron supervisor killed it, and the day shipped nothing. The scripted top-up is the widening; if it cannot reach twenty, render nothing and report the pool arithmetic.

Read the selected leads and packs. You may improve only `fit`, `gap`, `legit`, `risk`, and `effort` in `selected.json`. Do not add URLs absent from `verified.jsonl`, alter money paths, or replace the deterministic selection.

Render and validate immediately before sending:

```powershell
python report.py --date YYYY-MM-DD
python validate_delivery.py --date YYYY-MM-DD
```

If the verified pool holds fewer than 20 usable rows, `run.py` has already run the top-up; run `topup.py --date YYYY-MM-DD` once more (the three rounds are the Workable employer-board fallback, SmartRecruiters at keyword depth, and the rest of the direct-apply supply), then re-select with `select.py --force`. Never pass `--allow-short`. A short render is a failed run, not a deliverable, and the answer is more collection and resolution until the list holds twenty.

## Delivery

Email the rendered `report-YYYY-MM-DD.txt` as an attachment using email-sender. Read it back through IMAP and confirm the attachment byte count. Then send one short Telegram note to read the email.

Before declaring any shortfall, run the top-up and the employer-board fallback. A run that ships nineteen has not finished collecting, and the fix is more collection and resolution, not a smaller number. Do not send until `validate_delivery.py` passes.

## Extra sources, after the report

The 10am cron entry is one job, and every extra source is an extra pass inside it. The order is fixed: the twenty-lead report is rendered, validated and emailed first, and each additional pass runs after that send. A slow, blocked or failing pass can never delay, re-render or re-send the report.

Rules that hold for any source added here:

- Do not merge its rows into `selected.json`, `verified.jsonl` or the report. `report.py` refuses input that did not come through collection and verification, and rows typed in by hand are invented rows. An extra pass ships as its own short email with its own links.
- The employer-apply gate applies to every source, not only the pipeline. A source whose apply button is a signup or login wall, or whose only link is a board listing, cannot supply a lead as it stands: the pass resolves the employer's own Greenhouse, Lever, Ashby, SmartRecruiters or careers page per candidate, drops what it cannot resolve, and reports the drop count. Never print an aggregator signup URL as an apply link.
- Failure isolates to the extra pass. Nothing found, tools down, quota exhausted or a key missing means one short Telegram line naming what stopped it, saying the twenty-lead report is unaffected, and no email.
- Verify the price from the provider's own docs before wiring, and state the monthly arithmetic. "Free" usually covers the public read tools only, so check which tools the pass actually calls against the paid ones.
- The cron prompt names the exact tool names or scripts the pass uses, so the scheduled run does not improvise a different command.
- Removing a source is the same edit in reverse: strip its section from the prompt, `--remove-skill` anything attached for it, then stop. Deleting the provider's package, key file, workspace or the skills its installer dropped is a separate cleanup that needs its own order.

Current state: the 10am job runs the pipeline, then one Himalayas pass over the `himalayas` MCP server, free and keyless. The agent-data Job Search pass that preceded it was removed, so no API key, metered call or `job-search` workspace exists. Do not reintroduce it.

## Editing the cron prompt safely

```bash
hermes cron edit <id> --prompt "$(cat prompt.txt)" --add-skill <name> --remove-skill <name>
```

- Write the prompt to a file and pass it through `cat`. Command substitution strips trailing newlines, so compare the stored prompt to the file with `rstrip("\n")` on both sides rather than expecting an exact match.
- Read the prompt back out of `cron/jobs.json` and assert the stored text matches the file, plus that schedule, deliver target and the skills list are what you intended. The Skills line is the proof of what got attached.
- Use `--add-skill` / `--remove-skill` per skill. `--skill` with a rebuilt list silently drops any skill you forgot to carry over.

See `references/job-source-vetting.md` for the checklist that decides whether a candidate source is worth wiring, and what each source already vetted actually allows.
