from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class AuditLog(BaseModel):
    id: int
    action: str
    entity: str
    entity_id: Optional[int]
    payload: Optional[Any]
    created_at: datetime
    user_id: Optional[int]

    class Config:
        orm_mode = True
