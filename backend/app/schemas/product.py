from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    price: float
    cost: float
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class StockItem(BaseModel):
    id: int
    product_id: int
    location_id: int
    quantity: float

    class Config:
        orm_mode = True
