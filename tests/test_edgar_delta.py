import math

import pytest

from equities_lab.edgar.delta import FINANCE_TERMS, compute_section_delta
from equities_lab.edgar.sections import ExtractedSection


def make_section(section_id: str, text: str) -> ExtractedSection:
    import hashlib

    normalized = text
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return ExtractedSection(
        section_id=section_id,
        section_name=section_id,
        start_marker="Item X",
        end_marker="Item Y",
        raw_text=text,
        normalized_text=normalized,
        raw_text_sha256=h,
        normalized_text_sha256=h,
        word_count=len(text.split()),
        extraction_confidence=1.0,
        extraction_failure_reason=None,
    )


def test_delta_metrics_match_hand_calculated_example():
    prior = make_section(
        "item_1a_risk_factors",
        "Liquidity risk is material.\n\nRevenue was 100 million.\n\nCustomer demand is stable.",
    )
    current = make_section(
        "item_1a_risk_factors",
        "Liquidity risk is material.\n\nRevenue was 120 million.\n\nCybersecurity risk increased.",
    )
    delta = compute_section_delta(current, prior)
    assert delta.prior_comparable_flag is True
    assert delta.word_count_change == pytest.approx((11 - 12) / 12)
    assert delta.added_token_fraction == pytest.approx(3 / 10)
    assert delta.removed_token_fraction == pytest.approx(4 / 11)
    assert delta.jaccard_similarity == pytest.approx(7 / 14)
    assert delta.sentence_novelty_rate == pytest.approx(2 / 3)
    assert delta.added_paragraphs == 2
    assert delta.removed_paragraphs == 2


def test_numeric_and_finance_term_density_changes():
    prior = make_section("item_7_mda", "Revenue 100 improved. Liquidity remained strong.")
    current = make_section("item_7_mda", "Revenue 120 declined. Liquidity risk became material.")
    delta = compute_section_delta(current, prior)
    assert delta.numeric_density_change == pytest.approx((1 / 7) - (1 / 6))
    prior_terms = 1
    current_terms = 3
    assert delta.finance_term_density_change == pytest.approx((current_terms / 7) - (prior_terms / 6))
    assert {"liquidity", "risk", "material"}.issubset(FINANCE_TERMS)


def test_paragraph_multiset_counts_duplicate_changes():
    prior = make_section(
        "item_3_legal_proceedings",
        "Same paragraph.\n\nSame paragraph.\n\nOld paragraph.",
    )
    current = make_section("item_3_legal_proceedings", "Same paragraph.\n\nNew paragraph.")
    delta = compute_section_delta(current, prior)
    assert delta.added_paragraphs == 1
    assert delta.removed_paragraphs == 2


def test_missing_prior_returns_explicit_nan_features():
    current = make_section("item_7a_market_risk", "Interest-rate risk increased to 5 percent.")
    delta = compute_section_delta(current, None)
    assert delta.prior_comparable_flag is False
    for value in (
        delta.word_count_change,
        delta.added_token_fraction,
        delta.removed_token_fraction,
        delta.jaccard_similarity,
        delta.sentence_novelty_rate,
        delta.added_paragraphs,
        delta.removed_paragraphs,
        delta.numeric_density_change,
        delta.finance_term_density_change,
    ):
        assert math.isnan(value)


def test_mismatched_section_ids_are_rejected():
    current = make_section("item_7_mda", "Current text.")
    prior = make_section("item_1a_risk_factors", "Prior text.")
    with pytest.raises(ValueError):
        compute_section_delta(current, prior)
