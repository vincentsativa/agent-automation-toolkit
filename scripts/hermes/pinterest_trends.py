#!/usr/bin/env python3
"""Pinterest public trends reader for the daily Pinterest cron.

Uses Pinterest's own public trend endpoints (no login, no cookies):
  /latest_available_date/      -> last date with data
  /top_trends_filtered/        -> ranked trend lists (presets 1-4)
  /metrics/                    -> search-volume series + growth for exact terms

Usage:
  python3 pinterest_trends.py
  python3 pinterest_trends.py --terms "ai agents,humanoid robot,cybersecurity"
  python3 pinterest_trends.py --terms-file /path/terms.txt
  python3 pinterest_trends.py --country US --days 90

Exit codes: 0 ok, 2 fetch failure (message on stderr).
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://trends.pinterest.com/",
}
BASE = "https://trends.pinterest.com"

PRESET_LABELS = {
    1: "SEASONAL / UPCOMING",
    2: "POPULAR (evergreen)",
    3: "BREAKOUT (fastest growing)",
    4: "TRENDING SEARCHES (full list)",
}


def fetch(url, tries=3):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8", "ignore"))
        except Exception as exc:  # noqa: BLE001
            last = exc
    raise RuntimeError(f"fetch failed: {url} ({last})")


def latest_date():
    d = fetch(f"{BASE}/latest_available_date/")
    return d.get("date")


def top_trends(end_date, country, preset, n=20):
    url = (
        f"{BASE}/top_trends_filtered/?lookbackWindow=2&endDate={end_date}"
        f"&rankingMethod=3&country={country}&trendsPreset={preset}&numTermsToReturn={n}"
    )
    return fetch(url).get("values", [])


def pct(v):
    if v is None:
        return "n/a"
    return f"{v:+.0f}%"


def metrics(terms, end_date, country, days):
    terms = [t.strip() for t in terms if t.strip()]
    if not terms:
        return []
    url = (
        f"{BASE}/metrics/?terms={urllib.parse.quote(','.join(terms), safe=',')}"
        f"&country={country}&end_date={end_date}&days={days}&aggregation=2"
        f"&normalize_against_group=false&predicted_days=0"
    )
    return fetch(url)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", default="")
    ap.add_argument("--terms-file", default="")
    ap.add_argument("--country", default="US")
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--lists", type=int, default=10, help="terms per trend list")
    ap.add_argument("--top", type=int, default=20, help="terms ranked per metrics query")
    args = ap.parse_args()

    try:
        end = latest_date()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"PINTEREST TRENDS - country {args.country} - data through {end}")

    terms = []
    if args.terms_file:
        try:
            with open(args.terms_file, encoding="utf-8") as fh:
                terms += [ln.strip() for ln in fh if ln.strip()]
        except OSError as exc:
            print(f"WARN: cannot read terms file: {exc}", file=sys.stderr)
    if args.terms:
        terms += [t.strip() for t in args.terms.split(",")]

    # Story keyword demand: only terms Pinterest has data for come back.
    rows = []
    for i in range(0, len(terms), 20):
        try:
            rows += metrics(terms[i:i + 20], end, args.country, args.days)
        except RuntimeError as exc:
            print(f"WARN: metrics failed: {exc}", file=sys.stderr)

    if terms:
        print("\n--- KEYWORD DEMAND (%d-day series, Pinterest search volume) ---" % args.days)
        if not rows:
            print("No candidate keyword has measurable Pinterest search volume right now.")
            print("Treat that as no demand signal, not as permission to invent a trend.")
        else:
            rows.sort(key=lambda r: r["counts"][-1]["count"] if r.get("counts") else 0, reverse=True)
            for r in rows:
                c = r.get("counts") or []
                if not c:
                    continue
                first, last = c[0]["count"], c[-1]["count"]
                change = ((last - first) / first * 100) if first else 0.0
                g = r.get("growth_rates") or {}
                direction = "RISING" if change >= 10 else ("FALLING" if change <= -10 else "FLAT")
                print(
                    f"{r['term']}: {last} searches/wk, {direction} {change:+.0f}% over {args.days}d "
                    f"(WoW {pct(g.get('wow_change'))}, MoM {pct(g.get('mom_change'))}, "
                    f"YoY {pct(g.get('yoy_change'))})"
                )
        missing = [t for t in terms if t.lower() not in {r["term"].lower() for r in rows}]
        if missing:
            print("No Pinterest volume data for: " + ", ".join(missing[:30]))

    for preset in (1, 2, 3, 4):
        try:
            vals = top_trends(end, args.country, preset, args.top)
        except RuntimeError as exc:
            print(f"WARN: list {preset} failed: {exc}", file=sys.stderr)
            continue
        label = PRESET_LABELS.get(preset, f"LIST {preset}")
        print(f"\n--- {label} ---")
        for v in vals[: args.lists]:
            mom = ((v.get("mom_change") or {}).get("value"))
            wow = ((v.get("wow_change") or {}).get("value"))
            bits = []
            if mom:
                bits.append(f"MoM {'10,000%+' if mom * 100 >= 10000 else f'{mom * 100:+.0f}%'}")
            if wow:
                bits.append(f"WoW {'10,000%+' if wow * 100 >= 10000 else f'{wow * 100:+.0f}%'}")
            print(f"{v.get('term')}: {v.get('searchCount', 0)} searches/wk" + (", " + ", ".join(bits) if bits else ""))

    print("\nRule: a trend may only shape the wording or the story choice. Never attach a trend to a story it does not actually describe.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
