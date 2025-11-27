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
    return fiscal_service.emit_invoice(payload)


@router.get("/status/{invoice_id}")
async def consultar_status(
    invoice_id: str, _: None = Depends(authorize(roles=["GERENTE", "FISCAL"]))
):
    return {"invoice_id": invoice_id, "status": "pendente"}
