# Analyst Expectations Deep Dive 02 — Modern Evidence & Feature Promotion

**Status:** Research branch continuing  
**Cutoff:** August 14, 2026  
**Phase-0 framework:** v0.7 — Feasibility Closed

## Question

Do modern data support analyst-revision features beyond plain EPS revision magnitude, especially after 2010 and around the 2020 regime break?

## Bottom line

The branch remains worth pursuing, but the evidence favors **behavioral/timing structure around revisions** more than a generic analyst-sentiment score.

### Promote / elevate

1. **Analyst-level stickiness / updating behavior — VERY HIGH.** A 2026 *Review of Finance* article reports stronger return predictability from consensus revisions made by sticky analysts than from traditional all-analyst consensus revisions, with stronger effects when forecasting difficulty is high.
2. **Revision speed / information-processing delay — VERY HIGH.** A 2018 *Journal of Financial Economics* study of 983,143 one-year-ahead EPS forecast revisions for U.S. firms over 2003–2013 finds that unexpectedly long I/B/E/S activation delays are associated with muted announcement reactions and larger subsequent drift, especially in neglected stocks.
3. **Change in disagreement conditioned on short constraints — HIGH.** 2023 *Review of Financial Studies* evidence using analyst dispersion through June 2020 shows disagreement shocks can persist for years and become especially important when pessimists are constrained from shorting.
4. **Event-time interaction with earnings — HIGH.** Short-horizon revisions behave differently depending on whether they arrive just after earnings, mid-quarter, or shortly before the next earnings announcement.
5. **Peer / network analyst revisions — HIGH.** 2025 evidence using U.S. data through 2021 finds focal-firm returns react to peer-firm analyst revisions; sign and magnitude depend on rivalry and common-analyst coverage. This supports a network propagation feature rather than isolated-firm treatment.
6. **Analyst-specific skill / responsiveness — HIGH.** Earlier evidence consistently finds heterogeneity across analysts in how they process secondary signals, and modern stickiness results strengthen the case for analyst-specific state variables.

### Keep as conditional, not standalone

- **Revision breadth.** Still plausible but not yet promoted as an independently established anomaly. Breadth should be tested against revision magnitude, analyst count, clustering, and event timing.
- **Revision clustering.** Clustering around earnings and other events is well documented, but much of it can reflect event-driven information release rather than independent alpha. Treat clustering as a context/state feature.
- **Forecast dispersion level.** Raw level remains contaminated by distress, size, short constraints, and denominator effects. Change in dispersion and interaction with short constraints are more defensible.
- **Recommendation revisions.** Modern evidence is weaker than the classic literature. A JFE study finds average post-revision recommendation drift is no longer significant in 2003–2010. Recommendation changes are therefore secondary to EPS revisions.

### Downgrade

- **Raw recommendation level.** Control/context only.
- **Long-horizon growth expectations.** Low prior trust; long-horizon expectations are slow-moving and more exposed to optimism/overreaction.
- **Simple forecast age.** Do not confuse age with behavioral stickiness or information-processing delay.

## Evidence details

### 1. Analyst stickiness is now the strongest modern extension

Cao et al. (2026), *Review of Finance*, estimate analyst-level sticky updating. Sticky analysts tend to compress revisions toward an intermediate/default belief when uncertainty is high. The paper reports that consensus revisions from sticky analysts have stronger return predictability than ordinary consensus revisions, and the relation strengthens when the fraction of sticky analysts covering a stock rises and when forecasting difficulty is elevated.

Source: https://doi.org/10.1093/rof/rfag022

**Feature implication:** estimate analyst-specific updating behavior from historical reactions to earnings/news rather than using a crude `days_since_forecast` variable.

### 2. Vendor activation timing is economically meaningful

The 2018 *Journal of Financial Economics* paper “Determinants and consequences of information processing delay” studies 983,143 one-year-ahead EPS revisions from 2003–2013. Mean activation delay is 1,547 minutes and median delay 551 minutes; the 95th percentile is just under five days. Longer unexpected activation delay is associated with muted immediate announcement response and larger post-announcement drift, concentrated in neglected stocks.

Source: https://doi.org/10.1016/j.jfineco.2017.11.005

**Feature implication:** preserve at least three clocks where possible: analyst issue/announcement time, vendor activation time, and researcher-availability time. Vendor activation delay itself may be a market-friction state variable.

### 3. Disagreement dynamics survived into a sample ending in 2020

Daniel, Klos, and Rottke (2023), *Review of Financial Studies*, use I/B/E/S forecast-dispersion data from May 1980 through June 2020 and lending-fee data from August 2004 through June 2020. Large changes in disagreement decay slowly, over roughly five years. Under short-sale constraints, disagreement and large price shocks are associated with persistent negative abnormal returns.

Source: https://doi.org/10.1093/rfs/hhac075

**Feature implication:** test `delta_dispersion × short_constraint × prior_price_shock`; do not use raw forecast dispersion as a universal stand-alone short signal.

### 4. COVID provides a genuine modern stress episode

