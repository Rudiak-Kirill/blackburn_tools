"""Get chat_id values from bot updates (uses TELEGRAM_BOT_TOKEN).

Usage:
  - Ensure `TELEGRAM_BOT_TOKEN` is set in environment or in `.env`/`.env.example`.
  - Run: `python scripts/get_chat_id_from_updates.py`

The script calls `getUpdates` and prints unique chat ids and basic info.
"""
import os
import sys
import json
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]


def load_token() -> str | None:
    # 1) env var
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if token:
        return token

    # 2) try app settings if available
    try:
        sys.path.insert(0, str(ROOT))
        from app.core.config import settings
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if token:
            return token
    except Exception:
        pass

    # 3) fallback to .env.example
    p = ROOT / '.env.example'
    if p.exists():
        with p.open('r', encoding='utf-8') as f:
            for line in f:
                s = line.strip()
                if s.startswith('TELEGRAM_BOT_TOKEN='):
                    return s.split('=', 1)[1] or None

    return None


def main():
    token = load_token()
    if not token:
        print('No TELEGRAM_BOT_TOKEN found in env, .env or .env.example')
        print('Set TELEGRAM_BOT_TOKEN and try again.')
        return 1

    url = f'https://api.telegram.org/bot{token}/getUpdates'
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print('Request to getUpdates failed:', e)
        return 2

    if not data.get('ok'):
        print('Telegram API returned error:', data)
        return 3

    updates = data.get('result', [])
    if not updates:
        print('No updates found. To capture chat_id: send a message to the bot or add the bot to a chat, then run this script again.')
        return 0

    chats = {}
    for upd in updates:
        # messages can be in 'message', 'edited_message', 'channel_post', 'callback_query'
        for key in ('message', 'edited_message', 'channel_post', 'callback_query'):
            obj = upd.get(key)
            if not obj:
                continue

            # callback_query wraps message in 'message' field
            if key == 'callback_query':
                obj = obj.get('message') or obj

            chat = obj.get('chat') if isinstance(obj, dict) else None
            if not chat:
                continue

            cid = chat.get('id')
            if cid in chats:
                continue

            chats[cid] = {
                'type': chat.get('type'),
                'title': chat.get('title'),
                'username': chat.get('username'),
                'first_name': chat.get('first_name'),
                'last_name': chat.get('last_name'),
                'sample_text': obj.get('text') if isinstance(obj, dict) else None,
            }

    print('\nFound chat ids:')
    for cid, info in chats.items():
        print(f'- {cid} ({info.get("type")}) title={info.get("title")} username={info.get("username")} name={info.get("first_name")} {info.get("last_name")} sample_text={repr(info.get("sample_text"))}')

    print('\nTip: For channels use chat_id of form -100<id> (numeric). If you don\'t see expected chat, send a message to the bot or add it to the chat, then run again.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
