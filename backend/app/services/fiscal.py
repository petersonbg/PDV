from abc import ABC, abstractmethod
from typing import Protocol

from app.models.sale import Sale


class FiscalResult(Protocol):
    success: bool
    message: str
    protocol: str | None
    access_key: str | None


class FiscalAdapter(ABC):
    """Interface para integrar NFC-e, SAT ou MFE."""

    @abstractmethod
    async def emit(self, sale: Sale) -> FiscalResult:
        ...

    @abstractmethod
    async def cancel(self, document_number: str, justification: str) -> FiscalResult:
        ...


class DummyFiscalAdapter(FiscalAdapter):
    async def emit(self, sale: Sale) -> FiscalResult:
        return type("Result", (), {"success": True, "message": "queued", "protocol": None, "access_key": None})()

    async def cancel(self, document_number: str, justification: str) -> FiscalResult:
        return type("Result", (), {"success": True, "message": "cancelled", "protocol": "000", "access_key": None})()
