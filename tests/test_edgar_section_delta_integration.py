from pathlib import Path

from equities_lab.edgar.delta import compute_section_delta
from equities_lab.edgar.sections import extract_sections


def test_sec_like_fixture_ignores_hidden_duplicate_and_produces_delta():
    html = Path("tests/fixtures/sec_like_10k_excerpt.html").read_text()
    current = extract_sections(html, "10-K")["item_1a_risk_factors"]

    assert current.extraction_failure_reason is None
    assert "Cybersecurity incidents" in current.raw_text
    assert "Hidden duplicate risk content" not in current.raw_text
    assert "420" in current.normalized_text

    prior_html = html.replace(
        "Cybersecurity incidents and supplier disruption", "Supplier disruption"
    ).replace("$420 million", "$390 million")
    prior = extract_sections(prior_html, "10-K")["item_1a_risk_factors"]
    delta = compute_section_delta(current, prior)

    assert delta.prior_comparable_flag is True
    assert delta.added_token_fraction > 0
    assert delta.numeric_density_change != 0
