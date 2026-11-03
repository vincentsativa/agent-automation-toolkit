# IONOS Credentials & Access (Updated May 8, 2026)

## SMTP — CONFIRMED WORKING ✅
- **Server:** smtp.ionos.com
- **Port:** 587 (TLS)
- **Username:** hello@phantom-byte.com
- **Password:** VJBvjbhydro1202$$
- Tested and working May 8 2026 — sent email from hello@phantom-byte.com to itself with attachment support

## Sending Email with Attachments (Python)
```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email(to, subject, body, attachment_path=None):
    msg = MIMEMultipart()
    msg['From'] = 'hello@phantom-byte.com'
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = attachment_path.split("/")[-1]
            part.add_header('Content-Disposition', f'attachment; filename={filename}')
            msg.attach(part)
    
    server = smtplib.SMTP('smtp.ionos.com', 587, timeout=30)
    server.starttls()
    server.login('hello@phantom-byte.com', 'VJBvjbhydro1202$$')
    server.send_message(msg)
    server.quit()
```

## DNS / Domain Changes: USE THE API, NEVER THE PANEL

Anything that changes a DNS record on an IONOS domain is done through the IONOS DNS API. Not the web panel, not `my.ionos.com`, not a browser. The browser path cannot log in (it hits a 2FA wall) and burns the turn for nothing. The API does the same job in one PUT.

- **Base:** `https://api.hosting.ionos.com/dns/v1`
- **Auth header:** `X-API-Key: <public_prefix>.<secret>`
- **Key file:** `/mnt/c/Users/<user>/workspace/memory/ionos-credentials.md`
- **Zones:** phantom-byte.com = `f9a1e796-0c8f-11f1-8880-0a5864440f43`, vincentsativa.com = `f1c666a0-1417-11f0-aecf-0a5864441ac4`
- **Calls:** `GET /zones` (list), `GET /zones/<zone_id>` (read, get record ids), `PUT /zones/<zone_id>/records/<record_id>` with `{name, type, content, ttl, disabled, prio}` (change one record), `POST /zones/<zone_id>/records` (create), `DELETE /zones/<zone_id>/records/<record_id>` (remove). Read the zone back after any write.
- **Back up the full zone JSON before any edit**, to `/mnt/c/Users/<user>/workspace/dns-backups/`.
- KARMA, the Windows agent, uses this same API. She never opens the panel either.

## Webmail (reading mail in a browser)
- **URL:** https://webmail.ionos.com/
- **Not for DNS.** Mail is read over IMAP (`imap.ionos.com:993`), which is already scriptable.

## Portal
- **URL:** https://my.ionos.com/
- **Not for DNS work.** Any DNS task goes through the API above.

---

## Session Note — May 16, 2026

**What happened:** User asked if I could email hello@phantom-byte.com. I said "no" because `send_message` doesn't support SMTP. True but wrong — the capability exists via this script.

**The lesson:** When user asks "can you email me", check this file FIRST. The send_email() function works and is confirmed live. Do NOT say email isn't available when the SMTP credentials are documented here. The `send_message` constraint is about messaging platforms, not email in general.

**Also:** Keep SMTP credentials in memory. A memory-only copy ensures the info survives even if this reference file is ever reorganized.