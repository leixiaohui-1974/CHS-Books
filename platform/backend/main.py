"""
Engineering Learning Platform - Backend Main Application
FastAPI主应用入口
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import make_asgi_app
import time
import logging

from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.core.cache import redis_client
from app.core.monitoring import setup_monitoring
from app.api import api_router

# 配置日志
from loguru import logger
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    level=settings.LOG_LEVEL
)


# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭时的生命周期管理"""
    # 启动时
    logger.info("🚀 启动应用...")
    
    # 初始化数据库表（开发环境）
    if settings.APP_ENV == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ 数据库表已创建")
    
    # 测试Redis连接
    try:
        await redis_client.ping()
        logger.info("✅ Redis连接成功")
    except Exception as e:
        logger.error(f"❌ Redis连接失败: {e}")
    
    # 设置监控
    setup_monitoring()
    logger.info("✅ 监控系统已启动")
    
    logger.info("✅ 应用启动完成！")
    
    yield
    
    # 关闭时
    logger.info("👋 关闭应用...")
    await redis_client.close()
    await engine.dispose()
    logger.info("✅ 应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="智能工程教学平台API",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
    lifespan=lifespan,
    openapi_tags=[
        {"name": "认证", "description": "用户认证和授权"},
        {"name": "用户", "description": "用户管理"},
        {"name": "书籍", "description": "教材书籍管理"},
        {"name": "章节", "description": "章节内容"},
        {"name": "案例", "description": "教学案例"},
        {"name": "工具", "description": "交互式工具"},
        {"name": "AI助手", "description": "智能学习助手"},
        {"name": "支付", "description": "支付相关"},
        {"name": "学习进度", "description": "学习进度追踪"},
        {"name": "管理员", "description": "管理员功能"},
    ]
)


# ========================================
# 中间件配置
# ========================================

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 受信任主机（生产环境）
if settings.APP_ENV == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )


# 速率限制
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有HTTP请求"""
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"📥 {request.method} {request.url.path}")
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # 记录响应信息
    logger.info(
        f"📤 {request.method} {request.url.path} "
        f"- Status: {response.status_code} "
        f"- Time: {process_time:.3f}s"
    )
    
    return response


# ========================================
# 异常处理
# ========================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    logger.warning(f"❌ 验证错误: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "请求数据验证失败",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未捕获的异常"""
    logger.error(f"❌ 未捕获异常: {type(exc).__name__}: {str(exc)}")
    
    if settings.APP_ENV == "development":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": f"服务器内部错误: {str(exc)}",
                "type": type(exc).__name__
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "服务器内部错误，请稍后重试"
            }
        )


# ========================================
# 路由注册
# ========================================

# 健康检查
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV
    }


# 根路径
@app.get("/", tags=["系统"])
async def root():
    """API根路径"""
    return {
        "message": "Welcome to Engineering Learning Platform API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.APP_DEBUG else "Disabled in production",
        "health": "/health"
    }


# Prometheus指标
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# 注册API路由
app.include_router(api_router, prefix="/api/v1")


# ========================================
# 启动命令
# ========================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
