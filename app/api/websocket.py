"""
WebSocket 实时对话服务
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import asyncio

router = APIRouter()

# 连接管理
class ConnectionManager:
    def __init__(self):
        # 活跃连接: {session_id: {websocket}}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # 会话上下文: {session_id: [messages]}
        self.session_contexts: Dict[str, list] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """客户端连接"""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
            self.session_contexts[session_id] = []
        self.active_connections[session_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """客户端断开"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
    
    async def send_message(self, message: str, session_id: str):
        """发送消息到指定会话的所有客户端"""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(message)
                except:
                    pass
    
    async def broadcast(self, message: str):
        """广播消息到所有客户端"""
        for session_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(message)
                except:
                    pass
    
    def add_context(self, session_id: str, role: str, content: str):
        """添加消息到会话上下文"""
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = []
        self.session_contexts[session_id].append({
            "role": role,
            "content": content
        })
        # 保留最近20条上下文
        if len(self.session_contexts[session_id]) > 20:
            self.session_contexts[session_id] = self.session_contexts[session_id][-20:]
    
    def get_context(self, session_id: str) -> list:
        """获取会话上下文"""
        return self.session_contexts.get(session_id, [])


manager = ConnectionManager()


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str, token: str = None):
    """
    WebSocket 实时对话
    
    连接: ws://host:port/api/ws/chat/{session_id}?token=xxx
    
    消息格式:
    - 发送: {"type": "message", "content": "你好"}
    - 接收: {"type": "message", "role": "assistant", "content": "回复内容"}
    """
    await manager.connect(websocket, session_id)
    
    try:
        # 发送连接成功消息
        await websocket.send_text(json.dumps({
            "type": "connected",
            "session_id": session_id
        }))
        
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": "无效的JSON格式"
                }))
                continue
            
            msg_type = message_data.get("type")
            
            if msg_type == "message":
                content = message_data.get("content", "").strip()
                if not content:
                    continue
                
                # 添加用户消息到上下文
                manager.add_context(session_id, "user", content)
                
                # 发送"正在输入"状态
                await websocket.send_text(json.dumps({
                    "type": "status",
                    "content": "thinking"
                }))
                
                # 调用 AI 对话服务
                from app.services.chat_service import ChatService
                chat_service = ChatService()
                
                try:
                    # 同步调用改为异步
                    reply = await chat_service.get_reply(
                        session_id=session_id,
                        message=content,
                        skill_id="general",
                        tenant_id=1
                    )
                    
                    # 添加 AI 回复到上下文
                    manager.add_context(session_id, "assistant", reply)
                    
                    # 发送 AI 回复
                    await websocket.send_text(json.dumps({
                        "type": "message",
                        "role": "assistant",
                        "content": reply
                    }))
                    
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "content": f"AI 回复失败: {str(e)}"
                    }))
            
            elif msg_type == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong"
                }))
            
            elif msg_type == "clear":
                # 清除会话上下文
                manager.session_contexts[session_id] = []
                await websocket.send_text(json.dumps({
                    "type": "status",
                    "content": "context_cleared"
                }))
            
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": f"未知消息类型: {msg_type}"
                }))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        print(f"WebSocket 错误: {e}")
        manager.disconnect(websocket, session_id)


@router.websocket("/ws/broadcast")
async def websocket_broadcast(websocket: WebSocket):
    """WebSocket 广播（用于系统通知）"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "broadcast":
                await manager.broadcast(json.dumps(message_data))
    
    except WebSocketDisconnect:
        pass


@router.get("/ws/status")
async def ws_status():
    """获取 WebSocket 状态"""
    return {
        "active_sessions": len(manager.active_connections),
        "total_connections": sum(len(conns) for conns in manager.active_connections.values())
    }
