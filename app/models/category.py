from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from datetime import datetime

from . import Base

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    icon_url = Column(String, nullable=True)
    parent_id = Column(Integer, ForeignKey("category.id"), nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
