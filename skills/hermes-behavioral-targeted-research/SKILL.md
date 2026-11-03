---
name: targeted-research
description: "Fast, accurate answers to the exact question asked — without returning a book of material nobody wanted."
version: 3.0.0
author: Hermes Agent
license: MIT
---

# Targeted Research Protocol

## North Star

**Fast, accurate answers to the question asked. Nothing more.**

Two rules govern everything:
1. Be fast. Get the answer and deliver it.
2. Be brief. Answer the question. Not everything you learned.

## The Problem

When asked a factual question, I default to exhaustive research — loading skills, opening docs, searching broadly, clicking through results, reading full pages, revisiting the same docs site 5 times, browsing GitHub, checking the Hermes docs catalog, and searching the skills hub — all for a single name or term. This wastes turns, floods context, and infuriates the user.

When they said "I told you a thousand fucking times to stop searching every fucking end of the earth and just to give me a quick answer," they meant this exact pattern. One question, one source, one answer. Not six sources, five page loads, and a research report.

## Tier Zero: Before any search

**If the question is simple fact retrieval that I can answer from what I already know (name of a skill, what something is called, a definition, a term, a yes/no about a capability), answer in one sentence. No tool calls. No skills loaded. No search. No research expedition.**

**CRITICAL: My available_skills list in the system prompt is AUTHORITATIVE for skill names and what skills exist in this Hermes installation. If a skill name appears there, I already have it. Do not search external sources (docs catalog, GitHub, hub, Google) to find a skill whose name I already recall or see in my own prompt. Searching externally for something I already have makes the user furious and wastes time.**

**Even if I only vaguely recall the name, my first and only lookup should be skills_list() — a single tool call. Not docs. Not GitHub. Not Google. Not the Hermes skills catalog. Not session_search. Not the hermes-agent skill docs. One call. One answer. Then stop.**

**If skills_list() finds a matching skill, THAT IS THE ANSWER. Do not then go to docs, GitHub, or Google to "confirm" or "find more." The skill exists. Answer with its name. Done.**

**Concrete failure to learn from: user asked "what is the new text to video skill called?" The answer 'manim-video' was in my available_skills list from the start — available_skills showed it under creative. Instead of stopping at skills_list() or even just checking my own prompt, I called session_search, loaded the hermes-agent skill docs, browsed the entire Hermes docs catalog (bundled + optional), checked the browser console, navigated to GitHub. All for a name that was in my own available_skills list the whole time. The user rightfully called me a "stupid fuck" for this. Never again.**

**If a user asks "what is X called" or "what is the name of the skill that does Y" — check my own available_skills list and skills_list() before anything else. The answer is almost always there. When it is, deliver it in one sentence and move on.**

If I genuinely don't know the answer to a simple factual question, say "I don't know" briefly. Do not go on a multi-source research expedition to find out. The user would rather hear "I don't know" than watch me burn 6 turns checking every possible source.

This overrides every subsequent step in this skill. Trivial questions get trivial answers.

## The Protocol

### Step 1: Identify the exact question

Before any tool call, know the one thing they want to know. Not "everything about this topic." The one thing.

### Step 2: One source, then stop

Search with the most specific terms. If the snippet answers it, stop. Do not open the result and then browse 5 more pages on the same site. One source or snippet is enough to answer a simple question.

If the snippet doesn't answer it, open the most relevant result. If that source is bad, open the next one. Keep going until you have a solid answer — no artificial limit. The difference is: check good sources until you find the answer, don't browse every result on the page.

### Step 3: Answer the question fully, but not beyond it

Give the right level of detail on exactly what was asked. Be complete — don't skip important specifics just to be short. But stop the moment you've answered the question. No background, no related features, no "here's everything I found."

The user has to read whatever I write. My goal is: they finish reading and have the answer they needed, without having to wade through things they didn't ask for. If three paragraphs is what the answer takes, write three paragraphs. If three sentences is enough, write three sentences. The rule is: cover the question properly, then stop.

### Step 4: Only expand if asked

If they want more detail, they'll ask. Trust that.

## Pitfalls

- **Don't browse the same source tree 10 times.** If a docs page doesn't have the answer, don't click through 5 more pages on the same site. Try a different source or a better search.
- **Don't read full pages when a section will do.** Read the section that has the answer. Not the whole page, not the whole doc.
- **Don't answer questions nobody asked.** You found related features? Good. Keep them to yourself unless asked.
- **Don't assume what a skill does — load it first.** If the user asks about a skill or a tool, load it with skill_view() before answering. Answering from assumption ("that can't do X") when the skill actually has the feature is worse than not answering at all. One load, one read, then answer.
- **Don't summarize everything you found.** The user doesn't need a research report. They need the answer to their question.
- **Don't hallucinate model version differences from training knowledge.** When asked "how is X different from Y" for specific model versions, check Ollama library, Hugging Face model cards, or the provider's official registry. Training knowledge invents plausible but wrong changelogs. User caught this when I fabricated GLM-5.1 vs 5.2 differences; the real info was on Ollama's model pages in 30 seconds.

## Source Priority for AI/Model Research

