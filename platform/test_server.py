#!/usr/bin/env python3
"""
简化的测试服务器 - 用于前端功能测试
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from pathlib import Path

app = FastAPI(title="Platform Test Server", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟数据
MOCK_BOOKS = [
    {
        "id": 1,
        "title": "水系统控制理论",
        "slug": "water-system-control",
        "description": "水系统控制理论教程",
        "chapters_count": 20,
        "cases_count": 45
    },
    {
        "id": 2,
        "title": "生态水力学",
        "slug": "ecohydraulics",
        "description": "生态水力学研究",
        "chapters_count": 15,
        "cases_count": 32
    }
]

MOCK_CHAPTERS = [
    {
        "id": 1,
        "book_id": 1,
        "title": "第一章 基础理论",
        "order": 1,
        "content": "# 第一章 基础理论\n\n这是基础理论的内容..."
    },
    {
        "id": 2,
        "book_id": 1,
        "title": "第二章 控制系统设计",
        "order": 2,
        "content": "# 第二章 控制系统设计\n\n这是控制系统设计的内容..."
    }
]

MOCK_CASES = [
    {
        "id": 1,
        "title": "案例1: 水池液位控制",
        "description": "使用PID控制器进行水池液位控制",
        "difficulty": "easy",
        "tags": ["PID", "液位控制"]
    },
    {
        "id": 2,
        "title": "案例2: 管道流量控制",
        "description": "管道流量的自动控制",
        "difficulty": "medium",
        "tags": ["流量控制", "自动化"]
    }
]

# 根路径
@app.get("/")
async def root():
    return {
        "message": "Platform Test Server",
        "version": "1.0.0",
        "status": "running"
    }

# 健康检查
@app.get("/health")
@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

# 书籍列表
@app.get("/api/v1/books")
async def get_books():
    return {
        "success": True,
        "data": MOCK_BOOKS,
        "total": len(MOCK_BOOKS)
    }

# 获取单本书籍
@app.get("/api/v1/books/{book_id}")
async def get_book(book_id: int):
    book = next((b for b in MOCK_BOOKS if b["id"] == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {
        "success": True,
        "data": book
    }

# 章节列表
@app.get("/api/v1/books/{book_id}/chapters")
async def get_chapters(book_id: int):
    chapters = [c for c in MOCK_CHAPTERS if c["book_id"] == book_id]
    return {
        "success": True,
        "data": chapters,
        "total": len(chapters)
    }

# 案例列表
@app.get("/api/v1/cases")
async def get_cases():
    return {
        "success": True,
        "data": MOCK_CASES,
        "total": len(MOCK_CASES)
    }

# 搜索接口
@app.get("/api/v1/search")
async def search(q: str = ""):
    results = []
    if q:
        # 简单的搜索逻辑
        for book in MOCK_BOOKS:
            if q.lower() in book["title"].lower():
                results.append({"type": "book", **book})
        for case in MOCK_CASES:
            if q.lower() in case["title"].lower():
                results.append({"type": "case", **case})
    return {
        "success": True,
        "data": results,
        "query": q,
        "total": len(results)
    }

# 执行代码接口（模拟）
@app.post("/api/v1/execute")
async def execute_code(request: dict):
    code = request.get("code", "")
    return {
        "success": True,
        "output": f"代码执行成功\n输入代码:\n{code[:100]}...\n\n模拟输出: Hello from test server!",
        "execution_time": 0.123
    }

if __name__ == "__main__":
    print("=" * 50)
    print("Platform Test Server Starting...")
    print("=" * 50)
    print("Frontend: http://localhost:8080")
    print("Backend:  http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
