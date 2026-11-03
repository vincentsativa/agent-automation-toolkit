#!/usr/bin/env python3
"""
feed_list.py - List feeds or unread articles.

Usage:
    python feed_list.py --feeds [--json]
    python feed_list.py --unread [--category <tag>] [--json] [--export json]
    python feed_list.py --all-articles [--json]

Flags:
    --feeds         List all watched feeds
    --unread        List all unread articles grouped by feed
    --all-articles  List all articles (read + unread)
    --category      Filter by category (use with --unread)
    --json          Output as JSON instead of plain text
    --export json   Export unread articles for pipeline integration
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


def get_db_path():
    """Resolve database path relative to this script's location."""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    return data_dir / "blogwatcher.db"


def list_feeds(as_json=False):
    """List all watched feeds."""
    db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, url, name, category, last_scanned, added_at 
            FROM feeds 
            ORDER BY category, name
        """)
        
        feeds = cursor.fetchall()
        conn.close()
        
        if as_json:
            output = {
                "exported_at": datetime.now().isoformat(),
                "total_feeds": len(feeds),
                "feeds": [
                    {
                        "id": row["id"],
                        "url": row["url"],
                        "name": row["name"],
                        "category": row["category"],
                        "last_scanned": row["last_scanned"],
                        "added_at": row["added_at"]
                    }
                    for row in feeds
                ]
            }
            print(json.dumps(output, indent=2))
        else:
            if not feeds:
                print("[blogwatcher] No feeds in watchlist")
                return 0
            
            print(f"=== Watched Feeds ({len(feeds)}) ===")
            current_category = None
            
            for row in feeds:
                category = row["category"] or "Uncategorized"
                if category != current_category:
                    current_category = category
                    print(f"\n--- {category} ---")
                
                name = row["name"] or row["url"]
                print(f"[{row['id']}] {name}")
                print(f"    URL: {row['url']}")
                if row["last_scanned"]:
                    print(f"    Last scanned: {row['last_scanned']}")
        
        return 0
        
    except sqlite3.Error as e:
        print(f"[blogwatcher] Database error: {e}", file=sys.stderr)
        return 1


def list_unread(category=None, as_json=False, export_json=False):
    """List all unread articles grouped by feed."""
    db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT a.id, a.title, a.link, a.published, a.summary,
                       f.id as feed_id, f.name as feed_name, f.category as feed_category
                FROM articles a
                JOIN feeds f ON a.feed_id = f.id
                WHERE a.is_read = 0 AND f.category = ?
                ORDER BY f.category, f.name, a.published DESC
            """, (category,))
        else:
            cursor.execute("""
                SELECT a.id, a.title, a.link, a.published, a.summary,
                       f.id as feed_id, f.name as feed_name, f.category as feed_category
                FROM articles a
                JOIN feeds f ON a.feed_id = f.id
                WHERE a.is_read = 0
                ORDER BY f.category, f.name, a.published DESC
            """)
        
        articles = cursor.fetchall()
        conn.close()
        
        # Group by feed
        feeds_dict = {}
        for row in articles:
            feed_name = row["feed_name"] or row["feed_id"]
            feed_category = row["feed_category"] or "Uncategorized"
            feed_key = (feed_category, feed_name)
            
            if feed_key not in feeds_dict:
                feeds_dict[feed_key] = {
                    "category": feed_category,
                    "name": feed_name,
                    "feed_id": row["feed_id"],
                    "articles": []
                }
            
            feeds_dict[feed_key]["articles"].append({
                "id": row["id"],
                "title": row["title"],
                "link": row["link"],
                "published": row["published"],
                "summary": row["summary"],
                "feed_name": row["feed_name"],
                "feed_category": row["feed_category"]
            })
        
        total_unread = len(articles)
        
        # Handle JSON export for pipeline
        if export_json:
            output = {
                "exported_at": datetime.now().isoformat(),
                "total_unread": total_unread,
                "articles": [
                    {
                        "id": art["id"],
                        "feed_name": art["feed_name"],
                        "feed_category": art["feed_category"],
                        "title": art["title"],
                        "link": art["link"],
                        "published": art["published"],
                        "summary": art["summary"]
                    }
                    for art_list in feeds_dict.values()
                    for art in art_list["articles"]
                ]
            }
            print(json.dumps(output, indent=2))
            return 0
        
        # Handle regular JSON output
        if as_json:
            output = {
                "exported_at": datetime.now().isoformat(),
                "total_unread": total_unread,
                "feeds": [
                    {
                        "category": feed_data["category"],
                        "name": feed_data["name"],
                        "feed_id": feed_data["feed_id"],
                        "unread_count": len(feed_data["articles"]),
                        "articles": feed_data["articles"]
                    }
                    for feed_data in feeds_dict.values()
                ]
            }
            print(json.dumps(output, indent=2))
            return 0
        
        # Plain text output
        if not articles:
            print("[blogwatcher] No unread articles")
            return 0
        
        current_feed_key = None
        
        for feed_key, feed_data in sorted(feeds_dict.items()):
            category, feed_name = feed_key
            article_count = len(feed_data["articles"])
            
            if feed_key != current_feed_key:
                current_feed_key = feed_key
                print(f"\n=== {feed_name} ({article_count} unread) ===")
            
            for art in feed_data["articles"]:
                print(f"[{art['id']}] {art['title']}")
                print(f"    {art['link']}")
                if art["published"]:
                    print(f"    Published: {art['published']}")
        
        return 0
        
    except sqlite3.Error as e:
        print(f"[blogwatcher] Database error: {e}", file=sys.stderr)
        return 1


