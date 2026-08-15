# Project Status — August 14, 2026

## Current state

Phase-0 v0.7 remains feasibility-closed for currently known specification-level risks. The project has moved from research-design work into implementation of the research lab.

## Active implementation frontier

**SEC EDGAR filings + company-reported event alpha**

Current build focus:
- accession-level SEC ingestion;
- immutable raw payload storage and hashing;
- conservative filing-availability timestamps;
- deterministic 10-K / 10-Q section extraction;
- year-over-year section-delta features;
- research-grade tests before broader feature expansion.

The first parser/delta upgrade is under review in PR #1.

## Analyst Expectations branch

The Analyst Expectations & Earnings Revisions branch remains a **high-priority research branch**, but rigorous historical testing is currently data-gated.

A proper historical test requires a legitimate point-in-time analyst-estimate dataset such as LSEG I/B/E/S, S&P Capital IQ Estimates Snapshot, or a sufficiently detailed alternative that preserves revision history and timestamps.

### Current access decision

- Fidelity provides useful I/B/E/S-derived retail research and consensus views, but it has not been verified as a bulk historical point-in-time analyst-revision source suitable for the lab's A1 backtest.
- Full institutional point-in-time products are commercial/licensed datasets and are not required to continue the current free-core work.
- **No enterprise analyst-data purchase is authorized at this stage.** The project will not spend thousands of dollars on institutional feeds before the free-core research lab and cheaper data paths justify that expense.
- The analyst experiment specification is preserved so the branch can resume later without repeating the literature/design work.

## Budget posture

Current priority is to maximize research progress with free or low-cost data:

1. SEC EDGAR and other public sources first.
2. Add inexpensive historical price/security data only when required for a concrete backtest and after checking its survivorship/delisting limitations.
3. Use low-cost consensus products only if they satisfy a specific experiment's timestamp/history requirements.
4. Request Zacks/Intrinio/LSEG/S&P quotes only when the lab has reached a test that genuinely requires them.
5. Do not buy institutional data merely because it is the canonical academic source.

## Live-trading boundary

This remains a research/backtesting system. No brokerage connection, automated execution, or real-money strategy deployment is authorized by the current project stage.
