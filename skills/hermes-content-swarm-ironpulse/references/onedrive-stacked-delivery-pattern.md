# Stacked Delivery Pattern: OneDrive + Email + Telegram Notification

## When to Use

When the user asks for IronPulse with themes AND specifies a OneDrive subfolder AND requests Telegram notification after email. This is the three-part stacked delivery.

## The Full Sequence

### Step 1: Write the report
Standard report to `~/.hermes/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt`

### Step 2: Copy to BOTH Desktop locations
```bash
cp ~/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt "/mnt/c/Users/<user>/Desktop/ironpulse-YYYY-MM-DD.txt"
cp ~/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt "/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/ironpulse-YYYY-MM-DD.txt"
```
Verify both with `ls -la`.

**PITFALL - Custom OneDrive filenames:** When the user specifies a different filename for the OneDrive copy (e.g. "IRONPULSE 4PM REPORT (IMPORTANT).txt" instead of ironpulse-YYYY-MM-DD.txt), use that exact filename for the OneDrive copy only. The Desktop copy keeps the standard naming convention. Honor the user's requested filename verbatim for the OneDrive copy — do not override it. Verify both filenames exist separately with ls -la.

### Step 3: Send email with attachment AND themes in body
Write the email script to this run's unique scratch dir — `SCRATCH=$(mktemp -d /tmp/hermes-cron-XXXXXX)`, then `$SCRATCH/send.py` — using the email-sender skill template. NEVER a fixed path like `~/send_email.py`: the file persists after the run and the next run's write_file is refused by the stale-overwrite guard. The body must contain the 3 themes with explicit namediffs — for each theme, state which PhantomByte article it could be confused with and explain why the angle is actually different.

**Subject format:** `IronPulse Report - YYYY-MM-DD - AI News + 3 Unpublished Themes`

**Email body structure:**
```
Vinny,

IronPulse report [date] attached.

3 THEMES FROM TODAY'S DATA - NOT YET COVERED ON PHANTOMBYTE

1. [Theme name]
[2-4 sentence description]
Why this is different from "[Closest PhantomByte article title]": [explicit namediff — the angle, scope, or implication that makes it distinct]

2. ...

3. ...

Full 20-story ranked report attached.

— Hermes
```

Execute with `python3 "$SCRATCH/send.py"`. Verify "Email sent successfully" output, then delete the scratch dir.

### Step 4: Telegram notification
Only if the user explicitly asked to be notified. Short confirmation, maximum 2 lines — do not paste headlines, summaries, or themes:
"Sent. 12 stories, 3 themes in email body. File at C:\Users\<user>\Desktop\ironpulse-YYYY-MM-DD.txt and in TODAYS DATA FILES."

**PITFALL — Telegram brevity on cron jobs:** Even when the user asked to be messaged after email delivery, keep the Telegram message minimal. No headlines, no expanded analysis, no walking through the themes. The report and themes are in the email and on Desktop. A long Telegram message on a cron-delivered IronPulse is wasted scroll the user will skip past.