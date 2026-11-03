"""Stage 1: pull raw postings from every enabled source into raw.jsonl.

Usage:
    python collect.py [--date YYYY-MM-DD] [--only remoteok,wwr] [--limit 300]

Sources and per-run search terms come from the skill's config directory
(config/sources.json and config/params.json), which the agent writes before a run.
"""

import argparse
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

DESC_CAP = 6000


def norm_title(company, title):
    text = title or ""
    if company and text.lower().startswith(company.lower()):
        text = text[len(company):]
    return text.lstrip(" :-–|").strip() or (title or "")


def record(source, title, company, url, **extra):
    row = {
        "source": source,
        "source_id": str(extra.pop("source_id", "") or ""),
        "title": (title or "").strip(),
        "company": (company or "").strip(),
        "url": (url or "").strip(),
        "apply_url": "",
        "posted": extra.pop("posted", None),
        "location": (extra.pop("location", "") or "").strip(),
        "employment_type": (extra.pop("employment_type", "") or "").strip(),
        "pay_raw": (extra.pop("pay_raw", "") or "").strip(),
        "description": C.strip_html(extra.pop("description", ""))[:DESC_CAP],
        "tags": extra.pop("tags", []) or [],
        "extra": extra,
    }
    hint = extra.pop("apply_url_hint", "") or ""
    link, email, count = C.pick_apply_target(row["description"])
    # Never fall back to the board's own listing URL. A listing page is not an
    # application path; it is the signup wall. No direct target means the lead
    # has no usable apply path and must be dropped downstream, not shipped.
    target = hint or link
    if target and C.is_aggregator_url(target):
        target = ""
    row["apply_url"] = target
    row["apply_email"] = email
    row["extra"]["apply_link_count"] = count
    row["age_days"] = C.age_days(row["posted"])
    row["pay"] = (C.parse_pay(row["pay_raw"])
                  or C.parse_pay(row["description"][:1500])
                  or C.find_pay_in_page(row["description"]))
    return row

# --------------------------------------------------------------- adapters

def s_remoteok(src, params):
    _, _, body = C.fetch(src["url"], ua=C.CONTACT_UA)
    data = json.loads(body)
    out = []
    for item in data:
        if not item.get("id") or not item.get("position"):
            continue
        pay = item.get("salary") or ""
        if not pay and (item.get("salary_min") or item.get("salary_max")):
            pay = "$%s-$%s per year" % (item.get("salary_min"), item.get("salary_max"))
        out.append(record(
            "remoteok", item.get("position"), item.get("company"),
            "https://remoteok.com/remote-jobs/" + item.get("slug", ""),
            source_id=item.get("id"), posted=item.get("date"),
            location=item.get("location") or "Remote", employment_type="",
            pay_raw=pay, description=item.get("description", ""),
            tags=item.get("tags") or [], apply_url_hint=item.get("apply_url", ""),
        ))
    return out


def s_remotive(src, params):
    out = []
    for term in params.get("terms") or [""]:
        url = src["url"] + ("&search=%s" % term.replace(" ", "%20") if term else "")
        _, _, body = C.fetch(url, ua=C.CONTACT_UA)
        data = json.loads(body)
        for item in data.get("jobs", []):
            out.append(record(
                "remotive", item.get("title"), item.get("company_name"), item.get("url"),
                source_id=item.get("id"), posted=item.get("publication_date"),
                location=item.get("candidate_required_location"),
                employment_type=item.get("job_type"), pay_raw=item.get("salary", ""),
                description=item.get("description", ""), tags=item.get("tags") or [],
                category=item.get("category", ""),
            ))
    return out


def s_jobicy(src, params):
    out = []
    terms = params.get("terms") or [""]
    tags = params.get("jobicy_tags") or (params.get("extra_search_phrases") or [])[:10]
    for term in list(terms) + list(tags):
        url = src["url"] + "&geo=usa" + ("&tag=%s" % term.replace(" ", "%20") if term else "")
        try:
            _, _, body = C.fetch(url, ua=C.CONTACT_UA)
            data = json.loads(body)
        except Exception:
            continue
        for item in data.get("jobs", []):
            pay = ""
            if item.get("annualSalaryMin") or item.get("annualSalaryMax"):
                pay = "$%s-$%s per year" % (item.get("annualSalaryMin") or "?",
                                            item.get("annualSalaryMax") or "?")
            out.append(record(
                "jobicy", item.get("jobTitle"), item.get("companyName"), item.get("url"),
                source_id=item.get("id"), posted=item.get("pubDate"),
                location=item.get("jobGeo"), employment_type=", ".join(item.get("jobType") or []),
                pay_raw=pay, description=item.get("jobDescription") or item.get("jobExcerpt", ""),
                tags=item.get("jobIndustry") or [],
            ))
    return out


