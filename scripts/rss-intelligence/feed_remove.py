#!/usr/bin/env python3
"""
feed_remove.py - Remove a feed and all its articles from the watchlist.

Usage:
    python feed_remove.py --id <feed_id> [--log]
    python feed_remove.py --url <feed_url> [--log]

Flags:
    --id       Feed ID to remove
    --url      Feed URL to remove (alternative to --id)
    --log      Enable logging to data/blogwatcher.log
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


def remove_feed(feed_id=None, url=None, log_enabled=False):
    """Remove a feed and all its articles from the database."""
    if feed_id is None and url is None:
        error_msg = "[blogwatcher] Error: Must specify --id or --url"
        print(error_msg, file=sys.stderr)
        log_message(f"ERROR: {error_msg}", log_enabled)
        return 1
    
    db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Find the feed
        if feed_id:
            cursor.execute("SELECT id, name, url FROM feeds WHERE id = ?", (feed_id,))
        else:
            cursor.execute("SELECT id, name, url FROM feeds WHERE url = ?", (url,))
        
        feed = cursor.fetchone()
        
        if not feed:
            error_msg = f"[blogwatcher] Feed not found: {feed_id or url}"
            print(error_msg, file=sys.stderr)
            log_message(f"ERROR: {error_msg}", log_enabled)
            conn.close()
            return 1
        
        feed_id, name, feed_url = feed
        
        # Delete articles first (foreign key constraint)
        cursor.execute("DELETE FROM articles WHERE feed_id = ?", (feed_id,))
        
        # Delete the feed
        cursor.execute("DELETE FROM feeds WHERE id = ?", (feed_id,))
        
        conn.commit()
        conn.close()
        
        display_name = name or feed_url
        message = f"[blogwatcher] Removed feed: {display_name} ({feed_url})"
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
        description="Remove a feed and all its articles from the watchlist"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--id",
        type=int,
        help="Feed ID to remove"
    )
    group.add_argument(
        "--url",
        help="Feed URL to remove"
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Enable logging to data/blogwatcher.log"
    )
    
    args = parser.parse_args()
    sys.exit(remove_feed(args.id, args.url, args.log))


if __name__ == "__main__":
    main()
