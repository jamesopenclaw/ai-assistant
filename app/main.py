from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, knowledge, skills

app = FastAPI(title="AI Assistant API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])


@app.get("/")
async def root():
    return {"message": "AI Assistant API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
