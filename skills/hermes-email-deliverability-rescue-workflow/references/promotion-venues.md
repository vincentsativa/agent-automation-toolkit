# Promotion venues for the deliverability offer (email + community outreach)

Where the deliverability conversations happen online, and the angle for each. The 28-venue list below was verified against live sources: every venue exists, and the thread titles and member counts were confirmed live. Re-verify any venue's claim with a live search before quoting it in new material; the rule is the same as everywhere else in this skill, live query beats memory.

## The universal reply formula

Every venue has people describing symptoms ("open rates dropped," "clients say my invoices go to spam") and every venue is full of generic answers ("clean your list," "avoid spam words"). The offer wins with: one sentence of record-level diagnosis, one Socratic question that makes them check their own DNS, then the service. Never paste the same paragraph in two places; platforms and people overlap. Each venue also has self-promotion rules, read them before posting a link.

## Venues

### Reddit
- **r/Emailmarketing (~122k members)**, the most active public deliverability help desk. Live threads: deliverability sudden tanking, mail landing in spam, ESP-specific breakdowns. Angle: the diagnostic order people skip (check DMARC p=none with no rua first). Earn the mention with a useful comment; the sub tolerates a service mention when the comment stands alone.
- **r/coldemail (~58k)**, cold email operators mid-burn after adding a third sending tool; SPF lookup counts past 10, warmup panic. Self-promotion is banned, so link never goes in a post. Angle: "your stack, not your copy", most posters blame copy or tool when SPF silently hit permerror from nested includes. Free findings sheet CTA works in comments.
- **r/GrowthHacking**, operators, not beginners. Angle: tie deliverability to pipeline revenue.
- **r/smallbusiness**, non-technical owners whose invoices and booking confirmations go to spam. Angle: plain-English cost framing ("customers think you ignored them"). Socratic question opener beats any link.
- **r/Entrepreneur**, deliverability surfaces inside "my launch flopped" threads. Angle: DNS records as cheapest launch insurance.
- **r/Shopify**, abandoned-cart and order emails filtering to spam; owners get told to "contact support" and go in circles. Angle: name the missing branded sending domain or the p=none record.
- **r/WordPress**, Contact Form 7, WooCommerce order emails, password resets going to spam via unauthenticated host PHP mail. Angle: "your form emails are invisible." Flat $500 same-day fix reads well to this crowd.
- **r/msp (~247k)**, MSPs manage dozens of small business domains and hit record problems across the client base. Live threads exist on spam-despite-valid-SPF/DKIM/DMARC. Angle: white-label referral partner, not a buyer channel. Worth more per hour than buyer posting.

### Slack and vendor forums
- **Email Geeks Slack (email.geeks.chat, 28k+)**, dedicated deliverability channels; SPF flattening and DMARC policy debates weekly. Angle: peer positioning, answer questions, never blast. Application-gated join keeps spammers out, so members who see a good answer trust it.
- **Instantly Slack Community (instantly.ai/slack-community, 10k+)**, outbound professionals, deliverability is their #1 recurring complaint, dedicated warmup/deliverability channels. Angle: same-day agency rescue.
- **Klaviyo Community (community.klaviyo.com)**, dedicated Deliverability board, live "transactional email going into spam" threads; official answers rarely name the DNS record. Angle: the missing-record diagnosis nobody gives them.

### Forums and Q&A
- **Shopify Community forums**, live threads on emails landing in spam and the DNS records that fix it. Angle: done-for-you service for a non-technical but paying-accustomed crowd.
- **HubSpot Community (community.hubspot.com)**, dedicated Email Deliverability board with live "emails sent in HubSpot goes to spam" threads. Angle: "your email tool is not the problem, your records are."
- **Stack Overflow**, the classic "email goes to spam despite 10/10 mail-tester" question class; developers with failing transactional mail. Angle: developer-to-developer, exact record fix in code terms, offer link in profile only.
- **Super User / Webmasters / Unix Stack Exchange**, self-hosted Postfix and Exchange owners hitting the Gmail/Outlook wall; tagged spf question sets going back years. Angle: the authentication sequence; flat-fee service for those who would rather not touch DNS.
- **Quora (Email Marketing / Deliverability)**, "why are emails from my new business domain going to spam" gets thousands of views with thin answers. Angle: the new-domain record checklist; a thorough answer pulls views for years.
- **WordPress.org support forums**, "emails are delivered to spam" is a chronic repeated topic; the WP Mail SMTP ecosystem exists because of it. Angle: the plugin-gap, people install WP Mail SMTP and still fail on a missing DKIM selector.

### Mail-industry professional (referral and authority, not selling)
- **Mailop mailing list (mailop.org)**, the most concentrated deliverability expertise online; postmasters at major receivers debug failures in public. Angle: lurk, learn, build relationships with overflowed consultants. One respected participant's referrals beat a month of Reddit posting. Also a free early-warning feed on filtering changes.
- **Word to the Wise blog and Deliverability Summit (wordtothewise.com)**, where the deliverability consultant community gathers; the summit runs annually with a published speakers page. Angle: comment as a practitioner; authority play over time.

