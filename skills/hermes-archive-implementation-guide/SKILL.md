---
name: implementation-guide
description: Write paid DIY implementation guides.
trigger: "Vinny says 'write the implementation guide' or 'write the DIY guide' for a paid product"
---

# Implementation Guide Writing Skill

## Core Principle

A paid implementation guide is not a lead magnet. It does not hold back. It teaches the reader to succeed without you.

The business model is simple:
- Free diagnostic tool tells them what is wrong
- Paid guide ($29.99 or similar) tells them how to fix it, fully
- Done-for-you service ($500 or similar) is for those who do not want to do the work

The guide must deliver on its promise. If the reader finishes unable to do it themselves, the product is broken and the refund is deserved.

## When This Skill Applies vs. tutorial-writing

The `tutorial-writing` skill covers **lead magnets**: free tutorials that teach concepts without giving away the implementation.

This skill covers **implementation guides**: paid tutorials that teach the reader to do it themselves.

Do not confuse them. A lead magnet that reads like an implementation guide is giving away the product. An implementation guide that reads like a lead magnet is wasting the customer's money.

## The Procedure

### Step 1: Identify the Diagnostic Tool

Every implementation guide has a free diagnostic that feeds it. Identify:
- Where the diagnostic lives (URL)
- What findings it produces
- The severity states or categories it uses

The reader runs the diagnostic first, then uses the guide to fix each finding. The guide must map every diagnostic finding to a fix section.

### Step 2: Structure Around the Diagnostic Findings

Do not structure around the technology. Structure around the diagnostic experience:

```
CHECKER RESULT → FIND THE CORRESPONDING SECTION → FOLLOW THE STEPS → VERIFY → MOVE TO THE NEXT RECORD
```

### Step 3: Research Current Provider Instructions

Do not invent provider values. Do not use outdated instructions. For every provider covered:

1. Pull current official documentation from the provider's docs site
2. Verify the UI paths and record formats are current
3. Note any quirks (e.g., Microsoft 365 DKIM uses CNAME records with dynamic partition characters)
4. Use the provider's exact values, not generic examples

If a provider's documentation cannot be reached, say so. Do not fabricate.

### Step 4: Write the Preparation Section

Keep this short. The reader needs to identify:
- Their domain
- Their DNS provider
- Their email provider
- Every service that sends mail using their domain

Give them a worksheet or checklist. Then tell them to run the diagnostic and record the findings.

### Step 5: Write Each Fix Section

For each finding, use this format:

```
Finding: [Exact diagnostic finding text]

What you are doing: [One sentence]

Step 1 — [Action]
[Exact steps]

What to enter:
  Record type: [type]
  Name/Host: [exact value]
  Value: [exact value]
  TTL: [value]

Save it: [What to click]
Verify it: [Exact verification step]
If it doesn't work: [Troubleshooting]
```

Do not write theory sections. Do not write "why this matters" essays.

### Step 6: Write the DNS Provider Reference

Create a practical reference section for adding DNS records. Cover at minimum:
- Cloudflare
- GoDaddy
- Namecheap
- Any other provider the user specifies

For each:
- Record type
- Name / Host
- Value / Content
- TTL
- Where to find the DNS editor in their dashboard

Note terminology differences between providers. Do not pretend every dashboard looks the same.

### Step 7: Write the Alignment Section

Alignment is often the hardest concept. Teach it practically:
- Show the Authentication-Results header
- Point out each field (spf=, dkim=, dmarc=, header.from=, smtp.mailfrom=, header.d=)
- Show a passing example
- Show a failing example with explanation
- Explain the fix for each failure mode

### Step 8: Write the Final Verification

Give them a literal checklist:
- MX reviewed
- SPF count correct and within limit
- SPF qualifier intentional
- DKIM record published
- DKIM selector confirmed
- DKIM signing enabled
- DMARC published
- DMARC policy intentional
- DMARC reporting configured if desired
- Real email test passed
- Re-run the checker, all findings pass

### Step 9: Write the Bridge to Done-For-You

End with an honest section for those who tried and do not want to continue:
- Name the service and price
- List exactly what it includes
- Make clear the guide was worth buying even if they never use the service
- No pressure, no guilt

## Format Rules

- No em dashes anywhere. Use hyphens.
- Short paragraphs (1-4 sentences max)
- Step-by-step numbered procedures
- "What to enter" boxes with exact DNS fields
- Verification after every major action
- No theory sections
- No "why this matters" essays
- No general articles about the topic

## Output Format

Deliver as a professional PDF:
- Purple cover matching PhantomByte (#9D4EDD gradient)
- Cover tag: "PhantomByte"
- Title and subtitle
- Page numbers on every page (Page X)
- No text cut off or truncated
- Professional typography (Liberation Serif body, Liberation Sans headings)

Email the PDF to hello@phantom-byte.com and confirm on Telegram.

## Pitfalls

### Writing Theory Instead of Steps
The most common mistake. Every sentence should be actionable. If a sentence explains why something matters instead of what to do, cut it or reduce it to a clause.

### Not Mapping Every Finding to a Fix
The diagnostic is the contract. If the tool can say "SPF Missing" and the guide has no section for fixing a missing SPF record, the guide is incomplete. Enumerate every diagnostic finding before writing.

### Inventing Provider Values
Never tell the reader to use a generic SPF record. The correct value depends on what actually sends mail for their domain. Teach them to find the correct value from their provider. When a provider generates a specific record (like Google Workspace DKIM or Microsoft 365 DKIM CNAMEs), tell them to use the exact value from their provider's dashboard.

### Using Lead-Magnet Style for Paid Implementation
Do not hold back information to force a sale. The reader paid for the guide. Give them the complete guide. The done-for-you service exists for people who do not want to do the work, not for people who could not figure out the guide.

### Forgetting Verification
Every procedure must end with "re-run the PhantomByte checker" or equivalent verification. Without verification, the reader cannot know if the fix worked.

### Dangling Final Page
Check the PDF output. If the last page has only a few lines, adjust the content or add page-break controls to consolidate. Professional formatting matters for a paid product.

### Confusing Implementation Guide with Plan Document
If the user sends a plan or strategy document, do not convert it directly into a PDF and deliver it as the tutorial. A plan describes what to do. An implementation guide tells the reader exactly how to do it, with click paths and verification. These are different deliverables.
