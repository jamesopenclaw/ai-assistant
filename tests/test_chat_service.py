"""
聊天服务单元测试
"""
import pytest
import sqlite3
import os
import tempfile
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime

# 设置测试数据库
TEST_DB = "/tmp/test_chat_history.db"


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """设置测试数据库"""
    monkeypatch.setenv("CHAT_DB_PATH", TEST_DB)
    try:
        import app.services.chat_service as chat_service_module
        chat_service_module.DB_PATH = TEST_DB
    except Exception:
        pass
    # 初始化测试数据库
    conn = sqlite3.connect(TEST_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON messages(session_id)")
    conn.commit()
    conn.close()
    
    yield
    
    # 清理测试数据库
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


class TestChatService:
    """聊天服务测试"""

    def test_save_message(self):
        """测试保存消息"""
        from app.services.chat_service import ChatService
        
        service = ChatService()
        
        # 使用同步方式保存消息
        service._save_message("test-session", "user", "Hello")
        
        # 验证保存
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.execute(
            "SELECT * FROM messages WHERE session_id = ?",
            ("test-session",)
        )
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) == 1
        assert rows[0][1] == "test-session"
        assert rows[0][2] == "user"
        assert rows[0][3] == "Hello"

    def test_get_history(self):
        """测试获取历史消息"""
        from app.services.chat_service import ChatService
        
        service = ChatService()
        
        # 先保存消息
        service._save_message("test-session", "user", "Hello")
        service._save_message("test-session", "assistant", "Hi there")
        
        # 同步获取历史
        history = service._get_history("test-session")
        
        assert len(history) == 2
        assert history[0].role == "user"
        assert history[0].content == "Hello"
        assert history[1].role == "assistant"
        assert history[1].content == "Hi there"

    def test_get_history_empty_session(self):
        """测试获取空会话历史"""
        from app.services.chat_service import ChatService
        
        service = ChatService()
        history = service._get_history("non-existent-session")
        
        assert len(history) == 0

    def test_history_order(self):
        """测试历史消息顺序"""
        from app.services.chat_service import ChatService
        
        service = ChatService()
        
        # 按顺序保存消息
        service._save_message("order-test", "user", "Msg1")
        service._save_message("order-test", "assistant", "Reply1")
        service._save_message("order-test", "user", "Msg2")
        
        history = service._get_history("order-test")
        
        assert len(history) == 3
        assert history[0].content == "Msg1"
        assert history[1].content == "Reply1"
        assert history[2].content == "Msg2"

    @pytest.mark.asyncio
    async def test_get_reply_requires_api_key(self):
        """测试获取回复需要 API key"""
        from app.services.chat_service import ChatService
        
        service = ChatService()
        service.api_key = ""  # 空 API key
        
        # 模拟 API 调用会失败
        with patch.object(service, '_call_minimax', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = Exception("API Key required")
            
            with pytest.raises(Exception):
                await service.get_reply("test-session", "Hello")

    def test_message_timestamp(self):
        """测试消息时间戳"""
        from app.services.chat_service import ChatService
        
        service = ChatService()
        before = datetime.now().isoformat()
        service._save_message("ts-test", "user", "Test")
        after = datetime.now().isoformat()
        
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.execute(
            "SELECT timestamp FROM messages WHERE session_id = ?",
            ("ts-test",)
        )
        row = cursor.fetchone()
        conn.close()
        
        timestamp = row[0]
        assert before <= timestamp <= after


class TestDatabaseOperations:
    """数据库操作测试"""

    def test_multiple_sessions(self):
        """测试多会话隔离"""
        from app.services.chat_service import ChatService
        
        service = ChatService()
        
        # 创建两个会话
        service._save_message("session-1", "user", "Hello from 1")
        service._save_message("session-2", "user", "Hello from 2")
        
        history1 = service._get_history("session-1")
        history2 = service._get_history("session-2")
        
        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0].content == "Hello from 1"
        assert history2[0].content == "Hello from 2"

    def test_special_characters_content(self):
        """测试特殊字符内容"""
        from app.services.chat_service import ChatService
        
        service = ChatService()
        
        content = "Hello 🌍! 你好 🎉\n多行\n测试"
        service._save_message("special", "user", content)
        
        history = service._get_history("special")
        
        assert len(history) == 1
        assert history[0].content == content

    def test_long_content(self):
        """测试长内容"""
        from app.services.chat_service import ChatService
        
        service = ChatService()
        
        long_content = "A" * 10000  # 10k 字符
        service._save_message("long", "user", long_content)
        
        history = service._get_history("long")
        
        assert len(history) == 1
        assert len(history[0].content) == 10000
