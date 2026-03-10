from fastapi import Depends, HTTPException, status, Cookie, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.utils.database import get_db
from app.utils.auth import decode_token
from app.models.user import User

COOKIE_NAME = "access_token"


def extract_token(
    authorization: Optional[str] = None,
    access_token: Optional[str] = Cookie(None),
) -> str:
    """
    从 Authorization Header 或 Cookie 中提取 token
    优先级：Authorization Header > Cookie
    """
    # 1. 优先从 Authorization Header 读取
    if authorization:
        if authorization.startswith("Bearer "):
            return authorization[7:]
        return authorization
    
    # 2. 从 Cookie 读取
    if access_token:
        return access_token
    
    # 3. 都没有则抛出异常
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    authorization: Optional[str] = Header(None),
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
) -> User:
    """
    获取当前用户 - 支持从 Header 或 Cookie 读取 token
    
    使用方式：
    - Header: Authorization: Bearer <token>
    - Cookie: access_token=<token>
    """
    token = extract_token(authorization, access_token)
    
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
