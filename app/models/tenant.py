"""
租户模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from datetime import datetime
from app.utils.database import Base
import enum


class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class TenantPlan(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    plan = Column(SQLEnum(TenantPlan), default=TenantPlan.FREE)
    status = Column(SQLEnum(TenantStatus), default=TenantStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
