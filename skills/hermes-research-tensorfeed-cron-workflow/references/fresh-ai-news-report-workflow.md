# Fresh "Top N AI News Stories" Report Workflow (verified Aug 6, 2026)

Class of task: a cron request for "today's top N AI story headlines with a 5-6
sentence summary each + N themes," where the deliverable is a dated file in
`~/Desktop/TODAYS DATA FILES/` and an email with the file attached
(Telegram only gets a short "email sent" note — the user does NOT want 25
stories pasted to Telegram).

## Pre-flight dedup (MANDATORY)

The user's rule: every story MUST be new, NOT already in the existing data
files. Before writing anything:

1. `ls -la "~/Desktop/TODAYS DATA FILES/"` to list today's files.
2. Read EVERY data file present (ironpulse, tensorfeed_report, blogwatcher-dump).
3. Extract the story titles/headlines from each.
4. Only include stories absent from all of them.

## Discovery (RSS-first)

Batch-fetch the RSS feeds (see SKILL.md RSS-First Discovery section) via
scrapling Fetcher, parse with `xml.etree`, print `pubDate | title | link`.
Collect 30-40 candidates to comfortably cover N=25 after dedup. The `pubDate`
verifies freshness in one line.

Verified reliable feeds for this class: TechCrunch AI, Ars Technica AI, WIRED
AI, MIT Tech Review, BBC Technology, Guardian AI, Google News RSS (all load
clean via scrapling Fetcher). VentureBeat's `/category/ai/feed` returned stale
Jan-2026 items on Aug 6 — treat VentureBeat as unreliable for "today" reports.

## Verification (web_extract on canonical URLs)

For each candidate, `web_extract` the canonical source URL (Ars/BBC/Guardian/
WIRED article page). These render cleanly and give enough body for an accurate
5-6 sentence summary.

PITFALLS:
- Google News RSS `news.google.com/rss/articles/CB...` links FAIL web_extract
  (Keenable `422 unknown`). `web_search` the headline, then web_extract the real
  source URL.
- Do NOT try to summarize from a bare headline; a 5-sentence summary needs the
  article body. If the primary source is bot-blocked (Reuters), search a mirror.

## Writing

- Exactly N stories, each with its own 5-6 sentence summary (every story gets a
  summary — do NOT truncate to a few).
- 5 themes/patterns section at the end, synthesized from the N stories.
- Vinny rule: NO em dashes. Use commas/periods. Verify with
  `grep -c '—' <file>` = 0 before delivery.

## Save + email + telegram

- Filename format exactly as requested (e.g. `20-AI-News-Stories-YYYY-MM-DD.md`)
  in `~/Desktop/TODAYS DATA FILES/`.
- PITFALL (verified Aug 8, 2026): the `20-` prefix in the filename is a FIXED
  convention, NOT tied to the story count. Vinny asked for 25 stories and the
  file was still `20-AI-News-Stories-2026-08-08.md`. Do NOT "correct" the 20 to
  match the N requested. Use the literal filename format the user gave, verbatim.
- Email the file as an attachment to `hello@phantom-byte.com` using the
  email-sender-cron IONOS pattern (create `SCRATCH=$(mktemp -d /tmp/hermes-cron-XXXXXX)`,
  audit addresses with grep, run `python3`, confirm `Email sent successfully`
  + SMTP `Authentication succeeded`/`rcpt TO` lines, then delete the script).
- Telegram: the cron system auto-delivers the final response. Keep it to a
  short "file saved + email sent" confirmation. Do NOT paste the 25 stories,
  summaries, or themes into the Telegram message.
