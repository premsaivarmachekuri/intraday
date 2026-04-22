"""
Jim Simons / Renaissance Technologies signal engine.
All rules and thresholds are sourced from:
  wiki/pioneers/jim-simons.md
"""

import warnings
import numpy as np
import pandas as pd
from typing import Optional

warnings.filterwarnings('ignore', category=RuntimeWarning)

# ---------------------------------------------------------------------------
# Thresholds — cited per wiki section
# ---------------------------------------------------------------------------
# wiki §"Short-term mean reversion": Z-score thresholds
MR_Z_BUY = -1.5
MR_Z_SELL = 1.5
MR_LOOKBACK = 20
MR_RETURN_DAYS = 5

# wiki §"Serial correlation by asset class — Equity individual stocks: ~1%"
SC_WINDOW = 20

# wiki §"Weekend effect": Friday-to-Monday pattern
# wiki §"Relative, not absolute, price prediction"
REL_PERF_WINDOW = 10
REL_Z_THRESHOLD = 1.5

# wiki §"Volume anomaly / Price & Volume": volume Z-score
VOL_Z_THRESHOLD = 2.0

# wiki §"Hidden-state regime detection" via HMM
HMM_STATES = 3
HMM_LOOKBACK = 60


def _returns(df: pd.DataFrame, n: int = 1) -> pd.Series:
    return df['close'].pct_change(n).dropna()


# ---------------------------------------------------------------------------
# 1. Mean reversion Z-score
# wiki §"Short-term mean reversion (bedrock signal)": prices that deviate from
# their recent historical norm tend to revert. Z < -1.5 → oversold (buy),
# Z > 1.5 → overbought (sell).
# ---------------------------------------------------------------------------
def mean_reversion_zscore(df: pd.DataFrame, lookback: int = MR_LOOKBACK) -> dict:
    if len(df) < lookback + MR_RETURN_DAYS + 1:
        return {'zscore': 0, 'signal': 'NEUTRAL', 'strength': 0}

    ret_5d = df['close'].pct_change(MR_RETURN_DAYS).dropna()
    if len(ret_5d) < lookback:
        return {'zscore': 0, 'signal': 'NEUTRAL', 'strength': 0}

    recent = float(ret_5d.iloc[-1])
    window = ret_5d.iloc[-(lookback + 1):-1]
    mu, sigma = window.mean(), window.std()
    if sigma < 1e-9:
        return {'zscore': 0, 'signal': 'NEUTRAL', 'strength': 0}

    z = (recent - mu) / sigma

    if z < MR_Z_BUY:
        signal, strength = 'LONG', min(10, abs(z) * 3)
    elif z > MR_Z_SELL:
        signal, strength = 'SHORT', min(10, abs(z) * 3)
    else:
        signal, strength = 'NEUTRAL', 0

    return {
        'zscore': round(z, 3),
        'signal': signal,
        'strength': round(strength, 2),
        'explanation': (
            f"Mean reversion Z={z:.2f} (threshold ±{MR_Z_SELL}) "
            f"(wiki §Short-term mean reversion)"
        ),
    }


# ---------------------------------------------------------------------------
# 2. Serial correlation
# wiki §"Serial correlation by asset class": lag-1 autocorrelation of daily returns.
# Positive autocorr + upward trend → momentum continuation.
# Negative autocorr → mean reversion expected.
# ---------------------------------------------------------------------------
def serial_correlation(df: pd.DataFrame, window: int = SC_WINDOW) -> dict:
    if len(df) < window + 2:
        return {'autocorr': 0, 'signal': 'NEUTRAL', 'strength': 0}

    rets = _returns(df)
    if len(rets) < window:
        return {'autocorr': 0, 'signal': 'NEUTRAL', 'strength': 0}

    r = rets.iloc[-window:]
    # lag-1 autocorrelation
    ac = float(r.autocorr(lag=1)) if len(r) > 2 else 0
    if np.isnan(ac):
        ac = 0

    trend_up = df['close'].iloc[-1] > df['close'].iloc[-window]

    if ac > 0.05 and trend_up:
        signal, strength = 'LONG', min(10, ac * 50)
    elif ac > 0.05 and not trend_up:
        signal, strength = 'SHORT', min(10, ac * 50)
    elif ac < -0.05:
        # Negative autocorr → mean reversion
        signal = 'LONG' if df['close'].iloc[-1] < df['close'].iloc[-5] else 'SHORT'
        strength = min(10, abs(ac) * 30)
    else:
        signal, strength = 'NEUTRAL', 0

    return {
        'autocorr': round(ac, 4),
        'signal': signal,
        'strength': round(strength, 2),
        'explanation': (
            f"Serial corr lag-1={ac:.4f}, trend_up={trend_up} "
            f"(wiki §Serial correlation)"
        ),
    }


