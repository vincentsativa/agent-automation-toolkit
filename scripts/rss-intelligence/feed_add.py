#!/usr/bin/env python3
"""
feed_add.py - Add a new RSS/Atom feed to the watchlist.

Usage:
    python feed_add.py --url <feed_url> [--name <display_name>] [--category <tag>] [--log]

Flags:
    --url       Feed URL (required, must start with http:// or https://)
    --name      Human-readable name for the feed (optional)
    --category  Category tag for grouping feeds (optional)
    --log       Enable logging to data/blogwatcher.log
"""

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


def get_db_path():
    """Resolve database path relative to this script's location."""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    return data_dir / "blogwatcher.db"


def get_log_path():
    """Resolve log path relative to this script's location."""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    return data_dir / "blogwatcher.log"


def log_message(message, log_enabled=False):
    """Write a message to the log file if logging is enabled."""
    if log_enabled:
        timestamp = datetime.now().isoformat()
        log_path = get_log_path()
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")


def validate_url(url):
    """Check that URL starts with http:// or https://."""
    return url.startswith("http://") or url.startswith("https://")


def add_feed(url, name=None, category=None, log_enabled=False):
    """Add a new feed to the database."""
    if not validate_url(url):
        error_msg = "[blogwatcher] Error: URL must start with http:// or https://"
        print(error_msg, file=sys.stderr)
        log_message(f"ERROR: {error_msg}", log_enabled)
        return 1
    
    db_path = get_db_path()
    now = datetime.now().isoformat()
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if URL already exists
        cursor.execute("SELECT id, name FROM feeds WHERE url = ?", (url,))
        existing = cursor.fetchone()
        
        if existing:
            message = f"[blogwatcher] Feed already exists: {existing[1] or url} ({url})"
            print(message)
            log_message(message, log_enabled)
            conn.close()
            return 0
        
        # Insert new feed
        cursor.execute("""
            INSERT INTO feeds (url, name, category, added_at)
            VALUES (?, ?, ?, ?)
        """, (url, name, category, now))
        
        conn.commit()
        conn.close()
        
        # Build confirmation message
        parts = [name or url, f"({url})"]
        if category:
            parts.append(f"[category: {category}]")
        
        message = f"[blogwatcher] Feed added: {' '.join(parts)}"
        print(message)
        log_message(message, log_enabled)
        
        return 0
        
    except sqlite3.Error as e:
        error_msg = f"[blogwatcher] Database error: {e}"
        print(error_msg, file=sys.stderr)
        log_message(f"ERROR: {error_msg}", log_enabled)
        return 1
    except Exception as e:
        error_msg = f"[blogwatcher] Unexpected error: {e}"
        print(error_msg, file=sys.stderr)
        log_message(f"ERROR: {error_msg}", log_enabled)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Add a new RSS/Atom feed to the watchlist"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Feed URL (must start with http:// or https://)"
    )
    parser.add_argument(
        "--name",
        help="Human-readable name for the feed"
    )
    parser.add_argument(
        "--category",
        help="Category tag for grouping feeds"
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Enable logging to data/blogwatcher.log"
    )
    
    args = parser.parse_args()
    sys.exit(add_feed(args.url, args.name, args.category, args.log))


if __name__ == "__main__":
    main()
