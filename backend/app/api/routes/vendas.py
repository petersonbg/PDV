import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import authorize, get_db
from app.models.cash import CashRegister
from app.models.product import Product, StockItem, StockLocation, StockMovement
from app.models.sale import Payment, Sale, SaleItem
from app.schemas import sale as sale_schema

router = APIRouter(prefix="/vendas", tags=["vendas"])


def _calcular_total(itens: list[SaleItem]) -> float:
    return float(sum([float(item.total_price) for item in itens]))


async def _buscar_venda(session: AsyncSession, sale_id: int) -> Sale:
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


async def _buscar_caixa(session: AsyncSession, cash_register_id: int | None) -> CashRegister | None:
    if not cash_register_id:
        return None
    cash_register = await session.get(CashRegister, cash_register_id)
    if not cash_register:
        raise HTTPException(status_code=404, detail="Caixa não encontrado")
    if cash_register.status != "open":
        raise HTTPException(status_code=400, detail="Caixa não está disponível para vendas")
    return cash_register


async def _local_padrao_estoque(session: AsyncSession) -> StockLocation:
    result = await session.execute(select(StockLocation).where(StockLocation.is_default.is_(True)))
    location = result.scalars().first()
    if not location:
        location = StockLocation(name="Padrão", is_default=True)
        session.add(location)
        await session.flush()
    return location


async def _obter_item_estoque(session: AsyncSession, product_id: int) -> StockItem:
    result = await session.execute(select(StockItem).where(StockItem.product_id == product_id))
    stock_item = result.scalars().first()
    if not stock_item:
        location = await _local_padrao_estoque(session)
        stock_item = StockItem(product_id=product_id, location_id=location.id, quantity=0)
        session.add(stock_item)
        await session.flush()
    return stock_item


async def _registrar_baixa_estoque(session: AsyncSession, sale: Sale, user_id: int | None = None) -> None:
    for item in sale.items:
        stock_item = await _obter_item_estoque(session, item.product_id)
        stock_item.quantity = float(stock_item.quantity) - float(item.quantity)
        movement = StockMovement(
            stock_item_id=stock_item.id,
            change=-float(item.quantity),
            movement_type="sale",
            reason=f"Venda {sale.code}",
            sale_item_id=item.id,
            created_by_id=user_id,
        )
        session.add(movement)


async def _estornar_estoque(session: AsyncSession, sale: Sale, user_id: int | None = None) -> None:
    for item in sale.items:
        stock_item = await _obter_item_estoque(session, item.product_id)
        stock_item.quantity = float(stock_item.quantity) + float(item.quantity)
        movement = StockMovement(
            stock_item_id=stock_item.id,
            change=float(item.quantity),
            movement_type="sale_cancel",
            reason=f"Cancelamento da venda {sale.code}",
            sale_item_id=item.id,
            created_by_id=user_id,
        )
        session.add(movement)


def _gerar_cupom(sale: Sale) -> str:
    linhas = [f"CUPOM NÃO FISCAL - VENDA {sale.code}", "------------------------------"]
    for item in sale.items:
        linhas.append(
            f"{item.product.name if item.product else 'Produto'} x{float(item.quantity):.3f} "
            f"@ {float(item.unit_price):.2f} = {float(item.total_price):.2f}"
        )
    linhas.append(f"Subtotal: {_calcular_total(sale.items):.2f}")
    if float(sale.discount or 0) > 0:
        linhas.append(f"Desconto: -{float(sale.discount):.2f}")
    linhas.append(f"Total: {float(sale.total):.2f}")
    if sale.payments:
        linhas.append("Pagamentos:")
        for pagamento in sale.payments:
            status = "pago" if pagamento.paid else "pendente"
            linhas.append(f"- {pagamento.method}: {float(pagamento.amount):.2f} ({status})")
    linhas.append("------------------------------")
    linhas.append("Obrigado pela preferência!")
    return "\n".join(linhas)


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


