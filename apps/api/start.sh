#!/bin/bash

# WRHITW 后端启动脚本

set -e

echo "🚀 启动 WRHITW 后端..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔌 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt -q

# 创建 .env 文件（如果不存在）
if [ ! -f ".env" ]; then
    echo "⚙️  创建 .env 文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件配置数据库和 API key"
fi

# 启动服务
echo "🌐 启动 FastAPI 服务..."
echo "📖 API 文档：http://localhost:8000/docs"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
