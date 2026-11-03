#!/usr/bin/env python3
"""Verify mail authentication for a domain two ways: the DNS records, and the
Authentication-Results header on real delivered mail.

Usage:
    python3 verify-deliverability.py <domain>

Credentials come from the environment, never from the command line:
    MAIL_SMTP_HOST   default smtp.ionos.com
    MAIL_IMAP_HOST   default imap.ionos.com
    MAIL_USER        the mailbox to log in as, e.g. hello@example.com
    MAIL_PASS        its password

Exit code 0 means the DNS checks ran. The received-mail section reports SKIPPED
when no credentials are present; that is a gap to declare, never something to
paper over with a summary.
"""

import email
import json
import os
import smtplib
import ssl
import sys
import time
import urllib.parse
import urllib.request

DOH = [
    ("Cloudflare", "https://cloudflare-dns.com/dns-query"),
    ("Google", "https://dns.google/resolve"),
]


def resolve(name, rtype):
    """Return TXT answer strings from both resolvers, or None on failure."""
    out = {}
    for label, base in DOH:
        q = urllib.parse.urlencode({"name": name, "type": rtype})
        req = urllib.request.Request(base + "?" + q)
        if "cloudflare" in base:
            req.add_header("accept", "application/dns-json")
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.load(r)
        except Exception as exc:  # network or resolver failure
            out[label] = "ERROR: %s" % exc
            continue
        answers = [a.get("data") for a in data.get("Answer", [])]
        status = data.get("Status")
        # Status 3 is NXDOMAIN: the record is absent, which is a finding itself.
        out[label] = "NXDOMAIN (status 3)" if status == 3 else (answers or "no answer")
    return out


def check_records(domain):
    for rtype in ("TXT", "MX", "NS"):
        print("\n=== %s / %s ===" % (domain, rtype))
        for label, value in resolve(domain, rtype).items():
            print("  %-11s %s" % (label + ":", value))
    print("\n=== _dmarc.%s / TXT ===" % domain)
    for label, value in resolve("_dmarc." + domain, "TXT").items():
        print("  %-11s %s" % (label + ":", value))
    for sel in ("s1", "s2", "default", "s1-ionos", "s2-ionos"):
        print("\n=== %s._domainkey.%s / TXT ===" % (sel, domain))
        for label, value in resolve("%s._domainkey.%s" % (sel, domain), "TXT").items():
            print("  %-11s %s" % (label + ":", value))


def read_headers(user, password, imap_host, count=8):
    """Fetch the Authentication-Results header off recent delivered mail."""
    import imaplib

    box = imaplib.IMAP4_SSL(imap_host, 993, ssl_context=ssl.create_default_context())
    box.login(user, password)
    found = []
    for folder in ("INBOX", "Spam"):
        try:
            status, _ = box.select(folder, readonly=True)
        except Exception:
            continue
        if status != "OK":
            continue
        _, ids = box.search(None, "ALL")
        for i in ids[0].split()[-count:]:
            status, data = box.fetch(i, "(BODY.PEEK[HEADER])")
            if status != "OK" or not data or not data[0]:
                continue
            msg = email.message_from_bytes(data[0][1])
            found.append((folder, str(msg.get("Subject"))[:70], msg.get("Authentication-Results")))
    box.logout()
    return found


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    domain = sys.argv[1]
    user = os.environ.get("MAIL_USER")
    password = os.environ.get("MAIL_PASS")
    smtp_host = os.environ.get("MAIL_SMTP_HOST", "smtp.ionos.com")
    imap_host = os.environ.get("MAIL_IMAP_HOST", "imap.ionos.com")

    check_records(domain)

    print("\n=== received-mail proof ===")
    if not (user and password):
        print("  SKIPPED: set MAIL_USER and MAIL_PASS for a mailbox on this domain.")
        print("  No received-mail proof. Say so in the report; do not imply one.")
        return 0

    mark = "post-fix verification %d" % int(time.time())
    from email.mime.text import MIMEText

    msg = MIMEText("seed send")
    msg["From"] = user
    msg["To"] = user
    msg["Subject"] = mark
    with smtplib.SMTP(smtp_host, 587, timeout=60) as s:
        s.starttls(context=ssl.create_default_context())
        s.login(user, password)
        s.send_message(msg)
    print("  seed sent to %s, waiting 45s for delivery" % user)
    time.sleep(45)

    for folder, subject, ar in read_headers(user, password, imap_host):
        print("  --- [%s] %s" % (folder, subject))
        print("      %s" % (ar if ar else "(no Authentication-Results header)"))
    print("\n  Read the dmarc=, spf=, and dkim= results off a POST-SEND message.")
    print("  policy.dmarc= on an older message reflects the record at its own receipt time.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
