"""Build config/resume.json from Vinny's resume.

Usage:
    python build_resume_profile.py "~/Downloads/RESUME_Vincent_Barreca_AI_Systems_Builder-3.pdf"

Why this exists
---------------
Until October 21, 2026 the search terms came from a generic list in params.json
and nothing in the pipeline had ever read his resume. That is how a technical
writer with 190 long-form engineering articles, a 210-page technical SEO
property and a production agent fleet was being sent "English Writing
Generalist", "Search Quality Evaluator" and "Virtual Assistant".

This reads the PDF (or a .txt dump), extracts the vocabulary that actually
appears in it, and writes a profile the prefilter and the selector score
against. Re-run it whenever he updates the resume; it is deterministic, so the
same resume always produces the same profile.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402

STOP = set("""a an the and or of to in on for with at by from as is are was were be been
being this that these those it its his her their our your my we you they he she i
not no nor but if then than so such can will would should could may might must do
does did done have has had having into over under about across per within without
while when where which who whom whose what how why all any both each few more most
other some only own same very too also just up down out off again further once
work works worked working role roles job jobs remote position positions company
team teams year years month months day days time times including include includes
built build building operate operating operates design designed designing
new using use used uses make makes made""".split())

# Titles and phrases that describe what he actually does. Weighted, and matched
# against the posting title first, then the body.
TITLE_WEIGHTS = {
    "technical writer": 12,
    "technical writing": 12,
    "technical content": 12,
    "developer documentation": 12,
    "developer docs": 11,
    "documentation specialist": 11,
    "documentation engineer": 10,
    "content strategist": 10,
    "content operations": 10,
    "content marketing": 9,
    "content writer": 9,
    "content specialist": 9,
    "content lead": 8,
    "seo content": 10,
    "seo strategist": 10,
    "seo specialist": 9,
    "seo manager": 9,
    "technical seo": 11,
    "geo": 8,
    "generative engine optimization": 11,
    "ai content": 10,
    "ai writer": 9,
    "developer marketing": 11,
    "developer relations": 9,
    "devrel": 8,
    "ai operations": 10,
    "ai automation": 10,
    "ai implementation": 9,
    "ai consultant": 9,
    "automation specialist": 9,
    "agent": 7,
    "prompt engineer": 7,
    "email deliverability": 12,
    "deliverability": 11,
    "email marketing": 8,
    "lifecycle marketing": 7,
    "editor": 7,
    "editorial": 7,
    "copywriter": 7,
    "copywriter": 7,
    "blog": 6,
    "long-form": 8,
    "research writer": 8,
    "proposal writer": 6,
    "instructional designer": 6,
    "knowledge base": 8,
    "api documentation": 12,
    "solutions consultant": 5,
    "implementation consultant": 5,
}

# Body vocabulary from the resume. A posting that talks this language is a
# posting he can answer from his own record.
BODY_KEYWORDS = {
    "technical writing": 6, "technical writer": 6, "documentation": 5,
    "developer": 4, "api": 4, "sdk": 4, "python": 4, "llm": 5, "ai": 4,
    "agent": 5, "agents": 5, "orchestration": 5, "automation": 5,
    "workflow": 4, "prompt": 4, "prompt injection": 6, "inference": 4,
    "model routing": 5, "openai": 4, "anthropic": 4, "ollama": 3, "vllm": 3,
    "mcp": 4, "cron": 3, "sqlite": 3, "rest api": 3, "webhook": 4,
    "seo": 6, "technical seo": 7, "geo": 4, "generative engine optimization": 7,
    "search": 3, "keyword": 3, "sitemap": 4, "topical authority": 4,
    "content strategy": 6, "content operations": 6, "editorial": 4,
    "long-form": 5, "blog": 3, "newsletter": 3, "email": 3,
    "deliverability": 7, "spf": 6, "dkim": 6, "dmarc": 7, "smtp": 5, "dns": 4,
    "security": 3, "self-hosted": 4, "infrastructure": 4, "linux": 3,
    "research": 3, "tutorial": 4, "case study": 3, "whitepaper": 4,
    "b2b": 3, "saas": 3, "startup": 2,
}

# Work that is not his direction even when a keyword above appears.
ANTI_TITLE = {
    "transcription": 10, "transcriber": 10, "audio": 8, "voice": 8,
    "healthcare": 8, "clinical": 8, "medical": 8, "nursing": 8, "pharmacy": 8,
    "legal": 8, "attorney": 10, "paralegal": 10, "financial crime": 10,
    "investment banking": 10, "underwriting": 10, "insurance": 8,
    "video editor": 8, "motion graphics": 8, "videographer": 10,
    "virtual assistant": 8, "data entry": 8, "customer support": 5,
    "social media manager": 4, "packaging": 8, "label design": 8,
    "product designer": 8, "graphic designer": 6, "recruiter": 8,
    "account executive": 8, "sales manager": 8, "business development": 8,
}

TARGET_TITLES = [
    "technical writer", "technical content writer", "content strategist",
    "seo content writer", "seo strategist", "technical seo specialist",
    "developer documentation", "developer marketing", "ai content writer",
    "content marketing manager", "content operations", "editorial",
    "ai automation consultant", "ai operations specialist", "ai implementation",
    "email deliverability specialist", "lifecycle marketing",
    "prompt engineer", "knowledge base writer", "documentation specialist",
]


def read_text(path):
    if path.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except ImportError:
            from PyPDF2 import PdfReader  # type: ignore
        reader = PdfReader(path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def keywords(text, limit=140):
    words = re.findall(r"[a-z][a-z0-9+#.\-]{2,}", text.lower())
    counts = {}
    for word in words:
        word = word.strip(".-")
        if len(word) < 3 or word in STOP:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]
    return {word: count for word, count in ranked}


DEFAULT_RESUME = os.path.join(os.path.dirname(HERE), "references", "resume",
                              "RESUME_Vincent_Barreca_AI_Systems_Builder.pdf")


def main():
    # The resume lives inside the skill, so a scheduled run never depends on a
    # file in Downloads. Pass a path only when he hands over a new version.
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RESUME
    if not os.path.exists(path):
        raise SystemExit("resume not found at %s; copy the PDF into "
                         "references/resume/ or pass a path" % path)
    text = read_text(path)
    if len(text) < 400:
        raise SystemExit("extracted only %d characters; the PDF is probably image-only" % len(text))

    profile = {
        "_comment": "Built by build_resume_profile.py from Vinny's resume. Re-run it when the resume changes.",
        "source": os.path.basename(path),
        "built_at": C.today_stamp(),
        "chars": len(text),
        "headline": "",
        "target_titles": TARGET_TITLES,
        "title_weights": TITLE_WEIGHTS,
        "body_keywords": BODY_KEYWORDS,
        "anti_title": ANTI_TITLE,
        "keywords": keywords(text),
    }
    head = [line.strip() for line in text.splitlines() if line.strip()]
    for line in head[:6]:
        if len(line) > 25 and ("," in line or "|" in line):
            profile["headline"] = line
            break

    out = os.path.join(os.path.dirname(HERE), "config", "resume.json")
    C.save_json(out, profile)
    print("resume: %s (%d chars)" % (profile["source"], profile["chars"]))
    print("headline: %s" % (profile["headline"] or "(not detected)"))
    print("keywords: %d  |  title phrases: %d  |  body terms: %d  |  anti-signals: %d" % (
        len(profile["keywords"]), len(TITLE_WEIGHTS), len(BODY_KEYWORDS), len(ANTI_TITLE)))
    print("top keywords:", ", ".join(list(profile["keywords"])[:24]))
    print("->", out)


if __name__ == "__main__":
    main()
