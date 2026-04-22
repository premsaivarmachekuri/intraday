"""
Format scan results into Telegram HTML messages.
Telegram message limit: 4096 chars — splits automatically.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

IST = timezone(timedelta(hours=5, minutes=30))
MAX_MSG_LEN = 4000  # leave buffer below 4096
MAX_SETUPS = 15


def _esc(text: str) -> str:
    """Escape HTML special chars for Telegram parse_mode='HTML'."""
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


def _direction_emoji(d: str) -> str:
    return '📈' if d == 'LONG' else '📉'


def format_market_overview(results: list, nifty_df=None, banknifty_df=None) -> str:
    """Message 1: Market overview."""
    now_ist = datetime.now(IST).strftime('%Y-%m-%d %H:%M IST')

    longs = [r for r in results if r['direction'] == 'LONG']
    shorts = [r for r in results if r['direction'] == 'SHORT']

    # Top sector by count
    from collections import Counter
    sector_counts = Counter(r['sector'] for r in results)
    top_sector = sector_counts.most_common(1)[0][0] if sector_counts else 'N/A'

    # Overall regime from top result
    overall_regime = results[0]['regime'] if results else 'UNKNOWN'

    # NIFTY/BANKNIFTY last price
    def _last(df):
        if df is not None and len(df) > 0:
            c = float(df['close'].iloc[-1])
            prev = float(df['close'].iloc[-2]) if len(df) > 1 else c
            chg = (c - prev) / prev * 100
            return c, chg
        return None, None

    n50_p, n50_c = _last(nifty_df)
    bn_p, bn_c = _last(banknifty_df)
    n50_str = f"{n50_p:,.2f} ({n50_c:+.2f}%)" if n50_p else "N/A"
    bn_str  = f"{bn_p:,.2f} ({bn_c:+.2f}%)" if bn_p else "N/A"

    msg = (
        f"<b>🗓 Pre-Market Scan — {now_ist}</b>\n\n"
        f"<b>📊 MARKET REGIME</b>\n"
        f"• NIFTY 50: {_esc(n50_str)} — {overall_regime}\n"
        f"• BANK NIFTY: {_esc(bn_str)}\n\n"
        f"<b>📈 TODAY'S OPPORTUNITY SUMMARY</b>\n"
        f"• {len(longs)} LONG setups | {len(shorts)} SHORT setups\n"
        f"• Top sector: {_esc(top_sector)}\n"
        f"• Simons regime: {_esc(overall_regime)}\n"
    )
    return msg


def format_setup(rank: int, r: dict) -> str:
    """Format one trade setup."""
    entry = r.get('entry_zone', (0, 0))
    entry_mid = (entry[0] + entry[1]) / 2 if entry[1] > 0 else 0
    stop = r.get('stop_loss', 0)
    risk_pct = r.get('risk_pct', 0)

    # Livermore signals list
    lv_signals = r.get('livermore_signals', [])
    lv_sig_str = '\n'.join(
        f"  • {_esc(s.get('name','?'))}: {_esc(s.get('signal',''))} (str={s.get('strength',0):.1f})"
        for s in lv_signals
    ) or '  • None triggered'

    # Simons signals
    sm = r.get('simons_signals', {})
    mr_z = sm.get('mean_reversion', {}).get('zscore', 0)
    ac   = sm.get('serial_correlation', {}).get('autocorr', 0)
    rp_z = sm.get('relative_performance', {}).get('zscore', 0)

    msg = (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>#{rank} {_esc(r['symbol'])} ({_esc(r['exchange'])}) — "
        f"{_direction_emoji(r['direction'])} {_esc(r['direction'])}</b>\n"
        f"📌 {_esc(r['name'])}\n"
        f"Score: <b>{r['combined_score']:.1f}/10</b>  "
        f"[Livermore: {r['livermore_score']:.1f} | Simons: {r['simons_score']:.1f}]\n"
        f"Regime: {_esc(r['regime'])}\n\n"
        f"🎯 <b>ENTRY ZONE:</b> ₹{entry[0]:,.2f} – ₹{entry[1]:,.2f}\n"
        f"🛑 <b>STOP LOSS:</b> ₹{stop:,.2f}\n"
        f"📐 Risk: {risk_pct:.1f}% from mid-entry\n\n"
        f"📖 <b>LIVERMORE SIGNALS:</b>\n"
        f"{lv_sig_str}\n"
        f"<i>{_esc(r['livermore_explanation'][:200])}</i>\n\n"
        f"🔬 <b>SIMONS SIGNALS:</b>\n"
        f"• Regime: {_esc(r['regime'])}\n"
        f"• Mean Reversion Z: {mr_z:.2f}\n"
        f"• Serial Corr: {ac:.3f}\n"
        f"• Relative Perf Z: {rp_z:.2f}\n"
        f"<i>{_esc(r['simons_explanation'][:200])}</i>\n\n"
        f"💡 <b>COMBINED READ:</b>\n"
        f"<i>{_esc(r.get('combined_explanation','')[:250])}</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    return msg


def format_report(results: list, nifty_df=None, banknifty_df=None) -> list:
    """
    Format the full scan output as a list of Telegram messages.
    Splits at MAX_MSG_LEN to respect Telegram's 4096-char limit.
    """
    messages = []

    # Message 1: overview
    messages.append(format_market_overview(results, nifty_df, banknifty_df))

    # Messages 2-N: individual setups (top MAX_SETUPS)
    top = results[:MAX_SETUPS]
    current = ''
    for i, r in enumerate(top, start=1):
        block = format_setup(i, r) + '\n\n'
        if len(current) + len(block) > MAX_MSG_LEN:
            if current:
                messages.append(current.strip())
            current = block
        else:
            current += block

    if current.strip():
        messages.append(current.strip())

    if not top:
        messages.append('ℹ️ No high-confidence setups found today.')

    return messages
