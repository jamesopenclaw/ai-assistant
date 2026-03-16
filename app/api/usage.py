"""
用量统计 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.utils.database import get_db
from app.models.usage import Usage

router = APIRouter(prefix="/api/usage", tags=["usage"])


# Pydantic 模型
class UsageResponse(BaseModel):
    id: int
    tenant_id: int
    token_count: int
    request_count: int
    date: datetime
    
    class Config:
        from_attributes = True


class UsageSummary(BaseModel):
    tenant_id: int
    total_token_count: int
    total_request_count: int
    period_days: int


class UsageCreate(BaseModel):
    tenant_id: int
    token_count: int = 0
    request_count: int = 1


# 依赖：获取当前租户
def get_current_tenant_id() -> int:
    """从 token 中提取 tenant_id，默认返回 1（向后兼容）"""
    return 1


@router.post("", response_model=UsageResponse)
def create_usage_record(
    request: UsageCreate,
    db: Session = Depends(get_db)
):
    """记录用量（内部使用）"""
    # 查找今天是否已有记录
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    existing = db.query(Usage).filter(
        Usage.tenant_id == request.tenant_id,
        Usage.date >= today_start,
        Usage.date < today_end
    ).first()
    
    if existing:
        # 更新已有记录
        existing.token_count += request.token_count
        existing.request_count += request.request_count
        db.commit()
        db.refresh(existing)
        return UsageResponse(
            id=existing.id,
            tenant_id=existing.tenant_id,
            token_count=existing.token_count,
            request_count=existing.request_count,
            date=existing.date
        )
    
    # 创建新记录
    usage = Usage(
        tenant_id=request.tenant_id,
        token_count=request.token_count,
        request_count=request.request_count
    )
    db.add(usage)
    db.commit()
    db.refresh(usage)
    
    return UsageResponse(
        id=usage.id,
        tenant_id=usage.tenant_id,
        token_count=usage.token_count,
        request_count=usage.request_count,
        date=usage.date
    )


@router.get("", response_model=UsageSummary)
def get_usage(
    days: int = Query(7, ge=1, le=90, description="查询天数"),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id)
):
    """获取租户用量统计"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 聚合统计
    from sqlalchemy import func
    result = db.query(
        func.sum(Usage.token_count).label("total_tokens"),
        func.sum(Usage.request_count).label("total_requests")
    ).filter(
        Usage.tenant_id == tenant_id,
        Usage.date >= start_date
    ).first()
    
    return UsageSummary(
        tenant_id=tenant_id,
        total_token_count=result.total_tokens or 0,
        total_request_count=result.total_requests or 0,
        period_days=days
    )


@router.get("/daily", response_model=List[UsageResponse])
def get_daily_usage(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id)
):
    """获取每日用量详情"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    records = db.query(Usage).filter(
        Usage.tenant_id == tenant_id,
        Usage.date >= start_date
    ).order_by(Usage.date.desc()).all()
    
    return [
        UsageResponse(
            id=r.id,
            tenant_id=r.tenant_id,
            token_count=r.token_count,
            request_count=r.request_count,
            date=r.date
        )
        for r in records
    ]
