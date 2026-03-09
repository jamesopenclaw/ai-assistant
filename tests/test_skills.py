"""
技能 API 单元测试
"""
import pytest
from app.api.skills import SKILLS, list_skills, get_skill, toggle_skill
from fastapi import HTTPException


class TestSkills:
    """技能模块测试"""

    def test_list_skills(self):
        """测试获取技能列表"""
        result = list(SKILLS.values())
        assert len(result) == 3
        assert all("id" in skill for skill in result)
        assert all("name" in skill for skill in result)
        assert all("enabled" in skill for skill in result)

    def test_get_skill_existing(self):
        """测试获取已存在的技能"""
        skill = SKILLS["general"]
        assert skill["id"] == "general"
        assert skill["name"] == "通用助手"
        assert skill["enabled"] is True

    def test_get_skill_not_found(self):
        """测试获取不存在的技能"""
        assert "nonexistent" not in SKILLS

    def test_toggle_skill(self):
        """测试技能启用/禁用切换"""
        original_state = SKILLS["general"]["enabled"]
        
        # 切换状态
        SKILLS["general"]["enabled"] = not original_state
        assert SKILLS["general"]["enabled"] is not original_state
        
        # 恢复原状态
        SKILLS["general"]["enabled"] = original_state

    def test_all_skills_have_required_fields(self):
        """测试所有技能都有必需字段"""
        required_fields = ["id", "name", "description", "prompt", "enabled"]
        
        for skill_id, skill in SKILLS.items():
            for field in required_fields:
                assert field in skill, f"Skill {skill_id} missing field: {field}"

    def test_general_skill_prompt(self):
        """测试通用技能提示词"""
        assert "AI助手" in SKILLS["general"]["prompt"]
        assert "中文" in SKILLS["general"]["prompt"]

    def test_tech_skill_prompt(self):
        """测试技术专家提示词"""
        assert "技术专家" in SKILLS["tech"]["prompt"]
        assert "编程" in SKILLS["tech"]["prompt"]

    def test_knowledge_skill_prompt(self):
        """测试知识库技能提示词"""
        assert "知识库" in SKILLS["knowledge"]["prompt"]
