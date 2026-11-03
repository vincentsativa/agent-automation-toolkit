# Email Attachment Delivery Technique (IONOS SMTP)

Send an IronPulse (or any skill's output) as an email attachment with themes/analysis in the body.

## Reliable Pattern: Standalone Python Script

**DO NOT** use inline heredocs inside `terminal()` — triple-quoted strings inside a `python3 -c "..."` shell command cause SyntaxErrors due to quote escaping. Always write a standalone `.py` file and execute it.

## Step-by-Step

1. **Write the script to /tmp:**

```python
#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

msg = MIMEMultipart()
msg['From'] = 'hello@phantom-byte.com'
msg['To'] = 'hello@phantom-byte.com'
msg['Subject'] = 'IronPulse AI News Report - YYYY-MM-DD'

body = """[Themes analysis and article ideas go here in the body]

Full report with all 20 ranked stories is attached.

-- Hermes
"""

msg.attach(MIMEText(body, 'plain'))

with open('~/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt', 'r') as f:
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(f.read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', filename='ironpulse-YYYY-MM-DD.txt')
    msg.attach(attachment)

with smtplib.SMTP('smtp.ionos.com', 587) as server:
    server.starttls()
    server.login('hello@phantom-byte.com', 'VJBvjbhydro1202$$')
    server.sendmail('hello@phantom-byte.com', 'hello@phantom-byte.com', msg.as_string())

print('Email sent successfully')
```

2. **Write via `write_file` tool** to `/tmp/send_ironpulse_email.py`

3. **Execute via terminal:**
   ```bash
   python3 /tmp/send_ironpulse_email.py
   ```

## Verify

After sending, the script prints "Email sent successfully" to stdout. No return code checking needed beyond exit code 0.

## Key Differences from Inline

| Method | Result |
|--------|--------|
| `python3 -c "..."` with triple-quoted body | SyntaxError: unterminated string |
| `write_file` to `/tmp/` + `python3 /tmp/script.py` | Works reliably |

## SMTP Config

- Server: smtp.ionos.com:587
- TLS required: `server.starttls()`
- Username: hello@phantom-byte.com
- Password: VJBvjbhydro1202$$
- Recipient: hello@phantom-byte.com
