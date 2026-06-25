from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    keycloak_id = Column(String(255), unique=True)

    full_name = Column(String(255))

    email = Column(String(255), unique=True)

    phone = Column(String(20), unique=True)

    role = Column(String(50), default="customer")
    # customer | business | admin

    referral_code = Column(String(20), unique=True)

    referred_by = Column(Integer, nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())