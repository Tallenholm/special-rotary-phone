# EDGAR Filings Deep Dive 02 — First Backtest and A0 Ingestion Spec

**Status:** Ready for implementation planning  
**Cutoff:** August 14, 2026  
**Phase-0 framework:** v0.7 — Feasibility Closed

## Decision

The first EDGAR experiment should **not** be generic filing sentiment and should **not** combine all 8-Ks into one label. The minimum credible A0 test is a section-delta study using 10-K / 10-Q text, with 8-K item families treated as separate event modules.

## Why section deltas come first

The evidence consistently says that *change* in disclosure carries more information than raw length, readability, or sentiment alone.

- Brown & Tucker (2011), Journal of Accounting Research: larger year-over-year MD&A modification is associated with larger stock-price reaction to 10-K filings; MD&A modification also tracks underlying economic change.
- Amel-Zadeh & Faasse (2016 working paper): changes in MD&A and footnote text predict future returns, volatility, and operating performance, with slower investor incorporation for footnotes than MD&A.
- Gan & Qiu (2021), International Review of Finance: increases in 10-K file size negatively predict future returns, but the effect is not simply Item 1A risk-factor word growth; disclosure change must be interpreted carefully.
- Brown et al. (2017), Journal of Accounting & Economics: 10-Ks have become longer, more boilerplate-heavy, stickier, and less specific/readable over time, so raw document length is a poor standalone signal.
- Kravet & Muslu (2013), Review of Accounting Studies: increases in textual risk disclosure are associated with higher volatility, trading volume, and analyst disagreement around filings.
- Lyle, Riedl & Siano (forthcoming Accounting Review): additions/removals of individual risk factors alter market uncertainty as measured by variance risk premia.

## First experiment: `EDGAR_DELTA_001`

### Research question

Do **year-over-year changes in economically important 10-K sections** predict subsequent abnormal returns or post-filing information-processing outcomes after controlling for simple filing size, fundamentals, prior returns, size, and sector?

### Track

**A0 Public / Prospective for data construction.**  
Historical return claims remain exploratory unless the price/security-master history satisfies v0.7 inactive/delisted/corporate-action requirements.

### Filing universe

- Domestic U.S. operating companies filing 10-K / 10-K/A.
- Exclude funds, SPAC shells where the section structure is not comparable, and issuers without a valid same-company prior-year 10-K.
- Keep amendments separately; never overwrite the original filing.
- Initial implementation should prefer liquid exchange-listed common stocks for practicality, but universe construction must remain point-in-time.

### Prediction timestamp

Use a **conservative public-availability timestamp** rather than the acceptance timestamp itself.

SEC guidance states filings are often available on sec.gov within roughly 1–3 minutes after EDGAR acceptance and that there is no exact timestamp for first public availability. Therefore:

- base rule: `tradable_time = acceptance_datetime + 5 minutes`;
- if that falls outside regular market hours, earliest regular-session trade is the next market open;
- sensitivity: +3 min, +10 min, next-open-only.

No same-close trade is allowed if the filing became usable after the decision timestamp.

### Sections for v1

Parse only high-value sections:

1. Item 1 — Business
2. Item 1A — Risk Factors
3. Item 2 — Properties (diagnostic only initially)
4. Item 3 — Legal Proceedings
5. Item 7 — MD&A
6. Item 7A — Market Risk
7. Financial-statement footnotes / notes section where robustly extractable

Do **not** build universal document understanding before these sections work reliably.

### Baseline delta features

For each section versus the prior comparable annual filing:

- normalized word-count change
- added-token fraction
- removed-token fraction
- Jaccard similarity
- cosine similarity on TF-IDF vectors
- sentence-level novelty rate
- boilerplate/stickiness score
- number of newly added paragraphs
- number of removed paragraphs
- change in financial-term density
- change in uncertainty/risk/legal terms using a finance-specific dictionary
- numeric density change
- section-presence / missingness flags

Keep embeddings / LLM features **out of the first baseline**. They can enter only after transparent features establish a benchmark.

### Primary targets

Test several horizons without tuning one after seeing results:

- filing reaction: next tradable session abnormal return
- 5 trading-day abnormal return
- 20 trading-day abnormal return
- 60 trading-day abnormal return
- post-filing realized volatility
- abnormal volume

Primary economic target for the first generation: **20-trading-day sector-relative return**.

### Required controls

- prior 1m / 6m / 12m returns
- size / market cap
- book-to-market or simple valuation control where PIT-clean
- profitability / investment baseline where PIT-clean
- filing size
- prior-year section size
- filing delay / seasonality
- sector or SEC SIC contemporaneous control
- liquidity / price screen
- contemporaneous earnings-event overlap flag

### Models

1. no-skill / equal-weight
2. univariate delta sorts
3. OLS / ridge
4. elastic net
5. gradient boosting only after linear baselines

No transformer or LLM forecasting model in Generation 1.

### Validation

Follow v0.7 exactly:

- chronological development splits
- purging/embargo where labels overlap
- all tried variants logged
- one sealed chronological generation test
- post-publication / 2010+ / 2020+ splits reported separately
- raw and sector/size/beta-adjusted diagnostics
- long-only and long-short economics separated
- realistic spread/slippage scenarios

## 8-K architecture — separate event modules

Do not treat `form == 8-K` as a signal. Classify by disclosed items.

