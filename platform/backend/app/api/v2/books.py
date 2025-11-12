"""
书籍和案例管理API
"""

from fastapi import APIRouter, HTTPException, Path as PathParam
from typing import List, Dict, Optional
import json
from pathlib import Path
import subprocess
import sys
import tempfile

router = APIRouter()

# 加载书籍目录
BACKEND_DIR = Path(__file__).parent.parent.parent.parent
BOOKS_CATALOG_FILE = BACKEND_DIR / "books_catalog.json"
CASES_INDEX_FILE = BACKEND_DIR / "cases_index.json"
BOOKS_BASE_DIR = BACKEND_DIR.parent.parent / "books"

def load_books_catalog():
    """加载书籍目录"""
    if not BOOKS_CATALOG_FILE.exists():
        return {"books": [], "statistics": {}}
    
    with open(BOOKS_CATALOG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_cases_index():
    """加载案例索引"""
    if not CASES_INDEX_FILE.exists():
        return {"books": [], "total_cases": 0}
    
    with open(CASES_INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

@router.get("/")
async def list_books():
    """获取所有书籍列表"""
    catalog = load_books_catalog()
    cases_index = load_cases_index()
    
    # 合并案例统计信息
    books = catalog.get("books", [])
    for book in books:
        # 从索引中找到对应的案例信息
        for book_cases in cases_index.get("books", []):
            if book_cases["slug"] == book["slug"]:
                book["actual_cases"] = book_cases.get("cases_count", 0)
                if "chapters" in book_cases:
                    book["has_chapters"] = True
                    book["chapters_count"] = book_cases.get("chapters_count", 0)
                break
    
    return {
        "success": True,
        "books": books,
        "statistics": catalog.get("statistics", {}),
        "total_scanned_cases": cases_index.get("total_cases", 0)
    }

@router.get("/{book_slug}")
async def get_book_detail(book_slug: str = PathParam(..., description="书籍标识")):
    """获取书籍详细信息"""
    catalog = load_books_catalog()
    cases_index = load_cases_index()
    
    # 查找书籍
    book = None
    for b in catalog.get("books", []):
        if b["slug"] == book_slug:
            book = b.copy()
            break
    
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    
    # 添加案例列表
    for book_cases in cases_index.get("books", []):
        if book_cases["slug"] == book_slug:
            book["cases"] = book_cases.get("cases", [])
            book["chapters"] = book_cases.get("chapters", [])
            book["actual_cases"] = book_cases.get("cases_count", 0)
            break
    
    return {
        "success": True,
        "book": book
    }

@router.get("/{book_slug}/cases")
async def list_book_cases(
    book_slug: str = PathParam(..., description="书籍标识"),
    skip: int = 0,
    limit: int = 100
):
    """获取书籍的所有案例"""
    cases_index = load_cases_index()
    
    # 查找书籍案例
    for book_cases in cases_index.get("books", []):
        if book_cases["slug"] == book_slug:
            cases = book_cases.get("cases", [])
            total = len(cases)
            
            return {
                "success": True,
                "book_slug": book_slug,
                "total": total,
                "cases": cases[skip:skip + limit]
            }
    
    raise HTTPException(status_code=404, detail="书籍案例不存在")

@router.get("/{book_slug}/cases/{case_id}")
async def get_case_detail(
    book_slug: str = PathParam(..., description="书籍标识"),
    case_id: str = PathParam(..., description="案例标识")
):
    """获取案例详细信息"""
    cases_index = load_cases_index()
    
    # 查找案例
    for book_cases in cases_index.get("books", []):
        if book_cases["slug"] == book_slug:
            cases = book_cases.get("cases", [])
            
            for case in cases:
                if case["id"] == case_id:
                    # 读取README文件
                    case_path = BOOKS_BASE_DIR / case["path"]
                    readme_path = case_path / "README.md"
                    
                    case_detail = case.copy()
                    
                    if readme_path.exists():
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            case_detail["readme"] = f.read()
                    
                    # 读取main.py
                    main_path = case_path / "main.py"
                    if main_path.exists():
                        with open(main_path, 'r', encoding='utf-8') as f:
                            case_detail["code"] = f.read()
                    
                    return {
                        "success": True,
                        "case": case_detail
                    }
            
            raise HTTPException(status_code=404, detail="案例不存在")
    
    raise HTTPException(status_code=404, detail="书籍不存在")

@router.post("/{book_slug}/cases/{case_id}/run")
async def run_case(
    book_slug: str = PathParam(..., description="书籍标识"),
    case_id: str = PathParam(..., description="案例标识"),
    timeout: int = 60
):
    """运行案例脚本"""
    cases_index = load_cases_index()
    
    # 查找案例路径
    case_path = None
    for book_cases in cases_index.get("books", []):
        if book_cases["slug"] == book_slug:
            cases = book_cases.get("cases", [])
            for case in cases:
                if case["id"] == case_id:
                    case_path = BOOKS_BASE_DIR / case["path"]
                    break
            break
    
    if not case_path or not case_path.exists():
        raise HTTPException(status_code=404, detail="案例不存在")
    
    main_file = case_path / "main.py"
    if not main_file.exists():
        raise HTTPException(status_code=400, detail="案例脚本不存在")
    
    # 运行脚本
    try:
        result = subprocess.run(
            [sys.executable, str(main_file)],
            cwd=str(case_path),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "case_id": case_id,
            "execution_time": "完成"
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "执行超时",
            "timeout": timeout
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/statistics/overall")
async def get_overall_statistics():
    """获取整体统计信息"""
    catalog = load_books_catalog()
    cases_index = load_cases_index()
    
    return {
        "success": True,
        "catalog_statistics": catalog.get("statistics", {}),
        "scanned_statistics": {
            "total_books": cases_index.get("total_books", 0),
            "total_cases": cases_index.get("total_cases", 0)
        }
    }

