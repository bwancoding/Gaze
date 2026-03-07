# WRHITW Scheduled News Fetcher

Automated news fetching system that runs periodically to collect international news from multiple sources.

---

## 📋 Overview

**Schedule**: Every 4 hours (configurable)  
**Sources**: 6 international news outlets  
**Categories**: Politics, Technology, Economy

---

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)

```bash
cd wrhitw/apps/api
./setup_cron.sh
```

### Option 2: Manual Setup

1. Open crontab editor:
   ```bash
   crontab -e
   ```

2. Add this line:
   ```bash
   0 */4 * * * cd /Users/bwan/.openclaw/workspace/wrhitw/apps/api && ./venv/bin/python fetch_news_scheduled.py >> /tmp/wrhitw_fetcher.log 2>&1
   ```

3. Save and exit

---

## 📊 News Sources

| Source | Category | Bias | Update Frequency |
|--------|----------|------|------------------|
| Reuters World | Politics | Center | Every 4 hours |
| AP News | Politics | Center | Every 4 hours |
| BBC World | Politics | Center-Left | Every 4 hours |
| TechCrunch | Technology | Center | Every 4 hours |
| The Verge | Technology | Center-Left | Every 4 hours |
| Bloomberg | Economy | Center | Every 4 hours |

---

## 📝 Viewing Logs

### Real-time Monitoring
```bash
tail -f /tmp/wrhitw_fetcher.log
```

### Recent Logs
```bash
tail -n 50 /tmp/wrhitw_fetcher.log
```

### Search Logs
```bash
grep "Created" /tmp/wrhitw_fetcher.log | tail -20
```

---

## 🔧 Configuration

### Change Schedule

Edit `wrhitw_cron.txt` and choose your preferred schedule:

```bash
# Every 4 hours (default)
0 */4 * * * ...

# Every hour
0 * * * * ...

# Every 15 minutes (testing)
*/15 * * * * ...

# Twice daily (00:00 and 12:00)
0 0,12 * * * ...
```

Then reinstall:
```bash
./setup_cron.sh
```

### Change Log Location

Edit `fetch_news_scheduled.py` and modify:
```python
LOG_FILE = Path('/your/custom/path/wrhitw_fetcher.log')
```

---

## 🧪 Manual Execution

Run the fetcher manually:

```bash
cd wrhitw/apps/api
./venv/bin/python fetch_news_scheduled.py
```

---

## 📈 Expected Output

Example log output:
```
[2026-03-06T05:54:31.217229+00:00] ============================================================
[2026-03-06T05:54:31.217705+00:00] WRHITW News Fetcher - Scheduled Task Started
[2026-03-06T05:54:31.217781+00:00] ============================================================
[2026-03-06T05:54:31.217842+00:00] Fetching Reuters World...
[2026-03-06T05:54:31.435330+00:00]   Retrieved 15 entries from Reuters World
[2026-03-06T05:54:31.435531+00:00]   ✓ Created: Global Climate Summit Reaches New Agreement...
[2026-03-06T05:54:31.435600+00:00]   ~ Updated: US Federal Reserve Maintains Interest Rates...
[2026-03-06T05:54:33.887063+00:00] ============================================================
[2026-03-06T05:54:33.887795+00:00] Summary: 12 new events, 3 updated events
[2026-03-06T05:54:33.887878+00:00] Completed at: 2026-03-06T05:54:33.887873+00:00
[2026-03-06T05:54:33.887943+00:00] ============================================================
```

---

## ⚠️ Troubleshooting

### Issue: RSS feeds return 0 entries

**Possible causes**:
- Network connectivity issues
- RSS feed temporarily unavailable
- Rate limiting

**Solutions**:
1. Check network connection
2. Try manual fetch to see errors
3. Wait and check next scheduled run

### Issue: Cron job not running

**Check if cron is installed**:
```bash
crontab -l
```

**Check cron logs** (macOS):
```bash
log show --predicate 'process == "cron"' --last 1h
```

**Verify Python path**:
```bash
cd wrhitw/apps/api
./venv/bin/python --version
```

### Issue: Permission denied

**Fix permissions**:
```bash
chmod +x fetch_news_scheduled.py
chmod +x setup_cron.sh
```

---

## 📊 Monitoring

### Check Recent Activity
```bash
grep "Summary:" /tmp/wrhitw_fetcher.log | tail -10
```

### Count Events Created Today
```bash
grep "Created:" /tmp/wrhitw_fetcher.log | grep $(date +%Y-%m-%d) | wc -l
```

### Check for Errors
```bash
grep "Error\|Fatal" /tmp/wrhitw_fetcher.log | tail -20
```

---

## 🔐 Security Notes

- Cron jobs run with your user permissions
- Logs are stored in `/tmp/` (world-readable)
- For production, consider:
  - Using a dedicated log directory with restricted permissions
  - Setting up log rotation
  - Monitoring disk space

---

## 📚 Additional Resources

- [cron documentation](https://www.gnu.org/software/mcron/manual/html_node/Crontab-file-format.html)
- [feedparser documentation](https://pythonhosted.org/feedparser/)
- [WRHITW Admin Guide](ADMIN.md)

---

**Last Updated**: 2026-03-06  
**Maintainer**: WRHITW Team
