from app.api.skills import SKILLS
import sqlite3
from datetime import datetime
from typing import List
from app.models.schemas import Message
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件

DB_PATH = "/tmp/chat_history.db"


def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


init_db()


class ChatService:
    def __init__(self):
        self.api_key = os.getenv("MINIMAX_API_KEY", os.getenv("OPENAI_API_KEY", ""))
        self.base_url = "https://api.minimax.chat/v1"
        self.model = "MiniMax-M2.5"
    
    def _call_minimax(self, messages: list) -> str:
        """调用 MiniMax API"""
        url = f"{self.base_url}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"MiniMax API error: {response.status_code} - {response.text}")
        result = response.json()
        if "choices" not in result:
            raise Exception(f"MiniMax response missing choices: {result}")
        return result["choices"][0]["message"]["content"]
    
    async def get_reply(self, session_id: str, message: str, skill_id: str = None) -> str:
        """获取 AI 回复"""
        # 获取技能配置
        skill = SKILLS.get(skill_id or "general", SKILLS["general"])
        
        # 构建系统提示
        system_prompt = skill["prompt"]
        
        # 获取历史记录
        history = self.get_history_sync(session_id)
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": message})
        
        # 调用 LLM
        reply = self._call_minimax(messages)
        
        # 保存到数据库
        self.save_message(session_id, "user", message)
        self.save_message(session_id, "assistant", reply)
        
        return reply
    
    def save_message(self, session_id: str, role: str, content: str):
        """保存消息"""
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (session_id, role, content, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    
    def get_history_sync(self, session_id: str) -> List[Message]:
        """获取历史消息（同步）"""
        conn = sqlite3.connect(DB_PATH)
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
    
    async def get_history(self, session_id: str) -> List[Message]:
        """获取历史消息"""
        return self.get_history_sync(session_id)
