from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.utils.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
