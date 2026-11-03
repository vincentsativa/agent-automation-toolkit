---
name: outline-claim-verification
description: "Verify claims a brief names, at the source, then stop."
version: 1.0.1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Research, Citations, Verification, Fact-Checking]
    category: research
---

# Outline Claim Verification

A brief, outline, or data dump naming sources is a set of claims to check, not a
research assignment. Verify only the sources it names, at the source itself, and
stop. Every rule here exists because an outline is a transcription by a human
or a generator, and transcriptions drift.

## When to Use

- A brief names specific papers, IDs, vendors, reports, or prior articles and
  asks for the piece to be fact-checked or for gaps to be filled.
- A deliverable will cite those sources in a SOURCES section or equivalent.
- Skip for open-ended topic research: if no specific source is named, this is
  not the skill, and running it anyway produces scope creep.

## Procedure

1. **List every named claim** with its identifier as the brief gives it: paper
   id, vendor, report name, page slug, statistic.
2. **Fetch each named source directly.** For an identifier-based source, the
   identifier resolves regardless of the title you were handed, so a direct
   fetch is authoritative. For a URL-based source, fetch the real path.
3. **Read the source's own title and abstract, not the brief's description.**
   Briefs name sources by topic ("the coding-agent cost study"), and the real
   title can differ materially. Cite the real title.
4. **Pull the source's own numbers** while you are on the page. Abstracts carry
   sample counts and deltas that briefs compress into one rounded headline.
5. **Probe every cross-referenced URL live in both extension forms.** See the
   extension-form pitfall below.
6. **Omit what you cannot verify** through a primary source after a bounded
   effort, rather than including it unlabeled or attributing it by guess.
7. **Emit a SOURCES section** listing every primary source actually used, with
   publication, real title, date, and URL, so the work can be spot-checked.

## Pitfalls

- **A slug that 404s without an extension may 200 with `.html`.** Probe both
  forms against a live status check before calling a link dead, and cite the
  form that resolves. A brief's own note that links were previously verified is
  a claim to re-check, not a fact to quote.
- **A stub `sitemap.xml` is not an index.** A site's sitemap may list only a
  handful of top-level pages while the content lives on a separate subdomain
  that never appears in it. A clean grep against the stub proves nothing about
  whether a page exists; probe the subdomain path directly.
- **A topic description is not a title.** An entry like a bare paper number
  plus a paraphrase is a description. Cite the source's real title or the claim
  cannot be found by a reader or checked by a spot-check.
- **Fetch redirects with follow enabled.** A bare host often answers a redirect
  on one form of the URL, so a no-redirect fetch returns a redirect stub that
  looks like an empty or missing document.
- **A news write-up is not the source.** Aggregators drop specifics from the
  original. When the piece leans on a detail, confirm it at the original and
  cite the original.
- **Don't broaden the sweep.** The named sources are the whole scope. Checking a
  source that no claim rests on is scope creep, and it is the failure this skill
  exists to prevent in the other direction.

## Verification

Before delivering: every named claim either traces to a primary source you
fetched, or is omitted. Every SOURCES entry has a resolvable URL and the real
title. No citation rests on a brief's paraphrase of a source.

## References

- `references/source-extraction-recipes.md` — concrete fetch and extract
  patterns per source type (preprint abstract pages, forum listings, product
  sites, self-hosted article archives, status probing without a browser).
