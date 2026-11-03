# Staging drafts into IONOS (the manual-review path, superseded)

Kept only for the case where Vinny asks for drafts again. The scheduling path in
SKILL.md is the current method.

```
source ~/.config/phantombyte/mailer.env
python3 stage_drafts.py --offer-url https://phantom-byte.com/email-deliverability-rescue --limit 20
```

1. It runs `outreach.py` dry with `--drafts <mktemp dir> --limit 20`. That selects the day's 20 through the full gate chain (qualified, fit screen, dedupe, cap) and writes one rendered message per domain. Nothing sends.
2. It parses each file's `To:` and `Subject:` lines, builds a MIMEText with `From: Vinny Barreca <hello@phantom-byte.com>`, and appends it as `M.append('Drafts', None, None, msg.as_bytes())`. Each draft then appears in webmail ready for a hand send.
3. It reads the folder back and prints every message's To and Subject. Count the folder and read the bodies back, do not trust the append loop's exit.
4. **Mark every staged domain in `state.json` in the SAME pass, as part of the load step, never as a follow-up run.** Vinny's standing instruction: when the drafts are loaded into the mailbox, `state.json` is written in that same run. Read the Drafts folder back over IMAP to get the real domain list, then write one `contacted` entry per domain with `status: "draft"`, `staged_at`, `draft_folder`, and `draft_uid`, and no `sent_at`. Back `state.json` up first. Never write a staged draft to `outreach_log.csv`: that file is the record of sends, and 20 draft rows there would claim 20 sends that never happened.
   - **Verify it by the dry-run count, not by reading the state file.** `outreach.py --list state.json` shows the entries, and a dry run must report `dropped, already contacted` equal to the number staged, with none of the staged domains appearing on a `[would send]` line. Reading the JSON back is not proof that the dedupe sees it.
   - **The entry shape matters.** `load_state()` folds the log in with `setdefault`, so a draft entry carrying no `sent_at` survives the fold and is not clobbered by the real send that comes later.
   - **Build the list from the folder read, never from a remembered list or a list quoted in chat.** On 2026-09-20 the recipient list carried in the conversation named only 19 domains and omitted one that was actually staged (`bayshorebaptistchurch.com`, Drafts UID 12); reading the folder is what caught it.

Pitfalls:
- **Address every IMAP operation on the Drafts folder by UID, never by sequence number.** On this server the two are different values for the same message (the first message read as sequence 1 and as UID 447, and message 20 as sequence 20 and UID 535), so `M.search`, `M.fetch`, `M.store` and the delete all run through `M.uid(...)`. A delete issued against a sequence number removes the wrong message silently, and the run reports success either way.
- **A restage keys on the folder read, never on `state.json`.** UIDs recorded in state can point at messages that no longer exist, so a delete driven by the state file leaves stale drafts in the folder while state claims they are gone. Read the folder, trash every message in it, confirm the folder is empty, then clear the draft entries.
- **Copy a draft to Trash before flagging it deleted.** Trash is the undo for a wrong-UID delete, and the copy is confirmed before anything is flagged, so a restage cannot destroy a draft it should have kept. Write a `uid / to / subject` manifest to disk as well.
- `os.system('source .../mailer.env')` does not export into Python's environment (os.system spawns sh, and the vars die with it); read the env file directly or source it in the shell before launching Python.
- Try `PHANTOMBYTE_SMTP_PASS` for the IMAP login first, and fall back to the mail password in the profile-extension `ionos-email-access.md` reference only if it is refused. Read the reference or the env file directly; never type a password into a script that is written to disk.
- Pass `ssl_context=ssl.create_default_context()` to `IMAP4_SSL`; the bare positional certfile/keyfile args raise ValueError in current Python.
- Staging drafts is NOT a send and does not consume the daily cap or write `outreach_log.csv`; the cap and the log are only touched by an actual `--send`, which stays manual. The `state.json` mark in step 4 is the one thing staging DOES write, and it writes it every time, because the mark is what stops a staged prospect from being staged or sent twice.
