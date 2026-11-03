"""Stage 2: apply Vinny's hard rules to raw.jsonl and rank what survives.

Usage:
    python prefilter.py [--date YYYY-MM-DD]

Writes candidates.jsonl (ranked, survive) and dropped.jsonl (reason for every drop,
so the rules can be tuned instead of guessed at).
"""

import argparse
import os
import re
import sys
import time
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

RULES = C.config("rules.json")
RESUME = C.resume_profile()


def host_of(url):
    try:
        return (urlparse(url).hostname or "").lower().replace("www.", "")
    except ValueError:
        return ""


def norm_key(text):
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def find_any(patterns, text):
    for pattern in patterns:
        if re.search(pattern, text or ""):
            return pattern
    return None


def _thin(value):
    return "{:,.0f}".format(value)


def score(row, params):
    points = 0
    title = row.get("title", "")
    for pattern, weight in (RULES.get("title_weights") or {}).items():
        if re.search(pattern, title):
            points += weight
    # His direction is not "any job that mentions AI". The October 21, 2026
    # report was filled with salaried tech roles because the title scoring treated
    # "AI", "operations" and "automation" as equally good signals in a Solutions
    # Architect requisition and in a Content Writer requisition. The families he
    # actually applies to now carry their own weights and sit above general
    # management and analyst titles.
    for pattern, weight in (RULES.get("strong_title_patterns") or {}).items():
        if re.search(pattern, title):
            points += weight
            break
    for pattern, weight in (RULES.get("adjacent_title_patterns") or {}).items():
        if re.search(pattern, title):
            points += weight
            break
    if row.get("pay"):
        points += 3
    age = row.get("age_days")
    if age is not None:
        points += max(0, 5 - age)
    if row.get("source") in ("whoishiring", "wwr"):
        points += 1
    monthly = row.get("monthly_low")
    if monthly and monthly >= float(RULES.get("band_min_monthly", 1000)):
        points += 2
    # Supply has to lean the way Vinny's spec leans: work he can do inside the
    # $1,000 to $2,500 band, not salaried roles that put his wife's coverage at
    # risk. Flexible, hourly and contract work ranks up; salaried above-band
    # roles rank down so they cannot crowd the verification budget.
    path, _second_chance = C.classify_path(row, RULES)
    if path in ("primary", "band_flexible_1099"):
        points += 6
    elif path == "above_band_w2":
        points -= 4
    # Resume fit. Until October 21, 2026 nothing in the pipeline had read his
    # resume, which is why a technical writer with 190 engineering articles was
    # being sent "English Writing Generalist" and "Search Quality Evaluator".
    # The profile is built from the PDF by build_resume_profile.py.
    points += min(C.resume_fit(row, RESUME), 80) * 0.5
    # The number he reads is the printed monthly figure. Rank the ones that land
    # inside the band above the ones that only reach it by working fewer hours.
    state = C.band_state(row, RULES)
    if state == "in_band":
        points += 10
    elif state == "above":
        points -= 5
    return round(points, 2)


REMOTE_LOCATION_RE = re.compile(r"(?i)(remote|anywhere|worldwide|global|distributed|telecommute|\bwfh\b)")
REMOTE_BODY_RE = re.compile(r"(?i)(fully remote|100% remote|remote[- ]first|remote position|"
                            r"work from anywhere|remote \(us|remote, us|remote - us)")
COUNTRY_WIDE_RE = re.compile(r"(?i)^(united states|usa|u\.s\.|us|north america|americas|anywhere)$")


def remote_confirmed(row):
    """Is this posting actually remote, judged on location first?

    A city in the location field is not a remote role, however often the body
    mentions remote work in its benefits. ATS boards carry hybrid and on-site
    reqs whose descriptions still say the word, so the location has to lead.
    """
    loc = (row.get("location") or "").strip()
    desc = (row.get("description") or "")[:2500]
    if REMOTE_LOCATION_RE.search(loc):
        return True
    if COUNTRY_WIDE_RE.match(loc):
        return True
    if REMOTE_BODY_RE.search(desc):
        return True
    return False


