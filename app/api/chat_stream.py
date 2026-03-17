"""
SSE 流式输出 API
"""
from fastapi import APIRouter, Header, Request
from fastapi.responses import StreamingResponse
from typing import Optional
import json
import asyncio
import os

router = APIRouter(prefix="/api/chat", tags=["chat-stream"])

# 模拟流式输出（实际需要根据模型API调整）
async def generate_stream_response(message: str, session_id: str, skill_id: str = None, tenant_id: int = 1):
    """生成流式响应"""
    
    # 调用 AI 服务获取回复
    from app.services.chat_service import ChatService
    chat_service = ChatService()
    
    # 这里获取完整回复（实际生产应该用流式API）
    try:
        full_reply = await chat_service.get_reply(
            session_id=session_id,
            message=message,
            skill_id=skill_id,
            tenant_id=tenant_id
        )
        
        # 模拟流式输出
        for char in full_reply:
            yield f"data: {json.dumps({'content': char, 'done': False})}\n\n"
            await asyncio.sleep(0.02)  # 打字速度
        
        # 发送完成信号
        yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@router.post("/stream")
async def chat_stream(
    message: str,
    session_id: str,
    skill_id: Optional[str] = None,
    tenant_id: int = Header(1, alias="X-Tenant-ID")
):
    """
    流式对话接口
    
    返回 SSE 格式:
    data: {"content": "你", "done": false}
    data: {"content": "好", "done": false}
    data: {"content": "", "done": true}
    """
    
    async def event_generator():
        try:
            from app.services.chat_service import ChatService
            chat_service = ChatService()
            
            # 获取完整回复
            full_reply = await chat_service.get_reply(
                session_id=session_id,
                message=message,
                skill_id=skill_id,
                tenant_id=tenant_id
            )
            
            # 流式输出每个字符
            for char in full_reply:
                yield f"data: {json.dumps({'content': char})}\n\n"
                await asyncio.sleep(0.03)  # 30ms 打字间隔
            
            # 发送完成信号
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/stream/word")
async def chat_stream_by_word(
    message: str,
    session_id: str,
    skill_id: Optional[str] = None,
    tenant_id: int = Header(1, alias="X-Tenant-ID"),
    words_per_minute: int = 300
):
    """
    按单词流式输出（可控制速度）
    
    words_per_minute: 每分钟字数，默认300
    """
    interval = 60.0 / words_per_minute  # 每个字的间隔
    
    async def event_generator():
        try:
            from app.services.chat_service import ChatService
            chat_service = ChatService()
            
            full_reply = await chat_service.get_reply(
                session_id=session_id,
                message=message,
                skill_id=skill_id,
                tenant_id=tenant_id
            )
            
            # 按词输出（中文按字符，英文按单词）
            words = []
            current_word = ""
            
            for char in full_reply:
                current_word += char
                if char in "，。！？；：、\n " or len(current_word) >= 3:
                    if current_word.strip():
                        words.append(current_word)
                    current_word = ""
            
            if current_word.strip():
                words.append(current_word)
            
            # 流式输出
            for word in words:
                yield f"data: {json.dumps({'content': word})}\n\n"
                await asyncio.sleep(interval)
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
