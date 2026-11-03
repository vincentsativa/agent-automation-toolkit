#!/usr/bin/env python3
"""
build-guide.py — Generate a new guide page from the template or fetch a live URL.

Usage:
    python build-guide.py --name "Sovereign AI Stack" --slug sovereign-ai-stack ^
        --content "C:\path\to\content.txt" --image "C:\path\to\cover.png" ^
        --price "0.99" --original-price "5" --gumroad "Sovereign-AI-Stack"

    # Or fetch a live page as template:
    python build-guide.py --url "https://vincentsativa.com/hermes-guide.html" ^
        --name "My Guide" --slug my-guide --content ...

All text content is read from the --content file.
The content file should have labeled sections matching the template slots.
Google Analytics (G-PDQCZE09E4) is automatically injected into every page.
Em dashes are automatically removed."""

import argparse
import os
import re
import shutil

# Template sections that get replaced
SECTIONS = {
    "TITLE": "TITLE_TAG",           # <title> tag
    "META_DESC": "META_DESCRIPTION", # <meta name="description">
    "BADGE": "BADGE_TEXT",           # .badge span
    "H1_BEFORE": "H1_SPAN_BEFORE",   # text before <span>
    "H1_SPAN": "H1_SPAN_TEXT",       # text inside <span>
    "H1_AFTER": "H1_SPAN_AFTER",     # text after </span>
    "SUBTITLE": "SUBTITLE_TEXT",     # .hero-subtitle
    "CTA_HEADLINE": "CTA_HEADLINE",  # CTA h2
    "CTA_BODY": "CTA_BODY_TEXT",     # CTA paragraph
    "PRICE": "PRICE_VALUE",          # price-tag
    "ORIGINAL_PRICE": "ORIGINAL_PRICE",
    "GUMROAD_SLUG": "GUMROAD_SLUG",
    "BENEFIT_1_ICON": "BENEFIT_1_ICON",
    "BENEFIT_1_TITLE": "BENEFIT_1_TITLE",
    "BENEFIT_1_DESC": "BENEFIT_1_DESC",
    "BENEFIT_2_ICON": "BENEFIT_2_ICON",
    "BENEFIT_2_TITLE": "BENEFIT_2_TITLE",
    "BENEFIT_2_DESC": "BENEFIT_2_DESC",
    "BENEFIT_3_ICON": "BENEFIT_3_ICON",
    "BENEFIT_3_TITLE": "BENEFIT_3_TITLE",
    "BENEFIT_3_DESC": "BENEFIT_3_DESC",
    "BENEFIT_4_ICON": "BENEFIT_4_ICON",
    "BENEFIT_4_TITLE": "BENEFIT_4_TITLE",
    "BENEFIT_4_DESC": "BENEFIT_4_DESC",
    "PERSONA_1_ICON": "PERSONA_1_ICON",
    "PERSONA_1_TITLE": "PERSONA_1_TITLE",
    "PERSONA_1_DESC": "PERSONA_1_DESC",
    "PERSONA_2_ICON": "PERSONA_2_ICON",
    "PERSONA_2_TITLE": "PERSONA_2_TITLE",
    "PERSONA_2_DESC": "PERSONA_2_DESC",
    "PERSONA_3_ICON": "PERSONA_3_ICON",
    "PERSONA_3_TITLE": "PERSONA_3_TITLE",
    "PERSONA_3_DESC": "PERSONA_3_DESC",
    "PERSONA_4_ICON": "PERSONA_4_ICON",
    "PERSONA_4_TITLE": "PERSONA_4_TITLE",
    "PERSONA_4_DESC": "PERSONA_4_DESC",
}


