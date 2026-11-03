"""Shared helpers for the remote-jobs-search skill. Standard library only."""

import glob
import html
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
CONTACT_UA = "VinnyJobSearch/1.0 (+contact hello@example.com)"

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(SKILL_DIR, "config")
RUN_ROOT = os.path.join(os.path.expanduser("~"), "job-search")

AGGREGATOR_HOSTS = (
    "remoteok.com", "remotive.com", "jobicy.com", "himalayas.app", "weworkremotely.com",
    "nodesk.co", "jobspresso.co", "news.ycombinator.com", "workingnomads.com",
    "arbeitnow.com", "linkedin.com", "twitter.com",
    "x.com", "facebook.com", "instagram.com", "youtube.com", "medium.com",
    "indeed.com", "glassdoor.com", "ziprecruiter.com", "builtin.com", "wellfound.com",
    "google.com", "bit.ly", "t.co",
)


def is_aggregator_url(url):
    """True when a URL points at a job board rather than the employer.

    A board page is a listing, not an application path: it usually wants an
    account before it shows the employer's form, and Vinny will not spend
    thirty minutes signing up to get a lead. Only the employer's own page, an
    ATS hosted for that employer, or a direct application email counts.
    """
    if not url:
        return False
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().replace("www.", "")
    if not host:
        return True
    for blocked in AGGREGATOR_HOSTS:
        if host == blocked or host.endswith("." + blocked):
            return True
    # A board can serve any country domain: arbeitnow.ch and arbeitnow.fr are the
    # same board as arbeitnow.com, and their posting URLs are not employer pages.
    for token in BOARD_TOKENS:
        if token in host:
            return True
    return False


BOARD_TOKENS = (
    "jobicy", "remoteok", "weworkremotely", "himalayas", "nodesk", "jobspresso",
    "workingnomads", "arbeitnow", "remotive", "indeed", "glassdoor", "ziprecruiter",
    "wellfound", "builtin", "jooble", "talent.com", "upwork", "contra", "micro1",
    "flexjobs", "freelancer", "peopleperhour", "toptal",
)

# Postings that require native fluency in a language Vinny does not have. They are
# real jobs and the wrong jobs for him, so they are dropped on the title rather
# than shipped and explained away. Alignerr alone published 5,667 of them.
NON_ENGLISH_LANGUAGE_RE = re.compile(
    r"(?i)\b(dutch|german|french|spanish|italian|portuguese|japanese|korean|mandarin|"
    r"chinese|cantonese|hindi|urdu|arabic|russian|polish|turkish|vietnamese|thai|"
    r"indonesian|malay|tagalog|filipino|swedish|norwegian|danish|finnish|greek|"
    r"hebrew|romanian|ukrainian|serbian|czech|hungarian|bulgarian|flemish|afrikaans|"
    r"bengali|tamil|telugu|punjabi|gujarati|swahili|farsi|persian)\b")


JUNK_URL_TOKENS = (
    "privacy", "terms", "cookie", "legal", "unsubscribe", "login", "signin",
    "sign-in", "register", "life-at", "about-us", "contact-us", "newsroom",
    "/blog", "/press", "job-seekers", "jobseekers", "career-services", "premium",
)


def is_junk_url(url):
    """Pages that are never an application form, however they were found."""
    if not url:
        return True
    low = url.lower()
    return any(token in low for token in JUNK_URL_TOKENS)


FREE_MAIL_DOMAINS = ("gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
                     "protonmail.com", "proton.me", "icloud.com", "mail.com", "gmx.com",
                     "yandex.com", "zoho.com")


def is_free_mail(email):
    return (email or "").lower().split("@")[-1].strip() in FREE_MAIL_DOMAINS


def has_direct_apply(row):
    """A lead is applicable only with a usable employer URL or a direct email.

    A free-mail address does not count on its own: the posting gives no way to
    tie that mailbox to the employer, which is the scam shape the skill warns
    about. A URL that passes the board and junk filters still counts.
    """
    apply_url = (row.get("apply_url") or "").strip()
    if apply_url and not is_aggregator_url(apply_url) and not is_junk_url(apply_url) \
            and not is_apply_index(apply_url):
        return True
    email = (row.get("apply_email") or "").strip()
    return bool(email) and not is_free_mail(email)


APPLY_INDEX_PATHS = (
    "", "/careers", "/career", "/careers/", "/jobs", "/job", "/join", "/join-us",
    "/work-with-us", "/hiring", "/employment", "/company/careers", "/careers/jobs",
    "/about/careers", "/en/careers", "/careers/home", "/jobs/all", "/open-roles",
    "/openings", "/vacancies", "/opportunities",
)


