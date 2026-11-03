#!/usr/bin/env python3
"""
feed_scan.py - Fetch and ingest new articles from RSS/Atom feeds.

Usage:
    python feed_scan.py --all [--log]
    python feed_scan.py --id <feed_id> [--log]

Flags:
    --id       Scan a specific feed by ID
    --all      Scan all feeds in the watchlist
    --log      Enable logging to data/blogwatcher.log
"""

import argparse
import hashlib
import sqlite3
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


USER_AGENT = "BlogWatcher/1.0 (OpenClaw Skill)"


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


def compute_content_hash(title, link, published):
    """Compute SHA256 hash of title+link+published for deduplication."""
    content = f"{title or ''}{link or ''}{published or ''}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def fetch_feed(url):
    """Fetch RSS/Atom feed from URL with proper User-Agent header."""
    headers = {"User-Agent": USER_AGENT}
    request = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def parse_rss_item(item, namespaces):
    """Parse an RSS 2.0 <item> element."""
    guid_elem = item.find("guid")
    guid = guid_elem.text if guid_elem is not None and guid_elem.text else None
    
    title_elem = item.find("title")
    title = title_elem.text if title_elem is not None and title_elem.text else ""
    
    link_elem = item.find("link")
    link = link_elem.text if link_elem is not None and link_elem.text else ""
    
    # Check for pubDate
    pub_elem = item.find("pubDate")
    published = pub_elem.text if pub_elem is not None and pub_elem.text else None
    
    # Check for dc:date (common in some feeds)
    if not published:
        dc_date = item.find("{http://purl.org/dc/elements/1.1/}date")
        if dc_date is not None and dc_date.text:
            published = dc_date.text
    
    # Get description/summary
    desc_elem = item.find("description")
    summary = ""
    if desc_elem is not None and desc_elem.text:
        # Strip HTML tags and limit to 500 chars
        text = strip_html(desc_elem.text)
        summary = text[:500] if len(text) > 500 else text
    
    return {
        "guid": guid,
        "title": title,
        "link": link,
        "published": published,
        "summary": summary
    }


def parse_atom_entry(entry, namespaces):
    """Parse an Atom <entry> element."""
    # Atom uses id instead of guid
    id_elem = entry.find("{http://www.w3.org/2005/Atom}id")
    guid = id_elem.text if id_elem is not None and id_elem.text else None
    
    title_elem = entry.find("{http://www.w3.org/2005/Atom}title")
    title = title_elem.text if title_elem is not None and title_elem.text else ""
    
    # Atom links are different - look for alternate or self
    link = ""
    for link_elem in entry.findall("{http://www.w3.org/2005/Atom}link"):
        rel = link_elem.get("rel", "alternate")
        if rel == "alternate" or not link:
            href = link_elem.get("href")
            if href:
                link = href
                if rel == "alternate":
                    break
    
    # Published date
    pub_elem = entry.find("{http://www.w3.org/2005/Atom}published")
    if pub_elem is None:
        pub_elem = entry.find("{http://www.w3.org/2005/Atom}updated")
    published = pub_elem.text if pub_elem is not None and pub_elem.text else None
    
    # Summary/content
    summary = ""
    summary_elem = entry.find("{http://www.w3.org/2005/Atom}summary")
    if summary_elem is None:
        summary_elem = entry.find("{http://www.w3.org/2005/Atom}content")
    if summary_elem is not None and summary_elem.text:
        text = strip_html(summary_elem.text)
        summary = text[:500] if len(text) > 500 else text
    
    return {
        "guid": guid,
        "title": title,
        "link": link,
        "published": published,
        "summary": summary
    }


def strip_html(text):
    """Remove HTML tags from text."""
    if not text:
        return ""
    # Simple HTML tag removal
    result = ""
    in_tag = False
    for char in text:
        if char == "<":
            in_tag = True
        elif char == ">":
            in_tag = False
        elif not in_tag:
            result += char
    # Collapse whitespace
    return " ".join(result.split())


def parse_feed(xml_content):
    """Parse RSS or Atom feed and return list of articles."""
    articles = []
    
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        raise ValueError(f"XML parse error: {e}")
    
    # Detect feed type
    # RSS 2.0 has <rss> or <channel> root
    # Atom has <feed> root with Atom namespace
    
    namespaces = {}
    
    # Check for RSS
    if root.tag == "rss" or root.find("channel") is not None:
        channel = root.find("channel") if root.tag == "rss" else root
        items = channel.findall("item") if channel is not None else root.findall("item")
        
        for item in items:
            article = parse_rss_item(item, namespaces)
            articles.append(article)
    
    # Check for Atom
    elif root.tag == "{http://www.w3.org/2005/Atom}feed" or root.tag == "feed":
        entries = root.findall("{http://www.w3.org/2005/Atom}entry")
        if not entries:
            entries = root.findall("entry")
        
        for entry in entries:
            article = parse_atom_entry(entry, namespaces)
            articles.append(article)
    
    else:
        # Try to find items anyway
        items = root.findall(".//item") + root.findall(".//{http://www.w3.org/2005/Atom}entry")
        for item in items:
            if item.tag.endswith("item"):
                article = parse_rss_item(item, namespaces)
            else:
                article = parse_atom_entry(item, namespaces)
            articles.append(article)
    
    return articles


