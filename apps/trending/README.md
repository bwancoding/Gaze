# WRHITW Trending MVP

Trending topic aggregation service - Crawls global news media, calculates event heat scores, and provides a real-time trending API

## Project Status

- ✅ **Task 1**: RSS News Source Configuration - Complete
- ✅ **Task 2**: Database Schema Implementation - Complete
- 🚧 **Task 3**: Reddit API Integration - In Progress
- ⏳ **Task 4**: Hacker News API Integration
- ⏳ **Task 5**: Heat Score Algorithm Implementation
- ⏳ **Task 6**: Event Deduplication & Clustering
- ⏳ **Task 7**: API Development
- ⏳ **Task 8**: Scheduled Task Scheduling
- ⏳ **Task 9**: Frontend Trending Page
- ⏳ **Task 10**: Integration Testing + Deployment

## Quick Start

### 1. Environment Setup

```bash
# Python 3.11+
python --version

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy environment variable template
cp .env.example .env

# Edit the .env file to configure database connection, etc.
```

### 3. Initialize Database

```bash
# Option 1: Use Python script (recommended)
python scripts/init_db.py

# Option 2: Use SQL migration file
psql -U wrhitw -d wrhitw -f migrations/001_initial_schema.sql
```

### 4. Test RSS Fetching

```bash
python scripts/test_rss_fetch.py
```

### 5. Start the Service

```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
python app/main.py
```

### 6. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Project Structure

```
trending/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management (15 media RSS sources)
│   ├── database.py          # Database connection
│   ├── models/              # Data models
│   │   ├── __init__.py
│   │   ├── source.py        # Data source model
│   │   ├── event.py         # Event clustering model
│   │   └── article.py       # Article model
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   └── rss_fetcher.py   # RSS fetching service
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   └── health.py        # Health check
│   ├── scheduler/           # Scheduled tasks (to be implemented)
│   └── utils/               # Utility functions (to be implemented)
├── tests/                   # Tests (to be implemented)
├── scripts/                 # Scripts
│   ├── init_db.py          # Database initialization
│   └── test_rss_fetch.py   # RSS fetch test
├── migrations/              # Database migrations
│   └── 001_initial_schema.sql
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variable template
└── README.md               # This file
```

## Database Schema

### sources (Data Sources Table)
- `id`: Primary key
- `name`: Media name
- `url`: RSS URL
- `stance`: Political stance (left/center/right)
- `region`: Region (us/uk/international)
- `priority`: Priority (P0/P1/P2)
- `enabled`: Whether enabled

### events (Events Table)
- `id`: Primary key
- `title`: Event title
- `summary`: Event summary
- `keywords`: Keywords list (JSONB)
- `heat_score`: Heat score
- `article_count`: Article count
- `media_count`: Media outlet count

### articles (Articles Table)
- `id`: Primary key
- `event_id`: Associated event ID
- `source_id`: Data source ID
- `title`: Article title
- `summary`: Article summary
- `url`: Article URL
- `published_at`: Publication time
- `heat_score`: Heat score
- `is_processed`: Whether clustered

## Configured Media Sources (15 outlets)

### P0 Priority (every 15-30 minutes)
1. Reuters (Center, International)
2. Associated Press (Center, International)
3. BBC News (Center-left, UK)
4. The Guardian (Left, UK)
5. Financial Times (Center, UK)
6. Bloomberg (Center, US)

### P1 Priority (every 30-60 minutes)
7. CNN (Left, US)
8. Fox News (Right, US)
9. The New York Times (Left, US)
10. The Wall Street Journal (Right, US)
11. The Economist (Center-right, UK)
12. Al Jazeera (Center, Qatar)

### P2 Priority (hourly)
13. Politico (Center-left, US)
14. The Hill (Center, US)
15. NPR (Left, US)

## Testing

```bash
# RSS fetch test
python scripts/test_rss_fetch.py

# Database initialization test
python scripts/init_db.py
```

## Next Steps

1. ✅ ~~RSS News Source Configuration~~
2. ✅ ~~Database Schema Implementation~~
3. 🚧 Reddit API Integration
4. ⏳ Hacker News API Integration
5. ⏳ Heat Score Algorithm Implementation
6. ⏳ Event Deduplication & Clustering
7. ⏳ API Development
8. ⏳ Scheduled Task Scheduling
9. ⏳ Frontend Trending Page
10. ⏳ Integration Testing + Deployment

## License

MIT License

---

**Development Team**: WRHITW
**Last Updated**: 2026-03-13
