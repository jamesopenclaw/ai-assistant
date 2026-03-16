"""
Session 管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, Query
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

# Session 存储（按租户隔离）
# {tenant_id: {session_id: Session}}
TENANT_SESSIONS = {}


class SessionResponse(BaseModel):
    session_id: str
    name: str
    created_at: str
    updated_at: str
    message_count: int


class SessionCreate(BaseModel):
    name: Optional[str] = None


class SessionUpdate(BaseModel):
    name: Optional[str] = None


def get_tenant_sessions(tenant_id: int = 1):
    """获取租户的 session 存储"""
    if tenant_id not in TENANT_SESSIONS:
        TENANT_SESSIONS[tenant_id] = {}
    return TENANT_SESSIONS[tenant_id]


@router.get("", response_model=List[SessionResponse])
def list_sessions(
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """列出所有 Session（按租户隔离）"""
    sessions = get_tenant_sessions(tenant_id)
    return [
        SessionResponse(
            session_id=sid,
            name=data["name"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            message_count=data.get("message_count", 0)
        )
        for sid, data in sessions.items()
    ]


@router.post("", response_model=SessionResponse)
def create_session(
    request: SessionCreate = SessionCreate(),
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """创建新 Session"""
    sessions = get_tenant_sessions(tenant_id)
    
    session_id = f"session-{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    
    sessions[session_id] = {
        "name": request.name or f"新会话 {len(sessions) + 1}",
        "created_at": now,
        "updated_at": now,
        "message_count": 0
    }
    
    return SessionResponse(
        session_id=session_id,
        name=sessions[session_id]["name"],
        created_at=now,
        updated_at=now,
        message_count=0
    )


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """获取指定 Session"""
    sessions = get_tenant_sessions(tenant_id)
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    data = sessions[session_id]
    return SessionResponse(
        session_id=session_id,
        name=data["name"],
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        message_count=data.get("message_count", 0)
    )


@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: str,
    request: SessionUpdate,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """重命名 Session"""
    sessions = get_tenant_sessions(tenant_id)
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if request.name:
        sessions[session_id]["name"] = request.name
    
    sessions[session_id]["updated_at"] = datetime.now().isoformat()
    
    data = sessions[session_id]
    return SessionResponse(
        session_id=session_id,
        name=data["name"],
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        message_count=data.get("message_count", 0)
    )


@router.delete("/{session_id}")
def delete_session(
    session_id: str,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """删除 Session"""
    sessions = get_tenant_sessions(tenant_id)
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    
    return {"message": "Deleted"}
