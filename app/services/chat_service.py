from app.api.skills import SKILLS
from app.services.knowledge_service import KnowledgeService
import sqlite3
from datetime import datetime
from typing import List
from app.models.schemas import Message
import os
import asyncio
import httpx
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal
from app.models.usage import Usage
from sqlalchemy import func

load_dotenv()

DB_PATH = os.getenv("CHAT_DB_PATH", "/tmp/chat_history.db")

# 初始化知识库服务
knowledge_service = KnowledgeService()


def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    
    # 检查表是否存在
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
    table_exists = cursor.fetchone() is not None
    
    if not table_exists:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                tenant_id INTEGER DEFAULT 1,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
    else:
        # 检查 tenant_id 列是否存在，不存在则添加
        cursor = conn.execute("PRAGMA table_info(messages)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'tenant_id' not in columns:
            conn.execute("ALTER TABLE messages ADD COLUMN tenant_id INTEGER DEFAULT 1")
    
    # 添加索引优化查询
    conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON messages(session_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tenant ON messages(tenant_id)")
    conn.commit()
    conn.close()


init_db()


def _estimate_tokens(text: str) -> int:
    """简单估算 token 数量（中英文混合）"""
    # 粗略估算：中文约 1.5 字符/token，英文约 4 字符/token
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    other_chars = len(text) - chinese_chars
    return int(chinese_chars / 1.5 + other_chars / 4)


class ChatService:
    def __init__(self):
        self.api_key = os.getenv("MINIMAX_API_KEY", os.getenv("OPENAI_API_KEY", ""))
        self.base_url = "https://api.minimax.chat/v1"
        self.model = "MiniMax-M2.5"
        # 复用 httpx 客户端
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client
    
    async def _call_minimax(self, messages: list) -> str:
        """调用 MiniMax API (异步)"""
        client = self._get_client()
        url = f"{self.base_url}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages
        }
        
        try:
            response = await client.post(url, json=payload, headers=headers)
        except httpx.TimeoutException:
            raise Exception("MiniMax API 超时")
        
        if response.status_code != 200:
            raise Exception(f"MiniMax API error: {response.status_code}")
        
        result = response.json()
        if "choices" not in result:
            raise Exception(f"MiniMax response missing choices")
        return result["choices"][0]["message"]["content"]
    
    async def _record_usage(self, tenant_id: int, token_count: int):
        """记录用量统计"""
        try:
            db = SessionLocal()
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + __import__('datetime').timedelta(days=1)
            
            # 查找今天是否已有记录
            existing = db.query(Usage).filter(
                Usage.tenant_id == tenant_id,
                Usage.date >= today_start,
                Usage.date < today_end
            ).first()
            
            if existing:
                existing.token_count += token_count
                existing.request_count += 1
            else:
                usage = Usage(
                    tenant_id=tenant_id,
                    token_count=token_count,
                    request_count=1
                )
                db.add(usage)
            
            db.commit()
            db.close()
        except Exception as e:
            print(f"记录用量失败: {e}")
    
    async def get_reply(self, session_id: str, message: str, skill_id: str = None, tenant_id: int = 1) -> str:
        """获取 AI 回复
        
        Args:
            session_id: 会话 ID
            message: 用户消息
            skill_id: 技能 ID
            tenant_id: 租户 ID（默认 1 向后兼容）
        """
        skill = SKILLS.get(skill_id or "general", SKILLS["general"])
        system_prompt = skill["prompt"]
        
        # 如果是知识库技能，先检索相关内容
        if skill_id == "knowledge":
            try:
                docs = await knowledge_service.search(message, k=3)
                if docs:
                    context = "\n\n".join([f"[参考{i+1}] {doc}" for i, doc in enumerate(docs)])
                    system_prompt = f"""你是一个基于企业知识库回答问题的AI助手。

参考知识：
{context}

请根据以上知识回答用户的问题。如果知识库中没有相关信息，请如实说明并基于你的理解回答。"""
            except Exception as e:
                print(f"知识库检索失败: {e}")
        
        # 获取历史
        history = await self.get_history(session_id)
        
        # 构建消息
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": message})
        
        # 估算 token 用量
        total_content = system_prompt + message + "".join([m.content for m in history])
        estimated_tokens = _estimate_tokens(total_content)
        
        # 调用 API
        reply = await self._call_minimax(messages)
        
        # 加上回复的 token
        estimated_tokens += _estimate_tokens(reply)
        
        # 异步记录用量
        asyncio.create_task(self._record_usage(tenant_id, estimated_tokens))
        
        # 保存消息（非阻塞）
        asyncio.create_task(self.save_message_async(session_id, "user", message, tenant_id))
        asyncio.create_task(self.save_message_async(session_id, "assistant", reply, tenant_id))
        
        return reply
    
    async def save_message_async(self, session_id: str, role: str, content: str, tenant_id: int = 1):
        """异步保存消息"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._save_message, session_id, role, content, tenant_id)
    
    def _save_message(self, session_id: str, role: str, content: str, tenant_id: int = 1):
        """保存消息"""
        try:
            conn = sqlite3.connect(DB_PATH, timeout=5.0)
            conn.execute(
                "INSERT INTO messages (session_id, tenant_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
                (session_id, tenant_id, role, content, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Save message error: {e}")
    
    async def get_history(self, session_id: str) -> List[Message]:
        """获取历史消息"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_history, session_id)
    
    def _get_history(self, session_id: str) -> List[Message]:
        """获取历史消息"""
        conn = sqlite3.connect(DB_PATH, timeout=5.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY id",
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            Message(role=row["role"], content=row["content"], timestamp=row["timestamp"])
            for row in rows
        ]
