#!/usr/bin/env python3
"""Stage ONE message in an IONOS IMAP Drafts folder, then verify it by read-back.

Nothing is sent. The message lands in Drafts for the user to open and press send.

Usage:
  python3 stage_draft.py --to someone@example.com \
      --subject "Short subject" --body-file body.txt [--attach /path/file.docx]

body.txt is plain text. Paragraphs are separated by a BLANK LINE and become <p>
paragraphs in the HTML part; single newlines become <br>. Both parts are built from
the same string so they cannot drift.

Before appending, the folder is read and its UIDs recorded. After appending, the new
UID is found by set difference (an append does not return a UID), the stored message
is fetched with BODY.PEEK[], and every check below must pass or the run exits 1:

  From is the account address, To matches, Subject is on the header and NOT in the
  body, the paragraph count survived, and the attachment is present when one was given.

When --replace is passed, every message already in Drafts is copied to Trash first
(Trash confirmed OK) and only then flagged deleted; the folder must read empty before
the replacement is appended, so a stale draft cannot survive a restage.

The signature block is supplied by the caller in the body file. Set it from a recent
message in the account's Sent Items folder rather than retyping it.
"""
import argparse
import email
import email.utils
import html
import imaplib
import mimetypes
import os
import re
import ssl
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

IMAP_HOST = "imap.ionos.com"
FROM_ADDR = "hello@phantom-byte.com"
FROM_NAME = "Vinny Barreca"
REFERENCE = ("~/skills/user-profile/"
             "vinny-profile-extension/references/ionos-email-access.md")


def mail_password():
    pw = os.environ.get("PHANTOMBYTE_SMTP_PASS", "")
    if pw:
        return pw
    try:
        txt = open(REFERENCE).read()
    except OSError:
        return ""
    m = re.search(r"\*\*Password:\*\*\s*(\S+)", txt)
    return m.group(1) if m else ""


def linkify(escaped):
    """Bare URLs in the body become anchors so the visible text stays clean."""
    return re.sub(r"(https?://[^\s<]+)", r'<a href="\1">\1</a>', escaped)


def to_html(text):
    out = []
    for para in text.split("\n\n"):
        para = para.strip()
        if para:
            out.append("<p>" + linkify(html.escape(para).replace("\n", "<br>")) + "</p>")
    return "<html><body>" + "".join(out) + "</body></html>"


def norm_subject(value):
    """A folded RFC 2047 header comes back with CRLF plus a space; compare normalized."""
    return " ".join((value or "").replace("\r", " ").replace("\n", " ").split())


def uids_in(M, folder):
    M.select(folder, readonly=True)
    st, ids = M.uid("SEARCH", None, "ALL")
    return [i.decode() for i in (ids[0].split() if ids and ids[0] else [])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--attach", default="")
    ap.add_argument("--from-name", default=FROM_NAME)
    ap.add_argument("--from-addr", default=FROM_ADDR)
    ap.add_argument("--folder", default="Drafts")
    ap.add_argument("--replace", action="store_true",
                    help="trash every existing draft in the folder before appending")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    body = open(args.body_file, encoding="utf-8").read().strip()
    if not body:
        raise SystemExit("REFUSED: body file is empty")
    if re.search(r"^\s*(subject:)", body, re.I | re.M):
        raise SystemExit("REFUSED: body carries a Subject line; that belongs in the header")
    if args.attach and not os.path.exists(args.attach):
        raise SystemExit(f"REFUSED: attachment not found: {args.attach}")

    if args.dry:
        print(f"would stage to {args.to}")
        print(f"subject: {args.subject}")
        print(f"body paragraphs: {len([p for p in body.split(chr(10)+chr(10)) if p.strip()])}")
        print(f"attachment: {args.attach or '(none)'}")
        print("signature present:" , "Vinny Barreca" in body)
        return 0

    pw = mail_password()
    if not pw:
        raise SystemExit("REFUSED: no IMAP password (set $PHANTOMBYTE_SMTP_PASS "
                         "or keep the password in ionos-email-access.md)")

    msg = MIMEMultipart("mixed")
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(body, "plain", "utf-8"))
    alt.attach(MIMEText(to_html(body), "html", "utf-8"))
    msg.attach(alt)
    if args.attach:
        ctype, _ = mimetypes.guess_type(args.attach)
        maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
        part = MIMEBase(maintype, subtype)
        part.set_payload(open(args.attach, "rb").read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment",
                        filename=os.path.basename(args.attach))
        msg.attach(part)
    msg["From"] = f"{args.from_name} <{args.from_addr}>"
    msg["To"] = args.to
    msg["Subject"] = args.subject
    msg["Date"] = email.utils.formatdate(localtime=True)

    M = imaplib.IMAP4_SSL(IMAP_HOST, 993, ssl_context=ssl.create_default_context())
    M.login(args.from_addr, pw)

    before = uids_in(M, args.folder)
    print(f"{args.folder} held {len(before)} message(s) before")

    if args.replace and before:
        M.select(args.folder)
        for uid in before:
            cp, _ = M.uid("COPY", uid, "Trash")
            print(f"  copy {uid} to Trash: {cp}")
            if cp != "OK":
                raise SystemExit("REFUSED: Trash copy failed; nothing deleted, nothing staged")
            M.uid("STORE", uid, "+FLAGS", "\\Deleted")
        M.expunge()
        left = uids_in(M, args.folder)
        if left:
            raise SystemExit(f"REFUSED: {left} survived the clear; not staging on top of them")
        before = []
        print("  folder cleared")

    r = M.append(args.folder, None, None, msg.as_bytes())
    print("append:", r[0])
    if r[0] != "OK":
        raise SystemExit(f"append failed: {r}")

    after = uids_in(M, args.folder)
    new = [u for u in after if u not in before]
    if not new:
        raise SystemExit("append reported OK but no new message appeared in the folder")
    uid = new[-1]

    st, d = M.uid("FETCH", uid, "(BODY.PEEK[])")
    raw = next((p[1] for p in d if isinstance(p, tuple)), None)
    M.logout()
    if raw is None:
        raise SystemExit("read-back returned nothing")

    stored = email.message_from_bytes(raw)
    plain = html_part = ""
    for p in stored.walk():
        if p.get_content_type() == "text/plain":
            plain = p.get_payload(decode=True).decode("utf-8", "replace")
        elif p.get_content_type() == "text/html":
            html_part = p.get_payload(decode=True).decode("utf-8", "replace")
    text_only = re.sub(r"<[^>]+>", "", html_part or plain)
    src_paras = [p for p in body.split("\n\n") if p.strip()]

    checks = {
        "from_identity": args.from_addr in (stored.get("From") or ""),
        "to": (stored.get("To") or "").strip().lower() == args.to.strip().lower(),
        "subject_header": norm_subject(stored.get("Subject")) == " ".join(args.subject.split()),
        "subject_absent_from_body": args.subject.lower() not in text_only.lower(),
        "paragraphs": (html_part.count("<p>") == len(src_paras)) if html_part else True,
        "plain_and_html": bool(plain) and bool(html_part),
        "attachment": (not args.attach) or any(p.get_filename() for p in stored.walk()),
    }
    for k, v in checks.items():
        print(f"  {'OK  ' if v else 'FAIL'} {k}")
    print(f"  uid={uid} paragraphs={html_part.count('<p>')}/{len(src_paras)}")
    bad = [k for k, v in checks.items() if not v]
    if bad:
        raise SystemExit("VERIFY FAILED: " + ", ".join(bad))
    print(f"\nDRAFT STAGED AND VERIFIED  uid={uid}  to={args.to}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
