# Equities Research Lab

Research-first systematic equities project. No live trading system is authorized by the current specification.

## Current source of truth

- **Phase-0 Master Dossier:** v0.7 — historical baseline; gate reopened after adversarial audit
- **Next specification:** v0.8 remediation in progress
- **Research cutoff:** August 14, 2026
- **Repository status:** Phase 0 reopened for verified specification gaps; safe EDGAR parser work may continue
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

## Current build focus

The following free-core EDGAR work remains authorized because the adversarial audit does not invalidate it:

- accession-level SEC ingestion;
- immutable raw-source storage and hashing;
- conservative filing-availability timestamps;
- deterministic 10-K / 10-Q section extraction;
- year-over-year filing-section delta features;
- research-grade tests before model complexity expands.

The next layers are frozen until the v0.8 remediation text is complete: quarterly XBRL fundamental construction, generic per-share/share-count signals, historical A0 cross-sectional alpha screening on survivor-biased prices, unsynchronized EOD options features, long-short delisting economics without borrow/financing state, and alternative-data linking without effective-dated entity lineage.

The Analyst Expectations & Earnings Revisions research remains preserved for later A1 testing, but no enterprise analyst-data purchase is authorized at this stage. Fidelity is useful for retail I/B/E/S-derived research views, but it has not been verified as a bulk historical point-in-time revision source suitable for the planned analyst backtest.

## Repository documentation

- `docs/PHASE_0_STATUS_v0.7.md` — v0.7 historical status plus current reopened gate state.
- `docs/PROJECT_STATUS_2026-08-14.md` — current implementation frontier, data-access decision, budget posture, and red-team gate state.
- `docs/research/PHASE_0_V07_ADVERSARIAL_AUDIT_2026-08-14.md` — verified red-team findings, rejected overstatements, and v0.8 remediation queue.
- `docs/research/ANALYST_EXPECTATIONS_DEEP_DIVE_03_DATA_PATH_AND_FIRST_BACKTEST.md` — analyst experiment and minimum backtest specification.
- `docs/research/ANALYST_EXPECTATIONS_ACCESS_DECISION_2026-08-14.md` — current decision to park paid PIT analyst-data procurement while preserving the branch.
- `docs/research/EDGAR_FILINGS_DEEP_DIVE_02_FIRST_BACKTEST.md` — current free-core EDGAR experiment specification.

The full 48-page v0.7 DOCX remains the master historical Phase-0 artifact outside GitHub. It must not be described as the currently closed specification after the August 14 adversarial audit; a v0.8 remediation revision is required.
