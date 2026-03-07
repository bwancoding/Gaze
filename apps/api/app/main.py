from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.routes import events, admin, stakeholders, stakeholder_verify, personas

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WRHITW API",
    description="Multi-perspective News Aggregation Platform API",
    version="0.1.0"
)

# CORS 配置 - 允许所有来源（开发环境）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(admin.router, prefix="/api", tags=["Admin"])
app.include_router(stakeholders.router, prefix="/api", tags=["Stakeholders"])
app.include_router(stakeholder_verify.router, prefix="/api", tags=["Verification"])
app.include_router(personas.router, prefix="/api", tags=["Personas"])

@app.get("/")
async def root():
    return {
        "message": "WRHITW API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    from datetime import datetime
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat()
    }
