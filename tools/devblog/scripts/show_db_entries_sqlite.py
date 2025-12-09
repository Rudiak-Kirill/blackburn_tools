"""
Show posts and commit_events using sqlite3 to avoid importing app modules.
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'blackburn_tools.db')
DB_PATH = os.path.abspath(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print('Posts:')
for row in cur.execute('SELECT id, project_id, status, telegram_message_id, content, created_at FROM posts ORDER BY created_at DESC LIMIT 10'):
    id, project_id, status, tg_id, content, created_at = row
    print(f'id={id} project_id={project_id} status={status} tg_message_id={tg_id} created={created_at}')
    print(content[:300])
    print('---')

print('\nCommits:')
for row in cur.execute('SELECT id, project_id, commit_hash, author, message, pushed_at FROM commit_events ORDER BY created_at DESC LIMIT 10'):
    id, project_id, chash, author, message, pushed_at = row
    print(f'id={id} project_id={project_id} hash={chash} author={author} pushed_at={pushed_at}')
    print(message[:200])
    print('---')

conn.close()
