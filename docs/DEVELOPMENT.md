# WRHITW 开发指南

🚀 **快速开始开发 WRHITW 项目**

---

## 📦 前置要求

- Node.js 18+ 
- pnpm 8+
- Python 3.11+
- PostgreSQL 15+ (本地开发可用 Docker)

---

## 🌐 前端开发

### 安装依赖

```bash
cd apps/web
pnpm install
```

### 启动开发服务器

```bash
pnpm dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
pnpm build
pnpm start
```

---

## 🔧 后端开发

### 创建虚拟环境

```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate  # Windows
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动开发服务器

```bash
uvicorn app.main:app --reload
```

访问 http://localhost:8000

### API 文档

访问 http://localhost:8000/docs 查看 Swagger UI

---

## 🗄️ 数据库设置

### 使用 Docker 启动 PostgreSQL

```bash
docker run -d \
  --name wrhitw-db \
  -e POSTGRES_USER=wrhitw \
  -e POSTGRES_PASSWORD=wrhitw \
  -e POSTGRES_DB=wrhitw \
  -p 5432:5432 \
  postgres:15
```

### 初始化数据库

```bash
psql -U wrhitw -d wrhitw -f docs/DATABASE_SCHEMA.sql
```

### 使用 Prisma（推荐）

```bash
cd apps/api
npx prisma generate
npx prisma db push
npx prisma studio  # 可视化数据库管理
```

---

## 🎨 设计系统

设计系统文档位于：`docs/DESIGN.md`

### Figma 设计文件

📎 [WRHITW Design System](https://www.figma.com/file/TODO) *(待创建)*

---

## 🤖 AI 配置

### 配置 API Key

创建 `.env` 文件：

```bash
# 百炼 AI
DASHSCOPE_API_KEY=sk-xxx

# 数据库
DATABASE_URL=postgresql://wrhitw:wrhitw@localhost:5432/wrhitw
```

---

## 📝 开发工作流

### 1. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 开发并提交

```bash
git add .
git commit -m "feat: 添加 xxx 功能"
```

### 3. 推送到远程

```bash
git push origin feature/your-feature-name
```

### 4. 创建 Pull Request

在 GitHub 上创建 PR，等待 code review

---

## 🧪 测试

### 前端测试

```bash
cd apps/web
pnpm test
```

### 后端测试

```bash
cd apps/api
pytest
```

---

## 📊 项目结构

```
wrhitw/
├── apps/
│   ├── web/              # Next.js 前端
│   │   ├── src/
│   │   │   ├── app/      # App Router
│   │   │   ├── components/
│   │   │   └── styles/
│   │   └── package.json
│   │
│   └── api/              # FastAPI 后端
│       ├── app/
│       │   ├── main.py
│       │   ├── routes/
│       │   ├── models/
│       │   └── services/
│       └── requirements.txt
│
├── packages/
│   └── design-system/    # 共享设计系统
│
├── docs/
│   ├── PRD.md            # 产品需求
│   ├── DESIGN.md         # 设计系统
│   ├── DATABASE_SCHEMA.sql
│   ├── AI_PROMPTS.md
│   └── DEVELOPMENT.md    # 这个文件
│
└── scripts/              # 工具脚本
```

---

## 🐛 常见问题

### 端口被占用

```bash
# 查看占用端口的进程
lsof -i :3000
# 杀死进程
kill -9 <PID>
```

### 依赖安装失败

```bash
# 清除缓存
pnpm store prune
# 重新安装
rm -rf node_modules
pnpm install
```

### 数据库连接失败

```bash
# 检查 PostgreSQL 是否运行
docker ps | grep wrhitw-db
# 重启容器
docker restart wrhitw-db
```

---

## 📚 参考资料

- [Next.js 文档](https://nextjs.org/docs)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Prisma 文档](https://www.prisma.io/docs)

---

**最后更新**: 2026-03-04  
**状态**: 🟡 开发中
