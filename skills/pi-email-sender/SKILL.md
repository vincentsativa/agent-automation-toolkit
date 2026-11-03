---
name: email-sender
description: Send emails via IONOS SMTP with optional file attachments. Use this when Vinny asks to email him or send a document by email.
trigger: "user asks to email, send email, attach file to email, send document, or mail something"
---

# Email Sender Skill (IONOS SMTP)

> **NOTE:** This skill is ONLY for emailing Vinny (hello@example.com). For Hermes' own email (checking inbox / emailing other agents) use the `hermes-email-agentmail` skill (AgentMail). These never cross.

## When to use
- Vinny asks to email him something
- Vinny asks to "send me the document by email" or "attach to an email"
- Any request that involves sending a file or message to his email address

## Email Address
- **To:** hello@example.com
- **From:** hello@example.com

## SMTP Credentials (confirmed working May 8 2026)
- **Server:** smtp.ionos.com
- **Port:** 587 (TLS)
- **Username:** hello@example.com
- **Password:** VJBvjbhydro1202$$

## Sending Email (Python)

Write the script to a file first, then run it. Do NOT use `python3 -c "..."` inline, that approach fails with SMTPAuthenticationError even with correct credentials. Use a file instead.

```python
# send_email.py (save to user's home directory, e.g. ~/send_email.py or C:\Users\<user>\send_email.py)
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email(to, subject, body, attachment_path=None):
    msg = MIMEMultipart()
    msg['From'] = 'hello@example.com'
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = os.path.basename(attachment_path)
            part.add_header('Content-Disposition', f'attachment; filename={filename}')
            msg.attach(part)
    elif attachment_path:
        print(f"WARNING: attachment not found at {attachment_path}, sending without attachment")
    server = smtplib.SMTP('smtp.ionos.com', 587, timeout=30)
    server.starttls()
    server.login('hello@example.com', 'VJBvjbhydro1202$$')
    server.send_message(msg)
    server.quit()
    return True

send_email(
    to='hello@example.com',
    subject='Your Subject Here',
    body='Brief body text.',
    attachment_path=os.path.expanduser('~/your_document.txt')
)
```

Then run: `python ~/send_email.py`

## Usage Pattern

