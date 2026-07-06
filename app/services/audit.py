from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.audit_log import AuditLog

async def log_audit(
    db: AsyncSession,
    actor_sub: str,
    actor_role: str,
    action: str,
    target_type: str,
    target_id: str,
    metadata: Optional[dict] = None,
):
    audit = AuditLog(
        actor_sub=actor_sub,
        actor_role=actor_role,
        action=action,
        target_type=target_type,
        target_id=target_id,
        extra_data=metadata,
    )
    db.add(audit)
    await db.commit()