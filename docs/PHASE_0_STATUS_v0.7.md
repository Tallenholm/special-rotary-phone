# Phase-0 Status — v0.7 Feasibility Closed

## Scope

Phase 0 is a research specification, not a live trading system. The objective is to identify statistically credible, executable, retail-relevant equity signals while preventing leakage, survivorship bias, false discovery, short-leg illusion, execution fantasy, and point-in-time data errors.

## Research tracks

### A0 — Public / Prospective
Public-data exploration and forward evidence using sources such as SEC EDGAR, ALFRED/FRED, FINRA, public filings, and public event streams. A0 may generate hypotheses and prospective evidence but cannot claim survivorship-clean historical alpha without research-grade historical prices and corporate-action/delisting treatment.

### A1 — Retail-Executable / Research-Grade Historical
Long-only or long-tilted research with survivorship-clean historical prices, inactive/delisted securities, corporate actions, point-in-time fundamentals/classifications where the signal requires them, realistic retail execution assumptions, and explicit delisting math.

### B — Institutional Long/Short
Adds point-in-time securities-lending data, borrow fees/availability, institutional data feeds, richer neutralization layers, and institutional execution/capacity requirements.

## Validation lifecycle

- Chronological development only.
- Nested validation for model/gate tuning.
- Purging/embargo or equivalent horizon-aware controls for overlapping labels.
- CPCV / overfitting diagnostics may supplement chronological validation where appropriate.
- Deflated/selection-adjusted performance statistics are required when many variants are tested.
- A sealed test is one-use confirmatory evidence for a research generation.
- Once its results are viewed, exposure is logged; redesigned models require later confirmatory data.
- Prospective paper/forward evidence outranks recycled historical holdouts.

## Data correctness

- Immutable raw-source snapshots and lineage.
- Accession-level as-filed SEC data for historical fundamentals; current CompanyFacts/Frames are discovery/QA tools, not historical truth by themselves.
- Original and restated facts stored concurrently.
- Effective-dated security identity and sector/industry classifications.
- Corporate actions, splits, dividends, mergers, spin-offs, delistings, exchange calendars, and missing-data states are explicit.
- Historical price research must include inactive/delisted securities for claims of cross-sectional alpha.

## Delisting hierarchy

1. Actual delisting return when available.
2. Defensible post-delisting/recovery value when available and timestamp-correct.
3. Exchange/reason-specific literature-based imputation for missing performance-related delistings.
4. Adverse stress scenario, including -100% where appropriate, reported separately from the base case.

## Signal evaluation

Every signal must report raw and neutralized diagnostics, long and short legs separately, costs before promotion, recent-era and post-publication performance, microcap/liquidity dependence, and sensitivity to restatements/classification choices.

Neutralization is diagnostic rather than an automatic kill criterion. If a signal intentionally captures sector or size propagation, the raw implementation may remain economically meaningful, but the source of returns must be transparent.

## Forecastability / regime gates

A gate is another model. It must be validated inside the same research lifecycle and compared against the ungated model. Acceptance is multi-objective and predeclared: return/CAGR, Sharpe, Sortino, Calmar, maximum drawdown, expected shortfall/tail loss, turnover, and exposure stability may all matter depending on the gate's stated purpose.

## Current project frontier

**SEC EDGAR filings + company-reported event alpha**

The current implementation work is the A0/free-core EDGAR path: accession-level ingestion, immutable raw storage, conservative filing-availability timestamps, deterministic 10-K/10-Q section extraction, and year-over-year filing-section delta features.

The prior **Analyst Expectations & Earnings Revisions** frontier remains a high-priority research branch, but rigorous historical testing is parked behind legitimate point-in-time analyst-data access. Public/prospective research must not reconstruct or scrape unversioned web consensus and call it point-in-time clean.

No enterprise analyst-data purchase is required to continue the current EDGAR implementation work. The analyst branch can resume when a suitable historical PIT source is available at a justified cost.

## Status

Phase-0 specification is closed for currently known vulnerabilities. Any newly discovered material flaw reopens the gate. Research-lab implementation may proceed only where the corresponding data and validation controls are implemented and verified. No live brokerage connection or automated real-money execution is authorized.