def s_himalayas(src, params):
    """Page deep into the Himalayas feed.

    The feed carries over 128k postings and is newest-first. Paging 40 pages
    reads under a day of it, which is why in-band work looked nonexistent.
    This walks offsets up to himalayas_max_offset in parallel and stops once a
    whole batch is older than the age window.
    """
    out = []
    max_offset = int(params.get("himalayas_max_offset", 30000))
    max_age = int(params.get("max_age_days", 30))
    seen = set()
    base = src["url"].split("&limit=")[0]

    def fetch_offset(offset):
        url = "%s&limit=20&offset=%d" % (base, offset)
        for attempt in range(3):
            try:
                _, _, body = C.fetch(url, ua=C.CONTACT_UA)
                return json.loads(body).get("jobs", [])
            except Exception:
                time.sleep(1.0 * (attempt + 1))
        return []

    def is_stale(batch):
        if not batch:
            return False
        stamps = []
        for item in batch:
            p = item.get("pubDate") or item.get("publishedDate")
            if isinstance(p, (int, float)) or (isinstance(p, str) and p.isdigit()):
                stamps.append(int(p))
        if not stamps:
            return False
        age_days = (time.time() - max(stamps)) / 86400.0
        return age_days > max_age

    if max_offset > 0:
        offsets = list(range(0, max_offset, 20))
        batches = []
        with ThreadPoolExecutor(max_workers=8) as pool:
            for offset, jobs in zip(offsets, pool.map(fetch_offset, offsets)):
                batches.append(jobs)
        # keep every batch that still sits inside the age window
        for jobs in batches:
            if is_stale(jobs) and not params.get("himalayas_keep_stale"):
                continue
            for item in jobs:
                key = item.get("guid") or item.get("applicationLink") or item.get("title")
                if key in seen:
                    continue
                seen.add(key)
                pay = ""
                if item.get("minSalary") or item.get("maxSalary"):
                    pay = "$%s-$%s per %s" % (item.get("minSalary") or "?",
                                              item.get("maxSalary") or "?",
                                              item.get("salaryPeriod") or "year")
                out.append(record(
                    "himalayas", item.get("title"), item.get("companyName"),
                    item.get("applicationLink") or item.get("url") or
                    ("https://himalayas.app/companies/%s/jobs" % item.get("companySlug", "")),
                    source_id=key, posted=item.get("pubDate") or item.get("publishedDate"),
                    location=", ".join(item.get("locationRestrictions") or []) or "Remote",
                    employment_type=item.get("employmentType", ""), pay_raw=pay,
                    description=item.get("description") or item.get("excerpt", ""),
                    categories=item.get("categories") or [], seniority=item.get("seniority") or [],
                ))
        return out

    pages = int(params.get("himalayas_pages", 10))
    for page in range(pages):
        offset = page * 20
        url = "%s&limit=20&offset=%d" % (src["url"].split("&limit=")[0], offset)
        try:
            _, _, body = C.fetch(url, ua=C.CONTACT_UA)
            data = json.loads(body)
        except Exception:
            break
        jobs = data.get("jobs", [])
        if not jobs:
            break
        for item in jobs:
            key = item.get("guid") or item.get("applicationLink") or item.get("title")
            if key in seen:
                continue
            seen.add(key)
            pay = ""
            if item.get("minSalary") or item.get("maxSalary"):
                pay = "$%s-$%s per %s" % (item.get("minSalary") or "?",
                                          item.get("maxSalary") or "?",
                                          item.get("salaryPeriod") or "year")
            out.append(record(
                "himalayas", item.get("title"), item.get("companyName"),
                item.get("applicationLink") or item.get("url") or
                ("https://himalayas.app/companies/%s/jobs" % item.get("companySlug", "")),
                source_id=key, posted=item.get("pubDate") or item.get("publishedDate"),
                location=", ".join(item.get("locationRestrictions") or []) or "Remote",
                employment_type=item.get("employmentType", ""), pay_raw=pay,
                description=item.get("description") or item.get("excerpt", ""),
                categories=item.get("categories") or [], seniority=item.get("seniority") or [],
            ))
    return out


