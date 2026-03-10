from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class Message(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    skill_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    timestamp: datetime


class Skill(BaseModel):
    id: str
    name: str
    description: str
    prompt: str
    enabled: bool = True


class Document(BaseModel):
    id: str
    filename: str
    file_type: str
    uploaded_at: datetime
    chunk_count: int = 0


class KnowledgeAddRequest(BaseModel):
    file_path: str


class ToolCallRequest(BaseModel):
    tool_name: str = Field(min_length=1)
    args: Dict[str, Any] = Field(default_factory=dict)


class ToolCallResponse(BaseModel):
    ok: bool
    tool: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class Template(BaseModel):
    id: str
    name: str
    content: str
