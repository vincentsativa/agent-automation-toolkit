# Agent Automation Toolkit

A working collection of scripts, scheduled jobs and skill definitions that run two
local AI coding agents (**Pi** and **Hermes**) on a Windows workstation and a Linux
dev box.

Everything here is code I wrote or adapted to make agents do real, verifiable work:
fetch a page and prove it is still live, send an email and prove the attachment
arrived intact, back up an agent home every night at 03:00, keep a job pipeline's
counts honest. The common thread is *verification* — almost every script exists
because a previous run reported success that was not true.

## What is in here

| Path | Contents |
| --- | --- |
| [`scripts/`](scripts) | 57 runnable scripts (Python, Bash, Node), grouped by domain |
| [`skills/`](skills) | 112 agent skill definitions (`SKILL.md`) — the procedures the agents load before acting |
| [`crons/`](crons) | Scheduled jobs: expressions, runner type, and the full instruction each one executes |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | How the two-agent system fits together |

## Scripts

### Job search pipeline — `scripts/job-search/`

A staged, resumable pipeline that collects remote AI/automation postings, applies hard
filters, resolves each posting to the employer's own apply page, verifies the posting is
still live *today*, and renders a report. Built because aggregator search endpoints
rate-limit and their "Apply" links point back at themselves.

| Script | What it does |
| --- | --- |
| `collect.py` | Stage 1 — pull raw postings from every enabled source into `raw.jsonl` |
| `prefilter.py` | Stage 2 — apply hard rules, rank survivors, log a reason for every drop |
| `resolve_employer.py` | Stage 2b — replace aggregator redirects with the direct employer apply URL |
| `verify.py` | Stage 3 — fetch each posting's own page and classify live / dead |
| `payfix.py` | Stage 3b — re-open live leads with no pay figure and pull the salary line |
| `pack.py` | Stage 4 — compress verified candidates into small packs for model judgement |
| `select.py` | Stage 4b — build a baseline selection so the list never depends on one model pass |
| `topup.py` | Stage 4c — widen supply and re-run the chain when the list lands short of target |
| `report.py` | Stage 5 — render the final report from the model's picks |
| `validate_delivery.py` | Refuse delivery when a report does not describe the final verified pool |
| `run.py` | One command that runs collect → prefilter → verify → pack |
| `common.py` | Shared helpers, standard library only |
| `build_resume_profile.py` | Build a machine-readable profile from a resume PDF |
| `build_workable_boards.py` | Cache employer boards to route around Workable's IP rate limit |
| `pull_himalayas_deep.py` | Deep-paginate the Himalayas feed in parallel and dedupe by guid |
| `probe_ats_slugs.py` | Probe Greenhouse / Lever / Ashby slugs in parallel before adding a company |
| `seed_ledger_from_document.py` | Seed the cross-day ledger from a list delivered outside the pipeline |

### Email operations — `scripts/email-ops/`

| Script | What it does |
| --- | --- |
| `email_guard.py` | Pre-send recipient gate: suppression list, role prefixes, disposable/free-mail domains, bad syntax, optional MX and SMTP `RCPT` probe |
| `imap_readback.py` | Proves a send landed: searches the inbox by subject and compares the decoded attachment length to the file on disk |
| `verify_forward.py` | Verifies a forwarding rule actually delivers to the destination mailbox |

### RSS / feed intelligence — `scripts/rss-intelligence/`

A SQLite-backed watcher for RSS and Atom feeds, split into one script per operation so
an agent can call exactly one step.

| Script | What it does |
| --- | --- |
| `db_init.py` | Create or migrate the database (idempotent) |
| `feed_scan.py` | Fetch and ingest new articles from one feed or all of them |
| `feed_add.py` / `feed_remove.py` | Manage the watchlist |
| `feed_list.py` | List feeds, unread articles, or export as JSON |
| `feed_mark_read.py` | Mark read by article, by feed, or everything |
| `opml_import.py` / `opml_export.py` | OPML round-trip so the watchlist is portable |
| `n8n_backup.py` | Push feeds and articles to n8n webhooks (credentials from env only) |

### DNS — `scripts/dns-ops/`

| Script | What it does |
| --- | --- |
| `ionos_dns.py` | Record management against the IONOS hosting API. Dry-run by default, automatic backup before every write, `--apply` required to change anything |

### SEO / page audit — `scripts/seo-audit/`

| Script | What it does |
| --- | --- |
| `offer_page_check.py` | Audits a landing page's SEO/GEO head block, contact-form wiring and sitemap/`llms.txt` presence; can submit to IndexNow. Exits non-zero on any failure so it works as a gate |

### Page building — `scripts/page-builder/`

| Script | What it does |
| --- | --- |
| `build-guide.py` | Generates a guide/product page from a saved template, or fetches a live URL and rebuilds it with new content |

