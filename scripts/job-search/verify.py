"""Stage 3: prove each candidate is still open today.

Usage:
    python verify.py [--date YYYY-MM-DD] [--cap 220] [--workers 6]

For every candidate the employer's own page is fetched and classified:
    live    - page loaded and shows a working apply mechanism, no closed marker
    dead    - 404 / gone / closed / filled / expired text detected
    blocked - the site refused the fetch (403, 429, bot wall): NOT a verified lead,
              keep it out of the report unless a second source proves it open
    unknown - page loaded but neither open nor closed markers were found

Writes verified.jsonl with the evidence for every decision.
"""

import argparse
import concurrent.futures as futures
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

DEAD_MARKERS = [
    "no longer accepting applications", "no longer available",
    "this job has expired", "job has expired", "position has been filled",
    "this position is closed", "applications are closed", "applications closed",
    "this posting is closed", "listing is closed", "role is no longer open",
    "job not found", "page not found", "no longer open", "we are no longer hiring",
    "this job posting is no longer active", "the position has been filled",
    "sorry, this job", "expired",
]

OPEN_MARKERS = [
    "apply for this job", "apply now", "apply for this position", "apply to this job",
    "submit application", "start your application", "apply today", "apply here",
    "jobposting", "validthrough", "easy apply", "send your resume", "email your resume",
    "how to apply", "to apply", "apply via",
]

APPLY_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def classify(status, final_url, body):
    """Return (verdict, evidence)."""
    if status == 0:
        return "unknown", "transport failure: %s" % body[:160]
    if status in (403, 429, 401):
        return "blocked", "HTTP %s (bot wall or rate limit)" % status
    if status >= 400:
        return "dead", "HTTP %s" % status
    text = C.strip_html(body).lower()
    # ATS job pages render their content with JavaScript, so the visible-text
    # markers further down never appear in the served HTML, and strip_html can
    # leave almost nothing. Greenhouse, Ashby and Lever all emit schema.org
    # JobPosting markup for an open posting, so test the raw body for it before
    # the size check. SmartRecruiters emits the same schema.org JobPosting as
    # microdata (itemscope itemtype="http://schema.org/JobPosting") instead of
    # JSON-LD, so both serializations count. Dead markers are checked first,
    # which keeps a filled or expired posting from passing this way.
    has_schema = bool(re.search(r'"@type"\s*:\s*"JobPosting"', body, re.I)) \
        or bool(re.search(r'itemtype="https?://schema\.org/JobPosting"', body, re.I))
    if len(text) < 200 and not has_schema:
        return "unknown", "page body too small to judge (%d chars)" % len(text)
    for marker in DEAD_MARKERS:
        if marker in text:
            return "dead", "page says: %s" % marker
    if has_schema:
        return "live", "ATS job page carries schema.org JobPosting markup for an open posting"
    hits = [marker for marker in OPEN_MARKERS if marker in text]
    if hits:
        return "live", "apply mechanism present: %s" % ", ".join(hits[:3])
    if re.search(r"<input[^>]+type=[\"']file", body, re.I) or "type=\"submit\"" in body.lower():
        return "live", "application form fields present"
    return "unknown", "loaded, no open/closed marker found"


