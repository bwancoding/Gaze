# WRHITW Cron Jobs 配置

## 概述

WRHITW 项目使用 OpenClaw 的 cron 功能来管理定时任务。

---

## 已配置的任务

### 1. Heartbeat (心跳检查)

**目的**: 每 30 分钟检查项目状态，保持 agent 活跃

**配置**:
- **Cron 表达式**: `*/30 * * * *`
- **超时**: 300 秒 (5 分钟)
- **交付**: 无（内部检查）

**检查内容**:
- 后端 API 服务 (端口 8080)
- 前端页面服务 (端口 3002)
- Gateway 服务状态
- Git 仓库状态（未提交变更）

**触发条件**:
- 服务停止 → 提醒用户重启
- 有未提交代码 → 询问是否 commit
- 空闲超过 1 小时 → 主动询问下一步任务

---

### 2. News Fetcher (新闻抓取)

**目的**: 每 4 小时从 RSS 源抓取国际新闻

**配置**:
- **Cron 表达式**: `0 */4 * * *` (每天的 0:00, 4:00, 8:00, 12:00, 16:00, 20:00)
- **超时**: 600 秒 (10 分钟)
- **交付**: 无（后台运行）
- **脚本**: `apps/api/fetch_news_scheduled.py`

**新闻源**:
- Reuters World (Politics)
- AP News (Politics)
- BBC World (Politics)
- TechCrunch (Technology)
- The Guardian (Politics)
- Al Jazeera (Politics)

**功能**:
- 从 RSS 源抓取最新新闻
- 自动去重（基于标题哈希）
- 创建 Event 记录到数据库
- 记录日志到 `/tmp/wrhitw_fetcher.log`

---

## 管理命令

### 查看所有任务
```bash
openclaw cron list
```

### 查看运行历史
```bash
openclaw cron runs
openclaw cron runs --job-id <job-id>
```

### 手动运行任务
```bash
# Heartbeat
openclaw cron run 4048bb57-39ae-4ab0-b46d-7ca6f0bf6495

# News Fetcher
openclaw cron run c04d0a62-0f9e-4637-8546-b0559f716f17
```

### 禁用/启用任务
```bash
# 禁用
openclaw cron disable <job-id>

# 启用
openclaw cron enable <job-id>
```

### 删除任务
```bash
openclaw cron rm <job-id>
```

### 添加新任务
```bash
openclaw cron add \
  --name "任务名称" \
  --cron "0 * * * *" \
  --message "执行的任务描述" \
  --timeout 300000 \
  --no-deliver
```

---

## 日志查看

### Heartbeat 日志
```bash
# 查看最近的运行记录
openclaw cron runs --job-id 4048bb57-39ae-4ab0-b46d-7ca6f0bf6495

# 查看完整日志
cat ~/.openclaw/cron/runs/4048bb57-39ae-4ab0-b46d-7ca6f0bf6495.jsonl
```

### News Fetcher 日志
```bash
# 查看抓取日志
tail -f /tmp/wrhitw_fetcher.log

# 查看 cron 运行记录
openclaw cron runs --job-id c04d0a62-0f9e-4637-8546-b0559f716f17
```

### Gateway 日志
```bash
openclaw logs --follow
```

---

## 故障排查

### Cron job 不执行
1. 检查 Gateway 是否运行：`openclaw gateway status`
2. 检查 job 是否启用：`openclaw cron list`
3. 查看运行历史：`openclaw cron runs`
4. 手动运行测试：`openclaw cron run <job-id>`

### News Fetcher 抓取失败
1. 检查网络连接
2. 检查 RSS 源是否可访问
3. 查看日志：`tail /tmp/wrhitw_fetcher.log`
4. 手动运行脚本：
   ```bash
   cd ~/.openclaw/workspace/wrhitw/apps/api
   ./venv/bin/python fetch_news_scheduled.py
   ```

### Heartbeat 不触发
1. 检查 cron 表达式是否正确
2. 检查 Gateway 时区设置
3. 查看下一次运行时间：`openclaw cron list`

---

## 下一步优化

### 短期
- [ ] 添加新闻抓取失败通知
- [ ] 添加服务异常自动重启
- [ ] 添加每日摘要报告

### 中期
- [ ] 添加更多新闻源
- [ ] 优化去重算法
- [ ] 添加 AI 摘要生成任务

### 长期
- [ ] 分布式任务调度
- [ ] 任务优先级队列
- [ ] 自动扩缩容

---

**文档更新**: 2026-03-07  
**维护者**: WRHITW Team
