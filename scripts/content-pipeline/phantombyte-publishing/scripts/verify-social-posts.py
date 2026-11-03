#!/usr/bin/env python
"""
Ad-hoc verification script for PhantomByte social media posts.
Run against the saved report file to catch:
  - X posts exceeding 190 characters
  - Character count markers that don't match actual lengths
  - Em dashes (forbidden in all PhantomByte content)
  - Missing Pinterest sections

Usage:
  python scripts/verify-social-posts.py <path-to-report-file>

Exit code: 0 = all checks pass, 1 = errors found
"""
import re
import os
import sys

def verify_report(report_path):
    if not os.path.exists(report_path):
        print(f"ERROR: File not found: {report_path}")
        return False

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []
    warnings = []

    # 1. No em dashes
    em_dash_count = content.count('\u2014') + content.count('\u2013')
    if em_dash_count > 0:
        errors.append(f"Found {em_dash_count} em/en dashes in document (forbidden)")

    # 2. Extract and validate X posts
    # Supports two formats:
    #   Format A: "POST 1 (189 chars):\n<post text>"
    #   Format B: "POST 1: ...\n<post text>\n(189 chars)"
    post_texts = []
    char_markers = re.findall(r'\((\d+) chars\)', content)

    # Try Format A first: POST N (NNN chars):\n<text>
    format_a = re.findall(
        r'POST \d+ \((\d+) chars\):\n(.+?)(?=\nPOST \d|\Z)',
        content,
        re.DOTALL
    )
    if len(format_a) == 5:
        post_texts = [t.strip() for _, t in format_a]
        char_markers = [int(c) for c, _ in format_a]
    else:
        # Fallback to Format B: POST N: ...\n<text>\n(NNN chars)
        format_b = re.findall(
            r'POST \d: .+?\n(.+?)\n\(\d+ chars\)',
            content,
            re.DOTALL
        )
        post_texts = [t.strip() for t in format_b]

    if len(post_texts) != 5:
        errors.append(f"Expected 5 X posts, found {len(post_texts)}")
    else:
        for i, post_text in enumerate(post_texts):
            actual_len = len(post_text)
            claimed = int(char_markers[i]) if i < len(char_markers) else actual_len
            if actual_len > 190:
                errors.append(f"Post {i+1}: {actual_len} chars exceeds 190 limit (claimed {claimed})")
            elif actual_len != claimed:
                warnings.append(f"Post {i+1}: claimed {claimed} chars but actual is {actual_len}")

    # 3. Pinterest sections exist
    pin_count = len(re.findall(r'^PIN \d:', content, re.MULTILINE))
    if pin_count != 5:
        errors.append(f"Expected 5 Pinterest pins, found {pin_count}")

    # 4. No bullet-point lists inside body paragraphs
    if re.search(r'^[*-]\s', content, re.MULTILINE):
        warnings.append("Found bullet-point list markers in document")

    # Summary
    if errors:
        print(f"VERIFICATION FAILED: {len(errors)} error(s)")
        for e in errors:
            print(f"  ERROR: {e}")
        return False
    else:
        print("VERIFICATION PASSED: All checks OK")
        if warnings:
            for w in warnings:
                print(f"  WARNING: {w}")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python verify-social-posts.py <path-to-report-file>")
        sys.exit(1)
    success = verify_report(sys.argv[1])
    sys.exit(0 if success else 1)
