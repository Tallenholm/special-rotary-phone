from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from bs4 import BeautifulSoup


_SPACE_RE = re.compile(r"[ \t\f\v]+")
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")


@dataclass(frozen=True)
class SectionDelta:
    prior_word_count: int
    current_word_count: int
    word_count_change_pct: float
    token_jaccard: float
    added_token_ratio: float
    removed_token_ratio: float
    changed: bool


def _clean_html_text(payload: bytes | str) -> str:
    soup = BeautifulSoup(payload, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    raw = soup.get_text("\n")
    lines: list[str] = []
    for line in raw.splitlines():
        line = _SPACE_RE.sub(" ", line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def _heading_pattern(item: str) -> re.Pattern[str]:
    escaped = re.escape(item)
    return re.compile(rf"(?im)^\s*item\s+{escaped}\b[^\n]*$")


def _next_heading_pattern(
    items: Iterable[str], *, include_part_ii: bool = False
) -> re.Pattern[str]:
    escaped = "|".join(re.escape(item) for item in items)
    part = r"|^\s*part\s+ii\b[^\n]*$" if include_part_ii else ""
    return re.compile(rf"(?im)(^\s*item\s+(?:{escaped})\b[^\n]*${part})")


def _best_section(
    text: str,
    *,
    item: str,
    next_items: Iterable[str],
    min_start: int = 0,
    include_part_ii_as_end: bool = False,
) -> str:
    start_re = _heading_pattern(item)
    end_re = _next_heading_pattern(
        next_items, include_part_ii=include_part_ii_as_end
    )

    candidates: list[str] = []
    for match in start_re.finditer(text, pos=min_start):
        body_start = match.end()
        end_match = end_re.search(text, pos=body_start)
        body_end = end_match.start() if end_match else len(text)
        body = text[body_start:body_end].strip()
        if body:
            candidates.append(body)

    if not candidates:
        return ""

    # Repeated item headings are common in tables of contents. The real filing
    # section is ordinarily much longer than the TOC entry, so select the
    # candidate with the most lexical content rather than the first match.
    return max(candidates, key=lambda value: len(_TOKEN_RE.findall(value)))


def extract_sections(payload: bytes | str, *, form: str) -> dict[str, str]:
    text = _clean_html_text(payload)
    normalized_form = form.upper().replace("/A", "")

    if normalized_form == "10-K":
        return {
            "item_1a_risk_factors": _best_section(
                text,
                item="1a",
                next_items=("1b", "1c", "2"),
            ),
            "item_7_mda": _best_section(
                text,
                item="7",
                next_items=("7a", "8"),
            ),
        }

    if normalized_form == "10-Q":
        part_ii_matches = list(
            re.finditer(r"(?im)^\s*part\s+ii\b[^\n]*$", text)
        )
        part_ii_start = part_ii_matches[-1].end() if part_ii_matches else 0
        return {
            "item_2_mda": _best_section(
                text,
                item="2",
                next_items=("3", "4"),
                include_part_ii_as_end=True,
            ),
            "part_ii_item_1a_risk_factors": _best_section(
                text,
                item="1a",
                next_items=("2", "3"),
                min_start=part_ii_start,
            ),
        }

    raise ValueError(f"unsupported form for section extraction: {form!r}")


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN_RE.findall(text)]


def compute_section_delta(prior: str, current: str) -> SectionDelta:
    prior_tokens = _tokens(prior)
    current_tokens = _tokens(current)
    prior_set = set(prior_tokens)
    current_set = set(current_tokens)
    union = prior_set | current_set

    token_jaccard = (
        len(prior_set & current_set) / len(union)
        if union
        else 1.0
    )
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
