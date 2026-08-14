# Analyst Expectations Deep Dive 01

**Status:** Research in progress  
**Cutoff:** August 14, 2026  
**Phase-0 framework:** v0.7 — Feasibility Closed

## Research question

Which components of analyst expectations contain independently useful, executable information for future stock returns, and which are merely delayed reflections of public information?

## Current verdict

Analyst information should not be represented as a single sentiment variable. The strongest evidence supports a multidimensional event/state representation built around **short-horizon EPS revisions, timing/responsiveness, deviation from consensus, analyst quality, and disagreement conditioned on short-sale constraints**.

### Promote to high-priority research

1. **Short-horizon EPS forecast revision magnitude** — strong historical evidence; must be tested with genuine point-in-time estimate history.
2. **Revision responsiveness after earnings** — strong mechanism evidence. Prompt analyst updating is associated with more immediate price incorporation and less PEAD.
3. **Analyst-level stickiness / slow updating** — very high-priority modern hypothesis. A 2026 *Review of Finance* paper reports that consensus revisions from sticky analysts have stronger return predictability than ordinary consensus revisions, especially when forecast difficulty is high.
4. **Deviation from consensus / boldness** — high priority. Revisions away from consensus have stronger price impact and influential revisions are more likely to come from leaders/stars and to move away from consensus.
5. **Disagreement × short-sale constraints** — high priority, especially as a short-leg / mispricing state rather than a simple long-only signal.
6. **Change in disagreement / dispersion dynamics** — research-worthy state variable; disagreement shocks decay slowly and interact with shorting constraints.
7. **Bellwether revision propagation** — high-priority network hypothesis for related-company spillovers.

### Keep as conditional / diagnostic

- **Forecast dispersion level:** historically associated with lower future returns, but interpretation is contested and the effect is strongly linked to small/distressed/short-constrained firms.
- **Recommendation changes:** informative only conditionally; many recommendation revisions do not visibly move price.
- **Target-price revisions:** possible complementary information, but lower priority than EPS revisions.
- **Long-horizon analyst growth forecasts:** lower prior trust because bias/noise increase with horizon.

### Do not promote yet

- **Revision breadth as a standalone anomaly.** Breadth (for example, the fraction of analysts revising upward over a window) is intuitive and worth testing, but this pass did not find primary evidence strong enough to label it an established independent return predictor. Treat as a hypothesis until replicated under the v0.7 protocol.
- **Forecast staleness alone.** Recency matters for construction and sticky updating appears predictive, but simple age-of-forecast has not yet been shown here to be a standalone alpha signal.

## Key evidence

### 1. Timing around earnings announcements is asymmetric

Ivković and Jegadeesh (2004), *Journal of Financial Economics*, study one-quarter-ahead forecast revisions from January 1990 to March 2002. Revisions are least informative in the week after earnings announcements. The information content of upward forecast revisions rises sharply in the week before the next earnings announcement, while downward revisions do not show the same final-week increase.

Source: https://doi.org/10.1016/j.jfineco.2004.03.002

**Implication:** event time relative to earnings must be a feature. `revision_direction × days_to/from_EA` should be tested rather than using revision direction alone.

### 2. Responsiveness appears to reduce PEAD

Zhang (2008), *Journal of Accounting and Economics*, studies analyst responsiveness after quarterly earnings announcements over 1996–2002. Analysts are classified as responsive when the first next-quarter forecast revision arrives within two trading days. Firm-quarters with responsive analysts exhibit a larger event-window earnings response and lower subsequent post-earnings-announcement drift.

Source: https://doi.org/10.1016/j.jacceco.2008.04.004

**Implication:** revision speed can function as an **information-efficiency state variable**. Slow revision following a large earnings surprise may identify situations where more PEAD remains.

### 3. Analysts underreact to informative secondary signals

Clement, Hales, and Xue (2011), *Journal of Accounting and Economics*, show that after earnings announcements analysts respond to announcement-period stock returns and earlier analysts' revisions, but underreact on average. Analysts who respond more appropriately to signal informativeness are more accurate and influential.

