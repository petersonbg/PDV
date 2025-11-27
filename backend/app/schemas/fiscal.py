from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class FiscalDocument(BaseModel):
    id: int
    sale_id: int
    model: str
    status: str
    protocol: Optional[str]
    access_key: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class FiscalEvent(BaseModel):
    id: int
    document_id: int
    type: str
    status: str
    message: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class InvoiceItem(BaseModel):
    product_code: str = Field(..., description="Código interno ou GTIN do item")
    description: str
    quantity: Decimal
    unit_price: Decimal
    ncm: str = Field(..., min_length=4, max_length=8)
    cfop: str
    cst: str
    csosn: Optional[str] = None


class InvoiceRequest(BaseModel):
    sale_id: int
    items: list[InvoiceItem]
    environment: str = Field("homologacao", description="producao ou homologacao")
    use_contingency: bool = False
    contingency_reason: Optional[str] = None


class InvoiceResponse(BaseModel):
    success: bool
    message: str
    protocol: Optional[str]
    access_key: Optional[str]
    contingency: bool
    xml_preview: Optional[str] = None


class CancelRequest(BaseModel):
    access_key: str
    justification: str


class CancelResponse(BaseModel):
    success: bool
    message: str
    protocol: Optional[str]
    access_key: Optional[str]


class ContingencyStatus(BaseModel):
    reference: str
    queued_at: datetime
    reason: Optional[str]
