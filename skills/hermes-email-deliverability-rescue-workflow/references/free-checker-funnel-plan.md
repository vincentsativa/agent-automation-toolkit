# Free domain checker funnel (Email Deliverability Rescue expansion)

The approved expansion of the $500 rescue: a free browser-side email domain checker as the front door. Funnel: free checker, then free explainers, then a $29.99 DIY guide on Gumroad, then the $500 rescue on PayPal, then the $250 per month monitoring attached to the rescue.

The plan, mockup, and report were delivered to Vinny by email; Pi deploys the page. Rebuild nothing without re-reading this file first.

## Where it lives and how it ships (Vinny's correction)

ONE page. The checker is blended into the existing offer page at `/email-deliverability-rescue`, between the hero and the price block, keeping that page's theme, stylesheet, and Socratic copy untouched. The separate-URL plan was scrapped: fetch the live offer page's raw HTML and edit it. The shipped mockup carries WORKING browser-side DoH logic with a copyable results block, the coffee button worded "Keep this checker free" at top, push and email capture wired exactly like the articles (signup-form class, phantombyte-push-btn id, the two existing scripts), and a three-path section in the page's own card style.

Known-answer domains verified in the browser: phantom-byte.com all clean (p=reject, 4 of 10 lookups, rua on), example.com (null MX must be flagged, SPF -all, DMARC p=reject, no rua), gmail.com (p=none monitor-only warning, custom-selector DKIM honesty note), and a nonexistent domain refused as NXDOMAIN. Pitfalls proven while testing: reset the findings accumulator per run or verdicts leak between checks; a null MX `0 .` grades as Configured under a presence check unless matched literally; surprising results get cross-checked against a raw `curl` DoH answer before being trusted (example.com really does publish v=spf1 -all and p=reject).

## Checker MVP

All checks run client-side over DNS-over-HTTPS (Google and Cloudflare resolvers), no backend, no API keys, no accounts, no database. Port the record logic from `email_scan.py` and port the SPF lookup counter from its known-answer-tested implementation; do not rewrite the counter.

- MX: published and resolvable. Definitive either way.
- SPF: present, single record (two SPF TXTs is a confirmed error), syntax, terminal qualifier, recursive lookup count against the 10-lookup limit.
- DKIM: probe common selectors only (google, selector1, selector2, k1, s1, s2, mte1, mte2, and similar). A miss is always worded "no key found on common selectors." Custom selectors cannot be enumerated from outside.
- DMARC: presence, p= value, pct=, rua presence. p=none is the highest-value detection in the tool: it looks configured and enforces nothing, and most owners read "DMARC present" as done.
- Alignment: cannot be determined from DNS, because it compares the From header of a sent message against the domain that passed SPF or DKIM. Say so and link the explainer showing how to read Authentication-Results off a received message.
- Blacklist and reputation checks are NOT in the MVP. DNSBL zones block or misreport from public DoH resolvers, and a wrong blacklist accusation is the worst false positive available.

## Severity model

Four fixed states used everywhere, in the tool, the explainers, and the guide:

1. Confirmed problem: DNS evidence proves it (no DMARC, over the lookup limit, two SPF records, syntax error).
2. Warning, needs attention: valid but weak (?all, p=none, missing rua). Most business domains live here.
3. Informational: true but not a defect (multiple platforms in SPF, null MX on a non-mail domain).
4. Unable to determine: custom-selector DKIM, alignment, anything needing a sent message.

Never a score out of 100, never a deliverability percentage. DNS proves a record missing; it cannot prove where mail lands, because placement also depends on content, volume, and sender reputation. The page carries a visible honesty box stating what the check can and cannot tell you. That box is a differentiator, not a disclaimer; no competitor says it out loud.

## Free versus paid boundaries

