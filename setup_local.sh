#!/bin/bash
# AI Assistant 本地开发环境启动脚本

set -e

echo "🚀 启动本地开发环境..."

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker Desktop"
    exit 1
fi

# 启动 Docker Compose
echo "📦 启动 PostgreSQL..."
docker-compose up -d

# 等待数据库就绪
echo "⏳ 等待数据库就绪..."
sleep 5

# 检查数据库连接
for i in {1..10}; do
    if docker exec ai-assistant-postgres pg_isready -U app_user -d ai_assistant > /dev/null 2>&1; then
        echo "✅ PostgreSQL 已就绪"
        break
    fi
    echo "⏳ 等待数据库启动... ($i/10)"
    sleep 2
done

# 复制环境配置
if [ ! -f .env ]; then
    echo "📝 复制环境配置文件..."
    cp .env.docker .env
    echo "⚠️  请编辑 .env 文件，添加你的 API Key"
else
    echo "✅ .env 文件已存在"
fi

echo ""
echo "🎉 环境启动完成！"
echo ""
echo "下一步："
echo "1. 编辑 .env 添加你的 MINIMAX_API_KEY"
echo "2. 启动后端: cd app && uvicorn main:app --reload --port 8013"
echo "3. 启动前端: cd ui/ai-assistant-pro && npm run dev"
echo ""
echo "停止数据库: docker-compose down"
