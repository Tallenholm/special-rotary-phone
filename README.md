# Equities Research Lab

Research-first systematic equities project. No live trading system is authorized by the current specification.

## Current source of truth

- **Phase-0 Master Dossier:** v0.8 — targeted-review re-closed specification; **10/10 for currently known specification-level risks only**
- **Implementation status:** not certified; applicable downstream components may now be implemented and tested under the v0.8 contracts
- **Historical baseline:** v0.7 — former feasibility-closed specification, preserved as audit history
- **Research cutoff:** August 14, 2026
- **Phase-0 re-closure:** August 15, 2026
- **Current implementation frontier:** SEC EDGAR filings + company-reported event alpha
- **Analyst Expectations branch:** research-ready but historical testing is parked behind legitimate point-in-time analyst-data access

## Research tracks

- **A0 — Public / Prospective:** public-data exploration and forward evidence. Survivor-biased historical data may be used for plumbing/QA only; it may not select or promote signal/model choices intended for later A1/B confirmation.
- **A1 — Retail-Executable / Research-Grade Historical:** long-only or long-tilted strategies using survivorship-clean historical prices and point-in-time data where required.
- **B — Institutional Long/Short:** adds point-in-time borrow availability/fees, richer commercial data, financing/collateral mechanics, and institutional execution/neutralization requirements.

## Current research rules

1. Research before implementation.
2. No signal becomes ACTIVE without satisfying the Phase-0 experiment protocol and the applicable implementation tests.
3. Publication date, sample-end date, replication date, and forward-validation date are separate.
4. Point-in-time correctness is mandatory.
5. Long-only and long/short economics are reported separately.
6. Costs, borrow constraints, delistings, selection bias, financing, and repeated holdout exposure are first-order variables.
7. Failed hypotheses remain in the Edge Graveyard.
8. Sealed historical tests are one-use confirmatory evidence per research generation; prospective data outrank recycled holdouts.
9. CPCV is a development/selection-risk diagnostic, not a substitute for unseen chronological or prospective evidence.
10. Long-short anomaly/factor tests report the raw dollar-neutral spread, an ex-ante beta/risk-controlled spread, and an attribution bridge by default; omission requires an explicit documented reason.
11. Historical LLM use is governed by task type: auditable extraction may be allowed with source grounding, while subjective semantic alpha remains restricted unless point-in-time contamination risk is controlled.
12. Cross-market features default to `feature_as_of < target_information_start`; equal timestamps require finer-grained ordering evidence proving the feature was available first.
13. Alternative-data entity links are bitemporal, and revisable public-data history requires source-native version history or a snapshot acquired no later than the historical prediction timestamp.

## Current build focus

The upstream EDGAR implementation remains the first engineering frontier:

- accession-level SEC ingestion;
- immutable raw-source storage and hashing;
- conservative filing-availability timestamps;
- deterministic 10-K / 10-Q section extraction;
- year-over-year filing-section delta features;
- research-grade tests before model complexity expands.

After Phase-0 specification re-closure, the previously frozen downstream components may now enter **implementation and test** only under the v0.8 contracts and mandatory test matrix. This includes quarterly XBRL fundamental construction, per-share/share-count features, A0/A1/B eligibility enforcement, synchronized options features, delisting/short-financing state, dependence-aware inference, and bitemporal/versioned alternative-data lineage.

Authorization to implement is not certification. Required tests and proof fields must pass before promotion. Missing required point-in-time data remains a blocker rather than being silently approximated.

The Analyst Expectations & Earnings Revisions research remains preserved for later A1 testing, but no enterprise analyst-data purchase is authorized at this stage. Fidelity is useful for retail I/B/E/S-derived research views, but it has not been verified as a bulk historical point-in-time revision source suitable for the planned analyst backtest.

## Repository documentation

- `docs/PHASE_0_V08_RE_CLOSED_STATUS.md` — current v0.8 re-closed specification status, gate semantics, QA evidence, and engineering boundary.
- `docs/research/PHASE_0_V08_TARGETED_REVIEW_2026-08-15.md` — targeted adversarial review, defects found, remediations, and final disposition.
- `docs/PHASE_0_STATUS_v0.7.md` — v0.7 historical status plus the reopened gate state that led to v0.8.
- `docs/PROJECT_STATUS_2026-08-14.md` — implementation frontier, data-access decision, budget posture, and pre-v0.8 red-team state.
- `docs/research/PHASE_0_V07_ADVERSARIAL_AUDIT_2026-08-14.md` — verified v0.7 red-team findings, rejected overstatements, and remediation queue.
- `docs/research/PHASE_0_V08_VALIDATION_PORTFOLIO_LLM_GOVERNANCE.md` — canonical v0.8 governance rules for validation hierarchy, mandatory dual portfolio reporting, and historical LLM use.
- `docs/research/ANALYST_EXPECTATIONS_DEEP_DIVE_03_DATA_PATH_AND_FIRST_BACKTEST.md` — analyst experiment and minimum backtest specification.
- `docs/research/ANALYST_EXPECTATIONS_ACCESS_DECISION_2026-08-14.md` — current decision to park paid PIT analyst-data procurement while preserving the branch.
- `docs/research/EDGAR_FILINGS_DEEP_DIVE_02_FIRST_BACKTEST.md` — current free-core EDGAR experiment specification.

The final generated v0.8 DOCX is a **59-page** project artifact. All 59 rendered pages were visually inspected after the final targeted-review edits with no clipping, broken tables, missing sections, or header/footer failures found.

## Gate boundary

**Phase-0 research specification:** RE-CLOSED / 10/10 for currently known specification-level risks.  
**Implementation:** OPEN / not yet certified.  
**Historical empirical validation:** OPEN.  
**Prospective validation:** OPEN.  
**Live brokerage / automated real-money execution:** NOT AUTHORIZED.
