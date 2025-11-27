from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class ContingencyRecord:
    reference: str
    payload: str
    created_at: datetime
    reason: str | None = None


class ContingencyManager:
    """Armazena documentos emitidos offline para posterior sincronização."""

    def __init__(self) -> None:
        self._queue: List[ContingencyRecord] = []

    def enqueue(self, reference: str, payload: str, reason: str | None = None) -> ContingencyRecord:
        record = ContingencyRecord(
            reference=reference,
            payload=payload,
            reason=reason,
            created_at=datetime.utcnow(),
        )
        self._queue.append(record)
        return record

    def pending(self) -> list[ContingencyRecord]:
        return list(self._queue)

    def flush(self) -> list[ContingencyRecord]:
        flushed = list(self._queue)
        self._queue.clear()
        return flushed
