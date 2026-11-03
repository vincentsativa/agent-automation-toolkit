# Contact form with address verification

How the PhantomByte offer-page form proves a submitter's email is real before the
lead is trusted. Stateless by design: no database, survives a container restart.

## Live endpoint

```
POST https://phantom-byte-contact-ionos-1091380733401.us-central1.run.app/api/contact-form
```

Accepts `{ name, email, message, domain, source }`. Sends via IONOS SMTP
(`smtp.ionos.com:587`) to `hello@phantom-byte.com`.

Backend source: `/mnt/c/Users/<user>/phantom-byte-contact-api/server.js`
Repo: `github.com/vincentsativa/phantom-byte-contact-api`

Two endpoints:
- `POST /api/contact-form` accepts the submission and sends the two emails
- `GET /api/verify?token=...` is the confirmation link target

## The flow

1. Validate and length-cap every field. Escape all interpolated values before
they go into the HTML email body; the submitter controls the name, the domain,
the message, and the email, so unescaped output is an injection hole.
2. Sign a token carrying `{ email, name, domain, source, ts }`.
3. Email the owner immediately: subject prefixed `[UNCONFIRMED]`, `replyTo` set
to the submitter so he can reply directly.
4. Email the submitter a confirmation link.
5. On click, email the owner a second notification prefixed `[CONFIRMED]` and
render a simple thank-you page.

The prefix is the whole point. An `[UNCONFIRMED]` submission is not a lead; a
`[CONFIRMED]` one is.

## Token signing (no database)

The token carries its own payload and an HMAC, so nothing is stored.

```js
const VERIFY_TTL_MS = 48 * 60 * 60 * 1000;
const VERIFY_SECRET = [REDACTED] || crypto.createHash('sha256')
  .update('phantombyte-verify-v1:' + smtpConfig.auth.pass).digest('hex');

function b64url(input) {
  return Buffer.from(input).toString('base64')
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function signToken(payload) {
  const body = b64url(JSON.stringify(payload));
  const sig = b64url(crypto.createHmac('sha256', VERIFY_SECRET).update(body).digest());
  return body + '.' + sig;
}
```

Verification must use `crypto.timingSafeEqual`, and must compare lengths first
because it throws on mismatched buffers:

```js
if (sig.length !== expected.length) return null;
if (!crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected))) return null;
```

Deriving the key from the password hash means the signature stays stable across
restarts with no extra environment variable to set. `VERIFY_SECRET` overrides it
if you ever want a dedicated key.

Validate `typeof payload.ts === 'number'` before the expiry check. A signed but
malformed payload should be rejected, not crash the handler.

## Rate limiting

In-memory, per IP, from `x-forwarded-for` (take the first entry and trim it,
Cloud Run appends). 5 submissions per hour. Return 429 with a message that
names the fallback email address. Prune the map when it grows, and be aware it
resets on container restart; that is acceptable at this volume and is not worth
a datastore.

## Pitfalls

- The form must send `source` so submissions from different pages are separable
  in the inbox. Without it, every page's form looks identical.
- A hidden honeypot field catches naive bots; leave it off the tab order and
  `aria-hidden`, and fake a success response rather than an error, so the bot
  does not retry.
- Never trust a client-side-only email format check. Validate server-side too.
- The `[UNCONFIRMED]` mail goes out before the submitter has proven anything, so
  never let it look like a booked lead.
- Verify locally with `node --check` only. Deploying is never this agent's job.
