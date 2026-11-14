---
name: scheduled-mail-staging
description: Use when staging mail to send later via a webmail API.
version: 1.0.0
author: hermes-curator
license: MIT
metadata:
  hermes:
    tags:
      - email
      - ionos
      - imap
      - scheduled-send
    related_skills:
      - email-sender
      - email-sender-cron
---

# Staging Mail to Send Later

Putting messages into an account's "scheduled" folder through a webmail API, with a send time, instead of sending them immediately. Covers the payload requirements that make a staged message actually deliver, how to verify a folder of queued mail, how to rebuild messages that already died, and how to prove an undocumented provider error code.

Vinny's live implementation is `~/money_ideas/schedule_drafts.py` for IONOS. The IONOS specific recipe, covering the endpoint sequence, the required sender field, the recipient shape, the `dateToSend` format, and the HTML content requirement, is in this skill's `references/ionos-ox-scheduled-mail.md`. For sending immediately rather than queuing, use the `email-sender` skill.

## When to Use

- A message is being queued to send later through a provider's webmail or mail API rather than sent immediately.
- A message must be staged in the account's Drafts folder for the user to review and press send himself.
- A provider reports that a scheduled message could not be sent, or a scheduled folder needs auditing for what will actually leave.
- Queued mail has failed and the dead messages must be rebuilt and re-verified.

## Rule 0: Staging a draft is IMAP append plus read-back, not an API call

The OX compose API is the send-later path. A message left in **Drafts** for a human to review is built locally and appended over IMAP instead, with the same discipline: set every header yourself, then read the stored message back and prove it.

```python
msg = MIMEMultipart("mixed")          # or "alternative" when there is no attachment
part_plain = MIMEText(body_text, "plain", "utf-8")
part_html = MIMEText(body_html, "html", "utf-8")
alt = MIMEMultipart("alternative"); alt.attach(part_plain); alt.attach(part_html)
msg.attach(alt)                        # attachments attach to the outer "mixed" part
msg["From"] = "Vinny Barreca <hello@phantom-byte.com>"
msg["To"] = to_addr
msg["Subject"] = subject
msg["Date"] = email.utils.formatdate(localtime=True)
M.select("Drafts"); M.append("Drafts", None, None, msg.as_bytes())
```

- Capture the UID set before the append, append, then re-list and take the UID that is new. Never assume the append returned the UID.
- Read the new UID back with `BODY.PEEK[]` and assert: `From` is the account address, `To` matches, the subject is on the header and absent from the body, the paragraph count survived, the promised fixed lines are present, and the attachment is on the stored message.
- A restage clears the folder first. Copy each old draft to `Trash` before flagging it deleted, confirm the folder is empty by count, and only then append the replacement. Trash is the undo for a wrong-UID delete.

### Comparing a stored header is not comparing a string

Do not assert equality against the raw stored header value. A long `Subject` is stored RFC 2047 folded, so it comes back with `\r\n` and a leading space in the middle, and a byte comparison reports a false failure on a message that is completely correct. Normalize both sides before comparing:

```python
stored = (msg.get("Subject") or "").replace("\r", "").replace("\n", " ")
stored = " ".join(stored.split())
assert stored == expected
```

Better still, use a subject under roughly 70 characters, which is what a reader's client shows anyway.

### The folder is the source of truth for what the user will open

`state.json` and any staging manifest are fast paths. The Drafts folder is what he actually sees. When they disagree, reconcile to the folder and correct the tracker. A restage driven by the tracker leaves orphans it cannot see, and the user opens a draft you believe you replaced.

### Ready-made stager

`scripts/stage_draft.py` does the whole draft path in one call: builds plain and HTML from one body file, sets every header, appends to `Drafts`, clears the folder first under `--replace` (copy to `Trash` confirmed before any delete), finds the new UID by set difference, and exits 1 unless every read-back check passes. Use it instead of writing a fresh staging script per task, and use `--dry` first when the body was just written.

```
python3 scripts/stage_draft.py --to someone@example.com \
    --subject "Short subject" --body-file body.txt [--attach /path/file.docx] [--replace] [--dry]
```


