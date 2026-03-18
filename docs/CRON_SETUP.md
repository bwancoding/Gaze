# WRHITW Cron Jobs Configuration

## Overview

The WRHITW project uses OpenClaw's cron feature to manage scheduled tasks.

---

## Configured Tasks

### 1. Heartbeat (Health Check)

**Purpose**: Check project status every 30 minutes to keep the agent active

**Configuration**:
- **Cron Expression**: `*/30 * * * *`
- **Timeout**: 300 seconds (5 minutes)
- **Delivery**: None (internal check)

**Check Items**:
- Backend API service (port 8080)
- Frontend page service (port 3002)
- Gateway service status
- Git repository status (uncommitted changes)

**Trigger Conditions**:
- Service stopped → Remind user to restart
- Uncommitted code → Ask whether to commit
- Idle for over 1 hour → Proactively ask about next task

---

### 2. News Fetcher

**Purpose**: Fetch international news from RSS sources every 4 hours

**Configuration**:
- **Cron Expression**: `0 */4 * * *` (runs at 0:00, 4:00, 8:00, 12:00, 16:00, 20:00 daily)
- **Timeout**: 600 seconds (10 minutes)
- **Delivery**: None (background process)
- **Script**: `apps/api/fetch_news_scheduled.py`

**News Sources**:
- Reuters World (Politics)
- AP News (Politics)
- BBC World (Politics)
- TechCrunch (Technology)
- The Guardian (Politics)
- Al Jazeera (Politics)

**Features**:
- Fetch latest news from RSS sources
- Automatic deduplication (based on title hash)
- Create Event records in the database
- Log output to `/tmp/wrhitw_fetcher.log`

---

## Management Commands

### List All Tasks
```bash
openclaw cron list
```

### View Run History
```bash
openclaw cron runs
openclaw cron runs --job-id <job-id>
```

### Manually Run a Task
```bash
# Heartbeat
openclaw cron run 4048bb57-39ae-4ab0-b46d-7ca6f0bf6495

# News Fetcher
openclaw cron run c04d0a62-0f9e-4637-8546-b0559f716f17
```

### Disable/Enable Tasks
```bash
# Disable
openclaw cron disable <job-id>

# Enable
openclaw cron enable <job-id>
```

### Delete a Task
```bash
openclaw cron rm <job-id>
```

### Add a New Task
```bash
openclaw cron add \
  --name "Task Name" \
  --cron "0 * * * *" \
  --message "Description of the task to execute" \
  --timeout 300000 \
  --no-deliver
```

---

## Viewing Logs

### Heartbeat Logs
```bash
# View recent run records
openclaw cron runs --job-id 4048bb57-39ae-4ab0-b46d-7ca6f0bf6495

# View full logs
cat ~/.openclaw/cron/runs/4048bb57-39ae-4ab0-b46d-7ca6f0bf6495.jsonl
```

### News Fetcher Logs
```bash
# View fetch logs
tail -f /tmp/wrhitw_fetcher.log

# View cron run records
openclaw cron runs --job-id c04d0a62-0f9e-4637-8546-b0559f716f17
```

### Gateway Logs
```bash
openclaw logs --follow
```

---

## Troubleshooting

### Cron Job Not Executing
1. Check if Gateway is running: `openclaw gateway status`
2. Check if the job is enabled: `openclaw cron list`
3. View run history: `openclaw cron runs`
4. Run manually to test: `openclaw cron run <job-id>`

### News Fetcher Failing
1. Check network connection
2. Check if RSS sources are accessible
3. View logs: `tail /tmp/wrhitw_fetcher.log`
4. Run the script manually:
   ```bash
   cd ~/.openclaw/workspace/wrhitw/apps/api
   ./venv/bin/python fetch_news_scheduled.py
   ```

### Heartbeat Not Triggering
1. Verify the cron expression is correct
2. Check Gateway timezone settings
3. View next scheduled run time: `openclaw cron list`

---

## Future Improvements

### Short-term
- [ ] Add notification for news fetch failures
- [ ] Add automatic service restart on failure
- [ ] Add daily summary report

### Mid-term
- [ ] Add more news sources
- [ ] Optimize deduplication algorithm
- [ ] Add AI summary generation task

### Long-term
- [ ] Distributed task scheduling
- [ ] Task priority queue
- [ ] Auto-scaling

---

**Document Updated**: 2026-03-07
**Maintainer**: WRHITW Team
