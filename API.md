# AI Assistant API 文档

Base URL: `http://127.0.0.1:8013`

---

## 1. 聊天接口

### 发送消息
```
POST /api/chat
```

**Request:**
```json
{
  "session_id": "会话ID",
  "message": "用户消息",
  "skill_id": "技能ID(可选，默认general)"
}
```

**Response:**
```json
{
  "session_id": "会话ID",
  "reply": "AI回复",
  "timestamp": "2026-03-07T08:30:00"
}
```

### 获取历史
```
GET /api/chat/history/{session_id}
```

**Response:**
```json
[
  {"role": "user", "content": "消息内容", "timestamp": "..."},
  {"role": "assistant", "content": "回复内容", "timestamp": "..."}
]
```

---

## 2. 技能接口

### 技能列表
```
GET /api/skills
```

**Response:**
```json
[
  {
    "id": "general",
    "name": "通用助手",
    "description": "日常对话",
    "prompt": "你是一个...",
    "enabled": true
  }
]
```

### 切换技能
```
POST /api/skills/{skill_id}/toggle
```

---

## 3. 知识库接口

### 文档列表
```
GET /api/knowledge/list
```

### 上传文档
```
POST /api/knowledge/add
Content-Type: multipart/form-data

file: [文件]
```

支持格式：PDF, Word, TXT, Markdown
