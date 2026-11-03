---
name: phantombyte-editorial-brief
description: Use for blogwatcher editorial briefs with email delivery.
version: 1.0.0
author: Hermes Agent
prerequisites:
  skills: [blogwatcher, email-sender]
---

# PhantomByte Editorial Brief

Produce a daily editorial intelligence brief for Vinny at PhantomByte. This skill captures Vinny's specific preferences that cannot be embedded in the bundled blogwatcher skill.

## Trigger

- "Run me a blogwatcher" with editorial output requested
- "Editorial brief" or "intelligence brief"
- Any request for a daily news report with theme analysis and email delivery

## Workflow

### 1. Scan and Extract

Follow the blogwatcher skill's Editorial Intelligence Brief Workflow for scanning and date-filtered extraction. The blogwatcher skill handles the tool-level mechanics.

### 2. Headline Volume

**Vinny's floor is 30 stories, max 40 ("minimum of 30 MAX 40 if the stories are good"), each with a 5-6 sentence summary.** Treat 30 as the floor and 40 as the ceiling: below 30 the run is short, and padding past 40 with thin stories is worse than stopping. The blogwatcher skill's own default of 12+ does NOT apply here. Take ALL available industry headlines from the date-filtered pool; fall back to arXiv papers (a separate section) to reach the floor.

### 3. Summary Depth

**Each story gets a 5-6 sentence summary.** Not 1-2 sentences. Lead with the most important fact, then context, then impact. For the 6-9 anchor stories that will drive unwritten themes, use delegate_task with parallel browser tasks to get full-article summaries. For the remaining ~15 headlines, write summaries from headline + source context.

**Synchronous delegate_task in cron context:** When running as a cron job (one-shot runner), delegate_task runs synchronously — results return before the turn ends. This differs from interactive sessions where subagents run in the background. You can rely on synchronous results for deep summaries in cron mode. Batch 3 tasks per call (max concurrency = 3), chain 2-3 rounds for 6-9 deep summaries.

### 4. Unwritten Themes

Cross-reference against articles.phantom-byte.com front page. Identify 5 themes (not 3) that haven't been covered. Each theme needs:
- A provocative article title angle
- Supporting sources from today's data
- Explicit statement of why this hasn't been covered (cite closest existing article with date and explain the difference)

### 5. File Output

Write the editorial brief to `~/blogwatcher-dump-YYYY-MM-DD.txt`.

### 6. Email Delivery

Use the email-sender skill to email the file as an attachment to hello@phantom-byte.com. Subject: "AI Daily News Brief — YYYY-MM-DD (N stories, 5 unwritten themes)". Body: brief summary of what's attached.

### 7. Windows Desktop Copy

**Do this by copying the file that is already on disk, before or after the email, but never report it as done without stat-ing the destination.** Copy the file to Vinny's Windows desktop folder:
```bash
mkdir -p "/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES"
cp ~/blogwatcher-dump-YYYY-MM-DD.txt "/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/"
```
Then confirm the file is really there with `search_files (target='files', pattern='blogwatcher-dump-*', path='/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/')` before saying it landed. That check is not decoration: a previous run reported this stage as `Filed to: <path>` and the file was absent from the folder, on two consecutive days. The claim came from the run's intent, not from a write that landed.

### 8. DB Cleanup

After the email is sent, clear the stockpile with the two-phase script:
```bash
bash ~/scripts/blogwatcher-cleanup.sh
```
It marks older articles read (keeping their URLs, which blocks re-import) and then purges truly ancient rows, printing the final totals. Run it AFTER the send, never before. Then delete the dump file and the run's scratch dir.

**The stockpile number is the proof the stage ran.** Read the totals it prints ("Final DB state: N total (M unread)"); a run that reports a cleanup without those numbers did not run the script.

### 10. Recovering a Run That Died With Only the Tail Outstanding

When a run is cut off after the brief is built, the tail (copy, email, cleanup) is all that
is missing. **Recover the tail; do not re-fire the job and do not rebuild the brief.** Every
step below is a single command against the file already on disk.

**Diagnose first, from the run's own words, before touching anything:**
```bash
ls -t ~/.hermes/cron/output/<job_id>/*.md | head -1   # read the last run's ## Response
```
That response names the finished stages and the unfinished ones in order, which tells you
exactly what to finish. Then `stat` the artifact it claims to have written — a response is a
claim, the file is evidence. A rebuilt brief is a fresh chance to introduce the errors the
first build already cleared, and re-firing duplicates a report that may already have gone
out.

**Then finish the tail in order:**
1. Stat the dump file. If present, copy it to `/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/` and confirm the copy landed with `md5sum` on BOTH paths — matching hashes are the proof, the `cp` exit code is not.
2. Email it from a fresh `mktemp -d` scratch dir per `email-sender-cron`. Assert `REFUSED RECIPIENTS: {}` and a `250 ... completed` reply; `send_message` returning without complaint is not a send.
3. Run the cleanup script and read the totals it prints.
4. Delete the dump file from `~/` and the run's scratch dir, leaving the desktop copy as the only copy.

