# Triaging a Pile of Service Ideas

## When to Use

Load this when several reports each propose a set of small paid services and he asks which to run, or which can be delivered with what already exists. Rank by these axes in this order, not by how good the offer sounds.

## The four axes

**1. Provable loss before the sale.** Can the defect be shown to the owner with an artifact they produced, a screenshot, a failed form submission, an unanswered call in their own log? Proof sells a $149 fix; a promise does not.

**2. Standup cost.** Does delivering it need anything bought, registered, or provisioned first? Zero-cost offers sell first because a sale can be delivered the same week.

**3. Delivery time.** Anything that cannot be finished inside roughly ninety minutes is a different product with a different price. Bundling more work into a $149 offer turns a profitable job into a loss.

**4. The blocker.** Name the exact gate before recommending the offer, and say whether it costs money or only time.

## Blocker classes worth checking before ranking

- **SMS and telephony.** US business messaging requires A2P 10DLC brand and campaign registration before texts can go out, and approval takes days to weeks. A missed-call text-back is therefore a configuration job inside a client's existing platform (OpenPhone, Dialpad, GoHighLevel) where their registration is already approved, not a build from scratch. Selling it to a business with no messaging-capable phone system stalls on the registration.
- **DNS and email authentication.** Records can be read from any machine over DNS, but writing them needs the client's registrar or DNS host login. The audit is deliverable today; the fix waits on access.
- **Google Business Profile, website admin, review platforms, cloud storage.** All require the client's own account access. Price that dependency into the delivery promise, and when access is refused, deliver exact instructions plus a re-test instead of claiming a fix.

## Offers that need no new accounts

- Contact form and lead-path testing: submit through a browser and confirm arrival in an inbox you control.
- Mobile tap-target and link checks: browser plus screenshots.
- Lighthouse audit: `npx lighthouse`, already available wherever Node is.
- Review response writing: no tooling at all.
- QR code plus short link: existing hosting is enough.

## Sequencing

Sell the offer whose proof is free first, and use that cash for the registration and provisioning on the offer that carries a wait. Start the wait in parallel so approval lands before the second sale does. A blocker that costs time is a scheduling problem, never a reason to drop the offer.
