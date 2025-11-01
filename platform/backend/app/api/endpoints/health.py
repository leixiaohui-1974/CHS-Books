"""
健康检查端点
提供系统健康状态、数据库连接、Redis连接等信息
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone
import psutil
import sys

from app.core.database import get_db

router = APIRouter()


@router.get("/health", tags=["系统"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    系统健康检查
    返回系统状态、数据库连接、内存使用等信息
    """
    try:
        # 数据库连接检查
        await db.execute(text("SELECT 1"))
        database_status = "healthy"
    except Exception as e:
        database_status = f"unhealthy: {str(e)}"
    
    # 系统资源信息
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=0.1)
    
    return {
        "status": "healthy" if database_status == "healthy" else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "v1.3.0-stable",
        "components": {
            "database": {
                "status": database_status,
                "type": "PostgreSQL"
            },
            "api": {
                "status": "healthy"
            }
        },
        "system": {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "memory": {
                "total_mb": round(memory.total / (1024 * 1024), 2),
                "available_mb": round(memory.available / (1024 * 1024), 2),
                "percent": memory.percent
            },
            "cpu_percent": cpu_percent
        }
    }


@router.get("/ready", tags=["系统"])
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    就绪检查
    用于Kubernetes等容器编排系统
    """
    try:
        await db.execute(text("SELECT 1"))
        return {
            "ready": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "ready": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/live", tags=["系统"])
async def liveness_check():
    """
    存活检查
    用于Kubernetes等容器编排系统
    """
    return {
        "alive": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/metrics", tags=["系统"])
async def metrics():
    """
    简单的系统指标
    """
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used
        },
        "cpu": {
            "percent": psutil.cpu_percent(interval=0.1),
            "count": psutil.cpu_count()
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
    }
