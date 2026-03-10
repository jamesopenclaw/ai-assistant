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
- ✅ Function Calling: 成功调用、工具不存在、工具异常降级与日志记录
- ✅ Web Search: 结构化返回、参数边界（count clamp）、降级与错误态（缺 key/空 query/上游非 200）
- ✅ 模板服务: 列表、详情、404 错误态

### 集成测试
- ✅ 根端点 `/` 和健康检查 `/health`
- ✅ 聊天 API: 验证、错误处理
- ✅ 技能 API: 列表、详情、切换、404
- ✅ 知识库 API: 端点存在性检查
- ✅ 聊天历史 API: 获取空会话、格式验证
- ✅ 模板 API: 列表、详情、404
- ✅ Function Calling API: 列工具、工具不存在降级
- ✅ 错误处理: 无效 JSON、405、404

## Smoke Checklist（第二轮）

> 目标：覆盖 Function Calling / Web Search / 模板 三块核心路径 + 关键错误态。

### A. Function Calling
- [ ] `GET /api/chat/tools` 返回已注册工具（至少包含 `web_search`）
- [ ] `POST /api/chat/tools/call` 调用不存在工具时：`200` + `ok=false` + 错误信息包含 `not found`
- [ ] `FunctionCaller.call()` 工具成功时：`ok=true` 且写入 `tool_call_logs(status=success)`
- [ ] `FunctionCaller.call()` 工具抛异常时：降级为 `ok=false` 且写入 `tool_call_logs(status=error)`

### B. Web Search
- [ ] 正常返回：输出 `query/total/top_result/results` 结构完整
- [ ] `count` 边界：<1 被提升到 1，>10 被截断到 10
- [ ] 空查询：抛 `ValueError(query is required)`
- [ ] 缺少 `BRAVE_API_KEY`：抛 `RuntimeError(BRAVE_API_KEY is not configured)`
- [ ] 上游非 200：抛 `RuntimeError(web_search failed: <status>)`

### C. 模板
- [ ] `GET /api/templates` 返回列表，元素包含 `id/name/content`
- [ ] `GET /api/templates/{id}` 正常返回对应模板
- [ ] `GET /api/templates/{bad_id}` 返回 `404` + `Template not found`
