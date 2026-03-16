"""
租户管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from app.utils.database import get_db, engine, Base
from app.models.tenant import Tenant, TenantStatus, TenantPlan

router = APIRouter(prefix="/api/tenants", tags=["tenants"])


# Pydantic 模型
class TenantResponse(BaseModel):
    id: int
    name: str
    plan: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TenantCreate(BaseModel):
    name: str
    plan: str = "free"


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    plan: Optional[str] = None
    status: Optional[str] = None


# 依赖：获取当前租户
def get_current_tenant_id(authorization: Optional[str] = Header(None)) -> int:
    """从 token 中提取 tenant_id，默认返回 1（向后兼容）"""
    # TODO: 实际实现时从 JWT token 中解析 tenant_id
    # 当前简单实现：检查特定 header 或默认 tenant_id=1
    return 1


# 创建表（首次运行时）
Base.metadata.create_all(bind=engine)


@router.post("", response_model=TenantResponse)
def create_tenant(
    request: TenantCreate,
    db: Session = Depends(get_db)
):
    """创建新租户"""
    tenant = Tenant(
        name=request.name,
        plan=TenantPlan(request.plan),
        status=TenantStatus.ACTIVE
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        plan=tenant.plan.value,
        status=tenant.status.value,
        created_at=tenant.created_at
    )


@router.get("", response_model=List[TenantResponse])
def list_tenants(
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id)
):
    """租户列表（管理员用）"""
    tenants = db.query(Tenant).all()
    return [
        TenantResponse(
            id=t.id,
            name=t.name,
            plan=t.plan.value,
            status=t.status.value,
            created_at=t.created_at
        )
        for t in tenants
    ]


@router.get("/me", response_model=TenantResponse)
def get_my_tenant(
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id)
):
    """获取当前租户信息"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        # 如果租户不存在，返回默认租户
        return TenantResponse(
            id=1,
            name="Default Tenant",
            plan="free",
            status="active",
            created_at=datetime.utcnow()
        )
    
    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        plan=tenant.plan.value,
        status=tenant.status.value,
        created_at=tenant.created_at
    )


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db)
):
    """获取指定租户信息"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    
    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        plan=tenant.plan.value,
        status=tenant.status.value,
        created_at=tenant.created_at
    )


@router.patch("/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: int,
    request: TenantUpdate,
    db: Session = Depends(get_db),
    current_tenant_id: int = Depends(get_current_tenant_id)
):
    """更新租户信息"""
    if tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="无权操作")
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")
    
    if request.name:
        tenant.name = request.name
    if request.plan:
        tenant.plan = TenantPlan(request.plan)
    if request.status:
        tenant.status = TenantStatus(request.status)
    
    db.commit()
    db.refresh(tenant)
    
    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        plan=tenant.plan.value,
        status=tenant.status.value,
        created_at=tenant.created_at
    )
