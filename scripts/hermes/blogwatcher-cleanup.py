#!/usr/bin/env python3
"""
Blogwatcher cleanup script - deletes articles older than 7 days
Usage: ./blogwatcher-cleanup.py [days_to_keep]
"""

import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

def main():
    days_to_keep = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    
    db_path = Path.home() / ".blogwatcher-cli" / "blogwatcher-cli.db"
    blogwatcher_cli = Path.home() / "blogwatcher-cli"
    
    print("=== Blogwatcher Cleanup ===")
    print(f"Database: {db_path}")
    print(f"Keeping articles from last {days_to_keep} days")
    print()
    
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        sys.exit(1)
    
    # Count articles before cleanup
    import subprocess
    try:
        result = subprocess.run([str(blogwatcher_cli), "articles", "--all"], 
                              capture_output=True, text=True)
        before = result.stdout.count("[")
    except:
        before = 0
    print(f"Articles before cleanup: {before}")
    
    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    cutoff_str = cutoff_date.strftime("%Y-%m-%d")
    print(f"Cutoff date: {cutoff_str}")
    print()
    
    # Connect to database and delete old articles
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Delete articles older than cutoff
    cursor.execute("DELETE FROM articles WHERE published_date < ?", (cutoff_str,))
    deleted = cursor.rowcount
    
    conn.commit()
    
    # Vacuum to reclaim space (needs separate connection)
    conn.close()
    conn = sqlite3.connect(str(db_path))
    conn.execute("VACUUM;")
    
    conn.commit()
    conn.close()
    
    # Count articles after cleanup
    try:
        result = subprocess.run([str(blogwatcher_cli), "articles", "--all"], 
                              capture_output=True, text=True)
        after = result.stdout.count("[")
    except:
        after = 0
    
    print()
    print(f"Articles after cleanup: {after}")
    print(f"Deleted: {deleted} articles older than {cutoff_str}")
    print("=== Cleanup Complete ===")

if __name__ == "__main__":
    main()
