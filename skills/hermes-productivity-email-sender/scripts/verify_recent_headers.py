#!/usr/bin/env python3
"""List recent INBOX and Spam headers with parsed subjects and attachment names.

Use this after a scripted send when `verify_delivery.py` returns NOT FOUND.
Subjects over roughly 60 characters are RFC-2822 folded in the stored header,
so an exact-string match misses mail that is sitting in INBOX. This prints the
decoded, unfolded subject so the comparison is against what the mail actually
says. A match here is proof of delivery; it is never a reason to re-send.

Usage:
    set -a; source ~/.config/phantombyte/mailer.env; set +a
    python3 verify_recent_headers.py --count 10
    python3 verify_recent_headers.py --contains "Draft"   # exit 1 when no match
"""
import argparse
import email
import imaplib
import os
import sys
from email.header import decode_header, make_header


def parsed_subject(msg):
    return str(make_header(decode_header(msg.get("Subject", ""))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10, help="headers per mailbox")
    ap.add_argument("--contains", default=None, help="case-insensitive subject filter")
    ap.add_argument("--boxes", default="INBOX,Spam")
    ap.add_argument("--user", default="hello@phantom-byte.com")
    a = ap.parse_args()

    pw = os.environ.get("PHANTOMBYTE_SMTP_PASS")
    if not pw:
        sys.exit(
            "PHANTOMBYTE_SMTP_PASS not set. Run: "
            "set -a; source ~/.config/phantombyte/mailer.env; set +a"
        )

    M = imaplib.IMAP4_SSL("imap.ionos.com", 993)
    M.login(a.user, pw)
    hits = 0
    for box in a.boxes.split(","):
        typ, _ = M.select(box, readonly=True)
        if typ != "OK":
            print(box, "not selectable")
            continue
        typ, data = M.search(None, "ALL")
        ids = data[0].split()[-a.count:]
        print("==", box, "last", len(ids))
        for i in reversed(ids):
            typ, d = M.fetch(i, "(RFC822)")
            msg = email.message_from_bytes(d[0][1])
            subj = parsed_subject(msg)
            atts = [p.get_filename() for p in msg.walk() if p.get_filename()]
            print(msg.get("Date"), "|", subj, "|", atts)
            if a.contains and a.contains.lower() in subj.lower():
                hits += 1
    M.logout()

    if a.contains:
        print("matches:", hits)
        sys.exit(0 if hits else 1)


if __name__ == "__main__":
    main()
