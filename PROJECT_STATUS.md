# WRHITW 项目进度报告
**日期**: 2026-03-05  
**状态**: MVP 开发完成

---

## 📊 项目概览

**WRHITW** (What's Really Happening In The World) - 多视角新闻聚合平台

**核心理念**: 让世界看到完整的故事，而不是单一的视角

---

## ✅ 已完成功能

### 1️⃣ 后端 API (FastAPI + Python)

**技术栈**:
- FastAPI (现代 Python Web 框架)
- SQLAlchemy (ORM)
- SQLite (开发数据库)
- Pydantic (数据验证)

**API 端点**:
```
GET    /api/events          # 获取事件列表
GET    /api/events/{id}     # 获取事件详情
POST   /api/events          # 创建事件
PUT    /api/events/{id}     # 更新事件
DELETE /api/events/{id}     # 删除事件
GET    /api/events/{id}/sources   # 获取事件来源
GET    /api/events/{id}/summary   # 获取 AI 摘要
```

**数据模型** (6 个表):
- `events` - 事件表
- `sources` - 信息源表
- `event_sources` - 事件 - 来源关联表
- `ai_summaries` - AI 摘要表
- `users` - 用户表
- `reading_history` / `bookmarks` - 阅读历史/收藏

**文件位置**:
```
wrhitw/apps/api/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── core/database.py     # 数据库配置
│   ├── models/__init__.py   # SQLAlchemy 模型
│   ├── schemas/__init__.py  # Pydantic 验证模型
│   ├── routes/events.py     # 事件 API 路由
│   └── services/ai_prompts.py  # AI 提示词模板
├── fetch_rss_news.py        # RSS 新闻抓取脚本
└── wrhitw.db                # SQLite 数据库
```

**当前状态**:
- ✅ 运行在 http://localhost:8080
- ✅ 16 个事件（6 个手动 + 10 个 RSS）
- ✅ API 文档：http://localhost:8080/docs

---

### 2️⃣ 前端页面 (Next.js 14 + React)

**技术栈**:
- Next.js 14 (React 框架)
- TypeScript
- Tailwind CSS (样式)
- React Hooks (状态管理)

**核心页面**:
- 首页 (`/`) - 故事化杂志风格
- 分类筛选 - 环境/财经/科技/政治
- 响应式设计 - 支持移动端

**特色功能**:
- 📖 故事化叙事（封面故事 + 故事引子）
- 🎨 分类配色系统
- ✨ 悬停动画效果
- 🔄 实时数据刷新
- 🌐 API 对接完成

**文件位置**:
```
wrhitw/apps/web/
├── src/
│   ├── app/
│   │   ├── page.tsx         # 首页（故事化设计）
│   │   └── layout.tsx       # 布局
│   ├── components/
│   │   ├── Header.tsx       # 页头
│   │   ├── EventCard.tsx    # 事件卡片
│   │   └── BiasBadge.tsx    # 偏见标签
│   └── styles/
│       └── globals.css      # 全局样式
└── .env.local               # 环境变量
```

**当前状态**:
- ✅ 运行在 http://localhost:3000
- ✅ 对接真实 API 数据
- ✅ 故事化界面展示

---

### 3️⃣ 数据获取系统

**RSS 新闻抓取器** (`fetch_rss_news.py`):
- ✅ BBC World (国际新闻)
- ✅ TechCrunch (科技新闻)
- 🔄 Reuters (网络问题)
- 🔄 The Verge (格式问题)

**工作流程**:
```
RSS Feed → feedparser 解析 → 数据清洗 → SQLite 存储 → API 读取 → 前端展示
```

**运行方式**:
```bash
cd wrhitw/apps/api
./venv/bin/python fetch_rss_news.py
```

---

## 📁 完整项目结构

```
wrhitw/
├── apps/
│   ├── api/                 # 后端 FastAPI
│   │   ├── app/
│   │   ├── venv/            # Python 虚拟环境
│   │   ├── fetch_rss_news.py
│   │   └── wrhitw.db
│   └── web/                 # 前端 Next.js
│       ├── src/
│       ├── node_modules/
│       └── .env.local
├── docs/                    # 文档
│   ├── AI_PROMPTS.md
│   ├── DATABASE_SCHEMA.sql
│   └── DESIGN.md
└── README.md
```

---

## 🎓 学习路径指南

### 🐍 后端开发 (Python/FastAPI)

**已涉及知识点**:
1. ✅ FastAPI 路由和端点
2. ✅ SQLAlchemy ORM 模型
3. ✅ Pydantic 数据验证
4. ✅ SQLite 数据库操作
5. ✅ CORS 跨域配置
6. ✅ RSS 数据抓取

**深入学习**:
1. **FastAPI 进阶**
   - 依赖注入系统
   - 中间件开发
   - WebSocket 实时通信
   - 背景任务处理
   
   📚 资源: https://fastapi.tiangolo.com/tutorial/

2. **SQLAlchemy 高级**
   - 复杂查询优化
   - 关系加载策略
   - 数据库迁移 (Alembic)
   
   📚 资源: https://docs.sqlalchemy.org/

3. **API 设计最佳实践**
   - RESTful 规范
   - 版本控制
   - 错误处理
   - 认证授权 (JWT)

**练习项目**:
- [ ] 添加用户认证系统
- [ ] 实现分页和过滤
- [ ] 添加 API 速率限制

---

### ⚛️ 前端开发 (Next.js/React)

**已涉及知识点**:
1. ✅ Next.js App Router
2. ✅ React Hooks (useState, useEffect)
3. ✅ Tailwind CSS 样式
4. ✅ 组件化开发
5. ✅ API 数据获取
6. ✅ 响应式设计

**深入学习**:
1. **Next.js 进阶**
   - 服务端渲染 (SSR)
   - 静态站点生成 (SSG)
   - API Routes
   - 图片优化
   
   📚 资源: https://nextjs.org/docs

2. **React 高级概念**
   - Context API
   - 自定义 Hooks
   - 性能优化
   - 状态管理 (Zustand/Redux)
   
   📚 资源: https://react.dev/

3. **TypeScript**
   - 类型系统
   - 泛型
   - 类型守卫
   
   📚 资源: https://www.typescriptlang.org/docs/

**练习项目**:
- [ ] 创建事件详情页面
- [ ] 添加搜索功能
- [ ] 实现暗色模式

---

### 🗄️ 数据库 (SQLite/PostgreSQL)

**已涉及知识点**:
1. ✅ 表结构设计
2. ✅ CRUD 操作
3. ✅ 外键关系
4. ✅ 类型转换 (UUID/ARRAY)

**深入学习**:
1. **SQL 基础**
   - SELECT/INSERT/UPDATE/DELETE
   - JOIN 查询
   - 索引优化
   
   📚 资源: https://www.sqlbolt.com/

2. **数据库设计**
   - 范式理论
   - ER 图设计
   - 性能优化

3. **PostgreSQL 迁移**
   - 从 SQLite 迁移
   - 高级数据类型
   - 全文搜索

**练习项目**:
- [ ] 设计用户系统表结构
- [ ] 优化查询性能
- [ ] 添加全文搜索

---

### 🤖 AI 集成 (可选)

**已涉及知识点**:
1. ✅ AI 提示词设计
2. ✅ 百炼 API 调用

**深入学习**:
1. **Prompt Engineering**
   - 结构化提示
   - Few-shot learning
   - Chain of Thought

2. **AI 应用开发**
   - 文本摘要
   - 情感分析
   - 实体识别

**练习项目**:
- [ ] 实现 AI 多视角摘要
- [ ] 自动偏见分析
- [ ] 新闻分类模型

---

## 🚀 部署上线

### 前端 (Vercel)
```bash
# 1. 安装 Vercel CLI
npm i -g vercel

# 2. 部署
cd wrhitw/apps/web
vercel

# 3. 配置环境变量
NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

### 后端 (Railway)
```bash
# 1. 安装 Railway CLI
npm i -g @railway/cli

# 2. 部署
cd wrhitw/apps/api
railway up

# 3. 配置数据库
railway add postgresql
```

**成本**: ¥0 (免费层)

---

## 📝 下一步建议

### 短期 (本周)
1. ✨ 创建事件详情页面
2. ⏰ 设置定时 RSS 抓取
3. 🧪 编写单元测试

### 中期 (本月)
1. 🤖 实现 AI 摘要生成
2. 👤 添加用户系统
3. 🚀 部署上线

### 长期 (下月)
1. 📱 移动端优化
2. 📊 数据分析面板
3. 🌍 更多新闻源

---

## 💡 关键技术决策

| 决策 | 选择 | 原因 |
|------|------|------|
| 后端框架 | FastAPI | 现代、快速、自动文档 |
| 前端框架 | Next.js 14 | SSR/SSG、SEO 友好 |
| 数据库 (开发) | SQLite | 零配置、便携 |
| 数据库 (生产) | PostgreSQL | 强大、可扩展 |
| 部署 | Vercel + Railway | 免费层够用 |
| 样式 | Tailwind CSS | 快速开发、一致性强 |

---

## 🎯 核心价值主张

**WRHITW 解决的问题**:
1. 信息茧房 - 只看得到单一视角
2. 媒体偏见 - 难以识别立场倾向
3. 信息过载 - 没时间看多篇报道

**我们的方案**:
1. 多源聚合 - 同一事件，多个媒体
2. AI 摘要 - 左/中/右三视角
3. 偏见分析 - 识别媒体立场

---

## 📞 常用命令速查

### 后端
```bash
# 启动 API
cd wrhitw/apps/api
./venv/bin/uvicorn app.main:app --reload --port 8080

# 抓取 RSS
./venv/bin/python fetch_rss_news.py

# 查看 API 文档
open http://localhost:8080/docs
```

### 前端
```bash
# 启动开发服务器
cd wrhitw/apps/web
pnpm dev

# 构建生产版本
pnpm build
pnpm start
```

---

**最后更新**: 2026-03-05  
**维护者**: WRHITW Team
