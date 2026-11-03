#!/usr/bin/env python3
"""Marker-table verification for an agent change-brief sync.

One row per brief item, counted in both trees, so "everything is applied" is a
claim backed by output instead of memory.

Usage:
    python3 verify_two_trees.py --items items.txt

items.txt lines look like:
    research/ai-model-vetting/SKILL.md|re-post-train
    creative/writing-style/SKILL.md|LAST-RESORT FALLBACK

Paths are relative to <tree>/skills. Blank lines and # comments are ignored.
Exit code is 1 when any item is missing from either tree.
"""
import argparse
import os
import sys

WSL = os.path.expanduser('~/.hermes')
WIN = '/mnt/c/Users/<user>/AppData/Local/hermes'


def count(root, rel, phrase):
    path = os.path.join(root, rel)
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8', errors='surrogateescape') as fh:
        return fh.read().count(phrase)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--items', required=True, help='file of relpath|phrase lines')
    ap.add_argument('--wsl', default=WSL)
    ap.add_argument('--win', default=WIN)
    args = ap.parse_args()

    missing = 0
    print('%-58s %5s %5s  %s' % ('item', 'WSL', 'WIN', 'verdict'))
    for line in open(args.items, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or '|' not in line:
            continue
        rel, phrase = (part.strip() for part in line.split('|', 1))
        rel = os.path.join('skills', rel)
        wsl = count(args.wsl, rel, phrase)
        win = count(args.win, rel, phrase)
        verdict = 'OK' if (wsl and win) else 'MISSING'
        if verdict != 'OK':
            missing += 1
        print('%-58s %5s %5s  %s' % (rel.replace('skills' + os.sep, ''), wsl, win, verdict))
    print('\n%d item(s) missing' % missing)
    sys.exit(1 if missing else 0)


if __name__ == '__main__':
    main()