Source: https://doi.org/10.1016/j.jacceco.2010.11.001

**Implication:** a useful event vector should measure `own_revision`, `prior_peer_revision`, `announcement_return`, and the degree of residual underreaction.

### 4. Modern evidence on analyst stickiness is especially important

Cao et al. (2026), *Review of Finance*, “Analyst stickiness and stock return predictability,” model analyst-level sticky updating. The paper reports that revisions by sticky analysts contain stronger return predictability than traditional consensus revisions, with stronger effects when a larger fraction of covering analysts are sticky and when forecasting difficulty is high.

Source: https://doi.org/10.1093/rof/rfag022

**Status caveat:** publication is current (June 2026), but this research note has not yet independently verified the exact sample-end date from the full paper. Keep publication date and sample-end date separate under the Four-Date Discipline.

**Implication:** “staleness” should be modeled behaviorally, not merely as forecast age. Candidate features include analyst-specific update persistence, distance from prior forecast, response to realized news, and historical responsiveness.

### 5. Deviation from consensus is informative

Loh and Stulz (2011), *Review of Financial Studies*, report that only about 12% of recommendation changes meet their definition of visibly influential. Influential changes are more likely when issued by leader/star/previously influential analysts, when moving away from consensus, when accompanied by earnings forecasts, and for firms with high forecast dispersion.

Source: https://doi.org/10.1093/rfs/hhq094

Jegadeesh and Kim (2010), *Review of Financial Studies*, find stronger price reactions when recommendation revisions move away from consensus, consistent with analyst herding reducing the informativeness of consensus-following revisions.

Source: https://doi.org/10.1093/rfs/hhp093

**Implication:** candidate features: analyst consensus distance before revision, revision direction relative to consensus, historical analyst influence, brokerage/resources, and forecast accompaniment.

### 6. Forecast dispersion is a conditional signal, not a clean standalone edge

Diether, Malloy, and Scherbina (2002), *Journal of Finance*, document lower future returns for firms with high analyst forecast dispersion, especially among small stocks and stocks with poor prior performance.

Source: https://doi.org/10.1111/0022-1082.00490

Daniel, Klos, and Rottke (2023), *Review of Financial Studies*, analyze disagreement dynamics. Their analyst-dispersion sample runs May 1980–June 2020, and their stock-lending sample runs August 2004–June 2020. Large disagreement shocks decay slowly, over roughly five years. In short-sale-constrained stocks, price-shock/disagreement combinations are associated with persistent negative abnormal returns.

Source: https://doi.org/10.1093/rfs/hhac075

**Implication:** test dispersion jointly with lending/short-sale proxies, prior returns, size, distress/credit state, and earnings-event timing. Do not treat `high_dispersion = short` as a universal rule.

### 7. Machine disagreement is a useful conceptual benchmark, but not analyst alpha

Bali et al. (2026), *Review of Financial Studies*, introduce machine forecast disagreement (MFD), a dispersion measure across ML return-forecast specifications. High disagreement predicts lower returns; the reported value-weighted high-minus-low disagreement spread is large, and the authors link it to short-sale costs and limits to arbitrage.

Source: https://doi.org/10.1093/rfs/hhag042

**Implication:** this is evidence that disagreement itself may be a state variable beyond analyst dispersion. It should motivate a future uncertainty/disagreement model, not be conflated with analyst consensus data.

### 8. Bellwether revisions can propagate to peers

Hameed, Morck, Shen, and Yeung (2015), *Review of Financial Studies*, identify highly followed “bellwether” firms whose fundamentals predict peer fundamentals. Analyst earnings forecast revisions for bellwether firms move prices of less-followed related firms, while the reverse effect is weaker.

Source: https://doi.org/10.1093/rfs/hhv042

**Implication:** future network feature: `bellwether_revision × peer_exposure × response_lag`.

### 9. Public disclosure changes analyst behavior

Tseng et al. (2023), *Review of Financial Studies*, use EDGAR adoption to show that easier public access to mandatory disclosures makes analyst earnings forecasts less optimistic and more accurate but also less price-informative; dispersion and boldness decline after EDGAR access improves.

