# Agent Automation Toolkit

Scripts, scheduled jobs and skill definitions that run two AI coding agents, **Pi** on
Windows and **Hermes** on a Linux dev box, as a working automation system rather than a
demo.

Every piece of this repository exists because a previous run reported success that was not
true.

- A keyword report went out with the attachment missing, because the send was handed a path
  Windows Python could not resolve. `scripts/email-ops/imap_readback.py` now re-reads the
  inbox and compares the attachment's decoded byte length to the file on disk.
- A backup job failed for many consecutive runs behind a global pre-push guard, with an
  error that pointed at the repository rather than at the hook.
  `scripts/devops/hermes-backup-restore/scripts/hermes-backup.py` runs every git call with
  a timeout and a non-zero exit, so a failed push is a failed run.
- Aggregator "Apply" buttons pointed back at the aggregator, and the pipeline dropped
  in-band work as "no direct application path" even when the job existed.
  `scripts/job-search/resolve_employer.py` finds the employer's own posting, and `verify.py`
  fetches that page and classifies it live, dead, blocked or unknown, a blocked fetch is
  not a verified lead.

That rule, *verify before you report*, is the design constraint behind most of the code,
the cron jobs, and the skills. Jobs print nothing when healthy and something when not,
because a status line that is always printed stops being read.

## What is in here

| Path | Contents |
| --- | --- |
| [`scripts/`](scripts) | 92 runnable scripts (Python, Bash, Node), grouped by domain |
| [`skills/`](skills) | 281 skill definitions, 262 Hermes (200 active, 62 retired) and 19 Pi, each with its bundled `references/`, `scripts/` and `templates/` |
| [`crons/`](crons) | 34 scheduled jobs: expression, runner type, model, preloaded skills and the full instruction each one executes |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | How the two-agent system fits together |

Python 3.9+ with the standard library for most of it; `playwright`, `requests`, `scrapling`
and `weasyprint` only where a script says so. Bash for the shell helpers, Node 18+ for the
two `.mjs` files.

## How it fits together

Two agents share one machine profile. **Pi** runs on the Windows side and handles the
public sites and deployment work; **Hermes** runs in WSL with its own home directory, its
own cron scheduler and a Telegram gateway. Each side runs its own nightly self-backup,
pushing its home directory to a git remote (`hermes-backup.py` on Windows,
`hermes-backup.sh` in WSL), and `agent-change-brief-collect.sh` turns the week's commits in
the shared repository into a brief the other agent reads before it changes anything.

Three mechanisms do most of the work:

**A scheduler that distinguishes scripts from prompts.** Every job in
[`crons/hermes-cron-jobs.json`](crons) carries a `runner`. A `deterministic-script` job has
`no_agent: true`: it runs its script and nothing else, so it makes no model call at all.
That covers twelve of the thirty-four jobs, including both backups, the verifier prefills,
the harvest and refill scripts and the post-update health check. An `agent-prompt` job runs
its `instructions` in a session, and six of those run a script first that states the
verdict in its output, so the instruction can tell the agent to report one line and stop or
go ahead and do the work. The cheap half of every job stays deterministic.

**Silence as a signal.** Jobs print nothing when there is nothing to say. The cron treats
empty output as a silent success, so the Telegram channel stays quiet and the one job that
must always speak (`BRUSH FEFE'S TEETH`) is written to say so explicitly. That convention
is what makes a 34-job schedule readable instead of a stream of "nothing happened"
messages.

**Pre-tool-call hooks.** Three scripts in [`scripts/hermes/`](scripts/hermes) run before a
tool executes: one enforces a per-turn tool-call ceiling, one moves a stale scratch file
aside so a legitimate write is not refused, one strips hard-wrapping from delivered text.
The scratch guard ships with an end-to-end proof, `e2e_proof_scratch_guard.py`, which
reproduces the exact blocked write and shows it refused without the hook and landing with
it.

## Scripts

### Job search pipeline, `scripts/job-search/` (17 scripts)

