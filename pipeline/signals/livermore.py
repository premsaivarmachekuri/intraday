"""
Jesse Livermore signal engine.
All rules and thresholds are sourced from:
  wiki/pioneers/jesse-livermore.md
"""

import numpy as np
import pandas as pd
from typing import Optional

# ---------------------------------------------------------------------------
# wiki §"The Livermore Secret Market Key (6-Point System)"
# "A move of ≥6 points from an extreme price triggers a column change"
# ---------------------------------------------------------------------------
PIVOT_THRESHOLD = 6.0        # points for stocks > ₹30
PIVOT_THRESHOLD_LOW = 1.0    # scaled for stocks ≤ ₹30 (proportional)
BREAKOUT_VOL_MULT = 1.5      # wiki §"Break-Out to New High": ≥50% above avg daily volume
PIVOT_ENTRY_MAX_PCT = 0.10   # wiki §"Entry Rules": buy within 5%-10% of Pivotal Point
STOP_LOSS_PCT = 0.10         # wiki §"10% Maximum Loss Rule"
RESUMPTION_PTS = 3.0         # wiki: "new move must extend ≥3 points beyond prior Pivotal Point"
NEW_HIGH_LOOKBACK = 252      # trading days (~1 year)
VOLUME_CLIMAX_WINDOW = 5     # wiki §"Spike + Volume Climax"
ROUND_NUMBERS = [10, 20, 50, 100, 200, 300, 500, 1000, 2000, 5000, 10000]
TIME_STOP_DAYS = 5           # wiki §"Time Stop": ~5 trading days


class LivermoreMarketKey:
    """
    Implements the 6-column Livermore Secret Market Key state machine.
    wiki/pioneers/jesse-livermore.md §"The Livermore Secret Market Key (6-Point System)"

    Columns (index 0-5):
      0 secondary_rally
      1 natural_rally
      2 upward_trend
      3 downward_trend
      4 natural_reaction
      5 secondary_reaction
    """

    COLUMNS = [
        'secondary_rally', 'natural_rally', 'upward_trend',
        'downward_trend', 'natural_reaction', 'secondary_reaction'
    ]
    UPTREND_COLS  = {0, 1, 2}
    DOWNTREND_COLS = {3, 4, 5}

    def __init__(self, price: float):
        # Determine threshold based on price level
        self.threshold = PIVOT_THRESHOLD if price > 30 else PIVOT_THRESHOLD_LOW
        self.col = 2  # start in upward_trend
        self.last_entry = price
        self.extreme = price   # highest in uptrend / lowest in downtrend
        self.pivotal_points: list = []  # [(price, type, index)]
        self._history: list = [(price, 2)]  # (price, col_index)

    def update(self, price: float, idx=None) -> int:
        """
        Process a new price. Returns current column index (0-5).
        wiki §"Complete Column-Change Rules"
        """
        col = self.col
        th = self.threshold

        if col == 2:  # upward_trend
            if price >= self.last_entry:
                self.last_entry = price
                self.extreme = price
            elif self.extreme - price >= th:
                # Shift to natural_reaction (col 4) — mark Pivotal Point
                self._mark_pivot(self.extreme, 'uptrend_top', idx)
                self.col = 4
                self.last_entry = price
                self.extreme = price

        elif col == 3:  # downward_trend
            if price <= self.last_entry:
                self.last_entry = price
                self.extreme = price
            elif price - self.extreme >= th:
                # Shift to natural_rally (col 1) — mark Pivotal Point
                self._mark_pivot(self.extreme, 'downtrend_bottom', idx)
                self.col = 1
                self.last_entry = price
                self.extreme = price

        elif col == 1:  # natural_rally
            last_ut = self._last_in_col(2)
            if last_ut and price > last_ut:
                # Exceeded last upward_trend entry → resume upward_trend
                self.col = 2
                self.last_entry = price
                self.extreme = price
            elif self.last_entry - price >= th:
                # Dropped th from natural_rally entry → natural_reaction
                nr_low = self._last_in_col(4)
                if nr_low and price < nr_low:
                    # Broke below natural_reaction → downward_trend
                    self._mark_pivot(self.last_entry, 'rally_top', idx)
                    self.col = 3
                else:
                    self.col = 5  # secondary_reaction
                self.last_entry = price
                self.extreme = min(self.extreme, price)

        elif col == 4:  # natural_reaction
            last_dt = self._last_in_col(3)
            if last_dt and price < last_dt:
                # Broke below last downward_trend → resume downward_trend
                self.col = 3
                self.last_entry = price
                self.extreme = price
            elif price - self.last_entry >= th:
                # Rallied th → natural_rally
                nr_high = self._last_in_col(1)
                if nr_high and price > nr_high:
                    # Exceeded natural_rally → upward_trend
                    self._mark_pivot(self.last_entry, 'reaction_bottom', idx)
                    self.col = 2
                else:
                    self.col = 0  # secondary_rally
                self.last_entry = price
                self.extreme = max(self.extreme, price)

        elif col == 0:  # secondary_rally
            nr_high = self._last_in_col(1)
            if nr_high and price > nr_high:
                self.col = 1
            elif self.last_entry - price >= th:
                self.col = 5
                self.last_entry = price

        elif col == 5:  # secondary_reaction
            nr_low = self._last_in_col(4)
            if nr_low and price < nr_low:
                self.col = 4
            elif price - self.last_entry >= th:
                self.col = 0
                self.last_entry = price

        self._history.append((price, self.col))
        return self.col

    def _mark_pivot(self, price, kind, idx):
        self.pivotal_points.append({'price': price, 'type': kind, 'idx': idx})

    def _last_in_col(self, col_idx):
        for price, c in reversed(self._history):
            if c == col_idx:
                return price
        return None

    def get_pivotal_points(self) -> list:
        return self.pivotal_points

    def get_current_state(self) -> dict:
        return {
            'column': self.COLUMNS[self.col],
            'col_idx': self.col,
            'last_entry': self.last_entry,
            'extreme': self.extreme,
            'pivotal_points': self.pivotal_points,
            'in_uptrend': self.col in self.UPTREND_COLS,
            'in_downtrend': self.col in self.DOWNTREND_COLS,
        }


