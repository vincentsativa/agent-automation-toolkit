# Daily Social Media Posts Cron — Full Workflow

Recurring daily cron producing a document of 10 Pinterest titles + descriptions,
ranked best to worst. #1 = strongest broadest hook, #10 = most niche; evergreen
post goes at #10.

## 1. Data source
Stories come from `~/Desktop/TODAYS DATA FILES/`. Primary file is
`20-AI-News-Stories-<date>.md` (~25 fresh stories, deduplicated against the other
reports). Supplement with `ironpulse-<date>.txt`, `tensorfeed_report_<date>.txt`,
`blogwatcher-<date>.txt` only if more material is needed. Do NOT invent stories.

## 2. Visit the boards first
Before writing, navigate each of Vinny's Pinterest boards to see what is already
posted (avoids re-using the same topics day over day, keeps the feed fresh):
- Main hub: `https://www.pinterest.com/PhantomByteAI/ai-news-machine-learning-emerging-tech/`
- AI Agents: `https://www.pinterest.com/PhantomByteAI/ai-agents-automation-guide/`
- AI Tools: `https://www.pinterest.com/PhantomByteAI/ai-tools-for-business-productivity-2026/`
- AI for Developers: `https://www.pinterest.com/PhantomByteAI/ai-for-developers-programming-ai-tutorials/`
- Agent Security: `https://www.pinterest.com/PhantomByteAI/agent-security-prompt-injection-sandboxing/`

## 3. Board assignment mapping (each post = exactly ONE board)
- AI agents, agentic AI, AI automation, agent frameworks → **AI Agents** (ai-agents-automation-guide)
- AI tools, AI for business, productivity, marketing software, AI writing/design tools → **AI Tools** (ai-tools-for-business-productivity-2026)
- AI for developers, programming AI, developer tools, coding tutorials, AI coding assistants, APIs, software development with AI → **AI for Developers** (ai-for-developers-programming-ai-tutorials)
- AI security, agent security, prompt injection, AI sandboxing, containment, least-privilege agents, model governance, AI threat defense → **Agent Security** (agent-security-prompt-injection-sandboxing)
- Everything else (AI news, ML, robotics, quantum, emerging tech, general AI news) → **Main AI News** (ai-news-machine-learning-emerging-tech) — the default.

## 4. Verification (MANDATORY before emailing)
Write the posts into a Python script list of tuples `(rank, board, title, desc)`,
then `len()`-check every title (max 100) and description (max 500). Do NOT trust
your own annotation — actual `len()` frequently differs from the number you
estimate. Drafts naturally land at 450-520 chars for descriptions; trim the
offenders one at a time until ALL pass. Re-run the script after every edit batch.
Keep the final list verified as "ALL OK" before generating the deliverable.

Writing tip that converges faster: write descriptions to ~350-400 chars first,
verify all pass, then expand each with SEO keywords and an engagement hook toward
450-500. Never write long and trim down (produces choppy prose and many iterations).

## 4b. Board labels are Vinny's picker
Vinny reads the BOARD labels in the text file to decide which posts to publish and
place into boards himself. His articles anchor the Main AI News board. So when the
day's data allows, spread posts across the non-news boards (AI Agents, AI Tools,
AI for Developers, Agent Security) so he has candidates to fill them. The day's
data is the hard constraint: never force a topic that has no story. Keep labels
clean and consistent so he can scan and pick fast.

## 5. Delivery
1. Write the document to `~/Desktop/TODAYS DATA FILES/social-media-posts-<date>.txt`
   — label each post with its rank and `BOARD: <name>`.
2. Email it as an attachment to `hello@phantom-byte.com` (the ONLY Vinny address;
   run the pre-flight address grep on the script). Subject: `Bill: Daily Social Media Posts For X and Pinterest`. Sign body with `— Bill`.
3. Telegram notification: ONLY a brief confirmation that the email was sent (e.g. "Email sent with today's social media posts for X and Pinterest"). Do NOT paste post content, titles, summaries, or lists into Telegram. The email is the delivery mechanism; the Telegram note is a doorbell.

## Style constraints (from writing-style skill — all apply)
- No em dashes. Proper punctuation only (commas, colons, periods).
- Keyword-rich for Pinterest SEO: include relevant AI terms naturally
  (artificial intelligence, machine learning, AI news, emerging technology,
  AI security, robotics, deep learning, AI infrastructure, future technology, AI policy).
- Lead with the concrete news hook (who/what/number), then why it matters, then an
  engagement close ("Save this for your next deep dive into...", "Follow PhantomByte
  for..."). Show authority, not hype. No "mind-blowing" or "game-changing" without evidence.
- Titles: front-load the primary keyword (Pinterest crawls left-to-right).
- Descriptions: primary keyword in the first ~50 chars (the search snippet).
