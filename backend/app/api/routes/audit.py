from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_active_user, get_db
from app.models.audit import AuditLog
from app.schemas import audit as audit_schema

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/", response_model=list[audit_schema.AuditLog])
async def list_logs(
    session: AsyncSession = Depends(get_db), user=Depends(get_active_user)
):
    result = await session.execute(select(AuditLog).order_by(AuditLog.created_at.desc()))
    return result.scalars().all()
