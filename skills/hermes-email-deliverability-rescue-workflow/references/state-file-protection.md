# Protecting the contact history (state.json)

`~/money_ideas/state.json` is the campaign's spam guard. It records every domain already scheduled or contacted and is what dedupes each new build against prior sends. Losing it means writing to people who already received an email, which is the one failure this pipeline exists to prevent. Treat any operation that can touch it as a high-risk operation.

## Rule: state.json is unreachable from the test suite (fixed 2026-09-27)

`test_outreach.py` used to resolve its state file to the PRODUCTION path at four sites (`state_file = os.path.join(HERE, "state.json")`), each with `os.remove(state_file)` in the matching `finally` block, and the `outreach.py` CLI it drives as a subprocess saves state on every run including a dry run. A single PASSING run therefore overwrote and then deleted the production history. Only the dedupe test redirected to a temp directory.

The fix, and the rule to keep: every path the suite touches comes from a per-run `tempfile.mkdtemp()` directory, and `outreach.py` reads its three file paths from the environment so the suite can redirect the subprocess too.

- `outreach.py`: `STATE_FILE`, `LOG_FILE`, and `STOP_FILE` each read `OUTREACH_STATE_FILE`, `OUTREACH_LOG_FILE`, `OUTREACH_STOP_FILE` first and fall back to the production name. A production run sets nothing and gets the real files, so this is safe to leave in place permanently.
- `test_outreach.py`: one `RUN_TMP = tempfile.mkdtemp(prefix="outreach_suite_")` at import, `TEST_STATE`/`TEST_LOG`/`TEST_STOP` built from it, the module-level `outreach.STATE_FILE` and friends reassigned to them, and `run_cli()` injecting all three into the subprocess env.

A test module's state path must point at a per-run temp directory, never at a production filename. When a test in this folder destroys real state, that is the defect to fix, and it is fixed in the test, not by remembering to be careful next time.

Prove the fix rather than reading it. Hash the production file, run the full suite to a pass, hash it again, and require the two to match:

```bash
cd ~/money_ideas
sha256sum state.json
set -a; . ~/.config/phantombyte/mailer.env; set +a
~/.venv/bin/python test_outreach.py; echo "---EXIT:$?---"
sha256sum state.json
```

Measured 2026-09-27: 133 passed, 0 failed, and `state.json` byte-identical before and after (`1be35799e034db332f1210316aa2ca77192da4cda4a3314fa3e43d7a2d07b74f`). The suite runs against live DNS, so it needs the mailer env sourced, or the postal-address and SMTP-pass refusal checks fail spuriously.

Grep for the pattern before trusting any script in this folder with the production file:

```bash
rg -n 'os\.remove|os\.unlink|shutil\.rmtree' ~/money_ideas/*.py
```

## Rebuilding after a wipe: IMAP is the source of truth

The scheduled sends exist on the mail host independently of the local file, so a wiped history is recoverable, and recovering it is not the same as having never lost it. Connect to `imap.ionos.com:993`; the `Scheduled` folder holds one message per scheduled prospect carrying its own `X-OX-Date-To-Send` header, and `Sent Items` holds the ones already sent. Rebuild `state.json` in the exact field shape `schedule_drafts.py` writes, one row per contacted domain:

```json
{"contacted": {"<domain>": {"email": "...", "status": "scheduled", "scheduled_at": "...", "scheduled_local": "...", "folder": "Scheduled"}}, "sent_today": {}, "log": []}
```

## Prove the rebuild by reading it back

A rebuild that wrote N rows proves nothing until the pipeline's own loader parses it. `outreach.py` imports `find_contacts`, which imports `requests`, so the read-back must run under an interpreter that carries the project dependencies (`~/.venv`) rather than a bare `python3`:

```bash
~/.venv/bin/python -c "import outreach; st = outreach.load_state(); print(len(st.get('contacted', {})))"
```

Report the read-back result as the proof or not at all. "The file was written with 100 rows" is a claim about a write; only the loader output is a claim about the pipeline.

## What to tell Vinny

Name the wipe, the cause, and the recovery separately and in that order. A dedupe result computed while the history was still intact stays valid even after a later wipe, so say so rather than re-deriving a number that was never in doubt. Then name the still-broken thing explicitly if it has not been fixed, because an unfixed self-deleting test is a future incident, not a closed one.

A recovery from IMAP is not a restoration. It restores only what still sits in the mail host's folders, so the rebuilt history is routinely SHORTER than the one that was lost, and the missing rows are previously contacted prospects who are now unblocked. Never report a rebuild as "the history is back" without measuring the gap against the newest backup that still has rows. The audit procedure and the `sent`-row trap are in `references/history-reconciliation.md`.
