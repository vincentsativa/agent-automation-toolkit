#!/usr/bin/env python
"""Jobicy candidate pool builder for the remote-job-sources skill.

Pulls Jobicy's public no-auth REST API and emits the ONLY pool the job report
may draw from. We Work Remotely is not referenced anywhere in this script.

Usage:
    python jobicy_pool.py            # writes pool to stdout + pool files
    python jobicy_pool.py --json     # JSON only
    python jobicy_pool.py --pick     # refresh, drop already-reported jobs,
                                     # write pool_pick.txt and record the picks

Output files (next to this script):
    pool_tier1.txt   Part-Time / Contract / 1099 candidates (unreported only)
    pool_tier2.txt   Full-Time candidates with employer-stated $90K+ USD salary
    pool_all.json    machine-readable pool (both tiers, every field kept)
    pool_pick.txt    the 10 slots this run may report (--pick only)
    reported_ids.json ledger of job IDs already sent to Vinny

Repeat rule (Vinny, 2026-11-08): a job that has appeared in any earlier report
is never reported again. The ledger makes that mechanical instead of hoped for.
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

API = "https://jobicy.com/api/v2/remote-jobs"
UA = {"User-Agent": "Mozilla/5.0 (compatible; hermes-remote-job-sources)"}
HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "reported_ids.json")
PICK_FILE = os.path.join(HERE, "pool_pick.txt")
PICK_IDS = os.path.join(HERE, "pool_pick_ids.json")
PICK_TIER1 = 5
PICK_TIER2 = 5
PICK_TOTAL = PICK_TIER1 + PICK_TIER2  # report size Vinny asked for: 10 jobs
# Candidate window handed to the run: enough choice for fit, small enough that the
# burn (every window id is recorded as reported) stays under daily Jobicy inflow.
WINDOW_TIER1 = 8
WINDOW_TIER2 = 12

# Industries Jobicy exposes that match the candidate profile (AI systems, agents,
# automation, engineering, SEO, content ops, support). Education, healthcare, legal,
# HR, accounting, plain sales and design are deliberately not swept: those listings
# were the bulk of the 2026-11-08 report (math tutors, LSAT tutors, resident-physician
# admissions consultants, account executives).
INDUSTRIES = [
    "copywriting",
    "marketing",
    "data-science",
    "supporting",
    "admin",
    "technical-support",
    "management",
    "project-management",
    "qa-testing",
    "cybersecurity",
    "seo",
    "engineering",
    "admin-support",
]

# --- Fit gate -------------------------------------------------------------
# A listing is not a candidate just because Jobicy returned it. Anything that
# matches OFF_PROFILE is dropped outright: Vinny is an AI systems builder, not a
# tutor, translator, clinician, lawyer, accountant or quota carrier, and a role
# that needs a licence, a clearance or a bar card is not an option for him.
OFF_PROFILE = (
    # teaching / tutoring
    r"\btutor", r"\bteacher", r"\bteaching", r"\bprofessor", r"\blecturer",
    r"\binstructor", r"\bcurriculum", r"\bk-?12\b", r"\bkindergarten",
    r"\bacademic", r"\bcampus", r"\badmissions consultant",
    # language / transcription
    r"\binterpreter", r"\btranslator", r"translat", r"\blinguist",
    r"transcri", r"localization review", r"\bsubject matter expert",
    # medical / clinical / licensed care
    r"\bphysician", r"\bmedical", r"\bclinical", r"\bnurse", r"\brn\b",
    r"\bpharmac", r"\bdental", r"\bdentist", r"\btherapist", r"\boncology",
    r"\bsurgeon", r"\bveterinar", r"\bcaregiver", r"\bnanny",
    # legal
    r"\battorney", r"\bcounsel", r"\blawyer", r"\bparalegal", r"\blaw school",
    r"\bjuris", r"\bcompliance officer",
    # finance / accounting
    r"\bunderwriter", r"\baccountant", r"\bcontroller\b", r"\bbookkeep",
    r"\bauditor", r"\bcpa\b", r"\bpayroll", r"\btax\b",
    # sales / quota / partnerships
    r"\baccount executive", r"\bsales", r"\bquota", r"\bbusiness development",
    r"\bpartnerships?\b", r"\bsdr\b", r"\bbdr\b", r"\brevenue\b",
    r"\bchannel\b", r"\baccount manager",
    # HR
    r"\brecruiter", r"\brecruiting", r"\btalent acquisition", r"\bcompensation",
    r"\bbenefits\b", r"\bpeople partner",
    # licence / clearance gated
    r"\bsecurity clearance", r"\bclearance\b", r"\btop secret", r"\bts/sci",
    r"\bdod\b", r"\bdow\b", r"\bfederal civilian", r"\blicensed", r"\bregistered\b",
)

# Signals the candidate profile actually wants. The GATE is on the title: a title
# has to name one of these, otherwise a generic "Senior Software Engineer,
# Platform" or "Software Engineer II (Android/Kotlin)" is not a lead for an AI
# systems builder and does not enter the pool however fresh it is.
CORE_TITLE = (
    r"\bai\b", r"\ba\.i\.", r"\bagentic\b", r"\bagents?\b", r"\bautomation\b",
    r"\bautomate\b", r"\bllms?\b", r"\bgenai\b", r"\bgenerative\b",
    r"\bmachine learning\b", r"\bml\b", r"\bmlops\b", r"\bprompt",
    r"\brag\b", r"\borchestrat", r"\bgpt\b", r"\bopenai\b", r"\banthropic\b",
    r"\bfine-?tun", r"\bembeddings?\b", r"\bvector\b", r"\bchatbot\b",
)
WORK_TITLE = (
    r"\bpython\b", r"\bapis?\b", r"\bintegration", r"\bwebhook", r"\bzapier\b",
    r"\bn8n\b", r"\bscrap(er|ing)\b", r"\bdata engineer", r"\bdata pipeline",
    r"\bsolutions? (architect|engineer|consultant)", r"\bforward deployed",
    r"\bdeveloper advocate", r"\bdeveloper relations", r"\bdevrel\b",
    r"\btechnical writer", r"\btechnical writing", r"\bdocumentation specialist",
    r"\bseo\b", r"\btechnical seo\b", r"\bgeo\b", r"\bsearch engine optimization",
    r"\bcontent (strategy|strategist|operations|ops|marketing)",
    r"\bmarketing (operations|automation|engineer)",
    r"\bgrowth engineer", r"\bemail (marketing|deliverability|ops)", r"\bdeliverability\b",
    r"\btechnical support", r"\bsupport engineer", r"\bimplementation (engineer|consultant|specialist)",
    r"\bno-?code\b", r"\bworkflow", r"\bdevops\b", r"\bsre\b", r"\bplatform engineer",
    r"\binfrastructure engineer", r"\bsystems? (engineer|architect|builder)",
)
CORE_RE = tuple(re.compile(p) for p in CORE_TITLE)
WORK_RE = tuple(re.compile(p) for p in WORK_TITLE)
OFF_RE = tuple(re.compile(p) for p in OFF_PROFILE)
# A title must name at least one core/adjacent signal, and score at least 2.
MIN_FIT_TITLE_HITS = 1
MIN_FIT_TOTAL_HITS = 2

# A language-specific title is only viable when that language is English. Vinny
# does not write Ukrainian, Slovenian, Turkish or Portuguese, so "AI Trainers
# Network - Turkish" and "L1 Support Engineer - Portuguese" are not leads.
NON_ENGLISH = (
    "portuguese", "spanish", "french", "german", "italian", "dutch",
    "turkish", "thai", "tagalog", "somali", "slovenian", "slovak",
    "serbian", "croatian", "bosnian", "polish", "latvian", "lithuanian",
    "estonian", "georgian", "armenian", "uzbek", "kyrgyz", "maltese",
    "lao", "mongolian", "ukrainian", "russian", "mandarin", "cantonese",
    "japanese", "korean", "vietnamese", "indonesian", "malay", "hindi",
    "urdu", "arabic", "hebrew", "persian", "farsi", "swahili", "amharic",
    "romanian", "bulgarian", "hungarian", "czech", "danish", "swedish",
    "norwegian", "finnish", "greek", "icelandic", "welsh", "irish",
    "mien", "marshallese", "mixteco", "hmong", "nepali", "bengali",
    "tamil", "telugu", "punjabi", "gujarati", "marathi", "khmer", "burmese",
)


def is_off_profile(text):
    return any(rx.search(text) for rx in OFF_RE)


def is_language_blocked(title):
    low = title.lower()
    if "english" in low:
        return False
    return any(re.search(r"\b" + lang, low) for lang in NON_ENGLISH)


def fit_score(title, body):
    """Core profile signals weigh 3, adjacent work signals 2, body mentions 1.

    Returns (score, title_hits). A listing needs at least one CORE or WORK hit in
    the title itself to be a candidate at all.
    """
    head = title.lower()
    rest = body.lower()
    core_t = sum(1 for rx in CORE_RE if rx.search(head))
    work_t = sum(1 for rx in WORK_RE if rx.search(head))
    core_b = sum(1 for rx in CORE_RE if rx.search(rest))
    work_b = sum(1 for rx in WORK_RE if rx.search(rest))
    score = core_t * 3 + work_t * 2 + core_b + work_b
    return score, core_t + work_t


# How many 100-listing pages to walk via nextCursor before stopping.
MAX_PAGES = 12

PART_TIME_TYPES = {"part-time", "contract", "freelance", "temporary", "per-diem"}
# A fetch that returns less than this is treated as a failed pull, not a pool.
MIN_POOL = 100
FETCH_ATTEMPTS = 4
RETRY_WAIT = 20
US_MARKERS = ("usa", "u.s", "united states", "anywhere", "worldwide", "remote", "north america")
TIER1_MONTHLY_CAP = 2500
TIER2_SALARY_FLOOR = 90000


def fetch(params):
    url = API + "?" + "&".join(f"{k}={v}" for k, v in params.items())
    last = None
    for attempt in range(FETCH_ATTEMPTS):
        req = urllib.request.Request(url, headers=UA)
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.load(resp)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last = exc
            code = getattr(exc, "code", None)
            if code not in (429, 500, 502, 503, 504):
                raise
            if attempt + 1 < FETCH_ATTEMPTS:
                time.sleep(RETRY_WAIT * (attempt + 1))
    raise last


def collect():
    jobs = {}
    # 1. Base sweep, paged forward through nextCursor (count caps at 100/page).
    cursor = None
    for page in range(MAX_PAGES):
        params = {"count": 100}
        if cursor:
            params["cursor"] = cursor
        try:
            data = fetch(params)
        except Exception as exc:
            print(f"[warn] page {page} failed: {exc}", file=sys.stderr)
            break
        batch = data.get("jobs", [])
        new = [j for j in batch if j["id"] not in jobs]
        for job in batch:
            jobs[job["id"]] = job
        cursor = data.get("nextCursor")
        if not new or not data.get("hasMore") or not cursor:
            break
    # 2. Per-industry sweeps catch listings the global ordering buries.
    for ind in INDUSTRIES:
        try:
            data = fetch({"count": 50, "industry": ind})
        except Exception as exc:  # one bad sweep must not kill the pool
            print(f"[warn] sweep industry={ind} failed: {exc}", file=sys.stderr)
            continue
        for job in data.get("jobs", []):
            jobs[job["id"]] = job
    return list(jobs.values())


def is_us_ok(job):
    geo = (job.get("jobGeo") or "").lower()
    if not geo:
        return True
    return any(marker in geo for marker in US_MARKERS)


def monthly_pay(job):
    """Normalise a posting's pay to monthly USD, or None when unstated."""
    lo, hi = job.get("salaryMin"), job.get("salaryMax")
    period = (job.get("salaryPeriod") or "").lower()
    cur = (job.get("salaryCurrency") or "USD").upper()
    if cur not in ("USD", ""):
        return None
    if lo is None and hi is None:
        return None
    val = hi if hi else lo
    if period.startswith("year"):
        return val / 12.0
    if period.startswith("month"):
        return float(val)
    if period.startswith("hour"):
        return float(val) * 20 * 4.33
    if period.startswith("day"):
        return float(val) * 20
    return None


