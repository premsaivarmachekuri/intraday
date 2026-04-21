# Simons Decision Protocol
> A twelve-lens framework for making high-quality decisions under uncertainty, derived from Jim Simons' core methodological principles — applicable to signal validation, position management, strategy evaluation, and any decision where data can be collected and patterns tested.

## What It Predicts / How to Use It
Run any significant decision through these twelve lenses sequentially. The framework forces separation of data from narrative, tests edge robustness, eliminates emotional override, and produces a mathematically defensible conclusion. Exit early at any lens that exposes a fatal flaw — don't proceed to synthesis on a broken premise.

## Inputs
- The decision or situation to be evaluated
- Available historical data or comparable prior instances
- Your current model, system, or strategy
- Candidate options or courses of action
- Recent failure cases to extract rules from

---

## Logic: The Twelve Lenses

### Lens 1 — Data First
What does the raw data show, stripped of all theory, narrative, and prior belief?

> *"We don't start with models. We start with data. We don't have any preconceived notions. We look for things that can be replicated thousands of times."* — Simons **confirmed**

Write down your current theory explicitly — then set it aside. What do the observable numbers, patterns, and historical instances actually show? If the data contradicts your theory, follow the data.

### Lens 2 — The 51% Edge
A small, reliable edge applied at high volume outperforms a large, unreliable edge applied rarely. **Edge × Volume** is the metric, not win rate alone.

Medallion won ~50.75% of trades. At 150,000–300,000 daily trades with 12–20× leverage, that tiny edge produced 66% gross annual returns. *"If you trade a lot, you only need to be right 51 percent of the time."* — Berlekamp **confirmed**

Identify your current win rate. Then ask: am I trying to be right once, or slightly right repeatedly? How do I increase volume while keeping per-attempt cost low?

### Lens 3 — Outsider Pattern Recognition
Domain expertise creates blind spots. Industry experience embeds untested assumptions about how things "should" work.

Simons never hired from Wall Street. He recruited mathematicians, physicists, cryptographers, and speech-recognition engineers — people who treated markets as a pattern-recognition problem, not a narrative to interpret. *"We can teach you about money. We can't teach you about smart."* — Nick Patterson **confirmed**

Identify the "Wall Street" of your domain — the conventional expertise everyone assumes they need. Then ask: what would a practitioner from an unrelated field notice that insiders cannot?

### Lens 4 — Never Override
The worst decisions are made when emotion drives an exception to a validated system. *"This time is different"* is the most expensive sentence in investing.

When Simons called Berlekamp during the Iraq-Kuwait war to suggest buying gold, Berlekamp refused to adjust the model. Simons' override instinct was wrong; the system was right. After repeated losses from discretionary overrides, Renaissance made the rule absolute: the model trades, humans do not interfere. **confirmed**

Identify every point in your system where human discretion can intervene. Can those override points be removed or constrained? Document the last override and its actual outcome.

### Lens 5 — The What, Not the Why
Trade the pattern, not the explanation. If a statistical regularity is confirmed and replicable, the absence of a causal story is irrelevant.

By 1997, more than half of Medallion's trading signals could not be fully explained by the team — yet they were traded anyway because they met statistical significance thresholds and survived out-of-sample testing. *"Any time you hear financial experts talking about how the market went up because of such and such, remember it's all nonsense."* — Peter Brown **confirmed**

List every narrative you are using to justify a position or decision. Strip them out. What is the observable, measurable pattern beneath them?

### Lens 6 — Layer the Signals
No single signal is sufficient. The power is in combining hundreds of partially-correlated weak signals into one robust prediction.

> *"Many of the anomalies we initially exploited are intact, though they have weakened some. What you need to do is pile them up. You need to build a system that is layered and layered."* — Simons **confirmed**

Identify your strongest single advantage. Then identify five other small advantages you are not yet leveraging. Map how they compound. Ask: what new layer can be added this period that is partially uncorrelated with existing signals?

### Lens 7 — Failure as Data
Every loss is an experiment that produced an unexpected result. The correct response is not regret — it is diagnosis and rule-building.

Simons wrote down every mistake, tested why it happened, and built an explicit rule to prevent recurrence. Losses were treated as informational assets, not emotional events. *inferred*

Take the most recent failure. Document it as a scientist would: (1) what was the hypothesis? (2) what actually happened? (3) where did the model break — bad data, bad assumptions, bad execution, or bad timing? (4) what specific rule prevents recurrence? If you ran this experiment 100 more times with the new rule in place, what would success rate be?

### Lens 8 — Reduce Position, Don't Panic
During volatility or regime uncertainty, do not change strategy — reduce exposure. Same signals, smaller bets, until clarity returns.

Medallion's automatic position-reduction protocol during the 2008 financial crisis kept losses contained while other funds blew up. The fund ended 2008 up 82% — not because it changed approach, but because it trusted its signals at reduced size rather than shutting down or panic-selling. **confirmed**

Identify your current exposure across capital, time, and attention. What is the minimum viable version of your current strategy? Shrink the bet; keep the method.

