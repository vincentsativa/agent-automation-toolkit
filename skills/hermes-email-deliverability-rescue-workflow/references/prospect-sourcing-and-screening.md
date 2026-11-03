# Sourcing and screening prospects for the deliverability offer

Condensed reference for the steps that run before any email is written: where the domains come from, which ones are real prospects, and how many are needed. Measured numbers come from live runs, not projections.

## 1. Get business domains free: OpenStreetMap Overpass

```
[out:json][timeout:180];
(
  nwr["website"]["name"](27.80,-82.55,28.10,-82.30);
  nwr["contact:website"]["name"](27.80,-82.55,28.10,-82.30);
  nwr["email"]["name"](27.80,-82.55,28.10,-82.30);
  nwr["contact:email"]["name"](27.80,-82.55,28.10,-82.30);
);
out tags;
```

- POST `{"data": <query>}` to `https://overpass-api.de/api/interpreter`. A bare requests call returns HTTP 406, so always send a real User-Agent: `PhantomByteProspectScan/1.0 (mail deliverability screening; contact hello@phantom-byte.com)`.
- Measured on the Tampa Bay bbox above: 2,221 records carrying a website tag, 1,246 to 1,249 distinct domains, in one call. Swap the bbox per metro.
- The `email` and `contact:email` tags are the quiet win: 160 records carried an email value covering 141 distinct domains, 29 of which were in the qualified set. Those addresses come from the business itself and cost nothing to collect, so use them before scraping any page.
- Normalize: strip the scheme, keep the host, drop a leading `www.`, lowercase, keep only real hostnames.
- License ODbL 1.0, `https://www.openstreetmap.org/copyright`. Attribution is the operative duty for a private screening extract.

## 2. Screen out chains: Tranco, not location counts

`https://tranco-list.eu/top-1m.csv.zip` is a public 1M-domain popularity ranking. A registrable domain in the top 100,000 is a national brand.

- Collapse to the registrable domain before lookup (`locations.x.com` and `x.com` are the same business), or the local store-finder page of a chain passes the check while its brand parent is blocked.
- Measured on the 243 qualified rows: the top-100k block dropped 30 chains (`7-eleven.com`, `arbys.com`, `cvs.com`, `apple.com`, `chick-fil-a.com`, `amtrak.com`, `autozone.com`, `amctheatres.com`, `baycare.org`, `choicehotels.com`) and kept every local business.
- **Do not use location counts from the geographic extract.** Counting how many times a domain appeared in the bbox flagged local single-location businesses (`1920yborcity.com`, `acropolistaverna.com`) as chains, while `advanceautoparts.com` appeared once and slipped past. The count measures mapped branches in one bbox, not the size of the business.
- Also drop by name: franchise locator subdomains (`locations.`, `locators.`, `find.`, `restaurants.`, `stores.`, `pizza.`, `shop.`, `order.`, `menus.`), `.gov` and `.mil` hosts, and the aggregator hosts (`wixsite.com`, `menufy.com`).
- Keep the blocklist on disk as a reusable `brand_blocklist.txt` so a scan does not re-download the 9 MB zip.

### 2b. Buyer fit: the second filter, and the reason rank alone is not enough

Rank answers "is this a chain". It does not answer "is this our buyer". `prospect_fit.py` runs both tests, and `outreach.py` calls it on every run so a bad prospect never reaches a draft.

