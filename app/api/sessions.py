"""
Session 管理 API - 增强版

支持：置顶/标记/搜索/导出
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, Query
from pydantic import BaseModel
from datetime import datetime
import uuid
import json

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

# Session 存储（按租户隔离）
# {tenant_id: {session_id: Session}}
TENANT_SESSIONS = {}

# 消息存储（按 session_id）
# {session_id: [messages]}
SESSION_MESSAGES = {}


class SessionResponse(BaseModel):
    session_id: str
    name: str
    created_at: str
    updated_at: str
    message_count: int
    is_pinned: bool = False
    is_starred: bool = False
    tags: List[str] = []


class SessionCreate(BaseModel):
    name: Optional[str] = None


class SessionUpdate(BaseModel):
    name: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_starred: Optional[bool] = None
    tags: Optional[List[str]] = None


class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


def get_tenant_sessions(tenant_id: int = 1):
    """获取租户的 session 存储"""
    if tenant_id not in TENANT_SESSIONS:
        TENANT_SESSIONS[tenant_id] = {}
    return TENANT_SESSIONS[tenant_id]


def get_session_messages(session_id: str) -> List[dict]:
    """获取会话的消息"""
    return SESSION_MESSAGES.get(session_id, [])


def save_session_message(session_id: str, role: str, content: str):
    """保存消息到会话"""
    if session_id not in SESSION_MESSAGES:
        SESSION_MESSAGES[session_id] = []
    SESSION_MESSAGES[session_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })


# ============ Session API ============

@router.get("", response_model=List[SessionResponse])
def list_sessions(
    tenant_id: int = Header(1, alias="X-Tenant-ID"),
    search: Optional[str] = Query(None, description="搜索会话名称"),
    pinned_only: bool = Query(False, description="仅返回置顶会话"),
    starred_only: bool = Query(False, description="仅返回星标会话"),
):
    """列出所有 Session（按租户隔离）"""
    sessions = get_tenant_sessions(tenant_id)
    result = []
    
    for sid, data in sessions.items():
        # 搜索过滤
        if search and search.lower() not in data.get("name", "").lower():
            continue
        # 置顶过滤
        if pinned_only and not data.get("is_pinned", False):
            continue
        # 星标过滤
        if starred_only and not data.get("is_starred", False):
            continue
        
        result.append(SessionResponse(
            session_id=sid,
            name=data["name"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            message_count=data.get("message_count", 0),
            is_pinned=data.get("is_pinned", False),
            is_starred=data.get("is_starred", False),
            tags=data.get("tags", [])
        ))
    
    # 置顶的排前面
    result.sort(key=lambda x: (not x.is_pinned, x.updated_at), reverse=True)
    
    return result


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
        "message_count": 0,
        "is_pinned": False,
        "is_starred": False,
        "tags": []
    }
    
    # 初始化消息存储
    SESSION_MESSAGES[session_id] = []
    
    return SessionResponse(
        session_id=session_id,
        name=sessions[session_id]["name"],
        created_at=now,
        updated_at=now,
        message_count=0,
        is_pinned=False,
        is_starred=False,
        tags=[]
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
        message_count=data.get("message_count", 0),
        is_pinned=data.get("is_pinned", False),
        is_starred=data.get("is_starred", False),
        tags=data.get("tags", [])
    )


@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: str,
    request: SessionUpdate,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """更新 Session（置顶/标记/重命名）"""
    sessions = get_tenant_sessions(tenant_id)
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    s = sessions[session_id]
    
    if request.name is not None:
        s["name"] = request.name
    if request.is_pinned is not None:
        s["is_pinned"] = request.is_pinned
    if request.is_starred is not None:
        s["is_starred"] = request.is_starred
    if request.tags is not None:
        s["tags"] = request.tags
    
    s["updated_at"] = datetime.now().isoformat()
    
    return SessionResponse(
        session_id=session_id,
        name=s["name"],
        created_at=s["created_at"],
        updated_at=s["updated_at"],
        message_count=s.get("message_count", 0),
        is_pinned=s.get("is_pinned", False),
        is_starred=s.get("is_starred", False),
        tags=s.get("tags", [])
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
    
    # 同时删除消息
    if session_id in SESSION_MESSAGES:
        del SESSION_MESSAGES[session_id]
    
    return {"message": "Deleted"}


@router.post("/{session_id}/pin")
def pin_session(
    session_id: str,
    pinned: bool = True,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """置顶/取消置顶会话"""
    sessions = get_tenant_sessions(tenant_id)
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions[session_id]["is_pinned"] = pinned
    sessions[session_id]["updated_at"] = datetime.now().isoformat()
    
    return {"session_id": session_id, "is_pinned": pinned}


@router.post("/{session_id}/star")
def star_session(
    session_id: str,
    starred: bool = True,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """星标/取消星标会话"""
    sessions = get_tenant_sessions(tenant_id)
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions[session_id]["is_starred"] = starred
    sessions[session_id]["updated_at"] = datetime.now().isoformat()
    
    return {"session_id": session_id, "is_starred": starred}


# ============ 消息 API ============

@router.get("/{session_id}/messages", response_model=List[MessageResponse])
def get_session_messages_api(
    session_id: str,
    tenant_id: int = Header(1, alias="X-Tenant-ID"),
    limit: int = Query(100, ge=1, le=500)
):
    """获取会话消息历史"""
    sessions = get_tenant_sessions(tenant_id)
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = get_session_messages(session_id)[-limit:]
    
    return [
        MessageResponse(role=m["role"], content=m["content"], timestamp=m["timestamp"])
        for m in messages
    ]


@router.post("/{session_id}/messages")
def add_session_message(
    session_id: str,
    request: MessageResponse,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """添加消息到会话"""
    sessions = get_tenant_sessions(tenant_id)
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    save_session_message(session_id, request.role, request.content or "")
    
    # 更新消息计数
    sessions[session_id]["message_count"] = len(SESSION_MESSAGES.get(session_id, []))
    sessions[session_id]["updated_at"] = datetime.now().isoformat()
    
    return {"message": "Saved"}
    
    # 更新消息计数
    sessions[session_id]["message_count"] = len(SESSION_MESSAGES.get(session_id, []))
    sessions[session_id]["updated_at"] = datetime.now().isoformat()
    
    return {"message": "Saved"}


# ============ 导出 API ============

@router.get("/{session_id}/export")
def export_session(
    session_id: str,
    format: str = Query("json", regex="^(json|markdown|text)$"),
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """导出会话记录"""
    sessions = get_tenant_sessions(tenant_id)
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    s = sessions[session_id]
    messages = get_session_messages(session_id)
    
    if format == "json":
        return {
            "session": {
                "name": s["name"],
                "created_at": s["created_at"],
                "message_count": len(messages)
            },
            "messages": messages
        }
    
    elif format == "markdown":
        md = f"# {s['name']}\n\n"
        md += f"- 创建时间: {s['created_at']}\n"
        md += f"- 消息数: {len(messages)}\n\n---\n\n"
        
        for m in messages:
            role_emoji = "👤" if m["role"] == "user" else "🤖"
            md += f"### {role_emoji} {m['role']}\n\n"
            md += f"{m['content']}\n\n"
            md += f"_{m['timestamp']}_\n\n---\n\n"
        
        return md
    
    else:  # text
        text = f"{s['name']}\n"
        text += f"{'=' * 40}\n\n"
        
        for m in messages:
            text += f"[{m['role']}] {m['content']}\n"
            text += f"  -- {m['timestamp']}\n\n"
        
        return text