### Lens 9 — The Monolithic Model
Treat all signals, constraints, and objectives as inputs to a **single unified optimisation** — not separate models stitched together. Improvement in one area automatically propagates to all others.

The Brown-Mercer 1995 breakthrough was replacing Renaissance's fragmented signal-by-strategy architecture with one portfolio optimizer that considered every signal, every cost, every constraint simultaneously. This was what made stock trading work. *"A living thing; it's always modifying."* — Simons **confirmed**

List all separate strategies or projects you are running. Which are actually interconnected but being treated independently? What would a unified model — where everything talks to everything — look like? What single activity, if improved, simultaneously improves the most others?

### Lens 10 — Competitive Moat
The biggest risk to any edge is other people copying it. The moat is complexity — a system so layered that even insiders cannot recreate it independently.

Renaissance employees could read all internal code, but nothing left the building. Non-competes were among the most restrictive in the industry. Medallion spread its strongest signal executions unpredictably throughout the trading day to avoid telegraphing its model to rivals. *"Once we've been trading a signal for a year, it looks like something different to people who don't know our trades."* — Renaissance executive **confirmed**

How easily can your edge be copied? Where are you inadvertently exposing the *how* instead of just the *what*? What complexity layer makes your edge genuinely hard to replicate?

### Lens 11 — Beauty as a Signal
Elegance signals robustness. Complexity and special-casing signal fragility.

> *"Be guided by beauty. Just as a great theorem can be very beautiful, a company that's really working very well, very efficiently, can be beautiful."* — Simons **confirmed**

A model that requires excessive patching, workarounds, or special-case rules is probably overfit to historical data and will fail out-of-sample. Parsimonious models with fewer parameters and cleaner logic generalise better. Among competing options, the elegant one is more likely to be right.

Which option, signal, or solution feels the most parsimonious? Which requires the most special-casing? The beautiful answer is the more trustworthy one.

### Lens 12 — The Synthesis
Aggregate all eleven lenses. Ignore the emotionally compelling narrative. Follow what the integrated data-and-structure analysis recommends. This is the "mathematical move" — not the emotional one.

---

## Decision Rules

| Lens | Pass Criterion |
|------|----------------|
| Data First | Decision based on observed pattern, not prior theory |
| 51% Edge | Edge × volume is positive in expectation; volume path is defined |
| Outsider | At least one untested domain assumption has been challenged |
| Never Override | No emotional exception to validated system is being made |
| What Not Why | Narrative stripped; pattern is measurable and replicable |
| Layer Signals | ≥3 independent signals or advantages point the same direction |
| Failure as Data | A post-mortem rule has been written for any comparable recent failure |
| Reduce Position | Bet size is proportional to regime clarity, not emotional conviction |
| Monolithic | Decision is consistent with the unified portfolio/strategy objective |
| Competitive Moat | Implementation does not expose proprietary method |
| Beauty | Preferred option is the most parsimonious, not the most elaborate |
| Synthesis | All passing lenses reconcile; conflicts resolved by majority |

---

## Pioneer Lineage
- [Jim Simons](../pioneers/jim-simons.md) — all twelve lenses derive from confirmed principles of Renaissance Technologies' methodology

---

## Examples

**Signal acceptance (Lenses 1 + 5)**: Medallion traded volume/price-lag signals that no team member could explain. The data showed replication across thousands of instances; the absence of a causal "why" was explicitly irrelevant. Pass.

**1990 gold override (Lens 4)**: Simons called Berlekamp repeatedly to suggest gold would rally during the Gulf War. Berlekamp refused to adjust the model. Simons' discretionary override was wrong; the system was right. The never-override rule was reinforced permanently.

**Reduce-position protocol — 2008 (Lens 8)**: During the financial crisis, Medallion's automatic position-reduction rules kept exposure proportional to regime clarity. Same signals, smaller bets. Result: +82% for the year while the broader hedge fund industry collapsed.

**Brown-Mercer unified optimizer — 1995 (Lens 9)**: Frey's stock-trading signals were profitable in simulation but lost money live. Diagnosis: portfolio assembly was fragmented. Fix: one monolithic optimiser. Result: stock-trading became Medallion's dominant profit engine.

**Berlekamp's 51% insight (Lens 2)**: Berlekamp calculated that Medallion needed only a 50.75% win rate if it increased trade volume sufficiently. He rebuilt the entire model around short-term, high-frequency signals — sacrificing the size of each win for the reliability of many small wins. Return in 1990: 55.9%.

---

## Cross-References
- [Jim Simons](../pioneers/jim-simons.md)
- [Quantitative Signal Pipeline](quantitative-signal-pipeline.md)
- [Regime-Aware Signal Weighting](regime-aware-signal-weighting.md)
- [Mean Reversion at Speed](mean-reversion-at-speed.md)
- [Position Sizing & Probe System](position-sizing.md)
- [Pattern Recognition](../concepts/pattern-recognition.md)
- [Statistical Arbitrage](../concepts/statistical-arbitrage.md)
