#!/usr/bin/env python3
"""Deterministic check block for a Ghostwriter Terminal draft.

Runs every gate the Send-First Fix-Later checklist requires in one pass, so a
future session does not hand-write the same python block again.

Usage:
    python3 check_draft.py <draft.txt> [body_word_lo] [body_word_hi]

body_word_lo/hi is the outline's ESTIMATED LENGTH band for the article body
(everything up to the SOURCES line). Omit it if the outline gave no band.

Prints PASS/FAIL for: em-dash and en-dash count, body word count against the
band, presence of the SOURCES / X POST / PINTEREST TITLE / PINTEREST
DESCRIPTION / QUICK KEYWORDS labels, X post length (<=280), Pinterest title
length (60-80), Pinterest description length (150-300), stray markdown
markers. Exit code is 0 only when every check passes.
"""
import sys


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    band = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) >= 4 else None
    t = open(path, encoding="utf-8").read()
    lines = t.split("\n")

    def label_index(name):
        for i, l in enumerate(lines):
            if l.strip() == name:
                return i
        return None

    ok = True
    print("file:", path)

    em, en = t.count("\u2014"), t.count("\u2013")
    good = (em == 0 and en == 0)
    print(f"em-dash: {em}  en-dash: {en}  {'PASS' if good else 'FAIL'}")
    ok &= good

    si = label_index("SOURCES")
    body = "\n".join(lines[:si]) if si is not None else t
    bw = len(body.split())
    if band:
        good = band[0] <= bw <= band[1]
        print(f"body words (to SOURCES): {bw}  band {band[0]}-{band[1]}  {'PASS' if good else 'FAIL'}")
        ok &= good
    else:
        print(f"body words (to SOURCES): {bw}  (no band given)")

    for name in ["SOURCES", "X POST", "PINTEREST TITLE", "PINTEREST DESCRIPTION", "QUICK KEYWORDS"]:
        present = name in t
        print(f"label {name}: {'OK' if present else 'MISSING'}")
        ok &= present

    xi, pt_i = label_index("X POST"), label_index("PINTEREST TITLE")
    di, ki = label_index("PINTEREST DESCRIPTION"), label_index("QUICK KEYWORDS")

    if xi is not None and pt_i is not None:
        x = "\n".join(lines[xi + 1:pt_i]).strip()
        good = len(x) <= 280
        print(f"X post length: {len(x)} (<=280)  {'PASS' if good else 'FAIL'}")
        ok &= good
    if pt_i is not None and di is not None:
        pt = "\n".join([l for l in lines[pt_i + 1:di] if l.strip()]).strip()
        good = 60 <= len(pt) <= 80
        print(f"Pinterest title length: {len(pt)} (60-80)  {'PASS' if good else 'FAIL'}")
        ok &= good
    if di is not None and ki is not None:
        pd = "\n".join([l for l in lines[di + 1:ki] if l.strip()]).strip()
        good = 150 <= len(pd) <= 300
        print(f"Pinterest description length: {len(pd)} (150-300)  {'PASS' if good else 'FAIL'}")
        ok &= good

    print(f"longest line: {max((len(l) for l in lines), default=0)}")
    md = t.count("##") + t.count("**") + t.count("---")
    print(f"markdown markers (##/**/---): {md}  {'PASS' if md == 0 else 'FAIL'}")
    ok &= (md == 0)

    print("RESULT:", "ALL CHECKS PASS" if ok else "CHECKS FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
