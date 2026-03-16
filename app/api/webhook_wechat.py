"""
企业微信机器人 Webhook 服务

接收企微群机器人的消息回调，调用 ai-assistant 处理，返回回复
"""
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict
import hashlib
import time
import httpx
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

router = APIRouter(prefix="/wechat", tags=["wechat"])

# 企微配置
WECHAT_TOKEN = os.getenv("WECHAT_TOKEN", "")
WECHAT_CORP_ID = os.getenv("WECHAT_CORP_ID", "")
WECHAT_CORP_SECRET = os.getenv("WECHAT_CORP_SECRET", "")
WECHAT_AGENT_ID = os.getenv("WECHAT_AGENT_ID", "")

# AI Assistant 服务地址
AI_ASSISTANT_URL = os.getenv("AI_ASSISTANT_URL", "http://127.0.0.1:8013")

# Token 缓存
_token_cache: Dict[str, tuple] = {}  # {corp_id: (token, expires_at)}


async def get_wechat_token() -> Optional[str]:
    """获取企微 access_token（带缓存）"""
    global _token_cache
    
    if not WECHAT_CORP_ID or not WECHAT_CORP_SECRET:
        return None
    
    # 检查缓存
    if WECHAT_CORP_ID in _token_cache:
        token, expires_at = _token_cache[WECHAT_CORP_ID]
        if time.time() < expires_at - 300:  # 提前5分钟刷新
            return token
    
    # 调用企微 API 获取 token
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken"
            params = {
                "corpid": WECHAT_CORP_ID,
                "corpsecret": WECHAT_CORP_SECRET
            }
            response = await client.get(url, params=params)
            data = response.json()
            
            if data.get("errcode") == 0:
                token = data["access_token"]
                expires_in = data.get("expires_in", 7200)
                _token_cache[WECHAT_CORP_ID] = (token, time.time() + expires_in)
                return token
    except Exception as e:
        print(f"获取企微token失败: {e}")
    
    return None


async def send_wechat_message(to_user: str, content: str) -> bool:
    """发送企微消息"""
    token = await get_wechat_token()
    if not token:
        print("[企微] 未配置企业ID/Secret，无法发送消息")
        return False
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send"
            params = {"access_token": token}
            
            data = {
                "touser": to_user,
                "msgtype": "text",
                "agentid": WECHAT_AGENT_ID,
                "text": {"content": content}
            }
            
            response = await client.post(url, params=params, json=data)
            result = response.json()
            
            if result.get("errcode") == 0:
                print(f"[企微] 消息发送成功 to={to_user}")
                return True
            else:
                print(f"[企微] 消息发送失败: {result}")
                return False
    except Exception as e:
        print(f"[企微] 发送消息异常: {e}")
        return False


async def send_wechat_group_message(room_id: str, content: str) -> bool:
    """发送企微群消息"""
    token = await get_wechat_token()
    if not token:
        print("[企微] 未配置企业ID/Secret，无法发送群消息")
        return False
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://qyapi.weixin.qq.com/cgi-bin/appchat/send"
            params = {"access_token": token}
            
            data = {
                "chatid": room_id,
                "msgtype": "text",
                "text": {"content": content}
            }
            
            response = await client.post(url, params=params, json=data)
            result = response.json()
            
            if result.get("errcode") == 0:
                print(f"[企微] 群消息发送成功 chatid={room_id}")
                return True
            else:
                print(f"[企微] 群消息发送失败: {result}")
                return False
    except Exception as e:
        print(f"[企微] 发送群消息异常: {e}")
        return False


def verify_wechat_signature(signature: str, timestamp: str, nonce: str) -> bool:
    """验证企微签名"""
    if not WECHAT_TOKEN:
        return True  # 未配置token时跳过验证
    
    tmp_list = sorted([WECHAT_TOKEN, timestamp, nonce])
    tmp_str = "".join(tmp_list)
    calc_signature = hashlib.sha1(tmp_str.encode()).hexdigest()
    
    return calc_signature == signature


