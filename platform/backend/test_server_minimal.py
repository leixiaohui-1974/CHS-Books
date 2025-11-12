"""
最小化测试服务器 - 仅用于textbook API测试
不包含认证功能，避免jose/cryptography依赖问题
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
from loguru import logger

# 导入textbooks API（直接导入避免加载其他端点）
from app.api.endpoints.textbooks import router as textbooks_router

# 创建FastAPI应用
app = FastAPI(
    title="Textbook API Test Server",
    description="Minimal server for testing textbook API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request, call_next):
    """记录所有HTTP请求"""
    start_time = time.time()
    logger.info(f"📥 {request.method} {request.url.path}")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"📤 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    response.headers["X-Process-Time"] = str(process_time)

    return response

# 注册textbooks API路由
app.include_router(textbooks_router, prefix="/api/v1/textbooks", tags=["教材内容"])

# 根路径
@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "📚 Textbook API Test Server",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "api": "textbooks"
    }

if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 启动最小化测试服务器...")
    logger.info("📚 仅包含 Textbook API")
    logger.info("🌐 访问 http://localhost:8000/docs 查看API文档")

    uvicorn.run(
        "test_server_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
