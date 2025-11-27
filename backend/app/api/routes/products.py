from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import authorize, get_active_user, get_db
from app.models.product import Product
from app.schemas import product as product_schema
from app.services.audit import log_action

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[product_schema.Product])
async def list_products(
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "VENDEDOR"])),
):
    result = await session.execute(select(Product))
    return result.scalars().all()


@router.post("/", response_model=product_schema.Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: product_schema.ProductCreate,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_active_user),
):
    product = Product(**payload.dict())
    session.add(product)
    await session.commit()
    await session.refresh(product)
    await log_action(session, user, "create_product", "Product", product.id, payload.dict())
    return product


@router.get("/{product_id}", response_model=product_schema.Product)
async def get_product(product_id: int, session: AsyncSession = Depends(get_db)):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
