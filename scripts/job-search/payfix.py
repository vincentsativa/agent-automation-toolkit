"""Stage 3b: re-open live leads that carry no pay figure and pull the salary line
straight from the employer's page, then write it back into verified.jsonl.

Usage:
    python payfix.py [--date YYYY-MM-DD] [--limit 30]

Pay is a hard part of the verification bar, so a lead that is live but silent on
pay gets one more targeted look before the report calls it unstated.
"""

import argparse
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

CONTEXT_RE = re.compile(
    r"(?i)[^\n]{0,120}(?:salary|compensation|pay range|hourly rate|per hour|per annum|"
    r"base pay|starting salary|budget|rate)[^\n]{0,160}")


def probe(url, timeout=25):
    status, final_url, body = C.fetch(url, timeout=timeout)
    if status in (0, 401, 403, 429):
        alt = C.scrapling_fetch(url, timeout=timeout)
        if alt and alt[0] and alt[0] < 400:
            status, final_url, body = alt
    if status >= 400 or not body:
        return None, "no fetch (HTTP %s)" % status
    text = C.strip_html(body)
    lines = [" ".join(m.group(0).split()) for m in CONTEXT_RE.finditer(text)]
    pay = C.find_pay_in_page(text) or C.find_pay_in_jsonld(body)
    if not pay:
        return None, "page fetched, no pay statement found"
    return pay, (lines[0][:180] if lines else pay["raw"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--limit", type=int, default=30)
    args = ap.parse_args()

    out_dir = C.run_dir(args.date)
    path = os.path.join(out_dir, "verified.jsonl")
    rows = C.load_jsonl(path)
    changed = 0
    for row in rows:
        if row["verify"]["verdict"] != "live" or row.get("pay"):
            continue
        if changed >= args.limit:
            break
        pay, evidence = probe(row.get("apply_url") or row["url"])
        changed += 1
        if pay:
            row["pay"] = pay
            row["pay_raw"] = pay["raw"]
            row["pay_source"] = "employer page (payfix)"
            monthly = C.monthly_estimate(pay, row.get("hours_per_week") or 40)
            if monthly:
                row["monthly_low"], row["monthly_high"], row["pay_formula"] = monthly
            print("  + %-52s %s" % (row["title"][:52], pay["raw"][:40]))
        else:
            print("  - %-52s %s" % (row["title"][:52], evidence[:60]))
        time.sleep(0.3)
    C.write_jsonl(path, rows)
    print("probed %d rows, %s" % (changed, path))


if __name__ == "__main__":
    main()
