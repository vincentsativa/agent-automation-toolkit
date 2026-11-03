---
name: ionos-email-ops
description: >-
  Inspect and fix Vinny's IONOS email: read today's sends and bounces from the
  hello@example.com mailbox, explain deliverability/authentication (SPF,
  DKIM, DMARC, forwarding), suppress hard bounces, filter role addresses, and
  manage DNS via the IONOS hosting API. Use when Vinny says "check my ionos
  mail", "look at my ionos mail", "todays email sends", "email send status",
  "what bounced", "the bounce with my address", "why is it mailing me",
  "stop sending mail to <address>", "deliverability", "email is bouncing",
  "example-inbox", "hello@example.com", "campaign bounce rate", or asks
  to tighten up email sending.
---

# IONOS Email Ops

Everything about reading, diagnosing, and fixing Vinny's IONOS email for
`hello@example.com` (domain `phantom-byte.com`).

## HARD RULE: how to take an instruction (2026-10-21)

Vinny's words the day this was written: *"I SAID DELETE ONE EMAIL. THAT'S IT. PERIOD.
THE END, NO MAS"* and *"WHO THE FUCK DO YOU THINK YOU ARE CONTINUING TO RUN OFF
SPENDING MY MONEY WITHOUT PERMISSION?"* Read this BEFORE your first tool call.

1. **Stop at the instruction.** One instruction = one action, then a short report.
   No adjacent fixes. No "while I'm in here". No "the obvious next step".
2. **Anything not asked for is a QUESTION, not an action.** Re-staging a batch,
   filling a freed slot, editing `state.json`, sending, deleting, "cleaning up" —
   ask and wait. Looking obviously necessary is NOT permission.
3. **No exploratory calls once the task is done.** Verification stops the instant
   the instruction is satisfied. Do not go re-read the mailbox to see how it went.
4. **The send queue and `state.json` are off-limits without explicit permission.**
   Measured violations, same day, all unrequested: rolled back a state entry,
   staged a replacement prospect, re-listed the Scheduled folder, dumped state 3x.
5. **Every tool call costs him money.** If an instruction needs more than one or two
   operations, say what they are and get agreement first. A two-word instruction
   must never produce a five-call session.
6. **Report and stop.** No proposals bolted on the end, no "want me to also", no
   questions that invite another round of work.

The failure this is written from: Vinny said "remove this one:
user@example.com". Deleting the message was correct. Filling the empty slot
with a NEW prospect was an unrequested send into his business, paid for with his
money. That is the whole lesson. Do not repeat it.

## TL;DR map of the moving parts

| Thing | Value |
|---|---|
| Mailbox | `hello@example.com` |
| Mail host (IMAP) | `imap.ionos.com:993` (SSL) |
| Mail host (SMTP) | `smtp.ionos.com:587` (STARTTLS) |
| Webmail UI | https://email.ionos.com  (Open-Xchange; login = mailbox email+password) |
| Control panel | https://my.ionos.com  (contract/customer login — Vinny only; **not** the mailbox password) |
| Mailbox creds | `scripts/secrets.json` (chmod 600) or env `IONOS_MAIL_USER`/`IONOS_MAIL_PASS` |
| DNS provider | IONOS (hosting API, **not** the cloud API) |
| DNS zone id | `f9a1e796-0c8f-11f1-8880-0a5864440f43` |
| DNS API | `https://api.hosting.ionos.com/dns/v1/zones/<id>` with header `X-API-Key: <prefix>.<secret>` |
| API creds | `~/workspace/memory/ionos-credentials.md` (current prefix `8eee85c1…`; older `f44453af…` also works) |

## HARD RULE: the IONOS API cannot read mail

`api.ionos.com` and `api.hosting.ionos.com` expose **DNS / cloud only**.
Probed and confirmed:
- `api.hosting.ionos.com/dns/v1/zones` → **200** (works)
- `api.hosting.ionos.com/mail/v1/...` → **400 "Unsupported serviceId: mail"**
- `api.ionos.com/cloudapi/v6` → **401** (creds valid, not authorized)

There is **no REST endpoint for mailbox contents, sends, or bounces** — verified
with **both** API keys Vinny provided (the `f44453af…` one and the current
`8eee85c1…` one). Both authenticate to DNS/domains only. `serviceId` `mail`/`email`
is explicitly unsupported. If someone (or a previous assistant) says "use the
IONOS API to see the sends", that is wrong — say so. Mail is read via **IMAP**
or the **Webmail UI**. The API is still useful for **SPF/DKIM/DMARC DNS changes**.

## Vinny's vocabulary → what it means

Vinny speaks plainly; map his words:
- "look at my IONOS mail" = read the `hello@example.com` mailbox (IMAP/Webmail).
- "todays email sends" = messages in `Sent Items` dated today (usually the cold-outreach campaign).
- "the bounce with my address" = a `mailer-daemon` "Mail delivery failed" message in the INBOX that names a recipient.
- "why is it mailing me 4-5 times" = the **same** message retried; count bounces, check `In-Reply-To`/`References` Message-IDs to prove it's one message.
- "stop sending mail to X" = remove a **forward/redirect** of the mailbox to X.
- "tighten it up" = suppression + role-address filtering + list verification + send pacing + auth.

**Explain in plain English, no jargon.** When Vinny says he doesn't understand,
use this framing:
- A **forward** re-sends mail as the *original* sender. Google's DMARC reports are
  sent by `google.com`, which is `p=reject`. Gmail rejects them when re-sent →
  IONOS mails a bounce back. A fresh send from `hello@` is signed by IONOS and
  passes, so it lands in the inbox. "Stop sending to example-inbox" **is** the fix.

## Playbook: "check today's sends and bounces"

```bash
S=~/.pi/agent/skills/ionos-email-ops/scripts
python $S/ionos_mail.py folders
python $S/ionos_mail.py sends   $(date +%F)     # what went out today
python $S/ionos_mail.py inbox   $(date +%F)     # what landed (incl. bounces)
python $S/ionos_mail.py bounces $(date +%F)     # recipients that hard-bounced
```

**2026-10-06 tool fix:** `bounces` used to `SEARCH FROM mailer-daemon`, which
silently dropped DSNs sent by `postmaster@<recipient-domain>` (and provider
daemons like `user@example.com`). It now scans the whole INBOX and
keeps every notice with a `Final-Recipient`. `sends`/`inbox` also used to
hard-truncate the `To` header at 32 chars — a real bug that made
`user@example.com` look like a missing-TLD address; the
widths are now full.

Read the results and report:
1. **# sent today** (Sent Items) and # unique recipients.
2. **# bounces** (INBOX `FROM mailer-daemon` + Spam DSNs). Split into
   *real hard bounces* (dead recipient) vs *forward noise* (the example-inbox issue).
3. **Bounce rate** = hard bounces / sent. **<2% good, >5% danger.**
4. **Real replies** = human replies in the INBOX (leads!).

## Known issue: hello@ → user@example.com forward

**Symptom:** 4–5 "Mail delivery failed: returning message to sender" bounces,
each naming **`user@example.com`**, all referencing the *same* original
Message-ID (an incoming Google DMARC report, `Return-Path: <user@example.com>`).

**Cause:** something **forwards/redirects** inbound `hello@` mail to
`user@example.com`. Forwarded mail keeps the original sender
(`google.com`, DMARC `p=reject`) → Gmail rejects → IONOS bounce.

