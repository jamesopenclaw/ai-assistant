# AI Assistant MVP

基于大模型的企业级 AI 对话 + 知识库问答系统

## 技术栈

- **后端**: Python/FastAPI
- **AI**: OpenAI API (GPT-4)
- **RAG**: LangChain + Chroma 向量数据库
- **数据库**: SQLite (聊天记录) + Chroma (向量)
- **部署**: Docker

## 功能

- 🤖 AI 对话 - 基于大模型的智能对话
- 📚 知识库问答 - RAG 方案，支持 PDF/Word/TXT/MD
- 💬 技能卡片 - 可配置的 AI 技能
- 💾 聊天记录 - 持久化存储

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
uvicorn app.main:app --reload

# Docker
docker-compose up -d
```

## API

- `POST /api/chat` - 发送消息
- `GET /api/chat/history/{session_id}` - 获取历史
- `POST /api/knowledge/add` - 添加文档
- `GET /api/knowledge/list` - 文档列表
- `GET /api/skills` - 技能列表
- `POST /api/skills/{skill_id}/toggle` - 启用/禁用技能
