"""
数据模型单元测试
"""
import pytest
from datetime import datetime
from app.models.schemas import (
    Message,
    ChatRequest,
    ChatResponse,
    Skill,
    Document,
    KnowledgeAddRequest
)


class TestMessage:
    """消息模型测试"""

    def test_message_creation(self):
        """测试消息创建"""
        msg = Message(role="user", content="你好")
        assert msg.role == "user"
        assert msg.content == "你好"
        assert msg.timestamp is None

    def test_message_with_timestamp(self):
        """测试带时间戳的消息"""
        now = datetime.now()
        msg = Message(role="assistant", content="你好", timestamp=now)
        assert msg.timestamp == now


class TestChatRequest:
    """聊天请求模型测试"""

    def test_chat_request_creation(self):
        """测试聊天请求创建"""
        req = ChatRequest(session_id="test-123", message="你好")
        assert req.session_id == "test-123"
        assert req.message == "你好"
        assert req.skill_id is None

    def test_chat_request_with_skill(self):
        """测试带技能的聊天请求"""
        req = ChatRequest(session_id="test-123", message="你好", skill_id="tech")
        assert req.skill_id == "tech"

    def test_chat_request_validation(self):
        """测试聊天请求字段验证"""
        # 缺少必需字段应该失败
        with pytest.raises(Exception):
            ChatRequest(session_id="test-123")


class TestChatResponse:
    """聊天响应模型测试"""

    def test_chat_response_creation(self):
        """测试聊天响应创建"""
        now = datetime.now()
        resp = ChatResponse(session_id="test-123", reply="你好", timestamp=now)
        assert resp.session_id == "test-123"
        assert resp.reply == "你好"
        assert resp.timestamp == now


class TestSkill:
    """技能模型测试"""

    def test_skill_creation(self):
        """测试技能创建"""
        skill = Skill(
            id="test",
            name="测试技能",
            description="这是一个测试技能",
            prompt="你是一个测试助手"
        )
        assert skill.id == "test"
        assert skill.name == "测试技能"
        assert skill.enabled is True  # 默认值

    def test_skill_disabled_default(self):
        """测试技能默认启用"""
        skill = Skill(
            id="test",
            name="测试",
            description="测试",
            prompt="测试"
        )
        assert skill.enabled is True


class TestDocument:
    """文档模型测试"""

    def test_document_creation(self):
        """测试文档创建"""
        now = datetime.now()
        doc = Document(
            id="doc-123",
            filename="test.pdf",
            file_type="pdf",
            uploaded_at=now,
            chunk_count=5
        )
        assert doc.id == "doc-123"
        assert doc.filename == "test.pdf"
        assert doc.chunk_count == 5

    def test_document_default_chunk_count(self):
        """测试文档默认分块数"""
        now = datetime.now()
        doc = Document(
            id="doc-123",
            filename="test.txt",
            file_type="text",
            uploaded_at=now
        )
        assert doc.chunk_count == 0


class TestKnowledgeAddRequest:
    """知识库添加请求测试"""

    def test_knowledge_add_request(self):
        """测试知识库添加请求"""
        req = KnowledgeAddRequest(file_path="/path/to/file.pdf")
        assert req.file_path == "/path/to/file.pdf"
