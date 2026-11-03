# Welcome Email, Sovereign AI Stack Blueprint PDF

**Created:** May 16, 2026
**Use:** Triggered on all new subscriber signups across all groups

---

## HTML (ready to paste into MailerLite)

```html
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #1a1a2e; background: #fafafa;">

<div style="background: #0d0d1a; padding: 30px; border-radius: 12px; color: #e0e0ff;">
  <p style="margin-top: 0;">Hey {$name},</p>

  <p>Welcome aboard. Here's your copy of <strong>The Sovereign AI Stack Blueprint</strong>.</p>

  <p>This blueprint lays out the full architecture for running your own AI agent stack. Model selection, tool routing, deployment patterns, cost control. Everything you need to keep your agents off third-party leashes.</p>

  <p><a href="https://vincentsativa.com/assets/The-Sovereign-AI-Stack-Blueprint.pdf" style="display: inline-block; padding: 14px 28px; background: #9D4EDD; color: #fff; text-decoration: none; border-radius: 8px; font-weight: bold;">Download the Blueprint →</a></p>

  <p>Questions? Just reply to this email.</p>

  <p style="margin-top: 30px; color: #888; font-size: 13px;">- Vinny<br>PhantomByte</p>
</div>

</body>
</html>
```

## Plain Text

```
Hey {$name},

Welcome aboard. Here's your copy of The Sovereign AI Stack Blueprint.

This blueprint lays out the full architecture for running your own AI agent stack. Model selection, tool routing, deployment patterns, cost control. Everything you need to keep your agents off third-party leashes.

Download the Blueprint →
https://vincentsativa.com/assets/The-Sovereign-AI-Stack-Blueprint.pdf

Questions? Just reply to this email.

- Vinny
PhantomByte
```

## MailerLite Automation Setup

**Trigger:** Subscriber joins group (any/all groups)
**Groups to wire:**
- Articles Newsletter: `184146703705704286`
- Playbook: `186325633265042550`
- Flowchart: `186325706890806816`
- Challenge: `186325707504224152`
- Audit: `186325707984471239`

**Automation flow:** Subscriber joins group → Delay 0 (immediate) → Send Email (above HTML)

**Notes:**
- The PDF is 14MB, too large for MailerLite attachment limit (10MB). Use hosted download link.
- PDF hosted at: `https://vincentsativa.com/assets/The-Sovereign-AI-Stack-Blueprint.pdf`
- This fires for ALL new subscribers regardless of funnel. Existing funnel sequences (5-day challenge, etc.) continue separately.
- Do NOT modify existing 4 automations when adding this one.

**API key location:** `C:\Users\<user>\workspace\mailerlite_setup_v4.py`, read the file for the full key (eyJ0eX... is truncated in scripts).

## Design Specs
- Background: `#0d0d1a`
- Text: `#e0e0ff`
- CTA button: `#9D4EDD` background, white text, 8px border-radius, 14px/28px padding
- From: `hello@phantom-byte.com`, name: `Vinny Barreca, PhantomByte`
- Track opens: true
- Language: English (language_id: 4 in API)