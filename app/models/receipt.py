from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    ForeignKey,
    DateTime
)
from sqlalchemy.sql import func
from app.db.base import Base

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    business_id = Column(Integer, ForeignKey("businesses.id"))

    receipt_image = Column(String(500))

    amount = Column(Numeric(10, 2))

    status = Column(String(50), default="pending")
    # pending | approved | rejected

    remarks = Column(String(500))

    created_at = Column(DateTime(timezone=True), server_default=func.now())