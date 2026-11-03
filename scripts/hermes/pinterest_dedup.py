#!/usr/bin/env python3
"""
Pinterest board dedup HARD GATE for the DAILY Pinterest Posts cron.

Two modes:

1) PRE-WRITE (no args): fetch already-pinned titles from all 7 PhantomByteAI
   boards via RSS and print them so the agent has context before writing.
   (Kept for backward compat / prompt injection.)

2) POST-WRITE ENFORCEMENT (arg = path to the planned posts file):
   Read the agent's just-written posts file, fetch the live already-pinned
   titles from all 7 boards, and HARD-REMOVE any planned post whose story
   matches an already-pinned story. Rewrites the file in place with only the
   non-duplicate posts. This is the deterministic gate — it does NOT rely on
   the model's judgment. The email step then sends whatever survives.

Why RSS instead of scrapling/browser:
  - Board page HTML only embeds image metadata (id, image_signature, images)
    in its `pins` object. Pin titles/descriptions load lazily and are NOT in
    the initial HTML, so the old scrapling regex returns 0.
  - RSS returns the ~25 most recent pin titles per board in ~0.4s each with a
    plain urllib GET. No StealthyFetcher, no headless browser, no token cost.

Usage:
    python3 ~/.hermes/scripts/pinterest_dedup.py                 # pre-write context
    python3 ~/.hermes/scripts/pinterest_dedup.py /path/posts.txt  # hard gate
"""

import html
import os
import re
import sys
import urllib.request

PROFILE = "PhantomByteAI"

# slug -> human label (must match the board names in the cron prompt)
BOARDS = {
    "ai-news-machine-learning-emerging-tech": "Main AI News",
    "ai-agents-automation-guide": "AI Agents",
    "ai-tools-for-business-productivity-2026": "AI Tools",
    "ai-for-developers-programming-ai-tutorials": "AI for Developers",
    "agent-security-prompt-injection-sandboxing": "Agent Security",
    "robotics-physical-ai-humanoid-robots": "Robotics & Physical AI",
    "quantum-computing-explained": "Quantum Computing",
}

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# Distinctive entity tokens that identify a story. A planned post is a
# duplicate only if it shares a DISTINCTIVE signature (specific product,
# model, event, person, or company+event) with an already-pinned title.
# Bare company names (nvidia, openai, meta, google, anthropic, etc.) and
# generic topic words are deliberately EXCLUDED: they appear across many
# different stories, so matching on them false-positives and nukes valid
# new posts. Keys are normalized the same way as the text (lowercase,
# punctuation stripped) so hyphenated/dotted keys like "glm-5.3" match.
STORY_KEYS = [
    # NVIDIA / hardware (specific products only, not bare "nvidia")
    "dgx spark", "gb10", "grace blackwell", "vera rubin",
    # robots (specific, not bare "humanoid")
    "unitree", "figure", "tesla optimus", "optimus",
    "collision avoidance", "force limiting", "behavioral constraints",
    # models (specific)
    "gpt-5.6", "gpt-5.5", "claude opus", "claude fable", "claude code",
    "kimi k3", "muse glimmer", "muse code", "muse spark", "glm-5.3",
    "frontiercode", "frontier code", "qwen3.6", "nemotron", "mythos 5",
    # companies / products (specific)
    "litellm", "scaled cognition", "personal computer", "copilot", "cursor",
    "openrouter", "mechanical turk", "superblocks", "designarena", "lovable",
    "waze", "terraform", "veeam", "zoom", "devin", "shopify",
    "model context protocol", "world ai cooperation", "shanghai",
    "xi jinping", "jensen huang", "vint cerf", "dawn song", "gartner",
    "samsung", "sk hynix", "hbm", "south korea", "ramageddon",
    # events / attacks (specific)
    "supply chain attack", "cloud keys", "ssh keys", "kubernetes",
    "open internet", "spear-phishing", "fake identities", "annotation flaw",
    "malicious code", "insider risk", "keystroke monitoring",
    "medical leave", "parental leave", "disability leave", "active directory",
    "power shell", "reward hacking", "coast runners", "behavioral state decay",
    "memory coach", "action preflight", "notebook memory", "sliding context",
    "self-replicating", "turf war",
]


