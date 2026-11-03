# imap_readback.py -- prove an email actually landed in Vinny's inbox.
#
# USE AFTER EVERY SEND THAT MATTERS (reports, corrected copies, deliveries):
#   python ~/AppData/Local/hermes/skills/productivity/email-sender/scripts/imap_readback.py \
#       --subject "Keyword Research" \
#       --attachment "~/keyword_research_article233.txt"
#
# WHAT IT PROVES: the message exists in INBOX with the searched subject, and the
# attachment's decoded byte length equals the file on disk. That is the only
# evidence that separates "SMTP said sent" from "the file arrived intact".
#
# TWO HOST TRAPS THIS ENCODES:
# 1. IONOS IMAP requires the search criteria as ONE parenthesized string:
#    M.search(None, '(SUBJECT "Keyword Research")'). Passing the parts as
#    separate arguments (M.search(None, "SUBJECT", "Keyword Research")) makes the
#    server answer BAD [b'expected search-key instead of RESEARCH'], because it
#    lexes the bare second argument as a search key.
# 2. Attachment paths given to Windows Python must be native Windows paths; the
#    script normalises separators so an MSYS-style path does not silently size
#    nothing.

import argparse
import email
import imaplib
import os
import sys

HOST = "imap.ionos.com"
USER = "hello@example.com"
PASSWORD = "YOUR_PASSWORD"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True, help="subject substring to search for")
    ap.add_argument("--attachment", default=None, help="local file that should have been attached")
    ap.add_argument("--expect", action="append", default=[], help="text that must appear in the body; repeatable")
    a = ap.parse_args()

    M = imaplib.IMAP4_SSL(HOST)
    M.login(USER, PASSWORD)
    M.select("INBOX")
    typ, data = M.search(None, '(SUBJECT "%s")' % a.subject.replace('"', ""))
    ids = data[0].split()
    print("matches in INBOX:", len(ids))
    if not ids:
        M.logout()
        sys.exit(2)

    typ, d = M.fetch(ids[-1], "(RFC822)")
    msg = email.message_from_bytes(d[0][1])
    print("subject:", msg["Subject"])
    print("to:", msg["To"])
    print("date:", msg["Date"])

    ok = True
    saw_attachment = False
    for part in msg.walk():
        fn = part.get_filename()
        if fn:
            saw_attachment = True
            payload = part.get_payload(decode=True) or b""
            print("attachment:", fn, len(payload), "bytes")
            if a.attachment:
                local = os.path.normpath(a.attachment)
                if not os.path.exists(local):
                    print("LOCAL FILE NOT FOUND:", local)
                    ok = False
                else:
                    size = os.path.getsize(local)
                    same = size == len(payload)
                    print("local file:", size, "bytes; identical size:", same)
                    ok = ok and same
    if a.attachment and not saw_attachment:
        print("NO ATTACHMENT IN THE DELIVERED MESSAGE")
        ok = False

    body = ""
    for part in msg.walk():
        if part.get_content_type() == "text/plain" and not part.get_filename():
            body = (part.get_payload(decode=True) or b"").decode("utf-8", "replace")
            break
    print("body chars:", len(body))
    for needle in a.expect:
        present = needle in body
        print("body contains %r: %s" % (needle, present))
        ok = ok and present

    M.logout()
    print("READBACK:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