# ---------------------------------------------------------------------------
# Pattern detectors — all return {signal, strength, explanation}
# ---------------------------------------------------------------------------

def detect_one_day_reversal(df: pd.DataFrame) -> dict:
    """
    wiki §"One-Day Reversal (Danger Signal)"
    Conditions: today high > prev high AND today close < prev close AND today volume > prev volume
    """
    if len(df) < 2:
        return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'Insufficient data'}
    r, p = df.iloc[-1], df.iloc[-2]
    triggered = (
        r['high'] > p['high'] and
        r['close'] < p['close'] and
        r['volume'] > p['volume']
    )
    if triggered:
        vol_ratio = r['volume'] / p['volume'] if p['volume'] > 0 else 1
        return {
            'signal': 'SHORT',
            'strength': min(10, 5 + vol_ratio * 2),
            'explanation': (
                f"One-Day Reversal: new high {r['high']:.2f} > {p['high']:.2f}, "
                f"close fell to {r['close']:.2f}, volume {vol_ratio:.1f}x — distribution signal "
                f"(wiki §One-Day Reversal)"
            ),
        }
    return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'No one-day reversal'}


def detect_pivotal_breakout(df: pd.DataFrame, market_key: LivermoreMarketKey) -> dict:
    """
    wiki §"Reversal Pivotal Point": price crosses above Pivotal Point on volume ≥150% of 20d avg.
    Volume criterion from wiki: "50%-500% increase in average daily volume"
    """
    if len(df) < 21:
        return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'Insufficient data'}

    pivots = market_key.get_pivotal_points()
    if not pivots:
        return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'No pivotal points established yet'}

    last_pivot = pivots[-1]['price']
    vol_avg_20 = df['volume'].iloc[-21:-1].mean()
    r = df.iloc[-1]

    vol_ok = r['volume'] >= vol_avg_20 * BREAKOUT_VOL_MULT  # ≥150% of 20d avg
    price_ok = r['close'] > last_pivot and r['close'] <= last_pivot * (1 + PIVOT_ENTRY_MAX_PCT)
    within_entry = r['close'] <= last_pivot * (1 + PIVOT_ENTRY_MAX_PCT)

    if vol_ok and price_ok and within_entry:
        strength = min(10, 6 + (r['volume'] / vol_avg_20 - 1.5) * 2)
        return {
            'signal': 'LONG',
            'strength': strength,
            'explanation': (
                f"Pivotal Breakout at {r['close']:.2f} above pivot {last_pivot:.2f}, "
                f"volume {r['volume']/vol_avg_20:.1f}x avg — within 5-10% entry zone "
                f"(wiki §Reversal Pivotal Point)"
            ),
        }
    return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'No pivotal breakout setup'}


