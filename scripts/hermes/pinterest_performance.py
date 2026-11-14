#!/usr/bin/env python3
"""Pinterest performance engine for the PhantomByteAI account.

Reads a Pinterest Analytics CSV export, computes per-board RATES (not totals),
derives a 10-slot daily topic allocation, and writes a state ledger that the
daily Pinterest posts cron reads before choosing topics.

Stdlib only: cron launches helper scripts with the gateway's own interpreter.

Modes
  (no args)        full human report + refresh the state ledger
  --brief          compact block for the daily cron (allocation + rules)
  --refresh        same as no args, but also enriches top pins with board data
  --enrich N       how many top pins to enrich (default 12, 0 disables)
  --csv PATH       use a specific export instead of the newest one found
  --no-write       print only, leave the ledger untouched
  --override PATH  apply a validated allocation override before reporting

Exit codes: 0 ok, 2 no analytics export found or unreadable.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

HOME = os.path.expanduser("~")
STATE_DIR = os.path.join(HOME, ".hermes", "state")
LEDGER = os.path.join(STATE_DIR, "pinterest_performance.json")
SNAPSHOTS = os.path.join(STATE_DIR, "pinterest_snapshots")
OVERRIDE = os.path.join(STATE_DIR, "pinterest_allocation.json")
SEARCH_DIRS = [
    ".../<user>/Downloads",
    os.path.join(HOME, "Downloads"),
    os.path.join(HOME, "Desktop"),
]
UA = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"
}

SLOTS = 10

# Board slug -> (short key, band min, band max)
BOARDS = {
    "ai-news-machine-learning-emerging-tech": ("news", 2, 4),
    "ai-for-developers-programming-ai-tutorials": ("dev", 1, 3),
    "ai-tools-for-business-productivity-2026": ("tools", 1, 3),
    "ai-agents-automation-guide": ("agents", 1, 2),
    "robotics-physical-ai-humanoid-robots": ("robotics", 1, 3),
    "agent-security-prompt-injection-sandboxing": ("security", 0, 2),
    "quantum-computing-explained": ("quantum", 0, 1),
}
KEY_TO_SLUG = {v[0]: k for k, v in BOARDS.items()}

LABELS = {
    "news": "AI News | Machine Learning & Emerging Tech",
    "dev": "AI for Developers & Programming AI [Tutorials]",
    "tools": "AI Tools for Business & Productivity [2026]",
    "agents": "AI Agents & Automation [Guide]",
    "robotics": "Robotics & Physical AI [Humanoid Robots]",
    "security": "Agent Security: Prompt Injection & Sandboxing",
    "quantum": "Quantum Computing [Explained]",
}

ANGLE = {
    "news": "lead with the concrete number or change, then why it matters",
    "dev": "visual hook: code, terminal output, or architecture diagram; save reason: a snippet, command, or comparison the reader can use",
    "tools": "visual hook: product UI or 3-step workflow; save reason: a prompt, checklist, or pricing comparison",
    "agents": "architecture comparison, benchmark numbers, or a real deployment result; never a generic 'what is an agent'",
    "robotics": "hardware or deployment visual, spec numbers, real pilot or factory result",
    "security": "a specific attack path plus the specific control that stops it",
    "quantum": "ONLY a major, dated development; never an explainer",
}


def find_export(explicit=None):
    if explicit:
        return explicit if os.path.isfile(explicit) else None
    candidates = []
    for d in SEARCH_DIRS:
        if os.path.isdir(d):
            candidates += glob.glob(os.path.join(d, "Pinterest Analytics overview*.csv"))
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


def parse_export(path):
    with open(path, encoding="utf-8-sig", errors="ignore") as f:
        raw = f.read()
    lines = [ln.rstrip("\r\n") for ln in raw.splitlines()]

    def idx(prefix):
        for i, ln in enumerate(lines):
            if ln.strip().startswith(prefix):
                return i
        return -1

    def cells(line):
        out, cur, q = [], [], False
        for ch in line:
            if ch == '"':
                q = not q
            elif ch == "," and not q:
                out.append("".join(cur).strip())
                cur = []
            else:
                cur.append(ch)
        out.append("".join(cur).strip())
        return out

    def num(s):
        s = (s or "").replace(",", "").strip()
        try:
            return int(float(s))
        except ValueError:
            return 0

    export = {"path": path, "range": None, "daily": [], "boards": [], "pins": []}
    for ln in lines[:12]:
        if re.match(r"^\d{4}-\d{2}-\d{2} - \d{4}-\d{2}-\d{2}$", ln.strip()):
            export["range"] = ln.strip()
            break

    i = idx("Date,Impressions")
    if i < 0:
        raise ValueError("no daily impressions table in export")
    for ln in lines[i + 1:]:
        if not ln.strip():
            break
        c = cells(ln)
        if len(c) >= 2 and re.match(r"^\d{4}-\d{2}-\d{2}$", c[0]):
            export["daily"].append((c[0], num(c[1])))
        else:
            break

    i = idx("Pinterest Link,Impressions,Engagement")
    if i >= 0:
        for ln in lines[i + 1:]:
            if not ln.strip() or ln.strip().startswith('"Top boards table'):
                break
            c = cells(ln)
            if len(c) < 6 or not c[0].startswith("http"):
                break
            slug = ""
            m = re.search(r"pinterest\.com/[^/]+/([^/?#]+)/?", c[0])
            if m:
                slug = m.group(1)
            key = BOARDS.get(slug, (None, 0, 0))[0]
            export["boards"].append({
                "slug": slug,
                "key": key,
                "url": c[0],
                "impressions": num(c[1]),
                "engagement": num(c[2]),
                "pin_clicks": num(c[3]),
                "outbound_clicks": num(c[4]),
                "saves": num(c[5]),
            })

    i = idx("Pinterest Link,Content Type")
    if i >= 0:
        for ln in lines[i + 1:]:
            if not ln.strip() or ln.strip().startswith('"Top pins table'):
                break
            c = cells(ln)
            if len(c) < 5 or not c[0].startswith("http"):
                break
            pid = re.search(r"/pin/(\d+)", c[0])
            export["pins"].append({
                "url": c[0],
                "pin_id": pid.group(1) if pid else "",
                "content_type": c[1],
                "source": c[2],
                "canonical": c[3],
                "engagement": num(c[4]),
            })
    return export


def enrich_pin(pin):
    try:
        req = urllib.request.Request(pin["url"], headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read().decode("utf-8", "ignore")
    except Exception as exc:  # network fault is not a data fault
        pin["enrich_error"] = str(exc)[:120]
        return pin
    m = re.search(r'"board":\{"name":"((?:[^"\\]|\\.){2,160})","url":"/([^/"]+)/([^/"]+)/"', body)
    if m:
        try:
            pin["board_name"] = json.loads('"' + m.group(1) + '"')
        except Exception:
            pin["board_name"] = m.group(1)
        pin["board_profile"] = m.group(2)
        pin["board_slug"] = m.group(3)
        pin["board_key"] = BOARDS.get(m.group(3), (None, 0, 0))[0]
    t = re.search(r'"title":"((?:[^"\\]|\\.){5,220})"', body)
    if t:
        try:
            pin["title"] = json.loads('"' + t.group(1) + '"')
        except Exception:
            pass
    link = re.search(r'"link":"(https?://[^"]+)"', body)
    if link:
        pin["link"] = link.group(1)
    return pin


def weeks(daily):
    """Four weekly buckets, newest last, plus the flag on estimated tail days."""
    buckets = []
    for start in range(0, len(daily), 7):
        chunk = daily[start:start + 7]
        if len(chunk) < 4:
            continue
        buckets.append((chunk[0][0], chunk[-1][0], sum(v for _, v in chunk)))
    return buckets


def score_boards(export):
    rows = []
    for b in export["boards"]:
        if not b["key"]:
            continue
        imp = b["impressions"] or 1
        rows.append({
            **b,
            "engagement_rate": b["engagement"] / imp,
            "pin_click_rate": b["pin_clicks"] / imp,
            "outbound_rate": b["outbound_clicks"] / imp,
            "save_rate": b["saves"] / imp,
            "save_share_of_engagement": (b["saves"] / b["engagement"]) if b["engagement"] else 0.0,
        })
    if not rows:
        return rows
    max_imp = max(r["impressions"] for r in rows) or 1
    max_eng = max(r["engagement_rate"] for r in rows) or 1
    max_save = max(r["save_rate"] for r in rows) or 1
    for r in rows:
        r["priority"] = (
            0.5 * (r["impressions"] / max_imp)
            + 0.3 * (r["engagement_rate"] / max_eng)
            + 0.2 * (r["save_rate"] / max_save)
        )
    rows.sort(key=lambda r: -r["priority"])
    return rows


def compute_allocation(scored):
    """10 slots, proportional to the measured priority, clamped to each band.

    Quantum is held out of the proportional pool: its reach is too small to earn
    slots on rate alone and it converts nothing (0 outbound clicks in the window).
    """
    pool = [r for r in scored if r["key"] != "quantum"]
    total_w = sum(r["priority"] for r in pool) or 1
    alloc = {}
    for r in pool:
        key, lo, hi = r["key"], BOARDS[r["slug"]][1], BOARDS[r["slug"]][2]
        alloc[key] = max(lo, min(hi, round(r["priority"] / total_w * SLOTS)))
    alloc["quantum"] = 0
    keys_by_priority = [r["key"] for r in pool]
    # Trim, lowest priority first, never below a band floor.
    while sum(alloc.values()) > SLOTS:
        for key in reversed(keys_by_priority):
            lo = BOARDS[KEY_TO_SLUG[key]][1]
            if alloc[key] > lo:
                alloc[key] -= 1
                break
        else:
            break
    # Fill, highest priority first, never above a band ceiling.
    while sum(alloc.values()) < SLOTS:
        for key in keys_by_priority:
            hi = BOARDS[KEY_TO_SLUG[key]][2]
            if alloc[key] < hi:
                alloc[key] += 1
                break
        else:
            break
    return alloc


def validate_override(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    alloc = data.get("allocation") or data
    clean = {}
    for key, n in alloc.items():
        if key not in KEY_TO_SLUG:
            raise ValueError("unknown board key in override: %s" % key)
        lo, hi = BOARDS[KEY_TO_SLUG[key]][1], BOARDS[KEY_TO_SLUG[key]][2]
        n = int(n)
        if n < lo or n > hi:
            raise ValueError("%s=%s outside band %s-%s" % (key, n, lo, hi))
        clean[key] = n
    if sum(clean.values()) != SLOTS:
        raise ValueError("override totals %s slots, must be %s" % (sum(clean.values()), SLOTS))
    return clean, data.get("reason", ""), data.get("updated_at", "")


def build(export, enrich_n):
    scored = score_boards(export)
    alloc = compute_allocation(scored)
    if os.path.isfile(OVERRIDE):
        try:
            override, reason, updated = validate_override(OVERRIDE)
            alloc = override
            allocation_source = "override (%s): %s" % (updated, reason)
        except Exception as exc:
            allocation_source = "computed (override rejected: %s)" % exc
    else:
        allocation_source = "computed"

    pins = export["pins"]
    if enrich_n and pins:
        with ThreadPoolExecutor(max_workers=6) as ex:
            pins = list(ex.map(enrich_pin, pins[:enrich_n])) + pins[enrich_n:]

    return {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "export_path": export["path"],
        "export_range": export["range"],
        "weeks": weeks(export["daily"]),
        "boards": scored,
        "allocation": alloc,
        "allocation_source": allocation_source,
        "contingency": {
            "security": "1 slot may replace one news slot when a genuine security story exists",
            "quantum": "1 slot may replace one news slot ONLY on a major dated development, max once per week",
        },
        "top_pins": pins,
        "angles": ANGLE,
    }


def fmt_pct(x):
    return "%.2f%%" % (x * 100)


def report(ledger):
    out = []
    out.append("PINTEREST PERFORMANCE LEDGER")
    out.append("=" * 60)
    out.append("Export: %s" % ledger["export_range"])
    out.append("Source: %s" % ledger["export_path"])
    out.append("Built:  %s" % ledger["generated_at"])
    out.append("")
    out.append("WEEKLY IMPRESSIONS")
    out.append("-" * 60)
    for a, b, v in ledger["weeks"]:
        out.append("  %s to %s   %7d" % (a, b, v))
    out.append("")
    out.append("BOARD RATES (share of impressions, engagement, saves, outbound)")
    out.append("-" * 60)
    total_imp = sum(b["impressions"] for b in ledger["boards"]) or 1
    out.append("  %-9s %8s %7s %7s %7s %8s %7s" % (
        "board", "imps", "share", "engR", "pinClk", "saveR", "outR"))
    for b in ledger["boards"]:
        out.append("  %-9s %8d %6.1f%% %6s %6s %7s %6s" % (
            b["key"], b["impressions"], b["impressions"] / total_imp * 100,
            fmt_pct(b["engagement_rate"]), fmt_pct(b["pin_click_rate"]),
            fmt_pct(b["save_rate"]), fmt_pct(b["outbound_rate"])))
    out.append("")
    out.append("DAILY TOPIC ALLOCATION (10 posts, source: %s)" % ledger["allocation_source"])
    out.append("-" * 60)
    for key, n in sorted(ledger["allocation"].items(), key=lambda kv: -kv[1]):
        out.append("  %d  %s" % (n, LABELS[key]))
        out.append("     angle: %s" % ANGLE[key])
    out.append("")
    out.append("  security contingency: %s" % ledger["contingency"]["security"])
    out.append("  quantum contingency:  %s" % ledger["contingency"]["quantum"])
    if any(p.get("board_key") or p.get("board_slug") for p in ledger["top_pins"]):
        out.append("")
        out.append("TOP PINS (enriched)")
        out.append("-" * 60)
        for p in ledger["top_pins"]:
            if p.get("engagement") is None:
                continue
            out.append("  %-9s eng=%-4s %s" % (
                p.get("board_key") or p.get("board_slug") or "?",
                p.get("engagement"),
                (p.get("title") or p["url"])[:80]))
        agg = {}
        for p in ledger["top_pins"]:
            if not p.get("engagement"):
                continue
            k = p.get("board_key") or p.get("board_slug") or "unmatched"
            a = agg.setdefault(k, {"pins": 0, "engagement": 0})
            a["pins"] += 1
            a["engagement"] += p["engagement"]
        out.append("")
        out.append("TOP-PIN ENGAGEMENT BY BOARD (the breakout pins, not the whole board)")
        out.append("-" * 60)
        for k, a in sorted(agg.items(), key=lambda kv: -kv[1]["engagement"]):
            out.append("  %-9s pins=%-3d engagement=%d" % (k, a["pins"], a["engagement"]))
    return "\n".join(out)


def brief(ledger):
    out = ["PINTEREST PERFORMANCE BRIEF (read before choosing topics)", "=" * 60]
    out.append("Export %s, allocation source: %s" % (
        ledger["export_range"], ledger["allocation_source"]))
    out.append("")
    out.append("SLOTS FOR TODAY'S 10 POSTS:")
    for key, n in sorted(ledger["allocation"].items(), key=lambda kv: -kv[1]):
        out.append("  %d  %s" % (n, LABELS[key]))
        out.append("      angle: %s" % ANGLE[key])
    out.append("")
    out.append("CONTINGENCIES:")
    out.append("  security: %s" % ledger["contingency"]["security"])
    out.append("  quantum:  %s" % ledger["contingency"]["quantum"])
    out.append("")
    out.append("MEASURED RATES (90-day window, rates not totals):")
    for b in ledger["boards"]:
        out.append("  %-9s eng %6s | save %6s | outbound %6s" % (
            b["key"], fmt_pct(b["engagement_rate"]),
            fmt_pct(b["save_rate"]), fmt_pct(b["outbound_rate"])))
    return "\n".join(out)


def write_snapshot(ledger):
    """Keep a dated history so the weekly loop can diff rates across exports."""
    os.makedirs(SNAPSHOTS, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(SNAPSHOTS, stamp + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)
    keep = int(os.environ.get("PINTEREST_SNAPSHOT_KEEP", "12"))
    files = sorted(glob.glob(os.path.join(SNAPSHOTS, "*.json")))
    for old in files[:-keep]:
        try:
            os.remove(old)
        except OSError:
            pass
    return path


def compare(threshold=0.25, min_pins=15):
    """Rate deltas between the two newest snapshots. Rates only, never totals."""
    files = sorted(glob.glob(os.path.join(SNAPSHOTS, "*.json")))
    if len(files) < 2:
        return ["Only %d snapshot(s) on disk. Nothing to compare yet." % len(files)]
    try:
        prev = json.load(open(files[-2], encoding="utf-8"))
        cur = json.load(open(files[-1], encoding="utf-8"))
    except Exception as exc:
        return ["Could not read snapshots: %s" % exc]
    out = ["SNAPSHOT COMPARISON",
           "  from: %s (%s)" % (os.path.basename(files[-2]), prev.get("export_range")),
           "  to:   %s (%s)" % (os.path.basename(files[-1]), cur.get("export_range")),
           ""]
    prev_by = {b["key"]: b for b in prev.get("boards", [])}
    moved = []
    for b in cur.get("boards", []):
        p = prev_by.get(b["key"])
        if not p:
            continue
        for metric, label in (("engagement_rate", "engagement"), ("save_rate", "save")):
            old, new = p.get(metric) or 0, b.get(metric) or 0
            rel = ((new - old) / old) if old else (1.0 if new else 0.0)
            flag = ""
            if abs(rel) >= threshold:
                flag = "  <== MOVED"
                moved.append((b["key"], label, old, new, rel))
            out.append("  %-9s %-10s %6.2f%% -> %6.2f%%  (%+5.1f%%)%s" % (
                b["key"], label, old * 100, new * 100, rel * 100, flag))
    out.append("")
    if moved:
        out.append("QUALIFYING MOVES (>= %d%% relative):" % int(threshold * 100))
        for key, label, old, new, rel in moved:
            out.append("  %s %s rate %+0.1f%% relative" % (key, label, rel * 100))
    else:
        out.append("No board moved by the qualifying threshold. Leave the allocation alone.")
    out.append("")
    out.append("Evidence test: the board must appear in the board table in both snapshots. The export carries")
    out.append("no per-pin counts, so a finer test is not computable from it. Pin titles per board come from")
    out.append("pinterest_dedup.py (RSS), not from this table.")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brief", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--enrich", type=int, default=None)
    ap.add_argument("--csv")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--override")
    ap.add_argument("--compare", action="store_true")
    args = ap.parse_args(argv)

    if args.compare:
        print("\n".join(compare()))
        return 0

    path = find_export(args.csv)
    if not path:
        print("ERROR: no Pinterest Analytics overview CSV found in: %s" % ", ".join(SEARCH_DIRS))
        print("Export it from Pinterest Analytics and drop it in Downloads, then re-run.")
        return 2
    try:
        export = parse_export(path)
    except Exception as exc:
        print("ERROR: could not parse %s: %s" % (path, exc))
        return 2

    if args.override:
        os.makedirs(STATE_DIR, exist_ok=True)
        glob_override = args.override
        try:
            with open(glob_override, encoding="utf-8") as f:
                payload = json.load(f)
            with open(OVERRIDE, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            validate_override(OVERRIDE)
        except Exception as exc:
            print("ERROR: override rejected: %s" % exc)
            return 2

    enrich_n = args.enrich if args.enrich is not None else (12 if args.refresh else 0)
    ledger = build(export, enrich_n)

    if not args.no_write:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(LEDGER, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=2)
        snap = write_snapshot(ledger)

    print(brief(ledger) if args.brief else report(ledger))
    if not args.brief:
        print("")
        print("Ledger written to %s" % (LEDGER if not args.no_write else "(not written)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
