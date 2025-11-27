from datetime import datetime
from typing import Optional
from pydantic import BaseModel


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
