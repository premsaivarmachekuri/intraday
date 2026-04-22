"""
Telegram message sender.
"""

import time
import sys
import requests


def send_report(messages: list, bot_token: str, chat_id: str) -> bool:
    """
    Send list of message strings to Telegram via Bot API.
    0.5s delay between messages to avoid flood limits.
    Retries once after 2s on HTTP error.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    success = True

    for i, text in enumerate(messages):
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True,
        }
        sent = _send_one(url, payload)
        if not sent:
            print(f"[sender] Failed to send message {i + 1}/{len(messages)}", file=sys.stderr)
            success = False
        if i < len(messages) - 1:
            time.sleep(0.5)

    return success


def _send_one(url: str, payload: dict) -> bool:
    """Attempt to POST one message; retry once on failure."""
    for attempt in range(2):
        try:
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                return True
            print(f"[sender] HTTP {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
        except requests.RequestException as e:
            print(f"[sender] Request error: {e}", file=sys.stderr)
        if attempt == 0:
            time.sleep(2)
    return False