def is_apply_index(url):
    """True when the link is a careers index rather than one job's application.

    mercor's Himalayas rows resolved to https://www.mercor.com/careers/, which is
    the company's job index: the reader still has to find the role, so it is not
    an application path and it must not print as one. The October 22, 2026 probe
    caught this after the resolver's search fallback returned the careers page.
    """
    if not url:
        return False
    try:
        # A bare domain root is an index too. The old normalization turned the
        # empty path into "/", which is not in APPLY_INDEX_PATHS, so
        # https://www.complex.com/ and https://blueprintprep.com/ passed as
        # "direct apply" leads on October 22, 2026 and both reached the picks as
        # if the employer had answered with a posting. Only "" is in the tuple;
        # normalize to "" so the homepage is caught.
        path = (urlparse(url).path or "").lower().rstrip("/")
    except ValueError:
        return True
    return path in APPLY_INDEX_PATHS


ANCHOR_RE = re.compile(r"<a\b[^>]*href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", re.I | re.S)


def resolve_apply_from_listing(html_text, listing_url):
    """Pull the employer's own apply link out of a job-board listing page.

    Board pages usually link to the real application target, which the feed or
    API never exposes. One fetch of the listing is enough to get it without
    creating an account. Returns (apply_url, apply_email); either may be empty.
    """
    from urllib.parse import urljoin

    scored = []
    for href, anchor in ANCHOR_RE.findall(html_text or ""):
        url = urljoin(listing_url, html.unescape(href).strip())
        if not url.startswith("http"):
            continue
        if is_aggregator_url(url) or "unsubscribe" in url.lower() or is_junk_url(url):
            continue
        label = strip_html(anchor).lower()
        score = 0
        if re.search(r"apply|application|submit", label):
            score += 4
        host = host_of(url)
        if any(host == h or host.endswith("." + h) for h in ATS_HOSTS):
            score += 5
        if re.search(r"(?i)privacy|terms|cookie|login|sign.?in|share|facebook|twitter", url):
            score -= 6
        if score <= 0:
            continue
        scored.append((score, url))
    scored.sort(key=lambda pair: -pair[0])
    email = ""
    for candidate in scored:
        if candidate[0] >= 4:
            return candidate[1], ""
    url, email, _count = pick_apply_target(strip_html(html_text or ""))
    if url and not is_aggregator_url(url):
        return url, email
    return "", email

ATS_HOSTS = (
    "greenhouse.io", "lever.co", "ashbyhq.com", "workable.com", "bamboohr.com",
    "recruitee.com", "myworkdayjobs.com", "workday.com", "smartrecruiters.com",
    "jobvite.com", "breezy.hr", "rippling.com", "paylocity.com", "icims.com",
    "jazzhr.com", "applytojob.com", "personio.com", "teamtailor.com",
    "workatastartup.com", "adp.com",
)

URL_RE = re.compile(r"https?://[^\s<>\"')\]]+")
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# ---------------------------------------------------------------- run folders

def run_dir(run_date=None, create=True):
    day = run_date or datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(RUN_ROOT, day)
    if create:
        os.makedirs(path, exist_ok=True)
    return path


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def load_jsonl(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def config(name):
    return load_json(os.path.join(CONFIG_DIR, name), {})

# ------------------------------------------------------------------- ledger

LEDGER_PATH = os.path.join(RUN_ROOT, "ledger.jsonl")
APPLIED_CANDIDATES = (
    os.path.join(RUN_ROOT, "applied-jobs.md"),
    os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "applied-jobs.md"),
    os.path.join(os.path.expanduser("~"), "Desktop", "applied-jobs.md"),
)


def lead_key(row):
    return re.sub(r"[^a-z0-9]+", " ", ((row.get("company") or "") + " " + (row.get("title") or "")).lower()).strip()


def dedupe_title(row):
    """Title with a trailing location variant removed.

    The same role posted once per city is one lead, not eight. On October 22,
    2026 a virtual-assistant employer published "Virtual Assistant - Omaha",
    "- Tulsa", "- Milwaukee" and six more, all identical apart from the city in
    the title. Only a suffix that matches the row's own location is stripped,
    so "Senior Content Strategist - Marketing" keeps its department.
    """
    title = row.get("title") or ""
    loc = (row.get("location") or "").split(",")[0].strip()
    if loc and loc.lower() not in ("remote", "us", "usa", "united states", "anywhere",
                                   "worldwide", "telecommute", "north america"):
        title = re.sub(r"(?i)\s*[-\u2013|]\s*%s\s*$" % re.escape(loc), "", title)
    # City and metro acronyms appear as "- DFW", "- SLC", "- NYC" and never as a
    # department name, so an all-caps suffix of two to four letters is a location.
    title = re.sub(r"\s*[-\u2013|]\s*[A-Z]{2,4}\s*$", "", title)
    # Vendor duplicates repeat the same role with a working-arrangement note in
    # parentheses ("Marketing Task Author" and "Marketing Task Author (AI Training)").
    title = re.sub(r"(?i)\s*\((ai training|remote|contract|part[- ]?time|full[- ]?time|"
                   r"freelance|hourly|us|usa|united states)\)\s*$", "", title)
    return title