Source: https://doi.org/10.1093/rfs/hhad008

**Implication:** analyst alpha should be conditioned on the quality/availability of public information. Filing-derived features and analyst revisions are complements in the model even if public disclosure reduces the analyst's standalone informational advantage.

### 10. Activation delays can create apparent information-processing delay

A 2018 *Journal of Financial Economics* paper on Thomson Reuters I/B/E/S activation delays finds that forecasts with longer unexpected database activation delays have muted announcement returns and larger post-announcement drift, concentrated in neglected stocks.

Source: https://doi.org/10.1016/j.jfineco.2017.11.005

**Implication:** vendor timestamps are not automatically equivalent to analyst-publication timestamps. Any analyst database must distinguish analyst issue time, vendor receipt/activation time, and researcher availability time.

## Candidate analyst event vector

For each analyst forecast event, eventually test:

- firm/security permanent ID
- analyst ID
- brokerage ID
- forecast horizon
- prior estimate
- revised estimate
- signed revision magnitude
- revision magnitude scaled by price / absolute consensus / forecast uncertainty
- event time relative to earnings announcement
- event time relative to management guidance / filing
- time since analyst's previous forecast
- time since last consensus change
- distance from pre-event consensus
- direction relative to consensus
- prior analyst forecast accuracy
- historical analyst responsiveness
- analyst stickiness estimate
- prior influence / price-impact history
- number of active covering analysts
- forecast dispersion level
- change in forecast dispersion
- fraction of recent analysts revising up/down (revision breadth — experimental)
- clustering intensity of revisions
- announcement-period stock return
- standardized earnings surprise
- revenue surprise
- management guidance revision
- sector/peer revision state
- bellwether revision exposure
- short-sale constraint / lending-cost state when available

## Required validation splits

The branch must be tested separately for:

- upward vs downward revisions
- pre-earnings vs immediate post-earnings vs mid-quarter revisions
- 1-quarter vs annual vs long-horizon forecasts
- large/liquid vs small/illiquid firms
- high vs low coverage
- high vs low dispersion
- responsive vs sticky analysts
- raw vs sector/industry-neutral performance
- long-only vs long/short economics
- original historical sample vs post-publication vs 2010+ vs 2020+ vs prospective period

## Data feasibility

This is an **A1/B commercial-data branch for rigorous historical testing**. Public EDGAR data cannot reproduce point-in-time analyst consensus histories. A0 can study management guidance, filings, earnings announcements, public price reaction, and prospective analyst events that are captured going forward, but it must not claim historical consensus alpha without legitimate PIT analyst data.

## Current priority ranking

| Component | Priority | Status |
|---|---:|---|
| Short-horizon EPS revision magnitude | Very High | Evidence-backed |
| Responsiveness / revision speed | Very High | Evidence-backed mechanism |
| Analyst stickiness | Very High | Modern 2026 evidence; sample-end verification pending |
| Consensus deviation / boldness | High | Evidence-backed |
| Analyst quality / influence | High | Evidence-backed |
| Disagreement × short constraints | High | Evidence-backed conditional state |
| Change in dispersion | High | Evidence-backed dynamics; direct alpha to test |
| Bellwether spillovers | High | Evidence-backed mechanism |
| Revision breadth | Medium-High | Hypothesis; not yet promoted |
| Simple forecast age/staleness | Medium | Diagnostic; not standalone yet |
| Recommendation level | Low-Medium | Control / context |
| Long-horizon growth forecasts | Low-Medium | Lower prior trust |

## Next research pass

1. Verify the exact sample periods and portfolio economics in the 2026 analyst-stickiness paper.
2. Search for direct evidence on revision breadth / clustering as a return predictor.
3. Examine positive-vs-negative revision asymmetry after Reg FD and in post-2010 samples.
4. Separate firm-specific revision information from industry/peer information.
5. Test whether analyst disagreement adds information after credit risk, volatility, short constraints, and options-implied uncertainty.
6. Identify legally/licensably accessible PIT analyst datasets and realistic costs for A1 research.
