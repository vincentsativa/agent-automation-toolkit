---
name: local-small-business-clients
description: Use when Vinny wants quick script cash from local clients.
---

# Local Small-Business Clients (Quick Script Cash)

Vinny's goal: **small, fast, easy cash** for little scripts and same-day fixes, NOT a freelance career. He builds systems; this is a side channel. The buyers are non-tech-savvy small business owners who pay cash for a specific problem solved today.

## Core principle
Non-tech-savvy small business owners never search for freelancers. They don't know what Upwork is. They ask their neighbor, their local Facebook group, or their barber. **Go where they already are, not where freelancers hang out.**

## Best channels (in order)
1. **Local Facebook groups** (town + "small business owners of [town]"). Owners post "anyone know someone who can fix my website/email/invoicing?" daily. Answer those directly.
2. **Nextdoor**, hyper-local, full of owners asking for help. Trust is built in: being local IS the credential. Join by verifying your address.
3. **BNI / chamber of commerce / local networking**, the referral engine.
4. **Walk-in / direct outreach** to local shops (barbershops, salons, plumbers, contractors, restaurants). Point at one specific pain, offer same-day flat-fee fix.
5. **Craigslist "computer services"**, old school but still works for this exact buyer (50+, runs a shop, never left Craigslist). Zero competition from the $5 crowd, no platform fees, buyer is pre-qualified.

## The pitch that works
Don't sell "I'm a freelancer." Sell "I'll fix your [specific problem] for $X, done today." Owners buy outcomes, not services. Flat fee, cash or Venmo, paid on completion.

## The repeat play
Build the script once, sell the same fix to ten local businesses. Pure margin after the first one.

## No-phone rule (CRITICAL, governs every channel and every idea)
**Vinny has 60 percent hearing loss and does not take phone calls.** Never build an ad, an intake flow, or a sales step that requires a call. State "email only, I do not take phone calls" in every ad, offer page, and first reply. It is a filter that removes buyers needing hand-holding, not something to apologize for. Where a normal process wants a call, substitute email plus a recorded screen-share walkthrough or a written one-pager.

## Craigslist phone-number rule (CRITICAL)
**Do NOT put a phone number in the Craigslist ad body.** Craigslist anonymizes email replies by default and its filters flag ads with numbers aggressively. Let buyers reply through the relay and keep the whole job in email. (Nextdoor tolerates a number, but publishing one invites exactly the calls he cannot take, so do not.)

## Safety filtering (Craigslist especially)
- Default to remote delivery with written authorization; meet at their business only when the job genuinely needs hands-on hardware. Never wire money or take "overpayment" checks.
- Get the problem described in their own words in an email before quoting.
- Flat fee, paid on completion, cash or Venmo.
- Test a prospect's broken form once, with your own contact details. Never submit it repeatedly.

## Diagnose before you contact (highest-conversion play in the whole skill)
For any fix that can be diagnosed remotely (mail records, dead contact forms, mobile layout, HTTPS, page weight), run the check across a batch of domains first and contact only the ones with a real specific break. "Your contact form does not send you anything" and "your domain has no DMARC enforcement" beat every generic service pitch, because the email already carries a true finding about their business. Diagnose a hundred in one evening, fix in 60 to 90 minutes, price $250 to $500 flat. The deliverability rescue is the fastest path from cold email to cash in this playbook.

Run the diagnosis as a script, never by hand: one file per checker, one CSV out, so the prospect list and the email copy come out of the same run and every claim in the email is something the run actually observed. See `references/prospect-diagnosis-scripts.md` for the DNS-over-HTTPS recipe, the DKIM wildcard and revoked-key traps, the form-submission nonce method that proves a form is dead, and the verification discipline to run before shipping any checker.

The buyer set is wider than local shops. B2B lead-gen agencies and cold-email operators (their entire product is inbox placement), newsletter operators, and SaaS firms whose transactional mail lands in spam all buy the same rescue at the same price, and they are reachable by email because they live in it.

Scan your own sending domain with the same checker before the first outreach batch. Your own deliverability underwrites every channel in this skill, so a soft-fail SPF or a monitor-only DMARC on your sending domain is a business-critical defect, not a curiosity.

## Ad templates
See `references/local-tech-ads.md` for the Craigslist (direct/transactional) and Nextdoor (warm/neighborly) ad templates. Both target the same buyer with the same flat-fee pitch, different tone per platform.

## Email delivery
When Vinny asks to email the ads, use the `email-sender` skill (IONOS SMTP to hello@phantom-byte.com). Write the file with a proper extension first, then send as attachment.
