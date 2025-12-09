"""
Create test project directly using sqlite3, avoiding importing app modules (safer while server runs).
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'blackburn_tools.db')
DB_PATH = os.path.abspath(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

repo_full_name = 'test_owner/test_repo'
cur.execute('SELECT id FROM projects WHERE repo_full_name = ?', (repo_full_name,))
row = cur.fetchone()
if row:
    print(f'Project already exists: id={row[0]}')
else:
    now = datetime.utcnow().isoformat()
    secret = 'test-secret'
    cur.execute(
        '''INSERT INTO projects (name, repo_type, repo_full_name, github_webhook_secret, language, ai_enabled, post_mode, telegram_chat_id, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        ('Test Project', 'github', repo_full_name, secret, 'en', 0, 'per_push', '123456789', now, now)
    )
    conn.commit()
    print('Created project, repo=', repo_full_name)

conn.close()
