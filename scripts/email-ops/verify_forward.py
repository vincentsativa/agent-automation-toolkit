#!/usr/bin/env python3
"""
Verify the hello@ -> Gmail forward is gone (or still active).

Sends a uniquely-marked test message TO hello@example.com:
  - if it shows up in the forward target's mailbox  -> forward STILL active
  - if it does not                                   -> forward is removed

Why this works: a successful forward leaves no trace on the IONOS side (no
bounce), so the ONLY reliable check is looking at the destination. This script
sends the probe and confirms it reached hello@; you check the Gmail side.

Usage:
  python verify_forward.py                       # send probe, print instructions
  python verify_forward.py --dest someone@x.com  # name the mailbox to check
"""
from __future__ import annotations
import email
import imaplib
import smtplib
import ssl
import sys
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from ionos_mail import _creds  # reuse credential resolution

USER, PW = _creds()
DEST = "user@example.com"


def main():
    dest = DEST
    if "--dest" in sys.argv:
        dest = sys.argv[sys.argv.index("--dest") + 1]
    subj = "[VERIFY] forward-removed check " + datetime.now().strftime("%H:%M:%S")
    body = (f"Probe sent {datetime.now().isoformat(timespec='seconds')}.\n\n"
            f"If this appears in {dest}, the hello@ -> Gmail forward is STILL active.\n"
            f"If it does NOT appear there, the forward is gone.\n")
    msg = MIMEText(body)
    msg["From"] = USER
    msg["To"] = USER
    msg["Subject"] = subj
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="phantom-byte.com")
    s = smtplib.SMTP("smtp.ionos.com", 587, timeout=30)
    s.starttls()
    s.login(USER, PW)
    s.send_message(msg)
    s.quit()
    print("probe sent ->", USER, "| subject:", subj)

    time.sleep(6)
    M = imaplib.IMAP4_SSL("imap.ionos.com", 993, ssl_context=ssl.create_default_context())
    M.login(USER, PW)
    M.select("INBOX", readonly=True)
    typ, data = M.search(None, 'SUBJECT', f'"{subj}"')
    ok = bool(data[0].split())
    M.logout()
    print("reached hello@ INBOX:", "YES" if ok else "NO (check IONOS)")
    print()
    print("NOW: open", dest)
    print(f"  search subject: {subj}")
    print("  - present  => forward is STILL active")
    print("  - absent   => forward removed ✓")


if __name__ == "__main__":
    main()
