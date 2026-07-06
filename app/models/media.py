import uuid
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from . import Base

class BusinessMedia(Base):
    __tablename__ = "business_media"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("business.id"), nullable=False)
    media_type = Column(Enum("logo", "cover_photo", "gallery_image", "video", name="media_type"), nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_by = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
