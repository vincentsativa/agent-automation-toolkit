# Next-Offer Rescue Shortlist — Reference

## When this applies
Vinny points at `C:\Users\<user>\OneDrive\Desktop\MONEY MAKING OPPORTUNITIES` and asks for the best ideas to make into next offers like Email Deliverability Rescue. This is archive-mining, not daily report generation.

## The four filters
Every shortlisted idea must pass all four:
1. Easy for a business owner to understand in one sentence without jargon.
2. Addresses a problem most businesses actually have right now.
3. Not many people offer a standalone fix — agencies bundle it into retainers or ignore it.
4. Programmatically verifiable before outreach so every email names a specific defect you measured that day.

## Template to copy
Live reference is `offer-pages/email-deliverability-rescue.html` and the live URL `https://phantom-byte.com/email-deliverability-rescue`. Price is $500 flat for one domain or one profile, fixed within 24 hours, entirely by email. Each offer page needs the same sections: headline that names the invisible problem, price plus monitoring upsell, three questions answered honestly, diagnostic table with four failure modes, what you get for $500, what you will not promise, who it is for, monitoring at $75 to $250 per month, and free-findings CTA plus direct PayPal button.

## Scanner plus findings sheet pattern
Reuse the deliverability pipeline shape for every rescue:
- One scanner script per offer that writes a CSV with `qualified` boolean, `defect_codes`, and severity, same shape as `email_scan.py`.
- One findings-sheet script per offer that reads that CSV and renders a one-page plain-language sheet, same shape as `findings_sheet.py` — every line traces to a live measurement.
- Scheduling reuses the existing IONOS path: scan batch overnight, filter to qualified, dedupe against `state.json`, schedule 15 to 20 per day, personalize line one from the live scan.
- Overpass harvest, contact finder, buyer-fit filter, stop list, and suppression handling are reused as is.

## Proven pre-check patterns
- Google Business Profile: Places Details API — opening_hours, photos length, rating, review count, website, phone, plus fetch of public Maps URL for claimed badge. Qualified when completeness score is below 60.
- Site speed: PageSpeed Insights API — mobile_score, LCP, TTFB, total byte weight. Qualified when mobile_score is below 50 or LCP is over 2.5 seconds.
- SSL and trust: curl cert inspection for expiry and SAN coverage, Scrapling crawl for mixed content http assets, header check for HSTS and X-Frame-Options. Qualified when cert is expired, www mismatch, or mixed content count is over 0.
- Broken links: crawl up to 300 to 500 internal pages, HEAD each link, compare sitemap. Qualified when broken internal count is over 5 or homepage or contact page is broken.
- ADA quick-fix: axe-core via Pa11y against homepage plus contact and booking pages for WCAG 2.1 AA. Qualified when critical plus serious is over 5 or total is over 15.

## Text report delivery
- Body paragraphs are ONE long unwrapped line per Article 14; verify with `awk '{ if (length($0) > m) m = length($0) } END { print m }' <file>` and expect the max to be well over 200. A short max means the file was wrapped and is wrong.
- Windows path on WSL is `/mnt/c/Users/<user>/OneDrive/Desktop/MONEY MAKING OPPORTUNITIES`; list files with `ls` to confirm counts before relying on memory.
- Send via IONOS SMTP `smtp.ionos.com:587` as `hello@phantom-byte.com` using `PHANTOMBYTE_SMTP_PASS` and `PHANTOMBYTE_POSTAL_ADDRESS` from `~/.config/phantombyte/mailer.env`. Use `MIMEMultipart` with attachment. Sign as instructed for the workflow — Frank for the next-offer shortlist, Bill for the daily cron.
- After the send returns SENT OK, notify on Telegram that the email was sent. Final response is the delivery channel — do not call a separate send tool for the notification.
