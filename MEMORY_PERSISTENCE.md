# 对话记忆持久化配置

## 功能说明

AI Assistant Pro 支持对话历史自动持久化，重启服务后对话历史不丢失。

## 工作原理

- 消息自动保存到 SQLite 数据库 (`/tmp/chat_history.db`)
- 每次对话后自动加载历史上下文
- 支持多租户隔离

## 配置

### 数据库路径

在 `.env` 中配置：

```env
CHAT_DB_PATH=/tmp/chat_history.db
```

### 切换到 PostgreSQL（生产环境）

```env
DATABASE_URL=postgresql://user:password@localhost/ai_assistant
```

切换后需要修改 `app/services/chat_service.py` 中的数据库连接逻辑。

## API

```bash
# 获取会话消息历史
GET /api/sessions/{session_id}/messages

# 导出对话
GET /api/sessions/{session_id}/export?format=json|markdown|text
```

## 数据清理

```bash
# 删除历史消息（可选）
# 直接删除数据库文件
rm /tmp/chat_history.db

# 重启服务后会自动创建新数据库
```
