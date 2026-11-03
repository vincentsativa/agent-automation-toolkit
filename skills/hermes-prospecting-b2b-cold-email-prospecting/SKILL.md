---
name: b2b-cold-email-prospecting
description: Use when prospecting needs verified-defect domain screening.
---

# B2B Cold Email Prospecting (Defect-Qualified)

Class-level procedure for building a prospect list where the pitch only works
on a domain that VERIFIABLY has the problem: source the domains, screen them
over public DNS, resolve a real human contact at each, and respect the
compliance line. One agent, one pass; deliver a plan or a sheet, never send
unless sending is explicitly requested in that turn.

## Always-on rules

- **Check a source's terms before building any collection step on it.** If the
terms forbid automated extraction or outreach use, the source is
disqualified even when the data is visible in a browser. Verdict table in
`references/sources-and-compliance.md`.
- **Every defect claim must come from a live scan of that domain's own DNS.**
Never generalize, never fabricate a finding. The first line of the cold email
names the specific defect, so an unverified finding kills the pitch's entire
premise.
- **Read the actual source text before citing a terms rule, a price, or a legal
limit.** Fetch the terms page or statute, quote the operative clause, and mark
anything not verified as UNVERIFIED in place. No guessed prices, no
remembered penalties.
- **Vet every GitHub repo via live API metadata before it enters a plan**
(stars, pushed_at, license, archived). No repo cited from memory. See
`references/sources-and-compliance.md` section 4.
- **Where unsure of a fact, say so in the deliverable instead of guessing.** A
named source with a real URL beats a description of a category.
- **B2B addresses only.** Never personal consumer addresses. No phone numbers
  anywhere in any prospect artifact (hearing loss; email-only contact).
- **Rank target verticals by primary loss data, not by intuition.** When asked
  which industries to pitch a verified defect to, the evidence is the annual
  FBI IC3 report (a government PDF with per-crime-type losses and per-industry
  incident rankings) plus the platform vendor's own enforcement rules (Google's
  sender guidelines, Microsoft Threat Intelligence advisories). Trade press
  carries the per-industry incidents. Never answer this from a general sense of
  who "probably" has the problem. Procedure and the worked evidence base are in
  `references/vertical-evidence-and-sizing.md`.
- **Split the pitch by which failure the defect actually is.** A record defect
  produces two different sales: outbound mail getting filtered (the buyer is
  anyone sending volume, and the platform rules define the bar) versus the
  domain being spoofable (the buyer is a firm that moves money or client
  documents over email). Same defect code, two openings, two buyer sets. The
  Google 5,000-messages-a-day enforcement threshold means the small local firm
  is almost never the outbound-enforcement target, so pitching them
  deliverability is the wrong opening; pitch them spoof protection.
- **When Vinny says he has his own scraping/sending methods and wants the business side, do not prescribe volume, cadence, or pipeline tooling** — express money math and workflow per 100 or per batch and defer infrastructure to his existing pipeline.
- **Outreach copy must report only the observed submission, never extrapolate to all prior leads.** A failed test proves the form failed on that submission; it does not prove every previous lead was lost or that the owner's inbox was empty. Report the page message, the endpoint, the status, and the response snippet, and stop there.
- **Label every checklist item as OUTSIDE-MEASURABLE or REQUIRES-ACCESS.** The notification recipient for WordPress form plugins (Contact Form 7, WPForms, Gravity Forms) generally requires administrative access to verify and is not reliably visible in public page source — never present it as page-source-verifiable. Similarly, a submitter-facing confirmation in your test inbox is outside-measurable only where advertised; owner-side notification delivery is requires-access.
- **A 200 OK does not prove delivery.** Define success as the handler's documented success signal (e.g., CF7 mail_sent, WPForms confirmation payload, Formspree success JSON) plus, when authorized access is available, an independently verified inbox or entry-log arrival. Without authorized access, report only the handler response.
- **Revenue math is illustrative until replaced with measured rates.** The 3% reply and 20% close assumptions are placeholders, not validated conversion rates — at those rates 100 qualified prospects produce an expected 0.6 sales and, at 20% care-plan uptake, 0.12 care plans per 100, so ten active care plans requires roughly 8,333 qualified prospects at constant rates. Track qualified rate, reply rate, positive-reply rate (interested/total replies), close rate, and care-plan take rate as separate metrics and replace every assumption with measured values. Day-30 care-plan counts are ambitious goals from zero, not forecasts.
- **The deliverable shape for a plan:** one file, emailed to
hello@example.com via the email-sender skill, with a plain-language
summary in the body; never paste the full text into chat or Telegram.

## Procedure

