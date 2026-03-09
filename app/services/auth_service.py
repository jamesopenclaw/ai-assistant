"""
用户认证服务
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from functools import wraps

# 模拟用户数据库（实际项目中应使用真实数据库）
MOCK_USERS_DB: Dict[str, Dict] = {}

# Token 存储（实际项目中应使用缓存/数据库）
TOKEN_STORE: Dict[str, Dict] = {}


class AuthError(Exception):
    """认证错误"""
    pass


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    使用 SHA-256 加密密码
    
    Args:
        password: 原始密码
        salt: 盐值（可选）
        
    Returns:
        (加密后的密码, 盐值)
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    # 双重 hash：salt + password
    password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return password_hash, salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """
    验证密码
    
    Args:
        password: 原始密码
        password_hash: 加密后的密码
        salt: 盐值
        
    Returns:
        验证是否通过
    """
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == password_hash


def create_token(user_id: str, username: str, expires_in: int = 3600) -> Dict:
    """
    创建访问令牌
    
    Args:
        user_id: 用户 ID
        username: 用户名
        expires_in: 过期时间（秒）
        
    Returns:
        token 信息
    """
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    TOKEN_STORE[token] = {
        "user_id": user_id,
        "username": username,
        "expires_at": expires_at,
        "created_at": datetime.utcnow()
    }
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "expires_at": expires_at.isoformat()
    }


def verify_token(token: str) -> Optional[Dict]:
    """
    验证令牌
    
    Args:
        token: 访问令牌
        
    Returns:
        用户信息，如果无效返回 None
    """
    if token not in TOKEN_STORE:
        return None
    
    token_data = TOKEN_STORE[token]
    
    # 检查是否过期
    if datetime.utcnow() > token_data["expires_at"]:
        # 删除过期 token
        del TOKEN_STORE[token]
        return None
    
    return {
        "user_id": token_data["user_id"],
        "username": token_data["username"]
    }


def register_user(username: str, password: str, email: Optional[str] = None) -> Dict:
    """
    注册新用户
    
    Args:
        username: 用户名
        password: 密码
        email: 邮箱（可选）
        
    Returns:
        用户信息
    """
    # 检查用户名是否已存在
    for user in MOCK_USERS_DB.values():
        if user["username"] == username:
            raise AuthError("用户名已存在")
    
    # 创建用户
    user_id = secrets.token_urlsafe(16)
    password_hash, salt = hash_password(password)
    
    user = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "salt": salt,
        "created_at": datetime.utcnow().isoformat()
    }
    
    MOCK_USERS_DB[user_id] = user
    
    return {
        "user_id": user_id,
        "username": username,
        "email": email,
        "created_at": user["created_at"]
    }


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    用户登录认证
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        用户信息和 token，如果认证失败返回 None
    """
    # 查找用户
    user = None
    for u in MOCK_USERS_DB.values():
        if u["username"] == username:
            user = u
            break
    
    if user is None:
        return None
    
    # 验证密码
    if not verify_password(password, user["password_hash"], user["salt"]):
        return None
    
    # 创建 token
    token_info = create_token(user["user_id"], user["username"])
    
    return {
        "user": {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"]
        },
        "token": token_info
    }


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """根据 ID 获取用户"""
    return MOCK_USERS_DB.get(user_id)


def clear_test_data():
    """清理测试数据"""
    MOCK_USERS_DB.clear()
    TOKEN_STORE.clear()
