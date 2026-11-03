# Classified ad venues for the deliverability offer

## When this applies

Vinny asks for an ad to post on a classifieds site (Oodle, Craigslist, the rest) and wants it emailed to him so he posts it later. He is not asking you to post: never create an account, never place a listing, unless he orders that directly. The deliverable is one file with the ad text, the account setup step, the place to post it, and the rules it had to obey, emailed as an attachment.

## The venue's own rules decide the shape of the ad, so read them live before writing a word

The classified copy has a hard constraint set that the email and the offer page do not, and guessing it produces an ad that gets removed. Fetch the venue's Terms, Content Policies, and FAQ with scrapling and quote the lines you are complying with.

Oodle's rules, read live from `https://www.oodle.com/info/terms/` and `https://www.oodle.com/info/contentpolicy/`. Watch the paths: `/terms/` 404s and `/info/terms/` is the live one, and the content policy is at `/info/contentpolicy/`, not `/content-policies/`. A guessed path on this site returns a real 404 page from its static host, so a 404 means wrong path, not blocked fetch.

- Registration is required to place a listing, one account per member. There is no standalone register URL; the working route is `https://www.oodle.com/post` and the Post a Free Ad button, which fires the site's login and registration prompt. A guessed register URL returns 404 on their server.
- Posting the same ad in more than one region is prohibited. So is posting the same item or service in more than one category, and multiple listings whose content is substantially similar.
- **Listing with links to external lead generation forms is prohibited.** The offer page CTA is exactly that, so the ad carries no URL.
- **Email addresses in listing content are hidden, and attempts to circumvent are prohibited.** The ad carries no email address.
- Phone numbers in listing titles are hidden, and images containing any type of contact information are prohibited. The ad carries no phone number.
- Also prohibited: keyword lists stuffed in for search matching, and items used to solicit email addresses for spammy or unrelated marketing.
- The No Spam Policy (section 5 of the Terms) forbids unsolicited email advertising to Oodle addresses or through Oodle systems, with stated civil and criminal exposure. Practical consequence: reply through the venue's own messaging. Do not harvest repliers and email them from the business mailbox outside the venue.

The result is an ad with exactly one reply route, the venue's own reply button. Say that in the file plainly, with the specific edit to avoid: adding the page link or the address later is the edit that gets the listing removed.

## Where to post it on Oodle

Services, then Technical Repair & Services (the Services nav also labels it Tech Help), in the New York Area. Long Island has no separate Services area page and rolls into New York Area. Post page `https://www.oodle.com/post`, category browse `https://services.oodle.com/new-york-area/`.

## The other classified venues, verified live

Every one of these was fetched and its own rules read, rather than assumed from a listicle.

- **Locanto** (`https://www.locanto.com`) has a Computer & Tech Help category and free posting. Its Terms ban duplicate or similar ads, more than one post with the same or similar content, ads posted in multiple cities, ads under 8 words, and ads placed in the wrong category. Its paid features are described as intended for commercial advertisers, which is the upsell, not a ban on a free post.
- **ClassifiedAds.com** (`https://www.classifiedads.com`) is free with a Services section including Web Design & Tech. Its Terms carry the standard set: no unsolicited commercial advertisement, no advertising in areas not designated for it, no repeatedly posting the same or similar content, and no posting the same service in more than one category or metro area. `/terms` works, `/terms.php` and `/rules.php` 404.
- **Geebo** (`https://www.geebo.com`) is free with a Services section and the same one-category, one-metro clause. Thin traffic; treat it as a free extra, not a channel.
- **Long Island dot com classifieds** (`https://www.longisland.com/classifieds/`) is local to Vinny, which is what matters for local-business buyers. Caution: its Terms state you may not use the site for promotional or commercial purposes unless expressly allowed by the publisher. Read that line before posting and offer its business directory route instead if the ad route is closed.
- **Claz** (`https://www.claz.org`) is the source behind a large share of the Services listings visible on Oodle, including the tech repair ads. Its rules were not read live because it rate-limited the automated fetch.

Dead, verified rather than assumed: Recycler.com has permanently closed, and USFreeAds no longer operates as a classifieds site, the domain now serves an unrelated Japanese site. A "free classified sites" listicle will still name both.

## Venue-fetch technique

- Scrapling carries these sites fine. Pull the rules page, then search the text for the operative keywords (`duplicate`, `multiple`, `more than one`, `commercial`, `solicit`, `advertis`, `spam`, `service`) rather than reading the whole agreement; the prohibitions cluster in one user-conduct section.
- Sitemaps are the fast way to the real paths: `https://www.oodle.com/sitemap.xml` lists `sitemap_files/categories.xml` and `sitemap_files/site.xml`, and the footer of the Terms page lists every info page that exists.
- A 403 with a JavaScript challenge is Cloudflare, not a rule against you: that is the blocked-page-recovery case, not evidence the venue is closed.

## The ad itself: the Socratic method in a venue with no form

The ad is the same argument as the page and the cold email, and the venue's constraints do not change the argument, only the frame. Written and delivered this way.

- Title carries the unanswerable question phrased as a topic: "Business Email: What State Are Your SPF and DMARC Records In Right Now". It reads as a subject line and still asks him something he cannot answer.
- The three questions are the entire body of the argument, same three moves in the same order, uncompressed: the recall (when a client last replied to an emailed invoice), the story he told himself (sent a quote, heard nothing, assumed they were not interested), the unanswerable one (could someone send mail that looks like it came from your address today, and would anything stop it). Flat lines ending in periods, because a venue that strips markup and line breaks does not preserve any other format.
- Then one line relocating the gap to his records, one declarative paragraph with the fix and the price and the turnaround, one line offering the two minute self check, one line for the free findings offer, and one line on the work declined. That is the whole ad.
- CTA is the venue's own reply button: "Reply through Oodle with the domain you send from and I will send back a one page findings sheet for it." Never add the offer page URL or the email address to make it easier; that is the edit that gets the listing removed.
- Do not soften the questions for a public channel. The reader is the same owner with the same filtered invoice, and a cheap channel is not a reason for a watered-down version.

The method skill lives at `socratic-sales-outreach` (user-owned, so it cannot be edited from here): its three-move pattern, its rewrite rules, and its banned shapes apply to this ad unchanged. Anything learned about the method itself belongs there, not here.

## Channel honesty, which belongs in the email

Classifieds are low intent. They cost nothing, so post them, but nobody browsing a classifieds Services list is shopping for mail infrastructure work. Say so in the covering email and point at the venue list that does match the offer, which is `references/promotion-venues.md`: the Email Geeks Slack, the Klaviyo Community deliverability board, the Shopify Community forums, the Instantly Slack, r/Emailmarketing and r/smallbusiness. Do not let a classified ad read to Vinny as a strategy when it is a free extra.
