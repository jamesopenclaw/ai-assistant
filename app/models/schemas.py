from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Message(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    session_id: str
    message: str
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
