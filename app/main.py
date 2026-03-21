from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import chat, chat_stream, knowledge, skills, auth, templates, webhook_wechat, tenants, usage, sessions, scheduler, users, autoreply, customer_service, models, websocket, monitor
from app.api.v1 import account
from app.middleware.monitor import MonitorMiddleware
from app.utils.database import engine, Base
# 导入所有模型以确保 Base.metadata 包含它们
from app.models import User, Tenant, Usage
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Assistant API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 监控中间件
app.add_middleware(MonitorMiddleware)

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "ui", "ai-assistant-pro", "dist")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Routes
app.include_router(auth.router)
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(chat_stream.router, prefix="/api/chat", tags=["chat-stream"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(webhook_wechat.router, prefix="/api/webhook", tags=["webhook"])
app.include_router(tenants.router, tags=["tenants"])
app.include_router(usage.router, tags=["usage"])
app.include_router(sessions.router, tags=["sessions"])
app.include_router(scheduler.router, tags=["scheduler"])
app.include_router(users.router, tags=["users"])
app.include_router(autoreply.router, tags=["autoreply"])
app.include_router(customer_service.router, tags=["customer-service"])
app.include_router(models.router, tags=["models"])
app.include_router(websocket.router, tags=["websocket"])
app.include_router(monitor.router, tags=["monitor"])
app.include_router(account.router, prefix="/api/v1/account", tags=["account"])


@app.get("/")
async def root():
    static_dir = os.path.join(os.path.dirname(__file__), "..", "ui", "ai-assistant-pro", "dist")
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI Assistant API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
