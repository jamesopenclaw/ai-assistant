"""
用户管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/users", tags=["users"])

# 用户存储（按租户隔离）
# {tenant_id: {user_id: User}}
TENANT_USERS = {}


class UserRole:
    """用户角色常量"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: Optional[str]
    role: str
    tenant_id: int
    created_at: str
    last_login: Optional[str]


class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    role: str = "user"


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


def get_tenant_users(tenant_id: int):
    """获取租户的用户列表"""
    if tenant_id not in TENANT_USERS:
        TENANT_USERS[tenant_id] = {}
    return TENANT_USERS[tenant_id]


@router.get("", response_model=List[UserResponse])
def list_users(
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """获取租户内用户列表"""
    users = get_tenant_users(tenant_id)
    return [
        UserResponse(
            user_id=uid,
            username=u["username"],
            email=u.get("email"),
            role=u.get("role", "user"),
            tenant_id=tenant_id,
            created_at=u.get("created_at", ""),
            last_login=u.get("last_login")
        )
        for uid, u in users.items()
    ]


@router.post("", response_model=UserResponse)
def create_user(
    request: UserCreate,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """创建用户（租户内）"""
    users = get_tenant_users(tenant_id)
    
    # 检查用户名是否已存在
    for u in users.values():
        if u["username"] == request.username:
            raise HTTPException(status_code=400, detail="用户名已存在")
    
    user_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    
    users[user_id] = {
        "username": request.username,
        "email": request.email,
        "password": request.password,  # 生产环境应该 hash
        "role": request.role,
        "status": "active",
        "created_at": now,
        "last_login": None
    }
    
    return UserResponse(
        user_id=user_id,
        username=request.username,
        email=request.email,
        role=request.role,
        tenant_id=tenant_id,
        created_at=now,
        last_login=None
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """获取指定用户"""
    users = get_tenant_users(tenant_id)
    
    if user_id not in users:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    u = users[user_id]
    return UserResponse(
        user_id=user_id,
        username=u["username"],
        email=u.get("email"),
        role=u.get("role", "user"),
        tenant_id=tenant_id,
        created_at=u.get("created_at", ""),
        last_login=u.get("last_login")
    )


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    request: UserUpdate,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """更新用户信息"""
    users = get_tenant_users(tenant_id)
    
    if user_id not in users:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    u = users[user_id]
    
    if request.username:
        u["username"] = request.username
    if request.email:
        u["email"] = request.email
    if request.role:
        u["role"] = request.role
    if request.status:
        u["status"] = request.status
    
    return UserResponse(
        user_id=user_id,
        username=u["username"],
        email=u.get("email"),
        role=u.get("role", "user"),
        tenant_id=tenant_id,
        created_at=u.get("created_at", ""),
        last_login=u.get("last_login")
    )


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """删除用户"""
    users = get_tenant_users(tenant_id)
    
    if user_id not in users:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不能删除自己
    if users[user_id].get("is_self"):
        raise HTTPException(status_code=400, detail="不能删除当前用户")
    
    del users[user_id]
    return {"message": "删除成功"}


@router.post("/{user_id}/login")
def user_login(
    user_id: str,
    password: str,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """用户登录验证"""
    users = get_tenant_users(tenant_id)
    
    if user_id not in users:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    u = users[user_id]
    
    if u.get("password") != password:
        raise HTTPException(status_code=401, detail="密码错误")
    
    if u.get("status") == "disabled":
        raise HTTPException(status_code=403, detail="账号已被禁用")
    
    # 更新最后登录时间
    u["last_login"] = datetime.now().isoformat()
    
    return {
        "user_id": user_id,
        "username": u["username"],
        "role": u.get("role", "user"),
        "message": "登录成功"
    }
