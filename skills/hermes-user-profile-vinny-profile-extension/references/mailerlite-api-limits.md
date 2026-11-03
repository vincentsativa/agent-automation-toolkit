# MailerLite API, Known Limitations (discovered May 2026)

## Authentication
- **API Key endpoint:** https://dashboard.mailerlite.com/integrations/api
- **Base URL:** https://connect.mailerlite.com/api
- **Auth header:** `Authorization: Bearer <key>`
- **Old key (dead):** eyJ0eX...K6mO, rotated after Cloud Run proxy deployment
- **Current key:** stored in ~/.hermes/credentials.md, also in Cloud Run env var for proxy

## Account Info
- **Account ID:** 2252055
- **Email:** [REDACTED_EMAIL]
- **Password (dashboard):** Gpen420$$$
- **Plan:** Free (500 subs / 12,000 emails/mo)
- **Dashboard login:** https://dashboard.mailerlite.com (guarded by Cloudflare Turnstile)

## API Can Do
- ✅ Create groups: `POST /groups` with `{"name": "group-name"}`
- ✅ Create automation shells: `POST /automations` with `{"name": "...", "enabled": false}`
- ✅ Add triggers: `POST /automations/{id}/triggers` with `{"type": "subscriber_joins_group", "group_ids": [...]}`
- ✅ Create steps with parent chain intact: `POST /automations/{id}/steps` with correct `parent_id`
- ✅ Get subscriber by email: `GET /subscribers/{url-encoded-email}`
- ✅ Create/upsert subscriber: `POST /subscribers`
- ✅ Delete automations: `DELETE /automations/{id}`
- ✅ List everything: automations, groups, subscribers, webhooks, campaigns

## API Cannot Do (for newer/post-2022 accounts)
- ❌ **Cannot set email content** (HTML/plain), PUT on email steps creates the step but ignores content. Email ID is created but body stays as MailerLite default placeholder "Edit this email".
- ❌ **Cannot enable automations**, PUT with `{"enabled": true}` accepts the request but returns `enabled: false`. API returns `complete_workflow: false` in trigger_data and refuses to toggle it.
- ❌ **Cannot add delay step properties** (value/unit/name), same PUT issue. Delay steps created via POST are fine, but any subsequent PUT on delay steps fails validation requiring fields that weren't needed at creation.
- ❌ **Cannot reorder steps after creation**, PUT on any step resets `parent_id` to null regardless of what you pass, breaking the parent chain.
- ❌ **Cannot populate email content in a single POST**, POST only accepts type/name/subject/from for email steps, no email content body.
- ❌ **Dashboard API v2** (dashboard.mailerlite.com/api/v2/) returns 403 from external, requires session cookies, not API key. Browser automation of the dashboard is blocked by Cloudflare Turnstile.

## Workarounds
- For simple automations (1 email, no delay): create shell + trigger via API, then user enables + adds email content in dashboard (~30s each)
- For multi-step automations (challenge with delays): user must build in dashboard from scratch, API cannot construct one correctly end-to-end
- The "Playbook Delivery" and "Flowchart Delivery" automations were created by May 1 Pi run and are `enabled: true` with some content (the API was able to set more on older accounts or via a different flow)

## Groups (active)
| Name | ID |
|------|-----|
| Articles Newsletter Subscribers | 184146703705704286 |
| playbook | 186325633265042550 |
| flowchart | 186325706890806816 |
| challenge | 186325707504224152 |
| audit | 186325707984471239 |

## Automations (active as of May 3, 2026)
| Name | ID | Status | Steps |
|------|----|--------|-------|
| [Funnel] Playbook Delivery | 186327116107744313 | 🟢 Enabled | 1 email |
| [Funnel] Flowchart Delivery | 186327118693533308 | 🟢 Enabled | 1 email |
| [Funnel] Audit Confirmation | 186327130362086812 | 🟢 Enabled | 1 email |

## Cloud Run Proxy
- **URL:** https://mailerlite-proxy-1091380733401.us-east1.run.app
- **Endpoint:** POST /api/subscribe
- **Health:** GET /health
- **Source:** /mnt/c/Users/<user>/workspace/phantom-byte-funnels/mailerlite-proxy/
- **Maps group slugs to IDs server-side** (playbook → 186325633265042550, etc.)
- **Rate limiting:** 5 req/min per IP
- **Old proxy (dead):** mailerlite-proxy-mvcy5omgra-uc.a.run.app, redirects to static thanks page
