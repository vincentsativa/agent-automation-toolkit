# Dataset-to-Outlines Workflow (Multi-Outline Generation from Local Data)

When the task provides a local data directory (typically
`C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES`) and asks for multiple
article outlines grounded in that data, follow this workflow.

This is distinct from the barrier-article outline workflow in the pinned
`phantombyte-content-writing` skill. That skill covers outlines from a
single problem/brief. This workflow covers batch outline generation from
a dataset of news/research files.

## Trigger Conditions
- "Research phantom-byte.com's existing content, then generate [N] article
  outlines from a local dataset"
- "Generate outlines from today's data files"
- Any task that says: read data files, generate outlines, deliver as .txt
  files via email

## Phase 1: Research the Brand

1. Navigate to articles.phantom-byte.com and review the full article catalog.
2. Note the category distribution (AI Infrastructure, AI Engineering, AI
   Security, AI Industry, AI Policy, etc.) and the article count per category.
3. Read at least one full published article to calibrate voice and structure.
   Use browser_console to extract article text if the snapshot is truncated.
4. Load the `phantom-byte-writing-style` skill for voice rules.
5. Identify coverage gaps: which categories are thin relative to the day's
   news themes. The data files (especially blogwatcher) often flag unwritten
   themes explicitly.

## Phase 2: Read All Source Data Files

1. Read every file in the specified data directory. Filenames change over
   time, so read everything in the directory rather than assuming specific
   names. Common patterns as of July 2026:
   - `20-AI-News-Stories-[date].md` (compiled news with themes and patterns)
   - `GLM AI NEWS REPORT.md` (headlines with themes and patterns, was
     previously `30 AI NEWS STORIES GROK.md`)
   - `blogwatcher-dump-[date].txt` (28 headlines with unwritten themes)
   - `ironpulse-[date].txt` (20 ranked AI stories)
   - `tensorfeed_report_[date].txt` (25+ items with themes and article
     recommendations)
   If a file appears with a different name, read it anyway. The directory
   is the source of truth, not this list.
2. Extract key themes, facts, and story angles from each file.
3. Do NOT fabricate claims or use unverified stats. Every fact in every
   outline must be traceable to a source data file.

## Phase 3: Generate Outlines with Distribution Requirements

1. Produce the requested number of outlines (typically 3).
2. Distribution: 1-2 outlines must be engineering/infrastructure-focused
   (reflecting PhantomByte's authority angle: "you can't do anything in AI
   without solid engineering"). The remaining outline(s) must cover a
   different angle within AI (industry news, tools, use cases, policy,
   lessons learned).
3. Each outline must match the PhantomByte voice identified in Phase 1.
4. Each outline must be written to teach: accessible to newbies while
   offering depth for professionals.

## Required Outline Format

Each outline .txt file should include these sections. The exact section
headers can vary based on the task spec, but the core elements must be
present: traceability, voice notes, and the full section-by-section
outline with hooks, teaching sections, checklists, and a closing
provocation.

A proven format (used July 17, 2026):

```
================================================================================
ARTICLE OUTLINE #[N] — [CATEGORY]
================================================================================

TITLE: [title]
CATEGORY: [category]
ESTIMATED LENGTH: [word count range]
READING LEVEL: [level]
TARGET AUDIENCE: [who this is for]

--------------------------------------------------------------------------------
SOURCE DATA TRACEABILITY
--------------------------------------------------------------------------------
[List every source data file used, with specific items/stories referenced.
 This section is non-negotiable. Every fact in the outline must be
 traceable to a source file listed here. Include the specific numbers,
 statistics, and quotes you plan to use, with their source attribution.]

--------------------------------------------------------------------------------
PHANTOMBYTE VOICE NOTES
--------------------------------------------------------------------------------
[Reminders for the writer: the voice elements this outline should use.
 Short punchy paragraphs, declarative sentences, // SECTION HEADER format,
 "What to Do Today" checklist, "The Uncomfortable Question" closer,
 cross-references to prior PhantomByte notes, core thesis connection.]

--------------------------------------------------------------------------------
OUTLINE
================================================================================

OPENING HOOK (2-3 paragraphs)
[The opening paragraphs, written in PhantomByte voice. Lead with a
 concrete number or fact, not a question. State the thesis bluntly.
 Cross-reference a prior PhantomByte Note for continuity.]

// [SECTION HEADER]
[Full section-by-section breakdown with content notes under each
 heading. Use // prefix for section headers to match published article
 style. Include the specific facts and numbers from the source data
 that each section will use. Each section should teach something
 concrete.]

// WHAT TO DO TODAY
[Checklist format. Each item is a concrete action the reader can take.]

// THE UNCOMFORTABLE QUESTION
[Closing provocation. End with a direct challenge to the reader,
 phrased as a blunt question or statement.]
```

### Key Format Rules

- Use `// SECTION HEADER` format for section headers within the
  outline body, matching the published article style on
  articles.phantom-byte.com. Not `## [SECTION NUMBER]` which is the
  tutorial format.
- Each outline file should be self-contained: a reader should
  understand the article's thesis, sources, structure, and voice from
  the file alone.
- Include the specific numbers and facts from the source data in the
  outline body, not just "use the stat about X." The writer should be
  able to produce the article from the outline without re-reading the
  data files.
- The source data traceability section should list the actual file
  names and the specific stories/items referenced from each.

## Phase 4: Save and Report File Paths

1. Save each outline as a separate .txt file in the data directory (or a
   specified output directory).
2. Report the FULL Windows file path for each file (e.g.,
   `C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES\outline1-[slug].txt`).
3. Do NOT report just the filename. The user needs the full path.

## Phase 5: Email Delivery

1. Send ONE email to hello@phantom-byte.com with ALL outline files attached.
2. Do NOT send separate emails for each file.
3. Email body: brief summary of each outline (title, source basis, category),
   plus the full Windows file paths.
4. Subject format: "Three Article Outlines from Today's Data Files (July 16,
   2026)" or similar date-stamped format.
