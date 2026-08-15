# Equities Research Lab

Research-first systematic equities project. No live trading system is authorized by the current specification.

## Current source of truth

- **Phase-0 Master Dossier:** v0.7 — Feasibility Closed
- **Research cutoff:** August 14, 2026
- **Repository status:** Phase-0 research specification closed; research-lab implementation underway
- **Current implementation frontier:** SEC EDGAR filings + company-reported event alpha
- **Analyst Expectations branch:** research-ready but historical testing is parked behind legitimate point-in-time analyst-data access

## Research tracks

- **A0 — Public / Prospective:** public-data exploration and forward evidence; no claim of survivorship-clean historical alpha without research-grade historical prices.
- **A1 — Retail-Executable / Research-Grade Historical:** long-only or long-tilted strategies using survivorship-clean historical prices and point-in-time data where required.
- **B — Institutional Long/Short:** adds point-in-time borrow availability/fees, richer commercial data, and institutional execution/neutralization requirements.

## Current research rules

1. Research before implementation.
2. No signal becomes ACTIVE without satisfying the Phase-0 experiment protocol.
3. Publication date, sample-end date, replication date, and forward-validation date are separate.
4. Point-in-time correctness is mandatory.
5. Long-only and long/short economics are reported separately.
6. Costs, borrow constraints, delistings, selection bias, and repeated holdout exposure are first-order variables.
7. Failed hypotheses remain in the Edge Graveyard.
8. Sealed historical tests are one-use confirmatory evidence per research generation; prospective data outrank recycled holdouts.

## Current build focus

The lab is implementing the free-core EDGAR path first:

- accession-level SEC ingestion;
- immutable raw-source storage and hashing;
- conservative filing-availability timestamps;
- deterministic 10-K / 10-Q section extraction;
- year-over-year filing-section delta features;
- research-grade tests before model complexity expands.

The Analyst Expectations & Earnings Revisions research remains preserved for later A1 testing, but no enterprise analyst-data purchase is authorized at this stage. Fidelity is useful for retail I/B/E/S-derived research views, but it has not been verified as a bulk historical point-in-time revision source suitable for the planned analyst backtest.

## Repository documentation

- `docs/PHASE_0_STATUS_v0.7.md` — canonical repository summary of the v0.7 architecture and controls.
- `docs/PROJECT_STATUS_2026-08-14.md` — current implementation frontier, data-access decision, and budget posture.
- `docs/research/ANALYST_EXPECTATIONS_DEEP_DIVE_03_DATA_PATH_AND_FIRST_BACKTEST.md` — analyst experiment and minimum backtest specification.
- `docs/research/ANALYST_EXPECTATIONS_ACCESS_DECISION_2026-08-14.md` — current decision to park paid PIT analyst-data procurement while preserving the branch.
- `docs/research/EDGAR_FILINGS_DEEP_DIVE_02_FIRST_BACKTEST.md` — current free-core EDGAR experiment specification.

The full 48-page v0.7 DOCX remains the master Phase-0 research artifact outside GitHub for now. It does not require a v0.8 merely because implementation status or data-access decisions changed.
