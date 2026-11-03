# DMARC remediation: record strings, checks, and proof

Depth for the staged DMARC fix. Load when writing a DMARC record, a fix prompt
for another agent, or a verification report.

## Record strings

Target DMARC record, published at `_dmarc.<domain>`, one record, one string,
no duplicate:

```
v=DMARC1; p=none; rua=mailto:<existing-mailbox>@<domain>; fo=1; adkim=r; aspf=r; pct=100
```

Why each tag, so nobody "improves" it:

- `p=none` collects reports without changing how any receiver filters the mail.
  This is what makes a first-stage fix risk-free.
- `rua` is where aggregate reports land. Without it the record does nothing at
  all, which is the most common state a domain is found in.
- `fo=1` asks for failure reports on anything failing either SPF or DKIM.
- `adkim=r` and `aspf=r` are relaxed alignment, which is what hosted senders
  (ESP and relay platforms) need. Strict alignment fails them routinely.
- `pct=100` is explicit rather than relying on a provider default.

**2026-10-05, this record is now mandatory, not optional.** Gmail (enforcement
ramped Nov 2025) and Microsoft (since 2025-05-05) require a published DMARC
record (`p=none` MINIMUM) plus SPF/DKIM alignment from any domain sending 5,000+
a day to their consumer addresses, and they REJECT non-compliant mail at the
gateway (Microsoft: `550 5.7.515 ... does not meet the required authentication
level`; a DMARC reject is `550 5.7.509`). So `p=none` with `rua` is the floor, not
the finish: the alignment half (SPF or DKIM matching the From domain) is what
actually passes, and the policy ladder below is what enforces it. `email_scan.py`
now grades these as CRITICAL and `auth_enforcement.preflight_sending_domain()`
checks alignment.

Enforcement stages, applied only on Vinny's separate instruction, never in the
same change as the reporting fix:

1. `p=none` with `rua` and a clean reporting window.
2. `p=quarantine`.
3. `p=reject`.

If reports show any legitimate sender failing alignment, fix that sender's
DKIM first. Do not raise the policy to make the reports stop.

## Prerequisite checks before writing anything

- Confirm every platform that actually sends as the domain has DKIM enabled
  and resolving. Ask which platform the owner stopped using; stale records are
  the usual hidden defect.
- Confirm the `rua` mailbox exists and can receive before publishing, and point
  it at one that already works rather than creating a dedicated address. An
  SMTP `RCPT TO` probe does not prove existence, because hosts answer 250 for
  unknown recipients; send a real message and read the bounce instead. If the
  address cannot receive, report that and stop rather than publishing a record
  pointing at a black hole.
- Count SPF DNS lookups: each `include` and each nested include costs one, and
  10 is the hard limit. Report the count; do not trim includes on your own.
- Do not add MTA-STS, TLS-RPT, CAA, or MX changes as part of a DMARC fix.

## Verification and proof

Resolver check, Windows: `Resolve-DnsName -Name _dmarc.<domain> -Type TXT -Server 1.1.1.1`
Resolver check, fallback: `nslookup -type=TXT _dmarc.<domain> 1.1.1.1`
Linux or WSL with no `dig`, use the DoH JSON query in SKILL.md.

Then send a real seed message from the domain and read the received source,
quoting the `Authentication-Results` header verbatim and naming the `spf=`,
`dkim=`, and `dmarc=` results. A summary of the result is not proof; the raw
header is.

Third-party inboxes are not required and are usually unavailable to the agent.
Read the header off the domain's own mailbox instead: connect to its IMAP host
and fetch `BODY.PEEK[HEADER]` for recent messages. Mail sent to any address on
the domain passes through that mailbox, so the header there is the same
evidence a Gmail seed would give, with no outside account involved. Note that
an earlier message's `policy.dmarc=` reflects the DMARC record at the time it
was received, so re-send after a record change before quoting a post-fix
header. `scripts/verify-deliverability.py` does this.

