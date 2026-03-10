# AI Assistant MVP

基于大模型的企业级 AI 对话 + 知识库问答系统。

## 技术栈
- 后端: FastAPI
- 模型: MiniMax/OpenAI 兼容调用
- RAG: LangChain + Chroma
- 存储: SQLite + Chroma

## 功能
- 🤖 AI 对话
- 📚 知识库问答（PDF/Word/TXT/MD）
- 🧩 Templates（提示词模板）
- 🛠️ Tools（Function Calling）
- 💾 聊天记录持久化

## 快速开始
```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8013
```

Docker:
```bash
docker-compose up -d
```

## 环境变量
最少需要：
- `MINIMAX_API_KEY`: 模型调用
- `BRAVE_API_KEY`: web_search 工具调用 Brave Search API

可选（工具增强）：
- `TOOL_MAX_RETRIES`（默认 `1`）: Function Calling 失败重试次数
- `WEB_SEARCH_TIMEOUT_SECONDS`（默认 `8`）: web_search 请求超时
- `WEB_SEARCH_CACHE_TTL_SECONDS`（默认 `600`，强制范围 300-900）: web_search 缓存 TTL

## Tools / Templates 调用
### 列出 tools
```bash
curl http://127.0.0.1:8013/api/chat/tools
```

### 调用 tool（web_search）
```bash
curl -X POST http://127.0.0.1:8013/api/chat/tools/call \
  -H 'Content-Type: application/json' \
  -d '{"tool_name":"web_search","args":{"query":"FastAPI tutorial","count":3}}'
```

### 列出 templates
```bash
curl http://127.0.0.1:8013/api/templates
```

### 获取单个 template
```bash
curl http://127.0.0.1:8013/api/templates/general-qa
```

## 测试
```bash
pytest -q
```
