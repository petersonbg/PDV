from collections import defaultdict
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import authorize, get_db
from app.models.product import Product, StockItem, StockMovement
from app.models.sale import Customer, Payment, Sale, SaleItem

router = APIRouter(prefix="/relatorios", tags=["relatorios"])


@router.get("/vendas/diario", response_model=list[dict])
async def vendas_diarias(
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "FINANCEIRO", "VENDEDOR"])),
):
    result = await session.execute(select(Sale))
    sales = result.scalars().all()

    resumo: dict[str, dict] = {}
    for sale in sales:
        data_venda = sale.created_at.date().isoformat() if sale.created_at else date.today().isoformat()
        if data_venda not in resumo:
            resumo[data_venda] = {"data": data_venda, "total": 0.0, "quantidade": 0}
        resumo[data_venda]["total"] += float(sale.total or 0)
        resumo[data_venda]["quantidade"] += 1

    return sorted(resumo.values(), key=lambda item: item["data"], reverse=True)


@router.get("/fluxo-caixa", response_model=list[dict])
async def fluxo_caixa(
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "FINANCEIRO"])),
):
    stmt = (
        select(Payment.method, Payment.paid, func.sum(Payment.amount).label("total"))
        .group_by(Payment.method, Payment.paid)
        .order_by(Payment.method)
    )
    result = await session.execute(stmt)

    return [
        {"metodo": row.method, "pago": row.paid, "total": float(row.total or 0)}
        for row in result.all()
    ]


@router.get("/produtos-mais-vendidos", response_model=list[dict])
async def produtos_mais_vendidos(
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "FINANCEIRO", "VENDEDOR"])),
):
    stmt = (
        select(
            Product.id,
            Product.name,
            func.sum(SaleItem.quantity).label("quantidade"),
            func.sum(SaleItem.total_price).label("faturamento"),
        )
        .join(SaleItem, SaleItem.product_id == Product.id)
        .group_by(Product.id, Product.name)
        .order_by(func.sum(SaleItem.quantity).desc())
    )
    result = await session.execute(stmt)

    return [
        {
            "product_id": row.id,
            "produto": row.name,
            "quantidade": float(row.quantidade or 0),
            "faturamento": float(row.faturamento or 0),
        }
        for row in result.all()
    ]


@router.get("/giro-estoque", response_model=list[dict])
async def giro_estoque(
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "ALMOXARIFE", "FINANCEIRO"])),
):
    stmt = (
        select(StockMovement.change, Product.id, Product.name)
        .join(StockItem, StockMovement.stock_item_id == StockItem.id)
        .join(Product, StockItem.product_id == Product.id)
    )
    result = await session.execute(stmt)

    movimentos: dict[int, dict] = defaultdict(
        lambda: {"produto": "", "entradas": 0.0, "saidas": 0.0, "saldo": 0.0}
    )

    for change, product_id, product_name in result.all():
        movimento = movimentos[product_id]
        movimento["produto"] = product_name
        quantidade = float(change or 0)
        if quantidade >= 0:
            movimento["entradas"] += quantidade
        else:
            movimento["saidas"] += abs(quantidade)
        movimento["saldo"] += quantidade

    return [
        {
            "product_id": product_id,
            "produto": data["produto"],
            "entradas": data["entradas"],
            "saidas": data["saidas"],
            "saldo": data["saldo"],
        }
        for product_id, data in movimentos.items()
    ]


@router.get("/clientes-fiado", response_model=list[dict])
async def clientes_fiado(
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "FINANCEIRO"])),
):
    stmt = (
        select(Customer.id, Customer.name, func.sum(Payment.amount).label("pendente"))
        .join(Sale, Sale.customer_id == Customer.id)
        .join(Payment, Payment.sale_id == Sale.id)
        .where(Payment.paid.is_(False))
        .group_by(Customer.id, Customer.name)
        .order_by(Customer.name)
    )
    result = await session.execute(stmt)

    return [
        {"customer_id": row.id, "cliente": row.name, "valor_pendente": float(row.pendente or 0)}
        for row in result.all()
    ]
