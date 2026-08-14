# EDGAR Filings Deep Dive 01 — Free-Core Event Alpha

**Status:** Active research branch  
**Cutoff:** August 14, 2026  
**Phase-0 framework:** v0.7 — Feasibility Closed

## Research question

Which company-reported SEC filing signals can be extracted from free EDGAR data with point-in-time rigor and plausibly add return-predictive information beyond headline earnings?

## Current verdict

EDGAR remains the strongest **free-core** research branch because filings provide discrete timestamps, rich structured and unstructured information, and a mechanism for slow information diffusion. But the likely edge is not “negative words = short.” The promising objects are **changes in disclosures, hidden/under-attended information, filing-derived uncertainty, and event-specific content**.

## Highest-priority hypotheses

### 1. Filing changes / deltas — VERY HIGH

Compare each 10-K/10-Q to prior filings and extract meaningful changes in:
- risk factors;
- MD&A;
- liquidity/capital resources;
- customer/supplier concentration;
- debt/covenants;
- capex/investment;
- inventory/receivables;
- litigation;
- cybersecurity;
- geographic exposure;
- segment structure;
- going-concern language;
- management uncertainty/tone.

**Reason:** longitudinal change is more informative than absolute document style and helps separate new information from persistent boilerplate.

### 2. Under-attended filing content — VERY HIGH

Long, complex filings can contain information that investors and analysts do not immediately process. Recent RFS evidence on merger filings shows that investor inattention to peer-selection information in deal documents can be followed by slow return adjustment over months.

**Implication:** build extraction around economically specific disclosures rather than whole-document sentiment alone.

### 3. Filing uncertainty as a conditioning state — HIGH

Recent evidence finds that uncertainty language in 10-K/Q filings affects how strongly investors react to subsequent earnings news: more filing uncertainty is associated with stronger immediate responses and weaker subsequent PEAD.

**Implication:** uncertainty may be more useful as an **information-processing state variable** than as a direct directional signal.

### 4. Event-specific 8-K items — HIGH

8-Ks are discrete, timestamped event filings. Candidate items include:
- material agreements;
- debt/financing;
- acquisitions/dispositions;
- impairments;
- delisting notices;
- auditor changes;
- executive departures;
- restructuring;
- cyber incidents;
- earnings/guidance attachments.

**Implication:** item-specific models are preferable to one generic 8-K classifier.

### 5. Simple domain-specific text models — HIGH

A 2026 *Journal of Financial Markets* paper reports that an elastic-net model over 10-K n-grams produced a return-predictive text factor and outperformed more complex NLP/LLM alternatives in that study.

**Implication:** the model ladder must start with transparent bag-of-words/n-gram baselines before LLM features.

## Evidence notes

### EDGAR materially changed disclosure access

Modern RFS evidence on the staggered EDGAR rollout shows that universal electronic access changed analyst behavior and improved investors' ability to use mandatory disclosures. The same paper summarizes post-EDGAR research finding measurable market reactions on 10-K/10-Q filing days.

Source: https://doi.org/10.1093/rfs/hhad008

### 10-K text evolves and contains substantial boilerplate

A 2017 *Journal of Accounting and Economics* study of 10-Ks from 1996–2013 documents increasing length, boilerplate, stickiness, and redundancy, with declining specificity/readability/hard-information share. Much of the increase is tied to fair-value, internal-control, and risk-factor disclosure requirements.

Source: https://doi.org/10.1016/j.jacceco.2017.07.002

**Implication:** raw document length or generic complexity can be regulation-driven. Delta features must distinguish required disclosure expansion from firm-specific information.

### Uncertainty language can change later earnings processing

A 2025 *Journal of Banking & Finance* paper finds that more uncertain 10-K/Q text is associated with stronger immediate reaction to subsequent earnings surprises and weaker later drift, alongside more sophisticated-investor attention.

Source: https://doi.org/10.1016/j.jbankfin.2025.107580

**Implication:** filing text can forecast the **speed of information incorporation**, not just return direction.

### Complex merger filings can contain ignored peer information

A 2023 RFS study finds that peer firms disclosed in M&A valuation analyses receive little immediate attention, yet peer identification is associated with later takeover probability, operating outcomes, and persistent return differences. The authors interpret this as valuable information in complex merger filings being gradually incorporated.

Source: https://doi.org/10.1093/rfs/hhad002

**Implication:** targeted extraction from merger/proxy filings is a strong future niche branch.

