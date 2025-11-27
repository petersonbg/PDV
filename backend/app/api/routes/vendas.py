import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import authorize, get_db
from app.models.product import Product
from app.models.sale import Payment, Sale, SaleItem
from app.schemas import sale as sale_schema

router = APIRouter(prefix="/vendas", tags=["vendas"])


def _calcular_total(itens: list[SaleItem]) -> float:
    return float(sum([float(item.total_price) for item in itens]))


@router.get("/", response_model=list[sale_schema.Sale])
async def listar_vendas(
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "FINANCEIRO"])),
):
    result = await session.execute(select(Sale))
    return result.scalars().unique().all()


@router.post("/", response_model=sale_schema.Sale, status_code=status.HTTP_201_CREATED)
async def criar_venda(
    payload: sale_schema.SaleCreate,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "VENDEDOR"])),
):
    sale_code = uuid.uuid4().hex[:8]
    itens: list[SaleItem] = []
    for item in payload.items:
        product = await session.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Produto {item.product_id} não encontrado")
        total_price = float(item.quantity) * float(item.unit_price)
        itens.append(
            SaleItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=total_price,
            )
        )

    pagamentos = [Payment(method=p.method, amount=p.amount, paid=False) for p in payload.payments]
    sale_total = _calcular_total(itens) - float(payload.discount or 0)
    sale = Sale(
        code=sale_code,
        status="pending",
        discount=payload.discount,
        total=sale_total,
        items=itens,
        payments=pagamentos,
        customer_id=payload.customer_id,
    )

    session.add(sale)
    await session.commit()
    await session.refresh(sale)
    return sale
