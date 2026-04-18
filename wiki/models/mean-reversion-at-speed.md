# Mean Reversion at Speed
> Exploit the statistical tendency of prices to revert toward a historical norm — but do it at intraday-to-multi-day horizons, at high volume, with a fractional edge that compounds into outsized returns.

## What It Predicts
That a price (or spread between two correlated instruments) that has deviated beyond a statistically defined threshold will, with slightly-better-than-even probability, return toward its norm within a short holding window (hours to days). The model does not predict *when* or *how much* — only that the direction of reversion is slightly more likely than not.

---

## Inputs
1. **Historical price series** (intraday, 5-minute bars preferred) — cleaned, split-adjusted, dividend-adjusted
2. **Baseline norm** — rolling mean or factor-model predicted value for the instrument or spread
3. **Deviation measure** — Z-score of current price vs. rolling mean (or spread vs. historical mean spread)
4. **Asset-class serial correlation** (confirmed Renaissance thresholds):
   - Deutsche mark / major currency futures: **~20%** serial correlation between consecutive periods
   - Other currency futures: **~10%**
   - Gold futures: **~7%**
   - Commodity futures (hogs, grains): **~4%**
   - Individual equities: **~1%**
5. **Transaction cost estimate** — gross edge must exceed estimated round-trip cost
6. **Portfolio leverage & concentration limits** (from the unified optimizer)

---

## Logic

### Why mean reversion exists at short horizons
Short-term price deviations are created by the mechanical behaviour of market participants:
- **Floor traders/locals** close positions before weekends and economic reports, creating predictable temporary imbalances
- **Block trades** by institutions move prices away from fair value; the impact dissipates once the trade is complete
- **Emotional overreaction**: investors over-shoot on news; prices then partially retrace as calmer participants re-enter
- **Systematic hedgers** rebalance portfolios on schedules that create predictable flows

*"What you're really modelling is human behaviour. Humans are most predictable in times of high stress — they act instinctively and panic."* — Nick Penavic, Renaissance researcher **confirmed**

### The serial correlation insight (Berlekamp / Laufer / Straus, ~1989–1992)
Price moves in consecutive periods are **not independent**:

| Asset | Serial correlation | Interpretation |
|-------|--------------------|----------------|
| Deutsche mark futures | **~20%** | Same-direction move repeats >50% of the time |
| Currency futures (other) | ~10% | Modest persistence |
| Gold futures | ~7% | Slight persistence |
| Commodity futures | ~4% | Near-random |
| Equities (individual) | ~1% | Essentially random at daily scale |

> *"The time scale doesn't seem to matter. We get the same statistical anomaly."* — Berlekamp **confirmed**

This means serial correlation signals are **scale-invariant**: whether you look at 5-minute bars or hourly bars, the same fractional edge exists.

### Intraday granularity (Laufer's five-minute bar innovation, ~1992)
Analysing data in 5-minute bars — not daily closes — revealed micro-patterns invisible to daily-bar analysis:
- The **188th five-minute bar** in cocoa futures (a specific time slot) behaved differently on high-volatility days vs. normal days
- **Friday morning trading bands** had an "uncanny ability" to predict the afternoon's trading bands on the same day
- These patterns are too fine-grained for human traders to act on consistently, but trivial for a computer

### The 51% threshold (Berlekamp's key insight)
> *"If you trade a lot, you only need to be right 51 percent of the time. We need a smaller edge on each trade."* — Berlekamp **confirmed**

At sufficient volume, a 51% win rate × large number of trades × leverage = large absolute returns. The law of large numbers is the engine. The edge per trade can be tiny; what matters is:
- **Number of independent trades** (Medallion: 150,000–300,000/day)
- **Consistency of the edge** (not degrading over the measurement window)
- **Transaction cost discipline** (edge must survive round-trip costs)

### The reversion-to-mean equity model (bedrock signal, 1995–2010+)
From the 1995 Brown-Mercer breakthrough, the core equity signal was:
- Identify stocks that have moved significantly relative to their factor-model predicted value (relative to sector, index, peers)
- Enter the position on the assumption of reversion
- Hold for ~2 days on average
- Exit when the reversion is complete or the signal probability approaches neutral

*"We make money from the reactions people have to price moves."* — Renaissance employee **confirmed**

A confirmed percentage of stocks experiencing big, sudden price rises or drops snapped back at least partially. This was most reliable in volatile markets when prices lurched before retracing.

---

## Decision Rules

### Entry
1. Calculate Z-score of current deviation from historical norm (or factor-model value)
2. Enter when |Z| ≥ threshold (Renaissance used multiple thresholds simultaneously across a portfolio of signals — not a single number)
3. Verify: **expected gain net of all transaction costs > 0**
4. Verify: regime context (HMM state) does not suppress this signal in the current environment
5. Direction: **fade the move** — buy the underperformer, short the outperformer (for pair/factor-relative trades)

### Sizing
- Size proportional to edge strength (Z-score magnitude × historical win rate for that level of deviation)
- Further scaled by fractional Kelly formula: `f* = (edge) / (variance of outcome)`
- Never risk more than a small fraction of portfolio on any single reversion signal
- Total portfolio leverage managed at fund level, not signal level

### Hold
- Average holding period: **1–2 days** (equities); can be hours for intraday signals
- Do not set a price target — hold until the model's expected value approaches neutral
- *There is no "wait for the big move."*

### Exit
1. Model signal probability returns to neutral (Z-score reverts to within ±0.5σ of norm)
2. Holding period expires — if reversion hasn't occurred within the expected window, model edge is gone, exit regardless
3. Signal decay: if a class of signals is underperforming their historical expectation, reduce weighting during investigation

### What NOT to do
- Do not override the model because you "know" why the price moved
- Do not hold through a signal expiry hoping for delayed reversion — each day without reversion is evidence the deviation may be permanent
- Do not size up in high-conviction moments — the system's power comes from consistent, mechanical application across thousands of trades, not from big individual bets

---

## Pioneer Lineage
- [Jim Simons](../pioneers/jim-simons.md) — the empirical framework described here is synthesised from Renaissance's process as documented in Zuckerman (2019)
- Elwyn Berlekamp — established the "51% at volume" core principle and the short-term trading focus; achieved 55.9% in 1990 with this approach
- Henry Laufer — five-minute bar analysis; the betting algorithm (continuous intraday reoptimisation); unified commodity/currency model
- Peter Brown & Robert Mercer — 1995 unified portfolio optimizer that made the equity version work; transferred statistical rigor from IBM speech recognition

---

## Examples
- **Weekend effect (confirmed)**: Floor traders close futures longs before weekends. Medallion systematically bought late Friday and sold early Monday, capturing the predictable reversion of this supply imbalance.
- **Pre-report anomaly (confirmed)**: Before most (not all) economic data releases, prices dropped; they rebounded immediately after. Medallion bought ahead of the release for markets where this pattern was statistically robust.
- **Equity reversion (1995 onward)**: Nova/Medallion bought stocks that had dropped more than expected relative to their factor model and shorted those that had risen more than expected. Average holding period ~2 days. Core equity-alpha signal for 10+ years.

---

## Cross-References
- [Jim Simons](../pioneers/jim-simons.md)
- [Statistical Arbitrage](../concepts/statistical-arbitrage.md)
- [Quantitative Signal Pipeline](quantitative-signal-pipeline.md)
- [Regime-Aware Signal Weighting](regime-aware-signal-weighting.md)
- [Position Sizing & Probe System](position-sizing.md)
- [Price & Volume Analysis](../concepts/price-volume.md)
