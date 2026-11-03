"""Stage 2b: give every candidate a direct employer apply path.

The aggregators do not expose the employer's application link: Himalayas points
its Apply button at its own signup, RemoteOK's redirect lands back on RemoteOK,
and WWR's points at its registration page. Left alone those rows are dropped by
verify.py as "no direct application path", which is how in-band work vanished
from the list even when it existed.

This stage takes each candidate with a missing or board-hosted apply path,
finds the employer's own posting through DuckDuckGo Lite, confirms the page by
reading it, and writes the resolved URL back into candidates.jsonl.

Usage:
    python resolve_employer.py [--date YYYY-MM-DD] [--limit 250] [--workers 4]
"""

import argparse
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from urllib.parse import parse_qs, unquote, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

try:
    from scrapling.fetchers import Fetcher
except Exception:  # pragma: no cover - scrapling is the 3.11 install
    Fetcher = None

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"}

BOARD_HOSTS = (
    "himalayas.app", "remoteok.com", "remotive.com", "weworkremotely.com", "jobicy.com",
    "workingnomads.com", "arbeitnow.com", "nodesk.co", "jobspresso.co", "hnrss.org",
    "news.ycombinator.com", "wayup.com", "simplyhired.com", "indeed.com", "linkedin.com",
    "glassdoor.com", "ziprecruiter.com", "monster.com", "careerbuilder.com", "dailyremote.com",
    "builtin.com", "jobright.ai", "jobgether.com", "makely.tech", "remotesource.com",
    "flexjobs.com", "opentoworkremote.com", "workfromanywhere.app", "diversityjobs.com",
    "talent.com", "dice.com", "remoterocketship.com", "realjobsfromanywhere.com",
    "helpwelp.com", "jobera.com", "visa-hunt.com", "expertini.com", "jobted.com",
    "careerjet.com", "jobrapido.com", "neuvoo.com", "jooble.org", "adzuna.com",
    "learn4good.com", "jobsxl.com", "jobseeker.com", "trabajo.org", "joboma.com",
    "hiring.cafe", "jobs.com", "recruitee.com", "workatastartup.com", "flexes.work",
)

ATS_HOSTS = (
    "greenhouse.io", "lever.co", "ashbyhq.com", "workable.com", "breezy.hr", "icims.com",
    "myworkdayjobs.com", "workday.com", "dayforcehcm.com", "zohorecruit.com",
    "smartrecruiters.com", "careers-page.com", "jobvite.com", "bamboohr.com",
    "paylocity.com", "ultipro.com", "rippling.com", "taleo.net", "recruiterbox.com",
)


def clean(text):
    return re.sub(r"[^a-z0-9 ]", " ", (text or "").lower())


def is_board(url):
    host = urlparse(url).netloc.lower()
    return any(h in host for h in BOARD_HOSTS)


def bing(query):
    """Bing RSS search. Returns [(title, url)] in result order."""
    url = "https://www.bing.com/search?q=%s&format=rss" % requests.utils.quote(query)
    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=25)
            if r.status_code != 200:
                time.sleep(1.2 * (attempt + 1))
                continue
            root = ET.fromstring(r.content)
            out = []
            for item in root.iter("item"):
                link = (item.findtext("link") or "").strip()
                title = item.findtext("title") or ""
                if link:
                    out.append((unescape(title), unescape(link)))
            return out
        except Exception:
            time.sleep(1.2 * (attempt + 1))
    return []


def ddg(query):
    """DuckDuckGo Lite search. Returns [(title, url)] in result order."""
    try:
        from scrapling.fetchers import Fetcher
    except Exception:
        return []
    url = "https://lite.duckduckgo.com/lite/?q=" + requests.utils.quote(query)
    try:
        page = Fetcher.get(url, timeout=25)
    except Exception:
        return []
    out = []
    for href in page.css("a::attr(href)").getall():
        if "uddg=" not in href:
            continue
        try:
            qs = parse_qs(urlparse(href if href.startswith("http") else "https:" + href).query)
            u = unquote(qs["uddg"][0])
        except Exception:
            continue
        if u.startswith("http"):
            out.append(("", u))
    return out


def search(query):
    seen, out = set(), []
    for title, url in ddg(query):
        if url not in seen:
            seen.add(url); out.append(url)
    for title, url in bing(query):
        if url not in seen:
            seen.add(url); out.append(url)
    return out

def slug_variants(company):
    base = re.sub(r"[^a-z0-9 ]", "", (company or "").lower())
    words = [w for w in base.split() if w not in ("inc", "llc", "ltd", "corp", "corporation", "co", "the", "group", "company")]
    if not words:
        return []
    out = []
    for cand in ("".join(words), "".join(words[:3]), words[0], "-".join(words), "-".join(words[:2])):
        if cand and cand not in out:
            out.append(cand)
    return out[:5]


def title_match(a, b):
    wa = set(re.findall(r"[a-z]{4,}", (a or "").lower()))
    wb = set(re.findall(r"[a-z]{4,}", (b or "").lower()))
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / float(len(wa))