def list_all_articles(as_json=False):
    """List all articles (read + unread)."""
    db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.id, a.title, a.link, a.published, a.is_read, a.ingested_at,
                   f.id as feed_id, f.name as feed_name
            FROM articles a
            JOIN feeds f ON a.feed_id = f.id
            ORDER BY a.ingested_at DESC
        """)
        
        articles = cursor.fetchall()
        conn.close()
        
        if as_json:
            output = {
                "exported_at": datetime.now().isoformat(),
                "total_articles": len(articles),
                "articles": [
                    {
                        "id": row["id"],
                        "feed_id": row["feed_id"],
                        "feed_name": row["feed_name"],
                        "title": row["title"],
                        "link": row["link"],
                        "published": row["published"],
                        "is_read": bool(row["is_read"]),
                        "ingested_at": row["ingested_at"]
                    }
                    for row in articles
                ]
            }
            print(json.dumps(output, indent=2))
        else:
            if not articles:
                print("[blogwatcher] No articles in database")
                return 0
            
            print(f"=== All Articles ({len(articles)}) ===")
            
            for row in articles:
                status = "R" if row["is_read"] else "U"
                feed_name = row["feed_name"] or f"Feed #{row['feed_id']}"
                print(f"[{status}] [{row['id']}] {row['title']}")
                print(f"    {feed_name} | {row['link']}")
        
        return 0
        
    except sqlite3.Error as e:
        print(f"[blogwatcher] Database error: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="List feeds or unread articles"
    )
    
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--feeds",
        action="store_true",
        help="List all watched feeds"
    )
    mode_group.add_argument(
        "--unread",
        action="store_true",
        help="List all unread articles"
    )
    mode_group.add_argument(
        "--all-articles",
        action="store_true",
        help="List all articles (read + unread)"
    )
    
    parser.add_argument(
        "--category",
        help="Filter by category (use with --unread)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of plain text"
    )
    parser.add_argument(
        "--export",
        choices=["json"],
        help="Export format for pipeline integration"
    )
    
    args = parser.parse_args()
    
    if args.feeds:
        sys.exit(list_feeds(args.json))
    elif args.unread:
        sys.exit(list_unread(args.category, args.json, args.export == "json"))
    elif args.all_articles:
        sys.exit(list_all_articles(args.json))
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    main()
