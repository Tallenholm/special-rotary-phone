# Phase-0 Status — v0.7 Historical Baseline / Gate Reopened

## Current gate state

**REOPENED on August 14, 2026 after an adversarial red-team audit identified material specification-level gaps.**

The prior `Feasibility Closed / 10/10` label is withdrawn as a current project-state claim. v0.7 remains the historical baseline document, but v0.8 remediation is required before Phase 0 can again be described as closed.

The verified findings and rejected overstatements are recorded in:

- `docs/research/PHASE_0_V07_ADVERSARIAL_AUDIT_2026-08-14.md`

## Scope

Phase 0 is a research specification, not a live trading system. The objective is to identify statistically credible, executable, retail-relevant equity signals while preventing leakage, survivorship bias, false discovery, short-leg illusion, execution fantasy, point-in-time data errors, and data-lineage failures.

## Research tracks

### A0 — Public / Prospective
Public-data and forward evidence using sources such as SEC EDGAR, ALFRED/FRED, FINRA, public filings, and public event streams.

A0 is prospective by default for signal evidence. Historical public/free data may be used for ingestion QA, parser testing, plumbing, and other explicitly non-selective engineering tasks. It may not be used to choose/promote signal families, model architecture, hyperparameters, or ranking thresholds intended for later A1/B confirmation unless the historical source independently satisfies the required inactive/delisted/security-master controls.

### A1 — Retail-Executable / Research-Grade Historical
Long-only or long-tilted research with survivorship-clean historical prices, inactive/delisted securities, corporate actions, point-in-time fundamentals/classifications where the signal requires them, realistic retail execution assumptions, explicit delisting state mechanics, and dependence-robust inference.

### B — Institutional Long/Short
Adds point-in-time securities-lending data, borrow fees/availability, recalls/buy-ins, short financing/rebate and collateral mechanics, richer commercial data, and institutional execution/capacity requirements.

## Validation lifecycle

- Chronological development only.
- Nested validation for model/gate tuning.
- Purging/embargo or equivalent horizon-aware controls for overlapping labels.
- CPCV / overfitting diagnostics may supplement chronological validation where appropriate.
- Deflated/selection-adjusted performance statistics are required when many variants are tested.
- A sealed test is one-use confirmatory evidence for a research generation.
- Once its results are viewed, exposure is logged; redesigned models require genuinely later confirmatory evidence or prospective forward data.
- CPCV reduces historical selection risk but does not make exposed history unseen again.
- Prospective paper/forward evidence outranks recycled historical holdouts.

## Data correctness — v0.8 remediation requirements

Existing v0.7 controls remain, with the following additions now mandatory for the next closed specification:

- Immutable raw-source snapshots and lineage.
- Accession-level as-filed SEC data for historical fundamentals; current CompanyFacts/Frames are discovery/QA tools, not historical truth by themselves.
- XBRL duration contexts must distinguish discrete-quarter from cumulative YTD facts; derived quarter flows must preserve source lineage.
- Specialized issuer classes such as banks, insurers, REITs, and broker-dealers require coherent mapping schemas or explicit predeclared exclusion.
- Share-count facts require class/dimension/measurement-basis validation before any per-share or market-cap feature is used.
- Form 8-K Item 4.02 non-reliance events must invalidate affected historical financial-statement features until a valid replacement becomes public.
- Original and restated facts remain stored concurrently.
- `As-filed SEC SIC` means archived accession-level filing-header/SGML provenance, not a current convenience-API issuer classification assumed to be historical.
- Effective-dated security identity and sector/industry classifications are required where the claim depends on them.
- Corporate actions, splits, dividends, mergers, spin-offs, delistings, exchange calendars, and missing-data states are explicit.
- Delisting simulation must define residual-capital/cash/reinvestment state and, for shorts, borrow/recall/buy-in/frozen-position assumptions.
- Options/derivatives features require explicit as-of timestamps aligned to the prediction target; `EOD` is not an acceptable timestamp abstraction by itself.
- Alternative-data entity mappings require effective-dated corporate lineage, and historical tests require versioned/source-native record history or immutable dated snapshots where live APIs can revise old records.
- Statistical inference must predeclare a method appropriate to both time-series and cross-sectional dependence; `robust SE` without a dependence model is insufficient.

## Signal evaluation

Every signal must report raw and neutralized diagnostics, long and short legs separately, costs before promotion, recent-era and post-publication performance, microcap/liquidity dependence, and sensitivity to restatements/classification choices.

For long-short signals, the conventional raw/dollar-neutral spread remains diagnostically useful, but an ex-ante beta/risk-controlled implementation must also be tested when structural leg asymmetry is economically material.

## Forecastability / regime gates

A gate is another model. It must be validated inside the same research lifecycle and compared against the ungated model. Acceptance is multi-objective and predeclared. Gate-triggered de-risk/re-risk turnover and slippage are charged to the gate itself. Binary switching should be benchmarked against smoother exposure scaling rather than assumed superior.

## Execution calibration

Rule 605 and similar public execution-quality statistics are priors, not direct fill subsidies. Average price-improvement figures must not be granted automatically to event-driven or toxic-flow orders; strategy-specific adverse-fill/slippage scenarios remain mandatory.

## LLM historical-use boundary

Modern LLMs are not presumed point-in-time clean for historical semantic alpha generation. Historical subjective/semantic LLM features cannot serve as confirmatory evidence unless contamination risk is controlled. Deterministic extraction may be used as an engineering parser only when independently validated against the source text and not permitted to infer future outcomes.

## Current project frontier

**SEC EDGAR filings + company-reported event alpha**

The following work remains authorized while v0.8 remediation is written:
- accession-level ingestion;
- immutable raw storage;
- conservative filing-availability timestamps;
- deterministic 10-K/10-Q section extraction;
- year-over-year filing-section delta features;
- parser fixtures and QA.

The following are frozen pending v0.8 specification completion:
- quarterly XBRL fundamental feature construction;
- generic per-share/share-count valuation signals;
- survivor-biased A0 historical signal/model selection;
- unsynchronized EOD options backtests;
- long-short delisting economics without borrow/financing state;
- alternative-data historical linking without effective-dated entity lineage.

The Analyst Expectations & Earnings Revisions branch remains high priority but parked behind legitimate point-in-time analyst-data access. No enterprise analyst-data purchase is authorized at this stage.

## Status

**Phase-0 v0.7 is not closed.** The gate remains reopened until the accepted findings in the August 14, 2026 adversarial audit are incorporated into v0.8 and the revised specification passes another targeted red-team review. No live brokerage connection or automated real-money execution is authorized.
