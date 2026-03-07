from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import ChatRequest, ChatResponse, Message
from app.services.chat_service import ChatService
from datetime import datetime

router = APIRouter()
chat_service = ChatService()


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """发送消息并获取 AI 回复"""
    try:
        reply = await chat_service.get_reply(
            session_id=request.session_id,
            message=request.message,
            skill_id=request.skill_id
        )
        
        return ChatResponse(
            session_id=request.session_id,
            reply=reply,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}", response_model=List[Message])
async def get_history(session_id: str):
    """获取会话历史"""
    try:
        history = await chat_service.get_history(session_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
