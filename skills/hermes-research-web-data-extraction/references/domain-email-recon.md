# Domain & Email Reconnaissance

Trace an email address or domain back to its owner by combining browser, curl, and DNS tools.

## Pattern: Investigate an Email Address

Given an email like `phantom-byte@dann-sommer.dk`:

1. **Check the domain's website**, `browser_navigate("https://dann-sommer.dk")`
2. **If SSL fails** (ERR_CERT_AUTHORITY_INVALID), fall back to `curl -sk https://dann-sommer.dk/` to bypass cert validation
3. **Extract contact info** from the page:
   - `browser_console(expression='document.body.innerText.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/gi)')`, finds all email addresses on the page
   - `grep -iE "email|contact|mailto"` on the raw HTML
4. **Resolve DNS** to confirm the domain resolves: `python3 -c "import socket; print(socket.getaddrinfo('dann-sommer.dk', 80))"`
5. **Cross-reference**: check if the email domain matches the site owner's domain, or if it's a custom alias at a personal domain

## Why This Works

- `curl -sk` bypasses SSL cert issues that block the browser
- `browser_console` with JS regex extracts all email addresses from the rendered page in one call
- The email domain often reveals the registrant's personal/business domain, even when the email alias is different from the site being investigated

## Pitfalls

- Some sites redirect HTTP to HTTPS with a self-signed cert, `curl -sk` handles this, the browser won't
- WordPress sites often encode email addresses with HTML entities (`&#107;&#111;...`), the browser console extracts the decoded version, curl HTML does not
- The email alias may be a branded catch-all (`phantom-byte@...`) that doesn't match the site owner's name, check the site footer for the actual contact email
