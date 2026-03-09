"""
用户认证系统测试
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.services import auth_service

client = TestClient(app)

# 测试数据
TEST_USERNAME = "testuser"
TEST_PASSWORD = "TestPassword123"
TEST_EMAIL = "test@example.com"


@pytest.fixture(autouse=True)
def cleanup():
    """每个测试前后清理数据"""
    auth_service.clear_test_data()
    yield
    auth_service.clear_test_data()


class TestPasswordHashing:
    """密码加密存储测试"""

    def test_password_hash_generates_salt(self):
        """测试密码 hash 生成盐值"""
        password_hash, salt = auth_service.hash_password(TEST_PASSWORD)
        
        assert password_hash is not None
        assert len(password_hash) == 64  # SHA-256 输出 64 个十六进制字符
        assert salt is not None
        assert len(salt) > 0

    def test_same_password_different_hash(self):
        """测试相同密码每次生成不同的 hash（因为盐值不同）"""
        hash1, salt1 = auth_service.hash_password(TEST_PASSWORD)
        hash2, salt2 = auth_service.hash_password(TEST_PASSWORD)
        
        assert hash1 != hash2  # 盐值不同导致 hash 不同
        assert salt1 != salt2

    def test_password_verification_success(self):
        """测试密码验证成功"""
        password_hash, salt = auth_service.hash_password(TEST_PASSWORD)
        
        assert auth_service.verify_password(TEST_PASSWORD, password_hash, salt) is True

    def test_password_verification_failure(self):
        """测试密码验证失败"""
        password_hash, salt = auth_service.hash_password(TEST_PASSWORD)
        
        assert auth_service.verify_password("wrong_password", password_hash, salt) is False

    def test_stored_password_is_hash_not_plaintext(self):
        """测试存储的密码是 hash 而不是明文"""
        user = auth_service.register_user(TEST_USERNAME, TEST_PASSWORD, TEST_EMAIL)
        
        # 从数据库获取用户
        stored_user = auth_service.get_user_by_id(user["user_id"])
        
        assert stored_user is not None
        assert stored_user["password_hash"] != TEST_PASSWORD  # 密码不应该是明文
        assert stored_user["password_hash"] != stored_user["salt"]  # 密码不应该是盐值
        assert len(stored_user["password_hash"]) == 64  # SHA-256 hash 长度
        assert stored_user["salt"] is not None

    def test_salt_is_unique_per_user(self):
        """测试每个用户的盐值是唯一的"""
        user1 = auth_service.register_user("user1", TEST_PASSWORD)
        user2 = auth_service.register_user("user2", TEST_PASSWORD)
        
        stored_user1 = auth_service.get_user_by_id(user1["user_id"])
        stored_user2 = auth_service.get_user_by_id(user2["user_id"])
        
        assert stored_user1["salt"] != stored_user2["salt"]


class TestTokenGeneration:
    """Token 生成测试"""

    def test_create_token_returns_valid_structure(self):
        """测试创建 token 返回正确结构"""
        token_info = auth_service.create_token("user123", "testuser")
        
        assert "access_token" in token_info
        assert "token_type" in token_info
        assert "expires_in" in token_info
        assert "expires_at" in token_info
        assert token_info["token_type"] == "bearer"

    def test_token_is_unique(self):
        """测试每次生成的 token 是唯一的"""
        token1 = auth_service.create_token("user123", "testuser")
        token2 = auth_service.create_token("user123", "testuser")
        
        assert token1["access_token"] != token2["access_token"]

    def test_token_contains_user_info(self):
        """测试 token 包含用户信息"""
        token_info = auth_service.create_token("user123", "testuser")
        
        # 验证 token 存储了用户信息
        user_info = auth_service.verify_token(token_info["access_token"])
        
        assert user_info is not None
        assert user_info["user_id"] == "user123"
        assert user_info["username"] == "testuser"


class TestTokenVerification:
    """Token 验证逻辑测试"""

    def test_verify_valid_token(self):
        """测试验证有效 token"""
        token_info = auth_service.create_token("user123", "testuser")
        
        user_info = auth_service.verify_token(token_info["access_token"])
        
        assert user_info is not None
        assert user_info["user_id"] == "user123"

    def test_verify_invalid_token(self):
        """测试验证无效 token"""
        user_info = auth_service.verify_token("invalid_token_12345")
        
        assert user_info is None

    def test_verify_expired_token(self):
        """测试验证过期 token"""
        import time
        # 创建一个立即过期的 token
        token_info = auth_service.create_token("user123", "testuser", expires_in=0)
        
        # 等待 token 过期
        time.sleep(1)
        
        user_info = auth_service.verify_token(token_info["access_token"])
        
        assert user_info is None


class TestRegistrationAPI:
    """注册接口测试"""

    def test_register_success(self):
        """测试注册成功"""
        response = client.post("/api/auth/register", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "email": TEST_EMAIL
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert data["username"] == TEST_USERNAME
        assert data["email"] == TEST_EMAIL

    def test_register_duplicate_username(self):
        """测试重复用户名注册"""
        # 先注册一个用户
        client.post("/api/auth/register", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        # 尝试重复注册
        response = client.post("/api/auth/register", json={
            "username": TEST_USERNAME,
            "password": "different_password"
        })
        
        assert response.status_code == 400
        assert "用户名已存在" in response.json()["detail"]

    def test_register_missing_username(self):
        """测试缺少用户名"""
        response = client.post("/api/auth/register", json={
            "password": TEST_PASSWORD
        })
        
        assert response.status_code == 422

    def test_register_missing_password(self):
        """测试缺少密码"""
        response = client.post("/api/auth/register", json={
            "username": TEST_USERNAME
        })
        
        assert response.status_code == 422

    def test_register_with_email(self):
        """测试带邮箱注册"""
        response = client.post("/api/auth/register", json={
            "username": "newuser",
            "password": TEST_PASSWORD,
            "email": "new@example.com"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "new@example.com"

    def test_register_invalid_email(self):
        """测试无效邮箱"""
        response = client.post("/api/auth/register", json={
            "username": "newuser",
            "password": TEST_PASSWORD,
            "email": "not-an-email"
        })
        
        assert response.status_code == 422


class TestLoginAPI:
    """登录接口测试"""

    def test_login_success(self):
        """测试登录成功"""
        # 先注册用户
        client.post("/api/auth/register", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        # 登录
        response = client.post("/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "access_token" in data["token"]
        assert "user" in data
        assert data["user"]["username"] == TEST_USERNAME

    def test_login_wrong_password(self):
        """测试密码错误登录"""
        # 先注册用户
        client.post("/api/auth/register", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        # 使用错误密码登录
        response = client.post("/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": "wrong_password"
        })
        
        assert response.status_code == 401

    def test_login_nonexistent_user(self):
        """测试不存在的用户登录"""
        response = client.post("/api/auth/login", json={
            "username": "nonexistent",
            "password": TEST_PASSWORD
        })
        
        assert response.status_code == 401

    def test_login_missing_fields(self):
        """测试缺少字段"""
        response = client.post("/api/auth/login", json={
            "username": TEST_USERNAME
        })
        
        assert response.status_code == 422


class TestTokenEndpointAPI:
    """Token 验证接口测试"""

    def test_verify_valid_token(self):
        """测试验证有效 token"""
        # 注册并登录
        client.post("/api/auth/register", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        login_response = client.post("/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        token = login_response.json()["token"]["access_token"]
        
        # 验证 token
        response = client.get(
            "/api/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["user"]["username"] == TEST_USERNAME

    def test_verify_invalid_token(self):
        """测试验证无效 token"""
        response = client.get(
            "/api/auth/verify",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False

    def test_verify_missing_token(self):
        """测试缺少 token"""
        response = client.get("/api/auth/verify")
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False


class TestCurrentUserAPI:
    """当前用户接口测试"""

    def test_get_current_user_success(self):
        """测试获取当前用户成功"""
        # 注册并登录
        client.post("/api/auth/register", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "email": TEST_EMAIL
        })
        
        login_response = client.post("/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        token = login_response.json()["token"]["access_token"]
        
        # 获取当前用户
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == TEST_USERNAME
        assert data["email"] == TEST_EMAIL

    def test_get_current_user_no_token(self):
        """测试未授权获取当前用户"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self):
        """测试无效 token 获取当前用户"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401


class TestLogoutAPI:
    """登出接口测试"""

    def test_logout_success(self):
        """测试登出成功"""
        # 注册并登录
        client.post("/api/auth/register", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        login_response = client.post("/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        token = login_response.json()["token"]["access_token"]
        
        # 登出
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        
        # 验证 token 已失效
        verify_response = client.get(
            "/api/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert verify_response.json()["valid"] is False

    def test_logout_without_token(self):
        """测试无 token 登出"""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == 200


class TestSecurityScenarios:
    """安全场景测试"""

    def test_cannot_login_with_plaintext_password(self):
        """测试不能使用明文密码登录（密码被加密存储）"""
        # 注册用户
        client.post("/api/auth/register", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        # 获取存储的用户信息
        from app.services.auth_service import MOCK_USERS_DB
        user = list(MOCK_USERS_DB.values())[0]
        
        # 尝试使用存储的 password_hash 登录（这不应该成功）
        response = client.post("/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": user["password_hash"]  # 使用 hash 而不是原始密码
        })
        
        assert response.status_code == 401

    def test_token_not_in_response_password(self):
        """测试 token 响应中不包含密码信息"""
        client.post("/api/auth/register", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        response = client.post("/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        data = response.json()
        # 确认响应中没有密码
        assert "password" not in str(data)
        assert "password_hash" not in str(data)
        assert "salt" not in str(data)

    def test_different_salt_prevents_rainbow_table(self):
        """测试不同盐值防止彩虹表攻击"""
        user1 = auth_service.register_user("user1", "samepassword")
        user2 = auth_service.register_user("user2", "samepassword")
        
        stored_user1 = auth_service.get_user_by_id(user1["user_id"])
        stored_user2 = auth_service.get_user_by_id(user2["user_id"])
        
        # 相同密码但 hash 不同（因为盐值不同）
        assert stored_user1["password_hash"] != stored_user2["password_hash"]
