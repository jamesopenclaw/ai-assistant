# AI Assistant Pro

基于大模型的企业级 AI 客服系统，支持多租户、知识库问答和智能客服切换。

## 🎯 项目简介

AI Assistant Pro 是一个企业级 SaaS 平台，帮助企业构建智能客服系统。支持 AI 对话、知识库 RAG、关键词自动回复、人工客服切换等功能。

## 🛠 技术栈

- **后端**: FastAPI + Python 3.11
- **前端**: React + Ant Design Pro + Umi
- **AI 模型**: MiniMax / OpenAI 兼容
- **RAG**: LangChain + Chroma
- **存储**: SQLite / PostgreSQL

## ✨ 核心功能

### 多租户 SaaS
- ✅ 租户管理 (Tenant)
- ✅ 用户管理 (User) + 角色权限
- ✅ 用量统计 (Usage)

### 对话能力
- ✅ AI 对话
- ✅ 知识库问答（RAG：PDF/Word/TXT/MD）
- ✅ 提示词模板
- ✅ Function Calling 工具

### 客服系统
- ✅ AI → 人工客服切换
- ✅ 客服上下线管理
- ✅ 自动分配空闲客服
- ✅ 会话转移

### 管理功能
- ✅ 会话管理（置顶/星标/搜索/导出）
- ✅ 关键词自动回复（精确/模糊/正则）
- ✅ 企业微信集成（Webhook）
- ✅ 定时任务推送

### 前端页面
- ✅ AI 聊天页面
- ✅ 知识库管理
- ✅ 会话管理
- ✅ 用户管理
- ✅ 关键词规则管理
- ✅ 客服管理
- ✅ 登录/注册

## 📁 项目结构

```
ai-assistant/
├── app/
│   ├── api/              # API 路由
│   │   ├── auth.py       # 认证
│   │   ├── chat.py       # 对话
│   │   ├── knowledge.py  # 知识库
│   │   ├── tenants.py    # 租户
│   │   ├── users.py      # 用户
│   │   ├── sessions.py   # 会话
│   │   ├── autoreply.py  # 关键词回复
│   │   ├── customer_service.py # 客服
│   │   ├── scheduler.py  # 定时任务
│   │   └── webhook_wechat.py  # 企微集成
│   ├── models/           # 数据模型
│   ├── services/         # 业务逻辑
│   └── main.py          # 应用入口
├── ui/
│   └── ai-assistant-pro/  # React 前端
├── .github/
│   └── workflows/       # CI/CD
└── requirements.txt     # Python 依赖
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/jamesopenclaw/ai-assistant.git
cd ai-assistant
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 添加必要的配置
```

必需配置：
```env
MINIMAX_API_KEY=your_api_key
```

企微配置（可选）：
```env
WECHAT_CORP_ID=your_corp_id
WECHAT_CORP_SECRET=your_secret
WECHAT_AGENT_ID=your_agent_id
WECHAT_TOKEN=your_token
```

### 4. 启动服务

```bash
# 启动后端 (端口 8013)
uvicorn app.main:app --host 0.0.0.0 --port 8013

# 或使用后台运行
nohup uvicorn app.main:app --host 0.0.0.0 --port 8013 > app.log 2>&1 &
```

### 5. 访问

- 后端 API: http://localhost:8013
- 前端: http://localhost:8013 (需先构建)
- API 文档: http://localhost:8013/docs

### 6. 前端构建

```bash
cd ui/ai-assistant-pro
npm install
npm run build
```

## 📡 API 接口

| 模块 | 前缀 | 说明 |
|------|------|------|
| 认证 | `/api/auth` | 登录/注册 |
| 对话 | `/api/chat` | AI 对话 |
| 知识库 | `/api/knowledge` | RAG |
| 租户 | `/api/tenants` | 多租户 |
| 用户 | `/api/users` | 用户管理 |
| 会话 | `/api/sessions` | 会话管理 |
| 关键词 | `/api/autoreply` | 自动回复 |
| 客服 | `/api/customer-service` | 客服切换 |
| 企微 | `/api/webhook/wechat` | 企微集成 |
| 用量 | `/api/usage` | 统计 |

## 🔧 开发

```bash
# 开发模式
uvicorn app.main:app --reload --port 8013

# 运行测试
pytest tests/

# 代码检查
ruff check .
flake8 .
```

## 📝 版本记录

### v1.0.0 (2026-03)
- 多租户 SaaS 架构
- AI 对话 + 知识库 RAG
- 关键词自动回复
- 人工客服切换
- 企业微信集成

## 📄 许可证

MIT License
