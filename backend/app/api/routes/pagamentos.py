import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import authorize, get_db
from app.models.sale import Payment, Sale
from app.schemas.payment import (
    PaymentConfirmation,
    PaymentIntegrationRequest,
    PaymentIntegrationResponse,
)

router = APIRouter(prefix="/pagamentos", tags=["pagamentos"])


async def _buscar_venda(session: AsyncSession, sale_id: int) -> Sale:
    result = await session.execute(
        select(Sale)
        .options(selectinload(Sale.items), selectinload(Sale.payments))
        .where(Sale.id == sale_id)
    )
    sale = result.scalar_one_or_none()
    if not sale:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return sale


def _criar_codigo_transacao(prefixo: str) -> str:
    return f"{prefixo}-{uuid.uuid4().hex[:10].upper()}"


def _gerar_qrcode_pix(codigo: str, valor: float, sale_id: int) -> tuple[str, str]:
    payload = f"00020126580014BR.GOV.BCB.PIX520400005303986540{valor:.2f}5802BR5913PDV Demo Ltda6014Sao Paulo BR6216SALE{sale_id:06d}6304"
    qr_ascii = f"PIX:{codigo}|SALE:{sale_id}|AMOUNT:{valor:.2f}"
    return qr_ascii, payload


@router.post("/tef", response_model=PaymentIntegrationResponse)
async def iniciar_tef(
    payload: PaymentIntegrationRequest,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "VENDEDOR", "FINANCEIRO"])),
):
    sale = await _buscar_venda(session, payload.sale_id)
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Valor do TEF inválido")

    codigo_transacao = _criar_codigo_transacao("TEF")
    pagamento = Payment(
        sale_id=sale.id,
        method="TEF",
        amount=payload.amount,
        paid=False,
        transaction_code=codigo_transacao,
        created_at=datetime.utcnow(),
        cash_register_id=sale.cash_register_id,
    )
    session.add(pagamento)
    await session.commit()

    return PaymentIntegrationResponse(
        method="TEF",
        transaction_code=codigo_transacao,
        status="pending",
        message="Transação enviada para o pinpad",
    )


@router.post("/pix", response_model=PaymentIntegrationResponse)
async def gerar_pix(
    payload: PaymentIntegrationRequest,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "VENDEDOR", "FINANCEIRO"])),
):
    sale = await _buscar_venda(session, payload.sale_id)
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Valor do PIX inválido")

    codigo_transacao = _criar_codigo_transacao("PIX")
    qr_ascii, copia_cola = _gerar_qrcode_pix(codigo_transacao, payload.amount, sale.id)

    pagamento = Payment(
        sale_id=sale.id,
        method="PIX",
        amount=payload.amount,
        paid=False,
        transaction_code=codigo_transacao,
        created_at=datetime.utcnow(),
        cash_register_id=sale.cash_register_id,
    )
    session.add(pagamento)
    await session.commit()

    return PaymentIntegrationResponse(
        method="PIX",
        transaction_code=codigo_transacao,
        status="pending",
        message="QR Code PIX gerado",
        qr_code=qr_ascii,
        copy_paste=copia_cola,
    )


@router.post("/confirmar", response_model=PaymentIntegrationResponse)
async def confirmar_pagamento(
    payload: PaymentConfirmation,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "VENDEDOR", "FINANCEIRO"])),
):
    result = await session.execute(
        select(Payment)
        .options(selectinload(Payment.sale))
        .where(Payment.transaction_code == payload.transaction_code)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")

    payment.paid = payload.approved
    if payload.approved:
        payment.transaction_code = payload.nsu or payment.transaction_code
        payment.sale.status = payment.sale.status or "pending"
        total_pago = sum(float(p.amount) for p in payment.sale.payments if p.paid)
        if payment.sale.items and total_pago >= float(payment.sale.total or 0):
            payment.sale.status = "completed"
    else:
        payment.sale.status = "pending"

    await session.commit()
    status = "paid" if payload.approved else "declined"
    mensagem = "Pagamento confirmado" if payload.approved else "Pagamento não aprovado"

    return PaymentIntegrationResponse(
        method=payment.method,
        transaction_code=payment.transaction_code,
        status=status,
        message=mensagem,
    )

