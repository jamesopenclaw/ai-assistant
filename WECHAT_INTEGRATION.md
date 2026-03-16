# 企微集成配置指南

## 环境变量配置

在 `.env` 文件中添加以下配置：

```env
# 企业微信配置（必需）
WECHAT_CORP_ID=your_corp_id
WECHAT_CORP_SECRET=your_corp_secret
WECHAT_AGENT_ID=your_agent_id
WECHAT_TOKEN=your_verification_token

# AI Assistant 地址（可选，默认 http://127.0.0.1:8013）
AI_ASSISTANT_URL=http://127.0.0.1:8013
```

## 获取企微配置

1. **登录企微管理后台** https://work.weixin.qq.com/
2. **创建应用** → 获取 `AgentId` 和 `Secret`
3. **获取企业ID** → 我的企业 → 企业信息 → 企业ID
4. **设置API接收** → 创建接收消息的回调URL

## API 接口

### 1. 企微 Webhook

```
GET  /api/webhook/wechat           - 企微验证回调URL
POST /api/webhook/wechat           - 企微消息回调入口
GET  /api/webhook/wechat/config    - 获取配置状态
POST /api/webhook/wechat/test      - 测试发送消息
```

### 2. 定时任务

```
GET    /api/scheduler/tasks              - 任务列表
POST   /api/scheduler/tasks              - 创建任务
DELETE /api/scheduler/tasks/{task_id}    - 删除任务
PATCH  /api/scheduler/tasks/{task_id}    - 更新任务
POST   /api/scheduler/tasks/{task_id}/run - 手动触发
```

## 企微机器人配置步骤

1. 在企微后台创建应用
2. 设置"API接收"：
   - URL: `https://你的域名/api/webhook/wechat`
   - Token: 填写 `WECHAT_TOKEN`
   - EncodingAESKey: 可选
3. 发布应用
4. 在群聊中添加机器人

## 测试

```bash
# 测试企微配置状态
curl http://127.0.0.1:8013/api/webhook/wechat/config

# 创建定时任务
curl -X POST http://127.0.0.1:8013/api/scheduler/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "早报推送",
    "type": "group",
    "target": "your-room-id",
    "content": "早上好！今日简报来了",
    "cron": "0 9 * * *"
  }'
```

## 消息流程

```
企微群消息
    ↓
POST /api/webhook/wechat
    ↓
解析消息（检查@机器人）
    ↓
调用 /api/chat 获取AI回复
    ↓
POST 企微发送消息API
    ↓
回复到群/个人
```
