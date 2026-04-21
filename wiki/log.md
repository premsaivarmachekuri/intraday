# Wiki Log

Append-only. Format: `## [YYYY-MM-DD] type | title`

---

## [2026-04-21] ingest | Jim Simons — Twelve Decision Frameworks (public interviews synthesis)
- Source: `raw/jim-simons-models.md` — twelve named frameworks from Simons' public statements and methodological principles
- **Four new elements added** to `wiki/pioneers/jim-simons.md`:
  - Core Philosophy: added "pile them up / layer and layer" signal-stacking quote (Simons, confirmed)
  - Core Philosophy: added "be guided by beauty" elegance-as-validity principle (Simons, confirmed)
  - Pattern-Recognition Rules: added Rule #11 — Elegance as a validity filter (Beauty as a Signal)
  - Money Management: added Volatility Protocol — reduce position size, keep strategy (2008 +82% example)
  - Emotional/Psychological Framework: added "Failures are experiments, not defeats" — post-mortem rule-building
  - Sources: added `raw/jim-simons-models.md` as secondary source
- **Created** `wiki/models/simons-decision-protocol.md` — twelve-lens decision framework synthesising all core Simons principles into a sequential analytical process with pass/fail decision rules and five worked examples
- Updated `wiki/index.md`: Simons Decision Protocol row added to Models table

## [2026-04-18] models | The Man Who Solved the Market (Zuckerman, 2019) — Model pages built
- Created `wiki/models/quantitative-signal-pipeline.md` — five-stage signal discovery, validation, combination, and decay-management process
- Created `wiki/models/mean-reversion-at-speed.md` — intraday/multi-day mean reversion model with asset-class serial correlation thresholds, 51% insight, five-minute bar analysis
- Created `wiki/models/regime-aware-signal-weighting.md` — HMM-based regime detection and signal weight adjustment (Baum-Welch lineage)
- Updated `wiki/models/position-sizing.md` — added Simons/fractional Kelly section alongside Livermore probe system
- Updated `wiki/models/multi-timeframe-confluence.md` — added Simons HMM analogue section with Livermore ↔ Simons equivalence table
- Updated `wiki/index.md` — three new model rows added

## [2026-04-18] re-ingest | The Man Who Solved the Market (Zuckerman, 2019) — FULL PDF READ
- Source: `raw/themanwhosolvedthemarket.pdf` (426 pages) — full text extracted via pdfplumber
- **Major update** to `wiki/pioneers/jim-simons.md`:
  - Added 1967 IDA classified paper ("Probabilistic Models for and Prediction of Stock Market Behavior") as origin of HMM approach
  - Added specific serial correlation numbers by asset class (Deutsche mark 20%, currencies 10%, gold 7%, commodities 4%, stocks 1%)
  - Added Berlekamp's "right 51% at volume" core insight
  - Added weekend effect and pre-report anomaly as named, confirmed tradeable effects
  - Added Laufer's five-minute bar analysis and Friday-band intraday pattern
  - Added Brown-Mercer 1995 unified portfolio optimizer as the actual stock-trading breakthrough
  - Added mean reversion as bedrock equity signal for 10+ years
  - Added nonintuitive signals policy (>50% unexplained by 1997 — traded anyway if statistically valid)
  - Added signal concealment methods (unpredictable spreading, trading to capacity)
  - Added relative pricing approach (not absolute direction)
  - Added source of alpha: exploiting active speculators, not buy-and-hold investors
  - Added 1990 55.9% gain figure and 1993 $280M capacity cap
  - All key quotes attributed with confirmed/inferred markers
- **Created** `wiki/concepts/statistical-arbitrage.md` — new concept page covering stat-arb mechanism, Renaissance implementation, Morgan Stanley APT lineage
- Updated `wiki/index.md`: stat-arb concept row added
- Pages touched: 2 updated/created

## [2026-04-18] ingest | The Man Who Solved the Market (Zuckerman, 2019)
- Source: `raw/themanwhosolvedthemarket.pdf` (121 pages) — PDF renderer unavailable; page built from book knowledge + web research
- Created pioneer page: `wiki/pioneers/jim-simons.md`
  - All 14 schema sections completed
  - Covers: HMM regime detection, statistical arbitrage, fractional Kelly sizing, 50.75% win rate thesis, transaction cost moat, signal decay management, market-neutral construction, psychological framework (eliminate human override)
- Updated `wiki/index.md`: Jim Simons row added to Pioneers table
- Pioneer roster: Jesse Livermore ✓, Jim Simons ✓ — 8 remaining

## [2026-04-18] ingest | How to Trade in Stocks (Livermore, 1940) — PRIMARY SOURCE
- Source: `raw/How-to-Trade-in-Stocks-Jesse-Livermore.pdf` (62 pages, original 1940 text)
- Updated pioneer page: `wiki/pioneers/jesse-livermore.md`
  - Added Pattern-Recognition Rules #8 (Round-Number Pivotal Points with Anaconda/Bethlehem examples) and #9 (New Listing High / Break Below Listing Low)
  - Expanded Market Key section with complete 10 Explanatory Rules: column-change triggers, Secondary Rally/Reaction logic, Pivotal Point marking (red/black underlines), buy/sell signal rules (Rule 7), trend reversal confirmation (Rule 8), 3-point / 6-point resumption rule
  - Elevated source hierarchy: 1940 original is now Primary
- Updated concept page: `wiki/concepts/pivotal-points.md`
  - Added Round-Number, New-High, and Break-Below-Prior-Low Pivotal Point types
  - Added Key Rules #7–9 (3-point, 6-point, round-number rules)
- Updated `wiki/index.md`: source attribution updated to reflect primary source

## [2026-04-18] ingest | Trade Like Jesse Livermore (Smitten, 2005)
- Created pioneer page: `wiki/pioneers/jesse-livermore.md`
- Created concept pages: pivotal-points, trend-following, accumulation-distribution, price-volume, pattern-recognition
- Created model pages: multi-timeframe-confluence, position-sizing, entry-exit-framework
- Initialised `wiki/index.md` and `CLAUDE.md` schema
- Source filed in `raw/Jesse Livermore.md`
- Pages touched: 9 new pages created
