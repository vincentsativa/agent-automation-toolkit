---
name: reorder-articles
description: Reorders articles on articles.phantom-byte.com homepage. Moves specified article HTML to position #1 in index.html, shifts all others down. NO articles removed, deleted, or modified. Use after publish-article when user says "put it at the top" or "make it number one".
---

# Reorder Articles Skill

## TRIGGER

When user says:
- "put it at the top"
- "make it number one"
- "reorder articles"
- "move [article name] to first position"
- "shift everything down"
- "reorder homepage"

## CRITICAL RULES

| Rule | Enforcement |
|------|-------------|
| **NO DELETIONS** | Never remove any article HTML file |
| **NO CONTENT CHANGES** | Never modify article HTML content |
| **ONLY index.html** | Only change the article order in homepage |
| **PRESERVE ALL OTHERS** | Every existing article stays, just shifts position |
| **NEW ARTICLE = 1** | Target article appears first in homepage list |
| **OTHERS +1** | All other articles shift down by one position |

## WORKFLOW

### Step 1: Identify Target Article

Determine which article to put at top:
- If user specifies: use that article
- If not specified: use the most recently published article

**Extract:**
- Filename (e.g., `the-claude-mythos-worlds-most-dangerous-ai.html`)
- Title, description, date from the HTML file
- Full article card HTML to insert

### Step 2: Read Homepage

```powershell
Get-Content "~/workspace/articles/index.html" -Raw
```

**Find the article list section:**
- Look for `<div class="article-grid">` or similar container
- Or find existing article cards: `<article class="article-card">`

### Step 3: Extract Article Card HTML

From target article's HTML file, build the homepage card:

```html
<article class="article-card">
    <h3><a href="the-claude-mythos-worlds-most-dangerous-ai.html">The Claude Mythos: Why the World's Most Dangerous AI Stays Under Lock and Key</a></h3>
    <p class="article-excerpt">Anthropic's Claude Mythos can hack any system and find critical vulnerabilities. Why did tech giants create the Glasswing initiative to contain it?</p>
    <span class="article-date">April 10, 2026</span>
</article>
```

### Step 4: Reorder Logic

**Read current homepage structure:**
```
Current order:
1. Article A (genius-to-useless-ai-agent.html)
2. Article B (why-openclaw-locally-beats-vps.html)
3. Article C (four-research-breakthroughs-ai-paralysis.html)
...
```

**Algorithm:**
1. Find target article card in homepage (if exists)
2. Remove it from current position
3. Insert as FIRST article in the list
4. All other articles naturally shift down

**OR** if article not yet on homepage:
1. Insert new article card as FIRST item
2. All existing articles shift down

### Step 5: Update index.html

Use edit tool to modify `~/workspace/articles/index.html`:

**Find the article grid/list section and reorder:**

```html
<!-- BEFORE -->
<div class="article-grid">
    <article class="article-card">
        <h3><a href="genius-to-useless-ai-agent.html">How My AI Agent Went From Genius to Useless</a></h3>
        ...
    </article>
    <article class="article-card">
        <h3><a href="why-openclaw-locally-beats-vps.html">Why OpenClaw Locally Beats VPS</a></h3>
        ...
    </article>
    <!-- Target article somewhere below or not present -->
</div>

<!-- AFTER (target at top) -->
<div class="article-grid">
    <article class="article-card">
        <h3><a href="the-claude-mythos-worlds-most-dangerous-ai.html">The Claude Mythos...</a></h3>
        ...
    </article>
    <article class="article-card">
        <h3><a href="genius-to-useless-ai-agent.html">How My AI Agent Went From Genius to Useless</a></h3>
        ...
    </article>
    <article class="article-card">
        <h3><a href="why-openclaw-locally-beats-vps.html">Why OpenClaw Locally Beats VPS</a></h3>
        ...
    </article>
    <!-- All other articles preserved, shifted down -->
</div>
```

