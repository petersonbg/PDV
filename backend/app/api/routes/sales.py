import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_active_user, get_db
from app.models.product import Product
from app.models.sale import Payment, Sale, SaleItem
from app.schemas import sale as sale_schema

router = APIRouter(prefix="/sales", tags=["sales"])


def _calculate_total(items: list[SaleItem]) -> float:
    return float(sum([float(item.total_price) for item in items]))


@router.get("/", response_model=list[sale_schema.Sale])
async def list_sales(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Sale))
    return result.scalars().unique().all()


@router.post("/", response_model=sale_schema.Sale, status_code=status.HTTP_201_CREATED)
async def create_sale(
    payload: sale_schema.SaleCreate,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_active_user),
):
    sale_code = uuid.uuid4().hex[:8]
    items: list[SaleItem] = []
    for item in payload.items:
        product = await session.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        total_price = float(item.quantity) * float(item.unit_price)
        items.append(
            SaleItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=total_price,
            )
        )

    payments = [Payment(method=p.method, amount=p.amount, paid=False) for p in payload.payments]
    sale_total = sum([float(p.amount) for p in payload.payments])
    sale = Sale(
        code=sale_code,
        status="pending",
        discount=payload.discount,
        total=sale_total,
        items=items,
        payments=payments,
        customer_id=payload.customer_id,
        cashier_id=user.id if user else None,
    )

    session.add(sale)
    await session.commit()
    await session.refresh(sale)
    return sale
