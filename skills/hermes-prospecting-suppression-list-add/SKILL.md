---
name: suppression-list-add
description: Use when Vinny says do not send an email address.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [outreach, suppression, email]
    related_skills: [openleads-prospecting-pipeline]
---

# Add an address to the DO NOT SEND list

## When to Use

Vinny says any of: do not send, don't send, remove, suppress, opt out, stop mailing, or "add this email to the do NOT send list", with an address.

## The file

`~/money_ideas/suppressed_addresses.txt`

That is the only list. `mail_verify.py` (SUPPRESS_FILE) loads it, `outreach.py` drops every matching address and dead domain before send, so one append is the whole job. Do not go hunting for other lists.

## Format

Tab separated, two fields: `address<TAB>reason`. Header lines begin with `#`. Addresses are compared exact and lowercase, and a bare domain in the file kills every address at that domain, so write the full address unless Vinny asks for the domain.

## Do it in one call

```bash
cd ~/money_ideas && grep -qiF -- "$ADDR" suppressed_addresses.txt || printf '%s\tDO NOT SEND\n' "$ADDR" >> suppressed_addresses.txt
```

The grep guard keeps a repeat order from writing the line twice. Use the reason Vinny gave when he gave one (`OPT OUT`, `requested stop`); default to `DO NOT SEND`.

## Then verify, same turn

```bash
grep -F -- "$ADDR" ~/money_ideas/suppressed_addresses.txt
```

Report the line in one or two lines. Done. No commentary.

## What went wrong once, do not repeat it

An order to add one address took 20 minutes and two attempts because the agent searched the whole home tree for a list it had not found yet. The file is named in this skill. Read it, append, verify: under 30 seconds. If the address is already there, say so in one line and stop.

## Rules that still apply

- Never write to memory for this; the file is the record.
- Do not edit skills or crons around it. This file is the only artifact touched.
- If a second list is ever introduced, it gets named here, not rediscovered.