@router.post("/iniciar", response_model=sale_schema.Sale, status_code=status.HTTP_201_CREATED)
async def iniciar_venda(
    payload: sale_schema.SaleStart,
    session: AsyncSession = Depends(get_db),
    user=Depends(authorize(roles=["GERENTE", "VENDEDOR"])),
):
    await _buscar_caixa(session, payload.cash_register_id)

    sale_code = uuid.uuid4().hex[:8]
    sale = Sale(
        code=sale_code,
        status="in_progress",
        discount=payload.discount,
        total=0,
        items=[],
        payments=[],
        customer_id=payload.customer_id,
        cashier_id=user.id if user else None,
        cash_register_id=payload.cash_register_id,
    )
    session.add(sale)
    await session.commit()
    await session.refresh(sale)
    return sale


@router.post("/adicionar-item", response_model=sale_schema.Sale)
async def adicionar_item(
    payload: sale_schema.SaleAddItem,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "VENDEDOR"])),
):
    sale = await _buscar_venda(session, payload.sale_id)
    if sale.status in {"completed", "canceled"}:
        raise HTTPException(status_code=400, detail="Venda não está aberta para edição")

    product = await session.get(Product, payload.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    unit_price = payload.unit_price if payload.unit_price is not None else float(product.price)
    sale.items.append(
        SaleItem(
            product_id=payload.product_id,
            quantity=payload.quantity,
            unit_price=unit_price,
            total_price=float(payload.quantity) * float(unit_price),
        )
    )
    sale.total = _calcular_total(sale.items) - float(sale.discount or 0)
    await session.commit()
    await session.refresh(sale)
    return sale


@router.post("/finalizar", response_model=sale_schema.SaleWorkflowResult)
async def finalizar_venda(
    payload: sale_schema.SaleFinalize,
    session: AsyncSession = Depends(get_db),
    user=Depends(authorize(roles=["GERENTE", "VENDEDOR", "FINANCEIRO"])),
):
    sale = await _buscar_venda(session, payload.sale_id)
    if sale.status == "canceled":
        raise HTTPException(status_code=400, detail="Venda cancelada não pode ser finalizada")
    if not sale.items:
        raise HTTPException(status_code=400, detail="Adicione itens antes de finalizar a venda")

    await _buscar_caixa(session, payload.cash_register_id or sale.cash_register_id)

    sale.discount = payload.discount
    sale.cash_register_id = payload.cash_register_id or sale.cash_register_id
    sale.total = _calcular_total(sale.items) - float(sale.discount or 0)
    sale.payments.clear()

    payment_total = 0.0
    for payment in payload.payments:
        payment_total += float(payment.amount)
        sale.payments.append(
            Payment(
                method=payment.method,
                amount=payment.amount,
                paid=True,
                transaction_code=uuid.uuid4().hex[:10],
                cash_register_id=sale.cash_register_id,
            )
        )

    if payment_total < float(sale.total):
        raise HTTPException(status_code=400, detail="Pagamentos não cobrem o total da venda")

    sale.status = "completed"
    await session.flush()
    await _registrar_baixa_estoque(session, sale, getattr(user, "id", None))
    await session.commit()
    await session.refresh(sale)

    receipt = _gerar_cupom(sale)
    cash_info = None
    if sale.cash_register_id:
        cash_info = {"cash_register_id": sale.cash_register_id, "movimento": payment_total}
    return sale_schema.SaleWorkflowResult(sale=sale, receipt=receipt, cash_control=cash_info)


@router.post("/cancelar", response_model=sale_schema.Sale)
async def cancelar_venda(
    payload: sale_schema.SaleCancel,
    session: AsyncSession = Depends(get_db),
    user=Depends(authorize(roles=["GERENTE", "FINANCEIRO"])),
):
    sale = await _buscar_venda(session, payload.sale_id)
    if sale.status == "canceled":
        return sale

    if sale.status == "completed" and payload.restock:
        await _estornar_estoque(session, sale, getattr(user, "id", None))

    sale.status = "canceled"
    for payment in sale.payments:
        payment.paid = False

    await session.commit()
    await session.refresh(sale)
    return sale


@router.get("/{sale_id}", response_model=sale_schema.Sale)
async def obter_venda(
    sale_id: int,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "VENDEDOR", "FINANCEIRO"])),
):
    return await _buscar_venda(session, sale_id)