def s_arbeitnow(src, params):
    out = []
    for page in (1, 2, 3):
        _, _, body = C.fetch("%s?page=%d" % (src["url"], page), ua=C.CONTACT_UA, max_bytes=4000000)
        data = json.loads(body)
        for item in data.get("data", []):
            if not item.get("remote"):
                continue
            out.append(record(
                "arbeitnow", item.get("title"), item.get("company_name"), item.get("url"),
                source_id=item.get("slug"), posted=item.get("created_at"),
                location=item.get("location"), employment_type=", ".join(item.get("job_types") or []),
                pay_raw="", description=item.get("description", ""), tags=item.get("tags") or [],
            ))
    return out


def _rss(src, params, name, problems=None):
    out = []
    for feed in src.get("feeds") or [src["url"]]:
        status, _, body = C.fetch(feed, ua=C.CONTACT_UA)
        if status != 200 or not body.strip():
            if problems is not None:
                problems.append("%s -> HTTP %s, %d bytes" % (feed, status, len(body)))
            continue
        try:
            root = ET.fromstring(C.clean_xml(body))
        except ET.ParseError as exc:
            if problems is not None:
                problems.append("%s -> parse error %s" % (feed, exc))
            continue
        for item in root.findall(".//item"):
            fields = {child.tag: (child.text or "") for child in item}
            title = fields.get("title", "")
            company = fields.get("company", "") or fields.get("dc:creator", "")
            if not company and ":" in title:
                company, title = title.split(":", 1)
            desc = fields.get("description", "")
            pay = ""
            found = C.parse_pay(C.strip_html(desc))
            if found:
                pay = found["raw"]
            out.append(record(
                name, norm_title(company, title), company, fields.get("link", ""),
                source_id=fields.get("guid", ""), posted=fields.get("pubDate"),
                location=" / ".join(x for x in (fields.get("region"), fields.get("country"),
                                                fields.get("state")) if x),
                employment_type=fields.get("type", ""), pay_raw=pay, description=desc,
                tags=[t.strip() for t in (fields.get("skills") or "").split(",") if t.strip()],
                category=fields.get("category", ""), expires_at=fields.get("expires_at", ""),
            ))
    return out


def s_wwr(src, params):
    problems = []
    out = _rss(src, params, "wwr", problems)
    for line in problems:
        print("    wwr feed problem: %s" % line)
    return out


def s_workingnomads(src, params):
    _, _, body = C.fetch(src["url"], ua=C.CONTACT_UA)
    data = json.loads(body)
    out = []
    for item in data:
        out.append(record(
            "workingnomads", item.get("title"), item.get("company_name"), item.get("url"),
            source_id=item.get("url"), posted=item.get("pub_date"),
            location=item.get("location"), employment_type="",
            pay_raw="", description=item.get("description", ""),
            tags=item.get("tags") or [], category=item.get("category_name", ""),
        ))
    return out


def s_nodesk(src, params):
    return _rss(src, params, "nodesk")


def s_jobspresso(src, params):
    return _rss(src, params, "jobspresso")


def s_hnrss_jobs(src, params):
    return _rss(src, params, "hnrss_jobs")


def s_whoishiring(src, params):
    """Latest 'Ask HN: Who is hiring' thread, top level comments only."""
    _, _, body = C.fetch(
        "https://hn.algolia.com/api/v1/search_by_date?query=%22Ask%20HN%3A%20Who%20is%20hiring%22"
        "&tags=story&hitsPerPage=3", ua=C.CONTACT_UA)
    hits = json.loads(body).get("hits", [])
    stories = [h for h in hits if h.get("title", "").lower().startswith("ask hn: who is hiring")]
    if not stories:
        return []
    thread = stories[0]
    _, _, tree = C.fetch("https://hn.algolia.com/api/v1/items/%s" % thread["objectID"],
                         ua=C.CONTACT_UA, max_bytes=4000000)
    data = json.loads(tree)
    out = []
    cap = int(params.get("per_source_limit", 120))
    for child in data.get("children", [])[:cap]:
        text = C.strip_html(child.get("text") or "")
        if len(text) < 80:
            continue
        header = text.split("\n")[0][:200]
        parts = [p.strip() for p in header.split("|")]
        company = parts[0] if parts else header
        role = parts[1] if len(parts) > 1 else header
        location = parts[2] if len(parts) > 2 else ""
        tail = " | ".join(parts[3:]) if len(parts) > 3 else ""
        pay = ""
        employment = ""
        if tail:
            if re.search(r"[\d$€£]", tail):
                found = C.parse_pay(tail)
                pay = found["raw"] if found else ""
            if not pay:
                employment = tail[:40]
        if len(parts) == 1:
            role = header
        out.append(record(
            "whoishiring", norm_title(company, role), company,
            "https://news.ycombinator.com/item?id=%s" % child.get("id"),
            source_id=child.get("id"), posted=child.get("created_at"),
            location=location, employment_type=employment,
            pay_raw=pay, description=text, tags=["hn", "whoishiring"],
        ))
    return out


