"""
FastAPI主应用
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.core.database import engine
from app.api import api_router
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info("🚀 应用启动中...")
    logger.info(f"📍 环境: {settings.ENVIRONMENT}")
    logger.info(f"🔧 调试模式: {settings.DEBUG}")
    
    yield
    
    # 关闭
    logger.info("👋 应用关闭中...")
    if engine:
        await engine.dispose()
    logger.info("✅ 数据库连接已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## 工程学习平台 API
    
    一个集教材、工具、AI助手三位一体的现代化工程学习平台。
    
    ### 核心功能
    
    * **用户系统** - 注册、登录、JWT认证
    * **课程管理** - 书籍、章节、案例三级结构
    * **学习追踪** - 完整的进度追踪系统
    * **工具执行** - 交互式工具运行
    * **AI助手** - 智能学习助手（开发中）
    
    ### 技术栈
    
    * FastAPI 0.104+
    * SQLAlchemy 2.0 (异步)
    * PostgreSQL 15
    * Redis 7
    * Python 3.11+
    
    ### 认证
    
    使用JWT Bearer token进行认证。在请求头中添加：
    ```
    Authorization: Bearer <your_token>
    ```
    """,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ========================================
# 中间件配置
# ========================================

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有HTTP请求"""
    start_time = time.time()
    
    # 记录请求
    logger.info(f"📥 {request.method} {request.url.path}")
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 记录响应
    logger.info(
        f"📤 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    # 添加处理时间头
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# ========================================
# 异常处理器
# ========================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    logger.warning(f"⚠️  验证错误: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "message": "请求参数验证失败"
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """处理数据库错误"""
    logger.error(f"❌ 数据库错误: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "数据库操作失败",
            "message": str(exc) if settings.DEBUG else "服务器内部错误"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    logger.error(f"❌ 未捕获异常: {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "服务器内部错误",
            "message": str(exc) if settings.DEBUG else "请联系管理员"
        }
    )


# ========================================
# 路由配置
# ========================================

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)


# 根路径
@app.get("/", tags=["根"])
async def root():
    """API根路径"""
    return {
        "message": "🎓 工程学习平台 API",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "status": "running",
        "environment": settings.ENVIRONMENT
    }


# 健康检查
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected" if engine else "disconnected"
    }


# 系统信息
@app.get("/info", tags=["系统"])
async def system_info():
    """系统信息"""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "cors_origins": settings.CORS_ORIGINS,
        "features": {
            "user_system": "✅",
            "course_management": "✅",
            "progress_tracking": "✅",
            "tool_execution": "✅",
            "payment_system": "⏳",
            "ai_assistant": "⏳"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