5. Use the email-sender skill with the multi-attachment pattern (pass a
   list of file paths to a send_email_with_attachments function).

## Multi-Attachment Email Pattern

The email-sender skill's SKILL.md shows single-attachment examples. For
multiple files in one email, use this pattern:

```python
import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email_with_attachments(to, subject, body, attachment_paths):
    msg = MIMEMultipart()
    msg['From'] = 'hello@phantom-byte.com'
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    for path in attachment_paths:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(path)
                part.add_header('Content-Disposition',
                    f'attachment; filename={filename}')
                msg.attach(part)
    server = smtplib.SMTP('smtp.ionos.com', 587, timeout=60)
    server.set_debuglevel(1)
    server.starttls()
    server.login('hello@phantom-byte.com', 'VJBvjbhydro1202$$')
    server.send_message(msg)
    server.quit()
    return True
```

Always write the script to a file first (not inline `python3 -c`), and
always include `set_debuglevel(1)` and a confirmation print after
`send_message` to verify the send succeeded.

## Pitfalls

- Do NOT skip the phantom-byte.com research step. Outlines must fit the
  existing voice, not a generic AI-blog tone.
- Do NOT submit outlines that aren't traceable back to the data files.
  Accuracy is non-negotiable for SEO/GEO reputation.
- Do NOT save outlines without proper Windows file path reporting.
- Do NOT send separate emails per outline. All files go in one email.
- Do NOT modify or reinterpret the workflow on your own. Execute exactly
  as specified.
- The `phantombyte-content-writing` skill is pinned and cannot be patched
  by the agent. If it needs updates, ask the user to unpin it first.
- The `// SECTION HEADER` format used in PhantomByte published articles
  (with the `// ` prefix) differs from the `## [SECTION NUMBER]` format
  used in tutorials. Article outlines should use `// SECTION HEADER` to
  match the published article style, not the tutorial style. Session
  proof (July 17, 2026): this session produced outlines using `//` headers
  and they matched the live site's published article structure.
- When reading articles.phantom-byte.com for brand research, the full
  snapshot may be truncated. The full snapshot is saved to a file under
  `~/.hermes/cache/web/browser-snapshot-*.txt`. Use read_file on that
  path to get the complete article text if you need more of the article
  than the initial snapshot returns.
- Browser snapshot truncation also means you may need to scroll the page
  or click through to read older articles in the archive. Use the LOAD
  MORE button to expand the archive list before selecting articles to
  read for voice calibration.
- The email-sender skill SKILL.md has a `set_debuglevel(1)` requirement
  for debugging sends, but this also produces very verbose output on
  successful sends. The SMTP debug output is normal and not an error.
  Look for "235 Authentication succeeded" and the final "250 Requested
  mail action okay" reply codes to confirm success.