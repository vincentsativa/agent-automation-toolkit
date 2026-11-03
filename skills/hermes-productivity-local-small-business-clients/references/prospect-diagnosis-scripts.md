# Prospect Diagnosis Scripts

Depth for the "diagnose before you contact" step: the recipes that turn a domain list into a prospect list where every row already carries a true finding. Build these as files you keep, not as ad-hoc one-liners, because the same checker gets re-run weekly and becomes the delivery tool once a client pays.

Two checkers cover the fastest-selling services:

- **Email record scan** (MX, SPF, DKIM, DMARC) feeds the deliverability rescue, $250 to $500 flat.
- **Site check** (20 points, including form submission) feeds the AI-built site rescue, $400 to $500 flat.

## DNS lookups without dependencies

Prefer DNS-over-HTTPS over shelling out to `dig`: it needs no package install and returns JSON you can grade directly. Both of these are free and unauthenticated.

- Cloudflare: `https://cloudflare-dns.com/dns-query` with header `accept: application/dns-json`
- Google: `https://dns.google/resolve`

Query shape: `GET {endpoint}?name=<fqdn>&type=TXT`. Keep a second endpoint as fallback and retry once; one provider having a bad minute should not fail a hundred-domain batch.

Record types used: `TXT` (16) for SPF and DKIM, `MX` (15) for mail hosts. On a negative result, `Answer` is absent rather than present-and-empty, so treat a missing key as no record instead of an error.

### TXT parsing traps

TXT answers come back as quoted strings, and a long record can arrive as several quoted chunks that must be joined with no separator before parsing. Splitting the data on whitespace breaks DKIM public keys, which are long base64 blobs. Join the quoted segments, then parse.

## Grading rules that decide the grade

**SPF**
- No record at all: fail. Anyone can send as the domain.
- Ends in `+all` or `?all`: fail. That authorizes every sender including a spoofer.
- Ends in `~all`: warn. This is the soft-fail default and most senders never tighten it, so it is the single most common real finding in a local batch.
- More than 10 DNS-lookup mechanisms: warn. Receivers that enforce the limit fail the check outright.
- Ends in `-all`: pass.

Count mechanisms that cause a lookup (`include:`, `ip4:`, `ip6:`, `a`, `mx`, `ptr`, `exists:`). Do not count the trailing `all` qualifier itself.

**DMARC** (at `_dmarc.<domain>`)
- Absent: fail.
- Present with `p=none`: fail in effect. It monitors only, so spoofed mail still delivers. This is the finding to lead with, because the client believes they are protected.
- `p=quarantine`: warn.
- `p=reject`: pass.

**DKIM** (probe common selectors at `<selector>._domainkey.<domain>`)
Two traps, both of which produce a wrong grade if you do not handle them:

1. **Empty `p=` is a revoked key, not a live one.** A record reading `v=DKIM1; p=` with nothing after `p=` is a published revocation. Grading it as a live key inverts the finding. Grade it as a failure and name the withdrawn selector.
2. **A wildcard under `_domainkey` makes every selector look present.** Some zones answer every name so no selector ever resolves as absent. Probe a **random** selector under `_domainkey` and, if it answers, suppress all per-selector results and report DKIM as unverifiable rather than as a pass or a fail. A probe at an arbitrary non-`_domainkey` name does NOT detect this wildcard, which is why the probe must live under `_domainkey`.

A missing DKIM key on common selectors is often a false negative when the sender uses a custom selector. Report it as unknown and tell the client to confirm their selector, rather than asserting a failure you cannot support.

## Proving a contact form is dead

A static read cannot tell a working form from a broken one: both return a success page. Capture HTTP evidence instead.

1. Parse the form and populate every field. Use a clearly synthetic identity plus a unique nonce in the free-text fields, for example `sitecheck-<epoch>-<hex>`.
2. Submit once, honoring the form's own method. Record status code, final URL after redirects, body length, a body hash, and a text snippet.
3. **Hash the response body across every form on the page.** Every form returning an identical body hash is the signature of a form that always reports success and never sends anything. That is the finding, and it needs no access to the client's inbox.
4. The checker cannot prove delivery, because it does not have the inbox. That is why the nonce exists: the follow-up email is one line, "I submitted your form at 2:14 PM with reference `sitecheck-<nonce>`. Did it reach you?" A no is the sale.

Limit this to sites the owner authorized, one submission per form. Testing a prospect's form once with your own details is the polite ceiling; repeated submissions is abuse and gets the sending domain burned.

## Site checks beyond the form

The remaining checks are cheap and each one is a line in the report: HTTPS reachable and certificate valid, HTTP redirecting to HTTPS, www and non-www resolving to one site (no redirect means duplicate content and split link equity), sitemap present, robots present, title length, meta description length, exactly one H1, viewport meta, `lang` attribute, a contact mechanism existing at all, a discoverable email address, home page weight, oversized images, broken internal links in a sampled set, privacy link, and address plus terms link.

Sample links and images rather than crawling everything; a 25-link sample finishes in seconds and finds the breaks that matter.

## Verify a checker before you sell its output

Run three targets, not one:

- **A known-good domain** with full records, to confirm the pass path produces passes.
- **A known-bad case**, to confirm the fail path actually fires.
- **A locally rigged target** for anything behavioral. For the form check, serve two forms that deliberately return the same success body from a local HTTP server, and confirm the tool reports the always-success signature. A clean real-world site cannot prove a detector works; a rigged negative case can.

Re-read raw upstream output whenever a result looks surprising. A DKIM pass on a domain that should not have keys is the tell for a wildcard zone, and the raw TXT answer shows it immediately.

## Honest limits to state in the deliverable

- The scan reads public DNS only. It fixes records and alignment; it cannot promise inbox placement, because what a mailbox provider decides is not yours to promise.
- The site check is a defect inspection, not an accessibility certification and not legal advice.
- Save the existing records before changing any. On DNS that makes every fix reversible in a minute, which is what lets a nervous owner say yes.