def dedupe_key(row):
    """Company plus role, ignoring a trailing location variant in the title."""
    return re.sub(r"[^a-z0-9]+", " ",
                  ((row.get("company") or "") + " " + dedupe_title(row)).lower()).strip()


def ledger_path(override=None):
    return override or LEDGER_PATH


def load_ledger(path=None):
    return load_jsonl(ledger_path(path))


def ledger_held(path=None, today=None):
    """Leads already reported on an earlier day: (urls, keys, reported_on by url).

    Entries recorded today are deliberately NOT held, so re-running the same day
    re-examines the same leads instead of returning an empty list. Dedupe is across
    days, which is the thing the daily cron needs.

    Held identities include the apply url and the apply email, not just the feed
    row url, because the same job reaches the pipeline with a different listing url
    on different days. Earlier days' report files and selected.json files are read
    as well, so a lead that shipped without a ledger entry still cannot come back.
    """
    today = today or today_stamp()
    urls, keys, when = set(), {}, {}
    for row in load_ledger(path):
        if row.get("reported_on") == today:
            continue
        for field in ("url", "apply_url", "apply_email"):
            value = row.get(field)
            if value:
                urls.add(value)
                when[value] = row.get("reported_on")
        if row.get("key"):
            keys.setdefault(row["key"], row.get("reported_on"))
    for day_dir in sorted(glob.glob(os.path.join(RUN_ROOT, "*"))):
        day = os.path.basename(day_dir)
        if not re.match(r"\d{4}-\d{2}-\d{2}", day) or day == today:
            continue
        reports = glob.glob(os.path.join(day_dir, "report-*.txt"))
        # A selected.json alone is not proof a lead was reported. On October 25,
        # 2026 the run selected six leads, the cron supervisor killed it before
        # report.py ran, and the next morning's prefilter then held those six
        # out as "already reported" when nothing had ever been sent. Only a day
        # whose report was actually rendered counts as a reported day.
        if not reports:
            continue
        for report in reports:
            try:
                text = open(report, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for value in re.findall(r"^Apply: (\S+)", text, re.M) + re.findall(r"^Apply by email: (\S+)", text, re.M):
                urls.add(value)
                when.setdefault(value, day)
        selected = load_json(os.path.join(day_dir, "selected.json"))
        for pick in (selected or {}).get("picks") or []:
            if pick.get("url"):
                urls.add(pick["url"])
                when.setdefault(pick["url"], day)
    return urls, keys, when



def ledger_append(rows, reported_on=None, path=None):
    """Record shipped leads. Idempotent on (url, reported_on)."""
    path = ledger_path(path)
    reported_on = reported_on or today_stamp()
    existing = {"%s|%s" % (r.get("url"), r.get("reported_on")) for r in load_ledger(path)}
    added = 0
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        for row in rows:
            marker = "%s|%s" % (row.get("url"), reported_on)
            if marker in existing:
                continue
            existing.add(marker)
            fh.write(json.dumps({
                "url": row.get("url"),
                "apply_url": row.get("apply_url"),
                "apply_email": row.get("apply_email"),
                "key": row.get("key") or lead_key(row),
                "company": row.get("company"),
                "title": row.get("title"),
                "source": row.get("source"),
                "pay_raw": row.get("pay_raw") or (row.get("pay") or {}).get("raw"),
                "reported_on": reported_on,
            }, ensure_ascii=False) + "\n")
            added += 1
    return added


def applied_hold(path=None):
    """URLs and company-plus-title keys from an applied-jobs.md style file."""
    paths = [path] if path else [p for p in APPLIED_CANDIDATES if os.path.exists(p)]
    urls, keys = set(), set()
    for candidate in paths:
        if not candidate or not os.path.exists(candidate):
            continue
        with open(candidate, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip(" \t-*#")
                if not line:
                    continue
                for url in URL_RE.findall(line):
                    urls.add(url.rstrip(".,;:"))
                keys.add(re.sub(r"[^a-z0-9]+", " ", line.lower()).strip()[:120])
    return urls, keys

# ------------------------------------------------------------------ fetching

def fetch(url, timeout=25, ua=UA, retries=2, max_bytes=900000):
    """Return (status, final_url, body_text). Status 0 means transport failure."""
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml,application/xml,application/json;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read(max_bytes)
                return resp.status, resp.geturl(), raw.decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read(20000).decode("utf-8", "replace")
            except Exception:
                pass
            return exc.code, url, body
        except Exception as exc:  # noqa: BLE001 - transport level, retry once
            last = exc
            time.sleep(1.5 * (attempt + 1))
    return 0, url, "FETCH_ERROR: %s: %s" % (type(last).__name__, last)


def scrapling_fetch(url, timeout=25, headless=False):
    """Fetch through scrapling when it is importable (it lives in the Python 3.11
    install on this box). Returns (status, url, html) or None.

    Plain Fetcher gets through most bot walls that urllib does not; headless=True
    uses the stealth browser for the ones that still refuse.
    """
    try:
        from scrapling.fetchers import Fetcher, StealthyFetcher
    except Exception:
        return None
    try:
        if headless:
            page = StealthyFetcher.fetch(url, headless=True, network_idle=True,
                                         timeout=max(timeout, 60) * 1000)
        else:
            page = Fetcher.get(url, timeout=timeout)
        body = getattr(page, "html_content", None) or getattr(page, "body", "") or ""
        if isinstance(body, bytes):
            body = body.decode("utf-8", "replace")
        status = getattr(page, "status", 0) or 0
        return int(status), url, str(body)
    except Exception:
        return None

# -------------------------------------------------------------------- text

TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"[ \t\r\f\v]+")


def strip_html(value):
    if not value:
        return ""
    text = str(value)
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", text, flags=re.I)
    text = TAG_RE.sub(" ", text)
    text = html.unescape(text)
    lines = [SPACE_RE.sub(" ", ln).strip() for ln in text.split("\n")]
    return "\n".join(ln for ln in lines if ln).strip()


XML_ENTITIES = {"amp", "lt", "gt", "quot", "apos"}
ENTITY_RE = re.compile(r"&([a-zA-Z][a-zA-Z0-9]*|#[0-9]+|#x[0-9a-fA-F]+);")


def clean_xml(text):
    """Feeds carry HTML entities that strict XML parsers reject; convert them to
    numeric references without touching the five XML built-ins or escaped markup."""
    def repl(match):
        name = match.group(1)
        if name in XML_ENTITIES or name.startswith("#"):
            return match.group(0)
        value = html.unescape(match.group(0))
        if value == match.group(0):
            return "&amp;" + name + ";"
        return "".join("&#%d;" % ord(ch) for ch in value)

    fixed = ENTITY_RE.sub(repl, text)
    return re.sub(r"&(?!#?[a-zA-Z0-9]+;)", "&amp;", fixed)


def host_of(url):
    try:
        from urllib.parse import urlparse
        return (urlparse(url).hostname or "").lower().replace("www.", "")
    except ValueError:
        return ""


def pick_apply_target(text):
    """Best external application URL and email found inside a posting body."""
    JUNK_EMAIL = ("noreply", "no-reply", "donotreply", "donot-reply", "support", "helpdesk",
              "privacy", "legal", "abuse", "postmaster", "webmaster", "copyright",
              "unsubscribe", "press", "security", "compliance", "dpo", "trust", "phishing",
              "vulnerability", "disclosure", "accessibility", "accommodations", "recruiting-ops")
    GOOD_EMAIL = ("jobs", "careers", "hiring", "talent", "apply", "recruit", "hr", "join",
                  "work", "team", "contact")
    urls = []
    for raw in URL_RE.findall(text or ""):
        url = raw.rstrip(".,;:")
        host = host_of(url)
        if not host or host.endswith("linkedin.com") or "unsubscribe" in url.lower():
            continue
        if is_junk_url(url) or is_aggregator_url(url):
            continue
        urls.append((0 if any(host.endswith(h) for h in ATS_HOSTS) else 1, url))
    urls.sort(key=lambda pair: pair[0])
    emails = []
    for raw in EMAIL_RE.findall(text or ""):
        email = raw.lower().strip(".")
        local = email.split("@")[0]
        if email.endswith((".png", ".jpg", ".gif", ".webp", ".svg")):
            continue
        if any(marker in local for marker in JUNK_EMAIL):
            continue
        emails.append((0 if any(marker in local for marker in GOOD_EMAIL) else 1, email))
    emails.sort(key=lambda pair: pair[0])
    return (urls[0][1] if urls else ""), (emails[0][1] if emails else ""), len(urls)

# ------------------------------------------------------------------ pay math

HOURS_PER_WEEK = 40
WEEKS_PER_MONTH = 4.33

RATE_RE = re.compile(
    r"\$\s?(\d[\d,]*(?:\.\d+)?)\s?(k)?"
    # Hyphen, en dash and em dash all appear in employer rate lines. A page
    # printing "$40.00\u2013$70.00 per hour" used to parse as a flat $40 because
    # only the ASCII hyphen was recognised, which under-stated the monthly
    # figure on exactly the part-time and contract work his band depends on.
    r"(?:\s*(?:[-\u2013\u2014]|to)\s*\$?\s?(\d[\d,]*(?:\.\d+)?)\s?(k)?)?"
    r"\s*(?:/|per\s+|an?\s+|each\s+)?"
    r"(hour|hr|hourly|year|yr|annum|annually|month|mo|monthly|week|wk|day|daily|project|article|piece|word|task|gig|video|post|deliverable|batch)?",
    re.I,
)


def _num(value, k_flag):
    if value is None:
        return None
    value = float(value.replace(",", ""))
    # "$70,000k-$80,000k" is a real posting line (Nautilus Solar, Oct 22, 2026)
    # and means $70,000 to $80,000. Multiplying a comma-grouped figure by a
    # thousand printed the role at $5.8 million a month.
    if k_flag and value < 1000:
        value *= 1000
    return value


def parse_pay(text):
    """Find the most probable pay statement. Returns dict or None."""
    if not text:
        return None
    best = None
    rank = {"hour": 6, "month": 5, "week": 4, "day": 3, "year": 2,
            "project": 1, "article": 1, "piece": 1, "word": 0}
    for match in RATE_RE.finditer(text):
        low = _num(match.group(1), match.group(2))
        high = _num(match.group(3), match.group(4))
        unit = (match.group(5) or "").lower()
        if low is None:
            continue
        if high is None:
            high = low
        if not unit:
            # A bare "$500,000" in a job description is usually revenue, ad
            # spend or funding, not pay. On October 22, 2026 two copywriting
            # roles rendered at $41,667 a month because "$500,000+ per month in
            # revenue" and "$1M/month in ad spend" were read as salary. Without
            # an explicit unit the number only counts when a pay label sits
            # beside it and no revenue or spend wording does.
            context = text[max(0, match.start() - 70):match.end() + 100]
            if re.search(r"(?i)\b(revenue|ad spend|spend|sales|arr\b|funding|raised|"
                         r"valuation|budget|turnover|invoic|billion|million in)\b", context):
                continue
            if not re.search(r"(?i)\b(salary|compensation|compensat|pay range|pay rate|"
                             r"rate of|stipend|hourly rate|base pay|day rate|"
                             r"project fee|per (hour|day|week|month|year)|monthly pay)\b", context):
                continue
            if low < 15 or (low < 1000 and "." not in match.group(1)):
                continue
            unit = "year" if low >= 20000 else "hour"
        unit = {
            "hr": "hour", "hourly": "hour", "yr": "year", "annum": "year",
            "annually": "year", "mo": "month", "monthly": "month",
            "wk": "week", "day": "day", "daily": "day",
        }.get(unit, unit)
        if unit == "hour" and (low > 400 or high > 400):
            continue
        if unit == "year" and low < 20000:
            continue
        if unit == "month" and low < 300:
            continue
        if unit == "day" and low < 40:
            continue
        if unit == "week" and low < 100:
            continue
        if unit in ("project", "article", "piece", "word", "task", "gig", "video", "post",
                    "deliverable", "batch") and low < 25:
            continue
        if low <= 0:
            continue
        candidate = {
            "period": unit,
            "min": low,
            "max": high,
            "raw": match.group(0).strip(" ,."),
        }
        if best is None or rank.get(unit, 0) > rank.get(best["period"], 0):
            best = candidate
    return best


def find_pay_in_page(text):
    """Pay extraction tuned for full job pages: look at pay-context sentences
    first, then fall back to the opening of the page."""
    if not text:
        return None
    contexts = re.findall(
        r"(?:salary|compensation|pay range|pay rate|rate for this role|hourly rate|per hour|"
        r"annual salary|base pay|starting salary|compensation range|budget|market range|"
        r"per year|per annum|salary range|total compensation|pay for this role)"
        r"[^.!?\n]{0,220}", text, re.I)
    best = None
    for chunk in contexts:
        found = parse_pay(chunk)
        if found:
            if found["period"] == "hour" or best is None:
                best = found
            if found["period"] == "hour":
                break
    if best:
        return best
    return parse_pay(text[:20000])


def find_pay_in_jsonld(body):
    """Pay from a job page's schema.org JobPosting baseSalary block.

    Ashby and Greenhouse job pages render with JavaScript, so the salary line a
    human sees never reaches strip_html, but the page still carries the
    structured baseSalary the employer publishes. That is the employer's own
    statement of pay, so it counts as stated pay rather than a guess.
    """
    if not body:
        return None
    idx = body.find('"baseSalary"')
    if idx < 0:
        return None
    chunk = body[idx:idx + 700]
    lo = re.search(r'"minValue"\s*:\s*([\d.]+)', chunk)
    hi = re.search(r'"maxValue"\s*:\s*([\d.]+)', chunk)
    if not (lo or hi):
        return None
    unit = re.search(r'"unitText"\s*:\s*"([A-Za-z]+)"', chunk)
    cur = re.search(r'"currency"\s*:\s*"([A-Z]{3})"', chunk)
    low = float(lo.group(1)) if lo else float(hi.group(1))
    high = float(hi.group(1)) if hi else low
    u = (unit.group(1) if unit else "YEAR").lower()
    period = {"year": "year", "month": "month", "hour": "hour",
              "week": "week", "day": "day", "annum": "year"}.get(u, "year")
    currency = cur.group(1) if cur else "USD"
    prefix = "$" if currency == "USD" else currency + " "
    if high != low:
        raw = "%s%s-%s per %s" % (prefix, _fmt(int(round(low))), _fmt(int(round(high))), period)
    else:
        raw = "%s%s per %s" % (prefix, _fmt(int(round(low))), period)
    return {"period": period, "min": low, "max": high, "raw": raw}


def detect_hours(text, default=40):
    """Hours per week implied by a posting. Returns (hours, note)."""
    if not text:
        return default, "assumed %d hrs/wk (posting states no hours)" % default
    low = re.search(r"(\d{1,2})\s*(?:-|to)\s*(\d{1,2})\s*(?:hrs|hours)\s*(?:/|per\s*)?(?:wk|week)",
                    text, re.I)
    single = re.search(r"(\d{1,2})\s*(?:hrs|hours)\s*(?:/|per\s*)?(?:wk|week)", text, re.I)
    if low:
        hours = (int(low.group(1)) + int(low.group(2))) / 2.0
        return hours, "posting states %s-%s hrs/wk" % (low.group(1), low.group(2))
    if single:
        return float(single.group(1)), "posting states %s hrs/wk" % single.group(1)
    if re.search(r"(?i)\bpart[- ]?time\b", text):
        return 20.0, "part-time posting, 20 hrs/wk assumed"
    if re.search(r"(?i)\b(1099|independent contractor|freelance|contractor|per task|"
                 r"per project|gig|flexible hours|set your own hours)\b", text):
        # Freelance and task work is priced by the hour but worked at the hours
        # he chooses. Assuming a 40-hour week turned every $25-40/hr gig into an
        # "above the band" lead and hid the in-band work behind a false number.
        return 20.0, "freelance or task work, 20 hrs/wk assumed at the hours he sets"
    if re.search(r"(?i)\b(full[- ]?time|40 hours)\b", text):
        return 40.0, "full-time posting, 40 hrs/wk assumed"
    return default, "assumed %d hrs/wk (posting states no hours)" % default


def classify_path(row, rules):
    """Which of Vinny's two money paths a lead lands on.

    primary        in band, $1,000 to $2,500 a month gross, protective of the SSI
    high_pay_1099  $80k+ shaped as 1099 contract or freelance work, which he takes
                   when there is no background check or the employer is second-chance
    above_band_w2  salaried above the band: included, but flagged as an insurance tradeoff
    unrated        pay not stated
    """
    paths = rules.get("paths") or {}
    band_max = float(paths.get("primary", {}).get("max_monthly",
                    rules.get("band_max_monthly", 2500)))
    hp = paths.get("high_pay_1099") or {}
    hp_monthly = float(hp.get("min_monthly",
                               float(hp.get("min_annual", 80000)) / 12.0))
    monthly_low, monthly_high = row.get("monthly_low"), row.get("monthly_high")
    if monthly_low is None:
        return "unrated", False

    title = (row.get("title") or "")
    employment = (row.get("employment_type") or "")
    pay = row.get("pay") or {}
    period = (pay.get("period") or "").lower()
    desc_head = (row.get("description") or "")[:1800]
    haystack = " ".join([title, employment, (row.get("pay_raw") or ""), desc_head])
    second_chance = False
    for pattern in rules.get("second_chance_signals") or []:
        if re.search(pattern, haystack):
            second_chance = True
            break

    # ---- engagement shape -------------------------------------------------
    # Reading the word "contract" out of the body alone is wrong. Nearly every
    # salaried US posting mentions contracts somewhere ("contract renewals",
    # "contract negotiations", "this contract", "contract manufacturer"), so the
    # old test classified salaried W-2 roles as 1099 work. On October 21, 2026
    # that silently disabled the salaried-above-band cap in prefilter.py and
    # report.py and produced a report of four salaried roles (Renewals Manager,
    # Solutions Consultant, Junior Data Solutions Architect, Senior Content
    # Writer) instead of the part-time and contract work Vinny asked for.
    # Shape now comes from the structured engagement fields and from explicit
    # self-employment markers, never from a bare "contract" in the prose.
    salaried_marker = bool(re.search(
        r"(?i)\b(full[- ]?time|fulltime|w-?2|salaried|permanent employee|permanent role)\b",
        employment)) or bool(re.search(
        r"(?i)\b(w-?2|salaried|full[- ]?time employee|full[- ]?time position)\b", desc_head))
    strong_contract = bool(re.search(
        r"(?i)\b(1099|independent contractor|freelancer?|contractor|subcontractor|"
        r"contract position|contract role|contract-to-hire|fixed[- ]term contract|"
        r"temporary contract|per task|per project|per assignment|project[- ]based|"
        r"freelance (role|position|contract))\b",
        " ".join([title, employment, desc_head])))
    structured_contract = bool(re.search(
        r"(?i)\b(contract|contractor|temporary|temp|part[- ]?time|parttime|freelance|seasonal)\b",
        employment))
    # Hourly, daily and per-piece pricing is shape evidence on its own: the
    # hours are his to set, which is the whole point of his primary path.
    flexible_period = period in ("hour", "day", "week", "task", "gig", "project",
                                 "article", "piece", "word", "deliverable", "batch")
    contract_shaped = strong_contract or structured_contract or flexible_period
    if salaried_marker and not strong_contract:
        contract_shaped = False

    if monthly_high <= band_max:
        return "primary", second_chance
    if flexible_period and not salaried_marker:
        # Hourly, task and freelance work is in-band capable when the posting is
        # shaped part-time: the rate is fixed and the hours are his to choose, so
        # the band is reached by working fewer hours rather than by finding a
        # different job. The October 17, 2026 list he held up as the better one
        # priced Alignerr at "25-63 paid hours a month" for exactly this reason.
        # A 40-hour hourly role is not that: it is a wage job at full-time hours,
        # so it falls through to the contract and above-band tests below.
        if float(row.get("hours_per_week") or 20) < 30:
            return "primary", second_chance
    if contract_shaped and monthly_high >= hp_monthly:
        return "high_pay_1099", second_chance
    if contract_shaped:
        return "band_flexible_1099", second_chance
    return "above_band_w2", second_chance


def monthly_estimate(pay, hours_per_week=HOURS_PER_WEEK):
    """Return (monthly_low, monthly_high, formula_note) or None."""
    if not pay:
        return None
    low, high = pay["min"], pay["max"]
    period = pay["period"]
    span = ("$%s-$%s" % (_fmt(low), _fmt(high))) if high != low else "$%s" % _fmt(low)
    if period == "hour":
        note = "%s/hr x %d hrs/wk x 4.33 weeks" % (span, hours_per_week)
        ml = low * hours_per_week * WEEKS_PER_MONTH
        mh = high * hours_per_week * WEEKS_PER_MONTH
    elif period == "year":
        note = "%s/yr divided by 12 months" % span
        ml, mh = low / 12.0, high / 12.0
    elif period == "month":
        note = "%s/mo" % span
        ml, mh = low, high
    elif period == "week":
        note = "%s/wk x 4.33 weeks" % span
        ml, mh = low * WEEKS_PER_MONTH, high * WEEKS_PER_MONTH
    elif period == "day":
        note = "%s/day x 21.7 workdays" % span
        ml, mh = low * 21.7, high * 21.7
    else:
        note = "%s per %s (project pricing, not a monthly rate)" % (span, period)
        ml = mh = low
    return ml, mh, note


def _fmt(value):
    if value is None:
        return "?"
    if float(value).is_integer():
        return "{:,}".format(int(value))
    return "{:,.2f}".format(value)


UNIT_WORD = {"hour": "hour", "year": "year", "month": "month", "week": "week",
             "day": "day", "task": "task", "project": "project"}


def band_state(row, rules):
    """Where the printed monthly figure sits against his band.

    in_band   the monthly estimate as posted overlaps $1,000 to $2,500
    above     it starts above the band even at the posting's own hours
    below     it tops out under $1,000
    unrated   no pay stated

    This is deliberately about the number a reader sees, not about whether the
    work could theoretically be trimmed to fit. On October 21, 2026 sixteen of
    twenty leads printed monthly figures of $3,000 to $10,000 while the report
    called them in-band because the hours were his to choose. He reads the
    printed number, and he is right to.
    """
    low, high = row.get("monthly_low"), row.get("monthly_high")
    if low is None or high is None or not row.get("pay"):
        return "unrated"
    band_min = float(rules.get("band_min_monthly", 1000))
    band_max = float(rules.get("band_max_monthly", 2500))
    if float(high) < band_min:
        return "below"
    if float(low) <= band_max:
        return "in_band"
    # Hourly and task work priced above the band at a full week is still in-band
    # work: the rate is fixed and the hours are his. A salaried role at the same
    # figure is not, because the hours are the employer's. That distinction is the
    # whole money rule, and flattening it is what made the October 21 report read
    # as sixteen above-band leads.
    pay = row.get("pay") or {}
    if (pay.get("period") or "").lower() in ("hour", "day", "task", "gig", "project",
                                             "article", "piece", "word", "deliverable",
                                             "batch"):
        employment = (row.get("employment_type") or "").lower()
        if not re.search(r"(full[- ]?time|w-?2|salaried)", employment):
            return "capable"
    return "above"


def resume_profile():
    """Vinny's resume profile, built by scripts/build_resume_profile.py."""
    return config("resume.json") or {}


def resume_fit(row, profile=None):
    """How well a posting matches the resume, scored from its own words.

    The title carries the most weight because a job called "Search Quality
    Evaluator" is not a technical writing job however many times its body says
    content. Anti-signals subtract, so transcription, healthcare, legal, video
    and assistant work cannot win on a stray keyword. Returns an integer; 0 is
    no signal at all.
    """
    profile = profile if profile is not None else resume_profile()
    if not profile:
        return 0
    title = (row.get("title") or "").lower()
    body = (row.get("description") or "")[:6000].lower()
    score = 0
    for phrase, weight in (profile.get("title_weights") or {}).items():
        if phrase in title:
            score += weight
    for phrase, weight in (profile.get("anti_title") or {}).items():
        if phrase in title:
            score -= weight
    seen = 0
    for phrase, weight in (profile.get("body_keywords") or {}).items():
        hits = body.count(phrase)
        if hits:
            score += weight * min(hits, 3)
            seen += 1
    # Matching many distinct topics from the resume beats repeating one word.
    score += min(seen, 12)
    return score


def resume_title_match(row, profile=None):
    """Does the title name one of the roles his resume is written for?"""
    profile = profile if profile is not None else resume_profile()
    title = (row.get("title") or "").lower()
    for phrase, weight in (profile.get("title_weights") or {}).items():
        if weight >= 9 and phrase in title:
            return phrase
    return ""


# Titles that disqualify regardless of how many resume words appear in the body.
# "Mechanical Engineering Expert - AI Content Specialist" matches "ai content" and
# is still a job for a mechanical engineer, not a technical writer.
HARD_ANTI = (
    "mechanical", "physics", "chemistry", "biology", "mathematics", "statistics",
    "pharmacology", "medicine", "law", "wms", "erp", "techno-functional",
    "functional consultant", "supply chain", "blue yonder", "sap", "oracle fusion",
    "transcription", "transcriber", "clinical", "healthcare", "medical", "nursing",
    "pharmacy", "attorney", "paralegal", "videographer", "video editor",
    "motion graphics", "packaging", "label design", "financial crime",
    "investment banking", "underwriting",
)


def resume_hard_anti(row):
    """The title names a different profession: no body keyword overrides this."""
    title = (row.get("title") or "").lower()
    for phrase in HARD_ANTI:
        if phrase in title:
            return phrase
    return ""


def resume_anti_title(row, profile=None):
    """The strongest reason this title is not his line of work, or ""."""
    profile = profile if profile is not None else resume_profile()
    title = (row.get("title") or "").lower()
    worst = ("", 0)
    for phrase, weight in (profile.get("anti_title") or {}).items():
        if phrase in title and weight > worst[1]:
            worst = (phrase, weight)
    return worst[0] if worst[1] >= 8 else ""


def pretty_pay(pay, raw=""):
    """One clean pay line. "$75-$75 per hourly" is not a sentence."""
    if not pay:
        return raw or "not stated in the posting"
    unit = UNIT_WORD.get((pay.get("period") or "").lower(), pay.get("period") or "")
    low, high = pay.get("min"), pay.get("max")
    if low is not None and high is not None and float(low) == float(high):
        return "$%s per %s" % (_fmt(low), unit or "unit")
    if raw:
        return re.sub(r"(?i)\bper\s+annual(ly)?\b", "per year", raw).replace("per hourly", "per hour")
    if low is not None and high is not None:
        return "$%s to $%s per %s" % (_fmt(low), _fmt(high), unit or "unit")
    return raw or "not stated in the posting"


def fmt_posted(posted):
    """A posting date as a date. Himalayas sends a unix stamp, feeds send RFC 822."""
    text = str(posted or "").strip()
    if not text:
        return "date not stated"
    if text.isdigit() and len(text) in (10, 13):
        value = int(text[:10])
        try:
            return time.strftime("%Y-%m-%d", time.localtime(value))
        except (ValueError, OSError):
            return text
    return text[:24]

# -------------------------------------------------------------------- dates

DATE_FORMATS = (
    "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S",
    "%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z",
    "%Y-%m-%d %H:%M:%S", "%Y-%m-%d",
)


def parse_date(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            stamp = float(value)
            # Lever returns createdAt as epoch milliseconds; treating that as
            # seconds overflows and the row came back with no age at all.
            if stamp > 1e11:
                stamp = stamp / 1000.0
            return datetime.fromtimestamp(stamp, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in DATE_FORMATS:
        try:
            got = datetime.strptime(text, fmt)
            return got if got.tzinfo else got.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    # ISO 8601 with fractional seconds and an offset, which is what the Ashby and
    # Greenhouse APIs emit ("2026-09-11T17:08:43.899+00:00"). Without this the age
    # came back unknown and the freshness rule silently stopped applying to every
    # ATS posting, which let months-old reqs through as fresh.
    try:
        got = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return got if got.tzinfo else got.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def age_days(value):
    got = parse_date(value)
    if got is None:
        return None
    now = datetime.now(timezone.utc)
    return max(0.0, (now - got).total_seconds() / 86400.0)


def today_stamp():
    return datetime.now().strftime("%Y-%m-%d")
