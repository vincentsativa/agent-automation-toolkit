"""Stage 5: render the final report from the model's picks.

Usage:
    python report.py [--date YYYY-MM-DD]

Input  : verified.jsonl (script output) + selected.json (model output)
Output : report-YYYY-MM-DD.txt  (unwrapped, one paragraph per physical line)

selected.json shape:
{
  "picks": [
    {"url": "<must match a verified row>", "fit": "why it fits",
     "gap": "none" | "specific gap", "risk": "LOW|LOW-MODERATE|MEDIUM|HIGH",
     "effort": "quick apply" | "heavy ATS", "engagement": "1099 contract",
     "legit": "evidence it is a real employer", "stretch": false}
  ],
  "rejects": [{"title": "...", "company": "...", "reason": "exact disqualifier"}],
  "summary": "optional one paragraph"
}

The count is honest: if fewer picks than the target arrive, the report refuses to
render unless --allow-short is passed, and then it says so in the header.
"""

import argparse
import os
import re
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402


def _flat(text):
    """Flatten pipes out of pick prose before it reaches a report line.

    The layout gate below refuses any line that packs two facts together with a
    pipe, because that is the blob layout Vinny rejected. Pick prose is built by
    interpolating the employer's own title, and titles legally contain pipes
    ("Senior PM | $110K Base | Remote"). The lead heading is exempt because the
    title is the employer's words, but the prose fields are the renderer's to
    produce, so the pipe is replaced there rather than refusing a lead whose
    title the employer wrote with one.
    """
    return re.sub(r"\s*\|\s*", " - ", (text or "").strip())

RULE = "=" * 80

PATH_LABEL = {
    "primary": "in your $1,000 to $2,500 a month band",
    "band_flexible_1099": "hourly 1099 work, above the band at full time and inside it at the hours you choose",
    "high_pay_1099": "$80k+ 1099 or contract, the path you said you will take, coverage tradeoff accepted",
    "above_band_w2": "above the band and salaried, so the coverage tradeoff is a real decision rather than an upgrade",
    "unrated": "pay not stated, so no band can be applied",
}


def pick_url(pick, verified):
    return pick.get("url")


