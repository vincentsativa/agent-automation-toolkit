#!/usr/bin/env python3
"""Mechanical spell check for a document written for Vinny.

Run it on THE FILE YOU ARE ABOUT TO DELIVER, one file at a time. Never point it
at a directory of data files: pyspellchecker stalls on lead lists and scan dumps
and will blow a tool timeout before it prints anything useful.

Usage:
    python3 spellcheck.py <file> [<file> ...]

Needs pyspellchecker. When the host has no checker, build the interpreter in a
fresh scratch dir first and call it from there:

    SCRATCH=$(mktemp -d /tmp/hermes-spell-XXXXXX)
    python3 -m venv "$SCRATCH/venv"
    "$SCRATCH/venv/bin/pip" -q install pyspellchecker
    "$SCRATCH/venv/bin/python" spellcheck.py <file>

Reading the output: a flagged word that is a name, brand, acronym, or product
term is NOT an error. Fix the ordinary words, then verify every proper noun
against the source by hand. A checker's suggestion for a proper noun is always
wrong, and a checker will not catch a name spelled as the wrong real word.
"""

import re
import sys

from spellchecker import SpellChecker

# Words the checker calls wrong and that are right: brands, products, acronyms,
# domain terms, and code identifiers. Extend this list, never edit the copy to
# satisfy the checker.
WHITELIST = set("""
addr ai api arc bimi canspam cli css csv db dkim dmarc dns ehlo esps gdpr gmail
helo html https imap ionos ip ips js json llm lookups mx openleads optin optout
outlook pdf php pmta ptr rua ruf smtp spf ssl stdout sys tcpa tls txt ui uri url
ux vinny yahoo phantombyte phantom-byte
""".split())

MAX_TOKENS = 6000


def words_in(text):
    tokens = set()
    for word in re.findall(r"[A-Za-z][A-Za-z'\-]*", text)[:MAX_TOKENS]:
        for part in word.replace("'", " ").split("-"):
            if len(part) >= 4:
                tokens.add(part.lower())
    return tokens - WHITELIST


def main(paths):
    spell = SpellChecker()
    if not paths:
        print("give at least one file, e.g. spellcheck.py report.txt")
        return 2
    for path in paths:
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError as exc:
            print("cannot read %s: %s" % (path, exc))
            continue
        tokens = words_in(text)
        unknown = sorted(spell.unknown(tokens))
        print("%s: %d tokens checked, %d flagged" % (path, len(tokens), len(unknown)))
        for word in unknown:
            print("    %s -> %s" % (word, spell.correction(word)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
