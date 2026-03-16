"""
企业微信机器人 Webhook 服务

接收企微群机器人的消息回调，调用 ai-assistant 处理，返回回复
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
import hashlib
import time
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/webhook", tags=["wechat"])

# 企微配置
WECHAT_TOKEN = os.getenv("WECHAT_TOKEN", "")
WECHAT_ENCODING_AES_KEY = os.getenv("WECHAT_ENCODING_AES_KEY", "")
WECHAT_CORP_ID = os.getenv("WECHAT_CORP_ID", "")

# AI Assistant 服务地址
AI_ASSISTANT_URL = os.getenv("AI_ASSISTANT_URL", "http://127.0.0.1:8013")


class WechatMessage(BaseModel):
    """企微消息模型"""
    msg_type: str
    content: str
    from_user: str
    agent_id: Optional[str] = None
    room_id: Optional[str] = None


class WechatResponse(BaseModel):
    """企微回复模型"""
    content: str


async def get_wechat_token() -> str:
    """获取企微 access_token"""
    # 这里需要实现企业微信的 access_token 获取逻辑
    # 实际使用时需要缓存 token（有效期2小时）
    raise NotImplementedError("需要配置企业微信企业ID和Secret")


async def send_wechat_message(to_user: str, content: str, agent_id: str = None):
    """发送企微消息"""
    # 实际使用时调用企微发送消息API
    print(f"[企微消息] 发送给 {to_user}: {content}")


def verify_wechat_signature(signature: str, timestamp: str, nonce: str) -> bool:
    """验证企微签名"""
    if not WECHAT_TOKEN:
        return True  # 未配置token时跳过验证
    
    tmp_list = sorted([WECHAT_TOKEN, timestamp, nonce])
    tmp_str = "".join(tmp_list)
    calc_signature = hashlib.sha1(tmp_str.encode()).hexdigest()
    
    return calc_signature == signature


@router.get("")
async def wechat_verify_get(request: Request):
    """
    企微回调URL验证（GET请求）
    用于首次配置回调URL时的验证
    """
    signature = request.query_params.get("signature", "")
    timestamp = request.query_params.get("timestamp", "")
    nonce = request.query_params.get("nonce", "")
    echostr = request.query_params.get("echostr", "")
    
    if not verify_wechat_signature(signature, timestamp, nonce):
        raise HTTPException(status_code=403, detail="签名验证失败")
    
    return echostr


@router.post("")
async def wechat_webhook(request: Request):
    """
    企微消息回调入口（POST请求）
    
    消息格式示例：
    {
        "msg_type": "text",
        "content": "Hello",
        "from_user": "user123",
        "agent_id": "1000001",
        "room_id": "room123"
    }
    """
    # 1. 验证签名（可选）
    signature = request.query_params.get("signature", "")
    timestamp = request.query_params.get("timestamp", "")
    nonce = request.query_params.get("nonce", "")
    
    if not verify_wechat_signature(signature, timestamp, nonce):
        raise HTTPException(status_code=403, detail="签名验证失败")
    
    # 2. 解析消息体
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="无效的JSON")
    
    msg_type = body.get("msg_type")
    content = body.get("content", "").strip()
    from_user = body.get("from_user", "unknown")
    room_id = body.get("room_id")  # 群消息时有值
    
    # 3. 忽略非文本消息
    if msg_type != "text":
        return {"status": "ok", "message": "暂只支持文本消息"}
    
    # 4. 忽略空消息
    if not content:
        return {"status": "ok", "message": "空消息忽略"}
    
    # 5. 构建 session_id（群聊用room_id，个人用user_id）
    session_id = room_id or from_user
    
    print(f"[企微消息] 收到消息 from={from_user} room={room_id}: {content}")
    
    # 6. 调用 AI Assistant
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{AI_ASSISTANT_URL}/api/chat",
                json={
                    "session_id": f"wechat_{session_id}",
                    "message": content,
                    "skill_id": "general"
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"AI服务调用失败: {response.status_code}")
            
            result = response.json()
            ai_reply = result.get("reply", "抱歉，我暂时无法回答这个问题。")
    
    except Exception as e:
        print(f"[企微消息] AI调用失败: {e}")
        ai_reply = "抱歉，服务暂时不可用，请稍后重试。"
    
    # 7. 发送回复
    print(f"[企微消息] AI回复: {ai_reply}")
    
    # 实际部署时取消注释
    # await send_wechat_message(from_user, ai_reply, body.get("agent_id"))
    
    return {"status": "ok", "message": "success"}
