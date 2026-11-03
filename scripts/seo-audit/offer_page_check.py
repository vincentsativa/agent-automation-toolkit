#!/usr/bin/env python3
"""
offer_page_check.py — audit a phantom-byte.com offer/landing page.

Checks the SEO/GEO head block, the contact-form wiring, and (optionally) that the
page is present in sitemap.xml / llms.txt. Can also submit the page to IndexNow.

Usage:
  python offer_page_check.py --file path/to/page.html
  python offer_page_check.py --url https://phantom-byte.com/my-offer
  python offer_page_check.py --url https://phantom-byte.com/my-offer --domain https://phantom-byte.com
  python offer_page_check.py --url https://phantom-byte.com/my-offer --submit-indexnow

Exit code: 0 if no FAILs, 1 if any FAIL.

Only the Python standard library is required.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html import unescape

GA_ID = "G-PDQCZE09E4"
API_HOST = "phantom-byte-contact-ionos-1091380733401.us-central1.run.app"
INDEXNOW_KEY = "phantombyte2026"
INDEXNOW_KEY_URL = "https://phantom-byte.com/phantombyte2026.txt"
INDEXNOW_ENDPOINTS = ["https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow"]

RESULTS = []  # (level, label, detail) with level in {"PASS","WARN","FAIL"}


def add(level, label, detail=""):
    RESULTS.append((level, label, detail))


def check(cond, label, fail_detail="", warn=False):
    if cond:
        add("PASS", label)
    else:
        add("WARN" if warn else "FAIL", label, fail_detail)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "phantombyte-offer-audit/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def meta(html, key, attr="name"):
    """Return content of <meta {attr}="{key}" content="...">."""
    pat = re.compile(
        r"<meta[^>]*\b" + attr + r"\s*=\s*[\"']" + re.escape(key) + r"[\"'][^>]*>", re.I
    )
    m = pat.search(html)
    if not m:
        return None
    c = re.search(r'content\s*=\s*["\']([^"\']*)["\']', m.group(0), re.I)
    return unescape(c.group(1)) if c else ""


def link_href(html, rel):
    pat = re.compile(r"<link[^>]*\brel\s*=\s*[\"'][^\"']*\b" + re.escape(rel) + r"\b[^\"']*[\"'][^>]*>", re.I)
    m = pat.search(html)
    if not m:
        return None
    c = re.search(r'href\s*=\s*["\']([^"\']*)["\']', m.group(0), re.I)
    return c.group(1) if c else ""


def audit(html, source_label, domain=None, slug=None):
    # ── basics ────────────────────────────────────────────────────────────────
    check(re.search(r"<meta[^>]*charset", html, re.I) is not None, "meta charset")
    check("name=\"viewport\"" in html or "name='viewport'" in html, "meta viewport")

    t = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    title = unescape(t.group(1).strip()) if t else ""
    check(bool(title), "title present")
    if title:
        check(len(title) <= 70, f"title length <= 70 (got {len(title)})", warn=True)

    desc = meta(html, "description")
    check(bool(desc), "meta description present")
    if desc:
        check(50 <= len(desc) <= 160, f"meta description 50-160 chars (got {len(desc)})", warn=True)

    robots = (meta(html, "robots") or "").lower()
    check("index" in robots and "noindex" not in robots, "robots allows indexing", f"robots={robots!r}")

    canon = link_href(html, "canonical")
    check(bool(canon), "canonical link present")
    if canon and domain and slug:
        expected = domain.rstrip("/") + "/" + slug
        check(canon.rstrip("/") == expected, f"canonical == {expected}", f"got {canon}")

    # ── social ────────────────────────────────────────────────────────────────
    for k in ("og:type", "og:url", "og:title", "og:description", "og:image"):
        check(bool(meta(html, k, "property")), f"{k} present")
    for k in ("twitter:card", "twitter:title", "twitter:description", "twitter:image"):
        check(bool(meta(html, k, "property") or meta(html, k, "name")), f"{k} present")
    check(bool(link_href(html, "icon")), "favicon present", warn=True)

    # ── analytics ─────────────────────────────────────────────────────────────
    check("googletagmanager.com/gtag/js" in html, "GA gtag.js script present")
    check(GA_ID in html, f"GA id {GA_ID} present")
    check(re.search(r"gtag\(\s*['\"]config['\"]", html) is not None, "gtag('config', …) call present")

    # ── structured data ───────────────────────────────────────────────────────
    blocks = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.S | re.I)
    check(bool(blocks), "JSON-LD block present")
    types = set()
    ok_json = True

    def collect(node):
        if isinstance(node, dict):
            if node.get("@type"):
                t = node["@type"]
                types.update(t if isinstance(t, list) else [t])
            for v in node.values():
                collect(v)
        elif isinstance(node, list):
            for v in node:
                collect(v)

    for b in blocks:
        try:
            data = json.loads(b.strip())
        except Exception as e:  # noqa: BLE001
            ok_json = False
            add("FAIL", "JSON-LD parses", str(e)[:120])
            continue
        collect(data)
    if ok_json and blocks:
        add("PASS", "JSON-LD parses")
    check("Service" in types, "schema: Service", f"types={sorted(types)}")
    check("Offer" in types, "schema: Offer", f"types={sorted(types)}", warn=True)
    check("FAQPage" in types, "schema: FAQPage", f"types={sorted(types)}", warn=True)
    check("BreadcrumbList" in types, "schema: BreadcrumbList", f"types={sorted(types)}", warn=True)

    # ── form wiring ───────────────────────────────────────────────────────────
    has_form = "contactForm" in html or re.search(r"<form", html, re.I) is not None
    check(has_form, "form present")
    check("/api/contact-form" in html, "form posts to contact API")
    check(API_HOST in html, "contact API host correct")
    check(re.search(r"Content-Type['\"]?\s*:\s*['\"]application/json", html) is not None,
          "form sends JSON content-type")
    check(re.search(r"source\s*:\s*['\"][^'\"]+['\"]", html) is not None, "form sends a `source` label")
    check('class="hp"' in html or "honeypot" in html.lower(), "honeypot present", warn=True)
    check("hello@example.com" in html, "email fallback present")

    # ── optional: sitemap / llms ──────────────────────────────────────────────
    if domain and slug:
        base = domain.rstrip("/")
        try:
            sm = fetch(base + "/sitemap.xml")
            check(slug in sm, f"in sitemap.xml", f"{slug} not found in {base}/sitemap.xml")
        except Exception as e:  # noqa: BLE001
            add("WARN", "sitemap.xml reachable", str(e)[:100])
        try:
            llms = fetch(base + "/llms.txt")
            check(slug in llms, "in llms.txt", f"{slug} not found in {base}/llms.txt", warn=True)
        except Exception as e:  # noqa: BLE001
            add("WARN", "llms.txt reachable", str(e)[:100])

    print(f"\nAudit: {source_label}\n" + "=" * (7 + len(source_label)))
    for level, label, detail in RESULTS:
        icon = {"PASS": "  ok ", "WARN": " warn", "FAIL": " FAIL"}[level]
        line = f"[{icon}] {label}"
        if detail and level != "PASS":
            line += f"  -> {detail}"
        print(line)
    fails = sum(1 for l, _, _ in RESULTS if l == "FAIL")
    warns = sum(1 for l, _, _ in RESULTS if l == "WARN")
    print("-" * 40)
    print(f"{len(RESULTS)} checks: {len(RESULTS) - fails - warns} pass, {warns} warn, {fails} fail")
    return fails


def submit_indexnow(urls):
    host = urllib.parse.urlparse(urls[0]).netloc
    payload = json.dumps({
        "host": host,
        "key": INDEXNOW_KEY,
        "keyLocation": INDEXNOW_KEY_URL,
        "urlList": urls,
    }).encode()
    print(f"\nIndexNow: submitting {len(urls)} URL(s) for host {host}")
    ok = False
    for ep in INDEXNOW_ENDPOINTS:
        try:
            req = urllib.request.Request(
                ep, data=payload, headers={"Content-Type": "application/json; charset=utf-8"}
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                status = r.status
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception as e:  # noqa: BLE001
            print(f"  {ep} -> error {str(e)[:80]}")
            continue
        good = status in (200, 202)
        ok = ok or good
        print(f"  {ep} -> {status} {'(accepted)' if good else '(FAILED)'}")
    if not ok:
        print("  IndexNow: no endpoint accepted the submission.")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="Audit a phantom-byte.com offer page.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="local HTML file")
    src.add_argument("--url", help="live page URL")
    ap.add_argument("--domain", help="site origin for sitemap/llms checks, e.g. https://phantom-byte.com")
    ap.add_argument("--slug", help="override slug (defaults to file name / URL path)")
    ap.add_argument("--submit-indexnow", action="store_true", help="submit page + sitemap to IndexNow")
    args = ap.parse_args()

    if args.file:
        html = open(args.file, encoding="utf-8").read()
        slug = args.slug or os.path.basename(args.file).rsplit(".", 1)[0]
        source = os.path.abspath(args.file)
    else:
        html = fetch(args.url)
        parsed = urllib.parse.urlparse(args.url)
        slug = args.slug or parsed.path.rstrip("/").split("/")[-1]
        if slug.endswith(".html"):
            slug = slug[:-5]
        source = args.url
        if not args.domain:
            args.domain = f"{parsed.scheme}://{parsed.netloc}"

    fails = audit(html, source, domain=args.domain, slug=slug)

    rc = 1 if fails else 0
    if args.submit_indexnow:
        base = (args.domain or "https://phantom-byte.com").rstrip("/")
        urls = [f"{base}/{slug}", f"{base}/sitemap.xml"]
        rc = submit_indexnow(urls) or rc
    sys.exit(rc)


if __name__ == "__main__":
    main()
