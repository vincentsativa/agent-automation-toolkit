# Website Redesign & Services Architecture Audit

> Session-proven workflow for redesigning a PhantomByte site's copy, services list, and positioning
> based on a full audit of the Hermes agent setup, existing websites, scripts, skills, and automations.
> Use when Vinny says "redesign the website" / "write new text and services" / "look at everything we've built and write new copy."

## Trigger

- "website redesign" + "look at our Hermes setup, skills, automations, websites, scripts"
- "write me new text and services we should list"
- Any request to reposition PhantomByte services based on actual capabilities

## Audit Phase: What to Inventory

When Vinny asks you to review "everything we've built," this is the full scan:

### 1. Live Websites (curl, not browser)
```bash
curl -sL https://phantom-byte.com 2>/dev/null | head -500
curl -sL https://articles.phantom-byte.com/ 2>/dev/null | head -300
curl -sL https://phantom-byte.com/tutorials/ 2>/dev/null | head -300
curl -sL https://vincentsativa.com/ 2>/dev/null | head -400
```
Extract: current positioning, tagline, services listed with prices, article categories and counts, tutorial list with prices, CTA structure, design system (CSS variables), footer links.

**Browser tools may be broken** (missing agent-browser binary). Use `curl -sL` as the primary extraction method. Do not waste turns retrying browser_navigate when it fails with a file-not-found error.

### 2. Hermes Skills Library
```python
# Call skills_list tool, then count by category
# Capture: total skill count, categories, and notable skills
```
Key metrics to extract: total skill count, category count, notable custom skills that represent real capabilities.

### 3. Cron Jobs / Automations
```bash
cat ~/.hermes/cron/jobs.json | python3 -c "import json,sys; ..."
```
Extract: job names, schedules, what they do. These are live automations that prove the "autonomous content engine" service.

### 4. Scripts Directory
```bash
ls /mnt/c/Users/<user>/workspace/scripts/ | grep -iE '\.py$|\.js$|\.sh$'
ls /mnt/c/Users/<user>/workspace/ | grep -iE '\.html$|\.js$|\.py$|\.css$'
```
Extract: what categories of scripts exist (scraping, SEO, email, PDF, Gumroad, backup, competitor monitoring, etc.). These map directly to service offerings.

### 5. Hermes Config
```bash
head -80 ~/.hermes/config.yaml
```
Extract: models available, provider setup, agent configuration. This proves the "sovereign AI stack" capability.

### 6. Article Catalog
```bash
curl -sL https://articles.phantom-byte.com/ 2>/dev/null | grep -oP 'card-category">[^<]*' | sort | uniq -c | sort -rn
curl -sL https://articles.phantom-byte.com/ 2>/dev/null | grep -c 'article-card'
```
Extract: total article count, category distribution. This is the proof for "operator credentials."

## Synthesis Phase: Translating Audit to Services

### Key Insight Pattern

The current phantom-byte.com undersells by ~10x. It positions as a commodity "AI for small business" shop (chatbots $297, content $147/mo, RSS $97/mo). But the actual infrastructure includes:
- 64 Hermes skills across 14 categories
- 6 daily automated cron jobs (research, writing, publishing pipeline)
- 100+ Python/JS/Shell scripts for scraping, SEO, publishing, email, PDF generation
- 110+ published articles
- 9 paid tutorials on Gumroad
- 20+ production websites and APIs on Cloud Run
- 4 free debugging resources
- Multiple AI models via Ollama (GLM-5.2, Kimi K2.6, DeepSeek V4, Gemini 3, Qwen, Nemotron)

### Service Architecture Method

1. **List what actually runs** (not what could run, what IS running)
2. **Group into service categories** based on the three pillars:
   - AI Debugging (agent audits, failure mode diagnostics)
   - Sovereign AI Stack (local model deployment, Hermes setup, agent systems)
   - Cloud & Cyber Security (deployment, scraping, infrastructure)
3. **Price based on project complexity**, not monthly subscriptions (one-time deployments $800-$2,500, monthly retainers $1,000/mo for content engines)
4. **Write copy that states what you do, not what you sell**. "We build sovereign AI stacks" not "AI chatbot for your website"
5. **Include a stats bar** with real numbers from the audit (articles, sites, skills, automations)
6. **Cross-promote all properties** (articles, tutorials, debugging resources)

### Positioning Shift Pattern

| Old Positioning | New Positioning |
|---|---|
| "AI for small business" | "AI R&D studio and infrastructure builder" |
| "AI That Actually Makes Money" | "AI Infrastructure That Ships" |
| Commodity services (chatbot, RSS, content) | Specialized services based on actual capabilities |
| $97-$297 price points | $200-$2,500 project-based |
| No proof/case studies | Full stats bar, operator credentials, 110+ articles |
| Single site focus | All four properties cross-promoted |

## Copy Voice for Website

Website copy is NOT article copy. Differences from phantom-byte-writing-style:
- Still no em dashes (non-negotiable)
- Still direct and concise
- But can use structured formatting (tables, numbered lists, bullet points)
- Service descriptions should be 2-3 sentences max per service
- Stats bar is one line per stat
- CTA copy is imperative: "Send us your problem" not "We'd love to help you"
- The skeptical edge stays but is channeled into "we tell you if AI is the wrong tool" framing

## Output Format

Present as a structured document with:
1. Current state summary (what the site says now)
2. What's actually running (the full audit)
3. Proposed redesign copy (hero, stats, services, how it works, proof, CTAs)
4. Key changes table (old vs new positioning)
5. Offer to build as HTML or adjust copy first

## PhantomByte Site Ecosystem Reference

| Site | Purpose | Content |
|---|---|---|
| phantom-byte.com | Main services site | Service offerings, contact, article previews |
| articles.phantom-byte.com | Article archive | 110+ articles, AI infrastructure focus |
| phantom-byte.com/tutorials/ | Tutorial store | 9 paid tutorials ($0.99-$9.99), Gumroad links |
| vincentsativa.com | Debugging hub | 4 free resources, agent audit funnel |

All four sites share: PhantomByte branding, CSS variables (--purple #9D4EDD, --green #00FF88, --dark #0a0a0a), ghost favicon, "Code from the shadows" tagline, IONOS SMTP contact form, Google Analytics (G-PDQCZE09E4).