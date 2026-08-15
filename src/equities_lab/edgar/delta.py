from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
import re

from .sections import ExtractedSection


FINANCE_TERMS = frozenset({
    "uncertainty",
    "risk",
    "material",
    "litigation",
    "liquidity",
    "impairment",
    "default",
    "covenant",
    "restructuring",
    "investigation",
})

_TOKEN_RE = re.compile(r"\b(?:[A-Za-z]+(?:['’][A-Za-z]+)?|\d+(?:\.\d+)?)\b")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True)
class SectionDelta:
    section_id: str
    word_count_change: float
    added_token_fraction: float
    removed_token_fraction: float
    jaccard_similarity: float
    sentence_novelty_rate: float
    added_paragraphs: float
    removed_paragraphs: float
    numeric_density_change: float
    finance_term_density_change: float
    prior_comparable_flag: bool


def _tokens(text: str) -> list[str]:
    return [m.group(0).lower().replace("’", "'") for m in _TOKEN_RE.finditer(text)]


def _normalized_sentence(sentence: str) -> str:
    return " ".join(_tokens(sentence))


def _sentences(text: str) -> list[str]:
    return [
        s
        for s in (_normalized_sentence(x) for x in _SENTENCE_RE.split(text.strip()))
        if s
    ]


def _paragraphs(text: str) -> list[str]:
    paragraphs = []
    for para in re.split(r"\n\s*\n", text.strip()):
        normalized = " ".join(_tokens(para))
        if normalized:
            paragraphs.append(normalized)
    return paragraphs


def _numeric_density(tokens: list[str]) -> float:
    if not tokens:
        return 0.0
    return sum(token[0].isdigit() for token in tokens) / len(tokens)


def _finance_term_density(tokens: list[str]) -> float:
    if not tokens:
        return 0.0
    return sum(token in FINANCE_TERMS for token in tokens) / len(tokens)


def _nan_delta(section_id: str) -> SectionDelta:
    nan = math.nan
    return SectionDelta(
        section_id=section_id,
        word_count_change=nan,
        added_token_fraction=nan,
        removed_token_fraction=nan,
        jaccard_similarity=nan,
        sentence_novelty_rate=nan,
        added_paragraphs=nan,
        removed_paragraphs=nan,
        numeric_density_change=nan,
        finance_term_density_change=nan,
        prior_comparable_flag=False,
    )


def compute_section_delta(
    current: ExtractedSection,
    prior: ExtractedSection | None,
) -> SectionDelta:
    if prior is None:
        return _nan_delta(current.section_id)
    if current.section_id != prior.section_id:
        raise ValueError(
            f"Section IDs must match: current={current.section_id!r}, prior={prior.section_id!r}"
        )

    current_tokens = _tokens(current.normalized_text)
    prior_tokens = _tokens(prior.normalized_text)
    current_set = set(current_tokens)
    prior_set = set(prior_tokens)

    union = current_set | prior_set
    jaccard = len(current_set & prior_set) / len(union) if union else 1.0

    current_sentences = _sentences(current.normalized_text)
    prior_sentence_set = set(_sentences(prior.normalized_text))
    novelty = (
        sum(sentence not in prior_sentence_set for sentence in current_sentences)
        / len(current_sentences)
        if current_sentences
        else 0.0
    )

    current_paragraphs = Counter(_paragraphs(current.normalized_text))
    prior_paragraphs = Counter(_paragraphs(prior.normalized_text))
    added_paragraphs = float(sum((current_paragraphs - prior_paragraphs).values()))
    removed_paragraphs = float(sum((prior_paragraphs - current_paragraphs).values()))

    return SectionDelta(
        section_id=current.section_id,
        word_count_change=(len(current_tokens) - len(prior_tokens))
        / max(len(prior_tokens), 1),
        added_token_fraction=len(current_set - prior_set) / max(len(current_set), 1),
        removed_token_fraction=len(prior_set - current_set) / max(len(prior_set), 1),
        jaccard_similarity=jaccard,
        sentence_novelty_rate=novelty,
        added_paragraphs=added_paragraphs,
        removed_paragraphs=removed_paragraphs,
        numeric_density_change=_numeric_density(current_tokens)
        - _numeric_density(prior_tokens),
        finance_term_density_change=_finance_term_density(current_tokens)
        - _finance_term_density(prior_tokens),
        prior_comparable_flag=True,
    )
