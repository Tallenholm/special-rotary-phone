# Equities Research Lab

Research-first systematic equities project. No live trading system is authorized by the current specification.

## Current source of truth

- **Phase-0 Master Dossier:** v0.7 — Feasibility Closed
- **Research cutoff:** August 14, 2026
- **Repository status:** synced to the v0.7 research specification summary
- **Current research frontier:** Analyst Expectations & Earnings Revisions

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

## Repository file

- `docs/PHASE_0_STATUS_v0.7.md` — canonical repository summary of the current v0.7 architecture, controls, validation lifecycle, and research frontier.

The full 48-page v0.7 DOCX remains the master research artifact outside GitHub for now. The repository will become the implementation source of truth once code/data-pipeline work begins.

The next research pass focuses on EPS estimate revisions, revision breadth, forecast dispersion, staleness, revision speed, analyst disagreement, and interaction with earnings surprises / PEAD.
