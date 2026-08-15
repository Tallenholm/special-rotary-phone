# Phase-0 v0.7 Adversarial Audit — August 14, 2026

## Decision

**Phase-0 v0.7 is reopened.**

The external red-team audit identified several material specification-level gaps that survive verification. The prior `Feasibility Closed / 10/10` label is therefore withdrawn as a current project-state claim. The v0.7 document remains an important historical baseline, but it is not the active closed specification until the accepted findings below are remediated in v0.8.

This does **not** invalidate the current deterministic EDGAR section-extraction work. PR #1 may continue because it does not yet construct quarterly XBRL fundamentals, historical cross-sectional portfolios, options features, or alternative-data entity links.

## Finding classes

### A. Accepted material gaps — v0.8 blockers

1. **XBRL duration/context integrity**
   - Duration facts must be classified by actual context start/end dates.
   - Discrete-quarter and YTD flows must never be conflated.
   - Where a required discrete flow is absent but mathematically derivable from compatible as-filed cumulative facts, derivation must be explicit, lineage-preserving, and period-compatible.
   - The audit overstates the claim that Q2/Q3 income-statement facts are generally only YTD; many 10-Qs report both three-month and YTD income-statement periods, while cash-flow statements commonly report only YTD. The underlying context-integrity flaw is nevertheless real.

2. **Issuer-class / sector accounting schemas**
   - A single generic commercial concept tree is insufficient for banks, insurers, REITs, broker-dealers, and other specialized issuers.
   - v0.8 must require either economically coherent issuer-class mappings or an explicit predeclared exclusion with coverage reporting. Missing sector concepts must never silently become zero.

3. **Share-count and equity-class dimensionality**
   - Cover-page shares, period-weighted EPS shares, treasury shares, class-specific shares, and consolidated equity are distinct quantities.
   - Per-share and market-cap features require explicit class aggregation/mapping rules and dimensional-context validation.

4. **Non-reliance / Item 4.02 invalidation state**
   - An Item 4.02 non-reliance event can make previously issued financial statements unusable before a later 10-K/A or 10-Q/A arrives.
   - Fundamental features dependent on an affected statement must enter an `INVALIDATED_PENDING_RESTATEMENT` state at the public non-reliance timestamp unless a narrower affected scope is documented.

5. **A0 historical-selection contamination**
   - v0.7 already prohibited strong historical claims without survivorship-clean prices, but this is not enough.
   - Survivor-biased/free historical data may be used for parser QA, plumbing, and explicitly non-selective demonstrations; it may not be used to choose/promote signal families, model architecture, hyperparameters, or ranking thresholds intended for later A1/B confirmation.
   - A0 signal validation is prospective by default unless the historical source independently satisfies the required inactive/delisted/security-master controls.

6. **Point-in-time classification provenance**
   - `as-filed SEC SIC` means the SIC from the accession's archived filing header/SGML or another demonstrably historical source.
   - The current issuer-level SIC exposed by modern convenience APIs must not be assumed to be the historical filing-date classification.
   - SIC remains a coarse fallback; if it cannot support the claimed industry-neutral interpretation, the result must be labeled accordingly rather than upgraded to a GICS-equivalent claim.

7. **Delisting position-state mechanics**
   - A delisting return is not enough. The simulator must define residual capital, cash/reinvestment policy, halts, OTC transitions, liquidation timing, corporate-action state, and terminal marking.
   - Short-side delistings additionally require borrow availability/recall/buy-in/fee/frozen-position assumptions; a mechanical `-55% stock return = +55% short profit` is not accepted as executable evidence without those controls.

8. **Cross-market timestamp synchronization**
   - Every derivative/options feature receives an explicit `feature_as_of` timestamp and may only predict a target whose information interval begins after that timestamp.
   - No universal `EOD` label is sufficient. Products/sessions ending at 4:15 p.m. ET cannot be paired with a 4:00 p.m. cash-equity prediction timestamp for the same overnight target.
   - v0.8 will use timestamp alignment, not a universal 3:59:59 ban: later snapshots may be valid for targets that begin after the later snapshot.

9. **Short financing and cash-yield mechanics**
   - Track B must model borrow fee, stock-loan rebate/credit treatment where applicable, margin/collateral financing, dividends/manufactured payments, halted-position carrying costs, and benchmark-rate regime effects.
   - Long-only and long/short simulations must also state how operational/uninvested cash is remunerated.

10. **Dependence-robust panel inference**
    - `dependence-robust SE` is too vague for cross-sectional multi-period panels.
    - Each experiment must predeclare an inference method appropriate to its estimand and dependence structure, with firm/date two-way clustering, date clustering, Driscoll-Kraay, block/bootstrap, or another justified method as applicable. Overlapping labels must additionally respect horizon-induced serial dependence.

11. **Effective-dated alternative-data entity resolution**
    - Sponsor/awardee/manufacturer names may not be linked with a static current ticker dictionary.
    - Historical entity links require effective-dated parent/subsidiary/ownership lineage; unresolved links remain unresolved rather than being forward-filled through future M&A knowledge.

12. **Versioned public alternative-data snapshots**
    - Live APIs that can revise old records are not automatically historical PIT stores.
    - Historical tests require source-native record histories where available or immutable dated snapshots/dumps captured with acquisition timestamps and hashes.
    - ClinicalTrials.gov exposes record history on the public site; openFDA explicitly warns that updates can change old records, while FDA also publishes non-cumulative quarterly raw adverse-event extract files.

