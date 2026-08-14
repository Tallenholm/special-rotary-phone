from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Iterable

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class SectionDelta:
    """Backward-compatible simple text delta used by the original EDGAR core."""

    prior_word_count: int
    current_word_count: int
    word_count_change_pct: float
    token_jaccard: float
    added_token_ratio: float
    removed_token_ratio: float
    changed: bool


@dataclass(frozen=True)
class ExtractedSection:
    """Auditable section-extraction record for research-grade filing deltas."""

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


@dataclass(frozen=True)
class _SectionSpec:
    section_id: str
    section_name: str
    start_item: str
    end_items: tuple[str, ...]


_TEN_K_SPECS = (
    _SectionSpec("item_1_business", "Item 1 — Business", "1", ("1A", "1B", "1C", "2")),
    _SectionSpec("item_1a_risk_factors", "Item 1A — Risk Factors", "1A", ("1B", "1C", "2")),
    _SectionSpec("item_2_properties", "Item 2 — Properties", "2", ("3",)),
    _SectionSpec("item_3_legal_proceedings", "Item 3 — Legal Proceedings", "3", ("4",)),
    _SectionSpec("item_7_mda", "Item 7 — MD&A", "7", ("7A", "8")),
    _SectionSpec("item_7a_market_risk", "Item 7A — Market Risk", "7A", ("8",)),
)

_TEN_Q_PART_I_SPECS = (
    _SectionSpec("part_i_item_2_mda", "Part I Item 2 — MD&A", "2", ("3",)),
    _SectionSpec("part_i_item_3_market_risk", "Part I Item 3 — Market Risk", "3", ("4",)),
)

_TEN_Q_PART_II_SPECS = (
    _SectionSpec("part_ii_item_1_legal_proceedings", "Part II Item 1 — Legal Proceedings", "1", ("1A", "2")),
    _SectionSpec("part_ii_item_1a_risk_factors", "Part II Item 1A — Risk Factors", "1A", ("2",)),
)

