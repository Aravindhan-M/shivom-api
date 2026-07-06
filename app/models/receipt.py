import uuid
from sqlalchemy import Column, Date, Numeric, Enum, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from . import Base

class Receipt(Base):
    __tablename__ = "receipt"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_sub = Column(String, nullable=False)
    business_id = Column(UUID(as_uuid=True), ForeignKey("business.id"), nullable=False)
    amount = Column(Numeric, nullable=False)
    receipt_date = Column(Date, nullable=False)
    status = Column(Enum("pending", "approved", "rejected", name="receipt_status"), default="pending")
    remarks = Column(String, nullable=True)
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
