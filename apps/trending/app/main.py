"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db
from app.api import health

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("🚀 WRHITW Trending API 启动中...")
    logger.info(f"📍 环境：{settings.ENVIRONMENT}")
    logger.info(f"📍 端口：{settings.API_PORT}")
    
    # 初始化数据库（开发环境）
    if settings.DEBUG:
        init_db()
        logger.info("✅ 数据库初始化完成")
    
    yield
    
    # 关闭时
    logger.info("👋 WRHITW Trending API 关闭中...")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="WRHITW 热榜话题聚合 API - 提供全球新闻事件热度排行",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, prefix="/health", tags=["health"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/status")
async def status():
    """服务状态"""
    return {
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.WORKERS,
        reload=settings.DEBUG
    )
