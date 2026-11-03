#!/usr/bin/env python3
"""Measure candidate X posts against a hard character cap.

Usage:
    python3 fit_x_char_cap.py TARGET URL CANDIDATE.txt [CANDIDATE2.txt ...]
    python3 fit_x_char_cap.py TARGET URL --text "full post text"

Prints for each candidate: body length, body+space+url length, and
OK / OVER / SHORT with the exact delta to the target. Also reports the
count X itself shows (a raw URL is wrapped to 23 chars by t.co).

Why this exists: subtracting character counts by eye while editing is
wrong several times in a row. Never trust an estimated delta; paste the
candidate and read the printed number.
"""
import sys
import os


def measure(body, url, target):
    total = len(body) + 1 + len(url)
    x_total = len(body) + 1 + 23  # t.co wraps any URL to 23 chars
    delta = total - target
    if delta > 0:
        status = f"OVER by {delta}"
    elif delta < 0:
        status = f"SHORT by {-delta}"
    else:
        status = "OK exact"
    return total, x_total, status


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    target = int(argv[1])
    url = argv[2]
    rest = argv[3:]

    items = []
    if rest[0] == "--text":
        items = [("<inline>", " ".join(rest[1:]))]
    else:
        for path in rest:
            with open(path, "r", encoding="utf-8") as fh:
                items.append((os.path.basename(path), fh.read().rstrip("\n")))

    worst = 0
    print(f"target={target}  url_len={len(url)}")
    for name, body in items:
        total, x_total, status = measure(body, url, target)
        if total > target:
            worst = 1
        print(f"{name}: body={len(body)} total={total} x_counts={x_total} -> {status}")
    print("NOTE: report total (body + 1 space + raw url) unless the user said to count the t.co form.")
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv))