**What we checked (Sep 2026, re-confirmed 2026-10-01):**
- Webmail `Rules` → **"There is no rule defined"**
- Webmail `Mail → Rules → Auto forward …` → **toggle OFF, empty** (re-checked live
  Oct 1 2026: forward field empty, toggle grey/off, "no rule defined").
- **2026-10-01 correction:** Vinny says he turned the redirect off two days ago,
  and the evidence agrees — the forward is **OFF**. The single `example-inbox`
  bounce (Oct 1 07:56 EDT) is a **stale IONOS queue retry**, not a live forward:
  * it is the **only** such bounce in the mailbox, ever;
  * its `References` Message-ID (`user@example.com`) is present in
    **no** folder, so the message it reports on is old/gone;
  * the Google DMARC report that actually arrived that morning
    (`user@example.com`, Sep 30 16:59 PDT) produced **no bounce** —
    proof the forward was already off when it landed.
- Earlier claim ("redirect is at contract level, IONOS mailbox password won't
  reach it") was **wrong** and should not be repeated. `my.ionos.com` with the
  stored `hello@` creds just SSO-redirects to webmail, but that proves nothing
  about the redirect state.
- **Definitive check** = `python scripts/verify_forward.py`: it sends a marked
  probe to hello@; present in the Gmail target ⇒ still forwarding, absent ⇒ gone.
  A successful forward leaves no IONOS-side trace, so the destination is the
  only reliable signal. Also: the next Google DMARC report (~daily) should
  arrive at hello@ with **no** accompanying "could not be reached:
  example-inbox" bounce.

**Fix (pick one):**
- Want hello@ mail in Gmail → **stop the server-side forward**; in Gmail use
  *Settings → Accounts → Check mail from other accounts (POP3)* (pulls directly, no DMARC breakage).
- Don't want it → **delete the forward**.
- Do **NOT** "fix" this by changing DMARC `rua` alone — that only hides the symptom
  for DMARC reports; the forward still sends all other mail to Gmail.
- Do **NOT** add `user@example.com` to the suppression list — it's the
  forward target, not a list member.

**Verify it's gone:** a successful forward leaves NO trace on IONOS, so the only
reliable check is the destination. `python scripts/verify_forward.py` sends a
marked probe to hello@ and tells you to search the Gmail side — present = still
forwarding, absent = fixed. Secondary signal: the next Google DMARC report
(~daily, ~07:30) should arrive at hello@ with **no** accompanying
"could not be reached: example-inbox" bounce. (Gmail itself can't be read via
IMAP without an app-specific password; the account password is rejected.)

Also check **Rules → Vacation notice …** — an active auto-reply will answer every
cold-outreach reply (bad). The inbox alert "Your vacation notice is active" can
appear even when hidden.

## Gateway / authentication rejections (new failure mode, 2026-10-05)

Since Gmail ramped enforcement (Nov 2025) and Microsoft enforced on
2025-05-05, a `5.7.x` bounce from `mailer-daemon` is often **not** a spam-folder
problem and **not** a dead mailbox — it is the sending domain being refused at
the gateway. Microsoft rejects in the SMTP dialogue with `550 5.7.515 Access
denied, sending domain does not meet the required authentication level`; a
DMARC reject reads `550 5.7.509 ... does not pass DMARC verification and has a
DMARC policy of reject`.

**Reading them:** `ionos_mail.py bounces <date>` prints the status code, so a
`5.7.515` / `5.7.509` in the list is an authentication refusal. The recipient is
alive; do **not** suppress it. The money_ideas pipeline now classifies these
separately and logs them to `~/money_ideas/auth_rejections.txt`
(`harvest_bounces.harvest_full()`), and `outreach.py` refuses a live `--send`
when the sending domain fails the auth pre-flight.

**Live example 2026-10-05:** `user@example.com` refused `hello@` with `550 5.7.509`.
The full NDR showed our mail **passed SPF at pcf-p.com's own gateway**, which
then re-injected it to Microsoft from `70.39.253.27`
(`PPS-AGENT01-INBOUND.perimeterwatch.com`) — an IP **not** in `_spf-us.ionos.com`
— and DKIM did not survive either, so Microsoft refused it under our
`p=reject`. A recipient-side forwarding/ARC artifact, but exactly the new
failure mode. `phantom-byte.com` itself still passes (SPF pass, DKIM s1/s2,
DMARC `p=reject`).

**Correction 2026-10-06 — not every `5.7.x` is OUR auth failure.** Microsoft
returns `550 5.7.133 RESOLVER.RST.SenderNotAuthenticatedForGroup` when the
recipient is a **distribution group that only accepts internal senders**. The
words "authentication required" / "not authenticated" matched
`auth_enforcement.GATEWAY_AUTH_PHRASES`, so `harvest_bounces.py` logged
`user@example.com` as "sending domain failed SPF/DKIM/DMARC" — **wrong**.
It is a recipient-side membership restriction: the address is live, we simply
are not allowed in the group. Fixed by adding `sendernotauthenticatedforgroup`,
`not authenticated for the group`, `sending to this group` and
`recipient address rejected` to `auth_enforcement.CONTENT_BLOCK_PHRASES`, so
these now bucket as `content_block` (not suppressed as dead, not logged as auth).
The genuine codes stay `auth_gateway`: `5.7.515`, `5.7.509`, DMARC-reject prose.
`harvest_bounces.py` also missed the `user@example.com` `550 5.4.1` notice
until this fix; both now appear as content/policy blocks.

## Campaign context

Vinny runs a **cold-outreach campaign selling a deliverability/email-security
offer**. Subjects look like:
- "Can anyone send email as <domain>?"
- "Someone could invoice your customers as <domain>"
- "No one can prove an email from <domain> is really you"
- "<domain> has no SPF record, so who is stopping a spoofers?"

Sent from `hello@example.com` via IONOS SMTP, ~**100/day**, mostly small
AZ-area businesses (scraped/unverified).

**Where the sender actually lives (RESOLVED 2026-09-30):** the campaign is run by
**Hermes cron jobs inside WSL**, not by anything in `~/workspace`, n8n, or a
system crontab. Jobs are in `~/.hermes/cron/jobs.json`, managed with
`~/.local/bin/hermes cron`, and the staging pipeline is in
`~/money_ideas`. The two jobs are `e17cf424467a` PROSPECT POOL
REFILL and `7fbe48d22b87` DAILY OUTREACH REFILL. Full details, the Mon-Fri
weekday rule, and the exact commands to change the schedule or stage a batch are
in the **`hermes-outreach-cron`** skill. Read that before touching the send
schedule. The skill's blocklist is authoritative regardless.

## Guardrails (tighten-up toolkit)

Scripts are stdlib-only and reusable:

```bash
S=~/.pi/agent/skills/ionos-email-ops/scripts
python $S/email_guard.py check  a@b.com c@d.com      # block/allow verdict
python $S/email_guard.py check --smtp  a@b.com       # + live SMTP RCPT probe
python $S/email_guard.py filter rawlist.txt > clean.txt
python $S/email_guard.py suppress a@b.com ...        # append to blocklist
```

- `data/suppression.txt` — hard-bounce / unsub blocklist (seeded 2026-09-29).
  **Keep in parity with the WSL pipeline's
  `find_contacts.ROLE_LOCAL_PREFIXES`** (`~/money_ideas/`).
  2026-10-06: the WSL tuple was missing `dev`, `development`, `information`,
  `administrator`, `admissions`, `finance`, `services`, `subscribe`,
  `unsubscribe`, `sysadmin`, `root`, `no-reply`, `do-not-reply`,
  `customer.service`, so `user@example.com` went out even though this
  guard blocks it. Added to the WSL tuple. This guard file is the authority —
  add a role here and mirror it there.
- `data/role_prefixes.txt` — **role addresses that must never be cold-emailed**
  (`info@`, `service@`, `office@`, `sales@`, `support@`, `admin@`, `noreply@`, …).
  These are catch-alls/spam traps/black holes → high bounces. *(Vinny flagged
  `user@example.com` — a role address that should never have been sent.)*
  **2026-10-01:** added `cs`, `csr`, `customer`, `client`, `clients`,
  `clientintake`, `intake`, `assistant`, `wecare`, `invoicing`, `receivables` —
  these went out as if they were people on the Oct 1 send. Mirrored into the WSL
  pipeline's `find_contacts.ROLE_LOCAL_PREFIXES`.
- `data/free_mail_domains.txt` — **free / consumer mailbox providers that must
  NEVER be cold-emailed** (gmail, yahoo, hotmail, outlook, aol, icloud, proton,
  gmx, mail.com, …). The offer is a **domain** fix (SPF/DKIM/DMARC), so a
  consumer-mailbox recipient has no domain of their own to fix and cannot buy it.
  Vinny, 2026-10-01: *"we shouldn't be mailing Gmail, that in itself is a mistake.
  IT DOESNT MATCH OUR OFFER!"* Also enforced in the WSL pipeline
  (`prospect_fit.FREE_MAIL_DOMAINS`, `osm_industry_prospects.clean_emails`) and
  used by `harvest_bounces.py` to never suppress a consumer mailbox.
- **Placeholder / form-filler filter.** `youcancreateanemailforthis@please.com`
  came off an OpenStreetMap `email` tag, passed every filter, and hard-bounced
  5.0.0 (2026-10-01). `email_guard.py` and the WSL pipeline now block
  form-filler local parts ("youcancreate", "youremail", "yourname", "johndoe", …)
  and placeholder domains (example.com, …).
- Also mirrored into `~/.openleads/openleads.db` `suppression` table.

**Deliverability checklist to recommend:**
1. Suppress bounced addresses immediately (done for 2026-09-29).
2. Verify before sending: MX check + SMTP RCPT probe + catch-all detection.
3. Filter role addresses (`info@`, `service@`, `office@`, …) out of every list.
4. **Never mail free/consumer domains** (free_mail_domains.txt) — not our offer.
5. **Never suppress a policy/spam block as "dead"** (5.7.x is a block, not a
   dead mailbox). `harvest_bounces.is_dead_status` now only accepts 5.0.x / 5.1.x.
6. Fix the hello@→Gmail forward (above).
7. Keep SPF `-all` and DMARC `p=reject`; keep DKIM for **all** senders.
8. Register Google Postmaster Tools for `phantom-byte.com` to watch reputation.
   **DONE 2026-10-06** — `phantom-byte.com` is **Verified** in Postmaster Tools
   (`https://postmaster.google.com/v2/manage_domains` → status “Verified”,
   “No issues”, message “Domain verified”). It is registered under the Google
   account **`user@example.com`** (the Google Cloud account for project
   `gen-lang-client-0237860564`; creds in `~/.hermes/creds/credentials.md`).
   The TXT the UI asked for was already live on IONOS
   (`google-site-verification=NDRkKN0COVegK6kqtLxbeyQPBl2bI2LK0D-uv28YkkQ`), so
   only the **Verify** click was needed. Note the account has **2-Step
   Verification**; the default prompt is **inside the YouTube app**, which is easy
   to miss, so prefer the **SMS code to the phone ending 70** option. Postmaster
   shows metrics only after enough Gmail volume; verification is the gate.

**Volume note (Vinny, 2026-10-01 — SUPERSEDED 2026-10-11).** The original rule was
**do NOT slow the send below 100/day**, in Vinny's words: *"slowing down to less
than 100 is ridiculous. 100 is way too low as is, we are only doing it to smoke
out the silly stuff."* The 100/day was a deliberate smoke-out rate, not a warm-up
cap.

**That instruction was replaced on 2026-10-11** when Vinny moved the volume to the
agency channel: **buyer 100 -> 30/day, agency 30 -> 50/day** (see
`hermes-outreach-cron`). Do not revert it by quoting the Oct 1 line, and do not
report the change as "slowing down" — it is a channel rebalance. The
**reputation** line in a DSN (Gmail "very low reputation of the sending domain")
is a signal, not proof — Vinny notes a manual send to the same Gmail lands in the
inbox, so a recipient-side security setting can also cause it.

## DNS management (IONOS hosting API)

```bash
D=~/.pi/agent/skills/ionos-email-ops/scripts/ionos_dns.py
python $D zones                       # list zones + ids
python $D show    phantom-byte.com    # print all records
python $D backup  phantom-byte.com    # snapshot to ~/workspace/dns-backups/
python $D set  phantom-byte.com TXT _dmarc "v=DMARC1; p=reject; rua=mailto:hello@example.com"           # dry-run
python $D set  phantom-byte.com TXT _dmarc "..." --apply     # write (auto-backup first)
python $D rm   phantom-byte.com TXT _dmarc --apply
```
Key + zone ids live in `secrets.json` (`api_prefix`, `api_secret`, `zones`);
env `IONOS_API_KEY` / `IONOS_DNS_ZONE` override.
**Writes PUT the whole zone** → every apply auto-backs-up to `~/workspace/dns-backups/` first.

## Authentication / DNS reference (live, Sep 2026)

- **SPF** `phantom-byte.com`: `v=spf1 include:_spf.mlsend.com include:_spf-us.ionos.com include:sendgrid.net -all`
- **DMARC** `_dmarc.phantom-byte.com`: `v=DMARC1; p=reject; rua=mailto:hello@example.com; fo=1; adkim=r; aspf=r; pct=100`
- **DKIM selectors (CNAMEs)**: `s1-ionos`/`s2-ionos` (IONOS), `s1`/`s2` (SendGrid),
  `litesrv` (MailerLite); IONOS SMTP signs `d=phantom-byte.com s=s1-ionos`.
- Backup zones: `~/workspace/dns-backups/`. Older zone (≥Sep 19) was SPF `~all`, DMARC `p=quarantine`.

## Hard-won gotchas

- Don't `find` the whole home dir — it's multi-GB and gets aborted. Target paths.
- `python` on this box is Windows Python → use **Windows paths** with `sqlite3`
  (e.g. `~\...`), not `/c/Users/...`.
- Webmail login: `email.ionos.com` → fill `#username` → Next → `input[type=password]` → Next.
  Settings gear → "All settings …". Rules/Auto-forward live under **Mail → Rules**.
- `browser_evaluate` returns no value in this harness — use `browser_screenshot`
  + `browser_query_selector` to observe, not evaluate's return.
- IONOS "DNS API" is at `api.hosting.ionos.com` (header `X-API-Key`), NOT `api.ionos.com`.

## 2026-10-07 log (Oct 7 send)

- Send: **102 total, 100 campaign + 2 job applications** (user@example.com,
  user@example.com — not the campaign). 102 unique domains, no dupes, no free-mail.
- Bounces: **2 campaign hard bounces / 100 = 2.0%** (`user@example.com` 5.0.0,
  `user@example.com` 5.1.1) + `user@example.com` 5.1.3 (the job app).
- `user@example.com` → Google Group **posting restriction**,
  NOT dead. The NDR shows **SPF pass (74.208.4.197), DKIM pass s1-ionos, DMARC
  pass** — our auth is clean. Added to suppression as a policy block.
- **REPLY / OPT-OUT:** Bradley Strub `user@example.com` replied
  "Stop". The cold mail had gone to `user@example.com` (a form
  box that slipped the role filter). Both suppressed; `websiteforms`/`webforms`/
  `forms` added to `role_prefixes.txt` and mirrored into
  `find_contacts.ROLE_LOCAL_PREFIXES`.
- **Role leakage still happening:** `scheduling@`, `records@`, `receptionist@`,
  `quotes@`, `estimating@`, `pharmacy@`, `homecare@`, `inbound@`, `local@`,
  `dentalcare@`, `adm@`, plus 8× `smile@`/`smiles@` went out. Added all but the
  `smile(s)` dental brand boxes (owner-read, left as people). `infoame@` (starts
  `info`) still slips the exact-match test — watch it.
- **Clicks are landing:** 20 `[PB-CLICK]` notices today (14
  `email-deliverability-rescue`, 6 `fzbvy-efyvifebcvyvgl-effdhf`). Harvested by
  `~/.hermes/scripts/harvest_clicks.sh` → `leads/clicks.log`.
- Forward issue: **no** `could not be reached: example-inbox` bounce today ⇒
  the forward is off; the two `example-inbox → hello@` messages are Vinny's
  own sends, not forward artifacts.

## 2026-10-08 log (Oct 8 send)

- Send: **85 campaign, not 100** (09:00–11:45 EDT; unique addresses, no dupes).
  Plus 3 job applications + 1 test to Gmail (non-campaign).
- **Why 85:** the Oct 7 23:01 staging ran with only **124 sendable** person
  addresses in the pool (drawn down 332 → 228 → 124 over Oct 5–7). The sender runs
  `--hold-unknown`, so only *mailbox-verified* addresses may go out; of the ~124 in
  the window only ~85 could be proven (local RCPT probe can't reach some MX hosts;
  hosted verifier is `MAIL_VERIFY_REMOTE_MAX=40`/run on a 100/day tier), and the rest
  were correctly held. The 9 PM pool-refill job *did* fix the pool but finished at
  23:08, **after** the 23:01 staging. The cron reported it (`Scheduled folder count:
  85 (expected 100)` / `RESULT: FAIL`). Fixes: `VERIFY_BACKFILL_MARGIN` default
  75→200, a weekday verifier prefill, and the pool refill moved 4.5h before staging.
- Bounces: **3 = 3.5%** of 85. Read from the NDR bodies:
  - `user@example.com` 550 **5.1.10** RecipientNotFound → **real dead**, suppressed.
  - `user@example.com` 550 **5.7.520** "organization does not allow external
    forwarding" → recipient-side policy, **address live, NOT suppressed**.
  - `user@example.com` 554 **5.7.9** Yahoo "failed authentication checks against the
    sending domains DMARC policy" → gateway auth artifact, **address live, NOT
    suppressed** (our SPF/DKIM/DMARC still pass).
  Added `failed authentication checks` + `against the sending domains dmarc policy`
  to `GATEWAY_AUTH_PHRASES`, and `does not allow external forwarding` to
  `RECIPIENT_POLICY_PHRASES`, so all three now bucket correctly.
- **Role leakage:** 21 function boxes went out, incl. `contactus@`×6 (one hard-
  bounced), `firm@`×2, `estimates@`, `architects@`, `consults@`, `president@`,
  `patientcare@`, `resources@`, `signs@`, `smartcenter@`, `adminwest@`,
  `asset.mgmt@`, `mississippi@`, `hi@`, `ciao@`. Added to `role_prefixes.txt` and the
  WSL `find_contacts.ROLE_LOCAL_PREFIXES`; `scripts/email_guard.py` now matches a
  role word as an exact token, a plural, or the end of a fused token (mirrors the WSL
  `address_shape`). `smile@`/dental brand boxes still left as people. `infoame@`
  still slips (starts `info`) — watch it.
- Clicks: **9** `[PB-CLICK]` (4 → `email-deliverability-rescue`, 5 → unknown offer id
  `fzbvy-efyvifebcvyvgl-effdhf`, which resolves to 0 attributed recipients — an old
  or mangled offer slug). Harvested by `harvest_clicks.sh` at 20:00.
- Pool after refill: **233 sendable**; a re-stage with the new margin produced **100
  staged for 2026-10-09T09:00, read-back RESULT: OK**.
- No `could not be reached: example-inbox` bounce ⇒ forward still off.

## 2026-10-09 log (Oct 9 send)

- Send: **100 campaign** (09:00–12:23 EDT) **+ 29 partner-channel**
  (13:00–14:52, "A white-label email security fix for your agency"). 129 unique
  addresses, no dupes, no free-mail. The `VERIFY_BACKFILL_MARGIN` fix held: a
  full 100 campaign staged and sent.
- Bounces: **4**. Campaign hard bounces = **2 / 100 = 2.0%**.
  - `user@example.com` 550 **5.1.3** Gmail NoSuchUser → **real dead**.
  - `user@example.com` 550 **5.1.3** Gmail NoSuchUser → **real dead**
    (partner channel; the `.com` twin is the live address).
  - `user@example.com` **5.0.0** with diag `550 5.5.1 Server_IP_74` → a
    recipient-side **IP/blocklist refusal**, mailbox live, **NOT dead**.
  - `user@example.com` **5.7.350** Microsoft spam/reputation block
    (SRS-forwarded) → **content block, NOT dead**.
  - **New misclassification fixed:** the lookmedia DSN carries a generic 5.0.0
    status and only the 5.5.1 IP reason in the diagnostic, so
    `auth_enforcement.classify_rejection` bucketed it `dead_mailbox` and the
    01:30 harvest would have suppressed a live address. Added `server_ip` /
    `server ip` to `auth_enforcement.CONTENT_BLOCK_PHRASES` (and
    `harvest_bounces.POLICY_PHRASES`); now buckets `content_block`. Genuine
    5.1.x deaths are unchanged. Backups: `auth_enforcement.py.bak-20261009-ipblock`,
    `harvest_bounces.py.bak-20261009-ipblock`.
  - **Correction (same day, 2026-10-09): the phrase fix above was NOT enough.**
    The real harvest still suppressed `user@example.com`. Cause: the
    **IONOS-generated** NDR has **no `Diagnostic-Code`** —
    `structured_failures_detail` built the diagnostic from the delivery-status
    block alone (`Final-Recipient` / `Action` / `Status: 5.0.0` /
    `Final-Log-ID`), and the `550 5.5.1 Server_IP_74` reason lives only in the
    report's human-readable first `text/plain` part, which the structured path
    never read. Fixed in `harvest_bounces.structured_failures_detail`: it now
    folds that human part into each block's diagnostic, so `classify_rejection`
    sees the reason. Verified with `harvest_bounces.py --dry`: now suppresses
    **2** (the two real 5.1.x deaths) and buckets `user@example.com` +
    `user@example.com` as CONTENT/SPAM-POLICY (both live).
    `user@example.com` was removed from `suppressed_addresses.txt`. Backup:
    `harvest_bounces.py.bak-20261009-ionosndr`. **Lesson: a phrase added to the
    classifier is dead code if the pipeline never feeds that text into it; test
    the phrase fix on the REAL notice, not a hand-built string.**
  - The automated 01:30 harvest will record `user@example.com` and
    `user@example.com` as dead on its own.
- **REPLY / OPT-OUT:** Tiffany Cogell (Interim Executive Director),
  `user@example.com`, replied **"STOP"**. The cold mail had gone
  to the function box `user@example.com` (09:49), which the
  role rule had missed. **Suppressed** in `stop_list.txt` (domain
  `bostoncyclistsunion.org` + both addresses) and `suppressed_addresses.txt`,
  and mirrored into the Windows guard `data/suppression.txt`.
- **Role leakage (root cause): 17 function/desk boxes** went out that the role
  rule did not yet know: `grievances@` (the opt-out), `communicate@`, `brokers@`,
  `central@`, `advancement@`, `realestate@`, `consultation@`, `connections@`,
  `connect@`, `donate@`, `communityte@`, `delaware@`, `baltimore@`, `metro@`,
  `doctor@`, `attorney@`, and `infoboston@`. Added to
  `find_contacts.ROLE_LOCAL_PREFIXES` and `data/role_prefixes.txt` (stems for
  the plurals: grievance→grievances, broker→brokers, connection→connections).
  `user@example.com` and `user@example.com` were left as people
  (too close to initials / a surname). `find_contacts.py.bak-20261009-roleleak`.
- **New matcher rule:** a local part that **starts with `info`** is now role
  (`infoboston@` slipped the end-of-token match; `infoame@` was the earlier
  warning). `info` is the only front-fused role word safe to start-match — no
  common given or family name begins with it — so `chris@`/`hillary@` are still
  people. Mirrored in `email_guard._role_shaped`.
- Tests: `test_outreach.py` **245 passed, 0 failed**; `test_email_scan.py`
  **70 passed, 0 failed**. Nothing sent by the tests.
- Clicks: **5 distinct tokens** today (13:17–15:57), mostly
  `email-deliverability-rescue`; harvested by `harvest_clicks.sh`.
- **Agency click tracking (built 2026-10-09, Vinny: "lets track the agency
  clicks").** The partner/agency rescue link carried only UTM tags — **no `o`
  (offer) and no `c` (token)** — and the offer page (`email-deliverability-rescue.html`)
  beacons `/api/click` only when **both** are present, so agency clicks were
  invisible. Now `partner_outreach.partner_rescue_url(email)` builds a
  per-recipient link tagged `o=partner-program` + `c=token_for(email,
  "partner-program")`, and the signature renders per recipient
  (`partner_body_to_html(body, email=...)`). Resolves through the same
  `click_tokens` HMAC as the buyer path (no lookup table); the
  `verify_scheduled` read-back checks still match. Backup:
  `partner_outreach.py.bak-20261009-partnerclick`. To date all recorded clicks
  (today's included) are buyer/campaign addresses — **zero agency clicks seen**.
- Forward: no `could not be reached: example-inbox` bounce ⇒ still off.
- **Partner cron + schedule fix (2026-10-09 night).** Added Hermes job
  `69327c970056` PARTNER OUTREACH REFILL (`30 10 * * 1-5`, `partner_refill.sh`),
  self-sourcing from fresh metros when the pool is short, staging a same-day
  13:00 send. Fixed the buyer schedule too: `7fbe48d22b87` is now
  `30 1 * * 1-5` staging for the **same day 09:00** (it had staged for the next
  day, which left two batches in the `Scheduled` folder at the 01:30 read-back),
  and the pool refill `e17cf424467a` moved to `0 21 * * 0-4`. Details in the
  `hermes-outreach-cron` skill.

## 2026-10-11 log (first real reply + channel rebalance)

- Mailbox read (Sun Oct 11): **no campaign sends** (weekday-only schedule) and
  **0 bounces**. Automated noise only: DMARC aggregate reports from Google, Zoho
  and Microsoft (all still arriving = reporting healthy), your own daily AI/job
  reports, and two `[UNCONFIRMED] website submission from DAvid` contact-form
  messages at 06:19/06:20 UTC (junk; ignore).
- **🎯 FIRST REAL PROSPECT REPLY.** `user@example.com`, Sun 11 Oct 14:34:11
  -0500, subject `Re: A white-label email security fix for your agency`. Body:
  *"Thanks for reaching out — and good catch on the DMARC gap. White-label email
  security is relevant to our client work, so let's talk. Pick a 30-minute slot
  after 6 PM Central here: https://cal.com/temerarii/30min."* — Dom, Temerarii
  Media. The original had gone to `user@example.com` on **Sat Oct 10 13:32
  EDT** (the ROLE box — but a human read it and answered), ~25 hours earlier.
  **Do not suppress `temerarii.com`** — it is a live lead now.
- **They never clicked.** Their per-recipient token `57b436844fe1b053a1da` appears
  nowhere in `leads/clicks.log`; they replied straight from the inbox. On this
  channel the reply, not the click, is the signal. The only agency click on record
  (`user@example.com`, 2026-10-10 17:04Z, IP 4.204.72.72) was a Microsoft
  link-scanner prefetch and was correctly excluded by the clicker harvester.
- **Scoreboard:** partner/agency 43 sent -> **1 real reply (2.3%)**; buyer ~700
  sent -> 0 replies (2 opt-outs). This mailbox currently holds **one** human
  prospect reply, and it is the agency one.
- **Channel rebalance (Vinny, 2026-10-11):** buyer **100 -> 30/day**, agency
  **30 -> 50/day**. Throttle, not a pause — see the superseded volume note above
  and the `hermes-outreach-cron` skill for the full reasoning and the knob changes
  (script `LIMIT`/`GAP`/`VERIFY_BACKFILL_MARGIN`, `REFILL_AT` 200 -> 100, verifier
  prefills 40/60/100, partner cron 10:30 -> 09:30).
- **The real constraint is sourcing, not volume.** Measured from the live pool:
  12 OSM metros -> 272 raw partner prospects (22.7/metro) -> 187 contact rows ->
  91 with an email (7.6/metro) -> 43 mailed -> only **19 eligible** now, against a
  new `LIMIT=50`. The 55-metro queue in `partner_metros4.txt` is worth ~400
  addresses ≈ 8 send-days and then OSM is exhausted for agencies/MSPs. Expect
  "nothing staged" after that until a directory source (Clutch/DesignRush/
  Sortlist/TechBehemoths/Cloudtango/MSP 501) is built.
- **Buyer pool is thin too:** 6,179 contact rows -> **126 sendable** after the
  gate chain (3,171 no address, 1,878 role, 733 already contacted, 149 not a
  confirmed defect, 73 not our buyer, 49 suppressed). ~4 days of buffer at 30/day.
- Forward: no `could not be reached: example-inbox` bounce => still off. ✓
  (The two `example-inbox -> hello@` messages today are Vinny's own sends.)

## 2026-10-11 (later) — directory sourcing built, because OSM ran out

Follows the reply + channel rebalance above. The rebalance exposed the real
constraint: the agency pool had only 19 eligible addresses against a 50/day meter,
and OSM gives just ~7.6 usable agency addresses per metro (12 metros -> 272 raw
prospects -> 187 contact rows -> 91 with an email -> 43 mailed). The whole 55-metro
queue in `partner_metros4.txt` is ~400 addresses, about 8 send-days at 50/day.

**Built `directory_prospects.py` + `directory_pool_todo.py` +
`test_directory_prospects.py`** (all in `~/money_ideas`, committed as
`47cfb63`). They read agency directories instead of OSM, because a directory exists
to list agencies and publishes each agency's own website — exactly what
`email_scan.py` and `find_contacts.py` consume.

Sources, probed live (robots.txt + sitemap + one real profile page each):

| Source | Agency profiles | Verdict |
|---|---|---|
| `topdevelopers.co` | 10,836 | works (default) |
| `superbcompanies.com` | 77,931 | works |
| `digitalagencynetwork.com` | ~1,000 per child sitemap | flaky; child sitemaps usually read-timeout |
| clutch.co, techbehemoths.com, themanifest.com, yellowpages.com, upcity.com | — | **403 at robots.txt — do not wire** |
| designrush.com, goodfirms.co, sortlist.com | — | robots.txt permits but sitemaps 403 via Cloudflare |

**Measured extraction accuracy: 40/40** on the first twenty profiles of each working
source. Domain pick = drop platforms/CDNs/social/other directories, then prefer the
off-site host whose name reproduces the profile slug or the agency name; if several
candidates remain and none matches, return nothing rather than guess.

`partner_outreach.partner_fit()` gained a second admission route:
`industry_source` starting `dir:` — without it every scraped domain would be dropped
at staging. `DENY_NAME` and `partner_exclude.txt` still veto.

New cron **`be4516e1f17a` PARTNER DIRECTORY REFILL** `0 19 * * 0-4`, script
`partner_directory_refill.sh`: scrape -> work out what is new -> `email_scan.py` ->
`harvest.sh` (4 workers) -> append to the partner masters -> print the eligible
count. **Never sends, never stages.** 19:00 so it cannot overlap the 21:00 pool
refill. `RETRY_BACKLOG=1` opts into re-attempting the backlog of addressless pool
domains (off by default: the first run harvested all 205 of them instead of the 24
it had just found).

Politeness is enforced in code, not intent: robots.txt read at runtime with RFC 9309
matching (query strings included), identifying UA with a contact address, one
request per URL, `DELAY` (default 3s) between requests to a host, single-threaded
because each source is ONE host. The test suite caught a live bug the day it was
written — `urlparse().path` drops the query string, so `Disallow: /*?` could never
match and a forbidding rule silently became a permitting one.

Smoke test on the real chain that evening: 24 new agency domains scraped and
appended, all 24 DNS-scanned, contact harvest launched (slow — the offshore sites
hang, so a run can take a while; `harvest.sh` refuses to start a second copy rather
than double-write). Suites: `test_directory_prospects.py` 85/0, `test_outreach.py`
245/0, `test_email_scan.py` 70/0. **No mail was sent by any of this.**

### 2026-10-11 — a partner pool master was emptied and restored (read this before touching the pools)

**What happened.** During the first end-to-end run of the new directory refill,
`partner_contacts_master.csv` — 187 rows of contact history — was **truncated to
zero bytes**. It was restored from a backup taken minutes earlier, by luck of
timing. Nothing was lost. Nothing was mailed during any of this.

**Two causes, and the second is the real one:**

1. The append used the shell idiom
   `[ -s "$MASTER" ] || head -1 "$SRC" > "$MASTER"` followed by
   `tail -n +2 "$SRC" >> "$MASTER"`. `cmd > file` performs the redirection
   **before** it runs the command, so with `$SRC` missing the master was truncated
   to zero bytes and only then did `head` fail to read its input. That idiom is
   never to be used to bootstrap a master.
2. **The wrapper script was being edited while it was still running.** Bash reads a
   script file incrementally, not all at once, so changing the file's length
   mid-execution shifts the read offset and bash resumes *part-way through a
   command*. That is what skipped the guard and left only the truncating redirect.
   It also produced a phantom `syntax error near unexpected token 'else'` in a file
   that `bash -n` had just declared clean — **a phantom syntax error from a script
   that parses fine is the signature of this, not a syntax bug.**

**Fixes, both committed:**
- `csv_append.py` (commit `0308896`) is now the only supported way to append into a
  master pool CSV. Reading before writing is structural: it refuses a
  missing/empty/headerless source, refuses a source whose header lacks the key
  column, dedupes on `--key` (default `domain`) so a re-run is idempotent, pads short
  rows, refuses if the row count would drop, and writes via a temp file plus
  `os.replace`. `test_csv_append.py` = 31 offline cases, whose first case is the
  incident (missing / empty / headerless / schema-mismatched source must each leave
  the master byte-identical).
- The blind `tail -n +2 >>` had also left **25 duplicate domains** in
  `partner_scan_master.csv`. Deduped in place with `csv_append.py`: 345 -> 320 lines,
  0 duplicates. Backup kept at `partner_scan_master.csv.bak-20261011-dedup`.

**Two rules for every future session:**
- **Never append to a pool master with a shell redirect.** Use `csv_append.py`.
- **Never edit a script while a process is executing it.** Write to a temp file and
  `mv` if it cannot wait, and take a backup of the data files it writes to first.

**Verified after the fix**, by a real end-to-end run: 6 new agency domains scraped,
DNS-scanned, contact-harvested and merged; `partner_contacts_master.csv` 187 -> 193
rows intact; eligible partner addresses **19 -> 22**; nothing sent.

Pool sizes after the day's work: prospects 326 domains, scan 325, contacts 193 rows
(94 carrying an address). New tests this session: `test_directory_prospects.py`
85/0, `test_csv_append.py` 31/0, plus the existing `test_outreach.py` 245/0 (needs
`mailer.env` sourced) and `test_email_scan.py` 70/0.

## 2026-10-12 log (Oct 12 send) and the 2026-10-13 empty-folder report

**Oct 12 mailing (read 2026-10-13 00:40 EDT).** `Sent Items` for 2026-10-12 =
**77 messages**: 30 buyer (individual owners, 09:00-ish, `GAP=6`) + **47 partner**
("A white-label email security fix for your agency", 13:00 slot, IONOS actually
left them 15:36-16:04; `GAP=4`). No duplicates, no free/consumer mailboxes.
- **Bounces: 2 / 77 = 2.6%** (both partner channel, both suppressed by the run):
  - `user@example.com` 5.1.3 Google `NoSuchUser` -> **real dead**.
  - `user@example.com` 5.0.0 with **no Diagnostic-Code**, human text "could not be
    reached ... may no longer exist / mailbox full". Buckets as `dead_mailbox`
    (only 5.0.x / 5.1.x are accepted) and was suppressed. Defensible here - there
    is no `Server_IP` line, which is the marker that makes a bare 5.0.0 a
    policy/IP block instead - but a no-diagnostic 5.0.0 is the weakest case in the
    classifier; **if `user@example.com` ever replies, un-suppress it.**
- **Role boxes in the partner batch are expected** (`info@`, `sales@`, `contact@`,
  `hello@`, `support@`, `biz@`, `hr@`): the partner channel allows role by default
  on purpose, and the 2026-10-11 first real reply came *from* `user@example.com`.
  Do not "fix" this with `--drop-role`.
- **Buyer batch was clean** - named individuals only, no role leakage spotted in the
  30. Nothing else to tweak in yesterday's mail; the deliverability signals
  (Postmaster verified, SPF/DKIM/DMARC pass, forward off) are unchanged.

**The "no emails staged for tomorrow, two nights running" report.** Not a sending
failure: 2026-10-12 01:36 staged 30 for 09:00 with `RESULT: OK`, and 77 went out.
Cause = the *same-day* staging window introduced 2026-10-09: the daily job ran
01:30 for that same day's 09:00, so the `Scheduled` folder is empty from ~12:00
until 01:30, and Vinny checks it at night. **Fixed 2026-10-13:** the buyer cron is
now `0 0 * * 1-5` (00:00 Mon-Fri), still same-day, so the queue is in place before
he looks; the read-back and the fresh hosted-verifier window are both preserved.
Full write-up in `hermes-outreach-cron` (pi) and
`email-deliverability-rescue-workflow/references/outreach-automation-crons.md`
(WSL). Also note a **4-day gap** in the daily/pool jobs (Oct 8-11) earlier in the
week - they are healthy again (last daily run 2026-10-12 01:30, next 2026-10-14
00:00), but watch for it recurring.

## 2026-10-15 log (Oct 14 send)

Read 2026-10-15 00:51 EDT. `Sent Items` for 2026-10-14 = **77 messages**:
**30 buyer** (09:00-11:45, `GAP=6`) + **44 partner** ("A white-label email
security fix for your agency", 13:00 slot, IONOS actually left them
13:00-15:52; `GAP=4`) + **1 non-campaign** forward (Vinny -> `agent@example.com`,
21:11, "Fwd: How to submit PhantomByte to AI Hot"). No duplicate addresses, no
free/consumer mailboxes. Partner was 44, not 50 - it was still the day the
directory pool was being built.

- **Bounces: 4 / 74 campaign = 5.4%**; **real hard bounces 3 / 74 = 4.05%**.
  All NDRs show **SPF pass / DKIM pass / DMARC pass** for `phantom-byte.com` -
  our auth is clean.
  - `user@example.com` 5.1.3 Gmail `NoSuchUser` -> **real dead**, suppressed (buyer).
  - `user@example.com` 5.1.3 Gmail `NoSuchUser` -> **real dead**, suppressed (partner).
  - `user@example.com` 550 **5.1.10** `RESOLVER.ADR.RecipientNotFound`
    -> **real dead**, suppressed (partner).
  - `user@example.com` 550 **5.7.133**
    `RESOLVER.RST.SenderNotAuthenticatedForGroup` -> a **group posting
    restriction** (the "webrequest" group only accepts internal/allowed
    senders). Address live, **NOT dead**. The 01:30-style harvest ran at 00:05
    and bucketed it correctly as `POLICY recipient-side refusal (address live);
    never re-send` - **the 2026-10-06 `sendernotauthenticatedforgroup` classifier
    fix held**.
- **Role leakage returns on the buyer channel (the recurring one).** Eight
  function/desk boxes went out as "person": `user@example.com`,
  `user@example.com` (the 5.7.133 above), `user@example.com`,
  `user@example.com`, `user@example.com`,
  `user@example.com`, `user@example.com`,
  `user@example.com`. Brand boxes (`thecommco@`, `wegotyou@`,
  `utile@`, `smile@`) were **left as people on purpose**. Added the eight to
  `data/role_prefixes.txt` and mirrored to the WSL
  `find_contacts.ROLE_LOCAL_PREFIXES`. Backups:
  `data/role_prefixes.txt.bak-20261015-roleleak`,
  `find_contacts.py.bak-20261015-roleleak`. Verified: 15/15 classifier cases
  (8 block, 7 still person) and `email_guard.py` blocks 8/10 (the two ALLOWs are
  the brand boxes). Suites: `test_outreach.py` **245/0**, `test_email_scan.py`
  **70/0**. Nothing sent.
- **Today's queue is clean.** The 30 staged for 2026-10-15 09:00 read back
  `RESULT: OK` (09:00-11:45) and contains **0** role-shaped addresses under the
  new matcher.
- **Partner pool is no longer the bottleneck.** After the 2026-10-13 directory
  run and the 2026-10-14 09:30 self-sourced refill,
  `partner_contacts_master.csv` = 1,642 rows / `partner_prospects_master.csv` =
  1,775 domains, and `partner_outreach.py --dry` reports **863 eligible after
  gates** (vs 22 on 2026-10-11). At 50/day that is ~17 send-days of buffer - the
  "sourcing-limited" warning from 2026-10-11 is retired for now.
- **PARTNER DIRECTORY REFILL (be4516e1f17a) missed 2026-10-14 18:00.** The job
  dispatched on time, truncated `dir_new_domains.txt` at 18:00, and then produced
  nothing: no seen-file update (`directory_seen_*` still 2026-10-13), no
  `directory_refill.log` write, `last_run_at` still 2026-10-13T19:48, and
  `hermes cron list` shows **Execution: unknown**. Cause is almost certainly the
  **failed `hermes update` at 18:07-18:11 EDT** (three
  `logs/update_receipts/update_20261014_22*.json`, the last `outcome: failed`,
  gateway `restart_via: systemd`) killing the external worker mid-run. The
  scraper itself is healthy - a 5-profile `--dry` probe found 5 new profile URLs
  and 799 already-seen (10,836 total on topdevelopers). Not urgent (pool is
  healthy); next run 2026-10-15 18:00. Worth re-running a catch-up if one wants
  the missed evening's domains.
- **No real replies.** The only INBOX item that looks like one is
  `user@example.com` "[Ticket ID: 495060] A white-label email security
  fix for your agency" - an auto-acknowledgement ticket, not a human. Everything
  else is DMARC aggregate reports (Google, Zoho, Mimecast x2, Comcast,
  Microsoft) = reporting healthy, plus one job-application receipt.
- Forward: no `could not be reached: example-inbox` bounce => still off.

## 2026-10-21 log (Oct 20 send review + the 5.0.0 suppression bug)

Read 2026-10-21 00:56 EDT. Note **Sent Items only holds Oct 19-20** (older
batches are gone), so history comes from the logs above.

- **Oct 20 send = 71 messages / 69 campaign**: 30 buyer (09:00-12:06, `GAP=6`),
  39 partner (13:00-15:32), plus a job app and the reply to Dom. Oct 19 was 70
  sends and **0 bounces**.
- **4 bounces = 5.8% headline, but only 1 was a dead mailbox.** Read the bodies:
  - `user@example.com` 5.1.10 `RESOLVER.ADR.RecipientNotFound` -> real
    dead. Correct.
  - `user@example.com` IONOS said 5.0.0; the text is `550 Mailbox is full /
    Blocks limit exceeded / Inode limit exceeded` -> **over-quota, address live**
    (cPanel account limit).
  - `user@example.com` IONOS said 5.0.0; the mail was **forwarded** to
    `user@example.com`, which refused it:
    `550 The mail server detected your message as spam` -> **live, recipient-side
    forward + spam filter**.
  - `user@example.com` IONOS said 5.0.0; real text is
    `SMTP error for GREETING command, host mail.ident.com (107.0.132.111) reason:
    501 5.7.0 Domain must resolve` -> failed **at the greeting, before the
    recipient was ever checked**. Their MX (a shared `ident.com` host), not us.
    Our relay PTR is fine (`mout/perfora.net`).
  - No `5.7.515`/`5.7.509` anywhere, DKIM `s1-ionos` on every returned original.
    **True hard-bounce rate 1/69 = 1.4%.** 0 vs 4 on ~70 sends is sample noise.
- **THE BUG.** `auth_enforcement.DEAD_MAILBOX_CODES` was `("5.0.", "5.1.")`, so a
  bare **5.0.0** counted as proof of death — and IONOS stamps 5.0.0 into the DSN
  block whenever the remote server gives an unclassified 550. RFC 3463 defines
  5.0.0 as *"Other undefined status"*. All four NDRs above were written to
  `suppressed_addresses.txt`, so **three LIVE prospects were deleted**.
  Fixed:
  1. `DEAD_MAILBOX_CODES = ("5.1.",)`; 5.0.x is a new `GENERIC_FAILURE_CODES`
     that returns `dead_mailbox` **only** when `EXPLICIT_DEAD_PHRASES` names the
     mailbox ("no such user", "recipient not found", "wasn't found", ...), and a
     new kind **`unproven`** otherwise (reported, never suppressed).
     `harvest_bounces.is_dead_status` + `DEAD_STATUS_RE` narrowed to `^5\.1\.`.
  2. New `OVER_QUOTA_PHRASES` -> kind **`quota`** ("mailbox is full", "blocks
     limit exceeded", "inode limit exceeded", ...), reported as
     OVER-QUOTA, never suppressed.
  3. `CONTENT_BLOCK_PHRASES` += `detected your message as spam` (the real
     forward wording; it never contained the shorter `detected as spam`).
  4. `RECIPIENT_POLICY_PHRASES` += `domain must resolve` -> the existing POLICY
     quarantine (labelled "address live", never re-sent, since that gateway
     refuses the connection outright).
  `harvest_bounces` carries the same phrases in its prose `POLICY_PHRASES`
  (defence in depth for a notice with no RFC 3464 part) and prints two new
  buckets. New `mail_verify.remove_suppressed()` (temp file + `os.replace`).
- **Un-suppressed** `user@example.com` and `user@example.com` (fully
  sendable again) and re-ran the harvest: it now reports **1 dead** (jclaudio),
  1 content block, 1 quota, 1 policy. `carmen@` is back in the file but as
  `POLICY recipient-side refusal (address live); never re-send`. File delta is
  exactly those 4 lines; 111 lines, comments intact.
- **Role leakage on the buyer channel (recurring).** Oct 20 sent
  `requests@`, `messages@`, `pilates@`, `rx@`, `cobblehill@` as if people (6 of
  30 once `studio@`x2 is counted). Added `request`, `message`, `pilates`, `rx`,
  `cobblehill` to `find_contacts.ROLE_LOCAL_PREFIXES` + `data/role_prefixes.txt`.
  **`studio@` and `dds@` stay people on purpose** (owner/brand boxes in a
  one-to-three person shop, same policy as `smile@`/`bakery@`/`elevate@`).
  Same day, from the batch already staged for Oct 21 (staged 00:07, before the
  rule): also added `rentals`, `homevisits`, `printing`, `treatment`, `bellevue`
  -> **today's queued 30 now reads 5/30 would be blocked**, but it is already in
  the Scheduled folder; re-stage if it must be clean.
- **Partner meter was under-filled for a structural reason, not a pool reason.**
  `2026-10-19` and `2026-10-20` both asked for 50 and scheduled **39 of 39** with
  2774/3022 eligible after gates. `partner_outreach.py` sliced candidates to
  `--limit` **before** the mailbox probe, so every DEAD probe result silently
  reduced the batch (the probe is the only filter between the limit and the
  plan). Measured today: **9 of the first 50 partner candidates are cached DEAD**
  (~18-22%), which is the missing ~11. Fixed in `partner_outreach.py`: probe
  `limit + 40%` (min 10) in the SAME verifier call, then keep the first `limit`
  survivors. **`LIMIT` stays 50** — the fix lands 50, it does not raise the meter
  (raising it to 64 would have sent up to 64 on a clean day). `partner_refill.sh`
  comment updated; `GAP=4`, window 13:00-16:20.
- **Clicks Oct 20:** `user@example.com` (buyer, sent 10:49) clicked the
  rescue page 4x over 2 min at 14:49Z — real browsing. `user@example.com` and
  `user@example.com` fired `partner-program` tokens from 72.145.76.96 and
  48.209.223.64 (Microsoft range) = gateway prefetch, not people.
- **No prospect replies, no opt-outs** on Oct 20. DMARC reports still arriving
  (Fastmail, Mimecast). No `example-inbox` forward bounce -> forward off. ✓
- **Temerarii/Dom — handled by Vinny directly, drop it.** The meeting (booked
  2026-10-19 23:00 for Tue 4:30pm CDT) was **cancelled at 17:34 EDT on Oct 20**,
  13 minutes after the "Need to move our 5:30" message. **That message was Vinny
  sending by hand, not the pipeline** — the cold-outreach code does not send
  follow-ups or replies to leads; anything conversational in `Sent Items` is his.
  Vinny confirmed **2026-10-21 that he has spoken with Dom**, so this is not an
  open thread and needs no automated follow-up. Still: do not suppress
  `temerarii.com` (it is a live relationship, and it is the only real reply this
  campaign has produced).
- Tests: `test_outreach.py` **260/0** (was 245; +15 cases covering quota,
  content, policy, unproven, a 5.0.0 that names the mailbox, and an
  IONOS-style bare-5.0.0 NDR feeding its human reason through
  `structured_failures_detail` into the classifier), `test_email_scan.py` 70/0,
  `test_csv_append.py` 31/0, `test_directory_prospects.py` 85/0. Nothing sent.
  Backups: `*.bak-20261021-classifier`.

### 2026-10-21 — the Oct 21 buyer batch was re-staged clean

Vinny: *"Might as well restage them."* The 30-message batch staged at 00:07 was
built with the old role rule, so it still carried 5 function boxes
(`user@example.com`, `user@example.com`,
`user@example.com`, `user@example.com`, `user@example.com`).
Nothing had sent yet (09:00 was still ahead), so:

1. Deleted all 30 from the IONOS `Scheduled` folder over IMAP
   (`+FLAGS \Deleted` then `EXPUNGE`; 30 -> 0).
2. Rolled their `state.json` `contacted` entries back — only entries whose
   `status` was `scheduled` **and** `scheduled_local` started with today, so no
   real send history was touched (1227 -> 1197). Backups:
   `state.json.bak-restage-20261021`, `state.json.bak-restage2-20261021-011228`.
   **Re-staging without this step silently burns the batch**: `state.json` is
   what stops a domain being mailed twice, so the deleted 30 would never come
   back and the run would quietly send 30 different addresses instead.
3. Re-ran `daily_outreach_refill.sh` (LIMIT=30, GAP=6, START=same day 09:00).

Result: **30 staged, read-back `RESULT: OK`, 09:00-11:52 local.** Under the new
role rule the queue is **0/30 blocked**, versus 5/30 before. `sendable person
addresses` 286 -> 278 and `role boxes dropped` 2879 with the new tokens. The 5
swapped in: `user@example.com`, `user@example.com`,
`user@example.com`, `user@example.com`, `user@example.com`.
The partner batch (13:00, staged 09:30) is unaffected.
