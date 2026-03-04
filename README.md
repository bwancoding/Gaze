# WRHITW - What's Really Happening In The World

🌍 **让世界看到完整的故事，而不是单一的视角。**

WRHITW 是一个多视角新闻聚合平台，通过 AI 技术帮助用户快速了解事件的多方观点，识别信息偏见，形成独立的判断。

---

## 📦 项目结构

```
wrhitw/
├── apps/
│   ├── web/          # Next.js 14 前端
│   └── api/          # FastAPI 后端
├── packages/
│   └── design-system/ # 设计系统
├── docs/             # 文档
└── scripts/          # 工具脚本
```

---

## 🚀 快速开始

### 前端开发

```bash
cd apps/web
pnpm install
pnpm dev
```

### 后端开发

```bash
cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 📚 文档

- [产品需求文档](./docs/PRD.md)
- [设计系统](./docs/DESIGN.md)
- [API 文档](./docs/API.md)

---

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 14, React, Tailwind CSS, TypeScript |
| 后端 | Python 3.11+, FastAPI, SQLAlchemy |
| 数据库 | PostgreSQL, Supabase |
| 部署 | Vercel (前端), Railway (后端) |
| AI | 百炼 (qwen3.5-plus) |

---

## 📝 开发进度

- [x] 项目初始化
- [ ] 设计系统建立
- [ ] 数据库 schema 设计
- [ ] AI 提示词模板
- [ ] 前端脚手架
- [ ] 后端 API 开发
- [ ] MVP 上线

---

## 📄 许可证

MIT License

---

**最后更新**: 2026-03-04