_BLOCK_TAGS = {
    "p", "div", "section", "article", "li", "tr", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6",
}
_TOKEN_RE = re.compile(r"\b[A-Za-z0-9]+(?:['’][A-Za-z]+)?\b")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _clean_line(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _visible_lines(html: bytes | str) -> list[str]:
    soup = BeautifulSoup(html or "", "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    for tag in list(soup.find_all(True)):
        if tag.attrs is None:
            continue
        style = re.sub(r"\s+", "", str(tag.get("style", "")).lower())
        aria_hidden = str(tag.get("aria-hidden", "")).lower()
        if (
            tag.has_attr("hidden")
            or aria_hidden == "true"
            or "display:none" in style
            or "visibility:hidden" in style
        ):
            tag.decompose()

    lines: list[str] = []
    for element in soup.find_all(_BLOCK_TAGS):
        if any(child.name in _BLOCK_TAGS for child in element.find_all(recursive=False)):
            continue
        text = _clean_line(element.get_text(" ", strip=True))
        if text and (not lines or text != lines[-1]):
            lines.append(text)
    if not lines:
        fallback = [_clean_line(x) for x in soup.get_text("\n").splitlines()]
        lines = [x for x in fallback if x]
    return lines


def _normalize_text(raw: str) -> str:
    paragraphs: list[str] = []
    for para in re.split(r"\n\s*\n|\n", raw):
        para = _clean_line(para)
        if not para:
            continue
        para = re.sub(r"(?<=\w)-\s+(?=\w)", "", para)
        paragraphs.append(para)
    return "\n\n".join(paragraphs)


def _word_count(text: str) -> int:
    return len(_TOKEN_RE.findall(text))


def _item_regex(item: str) -> re.Pattern[str]:
    escaped = re.escape(item)
    return re.compile(rf"^\s*item\s+{escaped}\b\s*[.:\-—–]?\s*.*$", re.IGNORECASE)


def _part_regex(part: str) -> re.Pattern[str]:
    return re.compile(rf"^\s*part\s+{part}\b\s*[.:\-—–]?\s*.*$", re.IGNORECASE)


def _indices_matching(
    lines: list[str], pattern: re.Pattern[str], start: int = 0, end: int | None = None
) -> list[int]:
    stop = len(lines) if end is None else end
    return [i for i in range(start, stop) if pattern.match(lines[i])]


def _find_next_boundary(
    lines: list[str],
    start_idx: int,
    end_items: Iterable[str],
    limit: int | None = None,
) -> tuple[int, str] | None:
    stop = len(lines) if limit is None else limit
    candidates: list[tuple[int, str]] = []
    for end_item in end_items:
        pattern = _item_regex(end_item)
        for idx in _indices_matching(lines, pattern, start_idx + 1, stop):
            candidates.append((idx, lines[idx]))
    return min(candidates, key=lambda x: x[0]) if candidates else None


def _failure(
    spec: _SectionSpec, reason: str, start_marker: str | None = None
) -> ExtractedSection:
    empty_hash = _sha256("")
    return ExtractedSection(
        section_id=spec.section_id,
        section_name=spec.section_name,
        start_marker=start_marker,
        end_marker=None,
        raw_text="",
        normalized_text="",
        raw_text_sha256=empty_hash,
        normalized_text_sha256=empty_hash,
        word_count=0,
        extraction_confidence=0.0,
        extraction_failure_reason=reason,
    )


def _extract_spec(
    lines: list[str],
    spec: _SectionSpec,
    region_start: int = 0,
    region_end: int | None = None,
) -> ExtractedSection:
    stop = len(lines) if region_end is None else region_end
    starts = _indices_matching(lines, _item_regex(spec.start_item), region_start, stop)
    if not starts:
        return _failure(spec, "missing_start_marker")

    viable: list[tuple[int, int, str, int]] = []
    start_without_end: str | None = None
    for start_idx in starts:
        boundary = _find_next_boundary(lines, start_idx, spec.end_items, stop)
        if boundary is None:
            start_without_end = lines[start_idx]
            continue
        end_idx, end_marker = boundary
        body_text = "\n".join(lines[start_idx + 1 : end_idx]).strip()
        wc = _word_count(body_text)
        if wc >= 6:
            viable.append((start_idx, end_idx, end_marker, wc))

    if not viable:
        if start_without_end is not None:
            return _failure(spec, "missing_end_marker", start_without_end)
        return _failure(spec, "insufficient_section_content", lines[starts[-1]])

    start_idx, end_idx, end_marker, _ = max(viable, key=lambda x: (x[3], x[0]))
    raw_text = "\n".join(lines[start_idx + 1 : end_idx]).strip()
    normalized = _normalize_text(raw_text)
    competing = len(viable)
    confidence = 1.0 if competing == 1 else max(0.6, 1.0 - 0.1 * (competing - 1))

    return ExtractedSection(
        section_id=spec.section_id,
        section_name=spec.section_name,
        start_marker=lines[start_idx],
        end_marker=end_marker,
        raw_text=raw_text,
        normalized_text=normalized,
        raw_text_sha256=_sha256(raw_text),
        normalized_text_sha256=_sha256(normalized),
        word_count=_word_count(normalized),
        extraction_confidence=confidence,
        extraction_failure_reason=None,
    )


def _choose_10q_body_parts(
    lines: list[str],
) -> tuple[tuple[int, int], tuple[int, int]] | None:
    part_i = _indices_matching(lines, _part_regex("I"))
    part_ii = _indices_matching(lines, _part_regex("II"))
    pairs: list[tuple[int, int]] = []
    for i in part_i:
        for j in part_ii:
            if j > i:
                pairs.append((i, j))
    if not pairs:
        return None
    i, j = max(pairs, key=lambda p: p[1] - p[0])
    return (i + 1, j), (j + 1, len(lines))


def extract_section_records(
    payload: bytes | str, form: str
) -> dict[str, ExtractedSection]:
    """Extract auditable canonical section records from 10-K/10-Q HTML."""

    normalized_form = form.strip().upper()
    if normalized_form not in {"10-K", "10-K/A", "10-Q", "10-Q/A"}:
        raise ValueError(f"Unsupported filing form: {form!r}")

    lines = _visible_lines(payload)
    if normalized_form.startswith("10-K"):
        return {spec.section_id: _extract_spec(lines, spec) for spec in _TEN_K_SPECS}

    regions = _choose_10q_body_parts(lines)
    if regions is None:
        specs = (*_TEN_Q_PART_I_SPECS, *_TEN_Q_PART_II_SPECS)
        return {
            spec.section_id: _failure(spec, "missing_part_markers") for spec in specs
        }

    part_i_region, part_ii_region = regions
    result = {
        spec.section_id: _extract_spec(lines, spec, *part_i_region)
        for spec in _TEN_Q_PART_I_SPECS
    }
    result.update(
        {
            spec.section_id: _extract_spec(lines, spec, *part_ii_region)
            for spec in _TEN_Q_PART_II_SPECS
        }
    )
    return result


def extract_sections(payload: bytes | str, *, form: str) -> dict[str, str]:
    """Backward-compatible string-only section API from the original core."""

    records = extract_section_records(payload, form)
    normalized_form = form.upper().replace("/A", "")
    if normalized_form == "10-K":
        return {
            "item_1a_risk_factors": records["item_1a_risk_factors"].raw_text,
            "item_7_mda": records["item_7_mda"].raw_text,
        }
    if normalized_form == "10-Q":
        return {
            "item_2_mda": records["part_i_item_2_mda"].raw_text,
            "part_ii_item_1a_risk_factors": records[
                "part_ii_item_1a_risk_factors"
            ].raw_text,
        }
    raise ValueError(f"unsupported form for section extraction: {form!r}")


def _legacy_tokens(text: str) -> list[str]:
    return [token.lower().replace("’", "'") for token in _TOKEN_RE.findall(text)]


def compute_section_delta(prior: str, current: str) -> SectionDelta:
    """Backward-compatible simple delta API; richer deltas live in delta.py."""

    prior_tokens = _legacy_tokens(prior)
    current_tokens = _legacy_tokens(current)
    prior_set = set(prior_tokens)
    current_set = set(current_tokens)
    union = prior_set | current_set

    token_jaccard = len(prior_set & current_set) / len(union) if union else 1.0
    added_token_ratio = len(current_set - prior_set) / max(1, len(current_set))
    removed_token_ratio = len(prior_set - current_set) / max(1, len(prior_set))
    word_count_change_pct = (
        (len(current_tokens) - len(prior_tokens)) / len(prior_tokens)
        if prior_tokens
        else (1.0 if current_tokens else 0.0)
    )

    return SectionDelta(
        prior_word_count=len(prior_tokens),
        current_word_count=len(current_tokens),
        word_count_change_pct=word_count_change_pct,
        token_jaccard=token_jaccard,
        added_token_ratio=added_token_ratio,
        removed_token_ratio=removed_token_ratio,
        changed=" ".join(prior_tokens) != " ".join(current_tokens),
    )
