import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from . import Base

class Reward(Base):
    __tablename__ = "reward"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_sub = Column(String, nullable=False)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipt.id"), nullable=True)
    points = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
