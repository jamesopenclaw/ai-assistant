# 测试说明

## 测试文件

- `test_skills.py` - 技能模块单元测试
- `test_schemas.py` - 数据模型单元测试
- `test_chat_service.py` - 聊天服务单元测试
- `test_api.py` - API 集成测试

## 安装测试依赖

```bash
pip install -r requirements-dev.txt
```

或者使用 uv:

```bash
uv pip install -r requirements-dev.txt
```

## 运行测试

### 运行所有测试
```bash
pytest
```

### 运行特定测试文件
```bash
pytest tests/test_skills.py
pytest tests/test_api.py
```

### 运行特定测试类
```bash
pytest tests/test_skills.py::TestSkills
pytest tests/test_api.py::TestChatAPI
```

### 运行特定测试用例
```bash
pytest tests/test_skills.py::TestSkills::test_list_skills -v
```

### 查看详细输出
```bash
pytest -v
```

### 显示 print 输出
```bash
pytest -s
```

## 测试覆盖

### 单元测试
- ✅ 技能模块: 列表、详情、切换、字段验证
- ✅ 数据模型: Message, ChatRequest, ChatResponse, Skill, Document, KnowledgeAddRequest
- ✅ 聊天服务: 消息保存、历史获取、时间戳、多会话隔离

### 集成测试
- ✅ 根端点 `/` 和健康检查 `/health`
- ✅ 聊天 API: 验证、错误处理
- ✅ 技能 API: 列表、详情、切换、404
- ✅ 知识库 API: 端点存在性检查
- ✅ 聊天历史 API: 获取空会话、格式验证
- ✅ 错误处理: 无效 JSON、405、404