- Free checker: answers "is something wrong." Findings, severity, what the record does, why it matters. No remediation plan, no generated record values.
- Free explainers (five, one per record): what the record does. Self-contained, front-loaded, written to be quotable.
- $29.99 guide: "how do I fix it myself, exactly." Exact values per provider, click paths for Google Workspace, Microsoft 365, GoDaddy, Cloudflare, plus Mailchimp and SendGrid as platforms, verification steps, re-check instructions. Full-build rule applies: generic DNS technique, not the proprietary stack, so ship it complete. SPF flattening is the headline chapter.
- $500 rescue: "take responsibility for it." Complex multi-platform conflicts, remediation, verification, before and after report.
- Hard line: the free tool never prints the corrected record. The guide teaches the buyer to write it; the service writes it for them.

## Pricing and channels

- The $500 service stays on PayPal (fee about $15). The never-Gumroad rule for the service is price-dependent, not absolute.
- The tutorial sells on Gumroad at $29.99: fee about $3, plus the marketplace, the existing phantombyteai.gumroad.com audience, and consistency with the catalog. Never mix: service on PayPal, tutorials on Gumroad.
- $29.99 rationale: the buyer is a business owner with invoices going to spam, comparing the price against a $500 alternative. It sits above the catalog's flagship tier for a more expensive problem without reading as a pamphlet.

## Competitive gap (verified live against each site)

- MXToolbox: fragmented single-record tools, heavy ads, enterprise upsell. Gives a result, no meaning.
- Kitterman: SPF only, dated page.
- mail-tester: requires sending mail to a unique address, single-use, scores without fixing. Built for newsletter campaign tests, not domain checks.
- learndmarc.com: genuinely educational, but requires a sent message and says view on desktop for the full experience. Mobile is where the audience is.
- dmarcian and EasyDMARC: free checkers funnel to DMARC-management SaaS subscriptions; record-by-record results push account signup.
- The gap nobody fills: single-page, enter-domain, no-email-required, all-records-at-once, plain-language findings, honest severity labels, an explicit statement of what DNS cannot prove, and a do-it-yourself or hire-us path.

## Keyword map (Google autocomplete, US)

- Tool terms, checker page title, H1, opening line: spf record checker, dkim record checker, dmarc record checker, email dns checker, domain email checker, email deliverability test. Incumbent-name variants (mxtoolbox, kitterman) are opportunities: people search the incumbent by name and the SERP can hand them an alternative.
- Problem terms, explainers and guide: spf too many lookups (plus mailgun and bluehost forms), spf permerror, spf softfail, dmarc p=none vs quarantine vs reject (the best table topic in the whole set), dmarc failing (sendgrid and mailchimp forms), dkim check failed, dmarc alignment, emails going to spam with the provider forms (gmail, outlook, google workspace, godaddy), email blacklist check, domain blacklist check.
- Question terms, FAQ and H2: how do i check my spf record, how do i know if dkim is working, how do i check my dmarc record, how to set up spf, dkim, dmarc with provider forms, dmarc setup guide, recommended dmarc settings.
- Zero-competition phrasings, use verbatim: "is my domain configured correctly", "spf dkim dmarc setup service".
- Parked future keyword: dmarc report reader and dmarc report viewer belong to the monitoring product, not the checker.

## Site architecture

