import pytest

from equities_lab.edgar.sections import compute_section_delta, extract_sections


TEN_K_WITH_TOC = b'''<html><body>
<h2>Table of Contents</h2>
<p>Item 1A. Risk Factors</p>
<p>Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations</p>
<hr/>
<h1>ITEM 1A. RISK FACTORS</h1>
<p>Our business depends on a small number of suppliers. Semiconductor shortages could delay production.</p>
<p>Cybersecurity incidents could interrupt operations and expose confidential information.</p>
<h1>ITEM 1B. UNRESOLVED STAFF COMMENTS</h1><p>None.</p>
<h1>ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS</h1>
<p>Revenue increased because unit volume and average selling prices increased.</p>
<p>Operating margin declined because logistics and warranty costs increased.</p>
<h1>ITEM 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK</h1>
<p>Interest-rate risk was not material.</p>
</body></html>'''

TEN_Q = b'''<html><body>
<h1>PART I</h1>
<h2>Item 2. Management's Discussion and Analysis of Financial Condition and Results of Operations</h2>
<p>Quarterly revenue increased by ten percent from stronger demand.</p>
<h2>Item 3. Quantitative and Qualitative Disclosures About Market Risk</h2>
<p>Market risk disclosure.</p>
<h1>PART II</h1>
<h2>Item 1A. Risk Factors</h2>
<p>Supply constraints remain a material risk and new export restrictions may reduce sales.</p>
<h2>Item 2. Unregistered Sales of Equity Securities and Use of Proceeds</h2>
<p>None.</p>
</body></html>'''


def test_extract_10k_prefers_real_section_over_table_of_contents() -> None:
    sections = extract_sections(TEN_K_WITH_TOC, form="10-K")
    assert "small number of suppliers" in sections["item_1a_risk_factors"]
    assert "Table of Contents" not in sections["item_1a_risk_factors"]
    assert "Revenue increased" in sections["item_7_mda"]


def test_extract_10q_gets_mda_and_part_ii_risk_factors() -> None:
    sections = extract_sections(TEN_Q, form="10-Q")
    assert "Quarterly revenue increased" in sections["item_2_mda"]
    assert "new export restrictions" in sections["part_ii_item_1a_risk_factors"]


def test_compute_section_delta_detects_novel_language() -> None:
    prior = "Demand was stable. Supply constraints were manageable."
    current = "Demand was stable. Supply constraints worsened. Export restrictions may reduce sales."
    delta = compute_section_delta(prior, current)
    assert delta.current_word_count > delta.prior_word_count
    assert 0.0 <= delta.token_jaccard < 1.0
    assert delta.added_token_ratio > 0.0
    assert delta.changed is True


def test_compute_section_delta_handles_identical_text() -> None:
    delta = compute_section_delta("Same disclosure.", "Same disclosure.")
    assert delta.token_jaccard == pytest.approx(1.0)
    assert delta.added_token_ratio == pytest.approx(0.0)
    assert delta.removed_token_ratio == pytest.approx(0.0)
    assert delta.changed is False
