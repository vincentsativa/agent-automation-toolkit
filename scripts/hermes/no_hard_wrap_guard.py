#!/usr/bin/env python3
"""pre_tool_call shell hook: strip hard-wrapping from delivered .txt/.md files.

WHY
---
Article 14 of the constitution bans hard-wrapping text in anything Vinny reads.
It has been broken repeatedly anyway, because enforcement lived only in prose
that a cron run may not load. The measured cause: cron sessions get a system
prompt with NO Article 14 text in it (verified against state.db: only 29 of
835 stored prompts carry it, and every one of those is interactive). A cron
agent that only sees "view the skill vinny-constitution" as a pointer writes a
column-wrapped report, and Vinny has to catch it.

Rule in prose is not enforcement. This hook is enforcement: it rewrites the
argument BEFORE the file is written, so a wrapped report cannot land no matter
which model, skill, or cron run produced it.

WHAT IT DOES
------------
Matcher scoped to write_file. If the target path ends in .txt or .md, every
line that is a WRAPPED CONTINUATION of the line above is joined onto it:

  * previous line does not end a sentence (no . : " ' ! ? | ) ]) and next line
    starts lowercase or an opening quote  -> join with a space
  * previous line ends in a hyphen and next starts lowercase -> join, drop hyphen
  * previous line is a bullet body, next line is indented >= 4 spaces and starts
    uppercase (a wrapped bullet continuation) -> join with a space

Never touches: .json/.yaml/.py/.html/.csv or any other extension, blank lines,
headings, separators, code fences, indented code blocks, table rows, or lines
that already end a sentence. The rewrite is returned as a Hermes "modify"
directive, so the file on disk is written once, already unwrapped.

FAILURE MODE
------------
fail_closed: false. Any error, timeout, or non-JSON condition leaves the write
untouched. A broken guard must never brick a file write.

Wire (agent/shell_hooks.py::_serialize_payload):
  stdin  {"hook_event_name": "pre_tool_call", "tool_name": "write_file",
          "tool_input": {"path": "...", "content": "..."}}
  stdout {"action": "modify", "args": {"path": "...", "content": "..."}}
"""
import json
import re
import sys

TEXT_EXTS = (".txt", ".md", ".markdown")
SENTENCE_END = (".", ":", '"', "'", "!", "?", "|", ")", "]", "—", "=")
LOWER_OR_QUOTE = re.compile(r'^[a-z(\u201c"]')
LOWER_ONLY = re.compile(r"^[a-z]")
STRUCTURAL = ("#", "-", "*", ">", "=", "`", "+", "|", "\\", "/", ":", "0")

MAX_JOINS = 4000


def _is_structural(line, indent):
    """Lines the hook must never join: headings, rules, fences, table rows, code."""
    s = line.strip()
    if not s:
        return True
    if indent >= 4:
        return True
    if s.startswith(STRUCTURAL):
        return True
    if re.match(r"^\d+[.)]\s", s):  # numbered list item
        return True
    if s.startswith("```"):
        return True
    return False


def _joins(prev_raw, cur_raw):
    """True when cur is a wrapped continuation of prev."""
    p = prev_raw.rstrip()
    c = cur_raw.strip()
    if not p or not c:
        return False
    if len(p) < 40:  # too short to be a wrapped body line
        return False
    c_indent = len(cur_raw) - len(cur_raw.lstrip())
    if _is_structural(cur_raw, c_indent):
        return False
    if p.endswith("-") and LOWER_ONLY.match(c):
        return True
    # A list that continues mid-item: "A, B, C," / "D, E" — the case that reached Vinny.
    if p.endswith(",") and re.match(r"^[A-Za-z0-9(\u201c\"]", c):
        return True
    if p.endswith(SENTENCE_END):
        return False
    if LOWER_OR_QUOTE.match(c):
        return True
    if c_indent >= 4 and c[0].isupper():
        return True
    return False


def unwrap(text):
    out = []
    joins = 0
    for raw in text.split("\n"):
        if out and joins < MAX_JOINS and _joins(out[-1], raw):
            p = out[-1].rstrip()
            c = raw.strip()
            if p.endswith("-") and LOWER_ONLY.match(c):
                out[-1] = p[:-1] + c
            else:
                out[-1] = p + " " + c
            joins += 1
            continue
        out.append(raw)
    return "\n".join(out), joins


def _wrap_band(text):
    return sum(1 for line in text.split("\n") if 60 < len(line) < 86)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    if payload.get("hook_event_name") != "pre_tool_call":
        return 0
    if payload.get("tool_name") != "write_file":
        return 0

    args = payload.get("tool_input")
    if not isinstance(args, dict):
        args = payload.get("args")
    if not isinstance(args, dict):
        return 0

    path = args.get("path") or args.get("file_path")
    content = args.get("content")
    if not isinstance(path, str) or not isinstance(content, str):
        return 0
    if not path.lower().endswith(TEXT_EXTS):
        return 0

    # No width gate: the wrapped lines that actually reached Vinny ran ~94-101 chars
    # (a sources block wrapped at a wide column), so a 60-86 "band" test missed them.
    # The join predicate is the gate — it only fires on a true continuation.
    fixed, joins = unwrap(content)
    if joins <= 0 or fixed == content:
        return 0

    new_args = dict(args)
    new_args["path"] = path
    new_args["content"] = fixed
    if "file_path" in args and "path" not in args:
        new_args["file_path"] = path
    sys.stderr.write(
        "no-hard-wrap guard: joined %d wrapped line(s) in %s\n" % (joins, path)
    )
    print(json.dumps({"action": "modify", "args": new_args}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
