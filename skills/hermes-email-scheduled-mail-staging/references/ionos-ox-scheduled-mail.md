# IONOS Scheduled Mail via the OX App Suite API

The schedule-later path: stage messages into the IONOS `Scheduled` folder with a send time instead of sending them now. Verified live against App Suite 8.46.152. Reference implementation: `~/money_ideas/schedule_drafts.py`.

## The one rule that matters

Every staged message MUST carry an explicit `from` field in the compose payload.

```python
payload = {
    "from": [["Vinny Barreca", "hello@phantom-byte.com"]],
    "to": [["", to_addr]],
    "subject": subject,
    "content": html_body,
    "contentType": "text/html",
    "dateToSend": when_utc.strftime("%Y%m%dT%H%M%SZ"),
    "meta": {"type": "new"},
}
```

Omit `from` and the server accepts the staging call, stores the message in `Scheduled`, then kills it at send time and mails the account a notice reading "Your scheduled mail could not be sent" with `An unexpected error occurred: MSG-0037`. The dead message stays in the folder and is never retried, so the failure is silent at staging and only surfaces hours later, one message at a time, starting at the first send slot.

The field is easy to drop because the same API sends an unscheduled message happily without it. In a controlled test the two arms were identical except for `from`, and only the arm carrying `from` delivered.

## Endpoints, in order

1. `POST https://email.ionos.com/appsuite/api/login?action=login`, form `name=<account addr>&password=<pw>` -> `{"session": "..."}`.
2. `POST /appsuite/api/mail/compose?session=<s>&type=new`, JSON body `[{}]`, header `Content-Type: application/json` -> `{"data": {"id": "draft.<hex>"}}`.
3. `POST /appsuite/api/mail/compose/<cid>/send?session=<s>&force_json_response=true`, multipart with `files={"file_0": (None, "")}` and `data={"JSON": <payload>}`. Success answers `{"data": {"id": ..., "folderId": "default0/Scheduled"}}`. Treat a `folderId` not ending in `Scheduled` as a failure, and treat a non-JSON response as a failure, never as a success.

`dateToSend` is UTC with a `Z` suffix, `YYYYMMDDTHHMMSSZ`.

## Recipient shape

`to` must be `[[localpart, address]]` or `[[address]]`. A `[None, None, addr]` shape is read as the literal string `null` and refused with `MSG-1008`. A bare address string is accepted at create time but produces "no recipient" at send time.

## Content is HTML

The compose API treats `content` as HTML and collapses newlines, so a plain-text body arrives as one unbroken block. Convert: blank lines become `<p>` paragraphs, single newlines become `<br>`, and escape the text so a stray angle bracket cannot inject markup.

## Verification by read-back

A `200` from the send call proves nothing about what will leave. Read the messages back off the folder over IMAP and check them:

- Host `imap.ionos.com`, port `993`, SSL.
- The folder names are not what you would guess: `Scheduled` selects as `"Scheduled"`, the sent folder is **`"Sent Items"`** (selecting `"Sent"` returns `NO`), plus `INBOX`, `Drafts`, `Spam`, `Trash`.
- Each staged message carries `X-OX-Date-To-Send` (epoch milliseconds) and `X-OX-Scheduled-Mail-Id`. It has no `Date` header until it actually sends, and no `From` header if `from` was omitted.
- Fetch with `BODY.PEEK[]` and parse with the `email` module. Check per message: `From` equals the account address, `To` matches the intended recipient, paragraph count matches the source, the postal line, the opt-out line, the offer URL, and the send time within a minute of the intended slot.
- Fail the whole run if any message lacks a `From`. A folder of messages that look right but carry no `From` is a folder of messages that will all die at MSG-0037.

IMAP search criteria with several quoted terms in one string can error with `BAD expected ... instead of "end of data"`. Search one term at a time, or list `ALL` and filter in Python.

## Rebuilding messages that already died

1. Back up every raw message in the folder first (fetch `BODY.PEEK[]` per UID, write as JSONL).
2. Delete the dead ones: select `"Scheduled"` read-write, `UID STORE <uid> +FLAGS (\Deleted)`, then `expunge`. Confirm the folder is empty before re-creating, so no leftovers inflate the count.
3. Re-create each one from the backed-up raw part: re-parse the stored HTML body, keep the original subject and recipient, add `from`, and assign a new `dateToSend` slot.
4. Read the folder back and prove every message. Only then update the send-tracking state file.

Keep every domain's send-tracking entry keyed to the fresh mail id after a rebuild, or a later run will treat the old dead message as the live one.

## Confirming an unknown send failure with an A/B probe

When the service reports a coded error you cannot find documented, do not guess. Schedule two self-addressed messages minutes apart, identical except for the one field you suspect, then read every folder back and see which one delivered. `Scheduled` is ideal because a staged probe costs nothing and cannot reach a real prospect. This turns an undocumented vendor error into a proven cause in one round.

## The notice mail

Failures arrive in `INBOX` from `IONOS Webmail <appsuite@mail.ionos.com>`, subject `Your scheduled mail could not be sent`, naming one subject per notice. Several dead messages therefore produce a trickle of notices at the first send slot, not one summary. Searching the whole account for that subject is the fastest way to learn how many messages died.

## Staging a draft instead of a scheduled send

When the user wants to review and press send himself, do not use the compose API at all. Build the message locally and append it over IMAP to the `Drafts` folder, then read it back with `BODY.PEEK[]` and check every field. Full field list and the header-normalization rule are in the parent SKILL.md.

- The same login works for both paths: `hello@phantom-byte.com` with the password from `$PHANTOMBYTE_SMTP_PASS` or the `ionos-email-access.md` reference.
- `Drafts` is also where a message that was composed in the webmail UI and never sent sits, so a restage that reads the folder will find drafts it did not create. Clear by count, confirm empty, then append.
- To replace a draft: read the folder, take the UIDs, `UID COPY <uid> Trash` (confirm `OK`), `UID STORE <uid> +FLAGS (\Deleted)`, `expunge`, confirm the folder is empty, then append the replacement.

## Account context

- Sending account: `hello@phantom-byte.com`, display name `Vinny Barreca`.
- Credentials and the IONOS DNS API notes live in `~/skills/user-profile/vinny-profile-extension/references/ionos-email-access.md`.
- The scheduling script reads the password from that reference or from `$PHANTOMBYTE_SMTP_PASS`.
- The prospect-outreach staging flow lives in `~/money_ideas/`: `outreach.py` renders the drafts, `schedule_drafts.py` stages them and verifies by read-back, `state.json` tracks per-domain status.