def parse_wechat_message(body: dict) -> Optional[dict]:
    """解析企微消息"""
    msg_type = body.get("msg_type")
    
    # 文本消息
    if msg_type == "text":
        content = body.get("content", "").strip()
        from_user = body.get("from_user_name", body.get("user_id", "unknown"))
        room_id = body.get("room_id")  # 群消息时有值
        
        # 检查是否@机器人（群消息中）
        if room_id and f"@{WECHAT_AGENT_ID}" in content:
            # 移除@机器人的部分
            content = content.replace(f"@{WECHAT_AGENT_ID}", "").strip()
        
        return {
            "msg_type": msg_type,
            "content": content,
            "from_user": from_user,
            "room_id": room_id,
            "agent_id": body.get("agent_id")
        }
    
    # 事件消息
    elif msg_type == "event":
        event = body.get("event")
        from_user = body.get("from_user_name", body.get("user_id", "unknown"))
        
        return {
            "msg_type": event,
            "content": f"[事件] {event}",
            "from_user": from_user,
            "room_id": body.get("room_id"),
            "agent_id": body.get("agent_id")
        }
    
    return None


async def call_ai_assistant(message: str, session_id: str, skill_id: str = "general") -> str:
    """调用 AI Assistant 服务"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{AI_ASSISTANT_URL}/api/chat",
                json={
                    "session_id": session_id,
                    "message": message,
                    "skill_id": skill_id
                },
                headers={"X-Tenant-ID": "1"}  # 默认租户
            )
            
            if response.status_code != 200:
                raise Exception(f"AI服务调用失败: {response.status_code}")
            
            result = response.json()
            return result.get("reply", "抱歉，我暂时无法回答这个问题。")
    
    except Exception as e:
        print(f"[企微] AI调用失败: {e}")
        return "抱歉，服务暂时不可用，请稍后重试。"


# ============ API 端点 ============

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
async def wechat_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    企微消息回调入口（POST请求）
    
    企微发送的消息格式：
    {
        "msg_type": "text",
        "content": "Hello",
        "user_id": "user123",
        "room_id": "room123",  # 群消息时有值
        "agent_id": "1000001"
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
    
    # 3. 解析消息
    msg = parse_wechat_message(body)
    if not msg:
        return {"status": "ok", "message": "忽略不支持的消息类型"}
    
    msg_type = msg["msg_type"]
    content = msg["content"]
    from_user = msg["from_user"]
    room_id = msg["room_id"]
    
    # 4. 忽略空消息和非文本（非事件）
    if not content or (msg_type != "text" and msg_type != "event"):
        return {"status": "ok", "message": "忽略空消息"}
    
    # 5. 构建 session_id
    session_id = f"wechat_{room_id or from_user}"
    
    print(f"[企微消息] 收到消息 from={from_user} room={room_id}: {content}")
    
    # 6. 异步调用 AI 并发送回复（不阻塞企微回调）
    async def process_and_reply():
        ai_reply = await call_ai_assistant(content, session_id)
        print(f"[企微消息] AI回复: {ai_reply}")
        
        if room_id:
            # 群消息回复到群
            await send_wechat_group_message(room_id, ai_reply)
        else:
            # 个人消息回复给个人
            await send_wechat_message(from_user, ai_reply)
    
    background_tasks.add_task(process_and_reply)
    
    return {"status": "ok", "message": "success"}


@router.get("/config")
async def get_wechat_config():
    """获取企微配置状态"""
    return {
        "configured": bool(WECHAT_CORP_ID and WECHAT_CORP_SECRET),
        "corp_id": WECHAT_CORP_ID[:8] + "..." if WECHAT_CORP_ID else "",
        "agent_id": WECHAT_AGENT_ID
    }


@router.post("/test")
async def test_wechat_message(to_user: str, content: str):
    """测试发送企微消息"""
    success = await send_wechat_message(to_user, content)
    return {"success": success}
