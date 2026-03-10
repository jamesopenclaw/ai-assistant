from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    database_url: str = "sqlite:///./ai_assistant.db"
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    minimax_api_key: Optional[str] = None

    model_config = {"extra": "ignore", "env_file": ".env"}


settings = Settings()

# Build engine with appropriate settings based on database type
def get_engine():
    url = settings.database_url
    if url.startswith("postgresql"):
        # PostgreSQL: use connection pool and pre-ping
        return create_engine(
            url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    else:
        # SQLite: keep original settings for backward compatibility
        return create_engine(url, connect_args={"check_same_thread": False})


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
