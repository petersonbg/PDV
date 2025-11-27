import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.core.security import get_password_hash
from app.models.product import StockItem, StockMovement
from app.models.sale import Sale
from app.models.user import Role, User


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


async def _get_or_create_role(session_factory: sessionmaker, name: str) -> Role:
    async with session_factory() as session:
        result = await session.execute(select(Role).where(Role.name == name))
        role = result.scalar_one_or_none()
        if not role:
            role = Role(name=name)
            session.add(role)
            await session.commit()
            await session.refresh(role)
        return role


async def _create_user(
    session_factory: sessionmaker, email: str, password: str = "secret", role_name: str = "GERENTE"
) -> User:
    role = await _get_or_create_role(session_factory, role_name)
    async with session_factory() as session:
        user = User(
            email=email,
            full_name="Test User",
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=False,
        )
        user.roles.append(role)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def _authenticate(client: AsyncClient, email: str, password: str) -> dict:
    response = await client.post(
        "/api/auth/token",
        data={"username": email, "password": password},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}, tokens


def test_authentication_login_and_refresh(client: AsyncClient, session_factory: sessionmaker):
    email = "auth@example.com"
    password = "strongpass"
    run(_create_user(session_factory, email=email, password=password, role_name="GERENTE"))

    _, tokens = run(_authenticate(client, email, password))
    assert "access_token" in tokens and "refresh_token" in tokens

    refresh_response = run(client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]}))
    assert refresh_response.status_code == 200
    refreshed = refresh_response.json()
    assert refreshed["access_token"]
    assert refreshed["refresh_token"]
    assert refreshed["token_type"] == "bearer"


def test_product_crud_flow(client: AsyncClient, session_factory: sessionmaker):
    email = "manager@example.com"
    run(_create_user(session_factory, email=email, role_name="GERENTE"))
    headers, _ = run(_authenticate(client, email, "secret"))

    product_payload = {
        "sku": "SKU-001",
        "name": "Produto Teste",
        "description": "Item de estoque",
        "price": 19.9,
        "cost": 9.9,
        "is_active": True,
    }
    create_resp = run(client.post("/api/produtos/", json=product_payload, headers=headers))
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["sku"] == product_payload["sku"]

    list_resp = run(client.get("/api/produtos/", headers=headers))
    assert list_resp.status_code == 200
    products = list_resp.json()
    assert any(prod["id"] == created["id"] for prod in products)

    detail_resp = run(client.get(f"/api/produtos/{created['id']}", headers=headers))
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["name"] == product_payload["name"]


def test_sale_workflow_and_stock_control(client: AsyncClient, session_factory: sessionmaker):
    email = "seller@example.com"
    run(_create_user(session_factory, email=email, role_name="GERENTE"))
    headers, _ = run(_authenticate(client, email, "secret"))

    product_payload = {
        "sku": "SKU-VENTA",
        "name": "Produto Venda",
        "description": None,
        "price": 50.0,
        "cost": 20.0,
        "is_active": True,
    }
    product_resp = run(client.post("/api/produtos/", json=product_payload, headers=headers))
    product_id = product_resp.json()["id"]

    sale_payload = {
        "customer_id": None,
        "discount": 0,
        "items": [{"product_id": product_id, "quantity": 2, "unit_price": 50.0}],
        "payments": [{"method": "cash", "amount": 100.0}],
    }
    sale_resp = run(client.post("/api/vendas/", json=sale_payload, headers=headers))
    assert sale_resp.status_code == 201
    sale = sale_resp.json()
    assert float(sale["total"]) == 100.0

    finalize_payload = {
        "sale_id": sale["id"],
        "payments": [{"method": "cash", "amount": 100.0}],
        "discount": 0,
    }
    finalize_resp = run(client.post("/api/vendas/finalizar", json=finalize_payload, headers=headers))
    assert finalize_resp.status_code == 200
    result = finalize_resp.json()
    assert result["sale"]["status"] == "completed"
    assert result["receipt"]

    async def _validate_stock():
        async with session_factory() as session:
            stock_item_result = await session.execute(select(StockItem).where(StockItem.product_id == product_id))
            stock_item = stock_item_result.scalar_one()
            assert float(stock_item.quantity) == -2.0

            movement_result = await session.execute(
                select(StockMovement).where(StockMovement.sale_item.has(product_id=product_id))
            )
            movement = movement_result.scalar_one()
            assert movement.movement_type == "sale"

            sale_db = await session.get(Sale, sale["id"])
            assert sale_db.status == "completed"

    run(_validate_stock())


def test_permissions_block_unauthorized_actions(client: AsyncClient, session_factory: sessionmaker):
    email = "vendedor@example.com"
    run(_create_user(session_factory, email=email, role_name="VENDEDOR"))
    headers, _ = run(_authenticate(client, email, "secret"))

    product_payload = {
        "sku": "SKU-PERM",
        "name": "Produto Restrito",
        "description": "",
        "price": 10.0,
        "cost": 4.0,
        "is_active": True,
    }
    response = run(client.post("/api/produtos/", json=product_payload, headers=headers))
    assert response.status_code == 403
    assert response.json()["detail"] == "Perfil insuficiente"
