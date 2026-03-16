"""
关键词自动回复 API

当用户发送的消息匹配关键词时，自动回复预设内容
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
import uuid
import re

router = APIRouter(prefix="/api/autoreply", tags=["autoreply"])

# 关键词规则存储（按租户隔离）
# {tenant_id: [Rule]}
TENANT_RULES = {}


class AutoReplyRule(BaseModel):
    id: str
    keywords: List[str]  # 关键词列表
    reply: str  # 回复内容
    match_type: str = "exact"  # exact=精确匹配, fuzzy=模糊匹配, regex=正则
    enabled: bool = True
    priority: int = 0  # 优先级，数字越大越优先
    created_at: str


class AutoReplyRuleCreate(BaseModel):
    keywords: List[str]
    reply: str
    match_type: str = "exact"
    priority: int = 0


class AutoReplyRuleUpdate(BaseModel):
    keywords: Optional[List[str]] = None
    reply: Optional[str] = None
    match_type: Optional[str] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = None


def get_tenant_rules(tenant_id: int):
    """获取租户的规则列表"""
    if tenant_id not in TENANT_RULES:
        TENANT_RULES[tenant_id] = []
    return TENANT_RULES[tenant_id]


def match_keyword(text: str, rule: dict) -> bool:
    """检查文本是否匹配规则"""
    if not rule.get("enabled", True):
        return False
    
    match_type = rule.get("match_type", "exact")
    
    for keyword in rule.get("keywords", []):
        if match_type == "exact":
            if keyword.lower() == text.lower():
                return True
        elif match_type == "fuzzy":
            if keyword.lower() in text.lower():
                return True
        elif match_type == "regex":
            try:
                if re.search(keyword, text, re.IGNORECASE):
                    return True
            except re.error:
                pass
    
    return False


def check_autoreply(message: str, tenant_id: int = 1) -> Optional[str]:
    """检查消息是否触发自动回复"""
    rules = get_tenant_rules(tenant_id)
    
    # 按优先级排序
    sorted_rules = sorted(rules, key=lambda x: x.get("priority", 0), reverse=True)
    
    for rule in sorted_rules:
        if match_keyword(message, rule):
            return rule["reply"]
    
    return None


# ============ API ============

@router.get("/rules", response_model=List[AutoReplyRule])
def list_rules(tenant_id: int = Header(1, alias="X-Tenant-ID")):
    """获取关键词规则列表"""
    rules = get_tenant_rules(tenant_id)
    return [
        AutoReplyRule(
            id=r["id"],
            keywords=r["keywords"],
            reply=r["reply"],
            match_type=r.get("match_type", "exact"),
            enabled=r.get("enabled", True),
            priority=r.get("priority", 0),
            created_at=r.get("created_at", "")
        )
        for r in rules
    ]


@router.post("/rules", response_model=AutoReplyRule)
def create_rule(
    request: AutoReplyRuleCreate,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """创建关键词规则"""
    rules = get_tenant_rules(tenant_id)
    
    rule_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    
    rule = {
        "id": rule_id,
        "keywords": request.keywords,
        "reply": request.reply,
        "match_type": request.match_type,
        "enabled": True,
        "priority": request.priority,
        "created_at": now
    }
    
    rules.append(rule)
    
    return AutoReplyRule(
        id=rule_id,
        keywords=request.keywords,
        reply=request.reply,
        match_type=request.match_type,
        enabled=True,
        priority=request.priority,
        created_at=now
    )


@router.get("/rules/{rule_id}", response_model=AutoReplyRule)
def get_rule(
    rule_id: str,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """获取指定规则"""
    rules = get_tenant_rules(tenant_id)
    
    for r in rules:
        if r["id"] == rule_id:
            return AutoReplyRule(
                id=r["id"],
                keywords=r["keywords"],
                reply=r["reply"],
                match_type=r.get("match_type", "exact"),
                enabled=r.get("enabled", True),
                priority=r.get("priority", 0),
                created_at=r.get("created_at", "")
            )
    
    raise HTTPException(status_code=404, detail="规则不存在")


@router.patch("/rules/{rule_id}", response_model=AutoReplyRule)
def update_rule(
    rule_id: str,
    request: AutoReplyRuleUpdate,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """更新规则"""
    rules = get_tenant_rules(tenant_id)
    
    for r in rules:
        if r["id"] == rule_id:
            if request.keywords is not None:
                r["keywords"] = request.keywords
            if request.reply is not None:
                r["reply"] = request.reply
            if request.match_type is not None:
                r["match_type"] = request.match_type
            if request.enabled is not None:
                r["enabled"] = request.enabled
            if request.priority is not None:
                r["priority"] = request.priority
            
            return AutoReplyRule(
                id=r["id"],
                keywords=r["keywords"],
                reply=r["reply"],
                match_type=r.get("match_type", "exact"),
                enabled=r.get("enabled", True),
                priority=r.get("priority", 0),
                created_at=r.get("created_at", "")
            )
    
    raise HTTPException(status_code=404, detail="规则不存在")


@router.delete("/rules/{rule_id}")
def delete_rule(
    rule_id: str,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """删除规则"""
    rules = get_tenant_rules(tenant_id)
    
    for i, r in enumerate(rules):
        if r["id"] == rule_id:
            rules.pop(i)
            return {"message": "删除成功"}
    
    raise HTTPException(status_code=404, detail="规则不存在")


@router.post("/test")
def test_match(
    request: dict,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """测试消息是否匹配规则"""
    message = request.get("message", "")
    reply = check_autoreply(message, tenant_id)
    return {
        "message": message,
        "matched": reply is not None,
        "reply": reply
    }
