from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class SaleItemBase(BaseModel):
    product_id: int
    quantity: float
    unit_price: float


class SaleItem(SaleItemBase):
    id: int
    total_price: float

    class Config:
        orm_mode = True


class PaymentBase(BaseModel):
    method: str
    amount: float


class Payment(PaymentBase):
    id: int
    transaction_code: Optional[str] = None
    paid: bool

    class Config:
        orm_mode = True


class SaleBase(BaseModel):
    customer_id: Optional[int] = None
    discount: float = 0


class SaleCreate(SaleBase):
    items: List[SaleItemBase]
    payments: List[PaymentBase]


class Sale(SaleBase):
    id: int
    code: str
    status: str
    total: float
    created_at: datetime
    items: List[SaleItem]
    payments: List[Payment]

    class Config:
        orm_mode = True