### Social platforms
- **X / Twitter**, #EmailGeeks, #EmailDeliverability hashtags; practitioners answer questions in public. Angle: publish sanitized real findings (record string before/after) as threads; link in bio; every reply is a free mini audit.
- **LinkedIn**, agency deliverability posts pull real engagement from agency owners. Angle: the agency math ("one client's domain in the spam folder costs more per month than the fix costs once"). Post the diagnosis, let comments carry the pitch.
- **Facebook groups**, GoHighLevel agency groups have a literally recurring "how to set up email servers and not land in spam" thread; The Email Marketing Show community is lighter, full of course creators with broken newsletters. Angle: "reply with your domain, I will tell you what is broken for free" as the entry move.

### Developer and startup
- **Indie Hackers**, live deliverability how-to posts and discussions. Angle: founder-to-founder; newsletter revenue is tied to inbox placement, the ROI math is one line; share our own domain's record story as proof.
- **Hacker News**, live DMARC/spam threads and Show HN deliverability tools. Angle: technical deep-dive comment, cite RFC 7208 lookup counting and the p=none trap, mention the service in passing. One good comment sends years of trickle traffic.
- **dev.to**, active SPF/DKIM/DMARC debug posts every year. Angle: the migration angle ("you switched providers and never moved the DKIM records"); publish a how-to that diagnoses and links the offer at the end.
- **Newsletter operator communities and Substack deliverability writing**, operators read these religiously. Angle: comment on deliverability posts with a real record-level observation; operators with 5k–50k subscribers are ideal buyers.

### Platform communities
- **Google Workspace Admin Community (support.google.com/a)**, live "emails going to spam" admin threads. Angle: admin-helper; these admins manage multiple small business domains and hand off fixes they do not fully understand.
- **Microsoft Q&A (learn.microsoft.com/answers)**, live Outlook sender spam threads. Angle: reputation-repair, authentication plus reputation time; position the service as the setup-records-and-monitor part of recovery.

## Sequencing
- **Tier 1, start immediately:** r/Emailmarketing, r/coldemail, Email Geeks Slack, Klaviyo Community, Shopify forums, Instantly Slack. Highest concentration of people with the exact problem; the Socratic reply format works in all six.
- **Tier 2, next:** r/Shopify, r/WordPress, WordPress.org forums, Stack Overflow, Quora, X replies, Indie Hackers, Facebook GHL groups.
- **Tier 3, slow burn:** Mailop, Word to the Wise, dev.to, HN, LinkedIn, r/msp, Google Workspace community, Microsoft Q&A, Substack comments, Super User.

## Reddit rules (ban-happy, per Vinny)
- The offer link never goes in a post. r/coldemail bans self-promotion outright; a fresh account with a service link in its profile is flagged before the comment is read.
- Working sequence: two weeks of comment-only answers to fresh deliverability threads (sort by New), no link anywhere, not even the bio. Pitch only in DMs when someone asks how to fix it or who can do it.
- The scanner is the comment's proof layer: scan the domain named in the post, reply with the actual defect code and record string. Same specific-finding mechanic as the cold email, delivered publicly.
- r/msp is the most tolerant of the Reddit venues and the natural white-label/referral play.

## Content-post rule (dev.to, guest posts, daily.dev)
- Teach-first walkthrough, real record strings from the scan CSV as evidence, skip chain domains when quoting examples. A closing offer link framed as "if you'd rather this be done for you" is accepted because the article taught the fix first. Expectation is a slow-burn SEO play, not high-intent leads; never promise leads from a content post.
- When Vinny says he will post it himself, the deliverable is the finished, verified draft emailed as an attachment, never an outline plus an offer to write. Verify the draft before sending: zero em/en dashes, zero dash-as-separator, longest line unwrapped, numbers traced to the scan CSV, and for daily.dev every rule in `dailydev-and-content-venue-submission.md`.
- **Section-header format is venue-specific, so pick by venue and never by habit.** dev.to uses the `// HEADER` plain-prose shape; a daily.dev post uses short ALL CAPS plain lines with no markdown syntax at all, matching `phantom-byte-writing-style`. Applying one venue's header style to the other is a visible tell that the piece was not written for that venue.
- **Read the target venue's own rules live before drafting, not just the venue's angle in this list.** daily.dev's rules decide the whole shape of the post and they are not the dev.to rules: self-promotion as the primary purpose of a post is an explicit rejection, the AI-writing clause makes padded framing prose a real risk, corporate and personal blogs are excluded from Suggest a Source while Squads and direct posting are open, and the priority is niche sources under stricter review for mainstream content. The fetch path, the rule list, the post shape, and the pre-send checks are in `dailydev-and-content-venue-submission.md`.

## Email body for a content deliverable
When the deliverable is a content post, the covering email states what the file is, which venue's rules shaped it, which file the numbers came from, and the checks already run. It does not restate the post. The Telegram message afterwards is a doorbell and carries only that the email went out.

## Verification rule for venue research
When asked where conversations happen, do not write entries from inference. Verify each venue with a live search for its current deliverability threads (site: or community-name searches), pull real thread titles and member counts, and state the venue's self-promotion rules from its own rules page. The first pass at this list shipped entries that had to be corrected afterward because they were written from search-result titles rather than checked threads; the verified pass is what he accepted.
