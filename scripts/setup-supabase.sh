#!/bin/bash
# WRHITW Supabase 快速设置脚本
# 使用方法：./setup-supabase.sh

set -e

echo "=============================================="
echo "WRHITW Supabase 快速设置"
echo "=============================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python 版本
echo -e "\n${YELLOW}检查 Python 版本...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python $python_version"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}错误：pip3 未安装${NC}"
    exit 1
fi

# 进入项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# 安装依赖
echo -e "\n${YELLOW}安装 Supabase 依赖...${NC}"
pip3 install -r apps/api/requirements-supabase.txt

# 检查 .env 文件
if [ ! -f "apps/api/.env" ]; then
    echo -e "\n${YELLOW}创建 .env 文件...${NC}"
    cp apps/api/.env.example apps/api/.env
    echo -e "${GREEN}✅ .env 文件已创建${NC}"
    echo -e "${YELLOW}请编辑 apps/api/.env 并填入 SUPABASE_DATABASE_URL${NC}"
else
    echo -e "\n${GREEN}✅ .env 文件已存在${NC}"
fi

# 检查数据库文件
if [ ! -f "apps/api/wrhitw.db" ]; then
    echo -e "\n${YELLOW}警告：SQLite 数据库文件不存在${NC}"
    echo "跳过数据迁移步骤"
    SKIP_MIGRATION=true
else
    echo -e "\n${GREEN}✅ SQLite 数据库文件存在${NC}"
    SKIP_MIGRATION=false
fi

# 显示使用说明
echo ""
echo "=============================================="
echo "设置完成！"
echo "=============================================="
echo ""
echo "下一步操作："
echo ""
echo "1. 创建 Supabase 项目"
echo "   访问：https://supabase.com"
echo ""
echo "2. 获取数据库连接 URL"
echo "   Dashboard → Settings → Database → Connection string"
echo ""
echo "3. 编辑 .env 文件"
echo "   nano apps/api/.env"
echo "   填入：SUPABASE_DATABASE_URL=postgresql://..."
echo ""
echo "4. 执行数据库 Schema"
echo "   在 Supabase SQL Editor 中运行："
echo "   docs/supabase_schema.sql"
echo ""
echo "5. 迁移数据"
if [ "$SKIP_MIGRATION" = false ]; then
    echo "   python scripts/migrate_to_supabase.py \\"
    echo "     --sqlite apps/api/wrhitw.db \\"
    echo "     --supabase-url \"postgresql://...\""
else
    echo "   (跳过 - SQLite 数据库不存在)"
fi
echo ""
echo "6. 启动 API 服务"
echo "   cd apps/api"
echo "   uvicorn app.main:app --reload"
echo ""
echo "详细文档：docs/MIGRATION_TO_SUPABASE.md"
echo ""
echo -e "${GREEN}=============================================="
echo "祝迁移顺利！🚀"
echo "==============================================${NC}"
