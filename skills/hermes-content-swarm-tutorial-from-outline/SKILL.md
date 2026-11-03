---
name: tutorial-from-outline
description: Write a complete, paid-quality technical tutorial from a user-provided outline file, then deliver it by email as a file attachment and confirm via Telegram. Use whenever the user says "write a tutorial using the uploaded outline," "write me a tutorial from this file," or any variant that points to a local outline/spec file.
tags: [tutorial, outline, email-delivery, paid-product, writing]
toolsets: [file, terminal, web, browser]
---

# Tutorial From Outline (Write + Email + Notify)

## Trigger

The user points to a local outline/spec file and asks for a complete tutorial based on it. Examples: "Write me a high quality tutorial using the uploaded outline," "write a tutorial from this file and email it." The outline IS the complete input. Do not wait for or invent other inputs.

## CRITICAL BEHAVIORAL RULE (read first)

**Instructions are NOT optional.** When the user gives a direct instruction with a file, execute it. Do not:

- Hunt for companion files the user never mentioned (e.g. "keyword research" that wasn't provided). The outline is the spec. Use it.
- Ask clarifying questions that imply the user failed to give you something. They gave you the outline. That is enough.
- Start narrating or asking "should I proceed?" Execute.
- Rewrite, "improve," or second-guess the outline structure. Cover every section the outline lists, in order.

If a referenced file genuinely does not exist AND the user named it, that is the only case for a single direct question. An outline with no separate research file means: write from the outline. Period.

## Mandatory Pre-Step: Load writing-style

Before writing ANY tutorial text, load the `writing-style` skill (`skill_view(name='writing-style')`). Apply its rules to the tutorial: no em dashes, no dashes as commas, proper punctuation, bold mixed-case short headers, hyphen bullets, second-person "you," concrete numbers, short paragraphs, opinionated framing where it adds value. These are hard rules, not guidelines.

## Steps

### 1. Read the outline file fully

Use `read_file` on the exact path the user gave. Read all lines. The outline defines: title, audience, modules/sections, what the buyer walks away with, bonus files, and the value thesis. Your tutorial must map 1:1 to these.

### 2. Write the complete tutorial

Write to a `.txt` file in the same folder as the outline (or the path the user specifies). Filename: descriptive, e.g. `Building_Model_Agnostic_Agent_Tutorial.txt`.

Quality bar (this is a $100-value product, not a blog post):

- Cover EVERY section in the outline, in order. Do not skip modules or bonus files.
- Include runnable code where the outline says "Code:" or "Code demo." Real, complete functions/classes, not snippets. Define dataclasses, interfaces, adapters, tests, router, CI yaml, docker-compose.
- Lead sections with concrete specifics (numbers, names, versions). No generic openings.
- Keep it self-contained: a buyer should be able to build from it without other docs.
- Word count target for a paid technical tutorial: 6,000 to 8,000 words when the outline is this detailed.
- Title Case headers in bold. No ALL CAPS headers. No em dashes anywhere.

### 3. Save and verify the file

After `write_file`, optionally `read_file` the head to confirm it wrote. Report the saved path.

### 4. Email it as an attachment (IONOS SMTP)

Load the `email-sender` skill for the exact SMTP pattern. Key points (verified on this host):

- TO address is ALWAYS `hello@example.com`. Never guess a different address.
- Write the sender script to `~\send_email.py` (use `write_file`, not inline `python3 -c`).
- Body is BRIEF: subject, "file attached," file path. Do NOT paste the full tutorial into the body (wastes money).
- Attachment path INSIDE the script must be a raw Windows string: `r'~\OneDrive\Desktop\...'`. MSYS `/c/...` paths fail for file reads inside Python.
- Run with: `python ~/send_email.py` (forward-slash Windows path, no leading slash, command is `python` not `python3`).
- On success the command returns no output and exit_code 0.

### 5. Notify the user

- If a Telegram tool/gateway is available in the session, send a short confirmation there after the email succeeds.
- If NO Telegram tool exists in the current toolset, state that plainly in chat and confirm the email was delivered. Do NOT fake a Telegram send or claim a notification was delivered when the tool isn't present.

## Pitfalls (from real session failures)

- **Phantom-file clarification.** Searching the filesystem for a "keyword research" file the user never provided, then asking where it was, wasted turns and provoked rage. The outline was the only input needed. Fix: trust the outline.
- **Contradicting the instruction.** Asking "should I skip the keyword research?" after being told to use the outline is defiance dressed as helpfulness. Fix: execute the instruction as given.
- **Em dashes.** The writing-style skill bans them. The outline user is hostile to them. Grep your output mentally for "—" and replace with commas, periods, or parentheses.
- **Email body too long.** Pasting the tutorial into the email body wastes SMTP/spend. Attach the file, keep body to 3 lines.
- **Wrong path style in script.** `os.path.exists('/c/Users/...')` returns False on this host. Use raw Windows paths inside the Python script.
- **Narrating instead of doing.** Don't say "I will now write the tutorial." Write it, email it, report. Minimal chat until delivery confirmed.

## Verification

- Tutorial file exists at the reported path and contains all outline sections.
- Email sent (exit_code 0, no SMTP error).
- User notified on the agreed channel.