def s_ats(src, params):
    """Employer ATS boards, read straight from the vendor APIs.

    This is the direct-apply source class: every row carries the employer's own
    application URL on Greenhouse, Ashby or Lever, so there is no board account
    wall between Vinny and the form. Only remote postings are taken at this
    stage, and each employer is capped so one big board cannot flood the run.
    """
    conf = C.config("companies.json")
    cap = int(params.get("ats_per_company", 40))
    out = []

    for company in conf.get("greenhouse") or []:
        url = "https://boards-api.greenhouse.io/v1/boards/%s/jobs?content=true" % company
        try:
            status, _, body = C.fetch(url, timeout=60, max_bytes=20000000)
            data = json.loads(body)
        except Exception:
            continue
        taken = 0
        for item in data.get("jobs") or []:
            loc = (item.get("location") or {}).get("name") or ""
            if "remote" not in loc.lower():
                continue
            out.append(record(
                "greenhouse:%s" % company, item.get("title"), item.get("company_name") or company,
                item.get("absolute_url"), source_id=item.get("id"),
                posted=item.get("first_published") or item.get("updated_at"),
                location=loc, employment_type="", pay_raw="",
                description=item.get("content") or "", apply_url_hint=item.get("absolute_url"),
            ))
            taken += 1
            if taken >= cap:
                break

    for company in conf.get("ashby") or []:
        url = "https://api.ashbyhq.com/posting-api/job-board/%s" % company
        try:
            status, _, body = C.fetch(url, timeout=45, max_bytes=12000000)
            data = json.loads(body)
        except Exception:
            continue
        taken = 0
        for item in data.get("jobs") or []:
            loc = item.get("location") or ""
            if not (item.get("isRemote") or "remote" in loc.lower()):
                continue
            out.append(record(
                "ashby:%s" % company, item.get("title"), company,
                item.get("jobUrl"), source_id=item.get("id"), posted=item.get("publishedAt"),
                location=loc or "Remote", employment_type=item.get("employmentType") or "",
                pay_raw="", description=item.get("descriptionPlain") or item.get("descriptionHtml") or "",
                apply_url_hint=item.get("applyUrl") or item.get("jobUrl"),
            ))
            taken += 1
            if taken >= cap:
                break

    for company in conf.get("lever") or []:
        url = "https://api.lever.co/v0/postings/%s?mode=json" % company
        try:
            status, _, body = C.fetch(url, timeout=45, max_bytes=12000000)
            data = json.loads(body)
        except Exception:
            continue
        taken = 0
        for item in data if isinstance(data, list) else []:
            loc = ((item.get("categories") or {}).get("location") or "")
            workplace = item.get("workplaceType") or ""
            if "remote" not in (loc + " " + workplace).lower():
                continue
            pay = ""
            sr = item.get("salaryRange") or {}
            if sr.get("min") or sr.get("max"):
                interval = (sr.get("interval") or "").replace("per-", "").replace("-salary", "").replace("-wage", "")
                unit = {"year": "per year", "hour": "per hour", "month": "per month", "day": "per day"}.get(interval, "per year")

                def _fmt(value):
                    value = float(value)
                    return "%d" % value if value >= 1000 else ("%.2f" % value).rstrip("0").rstrip(".")

                lo, hi = sr.get("min"), sr.get("max")
                if lo and hi and float(lo) != float(hi):
                    pay = "$%s-$%s %s" % (_fmt(lo), _fmt(hi), unit)
                elif lo or hi:
                    pay = "$%s %s" % (_fmt(lo or hi), unit)
            out.append(record(
                "lever:%s" % company, item.get("text"), company, item.get("hostedUrl"),
                source_id=item.get("id"), posted=item.get("createdAt"),
                location=loc, employment_type=(item.get("categories") or {}).get("commitment") or "",
                pay_raw=pay, description=item.get("descriptionPlain") or item.get("description") or "",
                apply_url_hint=item.get("applyUrl") or item.get("hostedUrl"),
            ))
            taken += 1
            if taken >= cap:
                break
    return out