**Critical:** 
- Do NOT change any article HTML files
- Do NOT remove any article cards
- Only reorder within index.html

### Step 6: Git Commit

```bash
cd ~/workspace/articles

git add index.html
git commit -m "chore: reorder homepage - <article-slug> now featured at #1"
```

### Step 7: Build & Deploy

```bash
cd ~/workspace/articles

# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/gen-lang-client-0237860564/articles --timeout=300s

gcloud run deploy articles `
  --image gcr.io/gen-lang-client-0237860564/articles `
  --region us-central1 `
  --allow-unauthenticated `
  --port 8080
```

### Step 8: Verify Homepage

```powershell
Start-Sleep -Seconds 15

# Check homepage loads
Invoke-WebRequest -Uri "https://articles.phantom-byte.com/" -UseBasicParsing | 
  Select-Object StatusCode
```

**Verify target article appears first** (parse HTML or visually check).

### Step 9: Report Success

```
✅ HOMEPAGE REORDERED

**Featured at #1:** <article-title>
**URL:** https://articles.phantom-byte.com/<slug>.html

**New homepage order:**
1. <Article 1>
2. <Article 2>
3. <Article 3>
...

**Build:** <revision-id>
**Status:** Live

All articles preserved. None removed. Only order changed.
```

## WHAT THIS SKILL DOES

✅ Reorders article cards in `index.html`
✅ Puts target article at position #1
✅ Shifts all other articles down by one
✅ Commits and deploys to Cloud Run
✅ Preserves ALL articles (none removed)

## WHAT THIS SKILL DOES NOT DO

❌ Does NOT delete any HTML files
❌ Does NOT modify article content
❌ Does NOT change footer or SEO
❌ Does NOT add/remove articles from site
❌ Does NOT change Privacy/Terms links

## FILE PATHS

- **Homepage:** `~/workspace/articles/index.html`
- **Articles:** `~/workspace/articles/*.html`
- **Live URL:** `https://articles.phantom-byte.com/`

## EXAMPLE INVOCATION

**User:** "put it at the top"

**Assistant:**
```
Identifying target article: the-claude-mythos-worlds-most-dangerous-ai.html

Reading homepage (index.html)...
Found 35 article cards.

Reordering:
- the-claude-mythos... → position 1 (was 23)
- genius-to-useless... → position 2 (was 1)
- why-openclaw-locally... → position 3 (was 2)
- ... (33 more articles shifted)

Committing and deploying...
```

**After deploy:**
```
✅ HOMEPAGE REORDERED

**Featured at #1:** The Claude Mythos: Why the World's Most Dangerous AI Stays Under Lock and Key
**URL:** https://articles.phantom-byte.com/the-claude-mythos-worlds-most-dangerous-ai.html

**New homepage order:**
1. The Claude Mythos...
2. How My AI Agent Went From Genius to Useless...
3. Why OpenClaw Locally Beats VPS...
4. Four Research Breakthroughs...
...

**Status:** Live

All 35 articles preserved. None removed.
```

## SAFETY CHECKS

Before reordering:
- ✅ Target article HTML file exists
- ✅ Homepage (index.html) exists
- ✅ Article card can be built from target HTML
- ✅ Git working tree clean
- ✅ User intent confirmed (reorder, not delete)

## ERROR HANDLING

| Error | Recovery |
|-------|----------|
| Article not found | Ask user for correct filename |
| Homepage parse fails | Read file, find article grid manually |
| Git push fails | Check auth, remote, retry |
| Cloud Build fails | Check GCP, view logs, retry |
| Order not updated | Wait 30s, hard refresh, verify deploy |

## MANUAL VERIFICATION

After deploy, verify at:
- Homepage: `https://articles.phantom-byte.com/`
- Target article should appear FIRST in the list

**Expected:** Target article is first visible article on homepage.

---

## QUICK REFERENCE

```
/skill:reorder-articles <article-slug>
# or simply: "put it at the top"

Result: Target article → #1 on homepage, all others → shift down
```
