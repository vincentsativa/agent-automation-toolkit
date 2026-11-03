# Recipient verification and bounce suppression

How a cold send stops mailing dead mailboxes. Read this before any run whose send volume is large enough that a 10 percent bounce rate matters, and before touching `mail_verify.py` or `harvest_bounces.py`.

## The order: the DSN read is authoritative, the RCPT probe is a pre-filter

A high bounce count is a LIST problem, not a sending problem, and the only place the truth about an address exists is the provider's own bounce notices sitting in the inbox.

1. **Read the provider's bounce notices FIRST, from the mailbox, before forming any theory.** Do not start from the code, the CSV, or a probe. The DSNs name the exact addresses that failed and the SMTP code and reason for each, which is the ground truth the whole fix is built on. In his words, the answer is in the mail, so go to the mail. A theory built before the bounce text is read is usually about the wrong layer.
2. **Classify only permanent failures as dead.** A 5.x.x status, or prose with no code at all that describes a permanent condition, suppresses the address. A 4.x.x is a greylist, a full mailbox, or a rate limit: a deferral, never a death, and treating it as dead deletes live prospects. IONOS and Google both describe permanent failures in prose with no status code anywhere, so a code-only matcher misses a third of them.
3. **Cut the "Original message" block before extracting any address.** A DSN appends the headers of the sent message, including the sender's own From and Reply-To. Parsing that block as a recipient list makes the sender suppress itself.
4. **Suppress at ADDRESS level, not domain level, for a DSN.** A dead `info@` is one mailbox; the owner's own address at the same company is a real prospect. The only reason a whole domain dies is DNS proving it accepts no mail at all.
5. **Make the harvest an automatic first step of the send path, never a step someone has to remember.** A suppression file only helps if it is current, and a documented order of operations is a step that gets skipped. The send script runs the harvest itself before it selects a single row, and a harvest failure is caught and printed so it never blocks a send whose addresses are already on file.
6. **A list the pipeline did not harvest is unverified regardless of its labels.** A status column beside a contact file is the other tool's assertion, not evidence.

## The RCPT probe: what it is worth and what it cannot do

A pre-send RCPT probe kills a real share of dead addresses before anything leaves. It is worth running, and it is not proof.

- **Measured floor and ceiling, on one real batch of 13 hard bounces: the probe caught 10 as DEAD at RCPT time, and the other 3 were unmaskable by RCPT at all because the receiving platform answers 250 for any address.** Treat those as two stacked checks, not competing ones. A 550 is a real finding; a 250 is not evidence.
- **Always corroborate a 250 with a random-local-part probe against the same domain.** If a random address is accepted too, the domain accepts anything and the RCPT proved nothing. Report those CATCH_ALL and flagged. This is the single check that decides whether an OK means anything. Google Workspace is the common case, and it answers 250 for a random local part.
- **Catch-all domains cannot be proven before the send, and the decision is to KEEP them by default.** Google Workspace answers 250 for any local part, so three of the 2026-09-28 bounces (`tsafla.com`, `guardianlit.com`, `collegegirlcleaningservice.com`) read CATCH_ALL and always will. Holding them back would drop real prospects on a network fact, and the rule is to err toward keeping. The correct backstop is the automatic DSN harvest, which suppresses the first real bounce permanently, so the default is to keep them and report them by name. `outreach.py --hold-catch-all` is the opt-in for the other branch when Vinny asks to hold them out of a cold list; it needs no code change. Separately, a host that accepts at RCPT and bounces later at LMTP (`magpiesmoderngeneral.com` did) and a host that accepts a live mailbox but bounces an owner address are both unprovable by any pre-send probe, and the DSN harvest is the only thing that catches them.
- **Never report DEAD on a 4xx, a timeout, or a refused connection.** A probe that did not run is not evidence that a mailbox is gone. Some MX hosts drop port 25 from a residential IP entirely, and calling that dead empties the list on a network fact instead of a mail fact.
- **UNKNOWN is allowed to send and is always reported by name. `outreach.py --hold-unknown` is the opt-in to hold unverified addresses out of a single run, and it NEVER suppresses them.** A timeout, a 4xx, or a refused connection is not evidence that a mailbox is gone, so holding an UNKNOWN is a per-run decision only: nothing is written to the suppression file, and the address returns and is re-probed on the next run. Only DEAD is ever persisted.
- **A domain with no MX is not dead.** Per RFC 5321 5.1 it is served by its own A/AAAA record, so fall back to the bare domain and probe that before reaching any conclusion.
- **Try every MX host, best preference first, and break on the first definitive answer.** A single host can defer a message another host accepts.
- **Present the real sending identity in `MAIL FROM`, not a throwaway verification address.** A host that runs sender verification answers a bare probe sender with a 4xx about the SENDER, which reads as UNKNOWN and hides the recipient's real status. No message body is ever transmitted by a probe, so there is nothing to bounce back.
- **Check null MX and NXDOMAIN before probing anything, and check the A/AAAA route before killing a no-MX domain.** Both null MX and NXDOMAIN are facts from the domain's own DNS. A null MX (RFC 7505, a single `0 .` record) means the domain accepts no mail at all and every address on it is dead by definition, which no port-25 probe will tell you because it just times out. But a domain with NO MX record is not dead: RFC 5321 5.1 serves it on its own A/AAAA record, so probe the bare domain. Only a domain with no MX AND no A/AAAA has no mail route at all and is dead from DNS alone. Measured 2026-09-28: `plushrecordingstudios.com` and `bhbdistributorsinc.com` publish no MX but do publish an A record, so an unconditional "no MX = dead" rule was a false-death waiting to delete a live bare-host mail server.

