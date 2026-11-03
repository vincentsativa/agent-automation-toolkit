#!/bin/bash
# Blogwatcher cleanup script - two-phase approach:
#   Phase 1: Mark articles older than threshold as read (blocks re-import via unique URL constraint)
#   Phase 2: Hard-delete articles older than archival limit (reclaims space)
# Usage: ./blogwatcher-cleanup.sh [days_to_mark_read] [days_to_purge]

MARK_READ_DAYS=${1:-7}
PURGE_DAYS=${2:-90}
DB_PATH="$HOME/.blogwatcher-cli/blogwatcher-cli.db"

echo "=== Blogwatcher Cleanup ==="
echo "Database: $DB_PATH"
echo ""

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo "ERROR: Database not found at $DB_PATH"
    exit 1
fi

python3 -c "
import sqlite3, os
from datetime import datetime, timedelta

db_path = os.path.expanduser('$DB_PATH')
conn = sqlite3.connect(db_path)

mark_read_days = $MARK_READ_DAYS
purge_days = $PURGE_DAYS
cutoff_mark = (datetime.now() - timedelta(days=mark_read_days)).strftime('%Y-%m-%d')
cutoff_purge = (datetime.now() - timedelta(days=purge_days)).strftime('%Y-%m-%d')

print(f'Mark as read cutoff: {cutoff_mark} (>={mark_read_days} days old)')
print(f'Purge cutoff: {cutoff_purge} (>={purge_days} days old)')
print()

# ---- Phase 1: Mark as read to block re-import ----
cursor = conn.cursor()
cursor.execute(
    'UPDATE articles SET is_read = 1 WHERE is_read = 0 AND published_date < ?',
    (cutoff_mark,)
)
marked = cursor.rowcount
print(f'Phase 1: Marked {marked} old articles as read (keeps URLs in DB to block re-import)')

# ---- Phase 2: Purge truly ancient data ----
cursor.execute(
    'DELETE FROM articles WHERE published_date < ?',
    (cutoff_purge,)
)
purged = cursor.rowcount
conn.commit()
print(f'Phase 2: Purged {purged} articles older than {purge_days} days')

# Vacuum to reclaim space (separate connection)
conn.close()
conn2 = sqlite3.connect(db_path)
conn2.execute('PRAGMA journal_mode=WAL')
conn2.execute('VACUUM')
conn2.close()

# Final count
conn3 = sqlite3.connect(db_path)
cursor = conn3.cursor()
cursor.execute('SELECT COUNT(*) FROM articles')
remaining = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM articles WHERE is_read = 0')
unread = cursor.fetchone()[0]
conn3.close()

print()
print(f'Final DB state: {remaining} total articles ({unread} unread)')
print('=== Cleanup Complete ===')
"
