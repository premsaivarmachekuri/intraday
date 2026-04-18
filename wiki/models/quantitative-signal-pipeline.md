# Quantitative Signal Pipeline
> A systematic, five-stage process for converting raw price data into deployable trading signals: collect → discover → validate → combine → monitor.

## What It Predicts
Not individual price moves — but whether a candidate pattern is a genuine, repeatable market inefficiency worth betting on at scale, and how much weight to give it once deployed.

## Inputs
- Clean historical price and volume data (tick, 5-minute bars, daily) across as many markets and instruments as possible
- Transaction cost estimates (bid-ask spread, slippage, market impact) for each target market
- Out-of-sample data reserve (never touched during discovery)
- Live trading results for deployed signals

---

## Logic: The Five Stages

### Stage 1 — Data Collection & Cleaning
The foundation of everything. **Dirty data produces bogus signals.** Renaissance spent years building and cleaning Sandor Straus's historical database before the models became reliable.

- Collect tick-level and intraday data where available; fill gaps with the best available daily data
- Normalise for splits, dividends, delistings, and exchange hours
- Flag and investigate anomalies — a price that looks like a pattern may be a data error
- The quality of the signal library is directly proportional to the quality of the data

> *"We realised we had been saving intraday data. It wasn't super clean, and it wasn't all the tick data, but it was more reliable and plentiful than what others were using."* — Sandor Straus **confirmed**

### Stage 2 — Signal Discovery
Search the data for **statistically significant, recurring anomalies** — without starting from an economic theory.

- Do not require a hypothesis before looking. Let the data surface the pattern.
- Include nonintuitive signals: by 1997, >50% of Medallion's signals could not be fully explained yet were statistically robust. They were traded anyway. *"Volume divided by price change three days earlier, yes, we'd include that."* — Renaissance executive **confirmed**
- Screen out the absurd: signals with no plausible mechanism and weak statistics are discarded (e.g., "stocks beginning with letter A outperform")
- Candidate signals include:
  - Serial correlation by asset class (see [Mean Reversion at Speed](mean-reversion-at-speed.md))
  - Calendar / time-of-day / day-of-week effects (weekend effect, pre-report anomaly)
  - Cross-asset spread deviations (stat-arb)
  - Regime-conditional signals (HMM state-dependent)
  - Behavioural artifacts (floor-trader positioning, hedger flows)

### Stage 3 — Validation (Out-of-Sample Testing)
The single most important discipline — distinguishes real signals from data overfitting.

- **Reserve a portion of historical data that is never used in discovery.** Test the signal on this unseen data only after the model is fully specified.
- Walk-forward testing: train on period A, test on period B, re-train on A+B, test on period C — repeat
- Beware data overfitting (also called curve-fitting): a signal with 10 free parameters and 100 data points will always appear to fit — but it is noise. The gold standard is: *fewer parameters, more data, out-of-sample survival*
- Transaction cost filter: a signal must be profitable **net of all costs** (bid-ask + estimated slippage + market impact) to pass. Many signals that look good gross are worthless net. *"I'm not sure we're the best at all aspects of trading, but we're the best at estimating the cost of a trade."* — Simons **confirmed**

> **The overfitting trap**: quant investor David Leinweber demonstrated that US stock returns can be predicted with 99% accuracy by combining Bangladeshi butter production, US cheese production, and global sheep population. Statistically significant. Economically meaningless. **Confirmed example from book.**

### Stage 4 — Ensemble Combination (Unified Portfolio Optimizer)
No single signal dominates. The system combines hundreds of weak, partially correlated signals into a single portfolio recommendation.

- **Brown-Mercer 1995 breakthrough**: treat all signals, leverage constraints, risk limits, short-availability constraints, and transaction costs as inputs to a **single monolithic optimisation problem** — not separate models stitched together
- The unified approach allows: (a) instant testing of new signals against the live portfolio's risk/cost structure; (b) automatic interaction effects — a new signal may be redundant with existing ones, or may hedge them beneficially; (c) adaptive rebalancing throughout the day
- The resulting portfolio is re-optimised continuously, adapting on its own — an early form of machine learning. Simons called it *"a living thing; it's always modifying."* **confirmed**
- Regime context (HMM state) modifies signal weights: signals that historically underperform in the current detected regime are down-weighted automatically. See [Regime-Aware Signal Weighting](regime-aware-signal-weighting.md)

### Stage 5 — Signal Monitoring & Decay Management
Deployed signals are not permanent. Markets adapt; competitors copy; edges decay.

- Continuously backtest deployed signals against live results
- Define a "decay threshold": if a signal's live Sharpe ratio drops materially below its backtest expectation, reduce allocation and investigate
- Common causes of decay: (a) competition — other funds discover the same anomaly; (b) market structure change — regulatory change, new instrument, shift in participant composition; (c) data regime change — the historical relationship no longer holds
- Retire signals gracefully — don't wait for them to become negative contributors
- Maintain a pipeline of new signals in discovery to replace decaying ones

> *"The system is always leaking. We keep having to keep it ahead of the game."* — Simons **confirmed**

---

## Decision Rules

| Stage | Pass criterion |
|-------|----------------|
| Data | No unexplained anomalies; all prices reconcile to exchange records |
| Discovery | Statistically significant in-sample (p < 0.01 or similar); not obviously nonsensical |
| Validation | Survives out-of-sample test; remains profitable net of transaction costs |
| Combination | Adds incremental Sharpe to the portfolio; does not breach leverage or concentration limits |
| Monitoring | Live Sharpe within 2σ of backtest expectation over rolling 6-month window |

---

## Pioneer Lineage
- [Jim Simons](../pioneers/jim-simons.md) — the entire pipeline described here is a synthesis of Renaissance Technologies' process as documented in *The Man Who Solved the Market*. Individual stage contributions: Straus (data), Baum/Berlekamp/Laufer (discovery), Berlekamp/Patterson (validation), Brown/Mercer (combination), Laufer/all (monitoring)

---

## Examples
- **Weekend effect discovery**: Berlekamp and Laufer observed that floor traders habitually closed futures positions before weekends. The pattern was statistically significant, survived out-of-sample testing, was cheap to execute (futures have low transaction costs), and added to the portfolio without crowding existing signals. Deployed.
- **Canadian dollar rejection**: Model showed edge but every real trade lost money. Investigation revealed three brokers on the Chicago floor were colluding to front-run Medallion's orders. Data anomaly — signal retired, market avoided.
- **Nova stock-trading system (1994)**: Frey's signals were profitable in simulation but lost money live. Brown and Mercer diagnosed the problem as a failure of the portfolio assembly stage — not the signals themselves. Fix: unified portfolio optimizer. Deployed successfully 1995.

---

## Cross-References
- [Jim Simons](../pioneers/jim-simons.md)
- [Statistical Arbitrage](../concepts/statistical-arbitrage.md)
- [Mean Reversion at Speed](mean-reversion-at-speed.md)
- [Regime-Aware Signal Weighting](regime-aware-signal-weighting.md)
- [Position Sizing & Probe System](position-sizing.md)
- [Pattern Recognition](../concepts/pattern-recognition.md)
- [Price & Volume Analysis](../concepts/price-volume.md)
