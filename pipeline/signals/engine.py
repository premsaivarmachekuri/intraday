"""
Signal engine: loads data from SQLite, runs Livermore + Simons, combines scores.
"""

import os
import sys
import csv
import sqlite3
import pandas as pd
import numpy as np
from typing import Optional

from signals.livermore import score_livermore
from signals.simons import score_simons
from signals.sector_map import get_sector, get_sister_stocks, get_sector_index, get_stock_info

# Free-tier safe limits (wiki plan §"For free TradingView accounts")
DAILY_LIMIT = 300
MIN5_LIMIT = 800


def _sqlite_to_df(rows: list, ts_col: str = 'ts') -> Optional[pd.DataFrame]:
    if not rows:
        return None
    df = pd.DataFrame(rows, columns=[ts_col, 'open', 'high', 'low', 'close', 'volume'])
    df[ts_col] = pd.to_datetime(df[ts_col])
    df = df.set_index(ts_col).sort_index()
    df = df.astype(float)
    return df if len(df) >= 5 else None


def load_instrument_data(
    db_path: str,
    symbol: str,
    exchange: str,
    daily_limit: int = DAILY_LIMIT,
    min5_limit: int = MIN5_LIMIT,
) -> dict:
    """Load daily + 5min candles from SQLite as pandas DataFrames."""
    con = sqlite3.connect(db_path)
    try:
        daily_rows = con.execute(
            f"""SELECT date, open, high, low, close, volume
                FROM candles_daily
                WHERE symbol=? AND exchange=?
                ORDER BY date DESC LIMIT {daily_limit}""",
            (symbol, exchange),
        ).fetchall()

        min5_rows = con.execute(
            f"""SELECT datetime, open, high, low, close, volume
                FROM candles_5min
                WHERE symbol=? AND exchange=?
                ORDER BY datetime DESC LIMIT {min5_limit}""",
            (symbol, exchange),
        ).fetchall()
    finally:
        con.close()

    return {
        'daily': _sqlite_to_df(list(reversed(daily_rows))),
        'min5': _sqlite_to_df(list(reversed(min5_rows))),
    }


def _read_csv_symbols(symbols_dir: str) -> list:
    instruments = []
    nse_csv = os.path.join(symbols_dir, 'nse_fno.csv')
    mcx_csv = os.path.join(symbols_dir, 'mcx.csv')
    idx_csv = os.path.join(symbols_dir, 'indexes.csv')

    with open(nse_csv, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            instruments.append({
                'symbol': row['symbol'], 'exchange': 'NSE',
                'name': row['name'], 'sector': row['sector'],
                'is_index': False,
            })
    with open(mcx_csv, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            instruments.append({
                'symbol': row['symbol'], 'exchange': 'MCX',
                'name': row['name'], 'sector': 'MCX',
                'is_index': False,
            })
    return instruments


def format_result(result: dict) -> dict:
    """Return structured dict for one instrument in a consistent format."""
    l = result.get('livermore', {})
    s = result.get('simons', {})
    entry = l.get('entry_zone', (0, 0))
    entry_mid = (entry[0] + entry[1]) / 2 if entry[1] > 0 else 0
    stop = l.get('stop_loss', 0)
    risk_pct = abs(entry_mid - stop) / entry_mid * 100 if entry_mid > 0 else 0

    return {
        'symbol': result['symbol'],
        'exchange': result['exchange'],
        'name': result['name'],
        'sector': result['sector'],
        'direction': result['direction'],
        'combined_score': result['combined_score'],
        'livermore_score': l.get('score', 0),
        'simons_score': s.get('score', 0),
        'entry_zone': entry,
        'stop_loss': stop,
        'risk_pct': round(risk_pct, 2),
        'livermore_signals': l.get('signals_triggered', []),
        'simons_signals': s.get('signals', {}),
        'livermore_explanation': l.get('explanation', ''),
        'simons_explanation': s.get('explanation', ''),
        'combined_explanation': result.get('combined_explanation', ''),
        'regime': s.get('regime', 'UNKNOWN'),
        'alignment': l.get('alignment', {}),
    }


def run_full_scan(db_path: str, symbols_dir: str) -> list:
    """
    For each instrument:
    1. Load OHLCV from SQLite
    2. Load sector index + sister stocks
    3. Run score_livermore() + score_simons()
    4. Combined score = 0.5 * livermore + 0.5 * simons
    5. Direction: both agree, OR one is strong (>7) and other neutral
    Returns sorted list of opportunities (LONG or SHORT only, score > 3).
    """
    instruments = _read_csv_symbols(symbols_dir)
    results = []

    # Cache loaded dataframes to avoid re-reading the same index/sister
    _df_cache = {}

    def get_df(sym, exch):
        key = (sym, exch)
        if key not in _df_cache:
            data = load_instrument_data(db_path, sym, exch)
            _df_cache[key] = data.get('daily')
        return _df_cache[key]

    print(f"[engine] Scanning {len(instruments)} instruments...")
    for i, inst in enumerate(instruments):
        sym = inst['symbol']
        exch = inst['exchange']

        try:
            sym_data = load_instrument_data(db_path, sym, exch)
            sym_df = sym_data.get('daily')

            if sym_df is None or len(sym_df) < 22:
                continue

            # Load sector index
            sector = inst['sector']
            sector_idx_sym = get_sector_index(sector)
            sector_idx_exch = 'MCX' if sector == 'MCX' else 'NSE'
            sector_df = get_df(sector_idx_sym, sector_idx_exch)

            # Load sister stocks
            sisters = get_sister_stocks(sym)
            sister1_df = get_df(sisters[0], 'NSE') if len(sisters) > 0 else None
            sister2_df = get_df(sisters[1], 'NSE') if len(sisters) > 1 else None

            # Market (NIFTY50)
            market_df = get_df('NIFTY50', 'NSE')

            # Run engines
            lv = score_livermore(sym, sym_df, market_df, sector_df, sister1_df, sister2_df)
            sm = score_simons(sym, sym_df, sector_df)

            # Combine scores
            # wiki plan: "Combined score = (livermore_score * 0.5) + (simons_score * 0.5)"
            combined = round(lv['score'] * 0.5 + sm['score'] * 0.5, 2)

            # Direction logic:
            # wiki plan: "only flag if both agree OR one is strong (>7) and other neutral"
            ld, sd = lv['direction'], sm['direction']
            if ld == sd and ld != 'NEUTRAL':
                direction = ld
            elif lv['score'] > 7 and sd == 'NEUTRAL':
                direction = ld
            elif sm['score'] > 7 and ld == 'NEUTRAL':
                direction = sd
            elif ld != 'NEUTRAL' and sd != 'NEUTRAL' and ld != sd:
                direction = 'NEUTRAL'  # conflicting — skip
            else:
                direction = 'NEUTRAL'

            if direction == 'NEUTRAL' or combined < 3:
                continue

            combined_explanation = (
                f"{lv['explanation']} | {sm['explanation']}"
            )

            results.append({
                'symbol': sym,
                'exchange': exch,
                'name': inst['name'],
                'sector': sector,
                'direction': direction,
                'combined_score': combined,
                'livermore': lv,
                'simons': sm,
                'combined_explanation': combined_explanation,
            })

            if (i + 1) % 20 == 0:
                print(f"[engine] Processed {i + 1}/{len(instruments)}...")

        except Exception as e:
            print(f"[engine] Error on {sym}: {e}", file=sys.stderr)
            continue

    results.sort(key=lambda x: x['combined_score'], reverse=True)
    print(f"[engine] Scan complete. {len(results)} opportunities found.")
    return [format_result(r) for r in results]