def parse_content_file(filepath):
    """Parse a content file into labeled sections.
    
    Format:
        [TITLE]
        The Guide Title | Tagline
        [SUBTITLE]
        Description text here...
        [BENEFIT_1_TITLE]
        Benefit name
        [BENEFIT_1_DESC]
        Description
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    sections = {}
    # Simple section parser: [SECTION_NAME]\ncontent\n
    pattern = re.compile(r'^\s*\[([A-Z0-9_]+)\]\s*$(.*?)(?=^\s*\[[A-Z0-9_]+\]\s*$|\Z)', 
                         re.MULTILINE | re.DOTALL)
    
    for match in pattern.finditer(text):
        key = match.group(1).strip()
        value = match.group(2).strip()
        sections[key] = value
    
    return sections


def build_html(template_path, sections, image_path, gumroad_slug):
    """Build the output HTML by replacing template placeholders."""
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Replace image src
    image_filename = os.path.basename(image_path)
    image_filename_clean = re.sub(r'[^a-zA-Z0-9._-]', '-', image_filename)
    html = re.sub(
        r'src="[^"]*cover\.png"',
        f'src="assets/{image_filename_clean}"',
        html
    )
    
    # Replace gumroad link
    html = re.sub(
        r'https://phantombyteai\.gumroad\.com/l/[^"\']+',
        f'https://phantombyteai.gumroad.com/l/{gumroad_slug}',
        html
    )
    
    # Replace title
    if 'TITLE' in sections:
        html = re.sub(
            r'<title>[^<]+</title>',
            f'<title>{sections["TITLE"]}</title>',
            html
        )
        html = re.sub(
            r'<meta name="description" content="[^"]*">',
            f'<meta name="description" content="{sections.get("META_DESC", sections["TITLE"])}">',
            html
        )
    
    # Replace badge
    if 'BADGE' in sections:
        html = re.sub(
            r'(<div class="badge">)[^<]+(</div>)',
            f'\\g<1>{sections["BADGE"]}\\g<2>',
            html
        )
    
    # Replace H1
    h1_before = sections.get('H1_BEFORE', 'The')
    h1_span = sections.get('H1_SPAN', 'Guide')
    h1_after = sections.get('H1_AFTER', 'Guide')
    
    html = re.sub(
        r'(<h1>)The (<span>)[^<]+(</span>)[^<]+(</h1>)',
        f'\\g<1>{h1_before} \\g<2>{h1_span}\\g<3> {h1_after}\\g<4>',
        html
    )
    
    # Replace subtitle
    if 'SUBTITLE' in sections:
        html = re.sub(
            r'(<p class="hero-subtitle">)[^<]+(</p>)',
            f'\\g<1>{sections["SUBTITLE"]}\\g<2>',
            html
        )
    
    # Replace CTA section
    if 'CTA_HEADLINE' in sections:
        html = re.sub(
            r'(<h2>)[^<]+(</h2>\s*<p>)',
            f'\\g<1>{sections["CTA_HEADLINE"]}\\g<2>',
            html
        )
    
    if 'CTA_BODY' in sections:
        html = re.sub(
            r'(<h2>[^<]+</h2>\s*<p>)[^<]+(</p>)',
            f'\\g<1>{sections["CTA_BODY"]}\\g<2>',
            html
        )
    
    # Replace price
    if 'PRICE' in sections:
        html = re.sub(
            r'(<div class="price-tag">)\$[0-9.]+',
            f'\\g<1>${sections["PRICE"]}',
            html
        )
    
    if 'ORIGINAL_PRICE' in sections:
        html = re.sub(
            r'<span class="original">\$[0-9.]+</span>',
            f'<span class="original">${sections["ORIGINAL_PRICE"]}</span>',
            html
        )
    
    # Replace benefits grid (4 items)
    for i in range(1, 5):
        icon = sections.get(f'BENEFIT_{i}_ICON', '')
        title = sections.get(f'BENEFIT_{i}_TITLE', '')
        desc = sections.get(f'BENEFIT_{i}_DESC', '')
        
        if title:
            # Find the i-th benefit-item and replace
            items = list(re.finditer(
                r'(<div class="benefit-item">\s*<div class="benefit-icon">)[^<]*(</div>\s*<h4>)[^<]*(</h4>\s*<p>)[^<]*(</p>\s*</div>)',
                html
            ))
            if i <= len(items):
                m = items[i-1]
                old = m.group(0)
                new = f'{m.group(1)}{icon}{m.group(2)}{title}{m.group(3)}{desc}{m.group(4)}'
                html = html.replace(old, new, 1)
    
    # Replace persona cards (4 items)
    for i in range(1, 5):
        icon = sections.get(f'PERSONA_{i}_ICON', '')
        title = sections.get(f'PERSONA_{i}_TITLE', '')
        desc = sections.get(f'PERSONA_{i}_DESC', '')
        
        if title:
            items = list(re.finditer(
                r'(<div class="persona-card">\s*<h4>)[^<]*(</h4>\s*<p>)[^<]*(</p>\s*</div>)',
                html
            ))
            if i <= len(items):
                m = items[i-1]
                # Handle icon + title in h4
                h4_content = f'{icon} {title}' if icon else title
                old = m.group(0)
                new = f'{m.group(1)}{h4_content}{m.group(2)}{desc}{m.group(3)}'
                html = html.replace(old, new, 1)
    
    # Replace "For Whom" subtitle
    if 'FOR_WHOM_SUBTITLE' in sections:
        html = re.sub(
            r'(<p class="subtitle">)[^<]+(</p>\s*<div class="persona-grid">)',
            f'\\g<1>{sections["FOR_WHOM_SUBTITLE"]}\\g<2>',
            html
        )
    
    # Remove any em dashes
    html = html.replace('\u2014', ' - ')
    
    # Inject Google Analytics (G-PDQCZE09E4) before <!-- Robots -->
    ga_snippet = '''    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-PDQCZE09E4"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-PDQCZE09E4');
    </script>

    <!-- Robots -->'''
    html = html.replace('<!-- Robots -->', ga_snippet)
    
    return html


def main():
    parser = argparse.ArgumentParser(description='Build a guide page from template')
    parser.add_argument('--name', required=True, help='Guide name (for filename)')
    parser.add_argument('--slug', required=True, help='URL slug')
    parser.add_argument('--content', required=True, help='Path to content file with [SECTION] labels')
    parser.add_argument('--image', required=True, help='Path to cover image')
    parser.add_argument('--gumroad', default='', help='Gumroad product slug')
    parser.add_argument('--price', default='0.99', help='Price')
    parser.add_argument('--original-price', default='5', help='Original/strikethrough price')
    parser.add_argument('--output-dir', default=None, help='Output directory (default: desktop/guide folder)')
    parser.add_argument('--repo-dir', default='~\\workspace\\funnel-pages', 
                        help='Repo directory for deployment')
    
    args = parser.parse_args()
    
    # Paths
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(skill_dir, 'template.html')
    
    if not os.path.exists(template_path):
        print(f"ERROR: Template not found at {template_path}")
        return 1
    
    if not os.path.exists(args.content):
        print(f"ERROR: Content file not found at {args.content}")
        return 1
    
    if not os.path.exists(args.image):
        print(f"ERROR: Image not found at {args.image}")
        return 1
    
    # Parse content
    sections = parse_content_file(args.content)
    
    # Add price/gumroad if not in content file
    if 'PRICE' not in sections:
        sections['PRICE'] = args.price
    if 'ORIGINAL_PRICE' not in sections:
        sections['ORIGINAL_PRICE'] = args.original_price
    
    gumroad = args.gumroad or args.slug
    
    # Build HTML
    html = build_html(template_path, sections, args.image, gumroad)
    
    # Determine output path
    if args.output_dir:
        output_dir = args.output_dir
    else:
        # Desktop folder named after guide
        desktop = os.path.expanduser('~/Desktop')
        output_dir = os.path.join(desktop, args.name.upper().replace(' ', '_'))
        os.makedirs(output_dir, exist_ok=True)
    
    output_html = os.path.join(output_dir, f'{args.slug}.html')
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML built: {output_html}")
    
    # Copy image to repo
    image_filename = re.sub(r'[^a-zA-Z0-9._-]', '-', os.path.basename(args.image))
    repo_image = os.path.join(args.repo_dir, 'assets', image_filename)
    shutil.copy2(args.image, repo_image)
    print(f"✅ Image copied: {repo_image}")
    
    # Copy HTML to repo
    repo_html = os.path.join(args.repo_dir, f'{args.slug}.html')
    shutil.copy2(output_html, repo_html)
    print(f"✅ HTML copied: {repo_html}")
    
    # Git commands
    print(f"\n⚡ Deploy commands (run these):")
    print(f"  cd {args.repo_dir}")
    print(f'  git add {args.slug}.html assets/{image_filename}')
    print(f'  git commit -m "feat: add {args.name} guide page"')
    print(f"  git push")
    print(f"\n🌐 Live at: https://vincentsativa.com/{args.slug}.html")
    
    return 0


if __name__ == '__main__':
    exit(main())
