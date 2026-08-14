# EDGAR Section Delta Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build deterministic 10-K/10-Q section extraction and transparent year-over-year delta features for `EDGAR_DELTA_001`.

**Architecture:** Add a focused `sections.py` parser that emits explicit extraction records, then a pure `delta.py` comparator that computes transparent baseline features. Keep network acquisition, price labels, embeddings, and 8-K classification outside this slice.

**Tech Stack:** Python 3.11+, BeautifulSoup 4, stdlib `re`, `hashlib`, `collections`, `math`, pytest.

## Global Constraints

- Work only on branch `feature/edgar-section-deltas`.
- Preserve Phase-0 v0.7 explicit failure states; never fabricate missing sections.
- No LLM, embedding, market-data, or backtest dependencies.
- Unit tests require no network.
- Deterministic inputs must produce deterministic hashes/features.

---

### Task 1: Canonical section extraction

**Files:**
- Create: `tests/test_edgar_sections.py`
- Create: `src/equities_lab/edgar/sections.py`

**Interfaces:**
- Produces: `ExtractedSection`, `extract_sections(html: str, form: str) -> dict[str, ExtractedSection]`.

- [ ] **Step 1: Write failing tests** covering duplicate TOC headings, heading punctuation/case variants, 10-Q Part I/II disambiguation, missing boundary failure, deterministic hashes, and numeric preservation.
- [ ] **Step 2: Run `pytest tests/test_edgar_sections.py -v` and verify RED** because `equities_lab.edgar.sections` does not exist.
- [ ] **Step 3: Implement minimal parser** with canonical form-specific section specs, BeautifulSoup visible text, heading regexes, bounded candidate selection, normalization, SHA-256 hashes, word count, confidence, and explicit failure reasons.
- [ ] **Step 4: Run `pytest tests/test_edgar_sections.py -v` and verify GREEN.**
- [ ] **Step 5: Run full `pytest -q`.**

### Task 2: Transparent delta features

**Files:**
- Create: `tests/test_edgar_delta.py`
- Create: `src/equities_lab/edgar/delta.py`

**Interfaces:**
- Consumes: `ExtractedSection` from Task 1.
- Produces: `SectionDelta`, `compute_section_delta(current, prior) -> SectionDelta`.

- [ ] **Step 1: Write failing tests** with hand-calculated word-count change, added/removed fractions, Jaccard, sentence novelty, paragraph multiset additions/removals, numeric-density change, finance-term-density change, and missing-prior NaNs.
- [ ] **Step 2: Run `pytest tests/test_edgar_delta.py -v` and verify RED** because `equities_lab.edgar.delta` does not exist.
- [ ] **Step 3: Implement minimal deterministic feature functions** using normalized text only and a frozen finance-term dictionary.
- [ ] **Step 4: Run `pytest tests/test_edgar_delta.py -v` and verify GREEN.**
- [ ] **Step 5: Run full `pytest -q`.**

### Task 3: Realistic SEC-like smoke fixture and integration QA

**Files:**
- Create: `tests/fixtures/sec_like_10k_excerpt.html`
- Create: `tests/test_edgar_section_delta_integration.py`
- Modify only if needed: `src/equities_lab/edgar/sections.py`, `src/equities_lab/edgar/delta.py`

**Interfaces:**
- Exercises `extract_sections` then `compute_section_delta` without network.

- [ ] **Step 1: Add a small immutable SEC-like HTML excerpt** containing a TOC, body Item 1A, Item 2, Item 7, Item 7A, tables, numbers, and realistic markup noise.
- [ ] **Step 2: Write failing integration test** that extracts body sections, verifies non-TOC content/hashes, and computes a delta against a modified prior excerpt.
- [ ] **Step 3: Run integration test and verify RED for the expected parser gap if any; otherwise strengthen the fixture/test until it proves a real integration behavior not already covered.**
- [ ] **Step 4: Make the minimal production adjustment required by the failing integration test.**
- [ ] **Step 5: Run `pytest -q` and require all tests green.**

### Completion verification

- [ ] `pytest -q` passes with zero failures.
- [ ] New public functions are covered by tests.
- [ ] Missing/ambiguous extraction remains explicit.
- [ ] No network dependency in tests.
- [ ] Compare branch against `main` and confirm changes are limited to the spec/plan, parser/delta code, tests, and fixtures.
