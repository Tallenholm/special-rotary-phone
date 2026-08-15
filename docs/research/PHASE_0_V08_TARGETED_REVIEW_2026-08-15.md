# Phase-0 v0.8 Targeted Adversarial Review — 2026-08-15

## Review target

Integrated Phase-0 Master Dossier v0.8, produced after the August 14 adversarial audit reopened the historical v0.7 gate.

## Review objective

Determine whether the v0.8 remediation actually closes the newly identified specification-level failure modes, rather than accepting the presence of remediation prose as evidence of closure.

The review specifically attacked:

- data/model-contract completeness;
- point-in-time and timestamp semantics;
- XBRL context and issuer-class rules;
- share-class dimensionality;
- invalidation/restatement state;
- A0 selection contamination;
- historical classification provenance;
- delisting and short-position state;
- financing/cash economics;
- dependence-aware inference;
- effective-dated/versioned alternative data;
- experiment/signal proof-field completeness;
- the logical separation between documentation closure and implementation verification.

## Findings discovered during targeted review

### TR-01 — Documentation-gate circularity

**Severity:** material specification defect  
**Problem:** The candidate froze affected downstream pipelines until Phase 0 re-closed while simultaneously requiring those pipelines to already contain passing unit/integration tests as a re-closure condition. This could deadlock the gate or encourage test claims about code that the specification itself had not authorized to be implemented.

**Resolution:** Phase-0 re-closure now requires complete implementation contracts, proof fields, and mandatory test specifications. Executing those tests is explicitly assigned to the subsequent implementation gate.

**Disposition:** CLOSED.

### TR-02 — Cross-market equal-timestamp leakage ambiguity

**Severity:** material specification defect  
**Problem:** The candidate said derivatives information must precede the target interval but elsewhere encoded `feature_as_of <= target_information_start`. At coarse timestamp resolution, equality can conceal contemporaneous information or uncertain ordering.

**Resolution:** Default invariant changed to `feature_as_of < target_information_start`. Equality is accepted only with finer-grained sequence/order evidence proving the feature was available first. Otherwise the feature is shifted to the next valid target. Conservative dissemination/processing latency remains mandatory.

**Disposition:** CLOSED.

### TR-03 — Signal/Experiment proof-field asymmetry

**Severity:** material auditability defect  
**Problem:** Several v0.8 controls were explicit in the Experiment Record but only implied or absent in the Signal Record, weakening promotion-time traceability.

**Resolution:** Signal Record proof fields now explicitly cover short financing/rebate/collateral/cash yield, delisting position state/residual capital/short closeout, cross-market tie handling, bitemporal alternative-data entity lineage, public-data PIT eligibility, and dependence-structure/estimator rationale.

**Disposition:** CLOSED.

### TR-04 — Historical snapshot and entity knowledge-time ambiguity

**Severity:** material point-in-time defect  
**Problem:** A literal reading of the candidate could allow a public-data snapshot first captured after a historical prediction timestamp to be treated as proof of what the API exposed earlier. Entity relationships also needed explicit knowledge-time, not only economic valid-time.

**Resolution:** Alternative-data lineage is now bitemporal. A historical record is eligible only if source-native version history reconstructs the state knowable at `t_pred`, or an immutable snapshot/dump was acquired no later than `t_pred`. Later-captured snapshots are prospective-only absent native history proving the prior state.

**Disposition:** CLOSED.

## Testability hardening

A second clean pass found that saying “mandatory tests must be specified” was still too abstract. The final specification therefore adds a 12-control implementation-test matrix. Every accepted material blocker has:

1. minimum mandatory test cases; and
2. an explicit pass invariant.

The matrix covers:

1. XBRL duration/context integrity;
2. specialized issuer accounting;
3. share-class dimensionality;
4. Item 4.02 non-reliance;
5. A0 historical-selection firewall;
6. historical classification provenance;
7. delisting position-state mechanics;
8. cross-market timestamp synchronization;
9. financing and cash yield;
10. dependence-robust inference;
11. bitemporal alternative-data entity resolution; and
12. versioned public-data snapshots.

The final specification also adds a 12-row traceability matrix linking every blocker to its detailed contract, Signal Record proof field(s), and Experiment Record proof field(s).

## Final targeted-review result

**Result:** PASS — no unresolved material specification-level gap identified after the final remediation pass.

**Phase-0 specification status:** RE-CLOSED / v0.8 / 10/10 for currently known specification-level risks.

This score is intentionally bounded. It does not certify implementation correctness, empirical alpha, prospective robustness, brokerage integration, automated execution, or production readiness. Those remain separate gates and require independent evidence.

## Final artifact QA

The re-closed master DOCX renders to 59 pages. All 59 pages were visually inspected after final edits. No clipping, broken tables, missing sections, or header/footer failures were found. Semantic checks confirmed the final closure state, strict cross-market ordering rule, 12 test-matrix rows, 12 traceability rows, and expanded proof fields.
