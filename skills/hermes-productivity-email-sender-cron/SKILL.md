---
name: email-sender-cron
description: Hard-won cron job email report patterns — money-making opportunity reports, article draft pre-send verification, execute_code limits, Telegram-in-response rules, and scrapling site research in cron. Use for any scheduled email-report cron job.
---

# Email Sender — Cron Report Patterns

Hard-won lessons for email-report cron jobs. Follow these exactly.

## Money-Making Opportunity Report Pattern

- **Folder:** `~/Desktop/LOW BUDGET MONEY MAKING OPPORTUNITIES/`
- **Filename:** `high-value-money-making-opportunities-YYYY-MM-DD.txt` (version with `-v2`, `-v3`, etc. as needed — **never overwrite** an existing file)
- **Verify by reading the file back** after writing it.
- **Email subject:** `High-Value Money-Making Opportunities - YYYY-MM-DD`
- **Email body:** count + Best Bet + startup cost + time to first paid validation + "report attached"
- **Sign:** `— Bill`
- **Telegram:** put the notification in the FINAL response. Do NOT call `hermes send --to telegram`.

## Python String Literal Pitfall

Apostrophes in the subject or body break single-quoted Python strings. Use **double quotes** for any string that contains an apostrophe.

## execute_code Blocked in Cron

**BLOCKED:** `execute_code` runs arbitrary local Python and is not available in cron contexts. Use `read_file` / `terminal` / `write_file` instead.

## Scratch Scripts Must Be Unique Per Run (HARD RULE — verified Sept 17, 2026)

Hermes refuses `write_file` on an existing file the current run never read
(`tools/file_tools_write_guards.py::_stale_overwrite_blocker`). A fixed scratch path
like `~/send_email.py` or `/tmp/extract_all.py` survives between runs, so
the first run creates it and every later run is refused — and the refusal is appended
to the delivered Telegram message as "⚠️ File-mutation verifier: N file edit(s) FAILED".
That warning is what Vinny sees, and it means a cron step silently failed.

**Every run: create a fresh scratch dir and write helpers inside it.**

```bash
SCRATCH=$(mktemp -d /tmp/hermes-cron-XXXXXX) && echo "$SCRATCH"
```

Then `write_file` to `<SCRATCH>/send.py` and run `python3 <SCRATCH>/send.py`. The dir is
new each run, so no path collides and the guard cannot fire. Delete the dir when done.

**If a `write_file` is refused, do NOT retry the same path** — make a new `mktemp -d` and
write there. Retrying a fixed path is exactly what produced the daily failures on
`/tmp/extract_all.py` and `~/send_email.py`.

Before running any email script, verify its addresses with `grep -oP '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' "$SCRATCH/send.py"`.

## Article Draft Pre-Send Verification

Before sending any article draft, verify:
- Em-dash count = 0
- X post under 190 characters
- Title case (no all-caps)
- 1,300–1,600 words
- Sources present when fact-checking was requested

**Send-first-fix-later is a violation.** Verify first, then send.

## IONOS Scheduled Mail Needs an Explicit From Identity (HARD RULE — verified Sept 22, 2026)

Staging a message into the IONOS Scheduled folder over the OX API (`POST
/appsuite/api/mail/compose/<cid>/send` with `dateToSend`) is **not** a send, and the
staging call does not validate the sender. A message staged with no `from` field is
accepted with a 200, lands in `default0/Scheduled` looking healthy, and then is killed
at send time with **MSG-0037**, leaving it dead in the folder with no retry. IONOS mails
a "Your scheduled mail could not be sent" notice to the account afterward.

**Always carry the sender explicitly:**

```python
payload = {
    "from": [["Vinny Barreca", "hello@phantom-byte.com"]],
    "to": [["", to_addr]],
    ...
}
```

Proof, from an A/B test that ran both payloads side by side to the same inbox: the
no-`from` message failed and stayed in Scheduled; the `from` message sent normally and
moved to Sent Items. That is the entire difference.

**The read-back check must assert `From`.** A verification that only checks recipients,
paragraph count, postal line, opt-out and send time passes on a folder of dead messages.
`schedule_drafts.py` now includes `checks["from_identity"] = bool(m.get("From")) and
MAIL_FROM in m.get("From")`, and the run fails without it.

**Recovery for an already-dead batch:** back up every raw message first, delete the
From-less ones from Scheduled, re-create each with the `from` field at a fresh send
time, then read the folder back and assert `From`, `To`, `Subject`, body, and
`X-OX-Date-To-Send` on every message.

## Telegram Notification in Cron

The final response IS the Telegram message. Do NOT call `hermes send --to telegram` — the cron system delivers your final response to the configured destination automatically.

## Scrapling for Site Research in Cron

Use scrapling's `Fetcher` from the Hermes venv (not `browser_navigate`):

```bash
cd ~/.hermes/hermes-agent/venv && source bin/activate && python3 -c "..."
```

**Pitfall:** `page.text` may return LENGTH 0, but `page.css(...)` still works — prefer CSS selectors for extraction.
