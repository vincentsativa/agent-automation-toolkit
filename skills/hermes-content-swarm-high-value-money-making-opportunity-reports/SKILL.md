---
name: high-value-money-making-opportunity-reports
description: Money-making opportunities report from TODAYS DATA FILES.
trigger: "daily money-making opportunity report, high-value opportunities from today's data files, generate money-making ideas"
---

# High-Value Money-Making Opportunity Reports

Recurring daily cron workflow: read the day's AI-news data files in `Desktop/TODAYS DATA FILES/`, filter out weak/trendy/duplicate ideas, produce a ranked report of high-value opportunities, save it, and email it to Vinny. The goal is NOT a content pipeline, it's finding throwaway, low-cost, sellable opportunities a technical solo operator can validate this week.

## Input Data Files (Desktop/TODAYS DATA FILES/)
Read EVERY data file, do not skip files because they look similar. Typical files:
- `20-AI-News-Stories-YYYY-MM-DD.md`, 20-25 fresh news stories with per-story stats
- `blogwatcher-dump-YYYY-MM-DD.txt`, 24-ish headlines + summaries + "unwritten themes"
- `ironpulse-YYYY-MM-DD.txt`, top ~20 ranked AI stories
- `tensorfeed_report_YYYY-MM-DD.txt`, top headlines + arXiv papers + emerging themes
- `outlineN-*.txt`, PhantomByte article outlines (STRONG opportunity signals; read these first, they already distil a thesis + evidence)
- `pinterest_posts_*`, `social-media-questions-*`, secondary/contextual

Extract concrete signals: new product/API releases, open-source tools/models, security incidents/breaches, AI cost increases/savings, new regulations/policy, platform changes, adoption/ROI evidence, new implementation methods. A news story is only evidence of a possible trigger, not proof of a business.

## Dedup Against the Opportunity Catalog (CRITICAL)
The catalog lives in `Desktop/LOW BUDGET MONEY MAKING OPPORTUNITIES/high-value-money-making-opportunities-*.txt` going back weeks (plus older `low-budget-*` and `opportunities-*` files). **Before writing anything, read at least the previous day's report fully and skim the prior week's titles** (grep `^# [0-9]` for the ranked titles).

A candidate is allowed only if it is materially different in at least TWO of these seven areas:
- Target buyer
- Expensive problem solved
- Paid offer
- Delivery method
- Revenue model
- Technical implementation
- Trigger event / new capability

Check duplicates rigorously. Renamed versions of an old idea, or an old idea with a new headline/marketing angle, are duplicates. Keep a running list in the report header of every rejected-as-duplicate idea. Recurring ones that keep being rejected (verify each day): AI Agent Security Audit, Open-Weight Deployment, Multi-Model Routing, AI Cost Governance, AI Search Visibility/AEO, EU AI Content Labeling Compliance, GPU Utilization Audit, Agent Memory Coach, MCP security/migration, AI Content Provenance, AI Spend Visibility, Agent Containment, Autonomous Coding Agent Operations.

## Opportunity Quality Gate
Include an opportunity only if it scores **20/25 or higher**. Score each 1-5:
1. **Pain and urgency**, does a specific buyer have an expensive/risky/revenue-impacting problem right now?
2. **Buyer reachability**, can I identify/contact ≥50 likely buyers this week (LinkedIn, GitHub, directories, communities, job posts)?
3. **Willingness to pay**, can I sell a paid audit/setup/pilot for ≥$500 before building SaaS?
4. **Fast validation**, sales asset + outreach within 24h, first paid engagement in 1-5 days?
5. **Repeatability/expansion**, can ≥70% of delivery be standardized? Clear upsell to retainer/managed/SaaS?

If fewer than 3 score 20+, return fewer than 3. Do NOT lower the standard to fill a quota.

