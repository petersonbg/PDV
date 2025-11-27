from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import authorize, get_db
from app.models.product import Product
from app.schemas import product as product_schema
from app.services.audit import log_action
from app.services.crud_base import CRUDBase

router = APIRouter(prefix="/produtos", tags=["produtos"])
product_crud = CRUDBase[Product, product_schema.ProductCreate, product_schema.ProductCreate](Product)


@router.get("/", response_model=list[product_schema.Product])
async def listar_produtos(
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "VENDEDOR"])),
):
    return await product_crud.get_multi(session)


@router.post("/", response_model=product_schema.Product, status_code=status.HTTP_201_CREATED)
async def criar_produto(
    payload: product_schema.ProductCreate,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(authorize(roles=["GERENTE"])),
):
    product = await product_crud.create(session, payload)
    await log_action(session, current_user, "create_product", "Product", product.id, payload.dict())
    return product


@router.get("/{product_id}", response_model=product_schema.Product)
async def obter_produto(
    product_id: int,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(authorize(roles=["GERENTE", "VENDEDOR"])),
):
    product = await product_crud.get(session, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product