- The checker is a section of the single blended offer page at `/email-deliverability-rescue`, not its own URL. It cross-links the explainers and anchors the $500 and form sections of the same page.
- Five explainer pages: SPF explained, DKIM and selectors, DMARC and the policy ladder, alignment, and why mail still goes to spam when records pass.
- FAQPage structured data on the blended page using the question phrasings above. Primary-source citations on the explainers (RFC 7208 for SPF, RFC 6376 for DKIM, RFC 7489 for DMARC, Google's sender requirements, Microsoft guidance). No llms.txt, no chunking, no AI-specific anything.

## Mockup rules (mobile-first)

The blended page is already mobile-optimized; the existing offer page CSS carries the mobile behavior, so extend its media queries rather than designing a separate mobile layout. Top to bottom: coffee banner worded "Keep this checker free" at top in the page's own highlighted-box style, hero, the working checker with domain input and severity legend, live findings table and copyable results block, then the original offer page flow: price and CTAs, three questions, records table, three-path cards, $500 deliverables, honesty box, will-not-promise, form, capture, footer.

- One primary action above the fold: check my domain. The coffee button sits above it but reads as secondary, yellow and slim, same pattern as the articles. One coffee ask only, never a second at the bottom.
- The $500 CTA appears exactly twice (path selection and page bottom), never interrupting a results read. Payment never happens on the checker page; it anchors to the rescue page.
- Capture sits between the explainers and the service block so it catches both the DIY reader and the future client.
- Verify before delivery: dash scan (em, en, spaced hyphen all zero, including inside hrefs), tag balance, Playwright screenshots at 390x844 and 1280x900, and a visual check of the mobile render before handing it over.

## Implementation order

1. Port the record logic and lookup counter into a browser-side DoH module.
2. Build the page from the mockup; real findings replace the placeholder block.
3. Known-answer test against domains with known states: one clean, one missing DMARC, one over the lookup limit, one on a custom DKIM selector, one nonexistent. The test_email_scan.py pattern applies directly.
4. Pi deploys. The deployment boundary is unchanged: write and verify locally, Pi ships.
5. Explainers publish one per day, each cross-linked from its findings.
6. The Gumroad guide follows once the findings language has met real users, so it teaches the fix for the exact wording people saw in their results.

## Parked until demand proves it

- The monitoring product (quarterly re-verify plus alert email; keyword demand exists via dmarc report reader and viewer). The $250 per month manual monitoring already exists on the rescue page; a second recurring product without evidence is complexity.
- The MSP white-label angle — unparked 2026-10-08 on Vinny's direction; the
  terms, copy drafts, sourcing, and page outline are in
  `references/partner-referral-channel.md`. r/msp stays the tolerant venue.
- The blacklist check, until a reliable resolver path for the major zones exists, and then as its own labeled check.

## Tutorial-outline prompt (for drafting the $29.99 guide outline)

Draft the complete outline for the PhantomByte email deliverability DIY guide, a paid Gumroad tutorial at $29.99.

Context: PhantomByte runs a $500 Email Deliverability Rescue service and a free email domain checker. The checker reports MX, SPF, SPF lookup count, DKIM on common selectors, DMARC, and alignment limitations, using four fixed severity states: Confirmed problem, Warning needs attention, Informational, Unable to determine. The guide teaches the buyer to fix every finding the checker can produce, on their own, and is the middle tier between the free checker and the $500 service.

Before drafting, verify current record specifics against primary sources: RFC 7208 for SPF, RFC 6376 for DKIM, RFC 7489 for DMARC, Google's bulk sender requirements, and Microsoft 365 DKIM guidance. Do not write a mechanism from memory if a live check can confirm it.

Requirements:
- Structure the outline in six parts: find what is broken, SPF, DKIM, DMARC, alignment, verify and re-check.
- Build it around the actual diagnostic findings the checker produces, not a generic email course. Every chapter traces to a finding.
- Cover provider click paths for Google Workspace, Microsoft 365, GoDaddy, Cloudflare, and at minimum Mailchimp and SendGrid as sending platforms.
- Include the SPF lookup flattening chapter prominently; community research shows it is the most-asked unsolved question.
- Use the Socratic method only at diagnosis and decision points, for example: are you sending from more than one platform, then your SPF may need to authorize multiple senders. Use direct instruction for click paths and record syntax; ambiguity there costs the sale.
- Never promise inbox placement. State plainly what DNS fixes and what it cannot fix.
- The final chapter is the honest bridge: when to stop DIY and hand it to the $500 service.
- For each chapter, list: the checker finding it answers, the exact fix procedure, the verification step, the most common mistake, and the internal link to the free explainer.
- Voice: direct, first person, short paragraphs, no em dashes, no corporate language, an experienced engineer telling the reader exactly what to click. Concrete record values and real syntax, no filler.
- The reader finishes able to check, understand, fix and verify without us. That is the product, not a leak.
- Output the outline as a single text document with part titles, chapter titles, a short description of each chapter's content, and a SOURCES section listing the primary references used.
