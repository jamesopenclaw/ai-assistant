"""
认证 API 路由 - 基于数据库和 JWT + HttpOnly Cookie
"""
from fastapi import APIRouter, HTTPException, Depends, Header, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.utils.database import get_db, settings
from app.utils.auth import get_password_hash, create_access_token, authenticate_user
from app.models.user import User
from app.models.auth import UserCreate, UserResponse, LoginRequest, TokenResponse
from app.utils.auth_middleware import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Cookie 配置
COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 60 * 60 * 24  # 24 小时（秒）


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
def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    用户登录
    
    - **username**: 用户名（必填）
    - **password**: 密码（必填）
    
    登录成功后会在 Cookie 中设置 HttpOnly Token
    """
    user = authenticate_user(db, request.username, request.password)

    if not user:
        raise HTTPException(
            status_code=401, 
            detail="用户名或密码错误"
        )

    access_token = create_access_token(data={"sub": user.username})

    # 设置 HttpOnly Cookie
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=True,  # 生产环境建议启用
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        # 本地开发可注释掉 domain
        # domain="your-domain.com"
    )

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
def logout(response: Response):
    """
    用户登出（清除 HttpOnly Cookie）
    """
    response.delete_cookie(
        key=COOKIE_NAME,
        # domain 需要与设置 cookie 时一致
        # domain="your-domain.com"
    )
    return {"message": "登出成功"}


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
