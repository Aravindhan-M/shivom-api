import uuid
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from . import Base

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_sub = Column(String, nullable=False)
    actor_role = Column(String, nullable=True)
    action = Column(String, nullable=False)
    target_type = Column(String, nullable=True)
    target_id = Column(String, nullable=True)
    extra_data = Column("metadata", JSON, nullable=True)   # renamed attribute, DB column stays "metadata"
    created_at = Column(DateTime, default=datetime.utcnow)