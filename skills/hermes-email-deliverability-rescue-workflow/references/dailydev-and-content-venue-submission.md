# Posting the deliverability offer to daily.dev (and reading its rules)

## Read the venue's rules from its live docs before writing a word

daily.dev's rules decide the post's shape, so fetch them every time rather than working from a remembered version. The docs are a JS-rendered site on `docs.daily.dev`; the reliable read is the sitemap plus scrapling, not a guessed URL.

```python
# scrapling (this is the required fetch path, per the scrapling-first rule)
from scrapling.fetchers import Fetcher
p = Fetcher.get('https://docs.daily.dev/sitemap.xml', timeout=40)
# the index points at /sitemap-0.xml; read every <loc> from that one
# pages that matter: content-guidelines, how-to-get-featured, content-moderation,
# suggest-new-source, creating-your-squad, growing-your-squad
Fetcher.get('https://docs.daily.dev/content-guidelines/', timeout=60).get_all_text()
Fetcher.get('https://docs.daily.dev/how-to-get-featured/', timeout=60).get_all_text()
```

- **Do not guess a docs path.** A plausible-looking path returned the site's 404 page, and the 404 renders the normal docs chrome, so a shallow read makes a missing page look like a loaded one. Confirm the slug against the sitemap before quoting a rule from it.
- A docs page also offers "Copy page as Markdown for LLMs" / "View as Markdown", which is the cheapest clean read when the rendered text is long.

## The three routes, and which one applies

- **Direct posting** ("New Post" button, everywhere on the platform) is open to every user. This is the route for the offer post. It replaced the older Community Picks system.
- **Squads** are open to all users and are the route daily.dev itself pushes for individuals, creators, and companies.
- **Suggest a Source** requires owning a well-known publication or a developer blogging platform. It explicitly EXCLUDES corporate and personal blogs, and daily.dev has formally migrated both classes of existing sources to Squads. Do not submit `articles.phantom-byte.com` as a source; it does not qualify, and the request burns the one thing a venue contact costs.

## The rejection list, verbatim in substance

A post is rejected, banned, or removed for: content irrelevant to developers; **content used primarily for self-promotion**; non-English content; content from sources inactive three months or more; clickbait or misleading content; content from sources with no public RSS or Atom feed; politically oriented content; programmatic SEO or auto-populated content; **AI-generated content or material with typical characteristics of AI-generated writing**; illegal, explicit, offensive, or discriminatory content; privacy violations, shortened or redirected URLs; content unsuitable for daily.dev's business reputation; and IP infringement.

- **Self-promotion as the primary purpose is the gate that matters.** The post must teach the diagnosis and the fix first, with the offer link in the closing ask. Same shape the dev.to rule already prescribes; the difference is formatting, below.
- **daily.dev prioritizes niche sources and applies more rigorous review to mainstream content.** A local-business defect study is niche, so say plainly in the body what was measured and how, rather than writing a general deliverability explainer.
- **The AI-writing clause is a real risk for a piece drafted by an agent.** Concrete measured numbers, live record strings pulled off the scan CSV, and plain declarative sentences are what separate this from generic generated prose. Do not pad the piece with framing paragraphs.
- An account is not needed to read the rules and not needed to draft. Posting itself is Vinny's action, so the deliverable is the finished file emailed to him, never a plan to post.

## The daily.dev post shape (differs from dev.to)

The same measured-finding skeleton as the dev.to post, formatted for daily.dev readers and for `phantom-byte-writing-style`:

1. Title leads with the measured number and states the human cost. "243 of 300 Small Business Domains Are Running Broken Mail Records. Nobody Told Them."
2. The sample is described and its origin named in plain language (public OpenStreetMap business listings for one metro), with the count and the percentage.
3. The defect breakdown by code, as a run of declarative sentences with the numbers, plus one line telling the reader the counts sum past the total because most domains carry more than one defect.
4. A section refusing the copy-blame frame, then two or three real record strings as the evidence, each followed by what a receiver does with it.
5. A ten minute check the reader can run: the three `dig` commands, then how to read each answer in order, including the 10-lookup limit and the fact that includes nest.
6. The staged fix order, with the sender inventory first and the explicit warning that jumping to `p=reject` turns a fix into an outage.
7. The ask, stated plainly: the flat fee, both delivery paths (we apply it with DNS access, or send a copy-paste sheet), the verification on two resolvers plus a read received-message header, and the free findings offer. Then the challenge question and the offer URL.

Formatting rules that are specific to what Vinny asks for in a plain-prose post file:

- Section headers are short ALL CAPS plain lines, no `##`, no `**`, no horizontal rules, no backticks, no bullet characters.
- Record strings sit inline in the prose, never in a code fence and never with a source attribution or URL after them.
- Numbers come off the scan CSV read in that session; quote the defect counts as measured, not rounded.
- One offer URL, placed at the end, so a reader who scrolls has exactly one link to hit.

## Verify before emailing, every time

Run the file through the mechanical pass and read the output rather than eyeballing the text:

```python
import re
t = open(path, encoding='utf-8').read()
print('em dash', t.count('\u2014'), 'en dash', t.count('\u2013'))
print('spaced hyphen', len(re.findall(r'\s-\s', t)))
print('braces', t.count('{') + t.count('}'))
print('longest line', max(len(l) for l in t.split('\n')))
```

All three dash counts and the brace count must read zero, and the longest line must be large (unwrapped body paragraphs), per the constitution's no-hard-wrap rule. Then send the file as an email attachment and prove the send by reading the message back over IMAP: the `Authentication-Results` header and the attachment byte count. A delivered attachment whose size does not match the file on disk is a truncated send, and it is invisible without that read-back.

## Email body for a content deliverable

When the deliverable is a content post, the covering email says what the file is, which venue's rules shaped it, which file the numbers came from, and the checks already run. It does not restate the post. The Telegram message afterwards is a doorbell and carries only that the email went out.
