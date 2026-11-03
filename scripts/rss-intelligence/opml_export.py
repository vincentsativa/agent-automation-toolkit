#!/usr/bin/env python3
"""
opml_export.py - Export feeds to an OPML file.

Usage:
    python opml_export.py --output <path_to_output.opml> [--category <tag>] [--log]

Flags:
    --output     Path to output OPML file (required)
    --category   Only export feeds with this category
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


def export_opml(output_path, category=None, log_enabled=False):
    """Export feeds to an OPML file."""
    db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT id, url, name, category 
                FROM feeds 
                WHERE category = ?
                ORDER BY category, name
            """, (category,))
        else:
            cursor.execute("""
                SELECT id, url, name, category 
                FROM feeds 
                ORDER BY category, name
            """)
        
        feeds = cursor.fetchall()
        conn.close()
        
        if not feeds:
            message = "[blogwatcher] No feeds to export"
            print(message)
            log_message(message, log_enabled)
            return 0
        
        # Build OPML document
        opml = ET.Element("opml", version="2.0")
        
        # Head section
        head = ET.SubElement(opml, "head")
        title = ET.SubElement(head, "title")
        title.text = "BlogWatcher Feed Export"
        
        date_created = ET.SubElement(head, "dateCreated")
        date_created.text = datetime.now().isoformat()
        
        # Body section
        body = ET.SubElement(opml, "body")
        
        # Group feeds by category
        categories = {}
        for feed in feeds:
            cat = feed["category"] or "Uncategorized"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(feed)
        
        # Create outline elements
        for cat_name in sorted(categories.keys()):
            cat_feeds = categories[cat_name]
            
            # If we have multiple categories, create folder outlines
            if len(categories) > 1:
                folder = ET.SubElement(body, "outline", text=cat_name)
                for feed in cat_feeds:
                    name = feed["name"] or feed["url"]
                    ET.SubElement(
                        folder, "outline",
                        text=name,
                        xmlUrl=feed["url"]
                    )
            else:
                # Single category or no categories - flat list
                for feed in cat_feeds:
                    name = feed["name"] or feed["url"]
                    ET.SubElement(
                        body, "outline",
                        text=name,
                        xmlUrl=feed["url"]
                    )
        
        # Write to file
        tree = ET.ElementTree(opml)
        
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write with XML declaration
        with open(output_file, "wb") as f:
            tree.write(f, encoding="UTF-8", xml_declaration=True)
        
        message = f"[blogwatcher] Exported: {len(feeds)} feeds to {output_path}"
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
        description="Export feeds to an OPML file"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output OPML file"
    )
    parser.add_argument(
        "--category",
        help="Only export feeds with this category"
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Enable logging to data/blogwatcher.log"
    )
    
    args = parser.parse_args()
    sys.exit(export_opml(args.output, args.category, args.log))


if __name__ == "__main__":
    main()
