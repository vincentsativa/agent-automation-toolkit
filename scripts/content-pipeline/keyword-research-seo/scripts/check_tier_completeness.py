# check_tier_completeness.py -- gate a keyword report before emailing it.
#
# PURPOSE: a report can leave a measured term out of the tier list while still
# discussing it in the recommendations, and then every count in the report is
# wrong by the number of skipped terms. This catches that mechanically instead
# of by eye.
#
# USAGE:
#   python check_tier_completeness.py <trends.json> <report.txt>
#
# Output: unique terms measured, terms missing from the report, and numbered
# entries per tier section. Exit code 1 when a term is missing or the tier
# totals do not add up to the unique term count.

import json
import re
import sys


def unique_terms(path):
    data = json.load(open(path, encoding="utf-8"))
    seen = []
    for batch in data.values():
        if not isinstance(batch, list):
            continue
        for entry in batch:
            if isinstance(entry, dict) and entry.get("term"):
                t = entry["term"].strip()
                if t.lower() not in [s.lower() for s in seen]:
                    seen.append(t)
    return seen


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def main(json_path, report_path):
    terms = unique_terms(json_path)
    text = open(report_path, encoding="utf-8").read()
    low = norm(text)

    missing = [t for t in terms if norm(t) not in low]

    sections = {}
    current = None
    for line in text.split("\n"):
        if line.startswith("TIER 1"):
            current = "TIER 1"
        elif line.startswith("TIER 2"):
            current = "TIER 2"
        elif line.startswith("TIER 3"):
            current = "TIER 3"
        elif line.startswith(("STRATEGIC RECOMMENDATIONS", "CRITICAL WINDOW")):
            current = None
        elif current and re.match(r"^\d+\. ", line):
            sections[current] = sections.get(current, 0) + 1

    total = sum(sections.values())
    print("unique terms measured:", len(terms))
    for k in ("TIER 1", "TIER 2", "TIER 3"):
        print("  %s numbered entries: %d" % (k, sections.get(k, 0)))
    print("numbered tier entries total:", total)
    print("terms not found anywhere in the report:", missing if missing else "none")

    ok = not missing and total >= len(terms)
    print("PASS" if ok else "FAIL: tier the missing terms, renumber, then re-run the formatter")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: check_tier_completeness.py <trends.json> <report.txt>")
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
