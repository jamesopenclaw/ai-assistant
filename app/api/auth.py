"""
认证 API 路由（测试友好版本）

说明：
- 使用 app.services.auth_service 作为轻量认证后端，保持与现有测试契约一致
- /verify 对无效/缺失 token 返回 200 + {valid:false}
- /me 对无效/缺失 token 返回 401
"""
from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, EmailStr

from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None


class LoginRequest(BaseModel):
    username: str
    password: str


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return authorization


@router.post("/register")
def register(request: RegisterRequest):
    try:
        return auth_service.register_user(
            username=request.username,
            password=request.password,
            email=request.email,
        )
    except auth_service.AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(request: LoginRequest):
    result = auth_service.authenticate_user(request.username, request.password)
    if not result:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return result


@router.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    token = _extract_bearer_token(authorization)
    if token and token in auth_service.TOKEN_STORE:
        del auth_service.TOKEN_STORE[token]
    return {"message": "登出成功"}


@router.get("/verify")
def verify_token(authorization: Optional[str] = Header(None)):
    token = _extract_bearer_token(authorization)
    if not token:
        return {"valid": False}

    user = auth_service.verify_token(token)
    if not user:
        return {"valid": False}

    return {
        "valid": True,
        "user": {
            "user_id": user["user_id"],
            "username": user["username"],
        },
    }


@router.get("/me")
def get_current_user(authorization: Optional[str] = Header(None)):
    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = auth_service.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    full_user = auth_service.get_user_by_id(user["user_id"])
    if not full_user:
        raise HTTPException(status_code=401, detail="User not found")

    return {
        "user_id": full_user["user_id"],
        "username": full_user["username"],
        "email": full_user.get("email"),
    }