### Document generation — `scripts/doc-generation/`

Four format parsers that turn structured plain text into HTML ready for WeasyPrint PDF
output: `plain-text-to-html.py`, `guide-to-html.py`, `blueprint-to-html.py`,
`cron-tutorial-to-html.py`.

### DevOps — `scripts/devops/`

| Script | What it does |
| --- | --- |
| `hermes-backup.py` | Nightly backup of an agent home to a private git remote, pure Python, non-prompting |
| `verify_provider_model.py` | Proves a custom provider entry and one of its models are live the way the picker reads them |
| `probe_provider_rows.py` | Prints the provider rows the model picker builds, with model counts and membership checks |
| `fix-after-update.sh` | Repairs the Python environment and desktop build after a half-finished self-update |
| `reapply-update-fix.py` | Re-applies the self-lock fix for the launcher executable after an update |

### Content pipeline — `scripts/content-pipeline/`

| Script | What it does |
| --- | --- |
| `phantombyte_site_scan.py` | Scan a published site for outline/overlap checks before commissioning a new article |
| `kw_run.py` | Single-call driver for a keyword research run (removes per-phase round trips) |
| `check_tier_completeness.py` | Gate a keyword report: every measured term must appear in the tier list, not just the prose |
| `screenshot_mockups.py` | Batch-screenshot HTML mockups with Playwright |
| `verify-social-posts.py` | Verify social copy against per-platform limits before publishing |

### Web and data collection — `scripts/web/`, `scripts/geo/`, `scripts/media/`

| Script | What it does |
| --- | --- |
| `recover_page.py` | Recovery ladder for blocked / paywalled / WAF'd pages: Wayback → archive.today → reader service, each result labelled with its provenance |
| `trends_api_extract.js` | Extracts data from Google Trends' internal API from inside a browser tab |
| `find_nearby.py` | Places lookup over OpenStreetMap (Overpass + Nominatim), no API keys |
| `fetch_transcript.py` | YouTube transcript to structured JSON |

### Agent tooling — `scripts/ollama/`, `scripts/telegram/`, `scripts/github/`, `scripts/productivity/`

| Script | What it does |
| --- | --- |
| `sync-ollama-models.py` | Reconciles the agent's model registry with what the local Ollama server actually serves |
| `silent-telegram-activity-patch.mjs` | Patch so tool/thinking activity reaches Telegram silently — one notification per turn instead of one per step |
| `silent-telegram-activity-test.mjs` | Functional test for that patch, driving the real runtime with a fake transport |
| `find-latest-rc.py` | Latest stable release plus latest release candidate (including tag-only RCs) |
| `gh-env.sh` | Detects the available GitHub auth path in a shell |
| `linear_api.py` | Linear GraphQL CLI, standard library only |

## Scheduled jobs — `crons/`

`crons/hermes-cron-jobs.json` is the live job table with secrets and delivery targets
removed: name, expression, enabled state, runner type (`deterministic-script` or
`agent-prompt`), model, and the full instruction the agent executes. Ten jobs, covering a
nightly backup, a 15-minute inbox processor, a polling panel that arms and cleans itself
up, and content-generation jobs.

## Skills — `skills/`

112 skill definitions. Each `SKILL.md` is what an agent loads before doing that class of
work: preconditions, procedure, the exact commands, and the pitfalls already paid for.
Prefixes show which agent the skill lives in (`pi-` or `hermes-`). Groups:

- `content-swarm-*` — the article pipeline from outline selection to publication,
  distribution, keyword research and platform-specific copy
- `job-search`/`prospecting-*` — the pipeline above plus screening and application material
- `devops-*` — agent installation, config, backup, desktop app, containers, model routing
- `software-development-*` — debugging, planning, TDD, code review, subagent workflows
- `behavioral-*` — verification rules the agent applies to itself
- `email-*`, `telegram-workflow-*`, `github-*`, `web-*`, `social-media-*`, `media-*`
- `pi-*` — deployment and maintenance procedures for the public sites, built around
  idempotent rebuilds and post-deploy checks

## Sanitisation

This repository is a cleaned export. Removed before publishing:

- API keys, tokens, bot tokens, OAuth secrets, private keys — every script reads
  credentials from environment variables or a local `secrets.json` that is not here
- real email addresses (replaced with `user@example.com`), phone numbers, chat IDs
- absolute home-directory paths (replaced with `~`)
- security and credential-handling tooling (secret scanners, push guards, credential
  repair scripts, token recovery) — deliberately excluded
- vendored third-party skill packs (document/office format skills) — not my work, omitted

## Requirements

Python 3.9+ (standard library for most scripts; `playwright`, `requests`, `scrapling`
and `weasyprint` only where the script says so), Bash for the shell helpers, Node 18+ for
the two `.mjs` files.

## License

MIT — see [LICENSE](LICENSE).