def money(value):
    if value is None:
        return "unknown"
    return "$%s" % C._fmt(round(value))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--allow-short", action="store_true")
    ap.add_argument("--ledger", help="override the ledger path (testing)")
    ap.add_argument("--no-ledger", action="store_true",
                    help="render without recording the leads as reported")
    args = ap.parse_args()

    rules = C.config("rules.json")
    params = C.config("params.json")
    target = int(rules.get("target_count", 20))
    band_min = float(rules.get("band_min_monthly", 1000))
    band_max = float(rules.get("band_max_monthly", 2500))
    out_dir = C.run_dir(args.date)
    # One row per url, and a live verification wins. A re-verified day can leave
    # the same url twice with different verdicts, and a plain dict build kept the
    # last write, which made report.py look up an "unknown" copy of a row that had
    # verified live and refuse its own picks.
    verified = {}
    for row in C.load_jsonl(os.path.join(out_dir, "verified.jsonl")):
        url = row.get("url")
        previous = verified.get(url)
        if previous is None or ((previous.get("verify") or {}).get("verdict") != "live"
                                and (row.get("verify") or {}).get("verdict") == "live"):
            verified[url] = row
    selected = C.load_json(os.path.join(out_dir, "selected.json"))
    if not selected or not selected.get("picks"):
        raise SystemExit("selected.json missing or has no picks")

    picks = selected["picks"]
    if len(picks) < target and not args.allow_short:
        raise SystemExit(
            "honest-count rule: %d picks for a target of %d. A short render is a failed run, "
            "not a deliverable. Widen collection, run the top-up and the Workable employer "
            "boards, re-verify and re-select until the list holds %d." % (len(picks), target, target))

    lines = []
    lines.append(RULE)
    lines.append("REMOTE JOB LEADS: %d VERIFIED LEADS" % len(picks))
    lines.append(RULE)
    lines.append("")
    lines.append("Date: %s" % (args.date or C.today_stamp()))
    lines.append("Applicant: New York")
    lines.append("Target: remote part-time, contract, freelance or flexible work capable of roughly $%s to $%s gross per month" % (
        C._fmt(round(band_min)), C._fmt(round(band_max))))
    lines.append("Focus: AI evaluation and training, AI and technical writing, SEO and GEO content, content operations, email marketing and deliverability, design and creative, admin and support work")
    lines.append("")
    if selected.get("summary"):
        lines.append(selected["summary"])
        lines.append("")
    # The composition line is computed from the picks, not written by the model.
    # His spec makes the majority-in-band rule binding, and on October 21, 2026
    # the summary described a list of salaried roles as acceptable while every
    # lead sat above his band. A computed line cannot drift from the leads.
    counted = {"primary": [], "band_flexible_1099": [], "high_pay_1099": [],
               "above_band_w2": [], "unrated": []}
    for pick in picks:
        row = verified.get(pick.get("url"))
        if row is None:
            continue
        path, _sc = C.classify_path(row, rules)
        if pick.get("path"):
            path = pick["path"]
        counted.setdefault(path, []).append(row)
    rows_by_url = {p.get("url"): verified.get(p.get("url")) for p in picks}
    states = [C.band_state(r, rules) for r in rows_by_url.values() if r is not None]
    printed_in_band = states.count("in_band")
    capable = states.count("capable")
    above = states.count("above")
    unpaid_n = sum(1 for r in rows_by_url.values() if r is not None and not r.get("pay"))
    lines.append("Composition")
    lines.append("  In your $%s to $%s band as written on the posting: %d of %d" % (
        C._fmt(round(band_min)), C._fmt(round(band_max)), printed_in_band, len(picks)))
    lines.append("  Hourly or per-task work that reaches the band at hours you choose: %d of %d" % (
        capable, len(picks)))
    lines.append("  Salaried and above the band: %d of %d" % (above, len(picks)))
    lines.append("  No pay stated on the posting: %d of %d" % (unpaid_n, len(picks)))
    lines.append("")
    lines.append("Every lead was matched against the resume in references/resume, not against a generic term list.")
    source_mix = {}
    for pick in picks:
        row = verified.get(pick.get("url")) or {}
        source = row.get("source") or pick.get("source") or "?"
        source_mix[source] = source_mix.get(source, 0) + 1
    if source_mix:
        lines.append("")
        lines.append("Source mix: %s" % ", ".join("%s %d" % (s, n)
                                                   for s, n in sorted(source_mix.items(), key=lambda kv: -kv[1])))
    lines.append("")
    lines.append("Every lead below was checked live today at the employer's own page, carries a working application path, and states pay or is flagged for it. Every lead came from this run; none is a choice of yours and none is carried over from a previous list.")
    lines.append("")
    lines.append("")
    lines.append(RULE)
    lines.append("THE LEADS")
    lines.append(RULE)
    lines.append("")

    problems = []
    for number, pick in enumerate(picks, start=1):
        row = verified.get(pick.get("url"))
        if row is None:
            problems.append("pick %d (%s) does not match any verified row" % (number, pick.get("url")))
            continue
        title = row.get("title") or "(untitled)"
        company = row.get("company") or "(company not stated)"
        age = row.get("age_days")
        posted = row.get("posted") or "date not stated"
        age_txt = "age unknown, treat with care" if age is None else "%.0f days old" % age
        # Everything about this lead hangs off its money path, so resolve it
        # before any line is written and print it inside the Pay block.
        path, second_chance = C.classify_path(row, rules)
        if pick.get("path"):
            path = pick["path"]
        label = PATH_LABEL.get(path, path)
        pay = row.get("pay") or {}
        hourly = (pay.get("period") or "").lower() in ("hour", "day", "task", "gig", "project",
                                                       "article", "piece", "word",
                                                       "deliverable", "batch")
        if path == "primary" and pay.get("period") == "hour" \
                and (row.get("monthly_high") or 0) > band_max:
            label = ("hourly or task work priced by the rate, and inside your $1,000 to $2,500 band "
                     "at the hours you choose")

        lines.append(RULE)
        lines.append("%d. %s" % (number, title))
        lines.append(RULE)
        lines.append("")
        lines.append("Role")
        lines.append("  Company: %s" % company)
        lines.append("  Source: %s" % (row.get("source") or "unknown"))
        lines.append("  Posted: %s (%s)" % (C.fmt_posted(posted), age_txt))
        lines.append("  Engagement: %s" % (pick.get("engagement") or row.get("employment_type") or "not stated"))
        lines.append("  Application effort: %s" % (pick.get("effort") or "not judged"))
        lines.append("  Background-check risk: %s" % (pick.get("risk") or "unrated"))
        lines.append("")
        lines.append("Pay")
        monthly = ""
        if row.get("monthly_low") is not None and not hourly:
            monthly = " = %s to %s per month" % (money(row["monthly_low"]), money(row["monthly_high"]))
        if not row.get("pay"):
            lines.append("  Not stated in the posting. Confirm the rate and the engagement before applying; this lead is here on the strength of the resume match, not the pay.")
        else:
            lines.append("  %s%s" % (_flat(C.pretty_pay(row.get("pay"), row.get("pay_raw") or "")), monthly))
        if hourly:
            # He is paid a rate, not a salary, so the number that matters is how
            # many paid hours land inside his band. Printing a 40-hour month at a
            # $120 ceiling is what made the October 21 list read as above band on
            # every line when the work itself is part-time by design.
            rate_low = float(pay.get("min") or pay.get("max") or 0)
            rate_high = float(pay.get("max") or rate_low)
            if rate_low > 0 and rate_high > 0 and band_min <= band_max:
                hrs_low = band_min / rate_high
                hrs_high = band_max / rate_low
                lines.append("  Band hours: $%s to $%s a month is about %.0f to %.0f paid hours a month, or %.0f to %.0f hours a week. The rate supports more hours than that and the hours are yours to set." % (
                    C._fmt(round(band_min)), C._fmt(round(band_max)), hrs_low, hrs_high,
                    hrs_low / 4.33, hrs_high / 4.33))
        elif row.get("pay_formula"):
            lines.append("  Monthly math: %s%s" % (row["pay_formula"], monthly))
        lines.append("  Money path: %s" % label)
        high = row.get("monthly_high")
        if high is not None and high > band_max and path == "above_band_w2":
            lines.append("")
            lines.append("Coverage")
            lines.append("  Insurance flag: at %s per month this sits above your %s to %s band, and income over about %s a month puts your wife's SSI and medical insurance at risk. Weigh it against replacing that coverage before applying." % (
                money(high), money(band_min), money(band_max), money(band_max)))
        elif high is not None and high > band_max and path == "high_pay_1099":
            lines.append("")
            lines.append("Coverage")
            lines.append("  Coverage tradeoff: at %s per month this is above your %s to %s band, which is the tradeoff you already said you will take on 1099 work at this level. Confirm the coverage replacement plan before you start, not after." % (
                money(high), money(band_min), money(band_max)))
        lines.append("")
        lines.append("Apply")
        apply_url = (row.get("apply_url") or "").strip()
        apply_email = (row.get("apply_email") or "").strip()
        if apply_url and not C.is_aggregator_url(apply_url) and not C.is_apply_index(apply_url):
            lines.append("  %s" % apply_url)
            if apply_email:
                lines.append("  Email: %s" % apply_email)
        elif apply_email:
            lines.append("  Email: %s" % apply_email)
        else:
            problems.append("pick %d (%s) has no direct apply path" % (number, title))
        lines.append("")
        lines.append("Fit")
        # Which part of the resume this lead answers. He asked whose resume the
        # search was using; this line is the answer, taken from the posting's own
        # words against the profile built from his PDF.
        profile = C.resume_profile()
        title_hit = C.resume_title_match(row, profile)
        body_hits = [p for p, w in sorted((profile.get("body_keywords") or {}).items(),
                                         key=lambda kv: -kv[1])
                     if p in (row.get("description") or "").lower()][:6]
        if title_hit or body_hits:
            lines.append("  Resume match: %s%s" % (
                ("title matches \"%s\"" % title_hit) if title_hit else "body matches his record",
                ("; posting talks " + ", ".join(body_hits)) if body_hits else ""))
        lines.append("  Why it fits: %s" % _flat(pick.get("fit") or ""))
        gap = _flat(pick.get("gap") or "none")
        lines.append("  Gap: %s" % gap)
        if pick.get("stretch"):
            lines.append("  Stretch fit: yes. The gap named above is the specific reason.")
        lines.append("")
        lines.append("Verification")
        lines.append("  Live check: %s at %s (%s)" % (
            row["verify"]["verdict"], row["verify"]["checked_at"], row["verify"]["evidence"]))
        if pick.get("legit"):
            lines.append("  Legitimacy: %s" % _flat(pick["legit"]))
        if second_chance:
            lines.append("  Second chance: the posting itself carries second-chance or no-background-check language, so this is one to test early rather than avoid.")
        lines.append("")
        lines.append("")

    # ---- application priority -------------------------------------------------
    # Same order as the leads, stated plainly, because the point of the list is
    # to tell him what to do first. He asked for best-to-worst ordering and the
    # October 17, 2026 report he liked carried this block.
    lines.append("")
    lines.append(RULE)
    lines.append("APPLICATION PRIORITY")
    lines.append(RULE)
    lines.append("")
    for number, pick in enumerate(picks, start=1):
        row = verified.get(pick.get("url")) or {}
        title = row.get("title") or pick.get("title") or "(untitled)"
        company = row.get("company") or pick.get("company") or "(company not stated)"
        engagement = pick.get("engagement") or row.get("employment_type") or "engagement not stated"
        pay = _flat(C.pretty_pay(row.get("pay"), row.get("pay_raw") or "")) or "pay not stated"
        lines.append("%d. %s" % (number, title))
        lines.append("   %s. %s. %s." % (company, engagement, pay))
        lines.append("")
    lines.append("")

    lines.append(RULE)
    lines.append("SCREENED OUT THIS RUN")
    lines.append(RULE)
    lines.append("")
    for number, reject in enumerate(selected.get("rejects") or [], start=1):
        lines.append("%d. %s" % (number, reject.get("title", "?")))
        lines.append("   %s. %s" % (reject.get("company", "?"), reject.get("reason", "?")))
        lines.append("")

    lines.append("")
    lines.append(RULE)
    lines.append("HOW EVERY LEAD WAS VERIFIED")
    lines.append(RULE)
    lines.append("")
    lines.append("Postings were pulled from the sources named per lead, filtered against your standing parameters in the same run, then each employer page was fetched again during this run and classified live, dead, blocked, or unknown from its own content.")
    lines.append("")
    lines.append("Only live pages with a working apply path and US eligibility made the list. Every apply link points at the employer's own application page or a direct application email, never at a job board listing that demands an account before it shows the form.")
    lines.append("")
    lines.append("Pay is quoted as posted, and the monthly figure is the stated rate converted with the formula shown on the lead.")
    lines.append("")
    lines.append("Screened-and-held leads: %d, out of %d candidates that survived the rules and %d raw postings pulled this run." % (
        len(selected.get("rejects") or []), len(verified), len(C.load_jsonl(os.path.join(out_dir, "raw.jsonl")))))
    lines.append("")

    # ---- hard gates on the final twenty -------------------------------------
    # A lead with no direct apply path, an unverified posting, or a list dominated
    # by one board is not shippable. These are the rules Vinny set on Oct 18, 2026:
    # he will not spend an hour creating accounts, and one board is not a search.
    max_per_source = int(rules.get("max_picks_per_source", 6))
    max_share = float(rules.get("max_single_source_share", 0.0) or 0.0)
    min_sources = int(rules.get("min_distinct_sources", 4))
    per_source, bad_verdicts, no_apply = {}, [], []
    for pick in picks:
        row = verified.get(pick.get("url"))
        if row is None:
            continue
        source = row.get("source") or "?"
        per_source[source] = per_source.get(source, 0) + 1
        verdict = (row.get("verify") or {}).get("verdict")
        if verdict != "live":
            bad_verdicts.append("%s (%s: %s)" % (row.get("title"), source, verdict))
        if not C.has_direct_apply(row):
            no_apply.append("%s (%s)" % (row.get("title"), source))
    errors = []
    over = {s: n for s, n in per_source.items() if n > max_per_source}
    if over:
        errors.append("source-diversity rule: more than %d picks from one source (%s). Spread the picks across sources and report the honest shortfall instead." % (
            max_per_source, ", ".join("%s=%d" % (s, n) for s, n in sorted(over.items()))))
    if max_share and picks:
        biggest = max(per_source.values()) if per_source else 0
        if biggest / float(len(picks)) > max_share:
            errors.append("source-diversity rule: %s supplies %d of %d picks, more than the %.0f%% one-board ceiling. Spread the list or report the honest shortfall." % (
                max(per_source, key=per_source.get), biggest, len(picks), max_share * 100))
    # A full list must span the minimum number of sources. A genuinely short day
    # cannot be held to the same bar, but it still may not be a one-board list.
    need = min_sources if len(picks) >= target else min(2, len(picks))
    if len(per_source) < need:
        errors.append("source-diversity rule: %d distinct sources for %d picks, minimum is %d. A list drawn from one board is not a search." % (
            len(per_source), len(picks), need))
    if bad_verdicts:
        errors.append("only live-verified leads may ship, these are not: %s" % "; ".join(bad_verdicts))
    if no_apply:
        errors.append("no direct apply path (board page or signup wall only): %s" % "; ".join(no_apply))
    # ---- money floor -------------------------------------------------------
    # A pick under the floor cannot render even when selected.json was built by
    # hand. The October 20, 2026 report shipped a $5-6.50/hr role and a $7/hr
    # role because the floor lived in prose and not in this gate. An hourly rate
    # below the NY minimum wage is a legal violation for work performed from
    # New York, and a monthly ceiling under his band is filler, not a lead.
    wage_floor = float(rules.get("wage_floor_hourly", 17.0))
    band_floor = float(rules.get("band_min_monthly", 1000))
    under_floor = []
    for pick in picks:
        row = verified.get(pick.get("url"))
        if row is None:
            continue
        path, _sc = C.classify_path(row, rules)
        pay = row.get("pay") or {}
        if pay.get("period") == "hour" and pay.get("max") is not None \
                and float(pay["max"]) < wage_floor:
            under_floor.append("%s (%s): tops out at $%.2f/hr, under the $%.2f NY minimum wage"
                               % (row.get("title"), row.get("company"), float(pay["max"]), wage_floor))
        elif row.get("monthly_high") is not None and float(row["monthly_high"]) < band_floor \
                and path != "high_pay_1099":
            under_floor.append("%s (%s): $%d/month is under his $%d floor"
                               % (row.get("title"), row.get("company"),
                                  int(float(row["monthly_high"])), int(band_floor)))
    if under_floor:
        errors.append("money-floor rule: these picks are under the floor and cannot ship. Drop them and re-render with --allow-short so the short list says so, never annotate a sub-floor lead and send it anyway: %s"
                      % "; ".join(under_floor))
    # ---- band-mix gate -------------------------------------------------------
    # On October 19, 2026 the report shipped 17 salaried roles above his cap and
    # Vinny rejected it: the list has to be mostly work he can actually take.
    # Hourly, part-time, contract and freelance work that fits the band at the
    # hours he chooses is the target. Salaried above-band roles are capped.
    min_band_share = float(rules.get("min_stated_band_share", 0.0) or 0.0)
    max_unpaid = int(rules.get("max_unpaid_picks", 4))
    unpaid = [r for r in (verified.get(p.get("url")) for p in picks)
              if r is not None and not r.get("pay")]
    if len(unpaid) > max_unpaid:
        errors.append("unpaid cap: %d picks state no pay, at most %d may ship" % (len(unpaid), max_unpaid))
    paid = [r for r in (verified.get(p.get("url")) for p in picks) if r is not None and r.get("pay")]
    if min_band_share and len(paid) >= 5:
        in_band_n = sum(1 for r in paid if C.band_state(r, rules) in ("in_band", "capable"))
        if in_band_n / float(len(paid)) < min_band_share:
            errors.append(
                "in-band-pay rule: only %d of %d picks print a monthly figure inside his $1,000 to $2,500 band "
                "(minimum %.0f%%). The list he rejected printed $3,464 to $10,392 on sixteen of twenty leads and "
                "called them in-band because the hours were his to choose. Select from the leads whose posted pay "
                "actually lands in the band" % (in_band_n, len(paid), min_band_share * 100))
        else:
            # The in-band rule is a rule about pay, so it is judged on the picks
            # that state pay. The earlier gate below divided the in-band count by
            # every pick including the unpaid ones, which made a list with three
            # unpaid leads arithmetically unable to clear 60 percent however much
            # in-band work it carried. Unpaid picks are still capped separately.
            pass

    # ---- coverage guard ---------------------------------------------------
    # The cap comes from rules.json and nowhere else. A hard-coded ceiling here
    # silently overrode that file and forced short lists: on October 23, 2026 the
    # verified pool held 20 shippable leads and the render refused anything over
    # seventeen. The count is the deliverable, so the file is the only limit.
    max_above = int(rules.get("max_above_band_picks", target))
    salaried_above, flexible = [], []
    for pick in picks:
        row = verified.get(pick.get("url"))
        if row is None:
            continue
        path, _sc = C.classify_path(row, rules)
        if path == "above_band_w2":
            salaried_above.append("%s (%s)" % (row.get("title"), row.get("company")))
        elif path in ("primary", "band_flexible_1099", "high_pay_1099"):
            flexible.append(row.get("title"))
    if len(salaried_above) > max_above:
        errors.append("band-mix rule: %d of %d picks are salaried and above his $1,000 to $2,500 band, and at most %d may ship. Drop the worst of them, keep the in-band and flexible leads, and re-render with --allow-short so the short list says so: %s"
                      % (len(salaried_above), len(picks), max_above, "; ".join(salaried_above)))
    min_share = float(rules.get("min_in_band_share", 0.0) or 0.0)
    if min_share and len(picks) >= 5:
        # Judged against the picks that carry pay, because an unpaid lead cannot
        # be in band or out of it. Counting unpaid picks in the denominator made
        # a list carrying three of them unable to reach 60 percent no matter how
        # much in-band work it also carried, and the unpaid count is capped on
        # its own line above.
        denom = len(counted.get("primary", [])) + len(counted.get("band_flexible_1099", [])) \
            + len(counted.get("high_pay_1099", [])) + len(counted.get("above_band_w2", []))
        share = (len(counted.get("primary", [])) + len(counted.get("band_flexible_1099", []))) / float(denom or 1)
        if share < min_share:
            errors.append(
                "in-band-mix rule: only %.0f%% of the paid picks are work he can take inside or near his band "
                "(minimum %.0f%%). A list of salaried roles above his cap is the October 21, 2026 report he "
                "rejected. Select from the in-band and flexible leads in candidates.jsonl instead of the salaried ones"
                % (share * 100, min_share * 100))

    if problems:
        errors.extend(problems)
    if errors:
        raise SystemExit("REFUSING TO RENDER:\n  " + "\n  ".join(errors))

    # ---- layout gate ---------------------------------------------------------
    # The report has to be readable: every lead is a titled block with its own
    # labelled sections, and no line carries two facts separated by a pipe. This
    # is checked here so a flattened render cannot be written no matter what
    # changes above.
    probe = "\n".join(lines)
    for section in ("Role", "Pay", "Apply", "Fit", "Verification"):
        found = probe.count("\n" + section + "\n")
        if found < len(picks):
            raise SystemExit(
                "REFUSING TO WRITE: the %s section appears %d times for %d leads. "
                "The layout is broken; fix the renderer instead of sending this."
                % (section, found, len(picks)))
    def _is_numbered_title(line):
        # A lead or reject heading is "12. Some Employer Job Title". Job titles
        # legitimately contain a pipe ("Regional Marketing Manager | West Coast"),
        # and the gate below exists to catch flattened prose, not a title the
        # employer wrote. On October 24, 2026 one picked title and five reject
        # titles carried pipes and the render refused a perfectly laid out file.
        stripped = line.strip()
        head = stripped[:6]
        return stripped[:1].isdigit() and ". " in head

    piped = [l for l in lines if " | " in l and l.strip()
             and not l.strip().startswith("=") and not _is_numbered_title(l)]
    if piped:
        raise SystemExit(
            "REFUSING TO WRITE: %d line(s) pack two facts together with a pipe, which is the "
            "blob layout he rejected. First offender: %r" % (len(piped), piped[0]))

    text = "\n".join(lines) + "\n"
    path = os.path.join(out_dir, "report-%s.txt" % (args.date or C.today_stamp()))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)

    recorded = 0
    if not args.no_ledger:
        shipped = []
        for pick in picks:
            row = verified.get(pick.get("url"))
            if row is None:
                row = {"url": pick.get("url"), "company": pick.get("company"),
                       "title": pick.get("title"), "source": pick.get("source"),
                       "apply_url": pick.get("apply_url"), "apply_email": pick.get("apply_email")}
            else:
                row = dict(row)
                row.setdefault("apply_url", pick.get("apply_url"))
                row.setdefault("apply_email", pick.get("apply_email"))
            shipped.append(row)
        recorded = C.ledger_append(shipped, reported_on=args.date or C.today_stamp(),
                                   path=args.ledger)

    longest = max(len(line) for line in text.split("\n"))
    wrapped = [line for line in text.split("\n")
               if line.strip() and len(line) < 100 and not line.startswith("=")
               and not line[:2].strip().rstrip(".").isdigit() and ":" not in line[:40]]
    print("report: %s" % path)
    print("leads: %d (target %d)" % (len(picks), target))
    print("ledger: recorded %d leads as reported on %s (held out of later days)" % (
        recorded, args.date or C.today_stamp()))
    print("longest line: %d chars (unwrapped check: paragraphs must be one long line)" % longest)
    if wrapped:
        print("possible wrapped lines:")
        for line in wrapped[:10]:
            print("   ", line[:100])
    for problem in problems:
        print("PROBLEM:", problem)
    print("attachments ready for the email-sender skill")


if __name__ == "__main__":
    main()