A staged, resumable pipeline that collects remote AI/automation postings, applies hard
filters, resolves each posting to the employer's own apply page, verifies the posting is
still live *today*, and renders a report. Built because aggregator search endpoints
rate-limit and their "Apply" links point back at themselves.

| Script | What it does |
| --- | --- |
| `collect.py` | Stage 1, pull raw postings from every enabled source into `raw.jsonl` |
| `prefilter.py` | Stage 2, apply hard rules, rank survivors, log a reason for every drop |
| `resolve_employer.py` | Stage 2b, replace aggregator redirects with the direct employer apply URL |
| `verify.py` | Stage 3, fetch each posting's own page and classify live / dead |
| `payfix.py` | Stage 3b, re-open live leads with no pay figure and pull the salary line |
| `pack.py` | Stage 4, compress verified candidates into small packs for model judgement |
| `select.py` | Stage 4b, build a baseline selection so the list never depends on one model pass |
| `topup.py` | Stage 4c, widen supply and re-run the chain when the list lands short of target |
| `report.py` | Stage 5, render the final report from the model's picks |
| `validate_delivery.py` | Refuse delivery when a report does not describe the final verified pool |
| `run.py` | One command that runs collect → prefilter → verify → pack |
| `common.py` | Shared helpers, standard library only |
| `build_resume_profile.py` | Build a machine-readable profile from a resume PDF |
| `build_workable_boards.py` | Cache employer boards to route around Workable's IP rate limit |
| `pull_himalayas_deep.py` | Deep-paginate the Himalayas feed in parallel and dedupe by guid |
| `probe_ats_slugs.py` | Probe Greenhouse / Lever / Ashby slugs in parallel before adding a company |
| `seed_ledger_from_document.py` | Seed the cross-day ledger from a list delivered outside the pipeline |

### Hermes agent home, `scripts/hermes/` (35 scripts)

The scripts in the WSL agent's own `~/.hermes/scripts` directory: the cron workers, the
pre-tool-call hooks, and the operational jobs the schedule calls. These are what the jobs
in [`crons/`](crons) actually run.

