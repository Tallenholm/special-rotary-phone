from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable
from zoneinfo import ZoneInfo


SEC_TIMEZONE = ZoneInfo("America/New_York")


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

        SEC guidance says filings are often available on sec.gov roughly 1–3
        minutes after acceptance, while no exact first-public-availability
        timestamp is exposed. The lab therefore uses +5 minutes as its default
        conservative availability rule and tests alternative delays separately.
        """
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
    """Parse SEC ``ACCEPTANCE-DATETIME`` as an America/New_York timestamp.

    EDGAR header timestamps are local Eastern wall-clock timestamps without an
    explicit offset. ZoneInfo supplies the correct EST/EDT offset for the date,
    which is essential before aligning a filing with market sessions.
    """
    dt = datetime.strptime(value, "%Y%m%d%H%M%S")
    return dt.replace(tzinfo=SEC_TIMEZONE)
