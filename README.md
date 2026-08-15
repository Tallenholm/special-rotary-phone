# Equities Research Lab

Research-first systematic equities project. No live trading system is authorized by the current specification.

## Current source of truth

- **Phase-0 Master Dossier:** v0.8 — red-team-remediated candidate specification; gate remains reopened pending targeted review
- **Historical baseline:** v0.7 — former feasibility-closed specification, preserved as audit history
- **Research cutoff:** August 14, 2026
- **Repository status:** integrated v0.8 candidate complete; safe EDGAR parser work may continue while the targeted re-closure review is pending
- **Current implementation frontier:** SEC EDGAR filings + company-reported event alpha
- **Analyst Expectations branch:** research-ready but historical testing is parked behind legitimate point-in-time analyst-data access

## Research tracks

- **A0 — Public / Prospective:** public-data exploration and forward evidence. Survivor-biased historical data may be used for plumbing/QA only; it may not select or promote signal/model choices intended for later A1/B confirmation.
- **A1 — Retail-Executable / Research-Grade Historical:** long-only or long-tilted strategies using survivorship-clean historical prices and point-in-time data where required.
- **B — Institutional Long/Short:** adds point-in-time borrow availability/fees, richer commercial data, financing/collateral mechanics, and institutional execution/neutralization requirements.

## Current research rules

1. Research before implementation.
2. No signal becomes ACTIVE without satisfying the Phase-0 experiment protocol.
3. Publication date, sample-end date, replication date, and forward-validation date are separate.
4. Point-in-time correctness is mandatory.
5. Long-only and long/short economics are reported separately.
6. Costs, borrow constraints, delistings, selection bias, financing, and repeated holdout exposure are first-order variables.
7. Failed hypotheses remain in the Edge Graveyard.
8. Sealed historical tests are one-use confirmatory evidence per research generation; prospective data outrank recycled holdouts.
9. CPCV is a development/selection-risk diagnostic, not a substitute for unseen chronological or prospective evidence.
10. Long-short anomaly/factor tests report both the raw dollar-neutral spread and an ex-ante beta/risk-controlled spread by default; omission requires an explicit documented reason.
11. Historical LLM use is governed by task type: auditable extraction may be allowed with source grounding, while subjective semantic alpha remains restricted unless point-in-time contamination risk is controlled.

## Current build focus

The following free-core EDGAR work remains authorized because the adversarial audit does not invalidate it:

- accession-level SEC ingestion;
- immutable raw-source storage and hashing;
- conservative filing-availability timestamps;
- deterministic 10-K / 10-Q section extraction;
- year-over-year filing-section delta features;
- research-grade tests before model complexity expands.

The following layers remain frozen until the integrated v0.8 candidate passes targeted re-closure review: quarterly XBRL fundamental construction, generic per-share/share-count signals, historical A0 cross-sectional alpha screening on survivor-biased prices, unsynchronized EOD options features, long-short delisting economics without borrow/financing state, and alternative-data linking without effective-dated entity lineage/versioned source history.

The Analyst Expectations & Earnings Revisions research remains preserved for later A1 testing, but no enterprise analyst-data purchase is authorized at this stage. Fidelity is useful for retail I/B/E/S-derived research views, but it has not been verified as a bulk historical point-in-time revision source suitable for the planned analyst backtest.

## Repository documentation

- `docs/PHASE_0_V08_CANDIDATE_STATUS.md` — current integrated v0.8 candidate status, QA result, engineering boundary, and re-closure checklist.
- `docs/PHASE_0_STATUS_v0.7.md` — v0.7 historical status plus the reopened gate state that led to v0.8.
- `docs/PROJECT_STATUS_2026-08-14.md` — implementation frontier, data-access decision, budget posture, and red-team gate state.
- `docs/research/PHASE_0_V07_ADVERSARIAL_AUDIT_2026-08-14.md` — verified red-team findings, rejected overstatements, and remediation queue.
- `docs/research/PHASE_0_V08_VALIDATION_PORTFOLIO_LLM_GOVERNANCE.md` — canonical v0.8 governance rules for validation hierarchy, mandatory dual portfolio reporting, and historical LLM use.
- `docs/research/ANALYST_EXPECTATIONS_DEEP_DIVE_03_DATA_PATH_AND_FIRST_BACKTEST.md` — analyst experiment and minimum backtest specification.
- `docs/research/ANALYST_EXPECTATIONS_ACCESS_DECISION_2026-08-14.md` — current decision to park paid PIT analyst-data procurement while preserving the branch.
- `docs/research/EDGAR_FILINGS_DEEP_DIVE_02_FIRST_BACKTEST.md` — current free-core EDGAR experiment specification.

The full generated v0.8 DOCX is a 56-page project artifact and has passed page-by-page render QA. It is the active candidate specification for targeted review, but Phase 0 must not be described as closed until that review is complete and any material findings are resolved.
