"""
健康检查 API
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/")
async def health_check():
    """
    健康检查端点
    
    返回服务状态、时间戳和基本信息
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "WRHITW Trending API",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check():
    """
    就绪检查端点
    
    用于 Kubernetes 等编排系统的就绪探针
    """
    # TODO: 添加数据库连接检查、Redis 连接检查等
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat()
    }