| Script | What it does |
| --- | --- |
| `agent-change-brief-collect.sh` | Collects the last 7 days of changes to the shared agent backup repo and emits a diff summary for the other agents to read |
| `agent-memory-tutorial-to-html.py` | Parses the agent-memory tutorial source into HTML for WeasyPrint PDF output |
| `blogwatcher-cleanup.py` | Delete watched articles older than N days straight from the blogwatcher SQLite DB |
| `blogwatcher-cleanup.sh` | Two-phase cleanup: mark old articles read so they cannot be re-imported, then purge past the archival limit |
| `blogwatcher-fetch.py` | Query watched articles by date from the blogwatcher DB, optionally saving them to a file |
| `check_agentmail.py` | Cron gate for the inbox processor: prints unread threads when there is mail, prints nothing when there is not |
| `daily-data-backup.sh` | Mirrors the day's data folder into the private backup repo |
| `daily_outreach_refill.sh` | The outreach data side end to end: clean the sendable list, refill when the pool is short, stage the day's schedule, verify by read-back, print one summary |
| `dir_harvest_instabox.sh` | Runs the partner-directory contact harvest on a cloud box and pulls the results back, so the local 90-minute cron timeout stops being the ceiling |
| `e2e_proof_scratch_guard.py` | End-to-end proof for the scratch-path hook: reproduces the exact blocked write, shows it refused without the hook and landing with it |
| `harvest_clicks.sh` | Pulls click notices into the leads log and rebuilds the clicker groups; idempotent and sends nothing |
| `hermes-backup.sh` | Pushes agent config, skills, cron, memories and kanban to a private git remote |
| `ironpulse_email_2026-09-11.py` | One-off: mails a dated report file as an attachment |
| `launch-desktop.sh` | Launch the desktop app with `--skip-build` instead of repackaging every time |
| `no_hard_wrap_guard.py` | Pre-tool-call hook that strips hard-wrapping from delivered `.txt`/`.md` files |
| `osm_build_reminder.py` | One-shot reminder for a scheduled build session |
| `partner_directory_refill.sh` | Grows the partner/agency pool from agency directories, then pushes new domains through the scan and harvest chain |
| `partner_refill.sh` | Stages the partner batch for a same-day send, sourcing fresh prospects when the pool is short |
| `pinterest_dedup.py` | Hard gate for the Pinterest cron: prints already-pinned titles before writing, and enforces dedup against the planned posts file after |
| `pinterest_prune.py` | Keeps the last N days of Pinterest post files and deletes the rest |
| `pinterest_trends.py` | Pinterest public trend endpoints, no login, no cookies, for the daily Pinterest job |
| `pool_harvest_instabox.sh` | Splits a domain batch across cloud boxes, harvests on each, pulls every slice back and merges once with dedup |
| `refill_check.sh` | Measures the sendable prospect pool and says whether a refill is due, the deterministic half of the refill job |
| `restart-gateway.sh` | Restart the user-level gateway service |
| `sbt-tutorial-to-html.py` | Parses the all-caps tutorial format into HTML for WeasyPrint PDF output |
| `scratch_path_guard.py` | Pre-tool-call hook that moves a stale fixed-path scratch file aside so a legitimate write is not refused |
| `send_pinterest_email.py` | Emails the day's Pinterest file with a sent-marker, so the agent cron and the backstop cron can never double-send |
| `send_social_email.py` | Same idempotent emailer for the social questions file |
| `start-wsl-browser.sh` | Starts the dedicated headless Chromium on a non-default profile that the browser harness connects to over CDP |
| `tensorfeed_filter.py` | Strips recurring unwanted stories from the news feed before any report is written |
| `turn_tool_cap_guard.py` | Pre-tool-call hook that enforces a per-turn tool-call ceiling |
| `update_health_check.py` | Post-update health check that prints nothing when healthy and only speaks when something regressed, so it costs zero tokens |
| `weekday_verifier_prefill.sh` | Spends the weekday's free verifier credits ahead of time and writes the verdict cache, sends no mail |
| `weekend_verifier_prefill.sh` | Same prefill for the weekend credit pool |
| `x-algorithm-update-check.sh` | Watches a third-party repo for new commits and releases, silent when nothing moved |

### Email operations, `scripts/email-ops/` (3 scripts)

| Script | What it does |
| --- | --- |
| `email_guard.py` | Pre-send recipient gate: suppression list, role prefixes, disposable/free-mail domains, bad syntax, optional MX and SMTP `RCPT` probe |
| `imap_readback.py` | Proves a send landed: searches the inbox by subject and compares the decoded attachment length to the file on disk |
| `verify_forward.py` | Verifies a forwarding rule actually delivers to the destination mailbox |

### RSS / feed intelligence, `scripts/rss-intelligence/` (9 scripts)

A SQLite-backed watcher for RSS and Atom feeds, split into one script per operation so an
agent can call exactly one step.

| Script | What it does |
| --- | --- |
| `db_init.py` | Create or migrate the database (idempotent) |
| `feed_scan.py` | Fetch and ingest new articles from one feed or all of them |
| `feed_add.py` / `feed_remove.py` | Manage the watchlist |
| `feed_list.py` | List feeds, unread articles, or export as JSON |
| `feed_mark_read.py` | Mark read by article, by feed, or everything |
| `opml_import.py` / `opml_export.py` | OPML round-trip so the watchlist is portable |
| `n8n_backup.py` | Push feeds and articles to n8n webhooks (credentials from env only) |

### Content pipeline, `scripts/content-pipeline/` (5 scripts)

| Script | What it does |
| --- | --- |
| `phantombyte_site_scan.py` | Scan a published site for outline/overlap checks before commissioning a new article |
| `kw_run.py` | Single-call driver for a keyword research run (removes per-phase round trips) |
| `check_tier_completeness.py` | Gate a keyword report: every measured term must appear in the tier list, not just the prose |
| `screenshot_mockups.py` | Batch-screenshot HTML mockups with Playwright |
| `verify-social-posts.py` | Verify social copy against per-platform limits before publishing |

