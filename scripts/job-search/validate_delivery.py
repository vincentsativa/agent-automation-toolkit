"""Refuse delivery when a report does not describe the final verified pool."""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    args = ap.parse_args()

    out_dir = C.run_dir(args.date)
    stamp = args.date or C.today_stamp()
    report = os.path.join(out_dir, "report-%s.txt" % stamp)
    selected = os.path.join(out_dir, "selected.json")
    verified = os.path.join(out_dir, "verified.jsonl")
    missing = [path for path in (report, selected, verified) if not os.path.isfile(path)]
    if missing:
        raise SystemExit("delivery gate: missing " + ", ".join(missing))

    report_time = os.path.getmtime(report)
    stale = [path for path in (selected, verified) if os.path.getmtime(path) > report_time]
    if stale:
        raise SystemExit(
            "delivery gate: report is stale; rebuild selected.json and re-render after "
            + ", ".join(stale)
        )
    print("delivery gate passed: report matches the final selected and verified inputs")


if __name__ == "__main__":
    main()
