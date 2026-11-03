---
name: email-sender
description: Send emails via IONOS SMTP with optional file attachments. Use this when Vinny asks to email him or send a document by email.
trigger: "user asks to email, send email, attach file to email, send document, or mail something"
---

# Email Sender Skill (IONOS SMTP)

> **NOTE:** This skill is ONLY for emailing Vinny (hello@phantom-byte.com). For Hermes' own email (checking inbox / emailing other agents) use the `hermes-email-agentmail` skill (AgentMail). These never cross.

## When to use
- Vinny asks to email him something
- Vinny asks to "send me the document by email" or "attach to an email"
- Any request that involves sending a file or message to his email address
- Interpret intent, not exact keywords: "email me" and any natural variant means this skill — do not wait for a verbatim trigger phrase. If the description matches the user's intent, load the skill.

## Email Address
- **To:** hello@phantom-byte.com
- **From:** hello@phantom-byte.com

## SMTP Credentials (confirmed working May 8 2026)
- **Server:** smtp.ionos.com
- **Port:** 587 (TLS)
- **Username:** hello@phantom-byte.com
- **Password:** VJBvjbhydro1202$$

## Sending Email (Python)

Write the script to a file first, then run it. Do NOT use `python3 -c "..."` inline — that approach fails with SMTPAuthenticationError even with correct credentials. Use a file instead.

```python
# <this run's $SCRATCH/send.py>
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email(to, subject, body, attachment_path=None):
    msg = MIMEMultipart()
    msg['From'] = 'hello@phantom-byte.com'
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = os.path.basename(attachment_path)
            part.add_header('Content-Disposition', f'attachment; filename={filename}')
            msg.attach(part)
    elif attachment_path:
        print(f"WARNING: attachment not found at {attachment_path}, sending without attachment")
    server = smtplib.SMTP('smtp.ionos.com', 587, timeout=60)
    server.starttls()
    server.login('hello@phantom-byte.com', 'VJBvjbhydro1202$$')
    server.send_message(msg)
    server.quit()
    return True

send_email(
    to='hello@phantom-byte.com',
    subject='Your Subject Here',
    body='Brief body text.',
    attachment_path='~/your_document.txt'
)
```

Then run: `python3 "$SCRATCH/send.py"` (see Usage Pattern — never a fixed path).

## Multiple Attachments in One Email (July 16, 2026)

When sending multiple files in a single email (e.g., 3 outline files), use
a list-based attachment function instead of the single-attachment pattern
above. Do NOT send separate emails per file.

```python
# <this run's $SCRATCH/send.py> — multiple attachments
import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email_with_attachments(to, subject, body, attachment_paths):
    msg = MIMEMultipart()
    msg['From'] = 'hello@phantom-byte.com'
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    for path in attachment_paths:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(path)
                part.add_header('Content-Disposition',
                    f'attachment; filename={filename}')
                msg.attach(part)
            print(f"Attached: {filename} ({os.path.getsize(path)} bytes)")
        else:
            print(f"WARNING: attachment not found at {path}")
    server = smtplib.SMTP('smtp.ionos.com', 587, timeout=60)
    server.set_debuglevel(1)
    server.starttls()
    server.login('hello@phantom-byte.com', 'VJBvjbhydro1202$$')
    server.send_message(msg)
    server.quit()
    print("Email sent successfully.")
    return True

send_email_with_attachments(
    to='hello@phantom-byte.com',
    subject='Your Subject Here',
    body='Brief body text.',
    attachment_paths=[
        '/path/to/file1.txt',
        '/path/to/file2.txt',
        '/path/to/file3.txt',
    ]
)
```

Key differences from the single-attachment pattern:
- Takes a list of paths instead of a single path
- Loops through attachments, attaching each one
- Prints a confirmation per attachment so you can verify all files were included
- Always include `set_debuglevel(1)` and a final print after `send_message`

## Press Release Distribution: HTML Required (CRITICAL — July 14, 2026)

When Vinny says "this is a FREE prlog campaign" or mentions any press release distribution platform, the attachment **must be HTML**, not `.txt`. Plain text files cannot contain clickable hyperlinks. PR Log and similar platforms ingest HTML and render links as live URLs.

See `references/press-release-html-format.md` for the full template and rules.

