#!/usr/bin/env python3
"""
Blogwatcher Article Fetcher
Query articles by date from blogwatcher-cli SQLite database.

Usage:
    python blogwatcher-fetch.py                    # Today's articles
    python blogwatcher-fetch.py 2026-04-17         # Specific date
    python blogwatcher-fetch.py 2026-04-17 --save  # Save to file
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".blogwatcher-cli" / "blogwatcher-cli.db"
OUTPUT_DIR = Path.home() / ".blogwatcher-cli" / "exports"

def fetch_articles(date_str=None, save=False):
    # Default to today if no date provided
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Validate date format
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print(f"Error: Invalid date format. Use YYYY-MM-DD (e.g., 2026-04-17)")
        sys.exit(1)
    
    # Check database exists
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        print("Run 'blogwatcher-cli scan' first to create the database.")
        sys.exit(1)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query articles for the specified date
    cursor.execute("""
        SELECT a.title, a.url, a.published_date, a.is_read, b.name as blog_name
        FROM articles a
        JOIN blogs b ON a.blog_id = b.id
        WHERE DATE(a.published_date) = ?
        ORDER BY b.name, a.published_date DESC
    """, (date_str,))
    
    articles = cursor.fetchall()
    conn.close()
    
    # Format output
    output_lines = []
    output_lines.append(f"BLOGWATCHER ARTICLES - {date_str}")
    output_lines.append("=" * 60)
    output_lines.append(f"Total articles: {len(articles)}\n")
    
    if not articles:
        output_lines.append("No articles found for this date.")
    else:
        current_blog = None
        for title, url, published, is_read, blog in articles:
            if blog != current_blog:
                current_blog = blog
                output_lines.append(f"\n📰 {blog}")
                output_lines.append("-" * 40)
            
            status = "✓" if is_read else "●"
            output_lines.append(f"  [{status}] {title}")
            output_lines.append(f"      {url}")
    
    output_lines.append("\n" + "=" * 60)
    
    output_text = "\n".join(output_lines)
    print(output_text)
    
    # Save to file if requested
    if save:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_file = OUTPUT_DIR / f"articles-{date_str}.txt"
        output_file.write_text(output_text)
        print(f"\nSaved to: {output_file}")
    
    return len(articles)

if __name__ == "__main__":
    # Parse arguments
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    save_flag = "--save" in sys.argv
    
    fetch_articles(date_arg, save=save_flag)
