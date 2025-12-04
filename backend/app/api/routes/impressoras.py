from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import authorize, get_db
from app.models.sale import Sale, SaleItem
from app.schemas.printer import PrintJobResult, PrintSaleRequest
from app.services.printer import ThermalPrinterService

router = APIRouter(prefix="/impressoras", tags=["impressoras"])


async def _carregar_venda(session: AsyncSession, sale_id: int) -> Sale:
    result = await session.execute(
        select(Sale)
        .options(
            selectinload(Sale.items).selectinload(SaleItem.product),
            selectinload(Sale.payments),
        )
        .where(Sale.id == sale_id)
    )
    sale = result.scalar_one_or_none()
    if not sale:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return sale


@router.post(
    "/imprimir-venda",
    response_model=PrintJobResult,
    status_code=status.HTTP_202_ACCEPTED,
)
async def imprimir_cupom_venda(
    payload: PrintSaleRequest,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "VENDEDOR", "FINANCEIRO"])),
):
    sale = await _carregar_venda(session, payload.sale_id)
    if sale.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A venda precisa estar finalizada para impressão",
        )

    printer_service = ThermalPrinterService(
        host=payload.printer.host,
        port=payload.printer.port,
        timeout=payload.printer.timeout,
        encoding=payload.printer.encoding,
    )

    try:
        receipt = printer_service.print_sale(sale)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Falha ao comunicar com a impressora: {exc}",
        ) from exc
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar impressão: {exc}",
        ) from exc

    return PrintJobResult(
        status="sent",
        message="Cupom enviado para a impressora",
        sale_id=sale.id,
        printer=payload.printer,
        receipt_preview=receipt,
    )
