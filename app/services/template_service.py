from typing import Dict, List
from fastapi import HTTPException


_BUILTIN_TEMPLATES: Dict[str, Dict[str, str]] = {
    "general-qa": {"id": "general-qa", "name": "通用问答", "content": "请用清晰、简洁的方式回答用户问题，必要时给出步骤。"},
    "code-review": {"id": "code-review", "name": "代码审查", "content": "你是资深工程师，请从正确性、可维护性、安全性角度审查代码并给出建议。"},
    "bug-fix": {"id": "bug-fix", "name": "缺陷修复", "content": "请先定位根因，再给出最小可行修复方案，并列出验证步骤。"},
    "architecture": {"id": "architecture", "name": "架构设计", "content": "请给出可扩展架构方案，说明关键模块、数据流与权衡。"},
    "product-prd": {"id": "product-prd", "name": "PRD 草案", "content": "请输出 PRD：背景、目标、用户故事、范围、验收标准、风险。"},
    "meeting-summary": {"id": "meeting-summary", "name": "会议纪要", "content": "请整理会议纪要：结论、行动项、负责人、截止时间。"},
    "email-polish": {"id": "email-polish", "name": "邮件润色", "content": "请将输入内容润色为专业邮件，保持礼貌并保留关键信息。"},
    "translation-cn-en": {"id": "translation-cn-en", "name": "中英翻译", "content": "请准确翻译并保留术语一致性，必要时给出两种译法。"},
    "learning-plan": {"id": "learning-plan", "name": "学习计划", "content": "请根据目标和时长生成可执行学习计划，按周拆解。"},
    "interview": {"id": "interview", "name": "面试官模式", "content": "请扮演面试官，提出逐步深入的问题并在最后给出反馈。"},
}


class TemplateService:
    def list_templates(self) -> List[dict]:
        return list(_BUILTIN_TEMPLATES.values())

    def get_template(self, template_id: str) -> dict:
        template = _BUILTIN_TEMPLATES.get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