def detect_new_52w_high(df: pd.DataFrame) -> dict:
    """
    wiki §"Break-Out to New High": today high > 252-day rolling high on volume ≥150% of 20d avg.
    "Buy when a stock breaks to a new all-time high on heavy volume (≥50% above average daily volume)"
    """
    if len(df) < 22:
        return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'Insufficient data'}

    lookback = min(NEW_HIGH_LOOKBACK, len(df) - 1)
    hist_high = df['high'].iloc[-(lookback + 1):-1].max()
    vol_avg = df['volume'].iloc[-21:-1].mean()
    r = df.iloc[-1]

    if r['high'] > hist_high and r['volume'] >= vol_avg * BREAKOUT_VOL_MULT:
        return {
            'signal': 'LONG',
            'strength': 8,
            'explanation': (
                f"New {lookback}d high at {r['high']:.2f} (prev {hist_high:.2f}), "
                f"volume {r['volume']/vol_avg:.1f}x avg — clear air above "
                f"(wiki §Break-Out to New High)"
            ),
        }
    return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'No new 52-week high breakout'}


def detect_continuation_pivot(df: pd.DataFrame, market_key: LivermoreMarketKey) -> dict:
    """
    wiki §"Continuation Pivotal Point": consolidation (volume dry-up) then breakout in trend direction.
    """
    if len(df) < 10:
        return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'Insufficient data'}

    state = market_key.get_current_state()
    recent_vol = df['volume'].iloc[-6:-1]
    avg_vol = df['volume'].iloc[-21:-6].mean() if len(df) >= 21 else df['volume'].mean()
    vol_dry_up = recent_vol.mean() < avg_vol * 0.7  # volume dried up to <70% of average
    r = df.iloc[-1]
    vol_breakout = r['volume'] > avg_vol * BREAKOUT_VOL_MULT

    if vol_dry_up and vol_breakout:
        direction = 'LONG' if state['in_uptrend'] else 'SHORT'
        return {
            'signal': direction,
            'strength': 7,
            'explanation': (
                f"Continuation Pivot: 5d volume dried to {recent_vol.mean()/avg_vol:.0%} of avg, "
                f"today breakout at {r['volume']/avg_vol:.1f}x — trend intact in {state['column']} "
                f"(wiki §Continuation Pivotal Point)"
            ),
        }
    return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'No continuation pivot setup'}


def detect_round_number_breakout(df: pd.DataFrame) -> dict:
    """
    wiki §"Round-Number Pivotal Points": price crossed a round number within last 3 days.
    "Stocks approaching round numbers almost invariably produce fast, straight movements once crossed"
    """
    if len(df) < 5:
        return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'Insufficient data'}

    recent = df.iloc[-4:]
    for rn in sorted(ROUND_NUMBERS, reverse=True):
        crossed = (
            recent['low'].min() <= rn and
            recent['close'].iloc[-1] > rn and
            recent['close'].iloc[0] <= rn
        )
        if crossed:
            r = df.iloc[-1]
            return {
                'signal': 'LONG',
                'strength': 7,
                'explanation': (
                    f"Round-Number Breakout: price crossed {rn} within last 3 days, "
                    f"current close {r['close']:.2f} — supply cleared "
                    f"(wiki §Round-Number Pivotal Points)"
                ),
            }
    return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'No round-number breakout'}


def detect_false_pivot_short(df: pd.DataFrame, market_key: LivermoreMarketKey) -> dict:
    """
    wiki §"False Pivotal Point (Short-Selling Signal)":
    Rally from multi-year low fails, then new low is made → short.
    """
    if len(df) < 30:
        return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'Insufficient data'}

    long_low = df['low'].min()
    recent_high = df['high'].iloc[-15:].max()
    recent_low = df['low'].iloc[-5:].min()
    prev_low = df['low'].iloc[-30:-15].min()

    # Rally from multi-year low (within 15% of all-time low in dataset)
    near_atr_low = df['close'].iloc[-20] < long_low * 1.15
    # Rally then new low
    rally_then_lower = recent_high > df['close'].iloc[-20] and recent_low < prev_low

    if near_atr_low and rally_then_lower:
        return {
            'signal': 'SHORT',
            'strength': 7.5,
            'explanation': (
                f"False Pivotal: rallied from near multi-year low {long_low:.2f}, "
                f"now breaking to new low {recent_low:.2f} — real buyers absent "
                f"(wiki §False Pivotal Point)"
            ),
        }
    return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'No false pivot setup'}


