---
name: remote-job-sources
version: 1.0.0
author: Hermes Agent
license: MIT
description: Use free no-auth remote job APIs and RSS feeds for searches.
metadata:
  hermes:
    tags: [jobs, remote, api, rss]
    related_skills: []
---

## When to Use

When Vinny asks to search remote jobs, monitor feeds, or look up listings from free no-auth sources.

# Remote Job Sources (no-auth)

## SOURCE POLICY, NON-NEGOTIABLE (Vinny, repeated instruction)

**Jobicy is the source. Use it first, and use all of it before anything else.**

### Step 1, mandatory, mechanical, before any other fetch

```bash
python C:/Users/<user>/AppData/Local/hermes/profiles/fifi/skills/research/remote-job-sources/jobicy_pool.py --pick
```

That script is the pool. It pulls the Jobicy REST API (paged via `nextCursor`, plus per-industry sweeps), keeps US-eligible listings, drops every listing already sent in an earlier report, and writes:

- `pool_pick.txt`, **this run's candidate window.** The 8 best-fit unreported Tier 1 and 12+ best-fit unreported Tier 2 listings, each with its `jobicy.com/jobs/...` apply URL. The two tiers total 10 jobs: 5 Tier 1 + 5 Tier 2, and every Tier 1 slot that cannot be filled is handed to Tier 2, so the run's line reads e.g. `Report exactly 0 Tier 1 + 10 Tier 2 = 10 jobs`. Report that split from this window and nothing from outside it. Build the document from this file.
- `pool_tier1.txt`, Part-Time / Contract / Freelance / Temporary, monthly USD <= $2,500 when pay is stated, unreported only
- `pool_tier2.txt`, Full-Time at $90,000+/yr USD, or a contract/1099 posting worth $90,000+/yr equivalent (a contract paying full-time money is Tier 2 work, not a capped part-time job), unreported only
- `pool_all.json`, same data, machine-readable
- `reported_ids.json`, ledger of every job ID already reported. `--pick` writes the whole window into it as reported, so a repeat cannot happen even if a later step is skipped.
- `pool_pick_ids.json`, today's window, used by `check_repeats.py`.

Read those files and build the report from them. Every listing in the pool already carries a `jobicy.com/jobs/...` apply URL, use that URL as the apply link. Do not substitute a company ATS URL for it, and do not re-search the web for a listing already in the pool.

**If the pull fails** (the script exits non-zero with `FAILED PULL`, or Jobicy rate-limits it), there is no pool and there is no report. Do not send an email, do not build a list from memory or an earlier day, do not substitute web-search results. Report the failure on Telegram with the script's own error line.

### Profile gate, non-negotiable (Vinny, 2026-11-08)

The 2026-11-08 report shipped five tutors, a resident-physician admissions consultant and four sales/legal roles. Vinny is an AI systems builder: the pool now drops, by title, every

- tutoring / teaching / K-12 / curriculum / academic-admissions role,
- interpreter / translator / linguist / transcription / localization-review role,
- medical, clinical, nursing, dental, therapy or other licensed-care role,
- attorney, counsel, paralegal, law-school or compliance-officer role,
- accountant, underwriter, auditor, payroll, tax or controller role,
- account-executive, sales, quota, partnership, channel or business-development role,
- recruiter, talent-acquisition, compensation or benefits role,
- clearance-gated role (clearance, top secret, DoD/DoW, federal civilian) or any title requiring a licence,
- and any title naming a non-English language, because he does not work in it.

The gate lives in `jobicy_pool.py` (`OFF_PROFILE`, `NON_ENGLISH`) and runs before tiering, so an off-profile listing cannot reach `pool_pick.txt` at any pay. Candidates are then ranked by profile fit (`ON_PROFILE`: AI, agents, automation, LLM, prompt, RAG, Python, API, integration, platform, infra, DevOps, data engineering, solutions/forward-deployed engineering, developer relations, technical writing, SEO/GEO, content ops, email deliverability, technical support), then freshness, with one listing per company so a single employer cannot fill the window.

**A report containing any of the role types above is a failed run**, even if the listing came from the window. If the fit gate and Jobicy's supply leave a tier short, report the shortfall, never pad a tier with an off-profile role, a repeat, or a listing from outside the window.

### Repeat rule, non-negotiable (Vinny, 2026-11-08)

No job may appear in two reports. The same Jobicy listings came back three days running because the pool was rebuilt but nothing remembered what had already been sent. If a listing's ID is in `reported_ids.json`, it is not reported. Do not re-list it because it is still open, still a good fit, or because a tier is short, report the shortfall instead. Never edit or delete `reported_ids.json` to make room, and never work around it by re-labelling a repeat job.

### Step 2, only if a tier is still short

