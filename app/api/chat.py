from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import ChatRequest, ChatResponse, Message, ToolCallRequest, ToolCallResponse
from app.services.chat_service import ChatService
from app.services.tools_runtime import function_caller, registry
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


@router.get("/tools")
async def list_tools():
    """列出已注册工具"""
    return registry.list_tools()


@router.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest):
    """统一工具调用入口"""
    result = await function_caller.call(request.tool_name, request.args)
    return ToolCallResponse(**result)
