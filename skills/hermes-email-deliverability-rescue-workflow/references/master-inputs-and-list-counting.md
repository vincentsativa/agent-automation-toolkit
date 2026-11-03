# The merged master inputs and counting the send list

## scan_master.csv and contacts_master.csv are the full-pipeline inputs

`scan_master.csv` is every scan result CSV concatenated and deduped by domain (first file wins on collision): email_scan_results, scan_1000_industry_results, scan_2000_industry_results, scan_2000_b3_results, ny500_scan_results, orlando_scan_results, orlando_300_results. `contacts_master.csv` is every contact list merged into the loader's `domain,email,person` format, first address per domain wins: contacts.csv, send_ready_1000_emails, send_ready_2000_final_emails, ny500_sendlist, orlando_osm_emails, osm_emails_tampa.

The full-pipeline command is `python3 outreach.py --csv scan_master.csv --emails contacts_master.csv --offer-url URL`. The original Tampa-only pair (email_scan_results + contacts.csv) still works as a subset. When a new scan or contact list lands, REGENERATE the masters from the per-list files rather than hand-adding rows, so the merge stays reproducible.

## Count the send list from a dry run, never from file arithmetic

Never answer "how many addresses do we have" by summing per-list files or quoting a remembered count. Three traps make file arithmetic wrong:

- **Per-list files overlap heavily.** The 1000-batch is mostly inside the 2000-batch (247 of 305 shared). Sum the files and you double-count.
- **A list's backing scan file may not be the obvious one.** The orlando OSM emails are qualified by `orlando_scan_results.csv` (the full 1,283-domain scan), not by `orlando_300_results.csv`; checking the wrong file understates the pool. Before asserting "no qualified scan backs this list," check EVERY scan CSV on disk.
- **Only the gated count means anything.** An address is sendable only if it passes the qualified-scan gate, the stop list, the fit filter, the dedupe, and has an actual address. Raw list lengths include rows the pipeline would refuse.

Run the dry run against the masters and read `Dry run complete: N messages composed` plus the tier breakdown out of the actual output; that number is the answer. A hand-summed figure that disagrees with the dry run is wrong, and a previously delivered hand-summed number must be explicitly corrected (a first estimate was low by ~20% for exactly these reasons).

## A superseded send_ready file can hold MORE rows than the final, and still feed sends

`send_ready_<tag>.csv` and `send_ready_<tag>_final.csv` are not interchangeable. The `_final` file is the post-assembly, post-fit, deduped list. The un-suffixed file is the earlier pass, and it is frequently LARGER because the fit filter and dedupe have not run yet, so it carries rows the final deliberately dropped. The same applies to the batch-2 pair: `send_ready_2000.csv` holds 597 against `send_ready_2000_final.csv`'s 547.

The trap: a scheduled or loaded batch picks addresses from the superseded file, so some of the sends in flight are NOT members of any counted batch, and a running total built only from the `_final` files silently undercounts what has actually been loaded. When you reconcile loaded against ready, intersect the loaded set against EVERY `send_ready*.csv` on disk, not just the finals, and report the addresses that match no batch at all as their own line.

Before quoting or acting on any `send_ready` file, list the family: `search_files` for `send_ready*` and prefer the `_final` variant for the file's own batch. Never sum a superseded file together with its own final.

## Verify the master merge before trusting it

All scan CSVs from this pipeline share one header; hash-compare `head -1` of each before concatenating. After merging, spot-check drafts from more than one source list (one ny500 row, one orlando row) with `--drafts DIR`, not just the first file in the merge, so a formatting mismatch in a later list cannot hide behind the first list's success.

## Run the test suite and dry runs on the system interpreter

`test_outreach.py` needs the pipeline's `requests` install and the mailer env. Use `/usr/bin/python3` (the Hermes-bundled python3 on PATH is a different version without the pipeline's packages) and source the env first: `set -a; . ~/.config/phantombyte/mailer.env; set +a`, or the postal-address and SMTP-pass refusal tests fail spuriously and the failure looks like a code regression when it is environment.
