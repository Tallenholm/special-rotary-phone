from datetime import timedelta

import pytest

from equities_lab.edgar.models import normalize_cik, parse_sec_acceptance
from equities_lab.edgar.storage import sha256_bytes, store_immutable


def test_normalize_cik_zero_pads() -> None:
    assert normalize_cik(320193) == "0000320193"


def test_normalize_cik_rejects_non_numeric() -> None:
    with pytest.raises(ValueError):
        normalize_cik("AAPL")


def test_sec_acceptance_uses_eastern_standard_time_in_winter() -> None:
    dt = parse_sec_acceptance("20260115163000")
    assert dt.utcoffset() == timedelta(hours=-5)
    assert dt.tzname() == "EST"


def test_sec_acceptance_uses_eastern_daylight_time_in_summer() -> None:
    dt = parse_sec_acceptance("20260715163000")
    assert dt.utcoffset() == timedelta(hours=-4)
    assert dt.tzname() == "EDT"


def test_sha256_is_deterministic() -> None:
    assert sha256_bytes(b"abc") == (
        "ba7816bf8f01cfea414140de5dae2223"
        "b00361a396177a9cb410ff61f20015ad"
    )


def test_store_immutable_allows_same_bytes(tmp_path) -> None:
    first = store_immutable(tmp_path, "raw/a.txt", b"same")
    second = store_immutable(tmp_path, "raw/a.txt", b"same")
    assert first.sha256 == second.sha256
    assert second.size_bytes == 4


def test_store_immutable_rejects_changed_bytes(tmp_path) -> None:
    store_immutable(tmp_path, "raw/a.txt", b"original")
    with pytest.raises(FileExistsError):
        store_immutable(tmp_path, "raw/a.txt", b"changed")
