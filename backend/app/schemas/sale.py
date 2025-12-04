from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class SaleItemBase(BaseModel):
    product_id: int
    quantity: float
    unit_price: float


class SaleItem(SaleItemBase):
    id: int
    total_price: float

    model_config = ConfigDict(from_attributes=True)


class PaymentBase(BaseModel):
    method: str
    amount: float


class Payment(PaymentBase):
    id: int
    transaction_code: Optional[str] = None
    paid: bool

    model_config = ConfigDict(from_attributes=True)


class SaleBase(BaseModel):
    customer_id: Optional[int] = None
    discount: float = 0


class SaleCreate(SaleBase):
    items: List[SaleItemBase]
    payments: List[PaymentBase]


class SaleStart(SaleBase):
    cash_register_id: Optional[int] = None


class SaleAddItem(BaseModel):
    sale_id: int
    product_id: int
    quantity: float
    unit_price: Optional[float] = None


class SaleFinalize(BaseModel):
    sale_id: int
    payments: List[PaymentBase]
    discount: float = 0
    cash_register_id: Optional[int] = None


class SaleCancel(BaseModel):
    sale_id: int
    reason: Optional[str] = None
    restock: bool = True


class Sale(SaleBase):
    id: int
    code: str
    status: str
    total: float
    created_at: datetime
    items: List[SaleItem]
    payments: List[Payment]

    model_config = ConfigDict(from_attributes=True)


class SaleWorkflowResult(BaseModel):
    sale: Sale
    receipt: Optional[str] = None
    cash_control: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)
