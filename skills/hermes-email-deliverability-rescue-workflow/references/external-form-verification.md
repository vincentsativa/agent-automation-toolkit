# Verifying a stranger's contact form from the outside

Supports the Dead Contact Form Rescue offer ($500 flat, email only, no calls, delivered in a day), the same shape as the deliverability rescue. The offer is only honest if every claim in the outreach email is something the scanner measured.

## What is provable without access, and what is not

The submission path is the measurement. The owner's inbox, spam folder, mail logs, and CRM are invisible to you, and a host can silently drop a PHP mail() call behind an HTTP 200, so never write "your inbox received nothing" or "your form drops every lead".

Provable from outside: whether a form exists in the markup and how many forms the page has; the exact action URL and method; whether the endpoint exists and what status and body it returns for your test submission; whether the browser actually issued a request when the button was pressed (this separates "the request failed" from "no request was ever sent"); whether a JavaScript exception fired; whether a third-party handler returned its own error such as an exhausted quota or a disabled project; whether a promised confirmation email to the submitter arrived; whether a captcha, honeypot, or required-field rule rejected a normal submission.

The email line that is allowed: name the domain, the timestamp, and the measured result. "I submitted your contact form this morning. The page told me the message was sent, and the request it made came back 404." The offer page carries the same limit under "What I will not promise": you cannot see their inbox, you test the path and fix what you find there.

## Scanner mechanics

Two phases per domain, because builder sites render the form in JavaScript and are invisible to a plain fetch. Phase one static: fetch the homepage, find the contact page by anchor text and by common paths (/contact, /contact-us, /get-in-touch, /book, /quote), parse every form element. Phase two dynamic: open the page in the headless browser, fill the form, enable network capture, submit, and record the request URL, status, response snippet, and any console exception.

Fingerprint the handler so the report can name the platform: /wp-json/contact-form-7/v1/contact-forms/<id>/feedback is Contact Form 7; /wp-admin/admin-ajax.php with a wpforms_submit or gravityforms action is WPForms or Gravity Forms; formspree.io/f/<id> is Formspree; a hidden form-name field on Netlify is Netlify Forms; api.web3forms.com is Web3Forms; a HubSpot forms endpoint is HubSpot; no form element plus a JavaScript bundle means Squarespace, Wix, or a custom widget.

Test identity: one name, one plainly labelled message ("This is a delivery test for your contact form"), no links in the payload, and a tagged address of hello+cf-<short hash of the domain>@phantom-byte.com so every submission is attributable and one inbox catches them all. Verify plus-addressing reaches the inbox before depending on it. One submission per prospect, only for prospects entering that day's outreach queue, because every working form delivers a real message into a stranger's inbox; scan the batch the night before and email it the next morning.

Output CSV columns, kept in the same shape as email_scan.py so the findings sheet and the scheduler keep working: domain, contact_page_url, form_found, form_count, action_url, method, handler_type, submit_status, submit_body_snippet, network_request_seen, js_error, captcha_type, honeypot_present, required_fields, test_email, confirmation_received, qualified, defect_codes, scanned_at. Qualified is deliberately narrow: any of a non-2xx submit status, a success message with no network request, a JS exception, a third-party handler in an error state, or no form at all on a site that advertises a contact page. The scanner writes its own CSV and cache, never state.json.

## Fix runbook by platform

- Contact Form 7: empty or wrong To address; a host blocking PHP mail() so the form reports success anyway; a plugin update issuing a new form id while the page still posts to the old one. Fix with authenticated SMTP, the correct recipient, and a re-pointed action.
- WPForms and Gravity Forms: notification never configured, conditional logic excluding the default submission, or anti-spam rejecting it. Fix, then add a mail log plugin so future losses are visible.
- Formspree, Web3Forms, Getform: an exhausted free tier returns a quota error that the front end swallows into the same friendly success message. Upgrade or replace, and make the front end surface real errors.
- Netlify Forms: form-name missing from the built HTML, so the POST 404s.
- Squarespace and Wix: platform black box, so the fix is often the destination mailbox, which is a deliverability job rather than a form job. Say so instead of implying a code fix.
- Custom PHP or Node endpoints: mail() headers, SMTP authentication failure, or a catch block returning success regardless of the outcome.
- Platform independent: mixed content or CORS blocking the POST, a mobile layout hiding the button under a chat widget, a duplicated stale form.

Every fix ends the same way: re-run the submitter, record the response, and where the buyer granted access confirm one fresh submission arriving in their own inbox. The re-test record is the proof the before-and-after report contains.

## Where the launch plan lives

The day-by-day launch plan for this offer is delivered by email, not kept on disk. Recover the delivered copy from the mailbox (see the artifact-recovery section of the email-sender skill) instead of re-deriving it, and when the plan is amended on disk, amend the same text in the generator that produced it.
