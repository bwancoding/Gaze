# WRHITW Development Guide

🚀 **Get started developing the WRHITW project**

---

## 📦 Prerequisites

- Node.js 18+
- pnpm 8+
- Python 3.11+
- PostgreSQL 15+ (Docker can be used for local development)

---

## 🌐 Frontend Development

### Install Dependencies

```bash
cd apps/web
pnpm install
```

### Start Development Server

```bash
pnpm dev
```

Visit http://localhost:3000

### Build for Production

```bash
pnpm build
pnpm start
```

---

## 🔧 Backend Development

### Create Virtual Environment

```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start Development Server

```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000

### API Documentation

Visit http://localhost:8000/docs to view the Swagger UI

---

## 🗄️ Database Setup

### Start PostgreSQL with Docker

```bash
docker run -d \
  --name wrhitw-db \
  -e POSTGRES_USER=wrhitw \
  -e POSTGRES_PASSWORD=wrhitw \
  -e POSTGRES_DB=wrhitw \
  -p 5432:5432 \
  postgres:15
```

### Initialize Database

```bash
psql -U wrhitw -d wrhitw -f docs/DATABASE_SCHEMA.sql
```

### Using Prisma (Recommended)

```bash
cd apps/api
npx prisma generate
npx prisma db push
npx prisma studio  # Visual database management
```

---

## 🎨 Design System

Design system documentation is located at: `docs/DESIGN.md`

### Figma Design File

📎 [WRHITW Design System](https://www.figma.com/file/TODO) *(To be created)*

---

## 🤖 AI Configuration

### Configure API Key

Create a `.env` file:

```bash
# Bailian AI
DASHSCOPE_API_KEY=sk-xxx

# Database
DATABASE_URL=postgresql://wrhitw:wrhitw@localhost:5432/wrhitw
```

---

## 📝 Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Develop and Commit

```bash
git add .
git commit -m "feat: add xxx feature"
```

### 3. Push to Remote

```bash
git push origin feature/your-feature-name
```

### 4. Create a Pull Request

Create a PR on GitHub and wait for code review

---

## 🧪 Testing

### Frontend Tests

```bash
cd apps/web
pnpm test
```

### Backend Tests

```bash
cd apps/api
pytest
```

---

## 📊 Project Structure

```
wrhitw/
├── apps/
│   ├── web/              # Next.js frontend
│   │   ├── src/
│   │   │   ├── app/      # App Router
│   │   │   ├── components/
│   │   │   └── styles/
│   │   └── package.json
│   │
│   └── api/              # FastAPI backend
│       ├── app/
│       │   ├── main.py
│       │   ├── routes/
│       │   ├── models/
│       │   └── services/
│       └── requirements.txt
│
├── packages/
│   └── design-system/    # Shared design system
│
├── docs/
│   ├── PRD.md            # Product requirements
│   ├── DESIGN.md         # Design system
│   ├── DATABASE_SCHEMA.sql
│   ├── AI_PROMPTS.md
│   └── DEVELOPMENT.md    # This file
│
└── scripts/              # Utility scripts
```

---

## 🐛 Common Issues

### Port Already in Use

```bash
# Find the process using the port
lsof -i :3000
# Kill the process
kill -9 <PID>
```

### Dependency Installation Failure

```bash
# Clear cache
pnpm store prune
# Reinstall
rm -rf node_modules
pnpm install
```

### Database Connection Failure

```bash
# Check if PostgreSQL is running
docker ps | grep wrhitw-db
# Restart the container
docker restart wrhitw-db
```

---

## 📚 References

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Prisma Documentation](https://www.prisma.io/docs)

---

**Last Updated**: 2026-03-04
**Status**: 🟡 In Development