WORKABLE_BOARDS = os.path.join(C.CONFIG_DIR, "workable-boards.json")


def workable_boards(params):
    """Poll each cached employer board. Used when the search endpoint is banned.

    jobs.workable.com/api/v1/jobs rate-limits by IP and answers
    {"error":"rate_limit"} for hours, which returned 0 records on October 23, 2026
    and took 41 of that day's 65 usable leads with it. apply.workable.com is a
    different service and keeps working. Boards come from build_workable_boards.py.
    """
    if not os.path.exists(WORKABLE_BOARDS):
        return []
    try:
        boards = json.load(open(WORKABLE_BOARDS, encoding="utf-8")).get("boards") or {}
    except Exception:
        return []
    per_acct = int(params.get("workable_per_board", 60))
    pause = float(params.get("workable_board_sleep", 1.2))
    out = []
    for company, slug in boards.items():
        url = "https://apply.workable.com/api/v1/widget/accounts/%s?details=true" % slug
        data = None
        for attempt in range(3):
            try:
                status, _, body = C.fetch(url, ua=C.CONTACT_UA, timeout=45)
                if status == 429:
                    # The widget service rate-limits the whole IP, not the slug.
                    # Sweeping every remaining board against a 429 burns the
                    # run's clock and looks like abuse, so stop the sweep; the
                    # next run re-reads the boards after the limit lifts.
                    print("  workable widget endpoint rate-limited (429), "
                          "stopping the board sweep after %d boards" % len(out), flush=True)
                    return out
                if status == 200:
                    data = json.loads(body)
                    break
            except Exception:
                pass
            time.sleep(3 + attempt * 4)
        if not isinstance(data, dict):
            time.sleep(pause)
            continue
        for item in (data.get("jobs") or [])[:per_acct]:
            if not item.get("telecommuting"):
                continue
            loc = item.get("locations") or [{}]
            country = (loc[0].get("country") if loc else "") or item.get("country") or ""
            location = ", ".join(p for p in (item.get("city"), item.get("state"), country) if p)
            out.append(record(
                "workable", item.get("title"), company,
                item.get("url") or item.get("application_url"),
                source_id=item.get("shortcode") or item.get("url"),
                posted=item.get("published_on"),
                location=(location + " (remote)").strip(", ") or "Remote",
                employment_type=item.get("employment_type") or "",
                pay_raw="", description=item.get("description") or "",
                tags=[item.get("department") or "", "remote"],
                apply_url_hint=item.get("application_url") or item.get("url") or "",
            ))
        time.sleep(pause)
    return out