1. **Source.** OpenStreetMap via OpenLeads `local` (free, ODbL permits it),
state business registry open-data APIs (Socrata JSON, no key), the company's
own contact page, chamber/exhibitor directories (manual, per-site terms
check). Paid fallback: a prospecting vendor like Hunter. Disqualified outright:
LinkedIn (agreement bans scraping), OpenCorporates (personal use only), WHOIS
as a contact source (registrant data redacted by default), any purchased list
without per-address provenance.
2. **Screen.** Run the DNS scanner over every domain BEFORE any email is
composed. Qualification rule: MX present plus any one defect D1 to D8, in
`references/sources-and-compliance.md`. Carry the defect code per row so the
email's first line names it. No MX means no reply path, never a prospect.
3. **Contact.** Company's own published contact page first; enrichment with a
person NAME plus domain second (name is required, company+domain alone
returns nothing); manual contact-page pass for the misses; role addresses
(info@, hello@) as flagged second-wave fallback; pattern guesses last and only
with SMTP verification. Verify every address over SMTP; unverified addresses
never enter the send file.
4. **Compliance-check the send script itself.** Before any first send, read the
actual template for a physical postal address and an ad identification
line; both are commonly missing from hand-rolled outreach scripts and both
are per-message CAN-SPAM violations. A greeting function that always returns
"there" undercuts a defect-specific pitch; feed the contact's name. CAN-SPAM's
concrete limits are in `references/sources-and-compliance.md` section 3.
5. **Deliver.** Plan or sheet to file, email it, confirm in chat. When the
pipeline includes sending, dry-run first and read every rendered email end
to end before the live flag.

## Choosing the vertical (when the prospect set is not yet fixed)

When the ask is "which industries should I pitch this to," the deliverable is a
ranked list with a named, cited reason per vertical, not a category brainstorm.

1. **Get the loss baseline from the government report.** Fetch the current FBI
   IC3 annual report PDF, extract the text, and pull the per-crime-type loss
   table plus any per-industry incident ranking. Two things to look for: the
   crime type that matches the defect (business email compromise, phishing and
   spoofing) and its year-over-year movement, and any chart that ranks
   non-critical-sector industries by reported incidents. That second chart is
   the single most useful artifact for this task, because it ranks small
   businesses by industry rather than by size.
2. **Get the enforcement bar from the platform vendor.** Google's "Email sender"/
   "Email sender guidelines FAQ" page states the threshold and the requirements
   in its own words, including the enforcement date. Microsoft's Threat
   Intelligence blog carries the mechanism for how a misconfiguration lets
   spoofed mail through. Quote the vendor, do not paraphrase a blogger.
3. **Get per-industry incidents from trade press**, one trade publication per
   vertical (real estate, legal, insurance, freight, distribution). Named human
   journalists only, per `research-source-standards`.
4. **Rank in two tiers plus a disqualify list.** Tier one is high pain, no IT
   staff, high value per email. Tier two buys after they connect the symptom.
   The disqualify list matters as much: enterprises with an IT department, and
   anyone whose real problem is sending to people who never opted in. Say the
   disqualification explicitly rather than softening the list.
5. **State the gaps.** A vendor report that the fetch could not reach is
   reported as unreachable by name, never filled in with a guess. "PowerDMARC
   publishes 2026 US DMARC adoption figures and their syndicated hosts blocked
   the fetch" is an acceptable line in the deliverable.

## Pitfalls
- **SPF lookup counting has two opposite errors.** Counting only the flat TXT
record undercounts (include: chains never followed, so nested providers hide
their lookups), and adding ip4:/ip6: tokens overcounts (those mechanisms cause
zero DNS lookups). Use checkdmarc (github.com/domainaware/checkdmarc,
Apache-2.0) which follows includes and counts per mechanism, or recurse the
includes yourself.
- **"No DKIM found on common selectors" is a routine false negative** (custom
selector names), so it never qualifies a domain on its own; it only upgrades
copy for a domain qualified on SPF/DMARC defects.
- **A wildcard TXT record answers every _domainkey probe**, producing false
DKIM hits; probe with a random selector name to detect it, and treat DKIM as
unverifiable behind a wildcard.
- **Clean the sending domain's own records before pitching deliverability.**
Mailing about SPF/DKIM defects from a domain with a stale include or dead
selectors is a credibility defect in itself.
- **Vendor pricing pages render plan structures but bury per-call numbers**;
if the exact figure matters, mark it UNVERIFIED rather than reading tea leaves
from a JS-rendered page that returned no parseable rows.
- **Unlicensed GitHub repos (no LICENSE file) are unusable regardless of
quality**, and archived repos are dead; a dead repo costs more than building
the small piece you need.