**Key rules:**
- Every URL must be an `<a href>` tag — plain text URLs in parentheses are not acceptable
- When Vinny says "make (X: URL) the clickable link," the anchor text is the label, not the raw URL
- Count original vs new chars to verify the reduction target is met
- Attach the `.html` file, do not paste HTML into the email body

## Large Attachments: Compress Before Sending (CRITICAL — June 20, 2026)

IONOS SMTP will timeout and disconnect if you try to upload a large file raw. A 2-minute 1080x1920 video can be 40-50MB. **Always compress video attachments before emailing.**

```bash
ffmpeg -y -i /path/to/large_video.mp4 -c:v libx264 -crf 28 -preset fast -c:a copy /path/to/large_video_compressed.mp4
```

This typically halves the file size with minimal quality loss. Target under 30MB for reliable SMTP delivery.

**If the attachment is still too large after compression,** do NOT attempt to send it via this SMTP. Upload it to a file host (Google Drive, Dropbox, etc.) and email the link instead.

## Usage Pattern

1. Build the document content and write it to a file. The file can be `.txt`, `.md`, `.pdf`, or any other format -- the SMTP attachment system handles all file types via MIMEBase. NEVER save without an extension -- Vinny expects a proper filename.
2. Write the send function + call to this run's UNIQUE scratch path. Create a fresh dir first:
   `SCRATCH=$(mktemp -d /tmp/hermes-email-XXXXXX) && echo "$SCRATCH"`, then write to
   `$SCRATCH/send.py` and run `python3 $SCRATCH/send.py`.
   **NEVER reuse `~/send_email.py` or any fixed `send_<job>.py` name.** A fixed
   path persists on disk after the run, so the next run's `write_file` is refused by the
   stale-overwrite guard and the job's email step fails. This is a HARD RULE.
   A descriptive placeholder directory such as `/tmp/hermes-226e-placeholder/send.py` is the
   same mistake wearing a different name: it is still a fixed path, and the next run hits the
   same refusal. Create the `mktemp -d` directory first and write `send.py` straight into that
   path in the same call. If the write was aimed at anything else, copy the file into $SCRATCH
   and delete the placeholder before sending.
3. Delete the scratch dir after the run so nothing is left for the next job to trip over.
4. Confirm to Vinny on Telegram -- do NOT paste document content into the chat

## Cron Job Email Pattern (July 10, 2026)

When a cron job emails a file as an attachment, follow this pattern:

1. **Write the file** to the designated desktop folder with a proper filename and extension
2. **Email it** as an attachment using the standard SMTP script
3. **Notify minimally** — send ONLY "Email sent" or "Email sent with today's [topic]" on Telegram. Nothing more. No content summary, no preview, no "here's what I found." The email is the delivery mechanism; the Telegram message is just a notification that it was sent.

This applies to any cron job that produces a daily file and emails it. The Telegram notification is a doorbell, not the package.

## Every Email Is Spell-Checked Before It Goes (added October 13, 2026)

Vinny forwards these emails and attachments to clients, agencies, and partners, so a misspelling travels with his name on it. Run a mechanical checker over the body and over every attached document before the send, never a read-through. When no checker is installed, build one in a scratch dir (`python3 -m venv "$SCRATCH/venv" && "$SCRATCH/venv/bin/pip" install pyspellchecker`) and read the flagged list. A checker flags correct words too (names, brands, acronyms), so verify proper nouns against the source and never accept its correction for one. Fix the file, re-run the check, and only then send.

**Call the checker with a LIST of words, never one word at a time.** `spell.unknown([w.lower() for w in re.findall(r"[A-Za-z][A-Za-z']+", text)])` is correct. `spell.unknown(w.lower())` inside a per-word loop passes a single STRING, which pyspellchecker iterates character by character and returns as almost-empty, so the loop prints a clean result on a document full of unknowns. A checker that returns `[]` on prose that clearly contains jargon is mis-called, not clean: confirm the checker works by running it once against a known misspelling (`spell.unknown('teh receve'.split())`) before trusting an empty flagged list. Expect and ignore the legitimate unknowns it does flag: product names, author names, acronyms (NCCL, MLP, FP8), coinages (matmuls, microbatches, pretraining), and URL fragments. A non-ASCII name splits at the character the regex cannot match, so "Mündler-Sasahara" comes back as `ndler` and `ller`: a proper noun flagged in pieces is the tokenizer, not a typo.

## Pitfall: NEVER re-run the whole sender after you already sent

