from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime
)
from sqlalchemy.sql import func
from app.db.base import Base

class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True)

    referrer_id = Column(Integer, ForeignKey("users.id"))

    referred_user_id = Column(Integer, ForeignKey("users.id"))

    points_awarded = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())