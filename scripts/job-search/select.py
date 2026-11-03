"""Stage 4b: build a baseline selected.json from the verified pool.

Usage:
    python select.py [--date YYYY-MM-DD] [--target 20] [--force]

Why this exists
---------------
The selection step used to be entirely the model's, reading packs and writing
selected.json by hand. That is where the October 21, 2026 run failed: the pool
held content, writing and AI-evaluation work, and the picks came back as a
Renewals Manager, a Solutions Consultant, a Junior Data Solutions Architect and
a salaried Senior Content Writer. The scripts were never the problem that day,
the picks were, and no amount of prose in SKILL.md stopped it.

This writes the list the rules actually describe:

  * live-verified rows with a direct apply path only
  * his job families first (writing, content, SEO, AI evaluation, support, admin)
  * in-band and hourly work before salaried work above the band
  * one role per company and role, not one per city
  * at most max_picks_per_source from any board and at least min_distinct_sources
  * twenty picks, or the honest short list when the pool cannot fill them

The model still owns the judgment layer: read the picks, rewrite fit, gap and
legit with the real evidence from the pack, and add the screened-out reasons.
Re-run report.py afterwards. Do not hand-build picks around this file.
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

PATH_ORDER = {"primary": 0, "band_flexible_1099": 1, "high_pay_1099": 2, "above_band_w2": 3,
              "unrated": 4}


def family_weight(title, rules):
    score = 0
    for pattern, weight in (rules.get("strong_title_patterns") or {}).items():
        if re.search(pattern, title or ""):
            score += weight
            break
    for pattern, weight in (rules.get("adjacent_title_patterns") or {}).items():
        if re.search(pattern, title or ""):
            score += weight
            break
    # Domain-qualified variants of his families are worse fits than the general
    # ones: "Legal & Government Content Reviewer" and "Financial Analyst - AI
    # Reviewer (Python)" are AI evaluation work that needs credentials he does not
    # have, and on the October 23 test they outranked "Prompt Writer" and "Search
    # Quality Evaluator", which are the two roles the October 17 list led with.
    for pattern, weight in (rules.get("deprioritize_title_patterns") or {}).items():
        if re.search(pattern, title or ""):
            score += weight
    return score


BAND_ORDER = {"in_band": 0, "capable": 1, "above": 2, "below": 3, "unrated": 4}


def rank_key(row, rules, profile=None):
    path, _sc = C.classify_path(row, rules)
    if row.get("selected_path"):
        path = row["selected_path"]
    return (
        # 1. the printed monthly figure lands inside his band
        BAND_ORDER.get(C.band_state(row, rules), 3),
        # 2. the posting matches his resume
        -C.resume_fit(row, profile if profile is not None else C.resume_profile()),
        # 3. his job families
        -family_weight(row.get("title"), rules),
        # 4. the rest of the run's scoring
        -(row.get("score") or 0),
        row.get("monthly_high") or 0,
    )


def usable(row, rules=None):
    """Is this row shippable on its own record, before any ranking?"""
    if (row.get("verify") or {}).get("verdict") != "live":
        return False
    if not C.has_direct_apply(row):
        return False
    if rules:
        title = row.get("title") or ""
        allow = any(re.search(p, title) for p in rules.get("allow_title_patterns") or [])
        if not allow and any(re.search(p, title) for p in rules.get("block_title_patterns") or []):
            return False
        if C.NON_ENGLISH_LANGUAGE_RE.search(title):
            return False
        if any(re.search(p, title) for p in rules.get("non_us_locations") or []):
            return False
        if not any(re.search(p, title) for p in rules.get("include_title_patterns") or []):
            return False
        # A stale verified pool can carry rows the current resume rules reject, so
        # the resume anti-signals are applied here too, not only in the prefilter.
        if C.resume_hard_anti(row):
            return False
        if C.resume_anti_title(row) and not C.resume_title_match(row):
            return False
        if not plausible(row, rules):
            return False
        pay = row.get("pay") or {}
        floor = float(rules.get("wage_floor_hourly", 17.0))
        if pay.get("period") == "hour" and pay.get("max") is not None \
                and float(pay["max"]) < floor:
            return False
        band_floor = float(rules.get("band_min_monthly", 1000))
        path, _sc = C.classify_path(row, rules)
        if row.get("monthly_high") is not None \
                and float(row["monthly_high"]) < band_floor \
                and path != "high_pay_1099":
            return False
    return True


def annual_floor(row):
    """The posted bottom of the pay range as a yearly figure, or None."""
    pay = row.get("pay") or {}
    low = pay.get("min")
    period = (pay.get("period") or "").lower()
    if low is None:
        return None
    if period == "year":
        return float(low)
    if period == "month":
        return float(low) * 12.0
    if period == "hour":
        return float(low) * 2080.0
    return None


def plausible(row, rules):
    """False when the pay line is a revenue, budget or ad-spend figure.

    The Limitless Agency row on October 23, 2026 read "$40,000 to $100,000 a month"
    and converted to $480,000 a year, which is a company number rather than a
    salary. The prefilter only applied the ceiling to annual postings, so a monthly
    figure walked straight into the picks.
    """
    ceiling = float(rules.get("max_plausible_annual", 400000))
    floor = annual_floor(row)
    return floor is None or floor <= ceiling


def human_reason(reason):
    """A drop reason a person can read. The stored reason names the regex that fired."""
    text = (reason or "").strip()
    for prefix, phrase in (
            ("title out of reach", "title is senior or engineering work, outside his direction"),
            ("title outside his direction", "not in his job families"),
            ("title names a non-US location", "posting is not US-based"),
            ("title requires native fluency", "requires native fluency in another language"),
            ("no pay stated", "states no pay"),
            ("not remote", "not a remote role"),
            ("not US-eligible", "not US-eligible"),
            ("US eligibility unconfirmed", "US eligibility not confirmed in the posting"),
            ("stale", "older than the freshness window"),
            ("already reported", "already sent on an earlier day"),
            ("already applied", "already applied"),
            ("duplicate", "duplicate of another listing"),
            ("below NY minimum wage", "below the NY minimum wage"),
            ("below his band floor", "pay is under his $1,000 floor"),
            ("implausible pay", "pay line reads as a revenue or budget figure"),
            ("permanently excluded", "permanently excluded platform"),
    ):
        if text.startswith(prefix):
            return phrase
    if text.startswith("blocked phrase"):
        return "posting carries a blocked phrase: %s" % text.split(":", 1)[-1].strip()
    if text.startswith("above-band salaried share cap") or text.startswith("source cap"):
        return "usable, but the run's verification budget went to stronger fits"
    return text.split(":")[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--target", type=int)
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing selected.json")
    args = ap.parse_args()

    rules = C.config("rules.json")
    profile = C.resume_profile()
    out_dir = C.run_dir(args.date)
    target = args.target or int(rules.get("target_count", 20))
    max_per_source = int(rules.get("max_picks_per_source", 6))
    min_sources = int(rules.get("min_distinct_sources", 4))
    path_out = os.path.join(out_dir, "selected.json")
    if os.path.exists(path_out) and not args.force:
        raise SystemExit("selected.json already exists; pass --force to rebuild the baseline "
                         "(the model's fit and gap text lives in that file)")

    rows = [r for r in C.load_jsonl(os.path.join(out_dir, "verified.jsonl"))
            if usable(r, rules)]

    # One lead per company and role. The same role posted per city is one job.
    unique, seen = [], set()
    for row in sorted(rows, key=lambda r: rank_key(r, rules, profile)):
        key = C.dedupe_key(row)
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    rows = unique

    # Fill by pay tier, then by resume fit inside each tier. Band-ok work fills
    # first and by itself would fill the whole list; a few well-matched roles above
    # the band are allowed because he said he will look at those when the fit is
    # real, and strong matches with no posted pay come last and capped.
    ranked = sorted(rows, key=lambda r: rank_key(r, rules, profile))
    rank_pos = {id(r): i for i, r in enumerate(ranked)}
    cap_above = int(rules.get("max_above_band_at_assumed_hours", target))
    cap_unpaid = int(rules.get("max_unpaid_picks", target))
    # The filler tier: after every in-band lead is placed, the rest of the twenty
    # comes from salaried roles whose posted range starts at $80,000 a year or
    # more, because those are the jobs worth his time once the flexible work runs
    # out. Under-band salaried roles are still selectable, but only as a last
    # resort behind the $80k tier.
    FILLER_MIN_ANNUAL = float(rules.get("filler_min_annual", 80000))
    cap_per_company = int(rules.get("max_picks_per_company", 2))
    platform_sources = set(rules.get("platform_sources") or [])
    picks, used, per_company = [], {}, {}
    above, unpaid = [0], [0]

    def tier(row):
        """The fill tier. In-band work first, then jobs paying over $80k a year.

        The list is built in that order: every in-band lead the verified pool holds,
        then salaried roles whose posted floor is $80,000 a year or more and that
        match the resume, then anything else only if those two tiers cannot fill
        twenty. Hourly, daily, per-task and per-project work counts as in-band work
        because the hours are his to choose, which is the whole point of the band.
        """
        path, _sc = C.classify_path(row, rules)
        pay = row.get("pay") or {}
        if not pay:
            return "unrated"
        if (pay.get("period") or "").lower() in ("hour", "day", "task", "gig", "project"):
            return "in_band"
        if path in ("primary", "band_flexible_1099"):
            return "in_band"
        if path == "high_pay_1099":
            return "high" if (annual_floor(row) or 0) >= FILLER_MIN_ANNUAL else "in_band"
        floor = annual_floor(row)
        if floor is not None and floor >= FILLER_MIN_ANNUAL:
            return "high"
        if path == "above_band_w2":
            return "other_above"
        return "unrated"

    def eligible(row, states, fit_floor=0):
        """Can this row be added right now without breaking a cap or a tier?"""
        if any(p["url"] == row["url"] for p in picks):
            return False
        source = row.get("source") or "?"
        if used.get(source, 0) >= max_per_source:
            return False
        state = tier(row)
        if state not in states:
            return False
        company = (row.get("company") or "?").strip().lower()
        # Alignerr and the like are talent platforms, not one employer: every row
        # carries the platform name, so a two-per-employer cap would stop at two
        # of its thirteen open roles.
        # An employer with several genuinely different in-band roles may show more
        # than one; an employer offering salaried roles above his band is held to
        # two so it cannot crowd out work he can take.
        company_cap = cap_per_company
        if state == "in_band":
            company_cap = int(rules.get("max_in_band_picks_per_company", 5))
        if source not in platform_sources and per_company.get(company, 0) >= company_cap:
            return False
        if state in ("high", "other_above", "in_band") and C.resume_fit(row, profile) < fit_floor:
            return False
        if state == "unrated" and (unpaid[0] >= cap_unpaid or C.resume_fit(row, profile) < max(fit_floor, 35)):
            return False
        return True

    def take(row):
        """Record one selected row and all counters that constrain later picks."""
        source = row.get("source") or "?"
        company = (row.get("company") or "?").strip().lower()
        state = tier(row)
        picks.append(row)
        used[source] = used.get(source, 0) + 1
        per_company[company] = per_company.get(company, 0) + 1
        if state == "high":
            above[0] += 1
        elif state == "unrated":
            unpaid[0] += 1

    # A full report has to span four sources. Reserve its first picks across
    # sources before a high-ranked board can consume the available slots. The
    # older round-robin fill only spread sources that happened to win a tier,
    # then reported a diversity failure after the fact.
    if len(rows) >= target:
        representatives = []
        seen_sources = set()
        for row in ranked:
            source = row.get("source") or "?"
            if source in seen_sources:
                continue
            state = tier(row)
            if eligible(row, (state,), 20):
                representatives.append(row)
                seen_sources.add(source)
        for row in representatives[:min_sources]:
            if len(picks) >= target:
                break
            if eligible(row, (tier(row),), 20):
                take(row)

    def fill(states, limit, fit_floor=0):
        """Fill to `limit`, preferring the boards that have contributed least.

        Round-robin by source, one slot per contributing source before any board
        gets a second pick. Without this the fill takes the top-ranked rows in
        rank order, so every above-band slot can land on the same two boards that
        already supplied the in-band work; the list then holds the target count
        but only three distinct sources, report.py refuses it on the source-spread
        gate, and the run ships a short list it did not have to ship. That is the
        October 22, 2026 failure: 78 usable rows across twelve boards, and a
        sixteen-lead delivery because the picks clustered on three of them.
        """
        while len(picks) < limit:
            best, best_key = None, None
            for row in ranked:
                if not eligible(row, states, fit_floor):
                    continue
                source = row.get("source") or "?"
                key = (used.get(source, 0), rank_pos[id(row)])
                if best_key is None or key < best_key:
                    best, best_key = row, key
            if best is None:
                return
            take(best)

    # Fill to the target in quality order: in-band paid work first, then salaried
    # roles above the band, then the no-pay rows last. The target is 20 and the
    # list ships at 20 whenever the verified pool holds 20 shippable rows.
    # Every in-band lead the pool holds goes in first, in resume-fit order. The rest
    # of the twenty comes from roles paying $80,000 a year or more, best fit first.
    # The fit bar only drops when that tier cannot fill the remaining slots, so the
    # list is always the strongest twenty the pool can support.
    fill(("in_band",), target, 0)
    fill(("high",), target, 55)
    fill(("high",), target, 45)
    fill(("high",), target, 35)
    fill(("other_above",), target, 60)
    fill(("other_above",), target, 45)
    fill(("unrated",), target, 60)
    fill(("high",), target, 0)
    fill(("other_above",), target, 0)
    fill(("unrated",), target, 0)

    # Report order: every in-band lead first (best resume fit first), then the $80k
    # roles in the same order, then the last-resort tiers. He reads the list top to
    # bottom, so the work he can take has to be the part he reaches first.
    TIER_ORDER = {"in_band": 0, "high": 1, "other_above": 2, "unrated": 3}
    picks.sort(key=lambda r: (TIER_ORDER.get(tier(r), 9), -C.resume_fit(r, profile),
                               -(r.get("score") or 0), r.get("monthly_high") or 0))

    # If the reserved pass left fewer than four sources only because the pool is
    # genuinely one-sided, say it here rather than silently shipping a short list.
    sources_used = {r.get("source") for r in picks}
    note = ""
    if len(sources_used) < min_sources:
        note = ("Only %d sources produced a usable lead today, under the %d-source floor. "
                "The report names the shortfall instead of padding from one board."
                % (len(sources_used), min_sources))

    picked_urls = {r["url"] for r in picks}
    reject_rows = []
    for row in sorted(rows, key=lambda r: rank_key(r, rules, profile)):
        if row["url"] in picked_urls:
            continue
        path, _sc = C.classify_path(row, rules)
        if path == "above_band_w2":
            reason = "salaried and above his $1,000 to $2,500 band, so it carries the coverage tradeoff and sits below the in-band picks"
        elif row.get("source") in used and used[row["source"]] >= max_per_source:
            reason = "usable, but the %s source cap is already filled and the list is spread across boards" % row["source"]
        else:
            reason = "usable, but ranked below the twenty picks on family fit and band"
        reject_rows.append({"title": row.get("title"), "company": row.get("company"),
                            "reason": reason})

    out = {
        "picks": [],
        "rejects": [],
        "summary": note,
        "_generated_by": "select.py",
    }
    for row in picks:
        path, _sc = C.classify_path(row, rules)
        pay = row.get("pay") or {}
        engagement = row.get("employment_type") or (
            "hourly %s" % pay.get("period") if pay.get("period") == "hour" else "not stated")
        out["picks"].append({
            "url": row["url"],
            "path": path,
            "employment": engagement,
            "effort": "standard ATS",
            "risk": "LOW-MODERATE" if path != "above_band_w2" else "MEDIUM",
            "fit": "%s role at %s in his direction (%s), posted as %s." % (
                row.get("title"), row.get("company"), engagement,
                row.get("pay_raw") or "pay stated on the posting"),
            "gap": "review the live posting before applying; the pack carries the full description",
            "legit": "%s%s" % ((row.get("company") or "the employer"),
                               " is the named employer and the apply link is its own application page"
                               if C.has_direct_apply(row) else " posts a direct application email"),
            "stretch": False,
        })

    # The screened-out section has to name the near-misses and the exact
    # disqualifier, which is the part he reads to trust the list. Rows that never
    # reached verification are included when they were in his job families and
    # failed one specific gate, so the report shows what was ruled out and why.
    try:
        dropped = C.load_jsonl(os.path.join(out_dir, "dropped.jsonl"))
    except Exception:
        dropped = []
    near_misses = [r for r in dropped
                   if family_weight(r.get("title"), rules) > 0
                   and not (r.get("drop_reason") or "").startswith("duplicate")]
    seen_rejects = set()
    for row in near_misses:
        key = C.dedupe_key(row)
        if key in seen_rejects or key in seen:
            continue
        seen_rejects.add(key)
        out["rejects"].append({"title": row.get("title"), "company": row.get("company"),
                               "reason": human_reason(row.get("drop_reason"))})
        if len(out["rejects"]) >= 18:
            break
    for item in reject_rows[:10]:
        out["rejects"].append(item)

    C.save_json(path_out, out)
    print("selected.json: %d picks (target %d) from %d sources: %s" % (
        len(out["picks"]), target, len(sources_used),
        ", ".join("%s %d" % (s, n) for s, n in sorted(used.items(), key=lambda kv: -kv[1]))))
    if note:
        print("NOTE:", note)
    print("->", path_out)
    print("next: read the packs, rewrite fit/gap/legit for each pick, then report.py")


if __name__ == "__main__":
    main()
