from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime
)
from sqlalchemy.sql import func
from app.db.base import Base

class RewardTransaction(Base):
    __tablename__ = "reward_transactions"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    receipt_id = Column(Integer, ForeignKey("receipts.id"))

    points = Column(Integer)

    transaction_type = Column(String(50))
    # earned | redeemed

    created_at = Column(DateTime(timezone=True), server_default=func.now())