### DevOps, `scripts/devops/` (5 scripts)

| Script | What it does |
| --- | --- |
| `hermes-backup.py` | Nightly backup of an agent home to a private git remote, pure Python, non-prompting |
| `verify_provider_model.py` | Proves a custom provider entry and one of its models are live the way the picker reads them |
| `probe_provider_rows.py` | Prints the provider rows the model picker builds, with model counts and membership checks |
| `fix-after-update.sh` | Repairs the Python environment and desktop build after a half-finished self-update |
| `reapply-update-fix.py` | Re-applies the self-lock fix for the launcher executable after an update |

### Document generation, `scripts/doc-generation/` (4 scripts)

Format parsers that turn structured plain text into HTML ready for WeasyPrint PDF output:
`plain-text-to-html.py`, `guide-to-html.py`, `blueprint-to-html.py` and
`cron-tutorial-to-html.py`.

### Agent tooling, `scripts/ollama/`, `scripts/telegram/`, `scripts/github/`, `scripts/productivity/`

| Script | What it does |
| --- | --- |
| `sync-ollama-models.py` | Reconciles the agent's model registry with what the local Ollama server actually serves |
| `silent-telegram-activity-patch.mjs` | Patch so tool/thinking activity reaches Telegram silently, one notification per turn instead of one per step |
| `silent-telegram-activity-test.mjs` | Functional test for that patch, driving the real runtime with a fake transport |
| `find-latest-rc.py` | Latest stable release plus latest release candidate (including tag-only RCs) |
| `gh-env.sh` | Detects the available GitHub auth path in a shell |
| `linear_api.py` | Linear GraphQL CLI, standard library only |

### Web, data collection and DNS

| Script | What it does |
| --- | --- |
| `web/recover_page.py` | Recovery ladder for blocked / paywalled / WAF'd pages: Wayback → archive.today → reader service, each result labelled with its provenance |
| `web/trends_api_extract.js` | Extracts data from Google Trends' internal API from inside a browser tab |
| `geo/find_nearby.py` | Places lookup over OpenStreetMap (Overpass + Nominatim), no API keys |
| `media/fetch_transcript.py` | YouTube transcript to structured JSON |
| `social/reddit.py` | Reddit reading client for research runs |
| `dns-ops/ionos_dns.py` | Record management against the IONOS hosting API. Dry-run by default, automatic backup before every write, `--apply` required to change anything |
| `seo-audit/offer_page_check.py` | Audits a landing page's SEO/GEO head block, contact-form wiring and sitemap/`llms.txt` presence; can submit to IndexNow. Exits non-zero on any failure so it works as a gate |
| `page-builder/build-guide.py` | Generates a guide/product page from a saved template, or fetches a live URL and rebuilds it with new content |

## Scheduled jobs, `crons/`

[`crons/hermes-cron-jobs.json`](crons/hermes-cron-jobs.json) is the live job table, exported
with credentials and delivery targets removed: name, expression, enabled state, runner
type, model, provider, preloaded skills and the full instruction.
[`crons/README.md`](crons/README.md) documents every field and lists all 34 jobs with what
each one runs.

