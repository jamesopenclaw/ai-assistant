"""
认证 API 路由 - 基于数据库和 JWT
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.utils.database import get_db
from app.utils.auth import get_password_hash, create_access_token, authenticate_user
from app.models.user import User
from app.models.auth import UserCreate, UserResponse, LoginRequest, TokenResponse
from app.utils.auth_middleware import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ============== API Endpoints ==============

@router.post("/register", response_model=UserResponse, status_code=201)
def register(request: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    
    - **username**: 用户名（必填）
    - **email**: 邮箱（必填）
    - **password**: 密码（必填）
    """
    # Check if username exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # Check if email exists
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # Create new user
    hashed_password = get_password_hash(request.password)
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        created_at=new_user.created_at,
    )


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    
    - **username**: 用户名（必填）
    - **password**: 密码（必填）
    """
    user = authenticate_user(db, request.username, request.password)

    if not user:
        raise HTTPException(
            status_code=401, 
            detail="用户名或密码错误"
        )

    access_token = create_access_token(data={"sub": user.username})

    return {
        "user": {
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email
        },
        "token": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600
        }
    }


@router.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    """
    用户登出（JWT 无状态，只需客户端删除 token）
    
    - **authorization**: Bearer token
    """
    return {"message": "登出成功，请客户端删除 token"}


@router.get("/verify")
def verify_token(current_user: User = Depends(get_current_user)):
    """
    验证 token
    
    - **authorization**: Bearer token
    """
    return {
        "valid": True,
        "user": {
            "user_id": str(current_user.id),
            "username": current_user.username
        }
    }


@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息
    
    - **authorization**: Bearer token
    """
    return {
        "user_id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email
    }
