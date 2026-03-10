from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import chat, knowledge, skills, auth, templates
from app.utils.database import engine, Base
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

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "ui", "ai-assistant-pro", "dist")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Routes
app.include_router(auth.router)
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])


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