def detect_volume_climax(df: pd.DataFrame) -> dict:
    """
    wiki §"Spike + Volume Climax (Distribution Warning)":
    Last 5 days: spike + heavy volume + no new high → distribution.
    """
    if len(df) < 26:
        return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'Insufficient data'}

    recent = df.iloc[-VOLUME_CLIMAX_WINDOW:]
    prior = df.iloc[-(VOLUME_CLIMAX_WINDOW + 20):-VOLUME_CLIMAX_WINDOW]
    avg_vol = prior['volume'].mean()
    max_recent_vol = recent['volume'].max()
    # Spike: price rose sharply in window
    price_spike = recent['high'].max() > prior['high'].max()
    heavy_vol = max_recent_vol > avg_vol * 2.0
    # No new high: most recent close below the spike high
    no_new_high = recent['close'].iloc[-1] < recent['high'].max() * 0.97

    if price_spike and heavy_vol and no_new_high:
        return {
            'signal': 'SHORT',
            'strength': 7,
            'explanation': (
                f"Volume Climax: spike to {recent['high'].max():.2f} on {max_recent_vol/avg_vol:.1f}x vol, "
                f"price rolled back — distribution signal "
                f"(wiki §Spike + Volume Climax)"
            ),
        }
    return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'No volume climax detected'}


def detect_time_stop(df: pd.DataFrame, entry_price: float) -> dict:
    """
    wiki §"Time Stop": 5 trading days elapsed, no meaningful progress → exit.
    """
    if len(df) < TIME_STOP_DAYS:
        return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'Not enough data'}
    recent = df.iloc[-TIME_STOP_DAYS:]
    progress = abs(recent['close'].iloc[-1] - entry_price) / entry_price
    if progress < 0.02:
        return {
            'signal': 'EXIT',
            'strength': 6,
            'explanation': (
                f"Time Stop triggered: {TIME_STOP_DAYS} days elapsed, "
                f"only {progress:.1%} move from entry {entry_price:.2f} "
                f"(wiki §Time Stop)"
            ),
        }
    return {'signal': 'NEUTRAL', 'strength': 0, 'explanation': 'Position still active'}


# ---------------------------------------------------------------------------
# Multi-timeframe alignment
# wiki §"Multi-Timeframe Logic"
# ---------------------------------------------------------------------------

def _trend_direction(df: pd.DataFrame) -> str:
    """Simple trend: compare recent 20-day SMA vs 50-day SMA."""
    if len(df) < 51:
        return 'SIDEWAYS'
    sma20 = df['close'].iloc[-20:].mean()
    sma50 = df['close'].iloc[-50:].mean()
    if sma20 > sma50 * 1.01:
        return 'UP'
    if sma20 < sma50 * 0.99:
        return 'DOWN'
    return 'SIDEWAYS'


def check_livermore_alignment(
    symbol: str,
    symbol_df: pd.DataFrame,
    market_df: pd.DataFrame,
    sector_df: pd.DataFrame,
    sister1_df: Optional[pd.DataFrame],
    sister2_df: Optional[pd.DataFrame],
) -> dict:
    """
    wiki §"Multi-Timeframe Logic":
      L1: NIFTY50 trend direction
      L2: sector index trend — must match L1
      L3: sister stock signals — ≥1 of 2 must confirm
      L4: individual stock signal
    """
    market_trend = _trend_direction(market_df) if market_df is not None and len(market_df) > 50 else 'UNKNOWN'
    sector_trend = _trend_direction(sector_df) if sector_df is not None and len(sector_df) > 50 else 'UNKNOWN'
    stock_trend = _trend_direction(symbol_df)

    # Sister confirmation
    sister_signals = []
    for sdf in [sister1_df, sister2_df]:
        if sdf is not None and len(sdf) > 20:
            sister_signals.append(_trend_direction(sdf))
    sister_confirm = any(s == stock_trend for s in sister_signals)

    aligned = (
        market_trend == stock_trend and
        (sector_trend == stock_trend or sector_trend == 'SIDEWAYS') and
        sister_confirm
    )

    return {
        'aligned': aligned,
        'market_trend': market_trend,
        'sector_trend': sector_trend,
        'stock_trend': stock_trend,
        'sister_confirmation': sister_confirm,
        'sister_signals': sister_signals,
        'explanation': (
            f"Market={market_trend}, Sector={sector_trend}, "
            f"Stock={stock_trend}, SisterConfirm={sister_confirm}"
        ),
    }