def ats_lookup(company, title):
    """Deterministic: ask the ATS APIs directly, no search engine involved."""
    for slug in slug_variants(company):
        try:
            r = requests.get("https://boards-api.greenhouse.io/v1/boards/%s/jobs" % slug, headers=UA, timeout=12)
            if r.status_code == 200:
                for j in r.json().get("jobs", []):
                    if title_match(title, j.get("title", "")) >= 0.6:
                        return j.get("absolute_url"), "greenhouse board %s matched the title" % slug
        except Exception:
            pass
        try:
            r = requests.get("https://api.lever.co/v0/postings/%s?mode=json" % slug, headers=UA, timeout=12)
            if r.status_code == 200 and isinstance(r.json(), list):
                for j in r.json():
                    if title_match(title, j.get("text", "")) >= 0.6:
                        return j.get("hostedUrl") or j.get("applyUrl"), "lever board %s matched the title" % slug
        except Exception:
            pass
        try:
            r = requests.get("https://api.ashbyhq.com/posting-api/job-board/%s" % slug, headers=UA, timeout=12)
            if r.status_code == 200:
                for j in r.json().get("jobs", []):
                    if title_match(title, j.get("title", "")) >= 0.6:
                        return j.get("jobUrl") or j.get("applyUrl"), "ashby board %s matched the title" % slug
        except Exception:
            pass
    return None

def belongs(url, company):
    """True when the URL is the employer's own page or that employer's ATS posting."""
    host = urlparse(url).netloc.lower()
    if any(h in host for h in BOARD_HOSTS):
        return False
    cflat = re.sub(r"[^a-z0-9]", "", (company or "").lower())
    if not cflat:
        return False
    if any(h in host for h in ATS_HOSTS):
        return cflat[:8] in re.sub(r"[^a-z0-9]", "", url.lower())
    return cflat[:10] in re.sub(r"[^a-z0-9]", "", host)


def score_url(url, company, title):
    host = urlparse(url).netloc.lower()
    slug = re.sub(r"[^a-z0-9]", "", url.lower())
    score = 0
    cslug = re.sub(r"[^a-z0-9]", "", company.lower())
    if cslug and cslug[:12] in slug:
        score += 2
    if any(h in host for h in ATS_HOSTS):
        score += 2
    words = [w for w in re.findall(r"[a-z]{4,}", clean(title))]
    score += sum(1 for w in words if w in slug) / max(1, len(words))
    return score


def confirm(url, company, title):
    """Return (ok, evidence) after reading the page.

    A page only counts when it belongs to the employer: either an ATS host that
    carries the employer's posting, or a host that names the company. An
    aggregator that merely repeats the title is not an apply path.
    """
    host = urlparse(url).netloc.lower()
    flat = url.lower().replace("-", "").replace("/", "")
    cslug = re.sub(r"[^a-z0-9]", "", company.lower())
    on_ats = any(h in host for h in ATS_HOSTS)
    own_domain = bool(cslug) and cslug[:10] in host.replace("-", "")
    # an ATS page must still belong to this employer: the board path or slug
    # has to name the company, otherwise it is someone else's posting
    ats_matches_company = bool(cslug) and cslug[:8] in flat
    if not own_domain and not (on_ats and ats_matches_company):
        return False, "host is neither the employer nor that employer's ATS posting"
    words = [w for w in re.findall(r"[a-z]{4,}", clean(title))]
    slug = url.lower()
    slug_hits = sum(1 for w in words if w in slug)
    try:
        r = requests.get(url, headers=UA, timeout=15, allow_redirects=True)
        body = clean(re.sub(r"<[^>]+>", " ", r.text))
        page_hits = sum(1 for w in words if w in body)
    except Exception:
        page_hits = 0
    need = max(2, len(words) // 2)
    if page_hits >= need:
        return True, "page text matched %d/%d title words" % (page_hits, len(words))
    # a JS-rendered ATS page carries no text in the raw HTML; the URL slug does
    if slug_hits >= need and on_ats:
        return True, "ATS url slug matched %d/%d title words (page is client-rendered)" % (slug_hits, len(words))
    return False, "no confirmation"


def resolve(row):
    company = (row.get("company") or "").strip()
    title = (row.get("title") or "").strip()
    if not company or not title:
        return None
    hit = ats_lookup(company, title)
    if hit and hit[0]:
        return hit
    queries = [
        "%s %s job" % (company, title),
        "%s %s apply" % (company, title.split("(")[0].strip()),
        '"%s" "%s"' % (title, company),
    ]
    seen = set()
    for q in queries:
        for url in search(q)[:14]:
            if url in seen or not belongs(url, company):
                continue
            seen.add(url)
            ok, why = confirm(url, company, title)
            if ok:
                return url, why
        time.sleep(0.4)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=None)
    args = ap.parse_args()

    params = C.config("params.json")
    if args.limit is None:
        args.limit = int(params.get("resolve_limit", 250))
    if args.workers is None:
        args.workers = int(params.get("resolve_workers", 4))

    run = C.run_dir(args.date)
    path = os.path.join(run, "candidates.jsonl")
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    targets = [r for r in rows if not r.get("apply_url") or is_board(r.get("apply_url", ""))]
    targets = [r for r in targets if not r.get("apply_email")]
    targets = targets[: args.limit]
    print("candidates %d, missing a direct apply path %d, resolving %d" % (len(rows), len(targets), len(targets)))

    by_key = {}
    resolved = 0

    def work(r):
        return r, resolve(r)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for i, (row, hit) in enumerate(pool.map(work, targets)):
            if hit:
                row["apply_url"] = hit[0]
                row["apply_resolved"] = hit[1]
                by_key[row.get("key") or row.get("url")] = row
                resolved += 1
                print("  resolved %-28s %s" % ((row.get("company") or "")[:28], hit[0][:110]), flush=True)
            if i % 20 == 0:
                print("  progress %d/%d resolved %d" % (i, len(targets), resolved), flush=True)

    for r in rows:
        k = r.get("key") or r.get("url")
        if k in by_key:
            r["apply_url"] = by_key[k]["apply_url"]
            r["apply_resolved"] = by_key[k]["apply_resolved"]
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("resolved %d of %d, wrote %s" % (resolved, len(targets), path))


if __name__ == "__main__":
    main()
