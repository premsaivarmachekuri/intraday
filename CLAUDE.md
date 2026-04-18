# Trading Pioneers Knowledge Graph — Wiki Schema

## Purpose
This wiki is a persistent, compounding knowledge base of legendary trading pioneers — their philosophies, pattern-recognition rules, mathematical models, market behaviours, and multi-timeframe prediction frameworks. The goal is to extract their tactical edge and synthesise a unified system for predicting price behaviour across any stock, sector, or time horizon.

## Directory Structure
```
trading/
  raw/                    ← immutable source documents (books, articles, transcripts)
  wiki/
    index.md              ← master catalog of all wiki pages
    log.md                ← append-only ingest/query/lint log
    pioneers/             ← one page per trading legend
    concepts/             ← cross-cutting ideas (trend-following, accumulation, etc.)
    models/               ← synthesised predictive frameworks
  CLAUDE.md               ← this file
```

## Pioneer Page Schema
Every file in `wiki/pioneers/` must contain these sections:

```markdown
# [Name] ([Birth]–[Death])
> One-sentence distillation of their core edge.

## Background
Brief biography focused on how they developed their edge.

## Core Philosophy
The fundamental beliefs driving all their decisions.

## Pattern-Recognition Rules
Specific, actionable patterns they traded — with precise conditions.

## Mathematical / Quantitative Models
Formulas, ratios, numerical thresholds they used.

## Market Behaviour Observations
How they read price, volume, breadth, sentiment, and crowd psychology.

## Multi-Timeframe Logic
How they reconciled daily, weekly, and long-term structure.

## Entry Rules
Exact conditions required before initiating a position.

## Exit Rules
Conditions that triggered profit-taking or stop-loss.

## Money Management
Position sizing, risk per trade, cash reserve rules.

## Emotional / Psychological Framework
How they controlled fear, greed, hope, and impatience.

## Tactical Edge (Summary)
3–5 bullet points: the specific conditions and behaviours that produced their outsized returns.

## Cross-References
Links to related concept and model pages.

## Sources
Books, interviews, or documents this page was built from.
```

## Concept Page Schema
Files in `wiki/concepts/` distil a cross-pioneer idea:

```markdown
# [Concept Name]
> One-sentence definition.

## Description
## Pioneer Perspectives
(How each relevant pioneer applied this concept — with cross-links)
## Synthesis
## Key Rules
## Cross-References
```

## Model Page Schema
Files in `wiki/models/` are synthesised, actionable frameworks:

```markdown
# [Model Name]
> What it predicts and how to use it.

## Inputs
## Logic
## Decision Rules
## Pioneer Lineage
(Which pioneers' ideas compose this model)
## Examples
## Cross-References
```

## Workflows

### Ingest
1. User drops a source into `raw/` and says "ingest [filename]"
2. Read the source thoroughly
3. Discuss key takeaways with user
4. Update the relevant pioneer page (or create it)
5. Update all affected concept and model pages
6. Update `wiki/index.md`
7. Append an entry to `wiki/log.md`

### Query
1. User asks a question
2. Read `wiki/index.md` to find relevant pages
3. Read those pages
4. Synthesise an answer with citations to wiki pages
5. If the answer is valuable, offer to file it as a new wiki page

### Lint (run periodically)
- Contradictions between pages
- Stale claims superseded by newer sources
- Orphan pages with no inbound links
- Concepts mentioned but lacking their own page
- Missing cross-references
- Data gaps worth filling

## Conventions
- All dates: ISO format (YYYY-MM-DD)
- Pioneer cross-links: `[Jesse Livermore](../pioneers/jesse-livermore.md)`
- Concept cross-links: `[Pivotal Points](../concepts/pivotal-points.md)`
- Model cross-links: `[Multi-Timeframe Confluence](../models/multi-timeframe-confluence.md)`
- Quote attribution: > "Quote text." — Pioneer Name, Source Title
- Certainty markers: use **confirmed** / *inferred* / ~~disputed~~ for claims

## Pioneer Roster (target)
- [x] Jesse Livermore
- [ ] Richard Wyckoff
- [ ] W.D. Gann
- [ ] William O'Neil
- [ ] Nicolas Darvas
- [ ] Mark Minervini
- [ ] Stanley Druckenmiller
- [ ] George Soros
- [ ] Paul Tudor Jones
- [ ] Ed Seykota