Landier and Thesmar (2020), *Review of Asset Pricing Studies*, track analyst expectations during February–May 2020. Forecasts for near-term earnings were progressively cut while longer-run forecasts moved much less; short-horizon dispersion rose sharply. Analysts' revision path was gradual rather than instantaneous.

Source: https://doi.org/10.1093/rapstu/raaa016

**Feature implication:** revision horizon and macro stress must interact. A one-quarter revision is not economically equivalent to a 3–5 year growth revision.

### 5. Recommendation drift appears to have decayed

A 2016 *Journal of Financial Economics* study examines post-recommendation revision drift and reports that average drift is no longer statistically significant in the 2003–2010 high-frequency trading period.

Source: https://doi.org/10.1016/j.jfineco.2015.09.004

**Feature implication:** recommendation changes remain contextual features, but should not be given the same prior weight as EPS estimate revisions.

### 6. Recommendation events can piggyback on corporate news

Altinkilic and Hansen (2009), *Journal of Accounting and Economics*, find that recommendation revisions frequently follow corporate events and news; narrow-window revision reactions are economically small on average.

Source: https://doi.org/10.1016/j.jacceco.2009.04.005

**Feature implication:** isolate the analyst event from the underlying corporate event. A multi-day return around a recommendation revision can wrongly attribute the corporate-news move to the analyst.

### 7. Peer revision propagation now has evidence through 2021

A 2025 study in *Meditari Accountancy Research* uses U.S. listed-company/analyst data from 1996–2021. Focal-firm returns are positively associated on average with peer-firm revisions, but the sign differs for rivals versus nonrivals; common analysts covering both firms strengthen information transfer.

Source: https://doi.org/10.1108/MEDAR-12-2024-2756

**Feature implication:** candidate network state:

`peer_revision × rivalry × common_analyst × peer_weight × focal_response_lag`

This belongs at the intersection of the Analyst and Supply-Chain/Network branches.

### 8. Multi-output inconsistency is not automatically low quality

A 2021 *Journal of Accounting and Economics* paper reports that 20–30% of simultaneous revisions across analyst outputs (earnings estimates, target prices, recommendations) move in opposite directions, but these inconsistent revisions are not generally less accurate or perceived as less valid than consistent ones.

Source: https://doi.org/10.1016/j.jacceco.2020.101339

**Feature implication:** do not force all analyst outputs into a single signed sentiment score. Preserve separate EPS, target-price, and recommendation dimensions and their cross-output consistency state.

## Revised feature hierarchy

| Feature | Priority | Evidence status |
|---|---:|---|
| Short-horizon EPS revision magnitude | Very High | Core historical + modern relevance |
| Analyst stickiness | Very High | Current 2026 evidence |
| Revision / activation speed | Very High | Strong mechanism + JFE evidence |
| Event time relative to earnings/guidance | Very High | Strong mechanism |
| Analyst-specific quality / responsiveness | High | Repeated evidence |
| Change in dispersion × short constraints | High | Evidence through June 2020 |
| Peer/common-analyst revision propagation | High | Evidence through 2021 |
| Consensus deviation / boldness | High | Established conditional information |
| Revision breadth | Medium-High | Hypothesis; independent alpha unproven |
| Revision clustering | Medium-High | Context feature; event confounding risk |
| Cross-output inconsistency | Medium | Preserve as state, not a quality penalty |
| Recommendation revision | Medium | Modern drift weaker |
| Target-price revision | Medium | Complementary only |
| Raw dispersion level | Medium-Low | Conditional / confounded |
| Recommendation level | Low | Control only |
| Long-horizon growth forecast | Low-Medium | Bias/noise concern |

## Required head-to-head tests

The first rigorous A1 analyst backtest should not test dozens of unrelated constructions. It should stage a controlled ladder:

1. `EPS_revision_magnitude` alone.
2. Add `event_time`.
3. Add `analyst_stickiness` / historical responsiveness.
4. Add `delta_dispersion`.
5. Add short-constraint interaction where Track B data exist.
6. Add peer/network revision state.
7. Add breadth and clustering last and require measurable incremental OOS value over the simpler model.

Each step must report incremental Rank IC, net return, turnover, calibration where probabilistic, exposure changes, and whether improvement persists in 2010+, 2020+, and prospective data.

## Promotion rule for breadth/clustering

Revision breadth or clustering is promoted only if it adds out-of-sample information after controlling for:

- signed revision magnitude
- number of active analysts
- event time relative to earnings/guidance
- firm size/liquidity
- prior return
- dispersion level/change
- analyst quality/stickiness composition
- sector/peer revision state

If breadth becomes redundant after these controls, it stays a descriptive state variable rather than a separate signal family.

## Current conclusion

The Analyst Expectations branch remains **HIGH PRIORITY**, but the likely edge is not “analysts are bullish.” The research target is the structure of belief updating:

> **what changed, who changed it, how quickly, relative to what public information, how much analysts disagree, whether pessimists can act, and whether the information propagates across related firms.**

The next pass should determine the realistic point-in-time data path and cost for an A1 historical replication, then specify the minimum first backtest rather than continuing literature accumulation indefinitely.
