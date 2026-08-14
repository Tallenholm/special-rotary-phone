# Analyst Expectations — Data Access Decision

**Date:** August 14, 2026  
**Related experiment spec:** `ANALYST_EXPECTATIONS_DEEP_DIVE_03_DATA_PATH_AND_FIRST_BACKTEST.md`

## Decision

The Analyst Expectations & Earnings Revisions branch remains research-ready, but the historical backtest is **parked until a legitimate point-in-time analyst-estimate dataset is available at a justified cost**.

The literature review and experiment design are not being discarded. They are preserved so the branch can resume later without repeating the research phase.

## Fidelity access

The available Fidelity account provides useful I/B/E/S-derived retail research, consensus views, historical earnings-versus-expectations information, and analyst reports. It is useful for manual inspection and may support prospective observation.

It has **not** been verified as a bulk historical point-in-time analyst-revision database with the complete analyst-level timestamps and revision history required by the planned A1 backtest. Therefore Fidelity retail research must not be treated as equivalent to I/B/E/S Detail, S&P Capital IQ Estimates Snapshot, or another research-grade PIT history product.

## Commercial-data posture

Canonical institutional sources remain valid future options, including:
- LSEG I/B/E/S;
- S&P Capital IQ Estimates Snapshot;
- Zacks historical estimate files;
- Intrinio/Zacks-derived estimate products where timestamp/history fields satisfy the experiment requirements.

However, **no enterprise analyst-data purchase is authorized now**. The project will not spend thousands of dollars on institutional feeds before the free-core lab proves that a specific experiment justifies that cost.

## Current budget rule

Use the least expensive data source that can honestly support the claim being tested:

1. Free/public data first.
2. Low-cost data only when a concrete experiment requires it.
3. Verify survivorship, delisting, timestamp, and identifier quality before treating a cheap source as A1 research-grade.
4. Request institutional quotes only when a surviving signal requires those fields.
5. Never lower point-in-time standards merely to avoid paying for data.

## Current action

Continue the A0/free-core **SEC EDGAR filings + company-reported event alpha** implementation path. Resume the historical analyst backtest later when suitable PIT data becomes economically justified or legitimately accessible.
