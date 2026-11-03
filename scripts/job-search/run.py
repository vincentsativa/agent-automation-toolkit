"""One command for the whole scripted side of the pipeline.

Usage:
    python run.py [--date YYYY-MM-DD] [--only remoteok,wwr] [--skip collect,prefilter,verify,pack]

Runs collect -> prefilter -> verify -> pack, then prints the counts and the pack
paths. It stops there on purpose: the judgment step (picking the leads and writing
selected.json) is the model's, and the send step belongs to the email-sender skill.
"""

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402


def run_step(script, extra):
    cmd = [sys.executable, os.path.join(HERE, script)] + extra
    print("\n=== %s ===" % script)
    result = subprocess.run(cmd, cwd=HERE)
    if result.returncode != 0:
        raise SystemExit("%s failed with exit code %d" % (script, result.returncode))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--only")
    ap.add_argument("--skip", default="")
    args = ap.parse_args()

    skip = {s.strip() for s in args.skip.split(",") if s.strip()}
    date_args = ["--date", args.date] if args.date else []

    if "collect" not in skip:
        run_step("collect.py", date_args + (["--only", args.only] if args.only else []))
    if "prefilter" not in skip:
        run_step("prefilter.py", date_args)
    if "resolve" not in skip:
        run_step("resolve_employer.py", date_args)
    if "verify" not in skip:
        run_step("verify.py", date_args)
    # Pay is recovered only after an employer page has been verified live.
    # Without this stage, direct-employer roles whose feed omitted pay are
    # treated as unrated and can occupy only the small no-pay allowance.
    if "payfix" not in skip:
        run_step("payfix.py", date_args + ["--limit", "100"])
    if "pack" not in skip:
        run_step("pack.py", date_args)
    # A deterministic baseline selection, written only when the model has not
    # written one yet. On October 21, 2026 the pool held the right job families
    # and the hand-picked list came back as four salaried roles; this makes the
    # rules the default and the model's judgment an improvement on it, not a
    # replacement for it. Existing selected.json is never overwritten here.
    if "select" not in skip:
        selected_path = os.path.join(C.run_dir(args.date), "selected.json")
        if os.path.exists(selected_path):
            print("\n=== select.py ===\nselected.json already exists, left untouched")
        else:
            run_step("select.py", date_args)
    # The count is the deliverable. A pass that lands under target because one
    # collection was too narrow is fixable without a human: widen the two in-band
    # sources, re-filter, re-verify, re-select. On October 22, 2026 the first pass
    # left the pool one short at twelve in-band roles and the list shipped at
    # nineteen, which is the failure this stage exists to prevent. It never relaxes
    # a cap; if supply is genuinely short it says so and the report states the
    # arithmetic.
    if "select" not in skip and "topup" not in skip:
        run_step("topup.py", date_args)

    out_dir = C.run_dir(args.date)
    print("\nrun dir: %s" % out_dir)
    held_urls, held_keys, _when = C.ledger_held(args.ledger if hasattr(args, "ledger") else None,
                                               today=args.date or C.today_stamp())
    print("  ledger holds %d urls and %d company+role keys from earlier days" % (
        len(held_urls), len(held_keys)))
    for name in ("raw.jsonl", "candidates.jsonl", "dropped.jsonl", "verified.jsonl", "INDEX.md"):
        path = os.path.join(out_dir, name)
        if os.path.exists(path):
            count = sum(1 for _ in open(path, encoding="utf-8"))
            print("  %-18s %d lines" % (name, count))
    print("\nnext: read the packs, write selected.json, then report.py, then email via the email-sender skill")


if __name__ == "__main__":
    main()
