#!/usr/bin/env python3
"""
opml_import.py - Import feeds from an OPML file.

Usage:
    python opml_import.py --file <path_to_opml.xml> [--category <tag>] [--confirm] [--log]

Flags:
    --file       Path to OPML file (required)
    --category   Apply this category to all imported feeds
    --confirm    Skip interactive confirmation (non-interactive mode)
    --log        Enable logging to data/blogwatcher.log
"""

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


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


def parse_opml(file_path):
    """Parse OPML file and extract feed outlines."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        raise ValueError(f"XML parse error: {e}")
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    
    feeds = []
    
    # OPML structure: <opml><body><outline .../></body></opml>
    body = root.find("body")
    if body is None:
        body = root  # Some OPML files skip the body tag
    
    def extract_outlines(element, parent_category=None):
        """Recursively extract outline elements with xmlUrl attribute."""
        for outline in element.findall("outline"):
            xml_url = outline.get("xmlUrl")
            text = outline.get("text") or outline.get("title") or xml_url
            
            if xml_url:
                # Get category from outline or parent
                category = outline.get("category") or outline.get("text") or parent_category
                
                feeds.append({
                    "url": xml_url,
                    "name": text,
                    "category": category
                })
            
            # Recurse into nested outlines (for folder structures)
            nested_category = outline.get("text") or outline.get("title")
            extract_outlines(outline, nested_category)
    
    extract_outlines(body)
    return feeds


def import_opml(file_path, category=None, confirm=False, log_enabled=False):
    """Import feeds from an OPML file."""
    db_path = get_db_path()
    
    # Parse OPML file
    try:
        feeds = parse_opml(file_path)
    except ValueError as e:
        error_msg = f"[blogwatcher] Error parsing OPML: {e}"
        print(error_msg, file=sys.stderr)
        log_message(f"ERROR: {error_msg}", log_enabled)
        return 1
    
    if not feeds:
        message = "[blogwatcher] No feeds found in OPML file"
        print(message)
        log_message(message, log_enabled)
        return 0
    
    # Show preview
    print(f"\n[blogwatcher] Found {len(feeds)} feeds in OPML file:\n")
    
    for i, feed in enumerate(feeds[:20], 1):  # Show first 20
        cat_str = f" [{feed['category']}]" if feed.get('category') else ""
        print(f"  {i}. {feed['name']}{cat_str}")
        print(f"     {feed['url']}")
    
    if len(feeds) > 20:
        print(f"  ... and {len(feeds) - 20} more")
    
    # Confirm import
    if not confirm:
        response = input(f"\nImport {len(feeds)} feeds? (y/n): ").strip().lower()
        if response != "y":
            print("[blogwatcher] Import cancelled")
            return 0
    
    # Apply global category if specified
    if category:
        for feed in feeds:
            feed["category"] = category
    
    # Import feeds
    now = datetime.now().isoformat()
    added = 0
    skipped = 0
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        for feed in feeds:
            # Check if URL already exists
            cursor.execute("SELECT id FROM feeds WHERE url = ?", (feed["url"],))
            
            if cursor.fetchone():
                skipped += 1
                continue
            
            # Insert new feed
            cursor.execute("""
                INSERT INTO feeds (url, name, category, added_at)
                VALUES (?, ?, ?, ?)
            """, (feed["url"], feed["name"], feed.get("category"), now))
            added += 1
        
        conn.commit()
        conn.close()
        
        message = f"[blogwatcher] Imported: {added} feeds added, {skipped} skipped (duplicates)"
        print(f"\n{message}")
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
        description="Import feeds from an OPML file"
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to OPML file"
    )
    parser.add_argument(
        "--category",
        help="Apply this category to all imported feeds"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip interactive confirmation (non-interactive mode)"
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Enable logging to data/blogwatcher.log"
    )
    
    args = parser.parse_args()
    sys.exit(import_opml(args.file, args.category, args.confirm, args.log))


if __name__ == "__main__":
    main()
