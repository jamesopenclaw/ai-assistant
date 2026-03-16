"""
用量统计模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from datetime import datetime, date
from app.utils.database import Base


class Usage(Base):
    __tablename__ = "usage_stats"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    token_count = Column(BigInteger, default=0)
    request_count = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