## Hard Rejection Rules
Reject ideas depending on: vague trend/hype/single news story with no reachable buyer; building an app/marketplace/SaaS/game/course/audience/community BEFORE validating a paid service; consumer speculation/affiliate/ad-revenue/virality/platform algorithms; generic AI content/consulting/prompt packs/commodity Fiverr work; unverifiable AI-detection claims; legal/medical/employment/financial/regulatory advice without a qualified partner; guaranteed security/compliance claims; hardware/inventory/paid-ads/paid-tools or >$500 costs before first payment; a vendor feature that makes the service unnecessary (unless there's a real implementation/audit wedge); long enterprise sales cycles (unless a smaller buyer can be sold first).

Frame security/compliance work as scoped assessments, testing, risk reduction, technical implementation, or remediation support, NEVER claim legal conclusions, guarantees, certification, or complete protection.

## Report Format (exact, per opportunity)
```
# [Rank]. [Specific Offer Name]
Score: X/25
- Pain and urgency: X/5
- Buyer reachability: X/5
- Willingness to pay: X/5
- Fast validation: X/5
- Repeatability and expansion: X/5

Ideal buyer: [job title, company type, employee range, technical/business signal]
Current trigger: [specific event/release/failure/pricing/regulation/platform shift + evidence from today's files]
The paid offer: [narrowly scoped audit/setup/pilot/implementation sellable immediately]
Starting price: [realistic, prefer ≥$500; reject if it can't credibly command $500]
Delivery in 1 to 5 days: [specific deliverables, tools, boundaries, what buyer receives]
Why they will pay: [ROI, reduced risk, cost savings, revenue recovery, reliability, time saved]
How to find 50 prospects this week: [specific LinkedIn titles, GitHub searches, directories, tech signals, communities, job-post keywords]
7-day validation plan: [1 proof asset today, 2 build prospect list w/ exact searches, 3 outreach using the trigger, 4 defined paid pilot, 5 minimum validation threshold]
Standardization path: [→ implementation package → retainer → managed service → software product]
Risks and boundaries: [technical limits, sales-cycle, legal/compliance, vendor dependency, what must NOT be promised]
Evidence: [exact filenames + specific supporting facts from each]
```

## Priority Categories
Only force ideas from categories the day's files support:
1. AI cost governance, FinOps, model routing, inference optimization
2. Agent security, coding-agent data leakage, prompt-injection testing, AI governance
3. Agent reliability, MCP tool optimization, agent QA, RAG, memory/context optimization
4. Private/open-weight AI deployment for one narrow business workflow
5. AI search visibility, AEO, crawler policy, publisher adaptation, content-distribution infra
6. Code quality/vulnerability/accessibility/security/technical audits combining automated tools + expert review

## Required Sections After Ranked Opportunities
1. **# Rejected Ideas** (3-8 items): each with name, why rejected, which quality gate it failed, whether it could become viable later and what would change. Prevents weak/trendy/low-ticket/legally-risky/duplicate ideas slipping in.
2. **# Best Bet This Week** (ONE only): why it beats the others, exact offer to sell first, exact starting price, ideal first 25 prospects, one proof asset to create today, exact outreach angle, ONE business-real validation metric (paid pilot / 3 booked calls / 5 pain-confirming prospects). NO vanity metrics (views, likes, followers, free signups).

## Save + Delivery
- **Save:** `Desktop/LOW BUDGET MONEY MAKING OPPORTUNITIES/high-value-money-making-opportunities-YYYY-MM-DD.txt`. If it exists, use `-v2`, `-v3`, etc. Do NOT overwrite. Verify by reading back first ~12 lines.
- **Email + Telegram:** follow the `email-sender-cron` skill (folder path, subject `High-Value Money-Making Opportunities - YYYY-MM-DD`, body must contain # opportunities + best bet + startup cost + time to first paid validation + "report attached", sign `- Bill`). The email-sender-cron skill also documents the SMTP pre-flight audit, single/multi-attachment patterns, and the cron auto-delivery rule (final response IS the Telegram message, do NOT call `hermes send`).
- **Final response** per FINAL RESPONSE RULE: 1) # qualified opportunities, 2) best bet, 3) saved file path, 4) email delivery status, 5) Telegram delivery status, 6) any failure preventing delivery. Do not paste the full report into chat.

## Next-Offer Rescue Shortlist (pre-checkable $500 offers modeled after deliverability rescue)
When Vinny asks to mine the existing `MONEY MAKING OPPORTUNITIES` archive (not TODAYS DATA FILES) for the next sellable offers, apply these four filters in addition to the quality gate: easy for a business owner to understand in one sentence, addresses a problem most businesses actually have, not many people offer a standalone fix for it, and you can programmatically verify the business has the problem before emailing so every outreach is specific and honest. The live template is `phantom-byte.com/email-deliverability-rescue` at $500 flat and 90 minutes of work, email only, no calls, with a monthly monitoring upsell; copy its page structure exactly: headline, price, three questions, diagnostic table of failure modes, what you get for $500, what you will not promise, who it is for, monitoring upsell, and free-findings CTA. Each idea needs a step-by-step build plan, the exact pre-check API or fetch that makes it qualified, the scripts to write (scanner plus findings sheet per offer, same CSV shape as `email_scan.py`), and the prospect source. Source path on WSL is `/mnt/c/Users/<user>/OneDrive/Desktop/MONEY MAKING OPPORTUNITIES` and contains 30 plus dated `high-value-money-making-opportunities-*.txt` reports plus `offer-pages/email-deliverability-rescue.html`; read at least 5 recent reports and grep titles with `^# [0-9]` to cover breadth before picking. Deliver as a text report with no hard-wrapping per Article 14, verify with `awk '{ if (length($0) > m) m = length($0) } END { print m }' <file>`, attach it via IONOS SMTP `smtp.ionos.com:587` as `hello@phantom-byte.com` using `PHANTOMBYTE_SMTP_PASS` from `~/.config/phantombyte/mailer.env`, sign the email as instructed (Frank for this workflow, Bill for the daily cron), and notify on Telegram that the email was sent. See `references/next-offer-rescue-shortlist.md` for the full checklist and prospect-verification patterns.

## Reviewing Offer Reports Other Agents Produced (FIFI / KARMA / FRANK)
When Vinny forwards two or more top-5 offer reports from his other agents and asks which is best, to rate them, or to pick the single best idea, answer all three parts in one pass with no questions back: rate the REPORTS best to worst with one reason each, rank EVERY idea across the reports in a single list with one line each, then name the single best idea, defend it, and state its honest catches.

Judge the reports on executability rather than on the dollar size of the ideas in them: email-only, $0 new spend, a defect verifiable before outreach, fixed price, no calls, and reuse of the existing `money_ideas` pipeline (scan script plus findings sheet plus IONOS scheduler) outranks a higher-ticket idea that needs a product built first or access to a client's machines.

Checks expected on every comparison:
- Duplicate detection ACROSS reports, not only within one. Two agents independently proposing the same offer at the same prices is the common case; give the idea one list entry and name both sources.
- Recycled ideas: an offer that matches the archive's own earlier "best bet" is not a new idea; say which report it came from.
- Ideas that are already live PhantomByte services. Before endorsing any offer, check it against the services already sold (the deliverability rescue page, the pricing on `phantom-byte.com`) and against the numbers in this skill. If it is the same business under a new name, say so first and plainly, then compare only the real deltas: price architecture, what is actually delivered, and whether the report invented a capability the live service deliberately refuses (placement testing, guarantees, certifications). Any price or claim that contradicts the live offer is the report's error, not a new option, and a monitor priced at a fraction of the real retainer is a volume-versus-ticket decision rather than a new opportunity.
- File integrity of each delivered report. A paste-broken report whose sections repeat many times is a defect worth one line, and it lowers that report's rating. Count unique lines against total lines rather than reading it through.
- Name the pick's operational catch as well as its strength (dashboard access needed, the owner must complete a step themselves, a long security review), because Vinny builds from these picks.

The winning single idea follows Vinny's own filter: largest buyer pool verifiable before outreach, cheapest pre-check, a defect invisible to the owner but provable by the seller, a fix the owner can see the same day (that becomes the testimonial), and a flat price with a monthly monitor after it.

## Voice / Style
Report body uses no em dashes (use commas/periods/parentheses). Signature `- Bill` is required only in the EMAIL body for the daily cron variant (an em dash here is intentional per email-sender rule); the next-offer shortlist signs as instructed, currently Frank.

## Pitfalls
- Duplicate-check laziness is the #1 failure mode. Always read the prior day's report + grep the prior week's titles before accepting a candidate.
- Never present an existing PhantomByte service as a fresh opportunity. Repackaging the deliverability rescue as a titled product with a $29/mo monitor and a placement check is the same business with wrong numbers, and Vinny spots it immediately.
- Do NOT invent model specs, benchmark numbers, or cost figures. Every stat must trace to a data file (cite the filename + fact).
- Don't force an idea from every priority category, only from categories today's files actually support.
- A vendor feature that makes the service redundant is a rejection, not an opportunity, unless there's a real integration/audit wedge.
