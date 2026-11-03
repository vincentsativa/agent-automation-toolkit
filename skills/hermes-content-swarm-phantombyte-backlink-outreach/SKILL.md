---
name: phantombyte-backlink-outreach
description: Use when building PhantomByte backlink outreach. White-hat.
tags: [SEO, backlinks, outreach, GEO, PhantomByte]
---

# PhantomByte Backlink Outreach

Class-level procedure for building and executing a white-hat backlink outreach campaign for articles.phantom-byte.com (or any PhantomByte property). The deliverable is a text report emailed to Vinny, not chat text.

## Always-on rules
- **Vinny is a builder, not a promoter. Lead with artifacts, never with pitching himself.** He has explicitly rejected the newsletter-pitch and podcast-guest route (his words: he is a builder, not a podcaster). Do not propose a sequence of pitching himself to hosts, do not draft guest pitches, and do not frame outreach as self-promotion theater. The channels that fit him, in priority order: (1) ship a working artifact (tool, script, repo, reference) that spreads on its own; (2) notify a tool maintainer whose README already links community tutorials, with no ask; (3) answer technical questions in builder venues with the working link. A one-way "I wrote a working tutorial for your tool" note to a maintainer is showing work, not pitching, and that distinction is the whole reason it is acceptable to him. Newsletter and podcast outreach stays available as a tier but is never the headline recommendation.
- **White-hat only.** No paid links, PBNs, link farms, guest-post networks that charge for placement, reciprocal link schemes, directory spam, comment-link dropping, or automated outreach blasts. Google's link spam policy is the constraint, and Vinny's brand strategy is SEO/GEO compounding, not risky shortcuts.
- **Every target must be verified live before it enters the report.** Fetch the site with scrapling (`Fetcher().get(url)`), confirm it resolves, and confirm the contact path (email, submission form, or contribute page) actually exists. A named contact beats a category placeholder every time.
- **No AI content farms or sites without named human authors as targets** (constitution Article 9 consistency).
- **Never call a link dofollow from a static fetch.** The only acceptable evidence is the live `rel` attribute on the rendered anchor. A static HTML fetch of a JavaScript-rendered platform (HackerNoon, Hashnode, freeCodeCamp) returns zero outbound anchors, so it can neither confirm nor deny the rel value; read the rendered DOM through `browser_exec` instead, or state the rel as unverified in the report. Medium is confirmed nofollow on outbound links (checked live on a large publication page), so it never belongs in a link-equity tier.
- **Em-dash count must be 0 in the report file**, verified programmatically over the file before the first email send, not after.
- **Delivery shape:** report as attached .txt file, concise summary in the email body (verdict, key findings, next action), never the full text pasted in the body. Email via email-sender skill, then confirm on Telegram.

## Completeness gate (learned the hard way)
A strategy report is not done while it contains gaps a tool could close. Before the first send:
1. Any "list of N targets" must be N NAMED targets with verified contact paths, not a category like "10 indie newsletters."
2. Baselines: attempt every baseline pull yourself (site audit, target verification, competitor surface checks). The only acceptable gap is one requiring user credentials you do not hold (e.g., Search Console login), and it must appear in the report as a specific, minimal user action with steps.
3. If the user asks "verify this is a good idea," the report must contain an explicit verdict section with honest reasoning, not just a plan.

Shipping a draft with placeholder categories and calling it complete gets called out as unfinished work and forces a v2 resend. Full output or nothing applies to strategy documents as much as to code.

## Procedure

### Phase 1: Audit the site
Fetch the target site with scrapling. Confirm: article count, publishing cadence, byline presence, categories. This grounds the strategy in reality and gives pitch-able asset counts.

### Phase 2: Verify targets live (scrapling, never browser for this)
Fetch each candidate target and confirm it is up AND find its real contact path:
- **Look for emails in raw page HTML**, not just rendered text: `re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', page.html_content)` — Substack sites often hide emails from `get_all_text()` but expose them in the body HTML.
- **Check /about, /contact, /privacy pages** for emails when the homepage has none (one site's contact only appeared in its privacy policy).
- **A 404 on a guessed /submit path means the path does not exist** — do not include it; find the real path or mark the target's contact method honestly.
- **Do not trust a documented contact path without re-probing it this session.** Submission URLs drift silently; paths recorded in `references/verified-targets.md` have since started returning 404, and the live replacement sits in the homepage navigation. Grep the homepage HTML for the real path in one pass instead of guessing slugs: `re.findall(r'href="([^"]*(?:write-for|contribut|submit|guest)[^"]*)"', html, re.I)`, then fetch each hit and keep the 200s. A site whose old write-for-us URL is dead usually still links the working one from the footer or a nav menu.
- **A 404 page can still leak the correct contact.** Editorial addresses often render on the 404 itself or in the site footer; grep any fetched page for an email regex before concluding a target has no contact.
- Obfuscated `[email protected]` placeholders mean the real address is in the mailto href or raw HTML; grep the raw body.

### Phase 3: Write the report
Structure that works (user approved this shape):
1. Verdict and reasoning (is this a good idea, honestly rated)
2. Existing assets inventory
3. Target lists in tiers, every entry verified with contact path
4. Prohibited tactics list (explicit, so white-hat is enforceable)
5. Step-by-step implementation starting "tomorrow"
6. Outreach email rules (under 120 words, one link, one ask, follow up once after 7 days, let them pick anchor text)
7. Weekly cadence loop with time budget
8. Measurement plan (referring domains baseline, realistic targets: +2 to 4 quality referring domains/month from a standing start)

### Phase 4: Pre-send verification
- Em-dash count 0 over the file (`t.count('\u2014')`), strip and recount
- Word count matches what the email body claims
- Every URL mentioned was fetched successfully this session

### Phase 5: Deliver
Email the attached report to hello@example.com via email-sender, brief summary body, then Telegram confirmation. Never paste report content into chat.

## Pitfalls
- **Substack-based newsletters rarely expose a public email** — contact is via reply-to-issue or their about page; check the raw HTML before declaring "no contact found."
- **Never guess or fabricate a submission URL.** A plausible-looking /submit that 404s must be removed or corrected before the report ships.
- **Do not buy SEO tools (Ahrefs/Semrush) in month 1** — run syndication and relationship tiers first, baseline via Search Console, and buy one month of link-intersect data only if month 1 lands under target. Getting data you cannot yet act on is waste.
- **Search Console data requires the user's Google login.** The automation Chrome profile (chrome-kw) has no Google session; do not attempt credential guessing. Mark it as the one user action.
- **If the automation browser is needed** (e.g., GSC check), launch chrome-kw via the browser-exec-recovery skill, and close it with kill_chromekw.ps1 verified (remaining: 0 AND port dead) when done.

## References
- `references/verified-targets.md` — the verified target list with contact paths (verify again before reusing; sites change), plus the target-verification technique notes.
- `references/offsite-syndication.md` — whether and how to republish originals on third-party platforms: canonical ownership, publish-first ordering, per-platform outbound-link rel values, and the standing verdict on Medium.
