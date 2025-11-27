from fastapi import APIRouter, Depends

from app.api.deps import authorize
from app.schemas import fiscal as fiscal_schema
from app.services.fiscal import FiscalService

router = APIRouter(prefix="/fiscal", tags=["fiscal"])
fiscal_service = FiscalService()


@router.post("/nota", response_model=fiscal_schema.InvoiceResponse)
async def emitir_nota(
    payload: fiscal_schema.InvoiceRequest,
    _: None = Depends(authorize(roles=["GERENTE", "FISCAL"])),
):
    return await fiscal_service.emit_invoice(payload)


@router.post("/nota/cancelamento", response_model=fiscal_schema.CancelResponse)
async def cancelar_nota(
    payload: fiscal_schema.CancelRequest,
    _: None = Depends(authorize(roles=["GERENTE", "FISCAL"])),
):
    return await fiscal_service.cancel_invoice(payload)


@router.get("/status/{access_key}", response_model=fiscal_schema.InvoiceResponse)
async def consultar_status(
    access_key: str, _: None = Depends(authorize(roles=["GERENTE", "FISCAL"]))
):
    return await fiscal_service.status(access_key)


@router.get("/contingencia", response_model=list[fiscal_schema.ContingencyStatus])
async def listar_contingencia(
    _: None = Depends(authorize(roles=["GERENTE", "FISCAL"])),
):
    return [
        fiscal_schema.ContingencyStatus(
            reference=item["reference"],
            queued_at=item["queued_at"],
            reason=item["reason"],
        )
        for item in fiscal_service.contingency_queue()
    ]
