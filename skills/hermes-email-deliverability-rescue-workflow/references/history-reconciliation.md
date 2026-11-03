# Reconciling the contact history against the mail host

`state.json` is the local index of who has been contacted. The mail host is the durable record. When the two disagree, the host wins (Article 17), and a history that is shorter than the host's record leaves previously contacted prospects unblocked and mail-able a second time.

## What a `sent` row in state.json actually means

A row marked `status: "sent"` is NOT proof of a send. When auditing, split the `sent` rows into two classes before quoting any number:

- **Real sends**: carry both an `email` address and a `sent_at` timestamp. This is the only class that counts as "written to."
- **Legacy rows**: marked `sent` with NO address and NO `sent_at`. These are historical residue from an older tracking scheme that marked a whole source list as sent, not per-recipient sends. Counting them inflates the send total massively.

Report the two classes separately. In one audit, 267 rows carried `status: sent`; only 22 had an address and a timestamp. The other 195 had neither, and the mail host's own `Sent Items` folder held no prospect mail at all, which is what settled it.

## The host is authoritative, and it records three different states

Read all of these over IMAP before drawing a conclusion. A folder count of zero does not mean nothing was sent; the sends may have been archived or trashed afterward.

- **`Scheduled`** holds mail queued with a future send time. Read the folder, not `state.json`'s `scheduled_at`, and count distinct recipient domains.
- **`Sent Items`** holds completed sends. Note the name exactly: the IONOS tree lists it as `"Sent Items"`, and a search for `Sent` will miss it and produce a false "nothing was ever sent."
- **`Trash`** matters, and this is the one that gets missed. Sent mail is frequently moved to Trash after a read-back, so a folder holding only "mail delivery failed" and report subjects can still be where a whole batch of sent prospect mail lives. Scan it and filter by recipient.

Filter out your own address and known non-prospect recipients (agent inboxes, test sends, personal mail) before reporting a prospect count.

## A rebuild from IMAP recovers only what is in the folders right now

Rebuilding `state.json` from the host restores the scheduled and in-folder sends, and it silently loses everything that was sent and then archived out of those folders. The rebuilt file is therefore not equivalent to the pre-wipe file, and the gap is exactly the set of people who can now be emailed twice.

Measure the gap rather than assuming it is closed. Compare the live `state.json` against the most recent backup and count both directions:

```bash
~/.venv/bin/python - <<'PYEOF'
import json
live = set(json.load(open('state.json')).get('contacted', {}))
for bak in sorted(__import__('glob').glob('state.json.bak-*'))[-4:]:
    b = json.load(open(bak)).get('contacted', {})
    bs = set(b)
    sent = {d for d, v in b.items() if v.get('status') == 'sent'}
    print(f"{bak}: {len(bs)} rows, {len(sent)} sent, "
          f"{len(bs - live)} missing from live, {len(sent - live)} sent-missing")
PYEOF
```

Backups whose file is empty or truncated are backups taken AFTER a wipe. Identify the most recent backup that still has rows, and treat its row set as the floor for what the history should contain.

## Report it as a risk with the number attached

Name the count of unblocked-already-contacted domains in one line and offer the reconcile as a single decision. Do not bury it, and do not fix it silently: adding rows to the history changes what the pipeline will refuse to send, which is his call.
