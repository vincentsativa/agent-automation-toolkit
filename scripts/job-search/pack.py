"""Stage 4: squeeze verified candidates into compact packs for the model to judge.

Usage:
    python pack.py [--date YYYY-MM-DD] [--size 40]

Cheap by design: one line per candidate plus a short description slice, so a
couple of hundred candidates can be judged without hauling raw JSON into context.
Writes packs/pack-NN.md and prints the paths.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

SNIPPET = 220


def money(value):
    return "" if value is None else "$%s" % C._fmt(round(value))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--size", type=int)
    ap.add_argument("--verdicts", default="live")
    args = ap.parse_args()

    params = C.config("params.json")
    out_dir = C.run_dir(args.date)
    rows = C.load_jsonl(os.path.join(out_dir, "verified.jsonl"))
    wanted = set(v.strip() for v in args.verdicts.split(","))
    rows = [r for r in rows if r["verify"]["verdict"] in wanted]
    if not rows:
        print("no candidates to pack")
        return

    size = args.size or int(params.get("pack_size", 40))
    pack_dir = os.path.join(out_dir, "packs")
    os.makedirs(pack_dir, exist_ok=True)
    for old in os.listdir(pack_dir):
        os.remove(os.path.join(pack_dir, old))

    index_lines = []
    for pack_no, start in enumerate(range(0, len(rows), size), start=1):
        chunk = rows[start:start + size]
        path = os.path.join(pack_dir, "pack-%02d.md" % pack_no)
        lines = ["PACK %d: %d candidates" % (pack_no, len(chunk)), ""]
        for offset, row in enumerate(chunk):
            idx = start + offset + 1
            pay = row.get("pay_raw") or "not stated"
            monthly = ""
            if row.get("monthly_low") is not None:
                monthly = " | monthly %s-%s" % (money(row["monthly_low"]), money(row["monthly_high"]))
            age = row.get("age_days")
            age_txt = "age unknown" if age is None else "%.0f days old" % age
            head = "[%03d] %s | %s | %s | %s | type=%s" % (
                idx, (row.get("title") or "")[:90], (row.get("company") or "")[:40],
                " ".join(pay.split())[:70], age_txt,
                (row.get("employment_type") or "n/a")[:30])
            if row.get("location"):
                head += " | %s" % row["location"][:40]
            head += " | src=%s | check=%s%s" % (
                row.get("source"), row["verify"]["verdict"], monthly)
            lines.append(head)
            lines.append("      url: %s" % row.get("url"))
            if row.get("apply_url"):
                lines.append("      apply: %s" % row["apply_url"])
            if row.get("apply_email"):
                lines.append("      apply email: %s" % row["apply_email"])
            if not C.has_direct_apply(row):
                lines.append("      apply: NONE, board page only, not shipable")
            snippet = " ".join(row.get("description", "").split())[:SNIPPET]
            if snippet:
                lines.append("      about: %s" % snippet)
            lines.append("")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        index_lines.append("pack-%02d.md  %d candidates  (indexes %d-%d)" % (
            pack_no, len(chunk), start + 1, start + len(chunk)))

    with open(os.path.join(out_dir, "INDEX.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join([out_dir] + index_lines) + "\n")
    print("packed %d candidates into %d packs" % (len(rows), len(index_lines)))
    for line in index_lines:
        print(" ", line)
    print("->", pack_dir)


if __name__ == "__main__":
    main()
