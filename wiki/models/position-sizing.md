# Position Sizing & Probe System

> Never commit full capital to a position before the market has confirmed your judgment — scale in only as price proves you right.

---

## What It Does

Eliminates the risk of carrying a large losing position by making the market prove itself at each step before more capital is deployed. The probe system is simultaneously a money management tool and a market feedback mechanism.

---

## Inputs

- Target position size (total shares or capital)
- Entry price (at or near Pivotal Point)
- Current price at each probe stage
- Whether each probe shows a profit

---

## Logic

The fundamental insight: you cannot know in advance whether your judgment is correct. You can only know *after* the market shows you. The probe system structures your entries so that maximum capital is only deployed when maximum evidence exists.

By requiring each subsequent purchase to be at a **higher price**, the system enforces a law: you are only adding to a position that is working. The market's upward movement is the evidence you need. If the stock stops going up — stop adding.

The psychological challenge: paying more for each lot feels wrong (human nature wants to buy cheap). Overcoming this is the discipline of the system. The "higher price" paid for each lot is the cost of the confirmation insurance.

---

## Probe Formula (Livermore Standard)

| Probe | % of Target Position | Condition to Execute |
|-------|---------------------|----------------------|
| 1st | 20% | At Reversal Pivotal Point |
| 2nd | 20% | Stock has advanced from probe 1 — probe 1 shows profit |
| 3rd | 20% | Stock continues advancing — probes 1+2 show profit |
| Final | 40% | Full conviction — all prior probes profitable; or Continuation Pivotal Point breakout |

**Total = 100% of target position**

Alternative ratios (Livermore acknowledged any ratio can work — the principle matters more than the specific ratio):
- 30% / 30% / 40%
- 25% / 25% / 25% / 25%
- 33% / 33% / 34%

---

## Decision Rules

**Add to position (continue probing):**
- Each prior probe shows a profit
- Stock is making new highs (or new lows on a short)
- Volume confirming the move

**Stop probing and hold:**
- Position is fully established
- No valid Continuation Pivotal Point to add at
- Market conditions unclear

**Exit entire position immediately:**
- Any single probe moves 10% against entry price
- Stock fails to advance after crossing a Pivotal Point
- Time stop: stock does not perform within ~5 trading days of entry
- One-Day Reversal pattern appears
- Tandem/sister stock breaks down
- Stock becomes a "Listless Drifter" — flat, no energy, no progress

**Never:**
- Average down (buy more of a losing position at a lower price)
- Meet a margin call
- Add to a position showing a loss

---

## Cash Reserve Rule

Maintain a permanent cash reserve — never be fully invested. Cash is inventory. Opportunities occur 4–5 times per year at maximum. The rest of the time, cash earns nothing but preserves optionality for the next high-conviction setup.

**Windfall Rule:** After any trade that doubles original capital, bank 50% of profits outside the market account. Physically separate it. This prevents the "round-trip" — giving back large gains in subsequent trades.

---

## Pioneer Lineage

**Jesse Livermore** — originated the probe concept from bucket shop discipline. The 10% forced-exit rule of bucket shops taught him that small, contained losses were a feature, not a bug. He extended this into a full scaling system. See [Jesse Livermore](../pioneers/jesse-livermore.md).

**Jim Simons / Renaissance Technologies** — replaced discretionary position sizing entirely with the fractional Kelly formula and a unified portfolio optimizer. Key principles:

- **Fractional Kelly sizing**: `f* = (edge) / (variance of outcome)`. Never bet the full Kelly; use a fraction (typically 25–50% of Kelly) to reduce variance while preserving most of the expected-value benefit.
- **Edge-based scaling**: position size automatically scales with signal strength (Z-score) and historical win rate — larger deviations receive larger bets, but only proportionally, not exponentially.
- **Diversification as the primary risk control**: 4,000+ simultaneous positions means idiosyncratic risk is nearly fully diversified away. No single position can materially harm the fund.
- **Leverage as a dial**: overall portfolio leverage is increased in high-confidence, high-liquidity conditions and dialled down in stressed or illiquid markets — but this is a portfolio-level decision, not a per-trade decision.
- **Capacity discipline**: Laufer's market-impact models measured with "surprising precision" how much of Medallion's own edge was consumed by its own trading. The fund was capped at $280M in 1993 when these models showed returns would erode. Growth only came by expanding into deeper (equity) markets.

See [Jim Simons](../pioneers/jim-simons.md).

---

## Cross-References

- [Jesse Livermore](../pioneers/jesse-livermore.md)
- [Jim Simons](../pioneers/jim-simons.md)
- [Pivotal Points](../concepts/pivotal-points.md)
- [Entry–Exit Framework](entry-exit-framework.md)
- [Multi-Timeframe Confluence](multi-timeframe-confluence.md)
- [Quantitative Signal Pipeline](quantitative-signal-pipeline.md)
- [Mean Reversion at Speed](mean-reversion-at-speed.md)
