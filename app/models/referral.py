import uuid
from sqlalchemy import Column, String, Integer, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from . import Base

class Referral(Base):
    __tablename__ = "referral"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_sub = Column(String, nullable=False)
    referred_sub = Column(String, nullable=True)
    referral_code = Column(String, unique=True, nullable=False)
    status = Column(Enum("invited", "joined", "first_submission_done", name="referral_status"), default="invited")
    points_awarded = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
