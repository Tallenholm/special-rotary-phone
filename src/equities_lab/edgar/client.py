from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

import httpx

from .models import normalize_cik


SEC_DATA_BASE = "https://data.sec.gov"
SEC_ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar/data"


@dataclass
class SecClient:
    user_agent: str
    min_interval_seconds: float = 0.12
    timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        if not self.user_agent.strip() or "@" not in self.user_agent:
            raise ValueError(
                "SEC User-Agent must identify the application and include a contact email"
            )
        self._last_request_at = 0.0
        self._client = httpx.Client(
            headers={
                "User-Agent": self.user_agent,
                "Accept-Encoding": "gzip, deflate",
                "Accept": "application/json,text/html,*/*",
            },
            timeout=self.timeout_seconds,
            follow_redirects=True,
        )

    @classmethod
    def from_env(cls) -> "SecClient":
        value = os.getenv("SEC_USER_AGENT", "").strip()
        if not value:
            raise RuntimeError(
                "Set SEC_USER_AGENT, e.g. 'EquitiesResearchLab your@email.com'"
            )
        return cls(user_agent=value)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "SecClient":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def _throttle(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_request_at
        remaining = self.min_interval_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)

    def _get(self, url: str) -> httpx.Response:
        self._throttle()
        response = self._client.get(url)
        self._last_request_at = time.monotonic()
        response.raise_for_status()
        return response

    def company_submissions(self, cik: str | int) -> dict[str, Any]:
        normalized = normalize_cik(cik)
        url = f"{SEC_DATA_BASE}/submissions/CIK{normalized}.json"
        return self._get(url).json()

    def filing_bytes(
        self,
        cik: str | int,
        accession_no: str,
        document_name: str,
    ) -> bytes:
        cik_numeric = str(int(normalize_cik(cik)))
        accession_compact = accession_no.replace("-", "")
        url = (
            f"{SEC_ARCHIVES_BASE}/{cik_numeric}/{accession_compact}/{document_name}"
        )
        return self._get(url).content

    def complete_submission_bytes(self, cik: str | int, accession_no: str) -> bytes:
        filename = f"{accession_no}.txt"
        return self.filing_bytes(cik, accession_no, filename)