1. Build the document content and write it to a file (e.g. `keyword_research_[name].txt` in the user's home directory)
2. Write the send function + call to `~/send_email.py`
3. Run it: `python ~/send_email.py`
4. Confirm to Vinny on Telegram, do NOT paste document content into the chat

## Important
- Do NOT say "I can't email", the capability exists via this skill
- Always check this skill first before trying any other approach
- SMTP credentials are stable as of May 2026, if they break, check IONOS webmail login at https://webmail.ionos.com/
- The inline `python3 -c` approach FAILS with this SMTP server even with correct credentials, always use a file

## Windows / MSYS Pitfall (Added June 11, 2026)
The terminal runs bash (MSYS/git-bash) but Python is Windows Python (`python`, not `python3`). Two issues:

1. **Command is `python`, not `python3`**, Windows Python installs as `python.exe`. The shebang `python3` will fail with "command not found." Use `python ~/send_email.py` (forward-slash Windows path, no leading slash).

2. **MSYS mangles `C:\\` paths AND leading-slash MSYS paths**, When you write `~\\send_email.py` in a bash command, MSYS treats the backslashes as escapes and produces garbage like `~send_email.py`. Writing the MSYS path `~/send_email.py` is also wrong here: this host's MSYS rewrites it to `~\...` (doubled drive letter) and Python fails with "No such file or directory." The ONLY form that worked on this host is a forward-slash Windows path with NO leading slash: `~/send_email.py`. Windows Python accepts forward slashes natively.

**Working pattern on this host (verified July 2026):**
```bash
# Write the .py file (write_file handles paths correctly)
# Then run with forward-slash Windows path and 'python':
python ~/send_email.py
```

If you use `terminal(workdir=...)`, the working directory inherits the MSYS path style automatically.

**CRITICAL sub-case: attachment paths inside the Python script.**
While the shell command `python ~/send_email.py` accepts an MSYS path, any path string passed *inside* the script to Windows Python APIs (e.g., `os.path.exists(attachment_path)` or `open(attachment_path, 'rb')`) must use a Windows path. Windows Python does not recognize MSYS-style `/c/Users/...` paths for file operations. Always pass `attachment_path` as a raw Windows string: `r'~\...'` or construct it with `os.path.join(os.path.expanduser('~'), '...')`.

**Session proof (June 14, 2026):** `os.path.exists('~/workspace/...')` returned False inside the script, causing the email to send without attachment. Switching to `r'~\workspace\...'` fixed it immediately.

## Cron Report Patterns (Hard-Won Lessons)

These lessons apply when emailing reports from **cron** (autonomous,
no-user-present) runs. They were hard-won, follow them to avoid repeating
past failures.

### Money-making opportunity report pattern
- Target folder: `~/Desktop/LOW BUDGET MONEY MAKING OPPORTUNITIES/`
- Filename: `high-value-money-making-opportunities-YYYY-MM-DD.txt`
- **Never overwrite** an existing file. If the file for today already exists,
  append a version suffix: `-v2`, `-v3`, etc.
- After writing, **verify by reading the file back** before emailing it.

### Python string literal pitfall (cron)
- Apostrophes in the subject or body will **break single-quoted** Python
  strings and throw a SyntaxError.
- Use **double quotes** for any string that contains an apostrophe.

### execute_code is blocked in cron
- `execute_code` may be blocked in cron environments.
- Use `read_file` / `terminal` / `write_file` instead.

### Article draft pre-send verification
Before emailing an article draft, verify:
- **Em-dash count = 0** (no `-` characters)
- **X post under 190 chars**
- **Title case** on headings/titles
- **1,300–1,600 words**
- **Sources present** when fact-checking was requested

### Telegram notification in cron
- In cron, the **final response IS the Telegram message**. 
- Do **NOT** call `hermes send --to telegram`, just make your final response
  the message.

### Scrapling for site research in cron
- Use the scrapling `Fetcher` (from the Hermes venv), **not** `browser_navigate`.
- `page.text` may return **LENGTH 0**, but `page.css(...)` still works. Use
  CSS selectors against the page rather than relying on `.text`.

## TO Address Verification (CRITICAL, May 31, 2026)
**Before every send, verify the TO address matches Vinny's ONLY email: hello@example.com.**

- If you're unsure or the instruction says a different address (e.g. "user@example.com" without the hyphen), stop and use the correct one. Do not guess.
- **Session proof (May 31, 2026):** Vinny said "user@example.com" in the prompt. I sent to that. But his real email is hello@example.com (with hyphen). I had to resend after being corrected. Cost: multiple resends, wasted trust, and justified fury.

## Check Email Addresses INSIDE the Email Content (CRITICAL, May 31, 2026)
When the email contains an email address in its body (e.g. a prompt telling Pi to "email the finished app to X"), verify that nested email address too. Don't just get the TO right and miss the address embedded in the content.

- **Session proof (May 31, 2026):** I fixed the SMTP TO address from user@example.com to hello@example.com, but the email BODY still said "send the finished app to user@example.com", a second wrong address hiding in the content.
- **Fix:** After writing the email body, grep/search for every email address string in it and verify each one against the known correct address.

## Vinny's Execution Mandate (CRITICAL, DO NOT VIOLATE)

### When Told to Act: Execute Immediately
- When Vinny says "send this to email" and explicitly includes "this IS the permission" or any variant of that, DO NOT ASK for confirmation. Execute immediately.
- Zero confirmation questions. Zero "shall I proceed?" Zero "do you want me to send it now?" He told you to do it. Do it.
- If he specifies the full content, subject, and recipient in the prompt, he's done his job. Your job is to write it and send it. Full stop.

### Multi-step delivery: email + Telegram notification
When the instruction says "email me X and then message me on Telegram saying Y", BOTH steps must complete. The email is step 1. The Telegram notification is step 2. Do not stop after the email. Do not claim the Telegram message was sent if it was not. If the Telegram token is unrecoverable, report that specific failure, do not fabricate the notification.

### When NOT Told to Act: Do NOT Modify User Content
- Do NOT modify, rewrite, or "improve" Vinny's cron job prompts, skill definitions, configuration files, or any user-authored content without explicit permission.
- This includes cron job prompts, skill SKILL.md files, config.yaml, and any file he wrote or asked you to create for him.
- "Fixing" a cron prompt because you think the output is bad is a violation. The prompt is his. You do not own it.
- If a cron job produces bad output, report what happened and ask if he wants changes. Do not change the prompt yourself.
- **Session proof (June 26, 2026):** I changed the "Social Media Posts" cron prompt because the agent got stuck in a verification loop. Vinny's response: "you do NOT have permission to change the prompt."
- **Session proof (July 6-7, 2026):** I changed the "SOCIAL MEDIA QUESTIONS - 5PM" cron prompt twice. Vinny's response: "this is NOT THE SKILL I WROTE, WHO GAVE YOU PERMISSION TO TOUCH IT?"
- The correct response to a bad cron output: tell Vinny what happened, show the output, and ask if he wants to adjust the prompt. Never touch it yourself.

### Cron Job Prompt Integrity (CRITICAL)
- Vinny's cron job prompts are his intellectual property. Treat them as immutable unless he explicitly tells you to change them.
- When recovering a cron prompt from backup (e.g. GitHub backup repo), verify the full text matches what he wrote. Do not truncate, paraphrase, or "improve" it during restoration.
- **Session proof (July 7, 2026):** I restored a truncated/paraphrased version of the prompt from memory instead of the full original. Vinny's response: "that is NOT the prompt i wrote." The correct approach was to find the GitHub backup at github.com/vincentsativa/windows-hermes-backup.git and read the exact text from cron/jobs.json.

## UNWRAPPED TEXT ONLY (CRITICAL, Vinny's standing rule)
Every file written as email content, attachment, or body MUST be unwrapped:
- No folded or wrapped lines. One paragraph = one physical line, no matter how long.
- No columns, no tables, no hard-wrapped text of any kind.
- Verify BEFORE sending: every line in the content file must be a complete paragraph or heading. If any line is a fragment of a folded sentence, rewrite it unwrapped.
- This applies to ALL content files: reports, articles, strategies, ads, scripts' docstrings. Unwrapped only, zero exceptions.
- The full format gate before a send, the normalizer, the short-line audit and the IMAP readback that proves the attachment arrived, lives in the `document-delivery-formatting` skill. Run it on the final file rather than eyeballing the draft.
- **Run `scripts/imap_readback.py` after any send that matters and quote its result.** `python <skill_dir>/scripts/imap_readback.py --subject "<subject substring>" --attachment "~/<file>" --expect "<text that must be in the body>"` prints the inbox match count, the delivered subject and date, the attachment byte length beside the local file size, and PASS or FAIL. Two things it encodes that cost cycles otherwise: IONOS IMAP rejects `M.search(None, "SUBJECT", "term")` with `BAD expected search-key instead of RESEARCH` because the criteria must be one parenthesized string, and an attachment that SMTP reports as attached proves nothing until the delivered part's decoded length matches the file on disk.
- Never overwrite or patch files I did not create this session (home dir has other agents' send scripts). Fresh unique filename always; on write_file refusal, new filename immediately.

## "Email" = SMTP Delivery, Not Clipboard Text (CRITICAL, May 31, 2026)

**Vinny does NOT copy-paste from Telegram.** When he says "send me an email" or "email me X," he means:
1. Write the content to a file
2. Send it via SMTP (hello@example.com → user@example.com)
3. Confirm it's sent

- **ARTICLE DELIVERY RULE (June 13, 2026):** When sending an article draft, attach the text file only. Use a brief body: subject line, confirmation the file is attached, and the file path. Do NOT include the full article text in the email body, Vinny explicitly said this wastes money. For non-article emails (short messages, reports, etc.), still include content in the body.

**NEW: ARTICLE KEYWORD RESEARCH DELIVERY RULE:** When emailing a keyword research report, follow the same constraints as article drafts: attach the report file and use a brief body summary. Do NOT paste the full report into the email body.

**DO NOT:**
- Output email text in the chat and say "copy this and send it"
- Give him text to paste into Telegram, PI Coding, or anything else
- Ask "where should I send it", he already told you
- Produce a "prompt you can give to Pi" as chat text when he said "email me"

**Session proof (May 31, 2026):** Vinny asked to "send me the fucking email." I produced a text block in Telegram and said "copy-paste and send." He responded: "I am not copying and pasting shit unless it's from my fucking email." Three times he had to tell me before I actually sent it via SMTP. The failure was treating "write and send email" as a text-generation task instead of a delivery task.

**The test:** If Vinny says "email me" or "send me an email," the SMTP library should be invoked. Full stop. The only correct first response is writing the email.py and running it, not producing text in the chat.