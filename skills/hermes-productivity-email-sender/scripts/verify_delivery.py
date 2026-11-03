#!/usr/bin/env python3
"""Read a just-sent message back out of the recipient's mailbox over IMAP.

A clean SMTP return proves the server accepted the message, not that it was
delivered with its attachments intact. This is the read-back that closes the
loop for the usual self-send to hello@phantom-byte.com.

Usage:
    set -a; source ~/.config/phantombyte/mailer.env; set +a
    python3 verify_delivery.py --subject "Temerarii meeting package"

Exit 0 and print the delivered headers plus attachment filenames when found;
exit 1 when it is in neither INBOX nor Spam after the wait.

Pitfall this exists to kill: a scripted SMTP send is NOT filed into the
"Sent Items" folder, so searching there proves nothing at all. The delivered
copy lands in the recipient's INBOX, usually within seconds.
"""
import argparse
import email
import imaplib
import os
import sys
import time
from email.header import decode_header, make_header

ADDR = "hello@phantom-byte.com"


def dh(value):
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return value or ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True, help="exact subject line to search for")
    ap.add_argument("--folders", default="INBOX,Spam")
    ap.add_argument("--attempts", type=int, default=6)
    ap.add_argument("--interval", type=int, default=10, help="seconds between polls")
    args = ap.parse_args()

    pw = os.environ.get("PHANTOMBYTE_SMTP_PASS")
    if not pw:
        sys.exit("REFUSED: source ~/.config/phantombyte/mailer.env first")

    M = imaplib.IMAP4_SSL("imap.ionos.com", 993)
    M.login(ADDR, pw)

    for _attempt in range(args.attempts):
        for folder in [f.strip() for f in args.folders.split(",") if f.strip()]:
            st, _ = M.select('"%s"' % folder, readonly=True)
            if st != "OK":
                continue
            st, data = M.uid("SEARCH", None, "SUBJECT", '"%s"' % args.subject)
            if st != "OK" or not data or not data[0]:
                continue
            for uid in data[0].split():
                st, fetched = M.uid("FETCH", uid, "(RFC822)")
                if st != "OK" or not fetched or not isinstance(fetched[0], tuple):
                    continue
                msg = email.message_from_bytes(fetched[0][1])
                print("DELIVERED to %s, uid=%s" % (folder, uid.decode()))
                for header in ("Date", "From", "To", "Subject"):
                    print("  %s: %s" % (header, dh(msg.get(header))))
                atts = [p.get_filename() for p in msg.walk() if p.get_filename()]
                print("  Attachments: %s" % atts)
                M.logout()
                return 0
        time.sleep(args.interval)

    print("NOT FOUND in %s after %ds" % (args.folders, args.attempts * args.interval))
    M.logout()
    return 1


if __name__ == "__main__":
    sys.exit(main())
