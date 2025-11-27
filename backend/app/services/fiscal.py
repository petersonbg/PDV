from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.fiscal import (
    ContingencyManager,
    DigitalSigner,
    NfceProcessor,
    SefazClient,
    TaxTableRepository,
)
from app.schemas.fiscal import CancelRequest, CancelResponse, InvoiceRequest, InvoiceResponse


@dataclass
class FiscalResult:
    success: bool
    message: str
    protocol: str | None
    access_key: str | None
    contingency: bool = False
    xml_preview: str | None = None


class FiscalAdapter(Protocol):
    async def emit(self, payload: InvoiceRequest) -> FiscalResult:
        ...

    async def cancel(self, payload: CancelRequest) -> FiscalResult:
        ...

    async def status(self, access_key: str) -> FiscalResult:
        ...


class NfceAdapter:
    """Adapter NFC-e que encadeia geração, assinatura e comunicação com SEFAZ."""

    def __init__(self) -> None:
        self.tax_tables = TaxTableRepository()
        self.signer = DigitalSigner()
        self.sefaz_client = SefazClient()
        self.contingency_manager = ContingencyManager()
        self.processor = NfceProcessor(
            tax_tables=self.tax_tables,
            signer=self.signer,
            sefaz_client=self.sefaz_client,
            contingency_manager=self.contingency_manager,
        )

    async def emit(self, payload: InvoiceRequest) -> FiscalResult:
        emission = self.processor.emit(
            sale_id=payload.sale_id,
            items=payload.items,
            offline=payload.use_contingency,
            contingency_reason=payload.contingency_reason,
        )
        return FiscalResult(
            success=emission.success,
            message=emission.message,
            protocol=emission.protocol,
            access_key=emission.access_key,
            contingency=emission.contingency,
            xml_preview=emission.xml,
        )

    async def cancel(self, payload: CancelRequest) -> FiscalResult:
        emission = self.processor.cancel(payload.access_key, payload.justification)
        return FiscalResult(
            success=emission.success,
            message=emission.message,
            protocol=emission.protocol,
            access_key=emission.access_key,
            contingency=emission.contingency,
            xml_preview=emission.xml or None,
        )

    async def status(self, access_key: str) -> FiscalResult:
        emission = self.processor.status(access_key)
        return FiscalResult(
            success=emission.success,
            message=emission.message,
            protocol=emission.protocol,
            access_key=emission.access_key,
            contingency=emission.contingency,
            xml_preview=emission.xml or None,
        )

    def pending_contingency(self) -> list[dict]:
        return [
            {
                "reference": record.reference,
                "payload": record.payload,
                "queued_at": record.created_at,
                "reason": record.reason,
            }
            for record in self.contingency_manager.pending()
        ]


class FiscalService:
    def __init__(self, adapter: FiscalAdapter | None = None) -> None:
        self.adapter = adapter or NfceAdapter()

    async def emit_invoice(self, payload: InvoiceRequest) -> InvoiceResponse:
        result = await self.adapter.emit(payload)
        return InvoiceResponse(**result.__dict__)

    async def cancel_invoice(self, payload: CancelRequest) -> CancelResponse:
        result = await self.adapter.cancel(payload)
        return CancelResponse(**result.__dict__)

    async def status(self, access_key: str) -> InvoiceResponse:
        result = await self.adapter.status(access_key)
        return InvoiceResponse(**result.__dict__)

    def contingency_queue(self) -> list[dict]:
        if hasattr(self.adapter, "pending_contingency"):
            return self.adapter.pending_contingency()  # type: ignore[no-any-return]
        return []
