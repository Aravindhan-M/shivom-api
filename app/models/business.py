from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime
)
from sqlalchemy.sql import func
from app.db.base import Base

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True)

    owner_id = Column(Integer, ForeignKey("users.id"))

    category_id = Column(Integer, ForeignKey("categories.id"))

    name = Column(String(255), nullable=False)

    description = Column(Text)

    address = Column(Text)

    city = Column(String(100))

    state = Column(String(100))

    latitude = Column(String(50))

    longitude = Column(String(50))

    phone = Column(String(20))

    email = Column(String(255))

    website = Column(String(255))

    logo = Column(String(255))

    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())