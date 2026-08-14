from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable


@dataclass(frozen=True)
class FilingMetadata:
    cik: str
    accession_no: str
    form: str
    filing_date: str
    report_date: str | None
    acceptance_datetime: datetime
    primary_document: str | None = None
    items: tuple[str, ...] = field(default_factory=tuple)
    amendment_flag: bool = False
    sic_as_filed: str | None = None

    @property
    def conservative_public_datetime(self) -> datetime:
        """Base Phase-0 rule: acceptance + 5 minutes.

        This is intentionally conservative because SEC guidance says filings are
        often available on sec.gov roughly 1–3 minutes after acceptance, while
        no exact first-public-availability timestamp is exposed.
        """
        from datetime import timedelta

        return self.acceptance_datetime + timedelta(minutes=5)


def normalize_cik(cik: str | int) -> str:
    value = str(cik).strip()
    if not value.isdigit():
        raise ValueError(f"CIK must be numeric: {cik!r}")
    return value.zfill(10)


def normalize_items(items: Iterable[str] | None) -> tuple[str, ...]:
    if not items:
        return ()
    return tuple(x.strip() for x in items if x and x.strip())


def parse_sec_acceptance(value: str) -> datetime:
    """Parse SEC ACCEPTANCE-DATETIME (YYYYMMDDHHMMSS) as US/Eastern-aware later.

    EDGAR headers do not carry an offset. We retain an aware UTC object only
    after the caller supplies/normalizes the correct market timezone context.
    For raw ingestion this function treats the value as a naive wall-clock and
    attaches UTC only as a placeholder; production normalization must replace
    this with America/New_York conversion before return-label construction.
    """
    dt = datetime.strptime(value, "%Y%m%d%H%M%S")
    return dt.replace(tzinfo=timezone.utc)