## Rule 1: The staging call succeeding is not the message sending

A create-and-schedule endpoint accepts payloads that are structurally incomplete. It answers `200`, the message appears in the scheduled folder looking correct, and then the server refuses to deliver it at the send time and notifies the account afterwards. Queued mail fails HOURS after you staged it, one message at a time, and is never retried.

So never report a staging run as done off the response code. Read every queued message back off the folder and check its stored headers and body. The read-back is the acceptance test.

## Rule 2: A queued message must carry every identity field explicitly

The field that makes a message deliverable is usually present by default on an immediate send and absent on a queued one. Set sender identity, recipient, subject, body, content type, and the send time in the payload yourself. Anything left to a provider default is a candidate for the silent-death failure in Rule 1. When in doubt, set the field explicitly rather than relying on what the provider fills in.

Recipient shape is its own trap: the API accepts several shapes at create time and only one is readable at send time. A value the server cannot interpret is sometimes stored as the literal string it printed and refused later. Prefer the explicit `[[localpart, address]]` form, and re-verify a recipient you changed.

## Rule 3: Verify the stored message, not your intent

Fetch each queued message with `BODY.PEEK[]`, parse it with the `email` module, and check the stored artifact:

- The sender identity header is present and is the account's own address. A missing sender identity is the classic silent-death cause.
- The recipient header matches the intended address.
- The body shape survived the API's transformation. HTML-composing APIs collapse plain-text newlines into one unbroken block, so paragraphs must be re-checked, not assumed. Compare the stored paragraph count against a reference message that was already sent and read correctly, not against what the source string looked like.
- The subject is on the header and NOWHERE in the body. Strip the tags from the stored body and assert the whole subject string and each of its clauses are absent from the body text. This is the one assertion that cannot be made from the template, because the duplication or the collapse happens after rendering and only the stored message shows it.
- The fixed content the template promises is present: the postal line, the opt-out line, the offer URL, and the recipient's own domain.
- The send time, read off the server's own scheduling header, is within a minute of the intended slot.
- The folder count equals the count you intended. Probe messages or leftovers from an earlier attempt make the count untrustworthy, so clear them before staging and check the count again after.

Fail the whole run if any check fails. Do not save the send-tracking state until the read-back passes, or the tracker records messages that will never leave.

**When the read-back does fail, the messages are already queued and the state was never written, so re-running the same command double-queues every one of them.** Failing before the state save is what keeps the tracker honest, and it is also what opens this hole: the folder now holds live mail the tracker has never heard of, so the next run sees a clean slate and stages the same recipients again. Recover by reading the FOLDER, never by re-running the command: reconcile the tracker from the live folder contents (recipient, mail id, send time, status) or empty the folder and confirm it is empty by count, and only then stage again. A rebuild that starts from the tracker cannot see the orphaned messages at all.

## Rule 4: Rebuild dead messages by backing up first

When queued messages have already died:

1. Back up every raw message in the folder before touching anything. Fetch each one's raw bytes and write them to a durable file.
2. Delete the dead messages and confirm the folder is empty. An empty folder makes the post-rebuild count meaningful.
3. Re-create each message from the backed-up raw part, adding the missing field, keeping the original subject, recipient, and body, and assigning a fresh send-time slot.
4. Read the folder back and prove every message before reporting anything.
5. Update the send-tracking state so each recipient points at the new mail id, or a later run will treat the old dead message as the live one.

## Rule 5: Prove an undocumented error code with a minimal A/B probe

When the provider reports a coded error with no public documentation, do not guess, do not go hunting through the sending code hoping to spot the cause, and do not hand the test back to the user. Schedule two self-addressed messages minutes apart that differ in exactly one field, then read every folder back and see which one delivered. A scheduled probe costs nothing, reaches no real prospect, and converts an unknown vendor code into a proven cause in one round. Then fix the code path and the already-queued messages in the same turn.

The same probe confirms the fix: the arm carrying the corrected field must reach the sent folder, and the arm without it must fail.

## Rule 6: Folder names differ from your guess

Do not assume the sent folder is called "Sent". Discover the folder list from the server (`LIST`) before searching, and treat a failed `SELECT` as a wrong name rather than an empty folder.