def load_ledger():
    """Return {job_id_str: date_first_reported}. Missing ledger = empty."""
    try:
        with open(LEDGER, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    ids = data.get("ids") if isinstance(data, dict) else None
    return dict(ids or {})


def save_ledger(ledger):
    payload = {
        "note": "Jobicy IDs already reported to Vinny. Never report these again.",
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(ledger),
        "ids": dict(sorted(ledger.items())),
    }
    tmp = LEDGER + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
    os.replace(tmp, LEDGER)


def classify(jobs):
    tier1, tier2 = [], []
    for job in jobs:
        types = {t.lower().replace(" ", "-") for t in job.get("jobType") or []}
        monthly = monthly_pay(job)
        title = job.get("jobTitle") or ""
        industries = job.get("jobIndustry") or []
        excerpt = (job.get("jobExcerpt") or "").replace("&hellip;", "")[:2000]
        # Fit gate: an off-profile TITLE never becomes a candidate, at any pay.
        # Only the title is gated: job descriptions routinely mention sales, legal
        # or clinical teams, and Jobicy's marketing industry is literally named
        # "Marketing & Sales", so body text is used for scoring only.
        if is_off_profile(title.lower()) or is_language_blocked(title):
            continue
        score, title_hits = fit_score(title, f"{title} {' '.join(industries)} {excerpt}")
        if title_hits < MIN_FIT_TITLE_HITS or score < MIN_FIT_TOTAL_HITS:
            continue
        rec = {
            "id": job["id"],
            "title": title,
            "company": job.get("companyName"),
            "types": job.get("jobType"),
            "industry": industries,
            "geo": job.get("jobGeo"),
            "level": job.get("jobLevel"),
            "posted": job.get("pubDate"),
            "salary_min": job.get("salaryMin"),
            "salary_max": job.get("salaryMax"),
            "salary_currency": job.get("salaryCurrency"),
            "salary_period": job.get("salaryPeriod"),
            "monthly_usd": round(monthly, 2) if monthly else None,
            "fit": score,
            "apply": job["url"],
            "excerpt": excerpt[:400],
        }
        if types & PART_TIME_TYPES:
            if monthly is None or monthly <= TIER1_MONTHLY_CAP:
                tier1.append(rec)
            elif monthly * 12 >= TIER2_SALARY_FLOOR:
                # A contract/1099 posting paying full-time money is Tier 2 work,
                # not a part-time job. The $2,500 part-time cap used to bin these
                # (Maven Clinic Conversational AI copywriter, $104K contract).
                tier2.append(rec)
        elif "full-time" in types:
            lo = job.get("salaryMin") or 0
            if lo >= TIER2_SALARY_FLOOR and (job.get("salaryPeriod") or "yearly").lower().startswith("year"):
                tier2.append(rec)
    tier1.sort(key=lambda r: (-r["fit"], r["monthly_usd"] is None, -(r["monthly_usd"] or 0)))
    tier2.sort(key=lambda r: (-r["fit"], -(r["salary_min"] or r["monthly_usd"] or 0)))
    return tier1, tier2


def render(recs, header):
    lines = [f"== {header} ({len(recs)}) ==", ""]
    for i, r in enumerate(recs, 1):
        pay = "not stated"
        if r["salary_min"] or r["salary_max"]:
            pay = f"{r['salary_min']}-{r['salary_max']} {r['salary_currency']} per {r['salary_period']}"
        lines += [
            f"{i}. {r['title']}",
            f"   Company: {r['company']}",
            f"   Type:    {', '.join(r['types'] or [])}",
            f"   Pay:     {pay}",
            f"   Remote:  {r['geo']}",
            f"   Posted:  {r['posted']}",
            f"   Apply:   {r['apply']}",
            "",
        ]
    return "\n".join(lines)


def pick(tier1, tier2, ledger, limit1=WINDOW_TIER1, limit2=WINDOW_TIER2):
    """Best profile fit first, freshness as tie-break; one listing per company.

    Ledger ids never come back. One-per-company stops a single employer filling
    the window (2026-11-08 shipped three Think Academy tutor ads and three Welo
    translation ads in one report).

    Tier 1 short of its 5 slots hands the difference to Tier 2, so the report is
    still PICK_TOTAL jobs when Tier 2 has the supply (Vinny, 2026-11-08).
    """
    def fresh(recs):
        out = [r for r in recs if str(r["id"]) not in ledger]
        out.sort(key=lambda r: (r["posted"] or "", r["id"]), reverse=True)
        out.sort(key=lambda r: -r["fit"])
        seen, uniq = set(), []
        for rec in out:
            key = (rec.get("company") or "").strip().lower()
            if key and key in seen:
                continue
            seen.add(key)
            uniq.append(rec)
        return uniq
    uniq1 = fresh(tier1)
    uniq2 = fresh(tier2)
    p1 = uniq1[:limit1]
    # Every Tier 1 slot that cannot be filled becomes a Tier 2 slot.
    deficit = max(0, PICK_TIER1 - len(p1))
    p2 = uniq2[:limit2 + deficit]
    return p1, p2


def main():
    do_pick = "--pick" in sys.argv
    ledger = load_ledger()
    jobs = [j for j in collect() if is_us_ok(j)]
    if len(jobs) < MIN_POOL:
        print(f"FAILED PULL: only {len(jobs)} US-eligible listings came back from Jobicy "
              f"(minimum {MIN_POOL}). No pool, no pick, no report. Nothing was written "
              f"and the ledger was not touched. Re-run once Jobicy stops rate-limiting.",
              file=sys.stderr)
        return 1
    tier1_all, tier2_all = classify(jobs)
    unreported1 = [r for r in tier1_all if str(r["id"]) not in ledger]
    unreported2 = [r for r in tier2_all if str(r["id"]) not in ledger]
    tier1, tier2 = unreported1, unreported2
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {"generated": stamp, "source": "jobicy.com REST API v2", "raw": len(jobs),
               "ledger_size": len(ledger),
               "excluded_as_reported": (len(tier1_all) - len(unreported1)) + (len(tier2_all) - len(unreported2)),
               "tier1": tier1, "tier2": tier2}
    with open(os.path.join(HERE, "pool_all.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
    with open(os.path.join(HERE, "pool_tier1.txt"), "w", encoding="utf-8") as fh:
        fh.write(render(tier1, f"TIER 1 PART-TIME / CONTRACT / 1099 pool, Jobicy {stamp}"))
    with open(os.path.join(HERE, "pool_tier2.txt"), "w", encoding="utf-8") as fh:
        fh.write(render(tier2, f"TIER 2 FULL-TIME $90K+ pool, Jobicy {stamp}"))
    if do_pick:
        p1, p2 = pick(tier1, tier2, ledger)
        # Report size is fixed at PICK_TOTAL: a short Tier 1 is paid for by Tier 2.
        report1 = min(PICK_TIER1, len(p1))
        report2 = min(PICK_TOTAL - report1, len(p2))
        total = report1 + report2
        total_short = max(0, PICK_TOTAL - total)
        short1 = max(0, PICK_TIER1 - len(p1))
        lines = [f"== THIS RUN'S CANDIDATE WINDOW, Jobicy {stamp} ==",
                 f"unreported pool: tier1={len(tier1)} tier2={len(tier2)}",
                 f"Report exactly {report1} Tier 1 + {report2} Tier 2 = {total} jobs",
                 f"(Tier 1 has {report1} of its {PICK_TIER1} slots; Tier 2 makes up the difference)"
                 if short1 else f"(full {PICK_TIER1} + {PICK_TIER2} split available)",
                 "for the candidate profile. Nothing outside these IDs is allowed.", ""]
        lines += render(p1, f"TIER 1 WINDOW - PART-TIME / CONTRACT / 1099 ({len(p1)} candidates)").split("\n")
        lines += render(p2, f"TIER 2 WINDOW - FULL-TIME $90K+ ({len(p2)} candidates)").split("\n")
        if short1:
            lines.append(f"TIER 1 SHORT {short1}: the balance comes from Tier 2, not from a repeat "
                         f"and not from an off-profile role")
        if total_short:
            lines.append(f"TOTAL SHORTFALL {total_short}: only {total} of {PICK_TOTAL} reportable "
                         f"leads exist today. Report {total} and say how many are missing.")
        with open(PICK_FILE, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        today = datetime.now().strftime("%Y-%m-%d")
        for rec in p1 + p2:
            ledger.setdefault(str(rec["id"]), today)
        save_ledger(ledger)
        with open(PICK_IDS, "w", encoding="utf-8") as fh:
            json.dump({"generated": stamp, "date": today,
                       "ids": [str(r["id"]) for r in p1 + p2]}, fh, indent=1)
        print(f"pulled {len(jobs)} US-eligible Jobicy listings at {stamp}")
        print(f"unreported: tier1={len(tier1)} tier2={len(tier2)}; ledger now {len(ledger)} ids")
        print("\n".join(lines))
        return
    if "--json" in sys.argv:
        print(json.dumps(payload, indent=1))
        return
    print(f"pulled {len(jobs)} US-eligible Jobicy listings at {stamp}")
    print(f"dropped {payload['excluded_as_reported']} listings already reported (ledger {len(ledger)})")
    print(render(tier1, "TIER 1 PART-TIME / CONTRACT / 1099 pool"))
    print(render(tier2, "TIER 2 FULL-TIME $90K+ pool"))


if __name__ == "__main__":
    sys.exit(main() or 0)
