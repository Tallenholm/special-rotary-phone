# Analyst Expectations Deep Dive 03 — Data Path & Minimum First Backtest

**Status:** Practical feasibility defined  
**Cutoff:** August 14, 2026  
**Phase-0 framework:** v0.7 — Feasibility Closed

## Decision

The Analyst Expectations branch is practical enough to continue, but rigorous historical testing is an **A1 research-grade data problem**, not a free-core historical backtest.

The minimum viable path is to obtain legitimate point-in-time analyst-estimate history, pair it with survivorship-clean price/security-master data, and test a deliberately small revision model before adding breadth, network, or complex behavioral features.

## Candidate point-in-time analyst datasets

### LSEG I/B/E/S

LSEG describes I/B/E/S as covering analyst detail, consensus, actuals, guidance, and related analytics with U.S. history back to 1976 and international history back to 1987. LSEG also exposes individual analyst forecasts and provides point-in-time/timestamp-oriented fields across related products.

Important implementation caveat: WRDS warns that I/B/E/S analyst and broker identifiers have been reassigned/reshuffled across data vintages. Analyst-specific features therefore must be **vintage-aware**. Do not assume a raw analyst ID is globally permanent across refreshed vendor files.

Practical access routes:
- Direct LSEG commercial license / API / bulk / cloud access.
- Institutional/academic access through WRDS where the institution subscribes to I/B/E/S.

Pricing is quote-based; no public list price should be assumed.

Primary sources:
- https://www.lseg.com/en/data-analytics/financial-data/company-data/ibes-estimates
- https://wrds-www.wharton.upenn.edu/pages/grid-items/thomson-reuters-ibes-demo/
- https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/vendor-partner-ibes/

### S&P Capital IQ Estimates Snapshot

S&P provides consensus, detailed estimates, revision history, analyst coverage, company guidance, and point-in-time snapshot data. Its current Snapshot product captures estimate-database changes every two hours and explicitly exposes effective-date/time fields. The current product page states that exact snapshot history is available from August 2016.

S&P also reports longer historical estimate coverage (North America from roughly 1999), but the **two-hour point-in-time Snapshot** is a newer history layer. Do not treat older generic historical estimates as equivalent to exact snapshot history without confirming field semantics and backfill methodology.

Pricing is quote-based.

Primary sources:
- https://www.spglobal.com/market-intelligence/en/solutions/capital-iq-estimates
- https://www.marketplace.spglobal.com/en/datasets/s-p-capital-iq-estimates-%281%29

### Vendor-derived quality signals

LSEG SmartEstimates weights analyst forecasts by recency and historical accuracy and includes RevisionCluster detection. These are useful benchmarks, but proprietary composite analytics must not become the only version of the signal; the lab should reproduce transparent primitive features where licensing permits.

Primary source:
- https://www.lseg.com/en/data-catalogue/analytics/quantitative-analytics/starmine-smartestimates

## Recommended first data choice

### Preferred A1 research path

**I/B/E/S Detail + CRSP** if legitimate WRDS/institutional access is available.

Why:
- Deep U.S. analyst history.
- Individual analyst-level records needed for responsiveness/stickiness research.
- Widely used in the literature we are trying to replicate.
- CRSP supplies inactive/delisted securities, durable identifiers, and terminal-return handling for research-grade cross-sectional validation.

### Preferred modern timestamp path

**S&P Capital IQ Estimates Snapshot + research-grade prices/security master** if the goal is a cleaner modern-era test beginning in 2016.

Why:
- Explicit two-hour point-in-time snapshots.
- Strong fit for a 2016+ / 2020+ modern validation branch.
- Directly supports revision direction/magnitude and coverage changes.

### A0 public/prospective fallback

If neither commercial path is available, do **not** fabricate historical analyst consensus.

Instead:
- capture analyst events prospectively from legally accessible sources;
- timestamp raw observations at acquisition time;
- pair with public EDGAR/company guidance/event data;
- build forward paper evidence only.

That evidence remains A0 until a research-grade historical dataset independently confirms the signal.

## Minimum first backtest — deliberately small

### Objective

Test whether **short-horizon EPS revision magnitude** contains modern cross-sectional information after proper timestamps, costs, event timing, and survivorship controls.

Do not begin with a giant analyst-feature model.

### Universe

- U.S. common equities.
- Exclude ADRs/ETFs/preferreds unless explicitly included later.
- Point-in-time universe.
- Minimum price/liquidity thresholds frozen before testing.
- Report large/liquid universe separately from broad universe.
- Include inactive/delisted securities.

### Prediction timestamp

For every analyst revision:

`available_time = max(valid_vendor_activation_time, documented_researcher_availability_time)`

If true analyst issue time is separately available, preserve it as another field rather than replacing activation time.

No signal may trade before `available_time` plus a conservative execution delay.

### Core feature v1

For analyst j, stock i, target period p:

`revision = new_estimate - prior_estimate`

Test scaling variants predeclared in one small family:

1. raw EPS revision;
2. revision / abs(prior consensus), with denominator floor;
3. revision / stock price;
4. standardized revision relative to that stock's recent analyst-revision distribution.

Do not search dozens of scaling choices.

### Consensus aggregation v1

Construct transparent point-in-time consensus from active valid analyst estimates.

Report:
- mean;
- median;
- analyst count;
- dispersion;
- age distribution.

Vendor-provided consensus is a benchmark, not automatically the sole source of truth.

### Event-time buckets

Predeclare:
- 0–2 trading days after earnings;
- 3–20 trading days after earnings;
- >20 days after earnings / pre-next-event;
- optional 5-trading-day pre-earnings bucket only when no blackout/leakage issue exists.

### Return horizons

Start with:
- 1 trading day;
- 5 trading days;
- 20 trading days;
- 60 trading days.

The primary economic horizon should be 5 or 20 days; 1-day is primarily information-incorporation diagnostics and 60-day tests persistence.

### Baselines

Before any behavioral feature:

1. no-skill / random ranking;
2. recent stock momentum;
3. standardized earnings surprise alone;
4. simple consensus EPS revision alone.

Any extension must beat the simple EPS-revision baseline out of sample.

### Portfolio tests

Report:
- quintile/decile rank spreads;
- long-only top bucket vs benchmark;
- long-short spread for research only;
- long-leg and short-leg economics separately;
- sector-neutral diagnostic;
- size/beta-neutral diagnostic;
- turnover and costs.

Track A1 retail feasibility is judged primarily from long-only / long-tilted economics.

### Historical generations

If sufficient history exists:

- development: older period;
- first sealed modern generation: 2010–2015 or similar depending on vendor coverage;
- second modern generation: 2016–2019;
- crisis/outlier diagnostic: 2020;
- later sealed generation: 2021–2024/2025 depending on data availability;
- prospective period thereafter.

Exact boundaries must be selected before inspecting final strategy results and depend on the licensed dataset.

For S&P Snapshot specifically, exact two-hour PIT history begins in August 2016, so do not invent earlier snapshot generations.

## Feature ladder after the baseline survives

Only if revision magnitude survives:

### Stage 2 — event timing
Add:
- days since earnings;
- days to next earnings;
- guidance proximity.

### Stage 3 — analyst behavior
Add:
- historical analyst accuracy;
- responsiveness to prior earnings/news;
- analyst stickiness.

### Stage 4 — disagreement
Add:
- dispersion level;
- delta dispersion;
- analyst count / coverage change.

### Stage 5 — breadth/clustering
Add:
- fraction revising upward/downward;
- number of revisions in trailing 1/3/5 trading days;
- cluster intensity normalized by coverage.

Breadth/clustering graduate only if they add OOS value beyond revision magnitude + event timing + analyst composition.

### Stage 6 — network
Add:
- peer revision state;
- common analyst links;
- bellwether exposure;
- rivalry/supply-chain context where justified.

## Critical data-quality tests

1. **Analyst-ID vintage stability** — never silently stitch reshuffled I/B/E/S analyst IDs across vendor vintages.
2. **Activation timestamp leakage** — distinguish issue time from vendor activation/researcher availability.
3. **Stale estimate policy** — vendor policies differ; reproduce and sensitivity-test a transparent age cutoff.
4. **Split adjustment** — use a historically safe methodology; do not allow ex-post split adjustments to rewrite historical forecast values.
5. **Consensus basis changes** — analysts may estimate different accounting bases; track inclusion/exclusion rules.
6. **Coverage changes** — a disappearing analyst is information/missingness, not automatically a zero revision.
7. **Delisted firms** — preserve terminal returns.
8. **Identifier mapping** — use point-in-time CRSP/IBES links or equivalent, not current tickers.

## Feasibility verdict

**GO for research, NOT GO for implementation.**

The branch is sufficiently supported to justify obtaining/accessing a legitimate PIT analyst dataset and running a controlled first replication. The next useful action is no longer another broad literature review; it is either:

1. establish whether I/B/E/S/WRDS or S&P Estimates Snapshot access is available; or
2. if not, start an A0 prospective capture pipeline while continuing other free-core signal research in parallel.

No analyst-alpha claim should be made until one of those data paths exists.