Fill the remaining slots from another no-auth source (Himalayas API, Remotive API, RemoteOK) and label that listing's source in the document. The Jobicy pool entries always come first and are never dropped to make room for another source.

### Banned source

**WE WORK REMOTELY IS BANNED.** No `weworkremotely.com` fetch, no API, RSS, category feed or listing page. No listing sourced from it. No apply link pointing at it. Not as a primary source, not as a fill-in, not as a fallback, not once. If a listing's apply URL points at weworkremotely.com, drop the listing.

### The check before the email goes out

```bash
grep -c "weworkremotely" <report file>   # must be 0
grep -c "jobicy.com/jobs/" <report file> # must be the count of Jobicy-sourced listings, not 0
python C:/Users/<user>/AppData/Local/hermes/profiles/fifi/skills/research/remote-job-sources/check_repeats.py <report file>  # must exit 0
```

`check_repeats.py` fails when a report carries a Jobicy ID that is not in today's window, or one that was reported on an earlier day. Any repeat is a failed run, rebuild it from `pool_pick.txt` before sending.

A report with zero `jobicy.com/jobs/` links, or any `weworkremotely.com` link, is a failed run, rebuild it from the pool before sending.

## Jobicy endpoints (what the script wraps)

- REST: `https://jobicy.com/api/v2/remote-jobs` (params: `count` max 100, `cursor`, `geo`, `industry`, `tag`, `level`)
- RSS: `https://jobicy.com/jobs/feed`
- Per-listing page: `https://jobicy.com/jobs/<id>-<slug>`

For GitHub-sourced remote jobs: github.com/topics/remote-jobs, remote-job-boards/* repos, curated awesome lists.

**HARDRULE: All jobs MUST be FREE to apply too. Preferable, I would like to be able to email them my resume and cover letter, but this in NOT  requirement. This is NON negotiable: All jobs MUST be FREE to apply too.

## IF you can find all of the job offers using "Jobicy" That would be great. Jobicy makes it easy to apply for these jobs. 

## Candidate profile (for job matching)

Resume: `C:\Users\<user>\OneDrive\Desktop\RESUME_Vincent_Barreca_AI_Systems_Builder.docx`

Target roles: AI systems builder, agent automation, AI infrastructure, technical SEO/GEO, remote full-time/contract/consulting. Immediate start.

Job constraints/preferences: Prefer remote-only 1099 roles; W-2 background checks likely an issue. Part-time cap at $2,500/month, OR full-time only at $90k+/year. All remote. Not a teacher, tutor, translator, clinician, lawyer, accountant or salesperson; licence-gated and clearance-gated roles are out.

Core strengths: agent orchestration, multi-model routing (Ollama, vLLM, llama.cpp/GGUF, OpenRouter), scheduled unattended automation (26 jobs), email-driven task queues, deterministic workflow control/verification, technical SEO/GEO on a 210-page topical authority property, email deliverability engineering (SPF/DKIM/DMARC).

Tooling: Hermes Agent, OpenClaw, Claude Code, MCP, webhooks, cron, Python, SQLite, REST, SMTP, DNS.

Background: independent entrepreneur/systems builder since 2004; independent AI systems builder since 2026. Remote or Ronkonkoma NY.

## Preferred lead types (from 2026-10-27 reports)

1099-friendly roles in: AI automation/agent workflow building, technical content writing, SEO/GEO and AI search, content operations, email marketing/deliverability, research and annotation, data tasks.

Filters learned: no recorded video intros, no mandatory degrees, no pay-to-apply, remote-only, US-eligible, working apply path verified live, and fresher postings preferred (14-day window).

Part-time target band $1,000-$2,500/month; full-time only at $90k+ and accepted as 1099 with coverage tradeoff considered.

## Tier coverage rule (mandatory, Vinny 2026-11-08)

Every curated list is 10 jobs, split 5 Tier 1 (part-time/1099, $1,000-$2,500/month) + 5 Tier 2 (full-time $90k+/yr, or contract/1099 worth $90k+/yr). `pool_pick.txt` states the split for the run, e.g. `Report exactly 0 Tier 1 + 10 Tier 2 = 10 jobs`.

**Short Tier 1 is paid for by Tier 2, not by a shortfall.** When Tier 1 has fewer than 5 viable roles, report all of them and fill the remaining slots with the next best Tier 2 leads so the report is still 10 jobs. State the real split in the header (for example `0 Part-Time/1099 | 10 Full-Time $90K+`) so Vinny can see the swap. Only when Tier 2 supply also runs out does the report come in under 10, and then it says exactly how many are missing.

The substitution never relaxes anything else: the extra Tier 2 entries still have to pass the profile gate, still be free to apply, and still be unreported.

