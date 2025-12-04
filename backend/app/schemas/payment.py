from typing import Optional

from pydantic import BaseModel, ConfigDict


class PaymentIntegrationRequest(BaseModel):
    sale_id: int
    amount: float


class PaymentIntegrationResponse(BaseModel):
    method: str
    transaction_code: str
    status: str
    message: str
    qr_code: Optional[str] = None
    copy_paste: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaymentConfirmation(BaseModel):
    transaction_code: str
    approved: bool = True
    nsu: Optional[str] = None

