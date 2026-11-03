# Parsing blogwatcher-cli `--all` output with Python

When extracting structured data from `blogwatcher-cli articles --all`, the output is plain text with indented blocks. Two things trip up naive parsers:

## 1. Leading whitespace on `[ID]` lines
The `[ID] [new] HEADLINE` lines are indented with 2 leading spaces. A regex like `^\[(\d+)\]` fails silently — use `^\s*\[(\d+)\]` or skip regex entirely and scan for `Published:` lines.

## 2. Better pattern: filter by `Published:` line, walk backwards
Instead of trying to parse from the `[ID]` header line, scan for lines containing the target date, then walk backward to collect headline, blog, URL, and categories.

## Working extractor (Python)

```python
import subprocess, re
from datetime import datetime

def get_today_articles(date_str="2026-06-20"):
    result = subprocess.run(
        ['~/blogwatcher-cli', 'articles', '--all'],
        capture_output=True, text=True, timeout=60
    )
    lines = result.stdout.split('\n')
    articles = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^\s*\[(\d+)\]\s+\[(\w+)\]\s+(.+)', line)
        if m:
            art_id, status, headline = m.group(1), m.group(2), m.group(3)
            blog_name = url = pub_date = categories = ""
            j = i + 1
            while j < len(lines) and not re.match(r'^\s*\[\d+\]\s+\[', lines[j]):
                jl = lines[j].strip()
                if jl.startswith('Blog:'):
                    blog_name = jl.replace('Blog:', '').strip()
                elif jl.startswith('URL:'):
                    url = jl.replace('URL:', '').strip()
                elif jl.startswith('Published:'):
                    pub_date = jl.replace('Published:', '').strip()
                elif jl.startswith('Categories:'):
                    categories = jl.replace('Categories:', '').strip()
                j += 1
            if pub_date == date_str:
                articles.append({
                    'id': art_id, 'status': status, 'headline': headline,
                    'blog': blog_name, 'url': url, 'date': pub_date,
                    'categories': categories
                })
            i = j
        else:
            i += 1
    return articles
```

## Notes
- Timeout of `60` seconds is sufficient for DBs with ~2000 articles.
- For DBs with 15K+ articles, the `--all` output can exceed 600K chars. Use `grep` pre-filtering for just the target date to reduce capture overhead, or pipe through `head` if you only need the newest N.
- Per-blog `--blog "Name"` calls are useful as a fallback when `--all` is truncated, but they return ALL unread articles for that source (not date-filtered). Always check `Published:` dates before including them in a daily report.
