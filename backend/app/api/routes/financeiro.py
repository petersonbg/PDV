from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import authorize, get_db
from app.models.sale import Payment

router = APIRouter(prefix="/financeiro", tags=["financeiro"])


@router.get("/fluxo-caixa", response_model=list[dict])
async def consultar_fluxo_caixa(
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "FINANCEIRO"])),
):
    result = await session.execute(Payment.__table__.select())
    return [
        {
            "id": payment.id,
            "metodo": payment.method,
            "valor": float(payment.amount),
            "pago": payment.paid,
        }
        for payment in result.scalars().all()
    ]


@router.get("/resumo")
async def resumo_financeiro(
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "FINANCEIRO"])),
):
    result = await session.execute(Payment.__table__.select())
    movimentos = result.scalars().all()
    total = sum([float(m.amount) if m.paid else 0 for m in movimentos])
    return {"saldo": total, "atualizado_em": date.today().isoformat()}
