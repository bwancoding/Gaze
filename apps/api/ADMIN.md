# WRHITW Admin Dashboard

Quick admin commands for event management.

## Event Status Management

### Archive an Event
```bash
curl -X POST http://localhost:8080/api/events/{event_id}/archive
```

### Close an Event (no new comments)
```bash
curl -X POST http://localhost:8080/api/events/{event_id}/close
```

### List Events by Status
```bash
# Active events
curl "http://localhost:8080/api/events?status=active"

# Archived events
curl "http://localhost:8080/api/events?status=archived"

# All events
curl "http://localhost:8080/api/events?status=all"
```

## Scheduled Tasks

### Run News Fetcher Manually
```bash
cd wrhitw/apps/api
./venv/bin/python fetch_news_scheduled.py
```

### Create Sample Events
```bash
cd wrhitw/apps/api
./venv/bin/python create_sample_events.py
```

## Cron Setup

Add to crontab (runs every 4 hours):
```bash
crontab -e
# Add line from cron_job.txt
```

## Database Migration

```bash
cd wrhitw/apps/api
python3 migrate_add_event_status.py
```
