"""
独立Textbook服务器 - 主应用
快速启动，用于前后端集成测试
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from database import init_db, get_db, engine
from api import router as textbook_router
from seed_data import seed_example_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    print("🚀 启动独立Textbook服务器...")
    print("📦 初始化数据库...")
    await init_db()
    print("✅ 数据库初始化完成")

    yield

    # 关闭
    print("👋 关闭服务器...")
    await engine.dispose()
    print("✅ 数据库连接已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="Textbook API Server",
    description="独立的教材内容API服务器，用于前后端集成测试",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(textbook_router, prefix="/api/v1/textbooks", tags=["Textbooks"])


# ==================== 根端点 ====================

@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "📚 Textbook API Server",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "sqlite"
    }


@app.post("/api/v1/seed")
async def seed_data_endpoint(db: AsyncSession = Depends(get_db)):
    """创建示例数据（便于测试）"""
    result = await seed_example_data(db)
    return {
        "message": "示例数据已创建",
        **result,
        "preview_url": f"/api/v1/textbooks/{result['book_slug']}/{result['chapter_slug']}/{result['case_slug']}"
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("📚 独立Textbook API服务器")
    print("=" * 60)
    print()
    print("✨ 特性:")
    print("  - SQLite数据库（无需PostgreSQL）")
    print("  - 完整Textbook API")
    print("  - 自动创建数据表")
    print("  - 示例数据生成")
    print()
    print("🌐 访问:")
    print("  - API文档: http://localhost:8000/docs")
    print("  - 健康检查: http://localhost:8000/health")
    print("  - 创建示例: http://localhost:8000/api/v1/seed (POST)")
    print()
    print("🚀 启动服务器...")
    print("=" * 60)
    print()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
