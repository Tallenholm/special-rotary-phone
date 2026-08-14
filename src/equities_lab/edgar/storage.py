from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StoredPayload:
    path: Path
    sha256: str
    size_bytes: int


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def store_immutable(root: str | Path, relative_path: str, payload: bytes) -> StoredPayload:
    """Persist a raw SEC payload without silently overwriting different bytes."""
    root_path = Path(root)
    destination = root_path / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)

    digest = sha256_bytes(payload)

    if destination.exists():
        existing = destination.read_bytes()
        existing_digest = sha256_bytes(existing)
        if existing_digest != digest:
            raise FileExistsError(
                f"immutable payload conflict at {destination}: "
                f"existing={existing_digest} incoming={digest}"
            )
        return StoredPayload(destination, digest, len(existing))

    destination.write_bytes(payload)
    return StoredPayload(destination, digest, len(payload))