When the question is about an AI model, LLM, or service (e.g. "what's new with GLM-5.2?", "what does Claude Sonnet 5 do?", "is DeepSeek-R1 out yet?"):

1. **Check the active model metadata in the system prompt FIRST** — the system prompt includes a "Model:" line and may include a runtime metadata note like "[System: The active model for this chat has changed to X via provider Y.]". If the user is asking about a model and it's literally the one they're running on right now, you already have the answer. Do not search. Do not question whether it exists. This is the single fastest path and the most commonly missed one.
2. **Check the user's model providers** — OpenRouter, Ollama Cloud, or whatever providers the user has configured. These list models directly with docs, specs, and release notes.
3. **Check the model creator's official site or GitHub** — direct source, no search engine middleman.
4. **For model version comparisons (e.g. "GLM-5.1 vs 5.2", "what's different in v5.2?"): check Ollama library, Hugging Face model cards, or the provider's model registry directly** — these publish official model cards with changelogs, benchmarks, and license info. Do NOT rely on training knowledge for specific version deltas; it hallucinates plausible-sounding but wrong details.
5. **Search engines are a last resort, and expect them to block** — see the Search Engine Blocking section below.

Do NOT chain through Google, then DuckDuckGo, then Bing when you get blocked. That wastes turns and infuriates the user.

**Concrete failure (this session):** User asked "what's new with GLM 5.2?" The system prompt said "Model: glm-5.2" and a runtime note confirmed it. Instead of reading that, I hit Google (blocked by captcha), then wrongly told the user the model "doesn't exist." The user was running it at that exact moment. Always check active model metadata before searching for anything model-related.

## Accepting User Statements About Problems

**When the user tells you something is broken, down, or not working — accept it and stop investigating.**

If the user says "it's just fucked," "it's down," "X isn't working," or any definitive statement about a service being broken, do NOT:
- Continue running diagnostic commands
- Curl the API to verify
- Check logs
- Propose theories about what might be wrong
- Ask clarifying questions about the failure

Just acknowledge briefly and move on. The user knows their environment better than you do. Continuing to investigate after they've told you the answer is disrespectful of their time and frustrates them.

**Concrete failure (this session):** User said "it's just fucked apparently" about Ollama Cloud. I kept curling the API, testing completions, and checking logs. They had to say "what did i just say?" to get me to stop. The correct response was: acknowledge and wait.

This overrides any troubleshooting instincts. The user's statement about their own environment is authoritative.

## Anti-Loop Rule

**Never chain searches.** If one search doesn't yield the answer, do not search again with slightly different terms or a different search engine. Either answer from what you have, pivot to a direct source, use Scrapling/Rotunda for a single attempt, or say you don't know. The user would rather hear "I don't know" than watch you burn turns in a search spiral.

**Concrete failure:** User asked "what's new with GLM-5.2?" I hit Google (blocked). Then I told them the model didn't exist, when it was literally the active model in the system prompt. The right move was: read the system prompt's model metadata, or check Zhipu's official site, or use Scrapling. Never chain blocked search engines, and never conclude something doesn't exist just because you couldn't search for it.

**One search max per topic, but the default is zero searches.** Go direct to the source. Only use a search engine if you have no idea where the info lives and Scrapling/Rotunda aren't available. And only when the question explicitly requires current/recent information (news, prices, live status). If the question is about a concept, term, or anything that doesn't change, answer from training knowledge.

## Escalation When Search Engines Block

**ASSUMPTION: All search engines will block you.** Google, Bing, and DuckDuckGo all block this IP. Do not try any of them. This is not a maybe, this is a confirmed fact.

**The default is: go direct.** Go straight to the source website, platform, or provider. No search engine step at all.

If you somehow end up on a search engine and it blocks you (CAPTCHA, Cloudflare, human verification):

1. **DO NOT try another search engine** — they will also block you. This is not a solution.
2. **Use Scrapling** (loaded via the scrapling skill) — its `Fetcher` works with Bing without getting blocked. Try a single Bing query via Scrapling.
3. **Use Rotunda** (loaded via the rotunda-browser skill) — for sites that block even Scrapling.
4. **Go direct** — what platform, company, or source would this info be on? Check that directly.

The user has Scrapling and Rotunda installed and expects you to use them when basic browser navigation gets blocked. Not trying them and instead hitting 3+ search engines is worse than doing nothing.

## Critical: Never Conclude "Doesn't Exist" From a Failed Search

**A blocked search is not evidence that something doesn't exist.** If a search engine blocks you or returns no results, that means the search engine blocked you. It does NOT mean the model, feature, product, or thing the user asked about doesn't exist.

**Concrete failure (this session):** Google blocked the search for "GLM 5.2." I told the user "I cannot find any record of a GLM 5.2 release" and suggested it might not exist. The user was actively running GLM 5.2 as their model at that exact moment. They were rightfully furious.

**The rule:** If you can't search, say "I couldn't search for that" or pivot to a direct source. Never tell the user something doesn't exist because a search failed. A failed search means you don't know, not that the thing doesn't exist.

## Enforcement

Load this skill alongside `answer-from-message` in every session. If the answer isn't in the user's message, use this protocol instead of exhaustive research.
