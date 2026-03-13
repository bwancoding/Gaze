# WRHITW Supabase 迁移 - 快速入门

> 🚀 从 SQLite 迁移到 Supabase PostgreSQL，支持高并发

---

## ⚡ 5 分钟快速开始

```bash
# 1. 安装依赖
cd wrhitw
pip install -r apps/api/requirements-supabase.txt

# 2. 创建 Supabase 项目
# 访问 https://supabase.com → New Project

# 3. 获取数据库 URL 并运行迁移
python scripts/migrate_to_supabase.py \
  --sqlite apps/api/wrhitw.db \
  --supabase-url "postgresql://postgres:[密码]@db.xxx.supabase.co:5432/postgres"
```

---

## 📁 文件结构

```
wrhitw/docs/
├── README_SUPABASE.md          # 本文档 (快速入门)
├── MIGRATION_TO_SUPABASE.md    # 完整迁移指南 (详细步骤)
├── MIGRATION_SUMMARY.md        # 迁移摘要 (交付物清单)
├── supabase_schema.sql         # PostgreSQL Schema (执行这个!)
├── sqlite_schema.sql           # SQLite Schema 备份
└── DATABASE_SCHEMA.sql         # 原始 schema 文档

wrhitw/scripts/
├── migrate_to_supabase.py      # 迁移脚本
└── setup-supabase.sh           # 快速设置脚本

wrhitw/apps/api/
├── app/core/database.py        # 更新的数据库配置
├── requirements-supabase.txt   # Supabase 依赖
└── .env.example                # 环境变量示例
```

---

## 📋 完整迁移步骤

| 步骤 | 操作 | 时间 | 文档 |
|------|------|------|------|
| 1 | 创建 Supabase 项目 | 5 分钟 | [MIGRATION_TO_SUPABASE.md](./MIGRATION_TO_SUPABASE.md#步骤-1-创建-supabase-项目) |
| 2 | 执行 Schema SQL | 2 分钟 | [MIGRATION_TO_SUPABASE.md](./MIGRATION_TO_SUPABASE.md#步骤-2-执行数据库-schema) |
| 3 | 运行迁移脚本 | 1 分钟 | [MIGRATION_TO_SUPABASE.md](./MIGRATION_TO_SUPABASE.md#步骤-3-迁移数据) |
| 4 | 更新配置 | 1 分钟 | [MIGRATION_TO_SUPABASE.md](./MIGRATION_TO_SUPABASE.md#步骤-4-更新后端配置) |
| 5 | 测试验证 | 2 分钟 | [MIGRATION_TO_SUPABASE.md](./MIGRATION_TO_SUPABASE.md#步骤-5-测试验证) |

**总计**: ~11 分钟

---

## 🔑 关键配置

### 环境变量 (.env)

```env
# 必填：Supabase 数据库连接
SUPABASE_DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres

# 可选：异步模式 (默认 true)
ASYNC_MODE=true
```

### 依赖安装

```bash
pip install asyncpg databases[postgresql] sqlalchemy python-dotenv
```

---

## 📊 迁移数据

| 表 | 记录数 | 状态 |
|----|--------|------|
| events | 391 | ✅ 待迁移 |
| users | 2 | ✅ 待迁移 |
| sources | 0 | ✅ 有默认数据 |
| 其他表 | 0 | ✅ 空表 |

---

## 🆘 遇到问题？

1. **连接问题**: 检查数据库密码和网络
2. **Schema 错误**: 在 Supabase SQL Editor 重新执行 `supabase_schema.sql`
3. **迁移失败**: 查看 [故障排查](./MIGRATION_TO_SUPABASE.md#故障排查)
4. **其他问题**: 阅读 [完整迁移指南](./MIGRATION_TO_SUPABASE.md)

---

## 📞 相关文档

- 📘 [完整迁移指南](./MIGRATION_TO_SUPABASE.md) - 详细步骤 + 故障排查
- 📄 [迁移摘要](./MIGRATION_SUMMARY.md) - 交付物清单 + 技术细节
- 💾 [PostgreSQL Schema](./supabase_schema.sql) - 执行这个创建表
- 🔧 [数据库配置](../apps/api/app/core/database.py) - asyncpg + databases

---

**准备就绪！开始迁移吧 🎉**