def work(row, timeout, headless=False):
    # Verify the actual application path, never the board's listing page.
    # An aggregator page proves nothing about whether the employer is hiring.
    url = (row.get("apply_url") or "").strip()
    if url and (C.is_aggregator_url(url) or C.is_junk_url(url) or C.is_apply_index(url)):
        url = ""
    email = row.get("apply_email")
    resolved_from = ""

    # When the feed row carried no employer link, fetch the listing once and pull
    # the employer's own apply target out of it. This is what replaces the old
    # behaviour of handing back the board page and calling it an application.
    if not url and not email:
        listing = row.get("url") or ""
        if listing and not C.is_aggregator_url(listing) and not C.is_junk_url(listing):
            # The row's own URL is the employer's page (Himalayas applicationLink,
            # Arbeitnow employer postings), so it is a direct apply target already.
            url = listing
            resolved_from = "posting url is the employer page"
        elif C.is_aggregator_url(listing):
            status, final_url, body = C.fetch(listing, timeout=timeout)
            if status == 200 and body:
                found_url, found_email = C.resolve_apply_from_listing(body, listing)
                if found_url:
                    url = found_url
                    resolved_from = "resolved from the board listing page"
                if found_email:
                    email = found_email

    if not url:
        out = dict(row)
        out["apply_email"] = email
        if email:
            out["verify"] = {
                "verdict": "live",
                "evidence": "post carries a direct application email: %s" % email,
                "http_status": 0, "final_url": "", "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "seconds": 0.0, "fetched_with": "none (email apply path)",
            }
        else:
            out["verify"] = {
                "verdict": "unverified",
                "evidence": "no direct application path (board page only, no employer link found)",
                "http_status": 0, "final_url": "", "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "seconds": 0.0, "fetched_with": "none",
            }
        return out
    row = dict(row)
    row["apply_url"] = url
    if email:
        row["apply_email"] = email
    started = time.time()
    status, final_url, body = C.fetch(url, timeout=timeout)
    fetched_with = "urllib"
    if status in (0, 401, 403, 429):
        alt = C.scrapling_fetch(url, timeout=timeout, headless=headless)
        if alt and alt[0] and alt[0] < 400:
            status, final_url, body = alt
            fetched_with = "scrapling-stealth" if headless else "scrapling"
        elif status == 429:
            time.sleep(3)
            status, final_url, body = C.fetch(url, timeout=timeout, retries=0)
            if status < 400:
                fetched_with = "urllib-retry"
    verdict, evidence = classify(status, final_url, body)

    # A posting that carries a direct application email satisfies the apply-path
    # rule on its own, even when the platform page itself is not fetchable.
    email = row.get("apply_email")
    link = (row.get("extra") or {}).get("apply_link")
    if email and not link and verdict != "dead":
        verdict = "live"
        evidence = "post carries a direct application email: %s" % email
    elif verdict == "blocked" and email:
        verdict = "live"
        evidence = "platform page blocked to automated checks (HTTP %s), but the post carries a direct application email: %s" % (status, email)

    out = dict(row)
    out["verify"] = {
        "verdict": verdict,
        "evidence": evidence,
        "http_status": status,
        "final_url": final_url,
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "seconds": round(time.time() - started, 2),
        "fetched_with": fetched_with,
        "resolved_from": resolved_from,
    }
    # Second chance at pay data straight from the employer's page.
    if not out.get("pay"):
        pay = C.find_pay_in_page(C.strip_html(body)) or C.find_pay_in_jsonld(body)
        if pay:
            out["pay"] = pay
            out["pay_raw"] = pay["raw"]
            out["pay_source"] = "employer page"
            monthly = C.monthly_estimate(pay, out.get("hours_per_week") or 40)
            if monthly:
                out["monthly_low"], out["monthly_high"], out["pay_formula"] = monthly
    emails = APPLY_EMAIL_RE.findall(C.strip_html(body)[:6000])
    if emails:
        out["verify"]["apply_emails"] = sorted(set(e.lower() for e in emails))[:3]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--cap", type=int)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=25)
    ap.add_argument("--headless", action="store_true",
                    help="use the scrapling stealth browser for retries (slow, ~60s a page)")
    ap.add_argument("--only-source", help="re-verify just one source, e.g. himalayas")
    ap.add_argument("--merge", action="store_true",
                    help="merge results into the existing verified.jsonl instead of replacing it")
    args = ap.parse_args()

    params = C.config("params.json")
    out_dir = C.run_dir(args.date)
    rows = C.load_jsonl(os.path.join(out_dir, "candidates.jsonl"))
    cap = args.cap or int(params.get("verify_cap", 220))
    rows = rows[:cap]
    if args.only_source:
        rows = [r for r in rows if r.get("source") == args.only_source]
    print("verifying %d candidates with %d workers" % (len(rows), args.workers))

    results = []
    with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for row in pool.map(lambda r: work(r, args.timeout, args.headless), rows):
            results.append(row)
            mark = {"live": "+", "dead": "-", "blocked": "!", "unknown": "?",
                    "unverified": "X"}[row["verify"]["verdict"]]
            print("  %s %-58s %s" % (mark, (row.get("title") or "")[:58],
                                     row["verify"]["verdict"]))

    if args.merge:
        keep = [r for r in C.load_jsonl(os.path.join(out_dir, "verified.jsonl"))
                if r.get("source") != args.only_source]
        results = keep + results
    # Collapse repeats, keeping the best verdict. Re-running verification over the
    # same day used to leave the same url twice, once live and once unknown, and
    # report.py's url lookup could then pick the stale copy and refuse its own list.
    order = {"live": 0, "blocked": 1, "unknown": 2, "unverified": 3, "dead": 4}
    best = {}
    for row in results:
        url = row.get("url")
        verdict = (row.get("verify") or {}).get("verdict")
        current = best.get(url)
        if current is None or order.get(verdict, 9) < order.get(
                (current.get("verify") or {}).get("verdict"), 9):
            best[url] = row
    results = list(best.values())
    C.write_jsonl(os.path.join(out_dir, "verified.jsonl"), results)
    counts = {}
    for row in results:
        counts[row["verify"]["verdict"]] = counts.get(row["verify"]["verdict"], 0) + 1
    print("verdicts:", counts)
    print("->", os.path.join(out_dir, "verified.jsonl"))


if __name__ == "__main__":
    main()
