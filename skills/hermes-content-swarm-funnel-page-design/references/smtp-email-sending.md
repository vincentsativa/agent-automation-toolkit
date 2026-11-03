# Sending Emails via IONOS SMTP

## Credentials
- **SMTP Host:** `smtp.ionos.com`
- **SMTP Port:** `587` (STARTTLS)
- **User:** `hello@phantom-byte.com`
- **From:** `hello@phantom-byte.com`

## Python Script Template

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

SMTP_HOST = "smtp.ionos.com"
SMTP_PORT = 587
SMTP_USER = "hello@phantom-byte.com"
SMTP_PASS = "VJBvjbhydro1202$$"

def send_email(to, subject, body_text, attachment_path=None, attachment_name=None):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain"))

    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = attachment_name or attachment_path.split("/")[-1]
            part.add_header("Content-Disposition", "attachment", filename=filename)
            msg.attach(part)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to, msg.as_string())

    print(f"Email sent to {to}")
```

## Usage Pattern
1. Write the script to a `.py` file (inline Python with f-strings causes escaping issues, always use a file)
2. Run with `python3 /path/to/script.py`
3. For multiple attachments, call `msg.attach()` for each file

## Pitfalls
- **Don't inline Python scripts via `python3 -c`**, f-strings, quotes, and special characters in passwords cause escaping nightmares. Write to a `.py` file and execute it.
- **Always use STARTTLS** (`server.starttls()`), IONOS requires TLS on port 587.
- **Attachment filenames**, `Content-Disposition` uses `filename=` not `filename=` with f-string shorthand. Use `part.add_header("Content-Disposition", "attachment", filename="name.txt")`.