### Priority A — immediate event modules

- **2.02 Results of Operations and Financial Condition** — earnings / operating updates; usually paired with Exhibit 99.1.
- **4.02 Non-Reliance on Previously Issued Financial Statements** — accounting/restatement risk; deserves a dedicated negative-event module.
- **1.01 Entry into Material Definitive Agreement** — contract / financing / strategic transaction module.
- **2.01 Completion of Acquisition or Disposition of Assets** — M&A / asset-sale module.
- **2.03 Creation of Direct Financial Obligation** — debt / financing module.
- **5.02 Director / Officer Changes and Compensation Arrangements** — governance / management-change module.

### Priority B — contextual / heterogeneous

- **7.01 Regulation FD Disclosure** — highly heterogeneous; classify Exhibit 99.1 content before modeling.
- **8.01 Other Events** — catch-all; requires content classification before any sign is assigned.
- **3.02 Unregistered Sales of Equity Securities** — financing/dilution module.
- **2.05 Exit or Disposal Activities** — restructuring/cost-cutting module.

### Lower initial priority

- 5.07 shareholder-vote outcomes
- routine bylaw amendments
- administrative exhibits without material event content

### 8-K rule

The **item code is metadata, not the label**. Item 7.01 or 8.01 can contain investor presentations, litigation developments, financing updates, product milestones, guidance, or other unrelated events. The event classifier must read the filing and relevant exhibits before assigning an economic category.

## Exact A0 EDGAR ingestion schema

### Filing table

- `cik`
- `accession_no`
- `form`
- `filing_date`
- `report_date`
- `acceptance_datetime`
- `conservative_public_datetime`
- `amendment_flag`
- `primary_document`
- `items[]`
- `sic_as_filed`
- `ticker_at_ingest`
- `exchange_at_ingest`
- `source_url`
- `raw_submission_sha256`
- `ingested_at`

### Document table

- `accession_no`
- `sequence`
- `document_name`
- `document_type`
- `description`
- `size_bytes`
- `raw_sha256`
- `text_sha256`
- `mime_type`
- `is_primary`
- `is_exhibit`
- `exhibit_type`

### Section table

- `accession_no`
- `section_id`
- `section_name`
- `extractor_version`
- `start_marker`
- `end_marker`
- `raw_text_sha256`
- `normalized_text_sha256`
- `word_count`
- `extraction_confidence`
- `extraction_failure_reason`

### Delta table

- `current_accession`
- `prior_accession`
- `section_id`
- all baseline delta features
- `prior_comparable_flag`
- `days_between_filings`
- `delta_feature_version`

## SEC acquisition rules

Use the SEC's official data sources:

- `data.sec.gov/submissions/CIK##########.json` for company filing history and metadata;
- EDGAR filing archive pages / complete submission text for exact accession contents and acceptance timestamp;
- accession-level original HTML / iXBRL for the historical source of truth;
- CompanyFacts / Frames only for discovery/QA, not as the PIT historical source of truth for backtests.

Operational requirements from SEC guidance:

- declare a descriptive User-Agent with contact information;
- remain below the current SEC maximum of 10 requests/second;
- cache immutable filing payloads locally;
- use bulk archives where appropriate rather than repeatedly crawling the same documents.

## Why 8-Ks are worth a separate branch

Prior literature finds 8-K items are associated with abnormal volume and return volatility, and some item categories exhibit post-filing drift. Other work shows 8-K filing frequency itself captures information intensity and relates to future return/volatility differences. This supports **event-family-specific research**, not a generic 8-K polarity score.

## Promotion gate for EDGAR_DELTA_001

Promote only if:

1. at least one predeclared delta feature or simple linear combination adds OOS information beyond filing size + prior returns + size/sector controls;
2. the effect survives 2010+ and 2020+ splits;
3. it is not microcap-only;
4. it survives realistic transaction-cost assumptions;
5. section extraction coverage and failure rates are reported and acceptable;
6. no result depends on acceptance-time leakage;
7. a sealed generation test confirms the development result.

Otherwise move the exact tested variant to the Edge Graveyard.

## Sources

- SEC EDGAR APIs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- SEC Accessing EDGAR Data / Fair Access: https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data
- SEC Webmaster FAQ / timestamps: https://www.sec.gov/about/webmaster-frequently-asked-questions
- Brown, S.V. & Tucker, J.W. (2011), *Journal of Accounting Research*, “Large-Sample Evidence on Firms’ Year-over-Year MD&A Modifications.” DOI: 10.1111/j.1475-679X.2010.00396.x
- Brown et al. (2017), *Journal of Accounting and Economics*, “The evolution of 10-K textual disclosure: Evidence from Latent Dirichlet Allocation.” DOI: 10.1016/j.jacceco.2017.07.002
- Kravet, T. & Muslu, V. (2013), *Review of Accounting Studies*, “Textual Risk Disclosures and Investors’ Risk Perceptions.”
- Gan, Q. & Qiu, B. (2021), *International Review of Finance*, “The information content of 10-K file size change.” DOI: 10.1111/irfi.12324
- Lerman, A. & Livnat, J. (2010), *Review of Accounting Studies*, “The New Form 8-K Disclosures.”
- Zhao, X. (2017), *Management Science*, “Does Information Intensity Matter for Stock Returns? Evidence from Form 8-K Filings.” DOI: 10.1287/mnsc.2015.2408
