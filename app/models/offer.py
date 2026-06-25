from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    Boolean,
    ForeignKey
)
from app.db.base import Base

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True)

    business_id = Column(Integer, ForeignKey("businesses.id"))

    title = Column(String(255))

    description = Column(Text)

    start_date = Column(Date)

    end_date = Column(Date)

    is_active = Column(Boolean, default=True)