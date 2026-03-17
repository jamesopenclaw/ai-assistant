"""
客服切换 API

支持 AI 客服和人工客服切换
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
import uuid
import os

router = APIRouter(prefix="/api/customer-service", tags=["customer-service"])

# 客服状态存储（按租户）
# {tenant_id: {session_id: {status, agent_id, assigned_at}}}
CS_SESSIONS = {}

# 在线客服列表
# {tenant_id: [Agent]}
ONLINE_AGENTS = {}


class Agent(BaseModel):
    agent_id: str
    name: str
    status: str = "online"  # online, busy, offline
    tenant_id: int
    last_active: str


class SessionStatus(BaseModel):
    session_id: str
    mode: str = "ai"  # ai, human
    agent_id: Optional[str] = None
    assigned_at: Optional[str] = None
    waiting_since: Optional[str] = None


class TransferRequest(BaseModel):
    session_id: str
    target_agent_id: Optional[str] = None  # 指定客服，不指定则分配


class MessageRequest(BaseModel):
    session_id: str
    content: str


def get_tenant_cs(tenant_id: int):
    """获取租户的客服状态"""
    if tenant_id not in CS_SESSIONS:
        CS_SESSIONS[tenant_id] = {}
    return CS_SESSIONS[tenant_id]


def get_online_agents(tenant_id: int) -> List[Agent]:
    """获取在线客服列表"""
    if tenant_id not in ONLINE_AGENTS:
        return []
    return [a for a in ONLINE_AGENTS[tenant_id] if a.status != "offline"]


def assign_agent(tenant_id: int) -> Optional[Agent]:
    """分配空闲客服"""
    agents = get_online_agents(tenant_id)
    for agent in agents:
        if agent.status == "online":
            return agent
    return None


# ============ 客服状态 API ============

@router.get("/status/{session_id}")
def get_session_status(
    session_id: str,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """获取会话当前客服状态"""
    cs = get_tenant_cs(tenant_id)
    
    if session_id not in cs:
        return SessionStatus(session_id=session_id, mode="ai")
    
    return SessionStatus(**cs[session_id])


@router.post("/transfer")
def transfer_to_human(
    request: TransferRequest,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """将会话从 AI 切换到人工客服"""
    cs = get_tenant_cs(tenant_id)
    session_id = request.session_id
    
    # 检查会话是否存在
    if session_id not in cs:
        cs[session_id] = {}
    
    if request.target_agent_id:
        # 指定客服
        agent = None
        if tenant_id in ONLINE_AGENTS:
            for a in ONLINE_AGENTS[tenant_id]:
                if a.agent_id == request.target_agent_id and a.status == "online":
                    agent = a
                    break
        
        if not agent:
            raise HTTPException(status_code=400, detail="指定客服不在线")
    else:
        # 自动分配空闲客服
        agent = assign_agent(tenant_id)
        if not agent:
            # 无空闲客服，加入等待队列
            cs[session_id] = {
                "session_id": session_id,
                "mode": "waiting",
                "waiting_since": datetime.now().isoformat()
            }
            return {
                "session_id": session_id,
                "mode": "waiting",
                "message": "当前无空闲客服，请稍候"
            }
    
    # 分配成功
    cs[session_id] = {
        "session_id": session_id,
        "mode": "human",
        "agent_id": agent.agent_id,
        "assigned_at": datetime.now().isoformat()
    }
    
    # 更新客服状态为忙碌
    agent.status = "busy"
    
    return {
        "session_id": session_id,
        "mode": "human",
        "agent_id": agent.agent_id,
        "agent_name": agent.name,
        "message": f"已转接到人工客服 {agent.name}"
    }


@router.post("/transfer-to-ai")
def transfer_to_ai(
    request: dict,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """将会话从人工切换回 AI"""
    session_id = request.get("session_id")
    cs = get_tenant_cs(tenant_id)
    
    if session_id not in cs:
        return {"message": "会话不在人工客服模式"}
    
    # 释放客服
    session = cs[session_id]
    if session.get("agent_id") and tenant_id in ONLINE_AGENTS:
        for a in ONLINE_AGENTS[tenant_id]:
            if a.agent_id == session["agent_id"]:
                a.status = "online"
                break
    
    # 切换回 AI
    cs[session_id] = {
        "session_id": session_id,
        "mode": "ai"
    }
    
    return {
        "session_id": session_id,
        "mode": "ai",
        "message": "已切换回 AI 客服"
    }


@router.post("/message")
def send_human_message(
    request: MessageRequest,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """发送人工客服消息"""
    session_id = request.session_id
    cs = get_tenant_cs(tenant_id)
    
    if session_id not in cs:
        raise HTTPException(status_code=400, detail="会话不存在或未转接人工")
    
    session = cs[session_id]
    if session.get("mode") != "human":
        raise HTTPException(status_code=400, detail="当前不是人工客服模式")
    
    # 这里应该发送到客服的消息系统
    # 简化实现：返回成功
    return {
        "session_id": session_id,
        "agent_id": session["agent_id"],
        "message": "消息已发送",
        "timestamp": datetime.now().isoformat()
    }


# ============ 客服管理 API ============

@router.get("/agents", response_model=List[Agent])
def list_agents(
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """获取在线客服列表"""
    return get_online_agents(tenant_id)


@router.post("/agents")
def register_agent(
    request: dict,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """客服上线（注册）"""
    name = request.get("name", "客服")
    
    if tenant_id not in ONLINE_AGENTS:
        ONLINE_AGENTS[tenant_id] = []
    
    agent_id = str(uuid.uuid4())[:8]
    agent = Agent(
        agent_id=agent_id,
        name=name,
        status="online",
        tenant_id=tenant_id,
        last_active=datetime.now().isoformat()
    )
    
    ONLINE_AGENTS[tenant_id].append(agent)
    
    return {
        "agent_id": agent_id,
        "name": name,
        "status": "online",
        "message": "客服已上线"
    }


@router.delete("/agents/{agent_id}")
def agent_offline(
    agent_id: str,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """客服下线"""
    if tenant_id not in ONLINE_AGENTS:
        raise HTTPException(status_code=404, detail="无在线客服")
    
    for i, a in enumerate(ONLINE_AGENTS[tenant_id]):
        if a.agent_id == agent_id:
            ONLINE_AGENTS[tenant_id].pop(i)
            
            # 释放该客服负责的会话
            cs = get_tenant_cs(tenant_id)
            for sid, session in cs.items():
                if session.get("agent_id") == agent_id:
                    cs[sid] = {"session_id": sid, "mode": "ai"}
            
            return {"message": "客服已下线"}
    
    raise HTTPException(status_code=404, detail="客服不存在")


@router.patch("/agents/{agent_id}")
def update_agent_status(
    agent_id: str,
    status: str,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """更新客服状态"""
    if tenant_id not in ONLINE_AGENTS:
        raise HTTPException(status_code=404, detail="无在线客服")
    
    for a in ONLINE_AGENTS[tenant_id]:
        if a.agent_id == agent_id:
            a.status = status
            a.last_active = datetime.now().isoformat()
            return {"agent_id": agent_id, "status": status}
    
    raise HTTPException(status_code=404, detail="客服不存在")
