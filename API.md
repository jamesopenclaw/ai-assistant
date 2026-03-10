# AI Assistant API 文档

Base URL: `http://127.0.0.1:8013`

---

## 0. 配置
在启动服务前配置 `.env`：

```env
MINIMAX_API_KEY=your-minimax-key
BRAVE_API_KEY=your-brave-key
TOOL_MAX_RETRIES=1
WEB_SEARCH_TIMEOUT_SECONDS=8
WEB_SEARCH_CACHE_TTL_SECONDS=600
```

说明：
- `BRAVE_API_KEY` 用于 `web_search` tool
- `WEB_SEARCH_CACHE_TTL_SECONDS` 限制在 `300-900` 秒（5-15 分钟）

---

## 1. 聊天接口

### POST /api/chat
发送消息。

Request:
```json
{
  "session_id": "会话ID",
  "message": "用户消息",
  "skill_id": "技能ID(可选，默认general)"
}
```

Response:
```json
{
  "session_id": "会话ID",
  "reply": "AI回复",
  "timestamp": "2026-03-07T08:30:00"
}
```

### GET /api/chat/history/{session_id}
获取会话历史。

---

## 2. Function Calling（Tools）

### GET /api/chat/tools
列出已注册 tools（含参数 schema）。

示例返回：
```json
[
  {
    "name": "web_search",
    "description": "Search the web and return structured summaries",
    "args_schema": {
      "type": "object",
      "required": ["query"],
      "properties": {
        "query": {"type": "string"},
        "count": {"type": "integer", "minimum": 1, "maximum": 10}
      }
    }
  }
]
```

### POST /api/chat/tools/call
统一 tool 调用入口。

Request:
```json
{
  "tool_name": "web_search",
  "args": {
    "query": "FastAPI tutorial",
    "count": 3
  }
}
```

Response:
```json
{
  "ok": true,
  "tool": "web_search",
  "result": {
    "query": "FastAPI tutorial",
    "total": 3,
    "top_result": {},
    "results": [],
    "source": "api"
  },
  "error": null
}
```

行为说明：
- 参数会按 `args_schema` 做最小校验（required/type/min/max）
- tool 失败后按 `TOOL_MAX_RETRIES` 自动重试

---

## 3. Templates

### GET /api/templates
列出模板。

### GET /api/templates/{template_id}
获取模板详情。

---

## 4. Skills

### GET /api/skills
技能列表。

### POST /api/skills/{skill_id}/toggle
启用/禁用技能。

---

## 5. 知识库

### GET /api/knowledge/list
文档列表。

### POST /api/knowledge/add
上传文档（multipart/form-data）。
