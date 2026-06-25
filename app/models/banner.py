from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True)

    image_url = Column(String(500))

    redirect_url = Column(String(500))

    is_active = Column(Boolean, default=True)