## Rule 7: Search criteria are fragile

IMAP `SEARCH` can error out on a criteria string with several quoted terms. Search one term at a time, or list `ALL` and filter in Python. A `BAD expected ... instead of "end of data"` error means the criteria string is broken, not the mailbox.

## Rule 8: Verify a send time in the target timezone, never UTC against UTC

A queued send time can only be checked by converting the server's own scheduling timestamp into the timezone the user named, then comparing it to the wall clock they asked for. Call the zone by name:

```python
import datetime, zoneinfo
tz = zoneinfo.ZoneInfo("America/New_York")
local = datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).astimezone(tz)
```

- **A comparison made with both sides in UTC cannot fail, so it proves nothing about the local clock.** A sender's own verifier typically builds the intended slot in UTC and reads the stored slot in UTC, so it stays green even when the message is queued for the wrong local hour. The timezone assertion is the one thing an independent read-back has to add, and it is the reason to run one even after the script reports success.
- **Read the epoch without converting and the times print hours away from the requested slot, which reads as a broken run and is not one.** Convert before you judge it, and say in the output which zone you converted into.
- **Use the named zone, not the machine's ambient offset.** An ambient offset is whatever the host happens to be set to and it moves at a DST boundary, so a run staged under one offset and verified under another appears to disagree with itself for no real reason.

## Diagnosing a failed cold send

When Vinny asks why a share of a batch did not go out, read the account's INBOX over IMAP and triage the failure notices before proposing anything. Full procedure, the four failure classes, and the role-address pattern that distinguishes a list-quality problem from a sender-reputation problem: `references/bounce-triage.md`.

Never report a bounce rate without the soft/hard split and the sent volume behind it. A hard-bounce cluster that is entirely `info@`/`contact@`/`hello@` means the addresses were guessed, and the fix is pre-send verification, not a change to the sending path.

Prove the verifier before trusting it: run it against one known-live address and one known-dead address. A check whose network path is silently dead returns UNKNOWN for everything while still printing a clean summary, so it looks healthy and checks nothing. The bounce notices are the cheapest available source for a suppression list, so harvest them instead of re-deriving it by hand each time.

## Failure notices arrive one at a time

Providers notify about queued-mail failures AFTER the send slot, one notice per message, not one summary. A folder of dead mail produces a trickle starting at the first slot. Searching the whole account for the provider's failure-notice subject is the fastest way to learn how many messages died and to confirm none are still queued.

## Rule 9: Reconcile the send history off every source before staging

The tracker (a state file, an index, a database row) is the fast path, not the record. It can be empty, truncated, or missing while the real history sits on disk and in the mailbox, and a staging run that trusts it will happily queue a message to someone who has already been written to. Staging time is where this is invisible: the folder looks clean and every response code is a success.

Before staging, read the tracker and, whenever it is empty or suspiciously short for the volume already sent, reconcile against every history source: each dated tracker backup, any plain-text contacted-domain list kept beside it, and the addresses in the sent folder fetched over IMAP. A candidate whose domain OR address appears in any one of those is not a candidate. Report how many were reconciled and how many survived.

- **An append-only send log is not a substitute.** It records what the pipeline sent, so mail that went out by hand outside the pipeline is invisible in it, and mail that is merely queued is correctly absent. Only the sent folder carries both.
- **Do not treat an empty tracker as a fresh start.** It is far more often a lost index than a genuinely new account, and the failure it causes is the one that turns outreach into spam.

## Rule 10: Confirm the batch arguments, not the defaults

A staging front end that drives another renderer usually carries defaults pointing at one dataset. Staging a different batch without overriding them renders and queues the wrong rows while every check still passes, because the run is internally consistent about the wrong list. Pass the dataset explicitly on both sides of the pipeline (the render step and the staging step) and confirm the rendered count against the size requested before anything touches the mailbox.

## Rebuild the sender's own verification too

When you fix the cause, add the check for it to the sending script's own verification step in the same edit, so the same defect cannot pass a future run. A verification that omits the field that killed the last batch is not a verification.