def s_workable(src, params):
    """Workable's public job-board search API.

    Workable hosts the employer's own application form, so every row is a
    direct-apply row with no board account wall. This is where the part-time,
    contract and freelance writing, editing, SEO and marketing work his spec
    asks for actually lives: the October 17, 2026 list he held up as the better
    one came from exactly this class of employer, and none of it was reachable
    through the aggregator feeds the pipeline used before.

    The API returns 20 rows a page with an opaque pageToken, and `workplace`
    filters server-side, so the run asks for remote rows only and pages two
    deep per term to stay inside a sane request budget.
    """
    base = src.get("url") or "https://jobs.workable.com/api/v1/jobs"
    terms = params.get("workable_terms") or (params.get("terms") or ["writer"])[:8]
    pages = int(params.get("workable_pages", 2))
    per_term = int(params.get("workable_per_term", 20))
    out, seen = [], set()
    blocked = bool(params.get("workable_force_boards"))
    if not blocked:
      for term in terms:
        token = None
        for _page in range(pages):
            query = {"query": term, "location": "us", "workplace": "remote"}
            if token:
                query["pageToken"] = token
            url = base + "?" + urlencode(query)
            data = None
            # Workable rate-limits a burst of searches: on October 21, 2026 a full
            # run came back with 20 rows instead of the usual thousand and the whole
            # in-band content supply vanished with it. Retry with backoff, and pause
            # between pages so a scheduled run never looks like a scrape.
            for attempt in range(3):
                try:
                    _, _, body = C.fetch(url, ua=C.CONTACT_UA, timeout=45)
                    data = json.loads(body)
                    if isinstance(data, dict) and data.get("error") == "rate_limit":
                        blocked = True
                        data = None
                        break
                    break
                except Exception:
                    time.sleep(2 + attempt * 3)
            if data is None:
                time.sleep(1.5)
                break
            time.sleep(0.4)
            jobs = data.get("jobs") or []
            for item in jobs:
                job_id = item.get("id") or ""
                if not job_id or job_id in seen:
                    continue
                if (item.get("language") or "en").lower() != "en":
                    continue
                if (item.get("workplace") or "").lower() != "remote":
                    continue
                seen.add(job_id)
                company = (item.get("company") or {}).get("title") or item.get("department") or ""
                loc = item.get("location") or {}
                location = ", ".join(part for part in (
                    loc.get("city"), loc.get("subregion"), loc.get("countryName")) if part)
                if "TELECOMMUTE" in (item.get("locations") or []):
                    location = (location + " (remote)").strip()
                description = "\n".join(part for part in (
                    item.get("description"), item.get("requirementsSection"),
                    item.get("benefitsSection")) if part)
                out.append(record(
                    "workable", item.get("title"), company, item.get("url"),
                    source_id=job_id, posted=item.get("created"),
                    location=location or "Remote",
                    employment_type=item.get("employmentType") or "",
                    pay_raw="", description=description,
                    tags=[item.get("department") or "", item.get("workplace") or ""],
                    apply_url_hint=item.get("url") or "",
                ))
            token = data.get("nextPageToken")
            if not token or len(out) >= per_term * len(terms):
                break
        if blocked:
            break
    if blocked or not out:
        # The search endpoint refused us (or the run forced the fallback). Read
        # the employer boards instead; they are the same employers, on a service
        # that is not banned, and every row carries application_url so the
        # apply-path gate is satisfied without any resolution step.
        print("  workable search endpoint refused (%s), polling %d employer boards"
              % ("rate_limit" if blocked and not params.get("workable_force_boards")
                 else "forced fallback" if blocked else "empty response",
                 _board_count()), flush=True)
        out = workable_boards(params)
    return out


def _board_count():
    try:
        return len(json.load(open(WORKABLE_BOARDS, encoding="utf-8")).get("boards") or {})
    except Exception:
        return 0