def evaluate(row, params, seen, dup_keys, held=None, applied=None, variant_keys=None):
    """Return (keep: bool, reason: str)."""
    url = row.get("url", "")
    if not url:
        return False, "no url"
    held_urls, held_keys, held_when = held or (set(), {}, {})
    identities = [url, row.get("apply_url") or "", row.get("apply_email") or ""]
    for identity in identities:
        if identity and identity in held_urls:
            return False, "already reported on %s" % held_when.get(identity, "an earlier run")
    if held_keys.get(row.get("key", "")):
        return False, "already reported on %s (same company and role)" % held_keys[row["key"]]
    applied_urls, applied_keys = applied or (set(), set())
    if url in applied_urls:
        return False, "already applied to this posting (applied-jobs.md)"
    host = host_of(url)
    for blocked in RULES.get("blocklist_hosts", []):
        if host.endswith(blocked):
            return False, "permanently excluded platform: %s" % blocked
    haystack = "\n".join([row.get("title", ""), row.get("company", ""),
                          row.get("description", "")[:3000]])
    phrase = find_any(RULES.get("block_phrases", []), haystack.lower())
    if phrase:
        return False, "blocked phrase: %s" % phrase
    title_pattern = find_any(RULES.get("block_title_patterns", []), row.get("title", ""))
    # Some wanted titles trip a generic block token ("Prompt Engineer" contains
    # "engineer"). An explicit allow pattern for the family wins over that token.
    if title_pattern and find_any(RULES.get("allow_title_patterns", []), row.get("title", "")):
        title_pattern = None
    if title_pattern:
        return False, "title out of reach or outside his direction: %s" % title_pattern
    if C.NON_ENGLISH_LANGUAGE_RE.search(row.get("title") or ""):
        return False, "title requires native fluency in a language other than English"
    title_geo = find_any(RULES.get("non_us_locations", []), row.get("title") or "")
    if title_geo:
        # "Staff Technical Writer | Remote | Germany" is a Germany posting even
        # when the location field says Remote, and it was reaching the report.
        return False, "title names a non-US location: %s" % (row.get("title") or "")[:70]
    # Resume match. A transcription, healthcare, legal, video or assistant title is
    # not his line of work even when a keyword from it appears in the body, and the
    # October 21 list was full of them while he asked for content writing.
    hard = C.resume_hard_anti(row)
    if hard:
        return False, "not a resume match: %s is a different profession" % hard
    anti = C.resume_anti_title(row, RESUME)
    if anti and not C.resume_title_match(row, RESUME):
        return False, "not a resume match: %s work" % anti
    location = row.get("location") or ""
    site_text = location + " " + (row.get("description") or "")[:200]
    if params.get("require_remote", True) and not remote_confirmed(row):
        return False, "not remote: %s" % (location or "no remote signal in location or body")
    if find_any(RULES.get("onsite_patterns", []), site_text) and not find_any(
            RULES.get("remote_signals", []), site_text):
        return False, "not remote: %s" % (location or site_text[:60])
    if params.get("us_only", True):
        desc_head = (row.get("description") or "")[:3000]
        us_ok = find_any(RULES.get("us_specific_locations", []), location) if location else None
        if us_ok is None:
            us_ok = find_any(RULES.get("us_specific_locations", []), desc_head)
        bad_geo = find_any(RULES.get("non_us_locations", []), location) if location else None
        if bad_geo and not us_ok:
            return False, "not US-eligible: %s" % location
        if not us_ok:
            confirmed = find_any(RULES.get("us_eligibility_signals", []), desc_head)
            blocked_geo = find_any(RULES.get("non_us_description_signals", []), desc_head)
            if confirmed and not blocked_geo:
                us_ok = confirmed
            elif (row.get("source") or "").split(":")[0] in ("greenhouse", "ashby", "lever") \
                    and (location or "").strip().lower() in ("remote", "remote (us)", "remote, us", "remote - us", "anywhere in the us"):
                # An employer's own ATS board is a US employer we vetted; a bare
                # "Remote" there is a US-remote posting, not a foreign listing.
                us_ok = "remote on a US employer's own application board"
            elif (row.get("source") or "").split(":")[0] in (RULES.get("us_ok_sources") or []):
                # A platform Vinny already accepts as US-contracted work. Its own
                # postings say Remote with no country restriction, and the family
                # is AI evaluation and writing, not offshore contracting.
                us_ok = "remote on a US talent platform that contracts US contributors"
            else:
                return False, "US eligibility unconfirmed: %s" % (location or "no location stated")
    age = row.get("age_days")
    max_age = float(params.get("max_age_days", 7))
    if age is not None and age > max_age:
        return False, "stale: %.1f days old (limit %s)" % (age, max_age)
    expires = (row.get("extra") or {}).get("expires_at")
    if expires:
        stamp = C.parse_date(expires)
        if stamp is not None and stamp.timestamp() < time.time():
            return False, "listing expired %s" % expires
    if params.get("require_pay") and not row.get("pay"):
        # A direct-apply employer page that matches his resume is not junk just
        # because the pay is not in the feed: Workable, Greenhouse, Ashby, Lever
        # and SmartRecruiters often keep it in a field the public API does not
        # return. Those rows go through to verification carrying pay_missing,
        # ship only in a capped and clearly flagged group at the bottom of the
        # list, and never count toward the in-band share. Everything else is
        # still dropped for stating no pay.
        direct = (row.get("source") or "").split(":")[0] in (
            "workable", "greenhouse", "ashby", "lever", "smartrecruiters")
        if direct and C.resume_fit(row, RESUME) >= 40:
            row["pay_missing"] = True
        else:
            return False, "no pay stated"
    # ---- money floor ------------------------------------------------------
    # His band is the floor, and no lead may sit under it. An hourly rate below
    # the New York minimum wage ($17.00 in New York City, Long Island and
    # Westchester; $16.00 elsewhere in the state, 2026) is a straight violation
    # for work performed from here, so it is dropped on the rate alone whatever
    # the engagement shape. A monthly ceiling under band_min_monthly is below
    # his stated band and is filler at best, and filler never reaches
    # verification. The one exemption is the $80,000-plus 1099 path he has said
    # he will take. This exists because the October 20, 2026 report shipped a
    # $5-6.50/hr role and a $7/hr role with nothing in code to stop them.
    path, _sc = C.classify_path(row, RULES)
    pay = row.get("pay") or {}
    wage_floor = float(RULES.get("wage_floor_hourly", 17.0))
    # The floor applies to the top of a stated range, not to its bottom. A
    # posting that says "$20 to $40 per hour" can pay above the floor and is not
    # a sub-floor lead; a posting that tops out under it cannot pay above it and
    # is dropped. Testing the minimum instead threw away every honest range, and
    # ranges are how hourly and freelance work is priced.
    if pay.get("period") == "hour" and pay.get("max") is not None:
        if float(pay["max"]) < wage_floor:
            return False, "below NY minimum wage: tops out at $%.2f/hr against a $%.2f floor" % (
                float(pay["max"]), wage_floor)
    monthly_high = row.get("monthly_high")
    band_floor = float(RULES.get("band_min_monthly", 1000))
    if monthly_high is not None and float(monthly_high) < band_floor and path != "high_pay_1099":
        return False, "below his band floor: $%d/month against a $%d floor" % (
            int(float(monthly_high)), int(band_floor))
    max_annual = float(RULES.get("max_plausible_annual", 400000))
    if pay.get("period") == "year" and pay.get("max") is not None \
            and float(pay["max"]) > max_annual:
        return False, ("implausible pay: $%s a year reads as a revenue, budget or ad-spend "
                       "figure rather than a salary" % _thin(float(pay["max"])))
    if not find_any(RULES.get("include_title_patterns", []), row.get("title", "")):
        return False, "title outside his direction"
    key = norm_key(row.get("company", "")) + "|" + norm_key(row.get("title", ""))
    if key in dup_keys:
        return False, "duplicate of an earlier listing"
    variant_key = C.dedupe_key(row)
    if variant_keys and variant_key in variant_keys:
        return False, "duplicate of an earlier listing (same role, different city in the title)"
    if url in seen:
        return False, "duplicate url"
    return True, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--ledger", help="override the ledger path (testing)")
    ap.add_argument("--include-seen", action="store_true",
                    help="ignore the cross-day ledger and re-examine everything")
    args = ap.parse_args()

    params = C.config("params.json")
    out_dir = C.run_dir(args.date)
    raw = C.load_jsonl(os.path.join(out_dir, "raw.jsonl"))

    held = C.ledger_held(args.ledger, today=args.date or C.today_stamp())
    applied = C.applied_hold()
    if args.include_seen:
        held = (set(), {}, {})
        applied = (set(), set())
    held_urls, held_keys, _when = held
    print("ledger: holding %d urls and %d keys reported on earlier days (applied list: %d urls)" % (
        len(held_urls), len(held_keys), len(applied[0])))

    kept, dropped = [], []
    seen = set()
    dup_keys = set()
    variant_keys = set()
    for row in raw:
        row["key"] = C.lead_key(row)
        hours, hours_note = C.detect_hours(
            (row.get("employment_type") or "") + " " + (row.get("description") or "")[:2500],
            int(params.get("hours_per_week", 40)))
        row["hours_per_week"] = hours
        row["hours_note"] = hours_note
        row["monthly"] = C.monthly_estimate(row.get("pay"), hours)
        if row["monthly"]:
            row["monthly_low"], row["monthly_high"], row["pay_formula"] = row["monthly"]
        keep, reason = evaluate(row, params, seen, dup_keys, held=held, applied=applied,
                                variant_keys=variant_keys)
        if keep:
            seen.add(row["url"])
            dup_keys.add(norm_key(row.get("company", "")) + "|" + norm_key(row.get("title", "")))
            variant_keys.add(C.dedupe_key(row))
            row["score"] = score(row, params)
            kept.append(row)
        else:
            row["drop_reason"] = reason
            dropped.append(row)

    kept.sort(key=lambda r: (-r.get("score", 0), r.get("age_days") if r.get("age_days") is not None else 99))

    # A candidate pool that is mostly salaried and above the band produces a
    # report that is mostly salaried and above the band; that is the failure
    # Vinny called out on October 19, 2026. Hold salaried above-band rows to a
    # share of the pool so verification budget goes to work he can actually take.
    share = float(params.get("max_above_band_share", 0.5))
    if 0 < share < 1:
        classified = [(row, C.classify_path(row, RULES)[0]) for row in kept]
        other_count = sum(1 for _row, path in classified if path != "above_band_w2")
        ceiling = int(other_count * share / (1.0 - share))
        culled, above = [], 0
        for row, path in classified:
            if path == "above_band_w2":
                above += 1
                if above > ceiling:
                    row["drop_reason"] = "above-band salaried share cap: pool keeps at most %d such rows beside %d other leads" % (ceiling, other_count)
                    dropped.append(row)
                    continue
            culled.append(row)
        kept = culled

    # No single board may flood the run. The pick-level cap lives in report.py;
    # this one keeps the candidate pool itself spread across sources, so the
    # verification budget is not spent on one board's listings.
    cap = int(params.get("max_candidates_per_source", 0) or 0)
    if cap:
        trimmed, per_source = [], {}
        for row in kept:
            source = row.get("source") or "?"
            if per_source.get(source, 0) >= cap:
                row["drop_reason"] = "source cap: already kept %d from %s" % (cap, source)
                dropped.append(row)
                continue
            per_source[source] = per_source.get(source, 0) + 1
            trimmed.append(row)
        kept = trimmed

    C.write_jsonl(os.path.join(out_dir, "candidates.jsonl"), kept)
    C.write_jsonl(os.path.join(out_dir, "dropped.jsonl"), dropped)

    reasons = {}
    for row in dropped:
        key = row["drop_reason"].split(":")[0]
        reasons[key] = reasons.get(key, 0) + 1
    print("raw: %d  kept: %d  dropped: %d" % (len(kept) + len(dropped), len(kept), len(dropped)))
    for key, count in sorted(reasons.items(), key=lambda kv: -kv[1]):
        print("  drop %-45s %4d" % (key[:45], count))
    print("->", os.path.join(out_dir, "candidates.jsonl"))


if __name__ == "__main__":
    main()
