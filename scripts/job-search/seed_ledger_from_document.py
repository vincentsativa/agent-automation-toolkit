"""Seed the cross-day ledger from a job list delivered outside report.py.

A hand-built list, an alternate document, or an emailed attachment never passes
through report.py, so nothing records it and the next run hands the same roles
straight back. This script parses such a document and appends one ledger entry
per lead, with the day it shipped, so prefilter holds them by company and role.

Usage:
    python seed_ledger_from_document.py <document> --date YYYY-MM-DD [--ledger PATH]
    python seed_ledger_from_document.py <document> --date YYYY-MM-DD --dry-run

Expected shape, tolerant of the variations the job reports use:

    1. Company Name - Job Title
    Pay: $65-95/hr, flex/project-based
    Apply: https://employer.example/apply

Numbered headings without a following Pay/Apply block are skipped, and inline
headings like "1. Company - Title: $65-95/hr, flex" keep only the title part.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def parse(path):
    rows = []
    current = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().split("\n")
    for line in lines:
        stripped = line.strip()
        heading = re.match(r"(\d{1,2})\.\s+(.+?)\s+-\s+(.+)$", stripped)
        if heading and not stripped.lower().startswith(("pay:", "apply:")):
            if current:
                rows.append(current)
            company = heading.group(2).strip()
            title = heading.group(3).strip()
            title = re.split(r":\s*\$", title)[0].strip()
            current = {"company": company, "title": title, "pay_raw": "", "apply_url": ""}
            continue
        if current is None:
            continue
        if stripped.lower().startswith("pay:"):
            current["pay_raw"] = stripped.split(":", 1)[1].strip()
        elif stripped.lower().startswith("apply"):
            current["apply_url"] = stripped.split(":", 1)[1].strip()
    if current:
        rows.append(current)
    keep = []
    for row in rows:
        if not row["company"] or not row["title"]:
            continue
        row["key"] = C.lead_key(row)
        row["url"] = row.get("apply_url") or "doc://%s/%s" % (slug(os.path.basename(path)), slug(row["company"] + " " + row["title"]))
        row["source"] = "seed-" + slug(os.path.basename(path))
        keep.append(row)
    return keep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("document")
    ap.add_argument("--date", required=True, help="the day the list shipped, YYYY-MM-DD")
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = parse(args.document)
    print("parsed %d leads from %s" % (len(rows), args.document))
    for row in rows:
        print("  %s | %s | %s" % (row["company"], row["title"], row.get("pay_raw") or ""))
    if args.dry_run:
        print(json.dumps([{k: r[k] for k in ("company", "title", "key", "url")} for r in rows], indent=1))
        return 0
    added = C.ledger_append(rows, reported_on=args.date, path=args.ledger)
    stored = {r.get("key"): r.get("reported_on") for r in C.load_ledger(args.ledger)}
    missing = [r["key"] for r in rows if stored.get(r["key"]) != args.date]
    print("appended %d entries for %s" % (added, args.date))
    if missing:
        print("NOT held after seed (check these): %s" % ", ".join(missing[:10]))
        return 1
    print("verified: every seeded key is stored on %s and will be held from the next day" % args.date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