| Job | Expression | Runner |
| --- | --- | --- |
| `30 AI NEWS STORIES DEDUP DAILY DATA FILE` | `0 16 * * *` | agent |
| `8AM TENSORFEED REPORT` | `0 8 * * *` | agent |
| `BLOGWATCHER REPORT 30+` | `1 15 * * *` | agent |
| `BRUSH FEFE'S TEETH` | `30 10 * * *` | agent |
| `CLICK HARVEST` | `0 20 * * *` | script |
| `Check For the latest Ollama version` | `0 21 * * *` | agent |
| `Check scrapling and rotunda` | `0 21 * * 5` | agent |
| `DAILY OUTREACH REFILL` | `0 0 * * 1-5` | agent |
| `DAILY Pinterest Posts 5:45PM` | `45 17 * * *` | agent |
| `Daily Data Files Backup` | `30 3 * * *` | script |
| `Delete Daily Data Files` | `30 3 * * *` | agent |
| `EMAIL TASK PROCESSOR (Frank/15min)` | `*/15 * * * *` | agent |
| `Hermes Update Health Check` | `0 2 * * *` | script |
| `INSTABOX POOL HARVEST` | `0 20 * * *` | script |
| `IronPulse 11am` | `0 11 * * *` | agent |
| `MONEY MAKING IDEAS TO USE INSTABOX.SH` | `0 18 * * *` | agent |
| `Ollama version check AM edition` | `0 9 * * *` | agent |
| `PARTNER DIRECTORY REFILL` | `0 4,7 * * *` | script |
| `PARTNER OUTREACH REFILL` | `30 9 * * 1-5` | script |
| `PRLog.org FREE press release - MONTHLY` | `31 16 7 * *` | agent |
| `PROSPECT POOL REFILL` | `0 21 * * 0-4` | agent |
| `PRUNE STALE PINTEREST POSTS` | `0 4 * * *` | script |
| `Pinterest Email Backstop` | `55 17 * * *` | script |
| `REMINDER ONLY - UPLOAD PRESS RELEASE - MONTHLY` | `1 18 7 * *` | agent |
| `SOCIAL MEDIA QUESTIONS - 5PM` | `50 16 * * *` | agent |
| `Social Media Questions Email Backstop` | `0 17 * * *` | script |
| `TUTORIAL IDEAS USING THE DATA` | `0 22 * * *` | agent |
| `Three Outlines For Articles` | `45 16 * * *` | agent |
| `WEEKDAY VERIFIER PREFILL` | `0 10 * * 1-5` | script |
| `WEEKEND VERIFIER PREFILL` | `0 10 * * 0,6` | script |
| `WEEKLY AI NEWS STORIES` | `30 14 * * 0` | agent |
| `Weekly Agent Change Briefs` | `0 5 * * 0,2,4,6` | agent |
| `hermes-weekly-backup` | `0 3 * * 0,1,2,3,4,5,6` | script |
| `x-algorithm repo update watcher` | `15 8 * * 0,3,6` | agent |

`script` runs with no model attached; `agent` runs the instruction in a session with the
listed skills preloaded. One job is disabled and kept for reference.

## Skills, `skills/`

281 skill definitions. A skill is what an agent loads before doing that class of work:
preconditions, procedure, the exact commands, and the pitfalls already paid for, plus
whatever `references/`, `scripts/` and `templates/` the work needs.

| Prefix | Count | What it covers |
| --- | --- | --- |
| `hermes-` | 200 | Active procedures for the WSL agent |
| `hermes-archive-` | 62 | Retired procedures kept as reference rather than deleted |
| `pi-` | 19 | Deployment and maintenance for the public sites, built around idempotent rebuilds and post-deploy checks |

Largest groups: `content-swarm` (37), the article pipeline from outline selection to
publication, distribution, keyword research and platform-specific copy; `devops` (25), 
installation, config, backup, desktop app, containers, model routing; `mlops` (22);
`research` (15); `productivity` (14); `creative` (13); `behavioral` (11), the verification
rules the agent applies to itself; `software-development` (7), debugging, planning, TDD,
code review, subagent workflows; `autonomous-ai-agents` (6).

## Sanitisation

This repository is a cleaned export of a live machine. Removed or replaced before
publishing:

- API keys, bot tokens, IndexNow and CMS tokens, OAuth secrets and private keys, every
  script reads credentials from environment variables or a local secrets file that is not
  here
- personal mailboxes and third-party addresses (replaced with `[REDACTED_EMAIL]` or
  `user@example.com`), phone numbers and chat IDs
- home-directory paths and usernames (`/home/…` and `C:\Users\…` replaced with `~` and
  `C:\Users\<user>`)
- security and credential-handling tooling (secret scanners, push guards, credential
  repair scripts, token recovery), deliberately excluded
- vendored third-party skill packs (document/office format skills), not my work, omitted

## License

MIT, see [LICENSE](LICENSE).