### B. Valid concerns that mostly strengthen existing v0.7 controls

1. **Rule 605 aggregation bias**
   - v0.7 already states that Rule 605 is a calibration prior, not a substitute for strategy-specific fill simulation, and already calls for event/security/order-specific execution tiers.
   - v0.8 should make explicit that average price-improvement credits are not automatically granted in toxic/event windows.

2. **Beta/volatility asymmetry in long-short spreads**
   - v0.7 already requires raw, beta-neutral, size-neutral, and factor-residualized diagnostics.
   - v0.8 should require both the conventional raw/dollar-neutral spread and an ex-ante risk-controlled implementation where economically relevant. It should not replace the raw spread entirely, because the raw spread remains diagnostically useful.

3. **Regime-gate lag and turnover shock**
   - v0.7 already treats a gate as another model and includes turnover/risk acceptance criteria.
   - v0.8 should explicitly charge gate-induced de-risk/re-risk turnover to the gate's own ledger and benchmark binary switching against smoother exposure scaling. Continuous volatility targeting is a benchmark, not a universal mandatory replacement.

4. **Hysteresis under changing score dispersion**
   - The concern is valid as a design risk, but adaptive hysteresis is not a universal law. Static and adaptive rules must compete under nested validation after costs; score dispersion and cost-aware thresholds may be candidate controls.

5. **Historical LLM contamination**
   - v0.7 already flags modern LLM historical knowledge contamination and prioritizes prospective evaluation.
   - v0.8 should distinguish deterministic extraction from subjective semantic alpha generation. A blanket ban based solely on model training cutoff is both difficult to verify and too broad; historical LLM-derived semantic features cannot be confirmatory unless contamination risk is controlled, while deterministic extraction may be allowed if independently validated against source text and designed not to infer future outcomes.

### C. Audit claims/recommendations not accepted as written

1. **Replace sealed holdouts with CPCV** — rejected.
   - v0.7 already uses purged/CPCV development paths, DSR/PBO where useful, one-use sealed chronological evidence, and prospective validation.
   - CPCV reduces selection risk but does not manufacture genuinely unseen future information. Exposed holdouts remain exposed. Finite-data scarcity is a real constraint, not a reason to relabel reused history as fresh confirmation.

2. **All 10-Q Q2/Q3 flows require YTD subtraction** — rejected as a universal rule.
   - Many income statements report both three-month and six-/nine-month periods. Cash-flow statements frequently provide YTD only. The required rule is context-aware duration handling, not blind de-accumulation of every interim flow.

3. **All options features must be cut at 3:59:59 p.m. ET** — rejected as universal.
   - The correct invariant is `feature_as_of <= target_information_start`. A 4:15 snapshot is invalid for a target beginning at the 4:00 cash close, but may be valid for a target beginning after 4:15.

4. **Ex-ante beta-neutral weighting must replace dollar-neutral anomaly spreads** — rejected as universal.
   - Both are useful. Raw/dollar-neutral spreads expose the economics of the original sort; ex-ante beta/risk controls test whether the alpha survives investable risk normalization.

5. **Only pre-event-cutoff pretrained LLMs may parse historical text** — rejected as universal.
   - Model training corpora/cutoffs are often not auditable at the required granularity, and deterministic extraction can be validated independently. The stricter rule applies to historical semantic/subjective feature generation used as alpha evidence, not every parsing task.

## Immediate engineering impact

### Allowed to continue
- immutable SEC raw caching;
- acceptance/availability timestamp handling;
- deterministic 10-K/10-Q section extraction;
- filing-section change/delta records;
- parser fixtures and QA.

### Frozen pending v0.8 specification text
- quarterly XBRL fundamental feature construction;
- generic share-count/per-share valuation signals;
- cross-sectional historical alpha screening on survivor-biased A0 prices;
- options `EOD` feature backtests without synchronized timestamps;
- long-short delisting economics without borrow/financing state;
- alternative-data historical linking without effective-dated entity lineage.

## Primary verification sources

- SEC Inline XBRL: https://www.sec.gov/data-research/structured-data/inline-xbrl
- SEC Accessing EDGAR Data / archived SGML headers: https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data
- SEC Searching With EDGAR Header Fields: https://www.sec.gov/edgar/searchedgar/edgarzones.htm
- SEC Form 8-K Item 4.02 examples in EDGAR archives
- Cboe Equity Options Extended Trading Hours FAQ: https://www.cboe.com/document/tech-spec/document/technical-specifications/equity-options-extended-trading-hours-faq
- SEC Rule 605 FAQs (2026): https://www.sec.gov/rules-regulations/staff-guidance/trading-markets-frequently-asked-questions/frequently-asked-questions-rule-605-regulation-nms
- FINRA brokerage/margin guidance: https://www.finra.org/investors/investing/investment-accounts/brokerage-accounts
- Petersen (2009), RFS, panel standard errors: https://doi.org/10.1093/rfs/hhn053
- ClinicalTrials.gov API / Record History documentation: https://clinicaltrials.gov/data-api/api
- FDA FAERS/AEMS quarterly raw files: https://www.fda.gov/drugs/fdas-adverse-event-reporting-system-faers/fda-adverse-event-reporting-system-faers-latest-quarterly-data-files
- openFDA download warning that updates can change old records: https://open.fda.gov/apis/drug/event/download/

## Gate state

**REOPENED — v0.8 remediation required before the Phase-0 specification can again be described as closed.**
