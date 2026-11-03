# Proving the outreach send path, and the dedupe gate

A successful SMTP call is not proof. These are the checks that are, run in one session before any real prospect is written to. Each one is cheap; each one has already been skipped once and shipped a false claim.

## 1. Render the message from a real row shape, never a hand-written body

Import `outreach.py`, build a row in the exact shape `email_scan.py` writes (at minimum `domain`, `defect_codes`, `qualified`), and call `build_message(row, offer_url)`. **It returns a 4-tuple, not a pair:** `(subject, body, kind, code)`, where `kind` is the template variant chosen and `code` is the defect code that variant names. Unpacking it as two values dies with `too many values to unpack (expected 2)`, so unpack all four. Set `PHANTOMBYTE_POSTAL_ADDRESS` in the environment first, the same as a real send. Print the subject and the body, then assert:

- no literal `{domain}` or `{postal_address}` survived into the text (a missing `.format()` slot ships a brace into real mail)
- no dash-as-separator anywhere, including inside the URL
- the variant selected is the one whose defect code is still live on the domain, chosen by `pick_template`'s priority order, NOT the row's first `defect_codes` entry. A row can carry several codes (153 of the 243 qualified rows did), so the first code in the CSV is frequently not the one the email is about. `pick_template` returns `(kind, code)` and `recheck_defect` confirms that returned `code`, which is what makes the email's claim true at send time. Never rewire it back to the first code in the row.

Repeat for one synthetic row per defect code. A new variant added to `SUBJECTS` but missed in `QUESTIONS` only shows up here.

Two things to read in the rendered output rather than assume:

- **The greeting is deliberately conservative.** `greeting_for(person, email)` uses a first name only when the printed name corroborates the mailbox, and falls back to `Hi there,`. That is correct behavior, not a bug, so do not "fix" it to always use a name; a garbage name reaching a greeting is the worse failure.
- **The fixed-price paragraph was removed on 2026-10-05.** The old "Two ways to fix it ... $29.99 ... flat $500" hard sell is gone; the body now carries a "why now" beat (`CHANGE_NOTE`, the Gmail/Microsoft enforcement) and ends with a soft close (`NO_PITCH`, the free checker), so the email reads as a heads-up rather than a pitch. Removing the price does NOT make it non-commercial under CAN-SPAM; the postal line and opt-out stay. Verify the rendered body names the change, carries no price, and leaks no brace.

## 2. Prove the send by reading it back, not by the absence of an exception

Send to Vinny's own address, then fetch it over IMAP and print the body and the `Authentication-Results` header. Confirm in that read-back:

- the postal address line is present
- the opt-out line is present
- the offer URL is present
- `dkim=pass`, `spf=pass`, `dmarc=pass`

If the message is NOT in the inbox, do not stop at "filtered". A message REJECTED
at the gateway leaves no header anywhere, so check for an authentication refusal
in the mailbox DSNs and in `auth_rejections.txt` (Microsoft `5.7.515` /
`5.7.509`) before calling it a placement problem. A gateway auth rejection means
the SENDING domain failed its own records; the recipient is fine and is never
suppressed. Run `python3 domain_preflight.py <sending-domain>` to prove the
records before blaming placement.

```python
import imaplib, ssl, email
M = imaplib.IMAP4_SSL('imap.ionos.com', 993, ssl_context=ssl.create_default_context())
M.login('hello@phantom-byte.com', <mail password>)
M.select('INBOX', readonly=True)
st, ids = M.search(None, 'ALL')
st, data = M.fetch(ids[0].split()[-1], '(BODY.PEEK[])')
msg = email.message_from_bytes(data[0][1])
print(msg.get('Subject'), '|', msg.get('Authentication-Results'))
```

Addresses used for this are throwaway or Vinny's own. A test that reaches a real stranger is not a test.

## 3. Negative-test every refusal

A safety check never observed firing is an untested check. Run `--send` and confirm the refusal, for each of these:

- `PHANTOMBYTE_POSTAL_ADDRESS` unset, every message refused
- `PHANTOMBYTE_SMTP_PASS` unset, login refused
- the sending domain fails its own SPF/DKIM/DMARC (`PHANTOMBYTE_SENDING_DOMAIN`
  set to a failing domain), refused by the auth pre-flight before any send is
  composed
- a row whose domain does not exist, refused by the live DNS re-check
- our own clean domain, refused by the live DNS re-check
- an address on `stop_list.txt`, dropped before send

## 4. Negative-test the dedupe

Record one send in `outreach_log.csv`, then assert all four:

- the same domain with a different address is blocked
- a second domain at the same address is blocked
- with `state.json` deleted, the domain is still blocked (history rebuilt from the log)
- an unrelated fresh domain is still allowed

Clean up `state.json` and `outreach_log.csv` after, or the test's fake rows block a real one. This only applies if you recorded the send by hand against the production files. `test_outreach.py` no longer can: it and the CLI it drives are redirected to a per-run temp directory, so a suite run leaves the production state and log untouched. See `references/state-file-protection.md`.

## 5. Clear test artifacts before a real run

`email_scan_results.csv` and any probe CSV are test debris. Delete them before the real scan, or the stale rows mix into the live run.

`state.json` and `outreach_log.csv` are NOT debris. They are the campaign's contact history, and they are the one thing in this folder that must never be deleted. `test_outreach.py` used to destroy them on every passing run; it no longer can, because it runs against a per-run temp directory. Never clear them to "start fresh": a deleted history is how someone who already received an email gets written to twice. If either is genuinely lost, rebuild it from the IONOS mail host rather than starting empty, per `references/state-file-protection.md`.

## 6. Read the staged drafts back out of the mailbox, not out of the render

The render step proves what `build_message` produced. It does not prove what landed in the mailbox, because the append path builds a second message object and the folder is the thing a human will send from. Verify against the live folder, per message:

- fetch every draft by UID with `M.uid('FETCH', uid, '(RFC822)')` and decode the body
- assert the body carries **no** line starting with `Subject:`, and that its first non-blank line is the greeting (`Hi there,` or `Hi <Name>,`)
- assert the `Subject` header is non-empty, since the subject no longer comes from the body
- assert no recipient appears twice
- assert the state-file UIDs and the folder UIDs are the same set in BOTH directions, so a state entry cannot point at a draft that is not there
- assert `outreach_log.csv` is absent or unchanged, because staging is not a send

Then prove the dedupe actually sees the staged set: run `outreach.py` dry over the same CSV and confirm `dropped, already contacted` equals the number staged, with none of the staged domains on a `[would send]` line. Reading `state.json` back proves nothing about the gate.

Cleanup that is part of the restage, not a separate step: copy each draft to Trash, confirm the folder is empty, and only then stage the new batch. A delete issued against a sequence number instead of a UID removes the wrong message and reports success, and a folder holding both the old and the new batch is one hand-send away from mailing the wrong body.
