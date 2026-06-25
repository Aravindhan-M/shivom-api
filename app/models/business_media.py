from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base

class BusinessMedia(Base):
    __tablename__ = "business_media"

    id = Column(Integer, primary_key=True)

    business_id = Column(Integer, ForeignKey("businesses.id"))

    media_url = Column(String(500))

    media_type = Column(String(20))
    # image | video