Once the script has printed "Email sent successfully" and the SMTP id, the email is delivered. Do NOT run the script again to "confirm" or after a later step, and do NOT re-write the content file after sending. Running the sender a second time sends Vinny a duplicate email, and re-writing the file after the send leaves the on-disk copy out of sync with the attachment he received (this produced a corrupted file on 2026-09-15: one post's body was blank because the file was rewritten after the email went out).

Rule: build the file, verify it, send it ONCE, then stop touching it.

## Verify the Send by Reading It Back (HARD RULE)

A clean SMTP return and a printed confirmation prove the server ACCEPTED the message, not that it arrived with its attachments intact. Close the loop in the same turn: read the delivered copy back out of the mailbox over IMAP and confirm the attachment filenames on it.

- Credentials: `set -a; source ~/.config/phantombyte/mailer.env; set +a` for `PHANTOMBYTE_SMTP_PASS`. IMAP is `imap.ionos.com:993`, login `hello@phantom-byte.com`.
- A self-send to hello@phantom-byte.com lands in INBOX within seconds. Search INBOX and Spam by subject.
- Run `scripts/verify_delivery.py --subject "<exact subject>"` (in this skill's directory). It polls, prints the delivered Date, From, To and Subject plus the attachment filenames, and exits non-zero when the message is not there. Report only what it printed.
- **A NOT FOUND from that script is not proof of non-delivery when the subject is long.** Subjects over roughly 60 characters are RFC-2822 folded in the raw header, so the stored value carries a CRLF and a leading space at the fold point and an exact-string match misses mail that is sitting right there in INBOX. Before concluding anything, list the last 8 to 10 INBOX headers and compare against the *parsed* subject (`decode_header` plus unfolding), not the raw one: `python3 scripts/verify_recent_headers.py --count 10` prints Date, parsed Subject, and attachment filenames for INBOX and Spam, and `--contains "<fragment>"` exits non-zero when nothing matches. Only after that comes back empty do you treat the send as failed, and even then check Spam before touching the sender again. A false negative that triggers a re-send delivers a duplicate, which is the worse outcome. Keep emailed subjects short enough to avoid the fold when you control them.
- Pitfall: a scripted SMTP send is NOT filed into the `Sent Items` folder. Searching there returns nothing and looks exactly like a failed delivery, which starts a re-send that duplicates the mail. `Sent Items` holds webmail-sent mail; the delivered copy in INBOX is the proof.
- `send_message()` returning an empty dict means no recipient was refused, not that anything was delivered. Do not report success on it alone.
- If the message is genuinely absent after the wait, check Spam before concluding anything, and never re-run the sender blindly: a duplicate email is worse than a delayed confirmation.
- **A subject match can be an OLDER email.** When several sends in one session share a subject stem, the verifier returns the first hit it finds and reports a delivery that belongs to a previous message, with the previous attachment on it. Confirm the message you just sent by Date against the clock and by the attachment filename, using `verify_recent_headers.py --count 8`, not by subject alone. Reading `17:39 (PDF)` as proof of a `17:41 (txt)` send is how a delivery gets misreported.

## Send the Format He Asked For, and Only That

The attachment format is part of the order. When he asks for a report, the attachment is the text file; producing a PDF, a docx, or an HTML page because it would look nicer is a substitution he will call out ("did I ask for a PDF?"). Typeset formats are for when he asks for one or has approved the format for that class of document. If a previous delivery was rejected for legibility, fix the legibility of the format he asked for, not the format itself.

Related: the layout he wants for text reports (ruled sections, ALL-CAPS headings, indented blocks, blank lines) lives in the `vinny-build-answers` skill's `templates/text-report-layout.txt`.

## Recovering an Artifact Vinny References by Name (added October 13, 2026)

Vinny refers to documents by their role ("the free domain report", "the notes I sent you"), not by a path, and those artifacts often exist only as an email attachment. Recover the real file from the mailbox instead of guessing at a local copy.

1. **Search for a string that appears only inside the artifact**, not a generic role phrase. `M.search(None, '(TEXT "FINDINGS SHEET")')` finds the document; `'(TEXT "report")'` returns hundreds of outreach emails that mention the word and buries it. IMAP TEXT search is case-insensitive and matches body prose.
2. **Search `INBOX`, `Sent Items`, and `Spam` in one pass.** An artifact produced and sent by another machine can appear in `Sent Items`, even though a scripted SMTP send from this host is never filed there.
3. **Pull the attachment.** Fetch the match, decode the subject with `decode_header`, walk `msg.walk()` for parts with `get_filename()`, and save the decoded payload under the exact filename it was sent with.
4. **Read the delivered attachment before editing it.** It is the copy Vinny is looking at, and it can differ from what any generator on this machine produces.

After correcting a delivered copy, correct the same text in the generator that produced it (grep the project for a distinctive line from the document) so the next one comes out clean. When the generator is not on this machine, say so in one line once the fix is done, rather than implying the source is covered.

When the on-disk file and the delivered attachment no longer agree because you fixed a defect after sending, send the corrected copy once with a subject that says what it is ("corrected copy") and name the change in the body. That is not the blind re-send the pitfall above warns about, because the file is different and the label says so.

## Re-sending a File a Cron Job Already Emailed (added October 28, 2026)

When Vinny replies to a cron notification with "resend this text file," the file he means is the artifact that job wrote, not the run transcript. Locate it by the job's own filename pattern and modification time, then email it again as an attachment.

1. **Find the artifact by pattern and mtime, with today's date in the name.** Daily jobs write a date-stamped file outside the cron directory (for example `~/pinterest_posts_YYYY-MM-DD.txt`). `ls -la` it and confirm its mtime matches the run time in the notification; a same-named file from yesterday is a different deliverable.
2. **Do not send the transcript under `~/.hermes/cron/output/<job_id>/`.** That directory holds the job's own run log (`YYYY-MM-DD_HH-MM-SS.md`), which is the agent's working record and can carry internal notes. It is a pointer to what ran, never the attachment Vinny received.
3. **If the pattern does not turn up the file, read the newest run log for the exact path the job wrote,** or fall back to the delivered copy in INBOX (see the artifact recovery section above).
4. **Email it again with a subject that says what it is** (`<topic> resend - <date>`), attach the file under its existing name, and confirm delivery by reading the headers back. Do not paste the content into Telegram; a resend means the same attachment path as before.

## Money-Making Cron Philosophy (July 10, 2026)

See `references/money-making-cron-philosophy.md` for the full origin story and philosophy.

Key rules for the money-making cron (job_id: 8e8f6f6f10e1):
- **NOT** a tutorial/article writer — that pipeline exists separately
- Finds specific, low-budget, actionable money-making opportunities from daily data files
- Saves text file to `Desktop/MONEY MAKING OPPORTUNITIES/` with date-stamped filename
- Emails as attachment to hello@phantom-byte.com
- Telegram notification is just "Email sent with today's money-making opportunities" — nothing more
- The philosophy: the infrastructure (data collection) is not the product. The throwaway idea found in the data is the product.

## Reminder vs Task Distinction (July 10, 2026)

When Vinny says "remind me of this in X time" or "remind me about X":
- Set the reminder cron job
- Confirm it's set
- **Do not** turn it into a task, discussion, or configuration session
- The reminder fires on schedule and delivers the message. That's it.

## Important
- Do NOT say "I can't email" — the capability exists via this skill
- Always check this skill first before trying any other approach
- SMTP credentials are stable as of May 2026 — if they break, check IONOS webmail login at https://webmail.ionos.com/
- The inline `python3 -c` approach FAILS with this SMTP server even with correct credentials — always use a file

## CRITICAL PITFALLS (June 15, 2026)

### Silent SMTP Failure — Exit Code 0 Means Nothing
The script can return exit code 0 and still fail to send. SMTP errors, auth failures, or connection timeouts may be swallowed if the script does not explicitly surface them. Always add `server.set_debuglevel(1)` when debugging a send, and always include a confirmation print after `server.send_message()`. If the output is empty, the email was NOT verified as sent. This is the most common cause of "the email was never sent" reports from Vinny.

### "Send me that file" means EMAIL, not Telegram
When Vinny says "send me that file" or "send me that right" after you already sent it to Telegram, he means **email it to him as a .txt attachment**. Do NOT send it to Telegram again. The SMTP library should be invoked immediately — no detour through Telegram delivery.

### File must already have proper extension before emailing
When creating a document for Vinny that will be emailed, write it with the correct extension from the start (`.txt`, `.md`, `.pdf`, etc.). Do NOT write it without an extension and then copy it to a different filename. Write it correctly the first time.

### No shortcuts, no bullshit
Vinny has explicitly stated: "you niggas better stop with the shortcuts and bullshit." This means:
- Do the full correct workflow every time, not a fast partial version
- If there are two ways to do something (Telegram vs email), do the one he asked for — don't pick the easier one
- If you're unsure, the answer is not "send to Telegram and see" — it's "do it right the first time"

## TO Address Verification (CRITICAL — May 31, 2026)
**Before every send, verify the TO address matches Vinny's ONLY email: hello@phantom-byte.com.**

- If you're unsure or the instruction says a different address (e.g. "[REDACTED_EMAIL]" without the hyphen), stop and use the correct one. Do not guess.
- **Session proof (May 31, 2026):** Vinny said "[REDACTED_EMAIL]" in the prompt. I sent to that. But his real email is hello@phantom-byte.com (with hyphen). I had to resend after being corrected. Cost: multiple resends, wasted trust, and justified fury.

## Pre-Flight Email Address Audit (CRITICAL — June 21, 2026)
**Before running the email script, grep for every email address in it and verify each one:**

```bash
grep -oP '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' "$SEND_SCRIPT"
```

where `$SEND_SCRIPT` is this run's job-specific script path (see Usage Pattern). It comes from the run's unique `mktemp -d` directory, never a fixed path.

This catches both the TO address and any email addresses embedded in the body text. Every address returned must match hello@phantom-byte.com (or the explicitly authorized recipient). If any address is wrong, fix it in the script before running. Do not skip this step — it takes 2 seconds and prevents the most common email failure mode.

## Check Email Addresses INSIDE the Email Content (CRITICAL — May 31, 2026)
When the email contains an email address in its body (e.g. a prompt telling Pi to "email the finished app to X"), verify that nested email address too. Don't just get the TO right and miss the address embedded in the content.

- **Session proof (May 31, 2026):** I fixed the SMTP TO address from [REDACTED_EMAIL] to hello@phantom-byte.com, but the email BODY still said "send the finished app to [REDACTED_EMAIL]" — a second wrong address hiding in the content.
- **Fix:** After writing the email body, grep/search for every email address string in it and verify each one against the known correct address.

## Two-Email Backup Architecture (June 2026)
When Vinny asks to email himself a copy of something (prompts, configs, documents), understand the system behind it:

- **Hot bucket** (his working email) — he works out of this daily, risk of accidental deletions
- **Cold bucket** (secondary email, never used for anything else) — pure read-only archive
- Any harmless/non-sensitive file gets emailed as a spare copy. If he or an agent fucks up an edit, the original is still in the email.
- Reason: "I delete my own shit a lot." Two-email system ensures nothing is ever truly gone.
- **Default delivery address for backup copies:** hello@phantom-byte.com (the working/hot bucket is always the target for backups unless otherwise specified)

## Vinny's Execution Mandate (CRITICAL — DO NOT VIOLATE)
- When Vinny says "send this to email" and explicitly includes "this IS the permission" or any variant of that, DO NOT ASK for confirmation. Execute immediately.
- Zero confirmation questions. Zero "shall I proceed?" Zero "do you want me to send it now?" He told you to do it. Do it.
- This rule also applies in reverse: do NOT touch/modify/delete his files without being asked. He will explicitly tell you when he wants action. When he does, act — don't ask if he's sure.
- If he specifies the full content, subject, and recipient in the prompt, he's done his job. Your job is to write it and send it. Full stop.

## "Email" = SMTP Delivery, Not Clipboard Text (CRITICAL — May 31, 2026)

**Vinny does NOT copy-paste from Telegram.** When he says "send me an email" or "email me X," he means:
1. Write the content to a file
2. Send it via SMTP (hello@phantom-byte.com → [REDACTED_EMAIL])
3. Confirm it's sent

**DO NOT:**
- Output email text in the chat and say "copy this and send it"
- Give him text to paste into Telegram, PI Coding, or anything else
- Ask "where should I send it" — he already told you
- Produce a "prompt you can give to Pi" as chat text when he said "email me"

**Session proof (May 31, 2026):** Vinny asked to "send me the fucking email." I produced a text block in Telegram and said "copy-paste and send." He responded: "I am not copying and pasting shit unless it's from my fucking email." Three times he had to tell me before I actually sent it via SMTP. The failure was treating "write and send email" as a text-generation task instead of a delivery task.

**The test:** If Vinny says "email me" or "send me an email," the SMTP library should be invoked. Full stop. The only correct first response is writing the email.py and running it — not producing text in the chat.