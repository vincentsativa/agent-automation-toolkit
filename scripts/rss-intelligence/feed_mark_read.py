#!/usr/bin/env python3
"""
feed_mark_read.py - Mark articles as read.

Usage:
    python feed_mark_read.py --id <article_id> [--log]
    python feed_mark_read.py --feed-id <feed_id> [--log]
    python feed_mark_read.py --all --confirm [--log]

Flags:
    --id         Mark a single article as read
    --feed-id    Mark all articles in a feed as read
    --all        Mark ALL unread articles as read (requires --confirm)
    --confirm    Confirm non-interactive operation (required for --all)
    --log        Enable logging to data/blogwatcher.log
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


def mark_read(article_id=None, feed_id=None, mark_all=False, confirm=False, log_enabled=False):
    """Mark articles as read."""
    db_path = get_db_path()
    
    # Validate arguments
    if not any([article_id, feed_id, mark_all]):
        error_msg = "[blogwatcher] Error: Must specify --id, --feed-id, or --all"
        print(error_msg, file=sys.stderr)
        log_message(f"ERROR: {error_msg}", log_enabled)
        return 1
    
    if mark_all and not confirm:
        # Interactive confirmation
        print("WARNING: This will mark ALL unread articles as read.")
        response = input("Continue? (y/n): ").strip().lower()
        if response != "y":
            print("[blogwatcher] Operation cancelled")
            return 0
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        if article_id:
            # Mark single article
            cursor.execute("SELECT id, title FROM articles WHERE id = ?", (article_id,))
            article = cursor.fetchone()
            
            if not article:
                error_msg = f"[blogwatcher] Article ID {article_id} not found"
                print(error_msg, file=sys.stderr)
                log_message(f"ERROR: {error_msg}", log_enabled)
                conn.close()
                return 1
            
            cursor.execute("UPDATE articles SET is_read = 1 WHERE id = ?", (article_id,))
            count = cursor.rowcount
            conn.commit()
            conn.close()
            
            message = f"[blogwatcher] Marked read: {count} article(s)"
            print(message)
            log_message(f"Marked article {article_id} ('{article[1]}') as read", log_enabled)
            
        elif feed_id:
            # Mark all articles in a feed
            cursor.execute("SELECT id, name FROM feeds WHERE id = ?", (feed_id,))
            feed = cursor.fetchone()
            
            if not feed:
                error_msg = f"[blogwatcher] Feed ID {feed_id} not found"
                print(error_msg, file=sys.stderr)
                log_message(f"ERROR: {error_msg}", log_enabled)
                conn.close()
                return 1
            
            cursor.execute("""
                UPDATE articles SET is_read = 1 
                WHERE feed_id = ? AND is_read = 0
            """, (feed_id,))
            count = cursor.rowcount
            conn.commit()
            conn.close()
            
            feed_name = feed[1] or f"Feed #{feed_id}"
            message = f"[blogwatcher] Marked read: {count} article(s) from {feed_name}"
            print(message)
            log_message(message, log_enabled)
            
        elif mark_all:
            # Mark ALL unread articles
            cursor.execute("""
                UPDATE articles SET is_read = 1 
                WHERE is_read = 0
            """)
            count = cursor.rowcount
            conn.commit()
            conn.close()
            
            message = f"[blogwatcher] Marked read: {count} article(s)"
            print(message)
            log_message(f"Marked all {count} unread articles as read", log_enabled)
        
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
        description="Mark articles as read"
    )
    
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        "--id",
        type=int,
        help="Article ID to mark as read"
    )
    target_group.add_argument(
        "--feed-id",
        type=int,
        help="Mark all articles in a feed as read"
    )
    target_group.add_argument(
        "--all",
        action="store_true",
        help="Mark ALL unread articles as read"
    )
    
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm non-interactive operation (required for --all)"
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Enable logging to data/blogwatcher.log"
    )
    
    args = parser.parse_args()
    sys.exit(mark_read(args.id, args.feed_id, args.all, args.confirm, args.log))


if __name__ == "__main__":
    main()
