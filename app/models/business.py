import uuid
from sqlalchemy import Column, String, Float, Enum, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from . import Base

class Business(Base):
    __tablename__ = "business"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_sub = Column(String, ForeignKey("user_profile.keycloak_sub"), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    business_name = Column(String, nullable=False)
    short_description = Column(String(150), nullable=True)
    detailed_description = Column(String(1000), nullable=True)
    mobile_number = Column(String, nullable=False)
    email = Column(String, nullable=True)
    landline_number = Column(String, nullable=True)
    website = Column(String, nullable=True)
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    pincode = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    business_timings = Column(String, nullable=True)
    status = Column(Enum("pending", "approved", "rejected", "suspended", name="business_status"), default="pending")
    rejection_reason = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