### Speculative disclosure language may contain positive private-information cues

A 2025 *Review of Corporate Finance Studies* article reports that greater use of speculative statements in 10-Ks predicts higher nonreverting abnormal returns over the following 16 weeks in its sample, with supporting insider/informed-buying and news-sentiment evidence.

Source: https://doi.org/10.1093/rcfs/cfaf021

**Status:** newer result; high-priority replication candidate, not accepted alpha.

### Simple structured text can beat more complex models

A 2026 *Journal of Financial Markets* study uses elastic-net regression on 10-K n-grams to create a return-predictive dictionary and reports that simple regressions outperform prominent financial dictionaries, off-the-shelf LLMs, and more complex ML alternatives in its tests.

Source: https://doi.org/10.1016/j.finmar.2026.101070

**Implication:** do not begin the EDGAR branch with a giant transformer.

## First free-core feature families

### Structured filing metadata

- form type;
- filing acceptance time;
- amendment flag;
- filing delay relative to fiscal period end;
- filing time of day / after-hours status;
- document count / exhibit count;
- 8-K item codes;
- exhibit types;
- filing length change;
- amendment frequency.

### Longitudinal text change

- section-level cosine/Jaccard change;
- added/deleted risk-factor topics;
- new named entities;
- new litigation/cyber/debt/customer/supplier mentions;
- sentence additions/removals;
- section-specific sentiment/uncertainty change;
- boilerplate-adjusted novelty;
- semantic distance from prior filing.

### Financial-statement change

Using the v0.7 lean XBRL layer:
- revenue growth;
- gross margin change;
- operating margin change;
- operating cash flow change;
- capex change;
- receivables/inventory growth;
- cash/debt changes;
- R&D/SBC changes where available;
- accrual/working-capital proxies.

### Event-specific 8-K features

Separate models by item/event family. Preserve:
- event category;
- disclosed effective date;
- acceptance timestamp;
- linked exhibits;
- whether event preceded/followed earnings;
- whether price already moved before filing;
- textual novelty vs company history.

## Minimum first EDGAR experiment

### Target

Test whether **filing novelty/change** predicts 5-, 20-, and 60-trading-day relative returns after the filing is publicly available.

### Universe

- U.S. common stocks;
- research-grade price history for historical validation when available;
- A0 prospective path allowed with public price feeds;
- exclude microcaps in primary results and report separately.

### Signal v1

For 10-K/10-Q:

1. split document into stable sections;
2. compare each section with the prior same-form filing;
3. compute transparent lexical/semantic change metrics;
4. isolate added/deleted economically relevant terms/topics;
5. combine with lean structured financial deltas;
6. do **not** use an LLM-generated scalar score as the primary baseline.

### Baselines

1. earnings surprise / recent earnings reaction;
2. momentum;
3. raw document length;
4. raw negative-tone score;
5. simple section-change metrics.

Any LLM feature must beat these.

### Timing

Use a conservative availability timestamp based on EDGAR acceptance plus explicit lag sensitivity. If the filing arrives after regular-hours close, earliest regular-session execution is next trading day unless a specific after-hours execution profile is being tested.

### Required controls

- same-day earnings announcement;
- guidance release;
- M&A event;
- financing event;
- sector/industry;
- size/liquidity;
- prior return;
- filing-time-of-day;
- amendment status;
- document length;
- year/regulatory regime.

## Promotion hierarchy

### Tier 1
- section-level filing deltas;
- lean XBRL financial changes;
- filing uncertainty as a conditioning state;
- event-specific 8-K classification.

### Tier 2
- speculative-language measures;
- entity/topic novelty;
- merger/proxy peer extraction;
- risk-factor additions/deletions;
- filing-time/attention interactions.

### Tier 3
- whole-document sentiment;
- readability;
- document length;
- generic embedding scores.

## Key warning

The EDGAR branch must distinguish **new information in the filing** from information already released in earnings press releases, guidance, or earlier corporate events. A filing-day return is not automatically caused by the filing.

## Next pass

1. identify the best section-diff literature and exact modern sample periods;
2. map 8-K item families to economically distinct event hypotheses;
3. define the exact A0 EDGAR ingestion schema and conservative availability clock;
4. choose the first 10-K/10-Q delta baseline that can be implemented without a universal XBRL/text platform;
5. test whether newer speculative/uncertainty language measures survive simpler novelty and tone controls.
