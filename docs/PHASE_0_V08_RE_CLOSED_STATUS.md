# Phase-0 v0.8 Re-Closed Status

**Date:** August 15, 2026  
**State:** PHASE-0 SPECIFICATION RE-CLOSED / v0.8 / 10/10 FOR CURRENTLY KNOWN SPECIFICATION-LEVEL RISKS  
**Implementation status:** NOT CERTIFIED  
**Master artifact:** `Equities_Research_Phase_0_Master_Dossier_v0.8_RE_CLOSED_FINAL.docx` (59-page generated artifact maintained with the project conversation/library workflow)

## What this status means

The targeted adversarial review of the integrated v0.8 candidate is complete. The Phase-0 **research specification** is re-closed because the accepted material failure modes are now represented by explicit contracts, proof fields, mandatory implementation-test specifications, and a blocker-to-proof-field traceability matrix.

The `10/10` designation is deliberately narrow: it means no unresolved material **specification-level** gap was found in the final targeted review for the risks currently known. It does **not** certify downstream implementation, historical empirical results, prospective performance, brokerage connectivity, automated execution, or real-money deployment.

## Targeted-review defects resolved before re-closure

The review found and fixed four additional specification defects rather than waving the candidate through:

1. **Documentation-gate / implementation-gate circularity.** Phase 0 now requires complete implementation contracts, proof fields, and mandatory test specifications. Actual execution of downstream unit/integration tests belongs to the separate implementation gate.
2. **Cross-market timestamp tie ambiguity.** The default invariant is `feature_as_of < target_information_start`. Equality is allowed only when finer-grained ordering evidence proves the feature was available first; otherwise the observation moves to the next valid target. Conservative dissemination/processing latency remains part of the rule.
3. **Proof-field asymmetry.** The Signal Record now carries explicit delisting position-state, financing/cash-yield, inference-rationale, cross-market tie-break, bitemporal entity-lineage, and public-data PIT-eligibility fields instead of leaving those controls implicit or only in the Experiment Record.
4. **Historical snapshot/entity knowledge-time ambiguity.** Alternative-data relationships are bitemporal. Historical public-data eligibility requires either source-native version history proving what was knowable at the prediction timestamp or an immutable snapshot acquired no later than that timestamp. A later-captured snapshot cannot be projected backward.

## Re-closure evidence

The final specification includes:

- all 12 accepted material findings as explicit contracts;
- a 12-control mandatory implementation-test matrix with minimum test cases and pass/fail invariants;
- a 12-row re-closure traceability matrix linking each blocker to its detailed contract, Signal Record proof field(s), and Experiment Record proof field(s);
- explicit A0/A1/B eligibility requirements;
- mandatory raw dollar-neutral, ex-ante risk-controlled, and attribution views for applicable long-short research;
- tiered historical-LLM governance and grounding evidence;
- strict cross-market availability ordering and conservative tie handling;
- bitemporal entity resolution and point-in-time public-data snapshot eligibility.

## Artifact QA

The final DOCX renders to **59 pages**. All 59 rendered pages were visually inspected after the last edits. No clipping, broken tables, missing sections, or header/footer failures were found. Automated semantic checks also confirmed:

- no current `STATUS: REOPENED` claim;
- no stale `feature_as_of <= target_information_start` rule;
- the strict `<` ordering rule is present;
- 12 mandatory implementation-test rows;
- 12 re-closure traceability rows;
- the new Signal Record and Experiment Record proof fields are present.

## Engineering boundary after specification re-closure

The v0.8 contracts now authorize the affected downstream components to enter **implementation and test**, including XBRL fundamental construction, per-share/share-count features, track enforcement, synchronized options features, delisting/short-financing state, dependence-aware inference, and bitemporal/versioned alternative-data lineage.

That authorization is not certification. A component may be promoted only after its applicable mandatory tests pass and its proof fields are populated. Missing required PIT data remains a blocker rather than an invitation to fabricate or silently approximate evidence.

## What is still not authorized

- calling an untested downstream component implementation-ready;
- promoting a historical result without satisfying its track/data contracts;
- using survivor-contaminated A0 history for prohibited signal/model selection;
- connecting a live brokerage account merely because Phase 0 closed;
- automated real-money execution or production deployment without later implementation, empirical, prospective-validation, and deployment gates.

The detailed review record is in `docs/research/PHASE_0_V08_TARGETED_REVIEW_2026-08-15.md`.