## Reading a DNS answer: parity before a death sentence

A DNS negative is a death sentence for an address, so it must be trusted only as far as the resolver is trusted.

- **A DNS-over-HTTPS negative that disagrees with a live SMTP answer is a resolver bug, not a finding.** Validate the resolver against an independent resolver on the same domain before any negative from it deletes a prospect. The failure mode is asymmetric: a missed death costs one bounce, a false death silently deletes a real local business.
- Prefer the live protocol answer when a resolver and a live probe disagree, and fix the resolver in the same turn so the wrong fact cannot return.

## Port 25 is blocked from WSL and open from Windows

Where the RCPT probe has to run, when the Linux side cannot reach port 25.

- **Do not conclude the probe is impossible from a Linux timeout.** Test the same host and port from the Windows side of the machine before designing around a block. The Windows side reaches port 25 over IPv6 on this host while WSL times out on both IPv4 and IPv6.
- **Choose the socket family from the address you resolved, and try BOTH families for the host.** A probe that forces IPv6 and is handed an IPv4 address fails with "None of the discovered or specified addresses match the socket address family", which reads as a probe failure and silently downgrades verdicts to UNKNOWN. The deeper trap is picking only the first family that resolves: measured 2026-09-28, an M365 MX published an AAAA that answered port 25 and an A that timed out, so a probe that stopped at the A record called a live mailbox UNKNOWN for no reason. Resolve every address of the MX host and try each until one connects.
- **A first-pass UNKNOWN gets one retry, on a longer connect timeout and a gentler concurrency.** A timeout is often a slow or throttled MX, not a blocked port, and a retry recovers the transient cases. A host that silently drops port 25 from this vantage point still ends UNKNOWN, which is honest and is reported by name; never convert that into a death.
- **The Windows bridge.** Send the whole address list as one batch on stdin to a single PowerShell process and read tab-separated verdicts back. One process per list, not one per address. Keep the probe source embedded in the Python module that reads its output so the two cannot drift apart.
- **Pass the probe as a base64 `-EncodedCommand`, never as a `-File`.** The encoded form never touches the Windows filesystem, so there is no temp path that must exist, no fixed file to be refused by the stale-overwrite guard, and no quoting or user-name character to survive. The earlier `-File` route needed a fresh `mktemp` directory under the Windows temp root on every call, and when that path was wrong the probe silently returned nothing and every address read UNKNOWN.
- **The submission relay is not a verifier.** Running `RCPT TO` against the account's own SMTP relay answers 250 for every recipient, including addresses already known to be dead, because a relay is not the destination. Do not build the check on it.

## Suppression file rules

- Tab-separated, address and reason. Read only the first field: reading the whole line makes `addr<TAB>reason` an address matching nothing, and suppression silently stops suppressing.
- Append-only and idempotent. Never rewrite the file in place, so a crash mid-run cannot truncate a list that already exists.
- A dead domain earns domain-level suppression only from a DNS fact (null MX or NXDOMAIN). Every DSN reason stays address level.
- Addresses on the file are never re-probed and never re-sent.

## Reporting a bounce problem to him

Name the mechanism, the number, and the layer the failure was in, and say plainly which part of the fix is verified and which is still open. A count of dead addresses by kind (DSN-proven, DNS-proven, catch-all) with the reason for each is what makes the result legible, and an unresolved item named as unresolved is what keeps the rest of the report trustworthy.
