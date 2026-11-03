# MailerLite Integration Reference (PhantomByte Funnels)

## Account Details
- **Email:** [REDACTED_EMAIL]
- **Plan:** Free tier (500 subs / 12,000 emails/mo)
- **Login:** https://dashboard.mailerlite.com
- **Account ID:** 2252055

## Group IDs & Funnel Mapping

| Funnel Slug | Group Name | Group ID |
|---|---|---|
| playbook | playbook | 186325633265042550 |
| flowchart | flowchart | 186325706890806816 |
| challenge | challenge | 186325707504224152 |
| audit | audit | 186325707984471239 |
| articles newsletter subscribers | Articles Newsletter Subscribers | 184146703705704286 |
| contact | (maps to articles group) | 184146703705704286 |

## Cloud Run Proxy Architecture

- **Live URL:** `https://mailerlite-proxy-1091380733401.us-east1.run.app`
- **Endpoint:** `POST /api/subscribe`, `GET /health`
- **Source:** `phantom-byte-funnels/mailerlite-proxy/main.py` (Windows workspace)
- **Deploy:** `phantom-byte-funnels/mailerlite-proxy/deploy.sh`
- **Project:** `gen-lang-client-0237860564`, Region: `us-east1`

**CRITICAL: Do NOT touch Cloud Run resources. The proxy is live and working.**

### Proxy Design
- Maps form `data-funnel` attribute slugs to group IDs server-side
- Accepts: `{ email, name, group, redirect, ...optional_fields }`
- Rate limits: 5 req/min per IP (in-memory counter)
- Returns: `{ success: true, redirect_url: "..." }`
- API key stored as Cloud Run env var, rotated May 2026

## Working Automation Creation Pattern

See `mailerlite_setup_v4.py` in the Windows workspace at:
`C:\Users\<user>\workspace\mailerlite_setup_v4.py`

This script is the **canonical working reference**, it successfully creates and enables automations via the MailerLite API. Key learnings from it:

1. **Create shell with `enabled: False`** first
2. **Add trigger** via `POST /automations/{id}/triggers` with `subscriber_joins_group` type
3. **Create steps** via `POST /automations/{id}/steps` with minimal payload (type, parent_id)
4. **Update step content** via `PUT /automations/{id}/steps/{step_id}` with a `data` wrapper
5. **Enable** via `PUT /automations/{id}` with `enabled: True`, this works when the automation has at least one step

### Email Step PUT Payload Pattern (confirmed working)
```python
put_body = {
    "data": {
        "type": "email",
        "parent_id": None,
        "name": sdef["name"],
        "subject": sdef["subject"],
        "from": FROM_EMAIL,
        "from_name": FROM_NAME,
        "reply_to": FROM_EMAIL,
        "language_id": 4,  # English
        "track_opens": True,
        "email": {
            "name": sdef["name"],
            "type": "builder",
            "from": FROM_EMAIL,
            "from_name": FROM_NAME,
            "reply_to": FROM_EMAIL,
            "subject": sdef["subject"],
            "language_id": 4,
            "track_opens": True,
            "content": {"html": sdef["html"], "plain": sdef["plain"]},
        },
    }
}
api("PUT", f"/automations/{aid}/steps/{sid}", put_body)
```

### API Key Location
The full API key is in `mailerlite_setup_v4.py` at line 9. The `...mHmw` suffix shown in some logs is not the full key, read the actual file to get it.

## Automations (as of May 16, 2026)

| Name | Trigger Group | Status |
|---|---|---|
| [Funnel] Playbook Delivery | playbook | 🟢 Enabled |
| [Funnel] Flowchart Delivery | flowchart | 🟢 Enabled |
| [Funnel] 5-Day Challenge | challenge | 🟢 Enabled |
| [Funnel] Audit Confirmation | audit | 🟢 Enabled |

All 4 automations were created and enabled via `mailerlite_setup_v4.py`.

## Pending: Welcome Email for ALL Subscribers

**Task:** Create a new automation triggered on ALL groups that sends The Sovereign AI Stack Blueprint PDF welcome email to every new subscriber regardless of funnel.

- **PDF URL:** `https://vincentsativa.com/assets/The-Sovereign-AI-Stack-Blueprint.pdf`
- **Automation type:** 1 immediate email (delay: 0)
- **Trigger groups:** All 5 groups (playbook, flowchart, challenge, audit, articles newsletter subscribers)
- **Pattern:** Same as existing lead magnet automations (playbook, flowchart)
- **Email HTML:** Dark card style, purple CTA button. Provided to user, ready to paste into MailerLite dashboard.

## Dashboard Login Issue
MailerLite login page at `accounts.mailerlite.com` uses Cloudflare Turnstile bot detection. All automated approaches (Playwright headless, StealthyFetcher, DynamicFetcher) fail consistently. Do NOT spend time trying to bypass it. For manual dashboard work, report to user.

## Useful curl Commands

```bash
# List groups
curl -s -H "Authorization: Bearer <KEY>" "https://connect.mailerlite.com/api/groups"

# List automations
curl -s -H "Authorization: Bearer <KEY>" "https://connect.mailerlite.com/api/automations"

# Get automation detail
curl -s -H "Authorization: Bearer <KEY>" "https://connect.mailerlite.com/api/automations/<ID>"

# List subscribers
curl -s -H "Authorization: Bearer <KEY>" "https://connect.mailerlite.com/api/subscribers"

# Test proxy
curl -s -X POST "https://mailerlite-proxy-1091380733401.us-east1.run.app/api/subscribe" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test","group":"playbook","redirect":"ty-01.html"}'
```

## Security History
1. Original problem: MailerLite API key hardcoded in `js/main.js` on public GitHub Pages
2. Fix: Created Cloud Run proxy keeping key server-side
3. Key rotated May 2026 after proxy deployment