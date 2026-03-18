# WRHITW Supabase Migration - Quick Start

> 🚀 Migrate from SQLite to Supabase PostgreSQL for high-concurrency support

---

## ⚡ 5-Minute Quick Start

```bash
# 1. Install dependencies
cd wrhitw
pip install -r apps/api/requirements-supabase.txt

# 2. Create a Supabase project
# Visit https://supabase.com → New Project

# 3. Get the database URL and run migration
python scripts/migrate_to_supabase.py \
  --sqlite apps/api/wrhitw.db \
  --supabase-url "postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres"
```

---

## 📁 File Structure

```
wrhitw/docs/
├── README_SUPABASE.md          # This document (Quick Start)
├── MIGRATION_TO_SUPABASE.md    # Full migration guide (detailed steps)
├── MIGRATION_SUMMARY.md        # Migration summary (deliverables list)
├── supabase_schema.sql         # PostgreSQL Schema (execute this!)
├── sqlite_schema.sql           # SQLite Schema backup
└── DATABASE_SCHEMA.sql         # Original schema documentation

wrhitw/scripts/
├── migrate_to_supabase.py      # Migration script
└── setup-supabase.sh           # Quick setup script

wrhitw/apps/api/
├── app/core/database.py        # Updated database configuration
├── requirements-supabase.txt   # Supabase dependencies
└── .env.example                # Environment variable example
```

---

## 📋 Full Migration Steps

| Step | Action | Time | Documentation |
|------|--------|------|---------------|
| 1 | Create Supabase project | 5 min | [MIGRATION_TO_SUPABASE.md](./MIGRATION_TO_SUPABASE.md#step-1-create-supabase-project) |
| 2 | Execute Schema SQL | 2 min | [MIGRATION_TO_SUPABASE.md](./MIGRATION_TO_SUPABASE.md#step-2-execute-database-schema) |
| 3 | Run migration script | 1 min | [MIGRATION_TO_SUPABASE.md](./MIGRATION_TO_SUPABASE.md#step-3-migrate-data) |
| 4 | Update configuration | 1 min | [MIGRATION_TO_SUPABASE.md](./MIGRATION_TO_SUPABASE.md#step-4-update-backend-configuration) |
| 5 | Test and verify | 2 min | [MIGRATION_TO_SUPABASE.md](./MIGRATION_TO_SUPABASE.md#step-5-test-and-verify) |

**Total**: ~11 minutes

---

## 🔑 Key Configuration

### Environment Variables (.env)

```env
# Required: Supabase database connection
SUPABASE_DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres

# Optional: Async mode (default: true)
ASYNC_MODE=true
```

### Install Dependencies

```bash
pip install asyncpg databases[postgresql] sqlalchemy python-dotenv
```

---

## 📊 Migration Data

| Table | Record Count | Status |
|-------|-------------|--------|
| events | 391 | ✅ Pending migration |
| users | 2 | ✅ Pending migration |
| sources | 0 | ✅ Has default data |
| Other tables | 0 | ✅ Empty tables |

---

## 🆘 Having Issues?

1. **Connection issues**: Check database password and network
2. **Schema errors**: Re-execute `supabase_schema.sql` in Supabase SQL Editor
3. **Migration failure**: See [Troubleshooting](./MIGRATION_TO_SUPABASE.md#troubleshooting)
4. **Other issues**: Read the [Full Migration Guide](./MIGRATION_TO_SUPABASE.md)

---

## 📞 Related Documentation

- 📘 [Full Migration Guide](./MIGRATION_TO_SUPABASE.md) - Detailed steps + troubleshooting
- 📄 [Migration Summary](./MIGRATION_SUMMARY.md) - Deliverables list + technical details
- 💾 [PostgreSQL Schema](./supabase_schema.sql) - Execute this to create tables
- 🔧 [Database Configuration](../apps/api/app/core/database.py) - asyncpg + databases

---

**Ready to go! Start migrating!**