def normalize(text):
    """Lowercase, strip punctuation/whitespace, collapse spaces."""
    t = text.lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def fetch_board_titles(slug):
    """Return the list of pin titles already on a board via its RSS feed."""
    url = f"https://www.pinterest.com/{PROFILE}/{slug}.rss"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8", "ignore")
    # First <title> is the board name itself; the rest are pin titles.
    titles = re.findall(r"<title>(.*?)</title>", body, re.S)
    return [html.unescape(t.strip()) for t in titles[1:] if t.strip()]


def story_matches(planned_text, pinned_titles):
    """Return True if planned_text matches any already-pinned title."""
    norm = normalize(planned_text)
    for pinned in pinned_titles:
        pnorm = normalize(pinned)
        # Exact-ish match on the full normalized string.
        if norm and (norm in pnorm or pnorm in norm):
            return True
        # Shared distinctive entity token => same story.
        # Keys are normalized identically to the text so hyphenated/dotted
        # keys (e.g. "glm-5.3" -> "glm 5 3") match the normalized text.
        for key in STORY_KEYS:
            knorm = normalize(key)
            if knorm and knorm in norm and knorm in pnorm:
                return True
    return False


def split_posts(text):
    """
    Split a posts file into individual post blocks.

    Handles the two formats the cron has produced:
      - "[BOARD] - Title\nDescription..."  (bracket-prefixed)
      - "[N] BOARD: Title\nDescription..."  (numbered)
    A new post starts at a line beginning with '[' that contains a board
    label or a number followed by 'BOARD'.
    """
    lines = text.splitlines()
    posts = []
    cur = []
    board_labels = [b.lower() for b in BOARDS.values()]

    def is_post_start(line):
        s = line.strip().lower()
        if not s.startswith("["):
            return False
        # "[Board] - Title" or "[1] BOARD: Title"
        inner = s.strip("[]").split("]")[0]
        if any(b in inner for b in board_labels):
            return True
        if re.match(r"^\d+\s*board", inner):
            return True
        return False

    for line in lines:
        if is_post_start(line) and cur:
            posts.append("\n".join(cur))
            cur = [line]
        else:
            cur.append(line)
    if cur:
        posts.append("\n".join(cur))
    return posts


def main():
    # ---- PRE-WRITE MODE: print already-pinned titles for agent context ----
    if len(sys.argv) < 2:
        total = 0
        for slug, label in BOARDS.items():
            try:
                titles = fetch_board_titles(slug)
            except Exception as e:
                print(f"[{label}] ERROR: {type(e).__name__}: {e}", file=sys.stderr)
                continue
            total += len(titles)
            for t in titles:
                print(f"[{label}] {t}")
        print(f"\n# {total} already-pinned titles across {len(BOARDS)} boards.",
              file=sys.stderr)
        return

    # ---- POST-WRITE HARD GATE: remove duplicates from the posts file ----
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"ERROR: posts file not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    # Gather all already-pinned titles across all boards.
    pinned = []
    for slug, label in BOARDS.items():
        try:
            pinned.extend(fetch_board_titles(slug))
        except Exception as e:
            print(f"[{label}] ERROR: {type(e).__name__}: {e}", file=sys.stderr)

    posts = split_posts(text)
    kept = []
    removed = []
    for post in posts:
        if story_matches(post, pinned):
            removed.append(post)
        else:
            kept.append(post)

    if removed:
        # Rewrite the file with only the kept posts.
        new_text = "\n\n".join(kept).strip() + "\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"DEDUP: removed {len(removed)} duplicate post(s) from "
              f"{os.path.basename(filepath)}. {len(kept)} kept.")
        for r in removed:
            first = r.splitlines()[0] if r.splitlines() else r
            print(f"  REMOVED: {first[:100]}")
    else:
        print(f"DEDUP: no duplicates found. {len(posts)} post(s) kept in "
              f"{os.path.basename(filepath)}.")

    # Always report how many pinned titles were checked.
    print(f"Checked against {len(pinned)} already-pinned titles across "
          f"{len(BOARDS)} boards.", file=sys.stderr)


if __name__ == "__main__":
    main()