# ---------------------------------------------------------------------------
# 3. Relative performance
# wiki §"Relative, not absolute, price prediction": Z-score of symbol's 5-day
# return minus sector index 5-day return.
# ---------------------------------------------------------------------------
def relative_performance(
    symbol_df: pd.DataFrame,
    index_df: Optional[pd.DataFrame],
    window: int = REL_PERF_WINDOW,
) -> dict:
    if index_df is None or len(symbol_df) < window + 6 or len(index_df) < window + 6:
        return {'rel_return': 0, 'zscore': 0, 'signal': 'NEUTRAL', 'strength': 0}

    sym_r5 = symbol_df['close'].pct_change(5).dropna()
    idx_r5 = index_df['close'].pct_change(5).dropna()

    # Align on common length
    min_len = min(len(sym_r5), len(idx_r5))
    if min_len < window:
        return {'rel_return': 0, 'zscore': 0, 'signal': 'NEUTRAL', 'strength': 0}

    spread = sym_r5.iloc[-min_len:].values - idx_r5.iloc[-min_len:].values
    spread = pd.Series(spread)

    recent = float(spread.iloc[-1])
    hist = spread.iloc[-(window + 1):-1]
    mu, sigma = hist.mean(), hist.std()
    if sigma < 1e-9:
        return {'rel_return': round(recent, 4), 'zscore': 0, 'signal': 'NEUTRAL', 'strength': 0}

    z = (recent - mu) / sigma

    # Extreme underperformance → mean reversion buy; extreme outperformance → sell
    if z < -REL_Z_THRESHOLD:
        signal, strength = 'LONG', min(10, abs(z) * 2.5)
    elif z > REL_Z_THRESHOLD:
        signal, strength = 'SHORT', min(10, abs(z) * 2.5)
    else:
        signal, strength = 'NEUTRAL', 0

    return {
        'rel_return': round(recent, 4),
        'zscore': round(z, 3),
        'signal': signal,
        'strength': round(strength, 2),
        'explanation': (
            f"Relative perf Z={z:.2f} vs sector (threshold ±{REL_Z_THRESHOLD}) "
            f"(wiki §Relative, not absolute, price prediction)"
        ),
    }


# ---------------------------------------------------------------------------
# 4. Weekend effect (NSE only)
# wiki §"Weekend effect": floor traders close before weekends → predictable
# Friday afternoon selling + Monday morning buying.
# ---------------------------------------------------------------------------
def weekend_effect(df: pd.DataFrame) -> dict:
    if len(df) < 5:
        return {'applicable': False, 'signal': 'NEUTRAL', 'explanation': 'Insufficient data'}

    last_date = pd.to_datetime(df.index[-1] if hasattr(df.index, 'freq') else df['ts'].iloc[-1]
                               if 'ts' in df.columns else df.iloc[-1].name)
    try:
        last_ts = pd.to_datetime(df.index[-1])
    except Exception:
        last_ts = pd.Timestamp.now()

    is_monday = last_ts.dayofweek == 0

    if not is_monday:
        return {
            'applicable': False,
            'signal': 'NEUTRAL',
            'explanation': 'Weekend effect only applies on Mondays',
        }

    # Friday close > Thursday close → late buying → Monday reversal sell
    fri_close = float(df['close'].iloc[-2]) if len(df) >= 2 else 0
    thu_close = float(df['close'].iloc[-3]) if len(df) >= 3 else 0
    late_buying = fri_close > thu_close

    signal = 'SHORT' if late_buying else 'NEUTRAL'
    return {
        'applicable': True,
        'signal': signal,
        'strength': 5 if signal == 'SHORT' else 0,
        'explanation': (
            f"Monday: Friday close {fri_close:.2f} {'>' if late_buying else '<='} "
            f"Thursday {thu_close:.2f} → {'late buying → sell setup' if late_buying else 'no late buying'} "
            f"(wiki §Weekend effect)"
        ),
    }


