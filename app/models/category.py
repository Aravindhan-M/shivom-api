from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)

    name = Column(String(100), nullable=False)

    slug = Column(String(100), unique=True)

    icon = Column(String(255))

    is_active = Column(Boolean, default=True)