from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.user import User


async def log_action(
    session: AsyncSession,
    user: User | None,
    action: str,
    entity: str,
    entity_id: int | None = None,
    payload: Any = None,
) -> None:
    audit_entry = AuditLog(
        action=action,
        entity=entity,
        entity_id=entity_id,
        payload=payload,
        user_id=user.id if user else None,
    )
    session.add(audit_entry)
    await session.commit()
