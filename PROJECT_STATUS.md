# WRHITW Project Status Report
**Date**: 2026-03-06  
**Status**: MVP Development - Sprint 1 Complete

---

## 📊 Project Overview

**WRHITW** (What's Really Happening In The World) - Multi-perspective News Aggregation Platform

**Core Mission**: See the full story, not just a single perspective

---

## ✅ Completed Features

### 1️⃣ Frontend (Next.js 14 + React) - 100% English

**Status**: ✅ All UI translated to English

**Core Pages**:
- Homepage (`/`) - Story-driven magazine style
- Event Detail (`/events/[id]`) - Multi-perspective view
- Category filters - Environment/Economy/Technology/Politics

**Features**:
- 📖 Story-driven narrative
- 🎨 Category color system
- ✨ Hover animations
- 🔄 Real-time data refresh
- 🌐 Full English UI

---

### 2️⃣ Backend API (FastAPI + Python) - English Ready

**Status**: ✅ Full English API + Category Translation

**New Features**:
- ✅ Event status management (active/archived/closed)
- ✅ Archive/Close endpoints
- ✅ Status filtering in list API
- ✅ Category translation (Chinese → English)

**API Endpoints**:
```
GET    /api/events?status={status}  # List with status filter
POST   /api/events/{id}/archive     # Archive event
POST   /api/events/{id}/close       # Close event
```

---

### 3️⃣ Event Status Management - NEW ✅

**Database Fields**:
- `status` - active/archived/closed
- `archived_at` - Timestamp when archived
- `closed_at` - Timestamp when closed

**API Examples**:
```bash
# Get active events
curl "http://localhost:8080/api/events?status=active"

# Archive event
curl -X POST http://localhost:8080/api/events/{id}/archive

# Close event
curl -X POST http://localhost:8080/api/events/{id}/close
```

---

### 4️⃣ Scheduled News Fetching - NEW ⏳

**Status**: ⏳ Script ready, cron setup pending

**Schedule**: Every 4 hours

**News Sources**:
- Reuters World, AP News, BBC World (Politics)
- TechCrunch, The Verge (Technology)
- Bloomberg (Economy)

---

## 📝 Next Steps (Sprint 2)

### High Priority
1. ⏳ Set up cron job for scheduled fetching
2. ⏳ Create admin dashboard (simple web UI)
3. ⏳ Implement stakeholder recognition system

### Medium Priority
4. 🔄 Discussion/comment system (basic version)
5. 🔄 User authentication (email/Google)
6. 🔄 Search functionality

---

## 📞 Quick Commands

### Backend
```bash
cd wrhitw/apps/api
./venv/bin/uvicorn app.main:app --reload --port 8080
./venv/bin/python fetch_news_scheduled.py
```

### Frontend
```bash
cd wrhitw/apps/web
pnpm dev
```

---

**Last Updated**: 2026-03-06  
**Maintainer**: WRHITW Team