def scan_feed(feed_id, feed_url, feed_name, cursor, log_enabled=False):
    """Scan a single feed and insert new articles."""
    now = datetime.now().isoformat()
    
    try:
        xml_content = fetch_feed(feed_url)
    except urllib.error.URLError as e:
        error_msg = f"[blogwatcher] Network error for {feed_name or feed_url}: {e.reason}"
        print(error_msg, file=sys.stderr)
        log_message(f"ERROR: {error_msg}", log_enabled)
        # Update last_scanned even on error to track attempts
        cursor.execute("UPDATE feeds SET last_scanned = ? WHERE id = ?", (now, feed_id))
        return 0
    except Exception as e:
        error_msg = f"[blogwatcher] Error fetching {feed_name or feed_url}: {e}"
        print(error_msg, file=sys.stderr)
        log_message(f"ERROR: {error_msg}", log_enabled)
        cursor.execute("UPDATE feeds SET last_scanned = ? WHERE id = ?", (now, feed_id))
        return 0
    
    try:
        articles = parse_feed(xml_content)
    except ValueError as e:
        error_msg = f"[blogwatcher] Parse error for {feed_name or feed_url}: {e}"
        print(error_msg, file=sys.stderr)
        log_message(f"ERROR: {error_msg}", log_enabled)
        cursor.execute("UPDATE feeds SET last_scanned = ? WHERE id = ?", (now, feed_id))
        return 0
    
    new_count = 0
    
    for article in articles:
        guid = article["guid"]
        title = article["title"]
        link = article["link"]
        published = article["published"]
        summary = article["summary"]
        
        # Compute content_hash as fallback dedup key
        content_hash = compute_content_hash(title, link, published)
        
        # Determine the unique key to use
        # Priority: guid > content_hash
        unique_key = guid if guid else content_hash
        
        # Check if article already exists
        cursor.execute("""
            SELECT id FROM articles 
            WHERE guid = ? OR content_hash = ?
        """, (guid, content_hash))
        
        if cursor.fetchone() is None:
            # Insert new article
            cursor.execute("""
                INSERT INTO articles 
                (feed_id, guid, title, link, published, summary, is_read, ingested_at, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
            """, (feed_id, guid, title, link, published, summary, now, content_hash))
            new_count += 1
    
    # Update last_scanned timestamp
    cursor.execute("UPDATE feeds SET last_scanned = ? WHERE id = ?", (now, feed_id))
    
    return new_count


def scan_feeds(feed_id=None, scan_all=False, log_enabled=False):
    """Scan one or all feeds for new articles."""
    db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        if scan_all:
            cursor.execute("SELECT id, url, name FROM feeds")
            feeds = cursor.fetchall()
        elif feed_id:
            cursor.execute("SELECT id, url, name FROM feeds WHERE id = ?", (feed_id,))
            feeds = cursor.fetchall()
            if not feeds:
                error_msg = f"[blogwatcher] Feed ID {feed_id} not found"
                print(error_msg, file=sys.stderr)
                log_message(f"ERROR: {error_msg}", log_enabled)
                conn.close()
                return 1
        else:
            error_msg = "[blogwatcher] Must specify --id or --all"
            print(error_msg, file=sys.stderr)
            log_message(f"ERROR: {error_msg}", log_enabled)
            return 1
        
        for feed in feeds:
            fid, url, name = feed
            new_count = scan_feed(fid, url, name, cursor, log_enabled)
            
            display_name = name or url
            message = f"[blogwatcher] Scanned: {display_name}, {new_count} new articles"
            print(message)
            log_message(message, log_enabled)
        
        conn.commit()
        conn.close()
        
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
        description="Fetch and ingest new articles from RSS/Atom feeds"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--id",
        type=int,
        help="Feed ID to scan"
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Scan all feeds"
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Enable logging to data/blogwatcher.log"
    )
    
    args = parser.parse_args()
    sys.exit(scan_feeds(args.id, args.all, args.log))


if __name__ == "__main__":
    main()