def s_smartrecruiters(src, params):
    """SmartRecruiters' public job search, paged, with per-posting detail reads.

    SmartRecruiters hosts the employer's own application form (careers.<company>
    or jobs.smartrecruiters.com/<company>), so every row is a direct-apply row in
    the same class as Workable and the employer ATS boards: no account wall, the
    form is on the employer's own board. Added October 25, 2026, the morning the
    Workable search endpoint rate-limited for the third straight day and Alignerr
    was excluded by Vinny, because his families still live on employer-hosted
    application pages and this search endpoint keeps answering.

    The search endpoint returns up to 100 rows per keyword and IGNORES every
    paging parameter (offset/page/from all return the same first row, verified
    October 25, 2026), so the depth lever is keyword breadth: the baseline walks
    his term lists one keyword each, and the top-up round expands the family
    terms with engagement and seniority modifiers for a second, deeper pass.
    Rows are held to fully remote US postings whose titles match his job
    families and whose release date sits inside the freshness window BEFORE any
    detail read, so the request budget goes to rows his rules can actually keep;
    the unpaged probe the same morning kept 338 raw rows of which 5 survived
    prefilter, and most of the waste was titles outside his direction and stale
    postings. The detail record carries compensation and the posting text, which
    the search result does not.
    """
    base = src.get("url") or "https://jobs.smartrecruiters.com/sr-jobs/search"
    terms = []
    if params.get("smartrecruiters_terms"):
        terms = list(params["smartrecruiters_terms"])
    else:
        for key in ("terms", "workable_terms", "extra_search_phrases"):
            for term in params.get(key) or []:
                if term and term not in terms:
                    terms.append(term)
    modifiers = params.get("smartrecruiters_modifiers") or []
    if modifiers:
        wide = []
        for term in terms:
            for modifier in modifiers:
                combo = "%s %s" % (term, modifier)
                if combo not in wide and combo not in terms:
                    wide.append(combo)
        terms = terms + wide
    request_cap = int(params.get("smartrecruiters_request_cap", 250))
    terms = terms[:request_cap]
    detail_cap = int(params.get("smartrecruiters_detail_cap", 700))
    max_age = float(params.get("max_age_days", 30))
    include = C.config("rules.json").get("include_title_patterns") or []
    period_map = {"YEARLY": "year", "HOURLY": "hour", "MONTHLY": "month",
                  "DAILY": "day", "WEEKLY": "week"}
    out, seen, details = [], set(), 0

    def _fmt(value):
        value = float(value)
        return "%d" % value if value == int(value) else ("%.2f" % value).rstrip("0").rstrip(".")

    def _search(term, offset):
        query = urlencode({"keyword": term, "location": "us", "limit": 100,
                           "offset": offset})
        for attempt in range(2):
            try:
                status, _, body = C.fetch("%s?%s" % (base, query),
                                          ua=C.CONTACT_UA, timeout=30)
                if status == 200 and body:
                    return json.loads(body).get("content") or []
            except Exception:
                pass
            time.sleep(1.0 + attempt)
        return None

    for term in terms:
        items = _search(term, 0)
        if items is None:
            time.sleep(0.35)
            continue
        for item in items:
            jid = item.get("id") or ""
            title = (item.get("name") or "").strip()
            loc = item.get("location") or {}
            if not jid or jid in seen:
                continue
            if not loc.get("remote") or (loc.get("country") or "").lower() != "us":
                continue
            if C.NON_ENGLISH_LANGUAGE_RE.search(title):
                continue
            if not any(re.search(p, title) for p in include):
                continue
            posted = (item.get("releasedDate") or "")[:10]
            age = C.age_days(posted)
            if age is None or age > max_age:
                continue
            seen.add(jid)
            if details >= detail_cap:
                continue
            ident = (item.get("company") or {}).get("identifier") or ""
            detail = None
            for attempt in range(2):
                try:
                    status, _, body = C.fetch(
                        "https://api.smartrecruiters.com/v1/companies/%s/postings/%s"
                        % (ident, jid), ua=C.CONTACT_UA, timeout=30)
                    if status == 200 and body:
                        detail = json.loads(body)
                    break
                except Exception:
                    time.sleep(1.0 + attempt)
            details += 1
            pay = ""
            comp = (detail or {}).get("compensation") or {}
            period = period_map.get((comp.get("period") or "").upper())
            currency = (comp.get("currency") or "USD").upper()
            if period and currency in ("USD", "US$") and (comp.get("min") or comp.get("max")):
                lo, hi = comp.get("min"), comp.get("max")
                if lo and hi and float(lo) != float(hi):
                    pay = "$%s-$%s per %s" % (_fmt(lo), _fmt(hi), period)
                else:
                    pay = "$%s per %s" % (_fmt(lo or hi), period)
            text = ""
            if detail:
                text = "\n".join((s.get("text") or "") for s in
                                 ((detail.get("jobAd") or {}).get("sections") or {}).values()
                                 if isinstance(s, dict))
                if not pay:
                    found = C.find_pay_in_page(text)
                    pay = (found or {}).get("raw") or ""
            loc_text = ", ".join(p for p in (loc.get("city"), loc.get("region"), "US") if p)
            out.append(record(
                "smartrecruiters", title,
                (item.get("company") or {}).get("name") or ident,
                item.get("applyUrl") or "https://jobs.smartrecruiters.com/%s/%s" % (ident, jid),
                source_id=jid, posted=posted,
                location=(loc_text + " (remote)").replace(", ,", ","),
                employment_type=((detail or {}).get("typeOfEmployment") or {}).get("label") or "",
                pay_raw=pay, description=text,
                tags=[ident, "remote"],
                apply_url_hint=item.get("applyUrl") or "",
            ))
        time.sleep(0.35)
    return out


ADAPTERS = {
    "remoteok": s_remoteok,
    "remotive": s_remotive,
    "jobicy": s_jobicy,
    "himalayas": s_himalayas,
    "arbeitnow": s_arbeitnow,
    "ats": s_ats,
    "wwr": s_wwr,
    "workingnomads": s_workingnomads,
    "nodesk": s_nodesk,
    "jobspresso": s_jobspresso,
    "hnrss_jobs": s_hnrss_jobs,
    "whoishiring": s_whoishiring,
    "workable": s_workable,
    "smartrecruiters": s_smartrecruiters,
}

