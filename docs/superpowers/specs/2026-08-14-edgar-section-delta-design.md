# EDGAR Section Delta Engine Design

## Goal

Build the smallest deterministic A0 pipeline that converts accession-level 10-K/10-Q HTML into canonical filing sections and year-over-year delta features suitable for `EDGAR_DELTA_001`, while preserving Phase-0 v0.7 timestamp, lineage, and failure-state rules.

## Scope

### In scope

- 10-K / 10-K/A / 10-Q / 10-Q/A primary-document HTML.
- Deterministic extraction of canonical sections using visible-text item headings and bounded next-item markers.
- Text normalization that preserves numbers and economically meaningful punctuation while removing HTML/layout noise.
- Per-section extraction metadata: section id/name, markers, hashes, word count, confidence, explicit failure reason.
- Prior-comparable filing pairing supplied by caller; no hidden entity matching inside the delta engine.
- Transparent baseline deltas: word-count change, added/removed token fractions, Jaccard similarity, numeric-density change, paragraph additions/removals, sentence novelty, and simple finance-term-density changes.
- Pure-Python feature generation with deterministic outputs.
- Tests using synthetic SEC-like HTML fixtures first; real SEC smoke-test fixture second.

### Out of scope

- LLM or embedding features.
- Universal SEC document understanding.
- 8-K economic classification.
- Full footnote taxonomy reconstruction.
- Price labels, portfolio construction, or backtesting.
- Automatic same-company prior-filing discovery beyond a small explicit comparator interface.

## Architecture

### `sections.py`

Owns canonical section definitions, HTML-to-visible-text conversion, heading detection, bounded extraction, normalization, and extraction confidence/failure states.

Public interface:

```python
@dataclass(frozen=True)
class ExtractedSection:
    section_id: str
    section_name: str
    start_marker: str | None
    end_marker: str | None
    raw_text: str
    normalized_text: str
    raw_text_sha256: str
    normalized_text_sha256: str
    word_count: int
    extraction_confidence: float
    extraction_failure_reason: str | None


def extract_sections(html: str, form: str) -> dict[str, ExtractedSection]: ...
```

### `delta.py`

Owns deterministic comparison of two already-extracted comparable sections.

Public interface:

```python
@dataclass(frozen=True)
class SectionDelta:
    section_id: str
    word_count_change: float
    added_token_fraction: float
    removed_token_fraction: float
    jaccard_similarity: float
    sentence_novelty_rate: float
    added_paragraphs: int
    removed_paragraphs: int
    numeric_density_change: float
    finance_term_density_change: float
    prior_comparable_flag: bool


def compute_section_delta(current: ExtractedSection, prior: ExtractedSection | None) -> SectionDelta: ...
```

## Section coverage

### 10-K family

- `item_1_business`
- `item_1a_risk_factors`
- `item_2_properties`
- `item_3_legal_proceedings`
- `item_7_mda`
- `item_7a_market_risk`

### 10-Q family

- `part_i_item_2_mda`
- `part_i_item_3_market_risk`
- `part_ii_item_1_legal_proceedings`
- `part_ii_item_1a_risk_factors`

Footnotes remain deferred until these sections meet coverage/QA targets.

## Extraction rules

1. Parse HTML with BeautifulSoup.
2. Remove script/style/noscript content and hidden layout noise where safely identifiable.
3. Convert to visible text with line boundaries preserved.
4. Normalize Unicode whitespace and item-heading punctuation.
5. Heading detection is case-insensitive and tolerant of variants such as `ITEM 1A.`, `Item 1A —`, and `PART I ITEM 2`.
6. For each section, choose the first plausible heading that has a valid later boundary and exceeds a minimum content length.
7. End at the earliest valid next canonical item heading for that form.
8. Never silently substitute a different section. Missing/ambiguous extraction returns an explicit failure state.
9. Repeated table-of-contents headings are rejected by minimum-content and boundary plausibility checks; if ambiguity remains, mark failure rather than guessing.

## Normalization

- HTML entities decoded.
- Repeated whitespace collapsed.
- Hyphenated line-wrap artifacts joined conservatively.
- Numbers retained.
- Text lower-cased for comparison features only; stored normalized text remains human-readable casing-neutral output.
- Empty lines collapsed but paragraph boundaries retained as `\n\n`.

## Confidence

Deterministic score in `[0, 1]` based on:

- exactness of start heading match,
- valid canonical end marker,
- minimum content length,
- absence of competing plausible start markers.

Confidence is diagnostic only; low-confidence sections remain explicit and are not auto-promoted.

## Delta semantics

- Token operations use normalized lowercase alphanumeric tokens.
- Added/removed fractions are set-based proportions relative to current/prior unique-token counts respectively.
- Jaccard uses unique-token sets.
- Sentence novelty is fraction of current sentences not matched exactly after normalization to a prior sentence.
- Paragraph additions/removals use normalized paragraph multiset counts.
- Numeric density is numeric tokens / total tokens.
- Finance-term density uses a small frozen baseline dictionary (`uncertainty`, `risk`, `material`, `litigation`, `liquidity`, `impairment`, `default`, `covenant`, `restructuring`, `investigation`) and is versioned in code.
- If no prior comparable section exists, `prior_comparable_flag=False`; numeric deltas become `NaN` rather than zero.

## Error handling

- Unsupported form raises `ValueError`.
- Malformed/empty HTML returns section records with explicit failure reasons where possible rather than fabricated text.
- Hashes are SHA-256 over UTF-8 encoded exact strings used by the stage.
- No exception path may convert missing sections into empty successful sections.

## Testing

1. Synthetic 10-K with duplicate TOC headings proves TOC rejection and correct body extraction.
2. Heading punctuation/case variants extract correctly.
3. Missing end marker produces explicit failure.
4. 10-Q Part I / Part II sections remain disambiguated.
5. Normalization is deterministic and preserves numbers.
6. Delta metrics match hand-calculated examples.
7. Missing prior section produces `prior_comparable_flag=False` and NaN deltas.
8. Real SEC smoke fixture is stored as a small immutable excerpt, not fetched during unit tests.

## Success criteria

- All deterministic unit tests pass.
- No network call is required for unit tests.
- Same input yields byte-identical normalized text and feature values.
- Missing/ambiguous sections are reported, never guessed.
- The implementation is sufficient to produce section/delta records for `EDGAR_DELTA_001` without introducing embeddings, labels, or execution logic.
