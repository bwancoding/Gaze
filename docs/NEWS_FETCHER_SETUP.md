# WRHITW 定时新闻抓取系统

**功能**: 每 4 小时自动从多个国际新闻源抓取 RSS 新闻  
**状态**: ✅ 已实现并测试通过

---

## 📊 测试结果

**首次运行结果** (2026-03-09 18:46):
- ✅ NY Times World: 8 新增，7 更新
- ✅ Hacker News: 1 新增，14 更新
- ✅ TechCrunch: 0 新增，15 更新
- ✅ The Verge: 0 新增，10 更新
- ❌ BBC World: SSL 错误 (跳过)

**总计**: 9 个新事件，46 个更新事件  
**数据库事件总数**: 107 个

---

## 🔧 安装步骤

### 1. 确认依赖已安装

```bash
cd /Users/bwan/.openclaw/workspace/wrhitw/apps/api
source venv/bin/activate
pip install requests feedparser
```

### 2. 测试运行

```bash
# 手动运行一次测试
python fetch_news_scheduled.py
```

### 3. 设置定时任务

#### macOS/Linux (Cron)

```bash
# 编辑 crontab
crontab -e

# 添加以下行 (每 4 小时运行一次)
0 */4 * * * cd /Users/bwan/.openclaw/workspace/wrhitw/apps/api && ./venv/bin/python fetch_news_scheduled.py >> /tmp/wrhitw_fetcher.log 2>&1
```

#### 验证 Cron 设置

```bash
# 查看当前 crontab
crontab -l

# 查看 cron 日志 (macOS)
grep CRON /var/log/system.log

# 查看 cron 日志 (Linux)
grep CRON /var/log/syslog
```

---

## 📁 相关文件

| 文件 | 说明 |
|------|------|
| `fetch_news_scheduled.py` | 主脚本 |
| `fetch_rss_news.py` | RSS 抓取基础脚本 |
| `cron_job.txt` | Cron 配置示例 |
| `setup_cron.sh` | 自动设置脚本 |
| `/tmp/wrhitw_fetcher.log` | 运行日志 |

---

## 🌐 新闻源列表

| 名称 | 类别 | 政治倾向 | 状态 |
|------|------|----------|------|
| NY Times World | Politics | center-left | ✅ |
| Hacker News | Technology | center | ✅ |
| TechCrunch | Technology | center | ✅ |
| The Verge | Technology | center-left | ✅ |
| BBC World | Politics | center-left | ⚠️ SSL 问题 |

---

## 🔍 监控与维护

### 查看运行日志

```bash
# 实时查看日志
tail -f /tmp/wrhitw_fetcher.log

# 查看最新 50 行
tail -50 /tmp/wrhitw_fetcher.log

# 查看错误
grep "Error\|✗" /tmp/wrhitw_fetcher.log
```

### 检查事件数量

```bash
# 查看数据库中的事件总数
curl http://localhost:8080/api/events | python3 -c "import sys,json; d=json.load(sys.stdin); print('总事件数:', d.get('total',0))"
```

### 手动触发抓取

```bash
cd /Users/bwan/.openclaw/workspace/wrhitw/apps/api
source venv/bin/activate
python fetch_news_scheduled.py
```

---

## 🐛 故障排除

### 问题 1: SSL 错误

**现象**: `SSLError(1, '[SSL] record layer failure')`

**原因**: 某些新闻源 (如 BBC) 的 SSL 证书验证失败

**解决方案**: 
- 脚本已配置跳过 SSL 验证 (`verify=False`)
- 如果持续失败，考虑更换新闻源

### 问题 2: 代理问题

**现象**: 连接超时或连接拒绝

**原因**: 代理配置不正确 (默认使用 Clash Verge mixed-port: 7897)

**解决方案**:
```python
# 修改 fetch_news_scheduled.py 中的 PROXY_CONFIG
PROXY_CONFIG = {
    'http': 'http://127.0.0.1:YOUR_PORT',
    'https': 'http://127.0.0.1:YOUR_PORT',
}
```

### 问题 3: Cron 不执行

**现象**: 日志文件没有更新

**检查步骤**:
1. 确认 cron 服务运行：`sudo systemctl status cron` (Linux)
2. 检查 crontab 语法：`crontab -l`
3. 查看 cron 日志
4. 确保脚本有执行权限：`chmod +x fetch_news_scheduled.py`

---

## 📈 性能优化建议

1. **添加新闻源**: 在 `NEWS_SOURCES` 列表中添加更多 RSS 源
2. **调整频率**: 根据需要修改 cron 表达式
3. **去重优化**: 检查 `generate_event_id` 函数的哈希算法
4. **错误处理**: 添加重试机制和网络超时处理

---

## 🔒 安全注意事项

1. **SSL 验证**: 生产环境应启用 SSL 验证
2. **代理配置**: 确保代理服务器可信
3. **日志文件**: 定期清理 `/tmp/wrhitw_fetcher.log`
4. **访问权限**: 确保脚本只有授权用户可以执行

---

**最后更新**: 2026-03-09  
**维护者**: WRHITW Team
