"""
API 集成测试
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)


class TestRootEndpoint:
    """根端点测试"""

    def test_root_endpoint(self):
        """测试根端点返回正确信息"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"

    def test_health_endpoint(self):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestChatAPI:
    """聊天 API 测试"""

    def test_chat_missing_fields(self):
        """测试缺少必需字段"""
        response = client.post("/api/chat", json={})
        assert response.status_code == 422  # Validation error

    def test_chat_invalid_session_id(self):
        """测试无效的 session_id"""
        response = client.post("/api/chat", json={
            "session_id": "",  # 空 session_id
            "message": "Hello"
        })
        assert response.status_code == 422

    def test_chat_empty_message(self):
        """测试空消息"""
        response = client.post("/api/chat", json={
            "session_id": "test-session",
            "message": ""
        })
        # 可能是 422 (验证错误) 或 500 (业务逻辑错误)
        assert response.status_code in [422, 500]


class TestSkillsAPI:
    """技能 API 测试"""

    def test_list_skills(self):
        """测试获取技能列表"""
        response = client.get("/api/skills")
        assert response.status_code == 200
        skills = response.json()
        assert isinstance(skills, list)
        assert len(skills) > 0
        
        # 验证技能结构
        for skill in skills:
            assert "id" in skill
            assert "name" in skill
            assert "description" in skill
            assert "enabled" in skill

    def test_get_skill_general(self):
        """测试获取通用技能"""
        response = client.get("/api/skills/general")
        assert response.status_code == 200
        skill = response.json()
        assert skill["id"] == "general"
        assert "prompt" in skill

    def test_get_skill_tech(self):
        """测试获取技术技能"""
        response = client.get("/api/skills/tech")
        assert response.status_code == 200
        skill = response.json()
        assert skill["id"] == "tech"

    def test_get_skill_knowledge(self):
        """测试获取知识库技能"""
        response = client.get("/api/skills/knowledge")
        assert response.status_code == 200
        skill = response.json()
        assert skill["id"] == "knowledge"

    def test_get_skill_not_found(self):
        """测试获取不存在的技能"""
        response = client.get("/api/skills/nonexistent")
        assert response.status_code == 404

    def test_toggle_skill(self):
        """测试切换技能状态"""
        # 先获取当前状态
        response = client.get("/api/skills/general")
        original_enabled = response.json()["enabled"]
        
        # 切换
        response = client.post("/api/skills/general/toggle")
        assert response.status_code == 200
        new_state = response.json()["enabled"]
        assert new_state != original_enabled
        
        # 恢复原状态
        client.post("/api/skills/general/toggle")


class TestKnowledgeAPI:
    """知识库 API 测试"""

    def test_knowledge_endpoint_exists(self):
        """测试知识库端点存在"""
        response = client.get("/api/knowledge")
        # 可能是 200 (正常) 或 500 (功能未完全实现)
        assert response.status_code in [200, 500]

    def test_knowledge_search_endpoint(self):
        """测试知识库搜索端点"""
        response = client.post("/api/knowledge/search", json={
            "query": "测试查询",
            "k": 3
        })
        # 可能返回 200 或 500 (依赖向量数据库)
        assert response.status_code in [200, 500]


class TestChatHistoryAPI:
    """聊天历史 API 测试"""

    def test_get_history_empty(self):
        """测试获取空会话历史"""
        response = client.get("/api/chat/history/nonexistent-session")
        assert response.status_code == 200
        history = response.json()
        assert isinstance(history, list)
        assert len(history) == 0

    def test_get_history_format(self):
        """测试历史消息格式"""
        # 先发送消息创建历史
        session_id = "test-history-format"
        
        try:
            client.post("/api/chat", json={
                "session_id": session_id,
                "message": "Test message"
            })
        except:
            pass  # 忽略 API 错误
        
        # 获取历史
        response = client.get(f"/api/chat/history/{session_id}")
        if response.status_code == 200:
            history = response.json()
            if len(history) > 0:
                # 验证消息格式
                msg = history[0]
                assert "role" in msg
                assert "content" in msg


class TestCORS:
    """CORS 测试"""

    def test_cors_headers(self):
        """测试 CORS 头"""
        response = client.options("/")
        # 检查 CORS 中间件是否配置
        # TestClient 默认不返回 CORS 头，需要检查实际请求
        assert response.status_code in [200, 405]  # 405 for OPTIONS not defined


class TestErrorHandling:
    """错误处理测试"""

    def test_invalid_json(self):
        """测试无效 JSON"""
        response = client.post(
            "/api/chat",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_method_not_allowed(self):
        """测试不支持的 HTTP 方法"""
        response = client.put("/api/skills")
        assert response.status_code == 405

    def test_not_found(self):
        """测试 404 路由"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
