#!/usr/bin/env python3
"""
n8n_backup.py - Backup blogwatcher data to n8n.

Sends feeds and unread articles to n8n webhook for backup/processing.

Usage:
    python n8n_backup.py --feeds [--log]           # Backup all feeds
    python n8n_backup.py --unread [--log]          # Backup unread articles
    python n8n_backup.py --all [--log]             # Backup everything
    python n8n_backup.py --test [--log]            # Test n8n connection
    python n8n_backup.py --trigger-workflow <name> [--data <json>] [--log]  # Trigger specific workflow

Flags:
    --feeds              Backup all feeds to n8n
    --unread             Backup unread articles to n8n
    --all                Backup feeds + unread articles
    --test               Test n8n API connection
    --trigger-workflow   Trigger a specific n8n workflow by name
    --data               JSON data to send with workflow trigger
    --log                Enable logging to data/blogwatcher.log
"""

import argparse
import json
import sqlite3
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


def get_script_dir():
    """Get the directory where this script is located."""
    return Path(__file__).parent


def get_config_path():
    """Resolve config path relative to this script's location."""
    script_dir = get_script_dir()
    return script_dir.parent / "config" / "n8n.env"


def get_db_path():
    """Resolve database path relative to this script's location."""
    script_dir = get_script_dir()
    data_dir = script_dir.parent / "data"
    return data_dir / "blogwatcher.db"


def get_log_path():
    """Resolve log path relative to this script's location."""
    script_dir = get_script_dir()
    data_dir = script_dir.parent / "data"
    return data_dir / "blogwatcher.log"


def load_config():
    """Load n8n configuration from .env file."""
    config_path = get_config_path()
    
    if not config_path.exists():
        raise FileNotFoundError(f"n8n config not found: {config_path}")
    
    config = {}
    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    
    return config


def log_message(message, log_enabled=False):
    """Write a message to the log file if logging is enabled."""
    if log_enabled:
        timestamp = datetime.now().isoformat()
        log_path = get_log_path()
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")


def n8n_request(url, method="GET", data=None, api_key=None, log_enabled=False):
    """Make a request to n8n API."""
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "BlogWatcher/1.0 (OpenClaw Skill)"
    }
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    body = None
    if data:
        body = json.dumps(data).encode("utf-8")
    
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status == 204:
                return {"success": True, "message": "No content"}
            
            response_data = response.read().decode("utf-8")
            if response_data:
                try:
                    return {"success": True, "data": json.loads(response_data)}
                except json.JSONDecodeError:
                    return {"success": True, "raw": response_data[:500]}
            return {"success": True}
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        error_msg = f"n8n HTTP Error {e.code}: {error_body}"
        log_message(f"ERROR: {error_msg}", log_enabled)
        return {"success": False, "error": error_msg}
        
    except urllib.error.URLError as e:
        error_msg = f"n8n URL Error: {e.reason}"
        log_message(f"ERROR: {error_msg}", log_enabled)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"n8n Request Error: {e}"
        log_message(f"ERROR: {error_msg}", log_enabled)
        return {"success": False, "error": error_msg}


def test_connection(config, log_enabled=False):
    """Test n8n API connection."""
    api_url = config.get("N8N_API_URL", "http://localhost:5678")
    
    message = f"[n8n] Testing connection to {api_url}..."
    print(message)
    log_message(message, log_enabled)
    
    # Test the n8n health endpoint
    health_url = f"{api_url}/healthz"
    result = n8n_request(health_url, method="GET", log_enabled=log_enabled)
    
    if result.get("success"):
        message = "[n8n] OK: n8n is running and reachable"
        print(message)
        log_message(message, log_enabled)
        print(f"[n8n] Instance: {api_url}")
        print(f"[n8n] Webhooks configured:")
        print(f"    - Backup: {config.get('N8N_WEBHOOK_BACKUP', 'not set')}")
        print(f"    - New articles: {config.get('N8N_WEBHOOK_NEW_ARTICLE', 'not set')}")
        return 0
    else:
        message = f"[n8n] FAIL: Connection failed - {result.get('error', 'Unknown error')}"
        print(message, file=sys.stderr)
        log_message(message, log_enabled)
        print("[n8n] Make sure n8n is running on http://localhost:5678")
        return 1


def get_feeds_from_db():
    """Fetch all feeds from database."""
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
        
        feeds = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return feeds
        
    except sqlite3.Error as e:
        print(f"[n8n] Database error: {e}", file=sys.stderr)
        return []


