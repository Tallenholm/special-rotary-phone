# Project Status — August 14, 2026

## Current state

**Phase 0 is reopened.**

A new adversarial audit identified several specification-level gaps that survive verification. The former `v0.7 Feasibility Closed / 10/10` label is withdrawn as a current project-state claim. v0.7 remains the historical baseline; v0.8 remediation is required before the gate can be closed again.

The verified audit is recorded in:
- `docs/research/PHASE_0_V07_ADVERSARIAL_AUDIT_2026-08-14.md`

## Active implementation frontier

**SEC EDGAR filings + company-reported event alpha**

The current parser/storage slice remains authorized because the audit does not invalidate it:
- accession-level SEC ingestion;
- immutable raw payload storage and hashing;
- conservative filing-availability timestamps;
- deterministic 10-K / 10-Q section extraction;
- year-over-year section-delta features;
- parser fixtures and QA.

PR #1 remains a valid review target.

### Frozen until v0.8 remediation is complete

- quarterly XBRL fundamental feature construction;
- generic share-count / per-share valuation signals;
- historical A0 cross-sectional signal selection using survivor-biased price data;
- options `EOD` feature tests without explicit cross-market timestamp alignment;
- long-short delisting simulations without borrow/recall/financing state;
- historical alternative-data linking without effective-dated entity resolution and versioned source records.

## Major accepted v0.8 remediation items

1. XBRL duration/context integrity and safe de-accumulation.
2. Specialized issuer-class accounting schemas or explicit exclusions.
3. Share-class/dimensional share-count rules.
4. Item 4.02 non-reliance invalidation state.
5. A0 historical-selection contamination controls.
6. Archived accession-level provenance for historical SEC SIC fallback.
7. Delisting position-state mechanics including OTC/short-side treatment.
8. Options/derivatives feature `as_of` synchronization with prediction targets.
9. Short financing/rebate/cash-yield mechanics.
10. Explicit dependence-robust panel inference.
11. Effective-dated alternative-data entity-resolution graph.
12. Versioned historical snapshots for public APIs whose old records can change.

Several audit recommendations were intentionally narrowed or rejected: CPCV does not replace genuinely unseen holdouts; not every Q2/Q3 flow requires blind YTD subtraction; not every options feature must be cut at 3:59:59 p.m.; raw dollar-neutral spreads remain useful alongside beta/risk-controlled implementations; and a blanket ban on every modern-LLM historical parsing task is too broad.

## Analyst Expectations branch

The Analyst Expectations & Earnings Revisions branch remains a **high-priority research branch**, but rigorous historical testing is still data-gated.

A proper historical test requires a legitimate point-in-time analyst-estimate dataset such as LSEG I/B/E/S, S&P Capital IQ Estimates Snapshot, or a sufficiently detailed alternative that preserves revision history and timestamps.

### Current access decision

- Fidelity provides useful I/B/E/S-derived retail research and consensus views, but it has not been verified as a bulk historical point-in-time analyst-revision source suitable for the lab's A1 backtest.
- Full institutional point-in-time products are commercial/licensed datasets and are not required to continue the current free-core work.
- **No enterprise analyst-data purchase is authorized at this stage.**
- The analyst experiment specification is preserved so the branch can resume later without repeating the literature/design work.

## Budget posture

Current priority is to maximize research progress with free or low-cost data:

1. SEC EDGAR and other public sources first.
2. Add inexpensive historical price/security data only for a concrete experiment and only after its survivorship/delisting limitations are understood.
3. Do not use cheap survivor-biased history for model/signal selection merely because the result will later be labeled `exploratory`.
4. Request Zacks/Intrinio/LSEG/S&P quotes only when a surviving experiment genuinely requires them.
5. Do not buy institutional data merely because it is the canonical academic source.

## Live-trading boundary

This remains a research/backtesting system. No brokerage connection, automated execution, or real-money strategy deployment is authorized. The Phase-0 gate must be re-closed under v0.8 before broader research-lab implementation resumes beyond the safe EDGAR parser/storage layer.
