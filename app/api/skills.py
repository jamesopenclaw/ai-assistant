from fastapi import APIRouter, HTTPException
from app.models.schemas import Skill

router = APIRouter()

# 内存中的技能配置（生产环境应存数据库）
SKILLS = {
    "general": {
        "id": "general",
        "name": "通用助手",
        "description": "日常对话和问题解答",
        "prompt": "你是一个友好的AI助手，用中文回答问题。",
        "enabled": True
    },
    "tech": {
        "id": "tech",
        "name": "技术专家",
        "description": "编程和技术问题解答",
        "prompt": "你是一个资深技术专家，擅长编程和系统架构。回答要专业、简洁。",
        "enabled": True
    },
    "knowledge": {
        "id": "knowledge",
        "name": "知识库问答",
        "description": "基于企业知识库的问答",
        "prompt": "你基于企业知识库回答用户问题。",
        "enabled": True
    }
}


@router.get("", response_model=list)
async def list_skills():
    """获取技能列表"""
    return list(SKILLS.values())


@router.get("/{skill_id}")
async def get_skill(skill_id: str):
    """获取单个技能详情"""
    if skill_id not in SKILLS:
        raise HTTPException(status_code=404, detail="Skill not found")
    return SKILLS[skill_id]


@router.post("/{skill_id}/toggle")
async def toggle_skill(skill_id: str):
    """启用/禁用技能"""
    if skill_id not in SKILLS:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    SKILLS[skill_id]["enabled"] = not SKILLS[skill_id]["enabled"]
    return SKILLS[skill_id]
