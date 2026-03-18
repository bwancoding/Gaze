# WRHITW - What's Really Happening In The World

**See the full story, not just a single perspective.**

WRHITW is a multi-perspective news aggregation platform that uses AI technology to help users quickly understand multiple viewpoints on events, identify information bias, and form independent judgments.

---

## Project Structure

```
wrhitw/
├── apps/
│   ├── web/          # Next.js 14 frontend
│   └── api/          # FastAPI backend
├── packages/
│   └── design-system/ # Design system
├── docs/             # Documentation
└── scripts/          # Utility scripts
```

---

## Quick Start

### Frontend Development

```bash
cd apps/web
pnpm install
pnpm dev
```

### Backend Development

```bash
cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Documentation

- [Product Requirements Document](./docs/PRD.md)
- [Design System](./docs/DESIGN.md)
- [API Documentation](./docs/API.md)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React, Tailwind CSS, TypeScript |
| Backend | Python 3.11+, FastAPI, SQLAlchemy |
| Database | PostgreSQL, Supabase |
| Deployment | Vercel (Frontend), Railway (Backend) |
| AI | Bailian (qwen3.5-plus) |

---

## Development Progress

- [x] Project initialization
- [ ] Design system setup
- [ ] Database schema design
- [ ] AI prompt templates
- [ ] Frontend scaffolding
- [ ] Backend API development
- [ ] MVP launch

---

## License

MIT License

---

**Last Updated**: 2026-03-04