# ---------------------------------------------------------------------------
# Master scoring function
# ---------------------------------------------------------------------------

def score_livermore(
    symbol: str,
    symbol_df: pd.DataFrame,
    market_df: Optional[pd.DataFrame] = None,
    sector_df: Optional[pd.DataFrame] = None,
    sister1_df: Optional[pd.DataFrame] = None,
    sister2_df: Optional[pd.DataFrame] = None,
) -> dict:
    """
    Aggregate all Livermore signals for one instrument.
    Returns score 0-10, direction, entry_zone, stop_loss, and explanations.
    """
    if symbol_df is None or len(symbol_df) < 22:
        return {
            'score': 0, 'direction': 'NEUTRAL',
            'signals_triggered': [], 'entry_zone': (0, 0),
            'stop_loss': 0, 'alignment': {}, 'explanation': 'Insufficient data',
        }

    last_price = float(symbol_df['close'].iloc[-1])

    # Build Market Key from full history
    mk = LivermoreMarketKey(float(symbol_df['close'].iloc[0]))
    for i, row in symbol_df.iterrows():
        mk.update(float(row['close']), i)

    # Run all detectors
    detectors = [
        ('one_day_reversal', detect_one_day_reversal(symbol_df)),
        ('pivotal_breakout', detect_pivotal_breakout(symbol_df, mk)),
        ('new_52w_high', detect_new_52w_high(symbol_df)),
        ('continuation_pivot', detect_continuation_pivot(symbol_df, mk)),
        ('round_number_breakout', detect_round_number_breakout(symbol_df)),
        ('false_pivot_short', detect_false_pivot_short(symbol_df, mk)),
        ('volume_climax', detect_volume_climax(symbol_df)),
    ]

    long_score = sum(d['strength'] for _, d in detectors if d['signal'] == 'LONG')
    short_score = sum(d['strength'] for _, d in detectors if d['signal'] == 'SHORT')
    signals_triggered = [
        {'name': name, **det}
        for name, det in detectors
        if det['signal'] != 'NEUTRAL'
    ]

    # Determine direction
    if long_score > short_score and long_score > 0:
        direction = 'LONG'
        raw_score = min(10, long_score / 2)
    elif short_score > long_score and short_score > 0:
        direction = 'SHORT'
        raw_score = min(10, short_score / 2)
    else:
        direction = 'NEUTRAL'
        raw_score = 0

    # Multi-timeframe alignment (wiki §Multi-Timeframe Logic)
    alignment = check_livermore_alignment(
        symbol, symbol_df, market_df, sector_df, sister1_df, sister2_df
    )
    # Alignment bonus/penalty
    if alignment.get('aligned') and direction != 'NEUTRAL':
        raw_score = min(10, raw_score * 1.3)
    elif not alignment.get('aligned') and direction != 'NEUTRAL':
        raw_score *= 0.7

    # Entry zone: within 5%-10% of last pivotal point (wiki §Entry Rules)
    pivots = mk.get_pivotal_points()
    if pivots:
        pivot_price = pivots[-1]['price']
    else:
        pivot_price = last_price
    entry_low = pivot_price * (1 + 0.005)
    entry_high = pivot_price * (1 + PIVOT_ENTRY_MAX_PCT)

    # Stop loss: 10% below entry (wiki §"10% Maximum Loss Rule")
    stop_loss = entry_low * (1 - STOP_LOSS_PCT)

    # Explanation
    sig_names = [s['name'] for s in signals_triggered]
    explanation = (
        f"Livermore: {direction} (score={raw_score:.1f}/10). "
        f"Signals: {', '.join(sig_names) or 'none'}. "
        f"{alignment['explanation']}"
    )

    return {
        'score': round(raw_score, 2),
        'direction': direction,
        'signals_triggered': signals_triggered,
        'entry_zone': (round(entry_low, 2), round(entry_high, 2)),
        'stop_loss': round(stop_loss, 2),
        'alignment': alignment,
        'explanation': explanation,
        'market_key_state': mk.get_current_state(),
    }
