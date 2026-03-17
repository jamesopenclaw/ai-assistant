"""
模型配置管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/models", tags=["models"])

# 模型配置存储（按租户隔离）
# {tenant_id: {model_id: ModelConfig}}
TENANT_MODELS = {}


class ModelProvider:
    """模型提供商常量"""
    MINIMAX = "minimax"
    OPENAI = "openai"
    DOUYIN = "douyin"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"


class ModelConfig(BaseModel):
    model_id: str
    name: str
    provider: str
    api_key: str
    base_url: Optional[str] = None
    model_name: str = ""
    enabled: bool = True
    is_default: bool = False
    created_at: str
    updated_at: str


class ModelConfigCreate(BaseModel):
    name: str
    provider: str
    api_key: str
    base_url: Optional[str] = None
    model_name: str = ""
    enabled: bool = True
    is_default: bool = False


class ModelConfigUpdate(BaseModel):
    name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_name: Optional[str] = None
    enabled: Optional[bool] = None
    is_default: Optional[bool] = None


# 支持的模型提供商
PROVIDERS = {
    "minimax": {
        "name": "MiniMax",
        "default_url": "https://api.minimax.chat/v1",
        "default_model": "MiniMax-M2.5"
    },
    "openai": {
        "name": "OpenAI",
        "default_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o"
    },
    "douyin": {
        "name": "豆包",
        "default_url": "https://ark.cn-beijing.volces.com/api/v3",
        "default_model": "doubao-lite-4k"
    },
    "deepseek": {
        "name": "DeepSeek",
        "default_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat"
    },
    "qwen": {
        "name": "阿里千问",
        "default_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-plus"
    }
}


def get_tenant_models(tenant_id: int):
    """获取租户的模型配置"""
    if tenant_id not in TENANT_MODELS:
        TENANT_MODELS[tenant_id] = {}
    return TENANT_MODELS[tenant_id]


@router.get("/providers")
def list_providers():
    """获取支持的模型提供商列表"""
    return PROVIDERS


@router.get("", response_model=List[ModelConfig])
def list_models(tenant_id: int = Header(1, alias="X-Tenant-ID")):
    """获取模型配置列表"""
    models = get_tenant_models(tenant_id)
    return [
        ModelConfig(
            model_id=mid,
            name=m["name"],
            provider=m["provider"],
            api_key="***" + m["api_key"][-4:] if m.get("api_key") else "",
            base_url=m.get("base_url"),
            model_name=m.get("model_name", ""),
            enabled=m.get("enabled", True),
            is_default=m.get("is_default", False),
            created_at=m.get("created_at", ""),
            updated_at=m.get("updated_at", "")
        )
        for mid, m in models.items()
    ]


@router.post("", response_model=ModelConfig)
def create_model(
    request: ModelConfigCreate,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """创建模型配置"""
    models = get_tenant_models(tenant_id)
    
    model_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    
    # 如果设为默认，取消其他默认
    if request.is_default:
        for m in models.values():
            m["is_default"] = False
    
    models[model_id] = {
        "name": request.name,
        "provider": request.provider,
        "api_key": request.api_key,
        "base_url": request.base_url or PROVIDERS.get(request.provider, {}).get("default_url"),
        "model_name": request.model_name or PROVIDERS.get(request.provider, {}).get("default_model"),
        "enabled": request.enabled,
        "is_default": request.is_default,
        "created_at": now,
        "updated_at": now
    }
    
    return ModelConfig(
        model_id=model_id,
        name=request.name,
        provider=request.provider,
        api_key="***" + request.api_key[-4:] if request.api_key else "",
        base_url=models[model_id]["base_url"],
        model_name=models[model_id]["model_name"],
        enabled=request.enabled,
        is_default=request.is_default,
        created_at=now,
        updated_at=now
    )


@router.get("/{model_id}", response_model=ModelConfig)
def get_model(
    model_id: str,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """获取模型配置"""
    models = get_tenant_models(tenant_id)
    
    if model_id not in models:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    m = models[model_id]
    return ModelConfig(
        model_id=model_id,
        name=m["name"],
        provider=m["provider"],
        api_key="***" + m["api_key"][-4:] if m.get("api_key") else "",
        base_url=m.get("base_url"),
        model_name=m.get("model_name", ""),
        enabled=m.get("enabled", True),
        is_default=m.get("is_default", False),
        created_at=m.get("created_at", ""),
        updated_at=m.get("updated_at", "")
    )


@router.patch("/{model_id}", response_model=ModelConfig)
def update_model(
    model_id: str,
    request: ModelConfigUpdate,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """更新模型配置"""
    models = get_tenant_models(tenant_id)
    
    if model_id not in models:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    m = models[model_id]
    
    # 如果设为默认，取消其他默认
    if request.is_default:
        for mid, mm in models.items():
            if mid != model_id:
                mm["is_default"] = False
    
    if request.name is not None:
        m["name"] = request.name
    if request.api_key is not None:
        m["api_key"] = request.api_key
    if request.base_url is not None:
        m["base_url"] = request.base_url
    if request.model_name is not None:
        m["model_name"] = request.model_name
    if request.enabled is not None:
        m["enabled"] = request.enabled
    if request.is_default is not None:
        m["is_default"] = request.is_default
    
    m["updated_at"] = datetime.now().isoformat()
    
    return ModelConfig(
        model_id=model_id,
        name=m["name"],
        provider=m["provider"],
        api_key="***" + m["api_key"][-4:] if m.get("api_key") else "",
        base_url=m.get("base_url"),
        model_name=m.get("model_name", ""),
        enabled=m.get("enabled", True),
        is_default=m.get("is_default", False),
        created_at=m.get("created_at", ""),
        updated_at=m["updated_at"]
    )


@router.delete("/{model_id}")
def delete_model(
    model_id: str,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """删除模型配置"""
    models = get_tenant_models(tenant_id)
    
    if model_id not in models:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    del models[model_id]
    return {"message": "删除成功"}


@router.post("/{model_id}/set-default")
def set_default_model(
    model_id: str,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """设为默认模型"""
    models = get_tenant_models(tenant_id)
    
    if model_id not in models:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    # 取消其他默认
    for mid, m in models.items():
        m["is_default"] = (mid == model_id)
    
    return {"message": "已设为默认模型"}


@router.get("/active")
def get_active_model(tenant_id: int = Header(1, alias="X-Tenant-ID")):
    """获取当前使用的模型"""
    models = get_tenant_models(tenant_id)
    
    # 优先返回默认模型
    for m in models.values():
        if m.get("is_default"):
            return {
                "model_id": m.get("model_id"),
                "name": m["name"],
                "provider": m["provider"],
                "model_name": m.get("model_name", "")
            }
    
    # 返回第一个启用的模型
    for mid, m in models.items():
        if m.get("enabled"):
            return {
                "model_id": mid,
                "name": m["name"],
                "provider": m["provider"],
                "model_name": m.get("model_name", "")
            }
    
    # 无可用模型
    return {"error": "无可用模型，请先配置"}