def get_unread_articles_from_db():
    """Fetch all unread articles from database."""
    db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.id, a.title, a.link, a.published, a.summary, a.ingested_at,
                   f.id as feed_id, f.name as feed_name, f.category as feed_category, f.url as feed_url
            FROM articles a
            JOIN feeds f ON a.feed_id = f.id
            WHERE a.is_read = 0
            ORDER BY a.published DESC
        """)
        
        articles = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return articles
        
    except sqlite3.Error as e:
        print(f"[n8n] Database error: {e}", file=sys.stderr)
        return []


def backup_feeds(config, log_enabled=False):
    """Backup all feeds to n8n webhook."""
    api_url = config.get("N8N_API_URL", "https://n8n.example.com")
    webhook_url = config.get("N8N_WEBHOOK_BACKUP", f"{api_url}/webhook/blogwatcher-backup")
    api_key = config.get("N8N_API_KEY")
    
    feeds = get_feeds_from_db()
    
    payload = {
        "type": "feeds_backup",
        "timestamp": datetime.now().isoformat(),
        "total_feeds": len(feeds),
        "feeds": feeds
    }
    
    message = f"[n8n] Backing up {len(feeds)} feeds to n8n..."
    print(message)
    log_message(message, log_enabled)
    
    result = n8n_request(
        webhook_url,
        method="POST",
        data=payload,
        api_key=api_key,
        log_enabled=log_enabled
    )
    
    if result.get("success"):
        message = f"[n8n] Backup successful: {len(feeds)} feeds sent"
        print(message)
        log_message(message, log_enabled)
        return 0
    else:
        message = f"[n8n] Backup failed: {result.get('error', 'Unknown error')}"
        print(message, file=sys.stderr)
        log_message(message, log_enabled)
        return 1


def backup_unread(config, log_enabled=False):
    """Backup unread articles to n8n webhook."""
    api_url = config.get("N8N_API_URL", "https://n8n.example.com")
    webhook_url = config.get("N8N_WEBHOOK_NEW_ARTICLE", f"{api_url}/webhook/blogwatcher-new-article")
    api_key = config.get("N8N_API_KEY")
    
    articles = get_unread_articles_from_db()
    
    payload = {
        "type": "unread_backup",
        "timestamp": datetime.now().isoformat(),
        "total_unread": len(articles),
        "articles": articles
    }
    
    message = f"[n8n] Backing up {len(articles)} unread articles to n8n..."
    print(message)
    log_message(message, log_enabled)
    
    result = n8n_request(
        webhook_url,
        method="POST",
        data=payload,
        api_key=api_key,
        log_enabled=log_enabled
    )
    
    if result.get("success"):
        message = f"[n8n] Backup successful: {len(articles)} unread articles sent"
        print(message)
        log_message(message, log_enabled)
        return 0
    else:
        message = f"[n8n] Backup failed: {result.get('error', 'Unknown error')}"
        print(message, file=sys.stderr)
        log_message(message, log_enabled)
        return 1


def trigger_workflow(workflow_name, config, data=None, log_enabled=False):
    """Trigger a specific n8n workflow by name."""
    api_url = config.get("N8N_API_URL", "https://n8n.example.com")
    api_key = config.get("N8N_API_KEY")
    
    # Construct workflow trigger URL
    # Format: /webhook/<workflow-name> or use API endpoint
    webhook_url = f"{api_url}/webhook/{workflow_name}"
    
    payload = data or {}
    payload["triggered_by"] = "blogwatcher"
    payload["timestamp"] = datetime.now().isoformat()
    
    message = f"[n8n] Triggering workflow: {workflow_name}..."
    print(message)
    log_message(message, log_enabled)
    
    result = n8n_request(
        webhook_url,
        method="POST",
        data=payload,
        api_key=api_key,
        log_enabled=log_enabled
    )
    
    if result.get("success"):
        message = f"[n8n] Workflow '{workflow_name}' triggered successfully"
        print(message)
        log_message(message, log_enabled)
        
        # Return any data from the workflow
        if "data" in result:
            print(f"[n8n] Workflow response: {json.dumps(result['data'], indent=2)}")
        
        return 0
    else:
        message = f"[n8n] Workflow trigger failed: {result.get('error', 'Unknown error')}"
        print(message, file=sys.stderr)
        log_message(message, log_enabled)
        return 1


def backup_all(config, log_enabled=False):
    """Backup both feeds and unread articles."""
    feeds_result = backup_feeds(config, log_enabled)
    unread_result = backup_unread(config, log_enabled)
    
    if feeds_result == 0 and unread_result == 0:
        message = "[n8n] Complete backup successful"
        print(message)
        log_message(message, log_enabled)
        return 0
    else:
        message = "[n8n] Partial backup completed (check errors above)"
        print(message, file=sys.stderr)
        log_message(message, log_enabled)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Backup blogwatcher data to n8n"
    )
    
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--feeds",
        action="store_true",
        help="Backup all feeds to n8n"
    )
    mode_group.add_argument(
        "--unread",
        action="store_true",
        help="Backup unread articles to n8n"
    )
    mode_group.add_argument(
        "--all",
        action="store_true",
        help="Backup feeds + unread articles"
    )
    mode_group.add_argument(
        "--test",
        action="store_true",
        help="Test n8n API connection"
    )
    mode_group.add_argument(
        "--trigger-workflow",
        help="Trigger a specific n8n workflow by name"
    )
    
    parser.add_argument(
        "--data",
        help="JSON data to send with workflow trigger"
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Enable logging to data/blogwatcher.log"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"[n8n] Error: {e}", file=sys.stderr)
        return 1
    
    # Execute requested operation
    if args.test:
        return test_connection(config, args.log)
    elif args.feeds:
        return backup_feeds(config, args.log)
    elif args.unread:
        return backup_unread(config, args.log)
    elif args.all:
        return backup_all(config, args.log)
    elif args.trigger_workflow:
        data = None
        if args.data:
            try:
                data = json.loads(args.data)
            except json.JSONDecodeError:
                print(f"[n8n] Error: Invalid JSON in --data", file=sys.stderr)
                return 1
        return trigger_workflow(args.trigger_workflow, config, data, args.log)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    main()