# ---------------------------------------------------------------------------
# 5. Volume anomaly
# wiki §"Price & Volume" / §"Market Behaviour Observations":
# High volume + price stall → distribution; high volume + advance → accumulation.
# ---------------------------------------------------------------------------
def volume_anomaly(df: pd.DataFrame, window: int = 20) -> dict:
    if len(df) < window + 2:
        return {'vol_zscore': 0, 'price_change': 0, 'signal': 'NEUTRAL', 'strength': 0}

    hist_vol = df['volume'].iloc[-(window + 1):-1]
    mu, sigma = hist_vol.mean(), hist_vol.std()
    if sigma < 1e-9 or mu < 1:
        return {'vol_zscore': 0, 'price_change': 0, 'signal': 'NEUTRAL', 'strength': 0}

    cur_vol = float(df['volume'].iloc[-1])
    vol_z = (cur_vol - mu) / sigma
    price_chg = float(df['close'].pct_change().iloc[-1])

    if vol_z > VOL_Z_THRESHOLD and abs(price_chg) < 0.005:
        signal, strength = 'SHORT', min(10, vol_z * 2)
        expl = f"Distribution: high vol Z={vol_z:.1f} but price flat"
    elif vol_z > VOL_Z_THRESHOLD and price_chg > 0.005:
        signal, strength = 'LONG', min(10, vol_z * 1.5)
        expl = f"Accumulation: high vol Z={vol_z:.1f} with price advance {price_chg:.2%}"
    elif vol_z < -1.5:
        signal, strength = 'NEUTRAL', 0
        expl = f"Volume dry-up Z={vol_z:.1f}"
    else:
        signal, strength = 'NEUTRAL', 0
        expl = f"Normal volume Z={vol_z:.1f}"

    return {
        'vol_zscore': round(vol_z, 3),
        'price_change': round(price_chg, 4),
        'signal': signal,
        'strength': round(strength, 2),
        'explanation': f"{expl} (wiki §Price & Volume)",
    }


# ---------------------------------------------------------------------------
# 6. HMM regime detection
# wiki §"Hidden-state regime detection (Baum-Welch algorithm)":
# 3-state HMM on log returns + volume change over trailing 60 days.
# States: 0=BEAR/high-vol, 1=SIDEWAYS/low-vol, 2=BULL/low-vol.
# ---------------------------------------------------------------------------
def detect_regime(df: pd.DataFrame, n_states: int = HMM_STATES, lookback: int = HMM_LOOKBACK) -> dict:
    """
    wiki §"Hidden Markov Models (Baum-Welch)": detect latent market regimes.
    Fit 3-state Gaussian HMM; label states by mean log return.
    """
    try:
        from hmmlearn import hmm
    except ImportError:
        return {'regime': 'UNKNOWN', 'confidence': 0, 'explanation': 'hmmlearn not installed'}

    if len(df) < lookback + 5:
        return {'regime': 'UNKNOWN', 'confidence': 0, 'explanation': 'Insufficient data for HMM'}

    subset = df.iloc[-lookback:]
    log_ret = np.log(subset['close'] / subset['close'].shift(1)).dropna()
    vol_chg = subset['volume'].pct_change().dropna()

    # Align lengths
    min_len = min(len(log_ret), len(vol_chg))
    if min_len < n_states * 5:
        return {'regime': 'UNKNOWN', 'confidence': 0, 'explanation': 'Too few data points for HMM'}

    X = np.column_stack([
        log_ret.values[-min_len:],
        vol_chg.values[-min_len:],
    ])
    # Clip extreme outliers
    X = np.clip(X, -0.5, 0.5)

    try:
        model = hmm.GaussianHMM(
            n_components=n_states, covariance_type='diag',
            n_iter=200, random_state=42, tol=1e-4,
        )
        model.fit(X)
        hidden_states = model.predict(X)
        current_state = int(hidden_states[-1])

        # Label states by mean log return (lowest=BEAR, middle=SIDEWAYS, highest=BULL)
        state_means = [X[hidden_states == s, 0].mean() if (hidden_states == s).any() else 0
                       for s in range(n_states)]
        ranking = np.argsort(state_means)  # [bear_idx, sideways_idx, bull_idx]
        labels = ['BEAR', 'SIDEWAYS', 'BULL']
        state_label_map = {int(ranking[i]): labels[i] for i in range(n_states)}

        regime = state_label_map.get(current_state, 'UNKNOWN')

        # Confidence = probability of current state from last step
        log_prob, posteriors = model.score_samples(X)
        confidence = float(posteriors[-1, current_state])

        return {
            'regime': regime,
            'confidence': round(confidence, 3),
            'state_idx': current_state,
            'explanation': (
                f"HMM 3-state regime={regime} (confidence={confidence:.1%}) "
                f"(wiki §Hidden-state regime detection)"
            ),
        }
    except Exception as e:
        return {
            'regime': 'UNKNOWN',
            'confidence': 0,
            'explanation': f"HMM fit failed: {e}",
        }


