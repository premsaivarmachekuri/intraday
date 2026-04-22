"""
Python entry point: read SQLite → signals → Telegram report.
Run after main.js has fetched market data.
"""

import os
import sys

# Allow imports from pipeline root
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from signals.engine import run_full_scan, load_instrument_data
from report.formatter import format_report
from report.sender import send_report

DB_PATH = os.environ.get('DB_PATH', 'data/market.db')
SYMBOLS_DIR = os.path.join(os.path.dirname(__file__), 'symbols')
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')


def main():
    print('[main.py] Starting signal engine...')

    if not os.path.exists(DB_PATH):
        print(f'[main.py] ERROR: Database not found at {DB_PATH}. Run node main.js first.')
        sys.exit(1)

    # Run full scan
    results = run_full_scan(DB_PATH, SYMBOLS_DIR)
    print(f'[main.py] {len(results)} opportunities identified.')

    # Load NIFTY50 + BANKNIFTY data for market overview
    nifty_data = load_instrument_data(DB_PATH, 'NIFTY50', 'NSE')
    bank_data = load_instrument_data(DB_PATH, 'BANKNIFTY', 'NSE')
    nifty_df = nifty_data.get('daily')
    bank_df = bank_data.get('daily')

    # Format messages
    messages = format_report(results, nifty_df, bank_df)
    print(f'[main.py] Formatted {len(messages)} Telegram message(s).')

    # Send
    if not BOT_TOKEN or not CHAT_ID:
        print('[main.py] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set — printing to stdout instead.')
        for i, msg in enumerate(messages, 1):
            print(f'\n--- Message {i} ---\n{msg}')
        sys.exit(0)

    print(f'[main.py] Sending to Telegram chat {CHAT_ID}...')
    ok = send_report(messages, BOT_TOKEN, CHAT_ID)
    if ok:
        print('[main.py] Report sent successfully.')
    else:
        print('[main.py] Some messages failed to send.', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
