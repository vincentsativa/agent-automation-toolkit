#!/usr/bin/env python3
"""
db_init.py - Initialize the BlogWatcher SQLite database.

Creates the data directory and blogwatcher.db file with all required tables.
Idempotent: safe to run multiple times.

Usage:
    python db_init.py [--log]

Flags:
    --log    Enable logging to data/blogwatcher.log
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
    data_dir.mkdir(parents=True, exist_ok=True)
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


def init_database(log_enabled=False):
    """Create the database and tables if they don't exist."""
    db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create feeds table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                name TEXT,
                category TEXT,
                last_scanned TEXT,
                added_at TEXT
            )
        """)
        
        # Create articles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_id INTEGER,
                guid TEXT UNIQUE,
                title TEXT,
                link TEXT,
                published TEXT,
                summary TEXT,
                is_read INTEGER DEFAULT 0,
                ingested_at TEXT,
                content_hash TEXT,
                FOREIGN KEY (feed_id) REFERENCES feeds(id)
            )
        """)
        
        # Create index on content_hash for faster dedup lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_content_hash 
            ON articles(content_hash)
        """)
        
        # Create index on is_read for faster unread queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_is_read 
            ON articles(is_read)
        """)
        
        # Create index on feed_id for faster feed-based queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_feed_id 
            ON articles(feed_id)
        """)
        
        conn.commit()
        conn.close()
        
        message = "[blogwatcher] Database ready."
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
        description="Initialize the BlogWatcher database"
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Enable logging to data/blogwatcher.log"
    )
    
    args = parser.parse_args()
    sys.exit(init_database(args.log))


if __name__ == "__main__":
    main()
