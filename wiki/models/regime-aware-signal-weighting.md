# Regime-Aware Signal Weighting
> Adjust the weight of every trading signal based on the inferred hidden state (regime) of the market — so the same signal is bet heavily in favourable regimes and suppressed in unfavourable ones.

## What It Predicts
Not market direction — but the **current state of the market system**. Markets switch between distinct, unobservable regimes (trending vs. mean-reverting, high-volatility vs. low-volatility, correlated vs. uncorrelated). Different signals have different reliability in different regimes. Identifying the current regime lets you concentrate edge where it exists and withdraw where it doesn't.

---

## Inputs
1. **Price and volume time series** — the observable output of the hidden system
2. **Hidden Markov Model (HMM)** — a statistical model that infers unobservable "states" from the sequence of observable outputs
3. **Signal library** — the full set of tradeable signals, each with its performance history conditional on each regime
4. **Current estimated regime probabilities** — output of the Baum-Welch algorithm applied to current data
5. **Signal weight adjustments** — lookup table: for each (signal, regime) pair, the scaling factor to apply

---

## Logic

### The core insight: markets have hidden states
Markets appear random on the surface. But their underlying dynamics shift between distinguishable configurations — regimes — that are not directly observable but can be *inferred* from the sequence of price movements. This is exactly analogous to:

- A **speech recognition system** inferring the intended word from a noisy sequence of sounds (the original application of HMMs by Peter Brown and Robert Mercer at IBM)
- A **poker player** inferring an opponent's hand strength from their sequence of betting decisions

The Baum-Welch algorithm — developed by Lenny Baum at the Institute for Defense Analyses in the 1960s, originally as a code-breaking tool — provides a principled, computationally tractable method for fitting HMMs to sequential data.

> *Hidden Markov Models allowed the system to infer unobservable market "states" — analogous to how speech-recognition software infers the intended word from noisy phonemes. Regime-aware positioning adjusts signal weights by detected state.* — Zuckerman (2019) **confirmed**

### How the HMM works in practice
1. Define K hidden states (e.g., K=3: "trending," "mean-reverting," "chaotic")
2. For each state, define a probability distribution over observed price moves
3. Use the Baum-Welch (Expectation-Maximisation) algorithm to fit the model parameters to historical data
4. At each timestep, compute the **posterior probability** of being in each state given all price history to date
5. Use these probabilities to weight signals accordingly

The model does not require you to *label* regimes in advance — the algorithm infers both the structure of the hidden states and the current most-likely state simultaneously.

### Why this beats static signal weights
A signal that works well in trending markets (momentum) may be actively harmful in mean-reverting markets. A signal calibrated on mixed historical data will underperform in both. Regime conditioning:
- **Concentrates bets** when the current regime matches the signal's historical sweet spot
- **Suppresses bets** when the regime makes the signal unreliable
- **Adapts automatically** as markets shift between regimes — no manual intervention required

This is the algorithmic equivalent of what Livermore called "reading the tape" to determine whether the market is in a trending or choppy condition before deciding whether to trade.

---

## Decision Rules

### Building the model
1. Fit an HMM with K states to a long historical price series using Baum-Welch
2. For each historical period, record the inferred regime and the subsequent performance of each signal
3. Build a regime-conditional performance table: `signal_weight[signal][regime] = historical_sharpe_in_that_regime / average_sharpe`
4. Normalise weights so the total portfolio exposure stays constant across regimes

### Live operation
1. At each timestep, run the forward algorithm on current price data to compute `P(regime=k | all data so far)`
2. For each signal in the library: `adjusted_weight = base_weight × signal_weight[signal][argmax_k P(regime=k)]`
   - Or use a **soft weighting**: `adjusted_weight = base_weight × Σ_k P(regime=k) × signal_weight[signal][k]`
3. Pass adjusted weights to the unified portfolio optimizer
4. Recalibrate the HMM periodically (e.g., quarterly) on an expanding data window

### Regime identification heuristics (to sanity-check HMM output)
| Regime indicator | Likely regime |
|-----------------|---------------|
| Cross-asset correlations spiking toward 1 | Crisis / risk-off |
| Intraday ranges compressing, low volume | Low-volatility / directionless |
| Serial correlations elevated (>10%) | Trending |
| Serial correlations near zero or negative | Mean-reverting |
| VIX-equivalent elevated + serial correlation high | Momentum-favourable |
| VIX-equivalent elevated + serial correlation low | Mean-reversion-favourable (panic then snap-back) |

---

## Pioneer Lineage
- [Jim Simons](../pioneers/jim-simons.md) — regime detection via HMM is a documented, confirmed element of the Medallion fund's architecture
- **Lenny Baum** — developed the Baum-Welch algorithm at the IDA; became a co-architect of Simons's early trading models; the algorithm is named for him
- **Peter Brown & Robert Mercer** — brought HMM expertise from IBM's speech-recognition group; applied it to market regime inference; confirmed their use of probabilistic sequential models in the 1995 equity breakthrough

---

## Examples
- **HMM in speech recognition (direct lineage)**: Brown and Mercer's IBM group modelled sounds as the output of a hidden Markov chain where each step is random yet dependent on the previous step. The system learned to transcribe language without "understanding" it — by learning the statistical structure. The identical mathematical apparatus was applied to price sequences at Renaissance. **confirmed**
- **Regime suppression of trend signals**: In periods when the HMM detects a mean-reverting regime (serial correlation near zero), momentum/trend signals are down-weighted or suppressed. In periods of elevated serial correlation (trending regime), they are amplified.
- **Crash-resilience (confirmed)**: Medallion gained 98.5% in 2000 and avoided catastrophic losses in 2007–2008 that crippled other quant funds. The regime-aware architecture allowed the system to detect shifts in market dynamics and adjust signal weights before the damage was done.

---

## Cross-References
- [Jim Simons](../pioneers/jim-simons.md)
- [Quantitative Signal Pipeline](quantitative-signal-pipeline.md)
- [Mean Reversion at Speed](mean-reversion-at-speed.md)
- [Multi-Timeframe Confluence](multi-timeframe-confluence.md) — Livermore's manual multi-timeframe context is the discretionary analogue of HMM regime detection
- [Pattern Recognition](../concepts/pattern-recognition.md)