Check the spam folder as well as the inbox. A `dmarc=pass` header in the spam
folder is still a pass. **But a message REJECTED at the gateway leaves no header
anywhere**, so "not in the inbox" is not by itself evidence of placement.
Distinguish a gateway rejection (a `5.7.515` / DMARC-reject NDR, or a line in
`auth_rejections.txt` and the mailbox's DSNs) from a soft placement issue. The
sending domain failing its own auth is the thing to fix, and it is NEVER fixed by
suppressing the recipient. See `references/outreach-send-verification.md`.

## Reading the aggregate report: the strongest available proof

A published `rua` causes the big receivers to mail the domain a report, and that
report is the evidence a resolver query cannot give you, because the receiver
measured the result itself rather than a third party reading the DNS.

- Read it over IMAP from the domain's own mailbox. Google's arrives from
  `noreply-dmarc-support@google.com`, daily, roughly 24 hours behind the window
  it covers, as a `.zip` holding one XML file.
- The `.zip` name is `<submitter>!<domain>!<begin-epoch>!<end-epoch>.zip`.
  Convert the epochs to UTC; `date_range` is always a fixed 24-hour window, so
  a report that lands mid-afternoon covers the previous UTC day.
- Parse with `zipfile` plus `xml.etree.ElementTree`. `report_metadata` gives the
  org and report ID, `policy_published` echoes the record the receiver actually
  saw, and each `record` gives `source_ip`, `count`, `identifiers/header_from`,
  and `policy_evaluated` with its `dkim`/`spf` results and any `reason` codes.
- Read it as: all records `dkim=pass` AND `spf=pass` with an empty `reason`
  list, and the sources being the domain's real sending IPs. Any `reason` entry
  names a failing sender, and that sender's DKIM gets fixed before any policy
  step is considered.
- The `count` field is message volume, so the report's total is the sum of
  `count` across records. Quote the real sum.
- Cross-check `policy_published` against a live resolver answer for `_dmarc`. A
  disagreement means the record changed after the window closed.

A mailbox with no reports in it is itself a finding: a record with no `rua`
produces none, which is why an empty inbox is the tell for the most common
broken state.

## Report format

Return exactly: backup file path; the `_dmarc` record as it now resolves (raw
output); the aggregate report's window, record count, and per-record
`dkim=`/`spf=` results with any `reason` codes; each sender platform's
DKIM status; the SPF lookup count; and anything blocked plus the exact block or
permission that stopped it.

A seed message's `Authentication-Results` header is the fallback proof when no
report has arrived yet. Do not name a Gmail or Outlook seed header in the report
unless one was actually sent from an account you have; the domain's own mailbox
is the proof source.

## Doing the DNS fix: the IONOS API, never the panel

All IONOS DNS changes go through the IONOS DNS API. Never `my.ionos.com`, never a browser, never a login screen. The browser path hits a 2FA wall, and it is the wrong door regardless.

- Base `https://api.hosting.ionos.com/dns/v1`, header `X-API-Key: <public_prefix>.<secret>`.
- Key file `/mnt/c/Users/<user>/workspace/memory/ionos-credentials.md`.
- Read `GET /zones/<zone_id>`, change one record `PUT /zones/<zone_id>/records/<record_id>` with `{name, type, content, ttl, disabled, prio}`, read the zone back to confirm.
- Back up the full zone JSON to `/mnt/c/Users/<user>/workspace/dns-backups/` before any edit.
- KARMA uses this same API and never opens the panel.

When another agent is doing the fix, or when the change is handed to Vinny:

- Deliver ONE self-contained prompt as a file. He will not assemble a prompt
  across messages, so a single request naming the artifact means the whole
  prompt in one block.
- State the verified current records in the prompt. The doing agent re-verifies
  before editing, but it must not have to rediscover the starting state.
- Enumerate the do-not-touch list explicitly, and make it include any record
  that is stale but harmless, so the agent does not "clean up" something out
  of scope.
- Require a backup step first, raw proof output second, and a fixed report
  format last.
- Keep the enforcement stages in the prompt marked as context only, after
  action, not to be done now.
- When he pushes back that the change might break mail, answer the mechanism in
  one pass: name the one record that changes, state that the policy value is
  unchanged so filtering behavior is identical, and list the abort points where
  the agent stops and reports instead of improvising.