**The email, once sent, is never sent again.** A second send gives Vinny two of the same
report. If you are unsure whether step 2 completed, check for the SMTP acceptance reply in
the run output before resending.

**Then fix the budget, or it happens again tomorrow.** Compare the job record's `max_turns`
against the ceiling in the run's turn-end line:
```bash
grep "<session_id>" ~/.hermes/logs/agent.log | grep "Turn ended"
# reason=max_iterations_reached(90/90) while jobs.json says max_turns: 200 == the field is not being read
```
A job record that advertises a budget larger than the ceiling the run died at is the
diagnosis, not a coincidence. The resolution fix and the packaged probe are in
`hermes-cron-troubleshooting` Failure Mode #9 and `scripts/probe_cron_job_turn_budget.py`.

### 9. Telegram Notification

Send ONE Telegram message confirming the email was sent. Do NOT paste document content. Format: "Email sent with today's editorial brief — N stories, 5 unwritten themes. File on your desktop."

**Cron/autonomous mode:** When running as a scheduled cron job (no user present), skip Telegram entirely. The cron delivery mechanism handles the final response. Do not attempt to send Telegram messages from a cron context.

**"Do NOT spam Telegram" rule:** If the user explicitly says "do NOT spam telegram" or "do NOT send to Telegram," skip Telegram entirely regardless of mode. The email is the delivery mechanism; Telegram is just a doorbell that can be silenced.

### 2b. Dedup Against TODAYS DATA FILES (do this BEFORE writing anything)

Vinny's "no duplicates" rule is strict and phrase-based, not title-based. TensorFeed/IronPulse files reword headlines, so exact-title matching fails. Use this procedure:

1. Concatenate every file in `/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/` (both the Windows/OneDrive mount and the `~/Desktop/` mirror) into one lowercased, punctuation-stripped blob (`re.sub(r"[^a-z0-9 ]", " ", s)` then collapse whitespace).
2. For each candidate story, extract 4 to 5 sentences worth of distinctive facts from the source article via `web_extract`, then test whether a 4-gram or 5-gram from those facts appears in the blob. A single keyword hit ("nscale", "palantir", "suno") is NOT a duplicate on its own; a matched 4-gram phrase is.
3. Verify borderline cases with a ±150-char context window around the hit before deciding. Common false positives: a keyword appearing in a round-up list, a paper abstract, or an unrelated table row.
4. Prefer newer stories. If yesterday's file covered a story under different wording, drop it; if today's fresh story is a genuine follow-up with new facts, it can stay only if the new facts are absent from the blob.

## Pitfalls

- **The run must not end early with stages outstanding.** This job's tail (copy, email, cleanup) is exactly what the turn ceiling eats first when the brief-building consumes the budget. Do not rebuild a finished brief to finish the tail: copy the file already on disk, send it, run the cleanup script. See step 10 for the recovery procedure, `hermes-cron-troubleshooting` Failure Mode #9 for the budget fix, and `agent-turn-efficiency` for the budget side.
- **Separator lines carry em dashes.** Box-drawing rules and titled section headers are where `—` sneaks into an otherwise clean brief (a section header reading `SECTION 3: UNWRITTEN THEMES — NOT ON PHANTOMBYTE`, and a sign-off line). Grep the finished file for `—` before sending and replace with a comma; a zero-em-dash claim made without grepping the actual file is a guess.
- **A job field is not a fix until the resolver reads it.** If the job record carries a `max_turns` and the run still dies at the global ceiling, the field is being persisted and ignored. Editing the brief's structure or trimming the story count does not fix that, and it costs the run its tail again on the next dispatch.
- **Report per-stage state, never "the job ran."** Four stages means four pieces of evidence: the file at the destination path, the send confirmation, the DB totals, the draft written. A status field saying `ok` is evidence about the process, not about the work.
- **Dedup by phrase, not by title.** A reworded headline passes title-matching while duplicating the exact same story. See step 2b.
- **Volume:** Vinny's floor is 30, ceiling 40, each with 5-6 sentences. See step 2.
- **Summary depth:** 1-2 sentence summaries are too short. Every story needs 5-6 sentences minimum.
- **Theme count:** 3 themes is the blogwatcher default. Vinny wants 5.
- **Windows path:** Always use `/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/` for the desktop copy, and stat it before claiming the copy landed.
- **Email first, then Telegram:** Send the email before sending the Telegram notification. The Telegram message is just a doorbell.
- **DB cleanup is mandatory:** Run the cleanup script after delivery, then remove the dump file and scratch dir. Do not stockpile.
