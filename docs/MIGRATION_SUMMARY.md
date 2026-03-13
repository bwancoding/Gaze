# WRHITW SQLite → Supabase 迁移摘要

**完成时间**: 2026-03-13  
**执行人**: AI Agent (小狗)  
**状态**: ✅ 已完成

---

## 📦 交付物清单

### 1. 数据库 Schema

| 文件 | 路径 | 说明 |
|------|------|------|
| `supabase_schema.sql` | `wrhitw/docs/supabase_schema.sql` | 完整的 PostgreSQL Schema (19KB) |
| `sqlite_schema.sql` | `wrhitw/docs/sqlite_schema.sql` | 现有 SQLite Schema 备份 |

**包含的表** (16 个):
- 核心表：`sources`, `events`, `event_sources`, `ai_summaries`, `users`, `reading_history`, `bookmarks`
- 扩展表：`stakeholder_types`, `stakeholders`, `event_stakeholders`, `stakeholder_verifications`, `user_stakeholder_roles`, `user_personas`, `event_stakeholder_verifications`, `comments`, `comment_votes`
- 版本表：`schema_version`

### 2. 迁移脚本

| 文件 | 路径 | 说明 |
|------|------|------|
| `migrate_to_supabase.py` | `wrhitw/scripts/migrate_to_supabase.py` | Python 迁移脚本 (10KB) |
| `setup-supabase.sh` | `wrhitw/scripts/setup-supabase.sh` | 快速设置脚本 (Shell) |

**功能**:
- ✅ 自动连接 SQLite 和 PostgreSQL
- ✅ 智能字段类型转换 (TEXT → UUID[], BOOLEAN, TIMESTAMP)
- ✅ 批量插入 (100 条/批次)
- ✅ 迁移后自动验证
- ✅ 错误处理和日志输出

### 3. 配置文件

| 文件 | 路径 | 说明 |
|------|------|------|
| `database.py` | `wrhitw/apps/api/app/core/database.py` | 更新的数据库配置 (5KB) |
| `requirements-supabase.txt` | `wrhitw/apps/api/requirements-supabase.txt` | Supabase 依赖列表 |
| `.env.example` | `wrhitw/apps/api/.env.example` | 环境变量示例 |

**新特性**:
- ✅ 自动检测 PostgreSQL vs SQLite
- ✅ 异步模式支持 (asyncpg + databases)
- ✅ 同步模式向后兼容
- ✅ 健康检查函数
- ✅ FastAPI 生命周期事件集成

### 4. 文档

| 文件 | 路径 | 说明 |
|------|------|------|
| `MIGRATION_TO_SUPABASE.md` | `wrhitw/docs/MIGRATION_TO_SUPABASE.md` | 完整迁移指南 (7KB) |
| `MIGRATION_SUMMARY.md` | `wrhitw/docs/MIGRATION_SUMMARY.md` | 本文档 |

---

## 📊 现有数据概览

从 SQLite 数据库导出：

| 表名 | 记录数 | 迁移优先级 |
|------|--------|-----------|
| `events` | 391 | 🔴 高 |
| `users` | 2 | 🔴 高 |
| `sources` | 0 | 🟡 中 (有默认数据) |
| `event_sources` | 0 | 🟢 低 |
| `ai_summaries` | 0 | 🟢 低 |
| `reading_history` | 0 | 🟢 低 |
| `bookmarks` | 0 | 🟢 低 |
| 其他扩展表 | 0 | 🟢 低 |

**总计**: 393 条有效数据需要迁移

---

## 🚀 快速开始

### 3 步完成迁移

```bash
# 1. 安装依赖
cd wrhitw
pip install -r apps/api/requirements-supabase.txt

# 2. 在 Supabase 创建项目并获取连接 URL
# 访问：https://supabase.com

# 3. 运行迁移
python scripts/migrate_to_supabase.py \
  --sqlite apps/api/wrhitw.db \
  --supabase-url "postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres"
```

---

## 📋 手动操作步骤

以下操作需要用户在 Supabase 控制台完成：

### 1. 创建 Supabase 项目 (5 分钟)

1. 访问 [supabase.com](https://supabase.com)
2. 登录/注册
3. 点击 "New Project"
4. 填写项目名、数据库密码、区域
5. 等待项目创建完成

### 2. 执行 Schema (2 分钟)

1. 进入项目 Dashboard → SQL Editor
2. 新建查询
3. 复制 `docs/supabase_schema.sql` 全部内容
4. 粘贴并运行

### 3. 配置环境变量 (1 分钟)

1. 复制 `.env.example` 为 `.env`
2. 填入 `SUPABASE_DATABASE_URL`
3. 保存

### 4. 运行迁移脚本 (1 分钟)

```bash
python scripts/migrate_to_supabase.py --sqlite apps/api/wrhitw.db --supabase-url "..."
```

### 5. 验证 (1 分钟)

```bash
# 在 Supabase SQL Editor 中运行
SELECT COUNT(*) FROM events;  -- 应返回 391
SELECT COUNT(*) FROM users;   -- 应返回 2
```

---

## 🔧 技术细节

### 类型映射

| SQLite | PostgreSQL | 说明 |
|--------|-----------|------|
| `TEXT` (UUID) | `UUID` | 使用 `uuid_generate_v4()` |
| `TEXT` (JSON) | `TEXT[]` / `UUID[]` | 数组类型 |
| `INTEGER` (0/1) | `BOOLEAN` | 布尔转换 |
| `DATETIME` | `TIMESTAMP WITH TIME ZONE` | 时区支持 |
| `DECIMAL` | `DECIMAL` | 精度保持 |
| `TEXT` | `TEXT` | 直接映射 |

### 异步支持

```python
# 异步模式 (推荐)
from databases import Database
from sqlalchemy.ext.asyncio import create_async_engine

database = Database(DATABASE_URL)  # PostgreSQL + asyncpg
```

### 连接池配置

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)
```

---

## ✅ 验证清单

- [x] Schema 文件创建 (19KB, 16 个表)
- [x] 迁移脚本编写 (支持批量插入)
- [x] 数据库配置更新 (asyncpg + databases)
- [x] 依赖文件创建
- [x] 环境变量示例
- [x] 完整迁移文档
- [x] 快速设置脚本
- [x] 执行权限设置

---

## 📞 后续支持

如有问题，请查阅：
- 详细文档：`docs/MIGRATION_TO_SUPABASE.md`
- Schema 文件：`docs/supabase_schema.sql`
- 故障排查章节：文档第 8 节

---

**迁移准备完成！🎉**

下一步：按照 `MIGRATION_TO_SUPABASE.md` 执行实际迁移操作。