- **Cutoff: the whole Tranco top 1M, not the top 100k used at harvest.** Everything between 250k and 1M in the measured set was still a multi-office firm or an institution, and every genuine local business sat outside the list entirely. Measured on the sendable contacts: the filter dropped 9 by rank (`curaleaf.com` #105,691, `adesa.com` #122,766, `bowlersmart.com` #124,053, `baycare.org` #141,862, `bluepearlvet.com` #156,809, `columbiarestaurant.com` #369,478, `chromalloy.com` #547,399, `brightonjones.com` #553,831, `bernssteakhouse.com` #972,980) and 5 by mailbox.
- **Function mailboxes are the signal rank cannot see.** A department desk means an organization with staff, not an owner reading his own inbox: `careers@`, `registrar@`, `franchise@`, `mediarelations@`, `marketing@`. Match the local part and its first dot/dash/underscore segment against the function list, because `marketing.team@` and `marketing-team@` are the same desk as `marketing@`.
- **Also drop by shape:** hosted site builders and aggregators (`wixsite.com`, `menufy.com`), chain store-locator subdomains, `.gov`/`.mil` hosts, and educational institution hosts.
- **Judge only rows that carry a contact address.** A no-address row is skipped later regardless, so including it inflates the drop count into a number that no longer describes the list the filter changed. Pass those rows through untouched.
- **Err toward keeping.** A false drop silently deletes a real local business and costs a sale; a false keep costs one send out of twenty. Specific rules, never a whole-TLD cut, so a genuine local nonprofit survives.

Report the effect as a count with per-row reasons (`--fit-report`), and report it only after a real run. Do not raise a marginal prospect as a question for Vinny: dropping it is the job this filter exists to do.

## 3. Get a contact address

Order of preference:

1. The OSM `email` / `contact:email` tag, if the bbox query carried it. One API call, no scraping.
2. The business's own contact page: `find_contacts.py`, which tries the home page plus `/contact`, `/contact-us`, `/about`, `/about-us`, `/team`, `/our-team` and similar.
3. A role address (`info@`, `contact@`) only when nothing more personal exists.

Measured yield, current and verified live on 2026-09-20: **84 of 243 qualified domains, 34.6 percent.** Broken out: 29 labeled person, 39 role, 16 osm, 128 no address, 31 skipped. Of the 212 real prospects (243 minus the skips), it is 39.6 percent. Treat 34.6 percent as the planning number. The person/role split now comes from `address_shape`, which reads the mailbox local part rather than a page name, so it is usable; the separately extracted name column remains a hint only.

Do not harvest from WHOIS or RDAP: Verisign's RDAP terms forbid mass-solicitation use and registrant data is redacted anyway. Do not build an address from a name pattern, which is the dictionary-attack line in 15 USC 7704(b)(1)(A).

## 4. How many domains to scan

The send ceiling is 20 a day, and it governs everything upstream.

- Qualification rate, measured twice: about **81 percent** (829 of 1,003, and 243 of 300).
- Reachability rate, measured live on 2026-09-20: **34.6 percent** (84 of 243, or 39.6 percent of the 212 real prospects once the 31 skips are excluded).
- Combined, roughly one sendable contact per 2.9 domains scanned, so about **58 domains yields a day's 20 sends** and about **290 yields a working week** of 20-a-day sending. That climbs sharply when the batch starts from published OpenStreetMap addresses instead of page scraping: 121 of the 150 domains in `scan_next_150.txt` (80.7 percent) already carry one. Vinny sets the batch size; ask rather than picking it. The number approved for the first real run was 300.
- Run the contact harvest only over the qualified rows, and only after the scan. 829 qualified domains with no reachable address is a worthless artifact.
- Never start a bulk scan or harvest that was not ordered. Testing a script is a handful of known domains, not a metro.

## 5. Sources that are disqualified, with the reason

| Source | Verdict |
| --- | --- |
| Google Places / Maps Platform | Forbidden twice: Terms 3.2.3(a) bars exporting or bulk-downloading places content, and the AUP bars using the services to facilitate unsolicited mass email |
| LinkedIn | User agreement forbids it |
| WHOIS / RDAP | Verisign RDAP terms forbid mass-solicitation use, and registrant data is redacted |
| ChamberofCommerce.com | Terms forbid it |
| Chamber or trade association member rosters | Not usable without written permission from that association |
| Florida Sunbiz bulk data | Allowed, but names only: no domains, no email addresses. A supplement, never the spine |
| Licensed list vendors (Apollo, Hunter, Data Axle) | Allowed under their terms, which pass the compliance duty to the buyer. Buy only for domains that survived the screen |