# -------------------------------------------------------------------- main

# Extra rows harvested into the run directory by an earlier collection attempt
# the same day (the widen and harvest scripts write here when a run has to
# improvise). Collection merges them instead of re-paying the API for the same
# postings; a fresh day's directory holds none of these files and the merge is a
# no-op.
SIDE_FILES = {
    "workable": ("workable_boards_extra.jsonl",),
    "smartrecruiters": ("smartrecruiters.jsonl", "smartrecruiters_broad.jsonl"),
}


def _side_rows(out_dir, name, rows, extra_dirs=()):
    """Append side-harvest rows for a source, deduped by url.

    Same-day files first, then the previous day's run directory: a harvest an
    earlier attempt improvised (Workable boards read before the widget endpoint
    went 429, a SmartRecruiters pass) is still supply, and the next morning's
    run inherits it instead of re-paying an endpoint that may now be banned.
    """
    wanted = SIDE_FILES.get(name) or ()
    if not wanted:
        return rows
    have = {r.get("url") for r in rows}
    added = 0
    for fname in wanted:
        for directory in (out_dir,) + tuple(extra_dirs):
            path = os.path.join(directory, fname)
            if not os.path.exists(path):
                continue
        try:
            lines = open(path, encoding="utf-8").read().splitlines()
        except Exception:
            continue
        for line in lines:
            try:
                row = json.loads(line)
            except Exception:
                continue
            url = row.get("url") or ""
            if not url or url in have:
                continue
            have.add(url)
            rows.append(row)
            added += 1
    if added:
        print("  merged %d rows from this day's or the previous day's side harvest for %s"
              % (added, name), flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--only", help="comma separated source names (appends to raw.jsonl)")
    ap.add_argument("--limit", type=int, help="max records per source")
    ap.add_argument("--param", action="append", default=[], metavar="KEY=VALUE",
                    help="temporary collection override; never writes config/params.json")
    ap.add_argument("--fresh", action="store_true",
                    help="wipe raw.jsonl first (default on a full run, never with --only)")
    args = ap.parse_args()

    sources = C.config("sources.json").get("sources", {})
    params = C.config("params.json")
    if args.limit:
        params["per_source_limit"] = args.limit
    for item in args.param:
        if "=" not in item:
            raise SystemExit("--param must use KEY=VALUE")
        key, value = item.split("=", 1)
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass
        params[key] = value
    wanted = [s.strip() for s in args.only.split(",")] if args.only else None

    out_dir = C.run_dir(args.date)
    raw_path = os.path.join(out_dir, "raw.jsonl")
    # The previous calendar day's run directory can hold side-harvest rows an
    # earlier attempt wrote; collect merges them as extra supply.
    prev_dirs = []
    try:
        from datetime import datetime as _dt, timedelta as _td
        _stamp = args.date or C.today_stamp()
        prev_dirs.append(os.path.join(
            C.RUN_ROOT, (_dt.strptime(_stamp[:10], "%Y-%m-%d") - _td(days=1)).strftime("%Y-%m-%d")))
    except Exception:
        pass
    prev_dirs = [d for d in prev_dirs if os.path.isdir(d)]
    wipe = args.fresh or not args.only
    if wipe and os.path.exists(raw_path):
        os.remove(raw_path)

    report = []
    total = 0
    for name, src in sources.items():
        if wanted and name not in wanted:
            continue
        if not src.get("enabled", True):
            report.append((name, "disabled", 0))
            continue
        adapter = ADAPTERS.get(src.get("adapter") or name)
        if adapter is None:
            report.append((name, "no adapter", 0))
            continue
        try:
            rows = adapter(src, params)
        except Exception as exc:  # noqa: BLE001 - one bad source must not stop the run
            report.append((name, "FAILED: %s: %s" % (type(exc).__name__, exc), 0))
            continue
        limit = params.get("per_source_limit")
        if limit:
            rows = rows[:int(limit)]
        rows = _side_rows(out_dir, name, rows, extra_dirs=prev_dirs)
        with open(raw_path, "a", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        total += len(rows)
        report.append((name, "ok", len(rows)))

    print("run dir:", out_dir)
    for name, status, count in report:
        print("  %-14s %-40s %4d" % (name, status, count))
    print("raw records:", total, "->", raw_path)


if __name__ == "__main__":
    main()
