---
name: pinterest-trends
description: "Use when asked what's trending on Pinterest in a niche."
trigger: "user asks what is trending on Pinterest, what Pinterest searches are rising, Pinterest niche demand, what to post on Pinterest, or Pinterest Predicts"
---

# Pinterest Trend Research

## When to Use
- "What's trending on Pinterest" / "what should we post on Pinterest" / "is <niche> big on Pinterest"
- Mapping a niche against Pinterest demand before writing or scheduling pins
- "What did Pinterest Predicts say" / long-horizon Pinterest demand
- NOT for article keyword targeting (that is `keyword-research-seo`, Google Trends) or for writing the pin itself

Purpose: which Pinterest search terms are rising for a given niche, with numbers. Every figure carries its **week-ending date and country**, Pinterest trend data is scoped to both and rolls weekly, so a number without them is not reportable.

## Step 1, Render the overview page
Plain `Fetcher` returns an empty body on trends.pinterest.com: it is a JS app shell. Render it.

```python
from scrapling.fetchers import StealthyFetcher
sf = StealthyFetcher()
p = sf.fetch('https://trends.pinterest.com/', headless=True, network_idle=True, timeout=60000)
text = p.get_all_text()          # Selector has no inner_text(); page.text is '' on a JS shell
```

That rendered text already carries: **Trends in the spotlight** (top 5 with % MoM + category), **Shopping trends** (top 10 product categories by outbound-click growth), the 5-row **search trends** preview, **Moments** (holidays marked Rising/Approaching), **Editors' Picks** keyword clusters, and the Pinterest Predicts carousel.

## Step 2, Keyword lists at scale: `/top_trends_filtered/`
Call it **from inside the rendered page** (session cookies are what make it return data):

```
GET https://trends.pinterest.com/top_trends_filtered/
    ?lookbackWindow=2&endDate=YYYY-MM-DD&rankingMethod=3
    &country=US&trendsPreset={1..4}&numTermsToReturn=100
```

Response: `{"values":[{"term","wow_change","mom_change","yoy_change","normalizedCount","seasonality_score", ...}]}`, the `*_change.value` fields are fractions (0.2 = 20%) on some presets and the sentinel `100.01` for off-the-chart growth on others, so normalize per preset before comparing across them.

Constraints:
- `trendsPreset` accepts only 1–4; anything else returns HTTP 400.
- `numTermsToReturn` max 100; above that returns HTTP 400.
- **Unknown query params are silently ignored.** A `term=`/`keyword=`/`interest=` filter that does not change the returned terms did not apply, verify by diffing the terms, never assume.
- `country` takes US, GB, CA, DE, FR, AU, IN … Scan every region you intend to speak about; do not extrapolate a niche's absence in one country to another.
- Get the current data bucket from `GET /latest_available_date/` → `{"date":"..."}`. The site's own overview called `endDate` as that date minus 3 days; print whichever `endDate` you used alongside the results so it can be corrected.

## Step 3, Per-keyword growth: `/metrics/`
```
GET /metrics/?terms=<ONE term>&country=US&end_date=...&days=90
    &aggregation=2&normalize_against_group=false&predicted_days=0
```
→ `[{'growth_rates':{'wow_change','mom_change','yoy_change'},'counts':[{date,count}...]}]`

- **One term per request.** Multi-term batches came back empty even for terms that resolve individually.
- **Read the HTTP status, not just the body.** A 429 answers with the body `[]`, byte-identical to "term has no data".
- A term outside Pinterest's index also returns `[]` with 200. Always fire one known-good control term (a term seen in Step 1/2) before reporting that a niche has no Pinterest data.

## Step 4, Pacing
Rate limits are **IP-wide and shared across every browser instance**, so concurrent scrapers poison each other. One session at a time, ≥1 s between calls, 20 s backoff on 429, and never start a second trend script while one is running.

## Step 5, When the niche comes back empty: answer with the keywords, from Google Trends
An empty Pinterest result is a coverage fact, not an answer to "which keywords are popular". The user asking for niche keywords wants a keyword list, so as soon as Step 2/3 show no matches, stop probing Pinterest and produce the list from Google Trends, same turn, no negative-only reply, no second request for confirmation.

Procedure (the `keyword-research-seo` skill holds the full method):
1. URL-param navigation in a named browser session: `https://trends.google.com/trends/explore?q=term1,term2,term3,term4,term5&geo=US&date=today%203-m`, never the searchbox, never a bare explore URL. Up to 5 terms per batch; batch the highest-value terms first because only some batches may land.
2. After load + ~6 s, read `document.body.innerText`: the `Average` row is the volume ranking, and each term's `Related queries → Rising` block is the "right now" signal (breakout / +N%).
3. From those rising blocks drop the queries unrelated to the niche, low-volume seeds return Google's generic filler (`best time to visit …`, `how to bake a cake`), and keep only queries naming the niche's own tools, models, formats and use cases.
4. Report the niche's volume-ranked keywords first, rising queries second, one line naming the source and window.

Dead ends on the anonymous Pinterest surface, do not re-chase them: `www.pinterest.com/resource/*` returns HTTP 403 `Invalid Resource Request` (search, suggestions and pin data alike), `/search/autocomplete/` returns an HTML shell instead of JSON, and `trends.pinterest.com/related_terms/` returns HTTP 400 `[]` under every param shape tried. Autocomplete/suggestion data is only reachable logged in.

## Login-gated surfaces
`/search/?country=US` (the full keyword table with weekly/monthly/yearly change columns, filters, CSV export) 302s to `showUnauthModal`, and www.pinterest.com pin search sits behind the same wall. Public coverage is therefore: overview page + `/top_trends_filtered/` + `/metrics/` + the Predicts report. Only attempt a login if credentials are actually supplied.

## Pinterest Predicts (annual, long-horizon demand)
`https://business.pinterest.com/pinterest-predicts/` via StealthyFetcher (JS-rendered). Each trend block contains a `What people are searching for` list of `keyword +NN%` lines; parse the rendered text with:

```python
re.findall(r"([a-z0-9 &\'-]{3,45})\s(\+\d{1,3}%)", text)
```

Read the footnotes for scope: it is a forecast built from global English search data over a fixed historical window, not this week's US volume, label it as such when reporting.

## Reporting
- The deliverable is the keyword list: terms first, numbers next, ranked by volume, source and window stated in one line. That is the whole answer.
- A one-line coverage statement backs a negative (`2,400 slots, 6 countries, 4 presets, 0 matches`), the scan inventory is evidence for the claim, never the body of the reply. Do not expand it into a methodology section.
- No unsolicited interpretation. Strategy, "what this means for posting", format suggestions and recommendations the user did not ask for are the failure mode this task keeps producing, the question names the deliverable, and the reply contains that deliverable and nothing else.
- When the niche is empty in Pinterest, the answer is the Google Trends keyword list from Step 5, not the emptiness.
- Trend data answers the question; no platform commentary around it.

## Script
`scripts/pinterest_trends_probe.py`, renders the page, resolves the current `endDate`, pulls top terms across presets/countries with 429 backoff, and prints matches for a regex niche pattern. Run it under the interpreter that has scrapling/playwright (see the `scrapling` skill's Access section).
