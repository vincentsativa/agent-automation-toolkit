#!/usr/bin/env python
"""Pull Pinterest's public trend keyword lists and scan them for a niche.

Usage:
  python pinterest_trends_probe.py "ai|chatgpt|prompt|midjourney" --country US
  python pinterest_trends_probe.py "ai" --country US,GB,CA --end-date 2026-11-06 --all

Run under the interpreter that has scrapling/playwright (NOT the Hermes venv, which lacks both):
  PY="C:/Users/<user>/AppData/Local/Programs/Python/Python311/python.exe"; $PY pinterest_trends_probe.py "ai"

Prints, per preset: term count and which terms matched. An empty match list with full term
counts means the niche is absent from the lists that were actually scanned.
"""
import argparse
import asyncio
import datetime as dt
import json
import re
import urllib.parse

from playwright.async_api import async_playwright

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36")
PRESETS = (1, 2, 3, 4)


async def fetch_terms(page, params, max_tries=5):
    """GET /top_trends_filtered/ from inside the rendered page; back off on 429."""
    url = "/top_trends_filtered/?" + urllib.parse.urlencode(params, doseq=True)
    for _ in range(max_tries):
        raw = await page.evaluate(
            "async (u) => { const r = await fetch(u, {credentials:'include'});"
            " return r.status + '|' + await r.text(); }", url)
        status, body = raw.split('|', 1)
        if status != '429':
            try:
                return status, json.loads(body).get('values', [])
            except (ValueError, AttributeError):
                return status, []
        await asyncio.sleep(20)
    return '429', []


async def resolve_end_date(page, explicit):
    if explicit:
        return explicit
    raw = await page.evaluate(
        "async () => (await fetch('/latest_available_date/', {credentials:'include'})).text()")
    latest = dt.date.fromisoformat(json.loads(raw)['date'])
    # The site's own overview requested endDate = latest - 3 days.
    return (latest - dt.timedelta(days=3)).isoformat()


async def run(args):
    pattern = re.compile(args.pattern, re.I)
    countries = [c.strip().upper() for c in args.country.split(',') if c.strip()]
    matched, scanned = [], 0

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await (await browser.new_context(user_agent=UA)).new_page()
        await page.goto('https://trends.pinterest.com/', wait_until='networkidle', timeout=60000)
        end_date = await resolve_end_date(page, args.end_date)
        print(f"endDate={end_date} presets={','.join(map(str, PRESETS))} "
              f"countries={','.join(countries)}")

        for country in countries:
            for preset in PRESETS:
                status, values = await fetch_terms(page, {
                    'lookbackWindow': 2, 'endDate': end_date, 'rankingMethod': 3,
                    'country': country, 'trendsPreset': preset, 'numTermsToReturn': 100,
                })
                terms = [v.get('term', '') for v in values]
                hits = [t for t in terms if pattern.search(t)]
                scanned += len(terms)
                matched.extend((country, preset, t) for t in hits)
                print(f"  {country}/preset{preset}: status={status} terms={len(terms)} "
                      f"matches={len(hits)} {hits if hits else ''}")
                if args.all and terms:
                    print('    ' + ', '.join(terms))
                await asyncio.sleep(1)   # rate limits are IP-wide: never fan out

        await browser.close()

    print(f"scanned {scanned} term-slots")
    if matched:
        for country, preset, term in matched:
            print(f"MATCH {country}/preset{preset}: {term}")
    else:
        print("MATCHES: none in the lists scanned above")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('pattern', help='regex matched case-insensitively against each term')
    ap.add_argument('--country', default='US', help='comma-separated country codes (default US)')
    ap.add_argument('--end-date', default=None, help='YYYY-MM-DD weekly bucket (default: derived)')
    ap.add_argument('--all', action='store_true', help='print every term, not just matches')
    asyncio.run(run(ap.parse_args()))


if __name__ == '__main__':
    main()
