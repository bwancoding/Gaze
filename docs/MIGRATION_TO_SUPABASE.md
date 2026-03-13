# WRHITW SQLite → Supabase PostgreSQL 迁移指南

**版本**: v2.0  
**创建时间**: 2026-03-13  
**状态**: ✅ 已完成

---

## 📋 目录

1. [迁移概述](#迁移概述)
2. [前置准备](#前置准备)
3. [步骤 1: 创建 Supabase 项目](#步骤-1-创建-supabase-项目)
4. [步骤 2: 执行数据库 Schema](#步骤-2-执行数据库-schema)
5. [步骤 3: 迁移数据](#步骤-3-迁移数据)
6. [步骤 4: 更新后端配置](#步骤-4-更新后端配置)
7. [步骤 5: 测试验证](#步骤-5-测试验证)
8. [故障排查](#故障排查)

---

## 迁移概述

### 为什么迁移到 Supabase？

| 特性 | SQLite | Supabase PostgreSQL |
|------|--------|---------------------|
| 并发支持 | ❌ 单文件锁 | ✅ 完整并发 |
| 扩展性 | ❌ 有限 | ✅ 无限扩展 |
| 高可用 | ❌ 无 | ✅ 自动备份 + 复制 |
| 实时功能 | ❌ 无 | ✅ WebSocket 订阅 |
| 认证集成 | ❌ 手动 | ✅ 内置 Auth |
| 存储 | ❌ 本地 | ✅ 对象存储 |

### 迁移内容

- ✅ 16 个数据表完整迁移
- ✅ UUID 主键适配
- ✅ 日期时间时区处理
- ✅ 数组类型转换 (TEXT[] / UUID[])
- ✅ 触发器和索引重建
- ✅ 初始数据插入

---

## 前置准备

### 系统要求

- Python 3.10+
- Node.js 18+ (可选，用于 Supabase CLI)
- 网络连接 (访问 supabase.com)

### 安装依赖

```bash
cd wrhitw/apps/api

# 安装 Supabase 迁移依赖
pip install -r requirements-supabase.txt

# 或手动安装
pip install asyncpg databases[postgresql] sqlalchemy python-dotenv aiosqlite
```

---

## 步骤 1: 创建 Supabase 项目

### 1.1 注册/登录 Supabase

访问 [supabase.com](https://supabase.com) 并登录。

### 1.2 创建新项目

1. 点击 **"New Project"**
2. 填写项目信息：
   - **Name**: `wrhitw` (或自定义)
   - **Database Password**: 设置强密码（保存好！）
   - **Region**: 选择最近的区域（如 `Singapore` 或 `Tokyo`）
3. 点击 **"Create new project"**
4. 等待 2-5 分钟，项目创建完成

### 1.3 获取数据库连接 URL

1. 进入项目 Dashboard
2. 左侧菜单 → **Settings** (⚙️) → **Database**
3. 找到 **Connection string**
4. 选择 **URI** 模式
5. 复制连接字符串，格式类似：
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```

> ⚠️ **安全提示**: 将密码替换为实际值，不要提交到 Git！

---

## 步骤 2: 执行数据库 Schema

### 方法 A: 使用 Supabase SQL 编辑器 (推荐)

1. 进入项目 Dashboard
2. 左侧菜单 → **SQL Editor**
3. 点击 **"New query"**
4. 打开文件 `docs/supabase_schema.sql`
5. 复制全部内容并粘贴到编辑器
6. 点击 **"Run"** (或 Ctrl+Enter)
7. 确认所有表创建成功

### 方法 B: 使用 psql 命令行

```bash
# 设置环境变量
export SUPABASE_DB_URL="postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres"

# 执行 schema
psql $SUPABASE_DB_URL -f docs/supabase_schema.sql
```

### 验证 Schema

在 SQL 编辑器中运行：

```sql
-- 检查表数量
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public';

-- 应该返回 17 (16 个数据表 + 1 个 schema_version)
```

---

## 步骤 3: 迁移数据

### 3.1 配置环境变量

```bash
cd wrhitw/apps/api

# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，填入 Supabase 连接 URL
nano .env
# 或
vim .env
```

`.env` 文件内容：

```env
SUPABASE_DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
ASYNC_MODE=true
```

### 3.2 运行迁移脚本

```bash
cd wrhitw/scripts

# 执行迁移
python migrate_to_supabase.py \
  --sqlite ../apps/api/wrhitw.db \
  --supabase-url "postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres"
```

### 3.3 验证迁移结果

迁移脚本会自动验证。输出示例：

```
🔍 验证迁移结果...
  ✅ sources: SQLite=10, PostgreSQL=10
  ✅ events: SQLite=391, PostgreSQL=391
  ✅ event_sources: SQLite=0, PostgreSQL=0
  ✅ ai_summaries: SQLite=0, PostgreSQL=0
  ✅ users: SQLite=2, PostgreSQL=2
  ...
```

### 3.4 手动验证 (可选)

在 Supabase SQL 编辑器中运行：

```sql
-- 检查各表数据量
SELECT 
    'sources' as table_name, COUNT(*) as row_count FROM sources
UNION ALL SELECT 'events', COUNT(*) FROM events
UNION ALL SELECT 'event_sources', COUNT(*) FROM event_sources
UNION ALL SELECT 'ai_summaries', COUNT(*) FROM ai_summaries
UNION ALL SELECT 'users', COUNT(*) FROM users;
```

---

## 步骤 4: 更新后端配置

### 4.1 更新数据库配置

文件已更新：`apps/api/app/core/database.py`

新配置支持：
- ✅ 自动检测 PostgreSQL vs SQLite
- ✅ 异步模式 (asyncpg + databases)
- ✅ 同步模式 (向后兼容)
- ✅ 健康检查
- ✅ FastAPI 生命周期事件

### 4.2 更新依赖

```bash
cd wrhitw/apps/api

# 安装新依赖
pip install -r requirements-supabase.txt
```

### 4.3 更新 .env 文件

确保包含以下变量：

```env
# 数据库
SUPABASE_DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
ASYNC_MODE=true

# (可选) Supabase 其他服务
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4.4 更新 FastAPI 应用

如果使用 FastAPI，确保注册生命周期事件：

```python
# apps/api/main.py
from fastapi import FastAPI
from app.core.database import register_lifespan_events

app = FastAPI()

# 注册数据库生命周期事件
register_lifespan_events(app)
```

---

## 步骤 5: 测试验证

### 5.1 数据库连接测试

```bash
cd wrhitw/apps/api

# 运行健康检查
python -c "
import asyncio
from app.core.database import health_check

async def test():
    ok = await health_check()
    print('✅ 数据库连接正常' if ok else '❌ 数据库连接失败')
    return ok

asyncio.run(test())
"
```

### 5.2 API 启动测试

```bash
# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问健康检查端点
curl http://localhost:8000/health
```

### 5.3 数据查询测试

```bash
# 测试事件列表 API
curl http://localhost:8000/api/v1/events | head -50

# 测试用户列表 API
curl http://localhost:8000/api/v1/users | head -50
```

### 5.4 并发测试 (关键！)

```bash
# 使用 ab (Apache Bench) 测试并发
ab -n 100 -c 10 http://localhost:8000/api/v1/events

# 或使用 wrk
wrk -t4 -c20 -d30s http://localhost:8000/api/v1/events
```

预期结果：
- ✅ 无数据库锁错误
- ✅ 所有请求成功 (200 OK)
- ✅ 响应时间 < 500ms

---

## 故障排查

### 问题 1: 连接超时

**错误**: `connection timed out`

**解决**:
1. 检查 Supabase 项目状态 (Dashboard → Home)
2. 确认数据库密码正确
3. 检查防火墙/网络设置
4. 尝试在 Supabase SQL 编辑器连接测试

### 问题 2: 认证失败

**错误**: `password authentication failed`

**解决**:
1. 在 Supabase Dashboard 重置数据库密码
2. 更新 `.env` 文件中的密码
3. 重启应用

### 问题 3: SSL 连接错误

**错误**: `SSL connection required`

**解决**:
在连接 URL 中添加 SSL 参数：
```
postgresql://user:pass@host:port/db?sslmode=require
```

### 问题 4: 表不存在

**错误**: `relation "xxx" does not exist`

**解决**:
1. 确认已执行 `supabase_schema.sql`
2. 检查 schema 是否正确：`SELECT * FROM information_schema.tables`
3. 重新运行 schema 脚本

### 问题 5: UUID 冲突

**错误**: `duplicate key value violates unique constraint`

**解决**:
1. 确认 `uuid-ossp` 扩展已启用
2. 检查迁移脚本是否正确处理 UUID
3. 清空表后重新迁移：`TRUNCATE TABLE xxx CASCADE;`

### 问题 6: 异步导入错误

**错误**: `No module named 'asyncpg'`

**解决**:
```bash
pip install asyncpg databases[postgresql]
```

---

## 回滚方案

如需回滚到 SQLite：

```bash
# 1. 更新 .env
DATABASE_URL=sqlite:///./wrhitw.db
ASYNC_MODE=false

# 2. 重启应用
# SQLite 数据保持不变，可继续使用
```

---

## 后续优化

### 性能优化

1. **连接池调优**:
   ```python
   engine = create_async_engine(
       DATABASE_URL,
       pool_size=20,
       max_overflow=40,
       pool_timeout=30
   )
   ```

2. **添加索引**:
   ```sql
   CREATE INDEX CONCURRENTLY idx_events_category_created 
   ON events(category, created_at DESC);
   ```

3. **查询优化**:
   - 使用 `EXPLAIN ANALYZE` 分析慢查询
   - 添加适当的联合索引

### 监控告警

1. 启用 Supabase Dashboard 监控
2. 设置慢查询日志
3. 配置告警通知 (Email/Slack)

### 备份策略

1. Supabase 自动备份 (免费 tier: 7 天)
2. 手动导出：`pg_dump > backup.sql`
3. 定期备份脚本 (cron)

---

## 相关文档

- [Supabase 官方文档](https://supabase.com/docs)
- [asyncpg 文档](https://magicstack.github.io/asyncpg/)
- [SQLAlchemy 异步文档](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [WRHITW 数据库 Schema](./supabase_schema.sql)

---

## 迁移检查清单

- [ ] Supabase 项目创建完成
- [ ] 数据库连接 URL 获取
- [ ] Schema 执行成功 (17 个表)
- [ ] 数据迁移完成 (391 events + 2 users)
- [ ] 迁移验证通过
- [ ] 依赖安装完成
- [ ] .env 配置完成
- [ ] 数据库连接测试通过
- [ ] API 启动测试通过
- [ ] 并发测试通过
- [ ] 监控告警配置 (可选)

---

**迁移完成时间**: 2026-03-13  
**执行人**: AI Agent (小狗)  
**审核**: 待人工审核
