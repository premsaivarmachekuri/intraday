# Multi-Timeframe Confluence

> Align the market, the sector, the industry group, and the individual stock in the same direction before pulling the trigger — the more levels that agree, the higher the probability.

---

## What It Predicts

Whether a trade setup has the maximum probability of working. A stock at a Pivotal Point that is also aligned with its group, its sector, and the overall market is a fundamentally different proposition from a stock at a Pivotal Point that is fighting against all three. This model filters setups to only the highest-conviction configurations.

---

## Inputs

1. **Overall market direction** — the specific exchange the stock trades on (Nasdaq, S&P 500, Dow, Amex). Is it in an upward trend, downward trend, or sideways?
2. **Sector direction** — is the broad sector (e.g., Technology, Financials, Energy) trending in the same direction as the market?
3. **Industry group direction** — is the specific group (e.g., Internet, Broker/Dealers, Oil Drilling) trending in the same direction?
4. **Sister stock / tandem stock** — is the other leading stock in the group confirming the same pattern?
5. **Individual stock setup** — is the stock at a Reversal or Continuation Pivotal Point?
6. **Volume confirmation** — does volume confirm the Pivotal Point?

---

## Logic

Livermore discovered that stocks do not move alone — they move in industry groups, which move in sectors, which move with the overall market. A legitimate move requires alignment across levels. Any level out of sync weakens the trade significantly.

**Hierarchy of confirmation:**

```
Level 1: Overall Market (Line of Least Resistance)
    ↓ must align
Level 2: Sector Trend
    ↓ must align
Level 3: Industry Group Trend
    ↓ must align
Level 4: Sister Stock (Tandem Trade) same pattern
    ↓ must align
Level 5: Individual Stock at Pivotal Point
    ↓ must confirm
Level 6: Volume surge at Pivotal Point
```

All six levels aligned = highest probability trade. Each level out of alignment reduces probability and should reduce position size or prevent the trade entirely.

---

## Decision Rules

| Levels aligned | Action |
|----------------|--------|
| All 6 | Full probe sequence — high conviction |
| 5 (missing volume) | Smaller first probe — wait for volume confirmation |
| 4 (stock or sister not confirming) | No trade — wait for confirmation |
| 3 or fewer | Avoid — low probability, high risk |
| Market against direction | Do not trade that direction at all |

**Top-Down Checklist (run before every trade):**

- [ ] What exchange does this stock trade on?
- [ ] What is the current trend of that exchange?
- [ ] What sector does this stock belong to? Is the sector trending in the same direction?
- [ ] What industry group is this stock in? Is the group trending in the same direction?
- [ ] Who is the sister/tandem stock (the other group leader)? Does it show the same pattern?
- [ ] Is the individual stock at a Pivotal Point (Reversal or Continuation)?
- [ ] Is there volume confirmation (≥50% above average daily volume)?
- [ ] Is the entry within 5–10% of the Pivotal Point?

---

## Pioneer Lineage

**Jesse Livermore** — originated Top-Down Trading and the Tandem/Sister Stock method. Refused to act on any stock signal without checking the group. His greatest wins (1907 crash short, 1929 crash short) came from watching leading groups roll over first, then aligning his shorts with the cascade. See [Jesse Livermore](../pioneers/jesse-livermore.md).

---

## Examples (from Livermore)

**1929 Short:** Watched copper stocks top out, then motor stocks top out. Initially went short too early (lost money). Then tracked the utility group — when it also peaked, he had three leading groups all rolling over. Went short in earnest with a line of 1 million shares. Made $100 million.

**2003 Bottom (documented in book):** The Nasdaq, Internet Group, and Broker/Dealer Group (Morgan Stanley + Merrill Lynch) all bottomed in Feb/Mar 2003 simultaneously. All showed Reversal Pivotal Points at the same time. This multi-level confluence confirmed the new uptrend with high conviction.

---

## Jim Simons — Algorithmic Analogue: Regime-Aware Signal Weighting

Simons implemented the same core idea — "is the market context right for this signal?" — but via Hidden Markov Models rather than manual chart reading.

Instead of checking whether the sector trend aligns with the market trend, Medallion asks: *what hidden regime does the HMM infer from the current price sequence, and does this signal historically work in that regime?*

Key equivalences:

| Livermore (discretionary) | Simons (systematic) |
|---------------------------|---------------------|
| Check market trend direction | HMM infers current regime (trending / mean-reverting / chaotic) |
| Check sector & group alignment | Cross-asset correlations and factor exposures |
| Sister stock confirmation | Pair / spread relationship Z-score |
| Volume confirming pivot | Statistical threshold on signal Z-score |
| "Market not right → do not trade" | Signal weight suppressed in unfavourable regime |

Both systems share the fundamental principle: **context before position.** Neither fires a signal in isolation — context must confirm before capital is deployed.

See [Jim Simons](../pioneers/jim-simons.md) and [Regime-Aware Signal Weighting](regime-aware-signal-weighting.md).

---

## Cross-References

- [Jesse Livermore](../pioneers/jesse-livermore.md)
- [Jim Simons](../pioneers/jim-simons.md)
- [Trend Following](../concepts/trend-following.md)
- [Pivotal Points](../concepts/pivotal-points.md)
- [Pattern Recognition](../concepts/pattern-recognition.md)
- [Entry–Exit Framework](entry-exit-framework.md)
- [Regime-Aware Signal Weighting](regime-aware-signal-weighting.md)
