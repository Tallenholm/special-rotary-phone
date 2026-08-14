import hashlib

import pytest

from equities_lab.edgar.sections import extract_section_records


def test_10k_rejects_toc_duplicate_and_extracts_body_item_1a():
    html = """
    <html><body>
      <div>TABLE OF CONTENTS</div>
      <div>Item 1. Business</div>
      <div>Item 1A. Risk Factors</div>
      <div>Item 2. Properties</div>
      <hr/>
      <h2>ITEM 1. BUSINESS</h2>
      <p>We operate a substantial industrial business with customers nationwide.</p>
      <h2>Item 1A — Risk Factors</h2>
      <p>Cybersecurity incidents could materially disrupt our operations and liquidity.</p>
      <p>Commodity prices and customer concentration may also create material risk.</p>
      <h2>ITEM 2. PROPERTIES</h2>
      <p>We own twelve facilities.</p>
      <h2>ITEM 3. LEGAL PROCEEDINGS</h2>
      <p>Routine proceedings only.</p>
      <h2>ITEM 4. MINE SAFETY DISCLOSURES</h2>
      <p>Not applicable.</p>
    </body></html>
    """

    result = extract_section_records(html, "10-K")
    section = result["item_1a_risk_factors"]

    assert section.extraction_failure_reason is None
    assert "Cybersecurity incidents" in section.raw_text
    assert "TABLE OF CONTENTS" not in section.raw_text
    assert section.end_marker.lower().startswith("item 2")
    assert section.word_count > 10


def test_10k_accepts_heading_punctuation_and_case_variants():
    html = """
    <html><body>
      <h2>item 7 — management’s discussion and analysis</h2>
      <p>Revenue increased 17 percent to 420 million dollars due to stronger demand.</p>
      <p>Liquidity remained adequate despite higher working capital.</p>
      <h2>ITEM 7A: QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK</h2>
      <p>Interest-rate exposure is monitored daily.</p>
      <h2>Item 8. Financial Statements and Supplementary Data</h2>
      <p>Financial statements follow.</p>
    </body></html>
    """

    result = extract_section_records(html, "10-k")
    mda = result["item_7_mda"]
    market = result["item_7a_market_risk"]

    assert mda.extraction_failure_reason is None
    assert "Revenue increased 17 percent" in mda.raw_text
    assert market.extraction_failure_reason is None
    assert "Interest-rate exposure" in market.raw_text
    assert "420" in mda.normalized_text


def test_missing_end_marker_is_explicit_failure():
    html = """
    <html><body>
      <h2>Item 7. Management's Discussion and Analysis</h2>
      <p>This section has content but the filing excerpt ends before Item 7A or Item 8.</p>
    </body></html>
    """

    result = extract_section_records(html, "10-K")
    section = result["item_7_mda"]

    assert section.extraction_failure_reason == "missing_end_marker"
    assert section.normalized_text == ""
    assert section.word_count == 0


def test_10q_disambiguates_part_i_and_part_ii_items():
    html = """
    <html><body>
      <div>PART I</div><div>Item 2</div><div>Item 3</div><div>PART II</div><div>Item 1</div><div>Item 1A</div>
      <h1>PART I — FINANCIAL INFORMATION</h1>
      <h2>Item 1. Financial Statements</h2><p>Statements.</p>
      <h2>ITEM 2. Management's Discussion and Analysis</h2>
      <p>Quarterly revenue rose 9 percent and operating cash flow improved.</p>
      <h2>Item 3. Quantitative and Qualitative Disclosures About Market Risk</h2>
      <p>Foreign exchange exposure increased.</p>
      <h2>Item 4. Controls and Procedures</h2><p>Controls.</p>
      <h1>PART II — OTHER INFORMATION</h1>
      <h2>Item 1. Legal Proceedings</h2>
      <p>A patent litigation matter remains pending.</p>
      <h2>Item 1A. Risk Factors</h2>
      <p>Supply-chain disruption and cybersecurity remain material risks.</p>
      <h2>Item 2. Unregistered Sales of Equity Securities and Use of Proceeds</h2><p>None.</p>
    </body></html>
    """

    result = extract_section_records(html, "10-Q")

    assert "Quarterly revenue rose" in result["part_i_item_2_mda"].raw_text
    assert "Foreign exchange exposure" in result["part_i_item_3_market_risk"].raw_text
    assert "patent litigation" in result["part_ii_item_1_legal_proceedings"].raw_text
    assert "Supply-chain disruption" in result["part_ii_item_1a_risk_factors"].raw_text


def test_hashes_are_deterministic_and_match_text():
    html = """
    <html><body>
      <h2>Item 3. Legal Proceedings</h2>
      <p>We face litigation involving 3 counterparties and $25 million.</p>
      <h2>Item 4. Mine Safety Disclosures</h2><p>None.</p>
    </body></html>
    """

    first = extract_section_records(html, "10-K")["item_3_legal_proceedings"]
    second = extract_section_records(html, "10-K")["item_3_legal_proceedings"]

    assert first == second
    assert first.raw_text_sha256 == hashlib.sha256(first.raw_text.encode("utf-8")).hexdigest()
    assert first.normalized_text_sha256 == hashlib.sha256(first.normalized_text.encode("utf-8")).hexdigest()
    assert "25" in first.normalized_text


def test_unsupported_form_rejected():
    with pytest.raises(ValueError):
        extract_section_records("<html></html>", "8-K")
