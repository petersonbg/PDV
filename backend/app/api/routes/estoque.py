from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import authorize, get_db
from app.models.product import StockItem, StockLocation

router = APIRouter(prefix="/estoque", tags=["estoque"])


@router.get("/itens", response_model=list[dict])
async def listar_itens(
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "ALMOXARIFE"])),
):
    result = await session.execute(StockItem.__table__.select())
    return [
        {"id": item.id, "product_id": item.product_id, "location_id": item.location_id, "quantity": float(item.quantity)}
        for item in result.scalars().all()
    ]


@router.get("/locais", response_model=list[dict])
async def listar_locais(
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "ALMOXARIFE"])),
):
    result = await session.execute(StockLocation.__table__.select())
    return [{"id": loc.id, "nome": loc.name, "padrao": loc.is_default} for loc in result.scalars().all()]