# ---------------------------------------------------------------------------
# Master Simons scoring function
# ---------------------------------------------------------------------------

def score_simons(
    symbol: str,
    symbol_df: Optional[pd.DataFrame],
    sector_df: Optional[pd.DataFrame] = None,
) -> dict:
    """
    Aggregate all Simons signals. Returns score 0-10, direction, regime, signals.
    wiki §"Ensemble signal aggregation": combine multiple weak signals into one score.
    wiki §"Signal stacking amplifies weak edges"
    """
    if symbol_df is None or len(symbol_df) < 25:
        return {
            'score': 0, 'direction': 'NEUTRAL', 'regime': 'UNKNOWN',
            'signals': {}, 'explanation': 'Insufficient data',
        }

    signals = {
        'mean_reversion': mean_reversion_zscore(symbol_df),
        'serial_correlation': serial_correlation(symbol_df),
        'relative_performance': relative_performance(symbol_df, sector_df),
        'weekend_effect': weekend_effect(symbol_df),
        'volume_anomaly': volume_anomaly(symbol_df),
    }

    regime_result = detect_regime(symbol_df)

    # Ensemble: weight signals
    # wiki §"Ensemble signal aggregation": no single signal dominates
    weights = {
        'mean_reversion': 0.30,
        'serial_correlation': 0.20,
        'relative_performance': 0.25,
        'weekend_effect': 0.10,
        'volume_anomaly': 0.15,
    }

    long_score = 0.0
    short_score = 0.0
    for key, sig in signals.items():
        w = weights.get(key, 0.1)
        if sig.get('signal') == 'LONG':
            long_score += sig.get('strength', 0) * w
        elif sig.get('signal') == 'SHORT':
            short_score += sig.get('strength', 0) * w

    # Regime context adjustment (wiki §"Regime-aware signal weighting")
    regime = regime_result.get('regime', 'UNKNOWN')
    if regime == 'BULL':
        long_score *= 1.2
    elif regime == 'BEAR':
        short_score *= 1.2
    # SIDEWAYS: no adjustment

    if long_score > short_score and long_score > 0:
        direction = 'LONG'
        raw_score = min(10, long_score * 2)
    elif short_score > long_score and short_score > 0:
        direction = 'SHORT'
        raw_score = min(10, short_score * 2)
    else:
        direction = 'NEUTRAL'
        raw_score = 0

    mr = signals['mean_reversion']
    sc = signals['serial_correlation']
    rp = signals['relative_performance']
    explanation = (
        f"Simons: {direction} (score={raw_score:.1f}/10), regime={regime}. "
        f"MR_Z={mr.get('zscore', 0):.2f}, "
        f"SerialCorr={sc.get('autocorr', 0):.3f}, "
        f"RelPerfZ={rp.get('zscore', 0):.2f}"
    )

    return {
        'score': round(raw_score, 2),
        'direction': direction,
        'regime': regime,
        'signals': signals,
        'regime_result': regime_result,
        'explanation': explanation,
    }
