"""
完整功能服务器 - 包含书籍管理
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
from pathlib import Path
import subprocess
import sys
import os

# 创建FastAPI应用
app = FastAPI(
    title="智能知识平台 V2.0 - 完整服务器",
    description="包含书籍管理、案例运行、AI助手的完整功能",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 知识库API
try:
    from api.knowledge_routes import router as knowledge_router
    app.include_router(knowledge_router)
    print('[OK] 知识库API已加载')
except ImportError as e:
    print(f'[WARN] 知识库API加载失败: {e}')
    print('[INFO] 如需使用知识库功能，请运行: pip install chromadb sentence-transformers')

# 教材API
try:
    from api.textbook_routes import router as textbook_router
    app.include_router(textbook_router)
    print('[OK] 教材API已加载')
except ImportError as e:
    print(f'[WARN] 教材API加载失败: {e}')

# 统一搜索API
try:
    from api.search_routes import router as search_router
    app.include_router(search_router)
    print('[OK] 统一搜索API已加载')
except ImportError as e:
    print(f'[WARN] 统一搜索API加载失败: {e}')

# 案例API
try:
    from api.case_routes import router as case_router
    app.include_router(case_router)
    print('[OK] 案例API已加载')
except ImportError as e:
    print(f'[WARN] 案例API加载失败: {e}')

# 代码执行API
try:
    from api.code_execution import router as execute_router
    app.include_router(execute_router)
    print('[OK] 代码执行API已加载')
except ImportError as e:
    print(f'[WARN] 代码执行API加载失败: {e}')

# 学习进度API
try:
    from api.progress_routes import router as progress_router
    app.include_router(progress_router)
    print('[OK] 学习进度API已加载')
except ImportError as e:
    print(f'[WARN] 学习进度API加载失败: {e}')

# 配置路径
BACKEND_DIR = Path(__file__).parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"
BOOKS_CATALOG_FILE = BACKEND_DIR / "books_catalog.json"
CASES_INDEX_FILE = BACKEND_DIR / "cases_index.json"
BOOKS_BASE_DIR = BACKEND_DIR.parent.parent  # 指向CHS-Books根目录

# 挂载静态文件目录（如果存在）
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# ==================== 工具函数 ====================

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

# ==================== 根路由 ====================

@app.get("/")
async def root():
    """根路径 - 返回统一前端页面"""
    unified_file = FRONTEND_DIR / "unified.html"
    if unified_file.exists():
        return HTMLResponse(content=unified_file.read_text(encoding='utf-8'))
    
    # 备用：旧版index.html
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding='utf-8'))
    
    # 如果前端不存在，返回API信息
    return {
        "message": "🎓 智能知识平台 V2.0 完整服务器",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "features": ["书籍管理", "案例运行", "代码智能", "AI助手"]
    }

@app.get("/learning")
async def learning_page():
    """统一学习平台页面"""
    learning_file = FRONTEND_DIR / "learning.html"
    if learning_file.exists():
        return HTMLResponse(content=learning_file.read_text(encoding='utf-8'))
    raise HTTPException(status_code=404, detail="学习平台页面未找到")

@app.get("/unified.html")
async def get_unified():
    """统一学习平台页面"""
    unified_file = FRONTEND_DIR / "unified.html"
    if unified_file.exists():
        return HTMLResponse(content=unified_file.read_text(encoding='utf-8'))
    raise HTTPException(status_code=404, detail="页面不存在")

@app.get("/textbooks.html")
async def get_textbooks():
    """教材阅读器页面"""
    textbooks_file = FRONTEND_DIR / "textbooks.html"
    if textbooks_file.exists():
        return HTMLResponse(content=textbooks_file.read_text(encoding='utf-8'))
    raise HTTPException(status_code=404, detail="页面不存在")

@app.get("/search.html")
async def get_search():
    """搜索页面"""
    search_file = FRONTEND_DIR / "search.html"
    if search_file.exists():
        return HTMLResponse(content=search_file.read_text(encoding='utf-8'))
    raise HTTPException(status_code=404, detail="页面不存在")

@app.get("/code-runner.html")
async def get_code_runner():
    """代码在线运行页面"""
    code_runner_file = FRONTEND_DIR / "code-runner.html"
    if code_runner_file.exists():
        return HTMLResponse(content=code_runner_file.read_text(encoding='utf-8'))
    raise HTTPException(status_code=404, detail="页面不存在")

@app.get("/ide", response_class=HTMLResponse)
async def ide():
    """AI编程IDE页面"""
    ide_file = FRONTEND_DIR / "ide.html"
    if ide_file.exists():
        return HTMLResponse(content=ide_file.read_text(encoding='utf-8'))
    else:
        raise HTTPException(status_code=404, detail="IDE页面不存在")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "server": "full"}

@app.get("/info")
async def system_info():
    """系统信息"""
    catalog = load_books_catalog()
    cases_index = load_cases_index()
    
    return {
        "version": "2.0.0",
        "books_count": len(catalog.get("books", [])),
        "total_cases": cases_index.get("total_cases", 0),
        "features": {
            "books_management": True,
            "case_execution": True,
            "ai_assistant": True,
            "code_intelligence": True
        }
    }

# ==================== 便捷案例API（快捷路由）====================

@app.get("/api/cases")
async def list_all_cases():
    """获取所有案例列表（聚合所有书籍的案例）"""
    cases_index = load_cases_index()
    all_cases = []
    
    for book_data in cases_index.get("books", []):
        book_slug = book_data.get("slug", "")
        for case in book_data.get("cases", []):
            case_info = case.copy()
            case_info["book_slug"] = book_slug
            all_cases.append(case_info)
    
    return all_cases

@app.get("/api/cases/{case_id}")
async def get_case_by_id(case_id: str):
    """通过case_id直接获取案例详情"""
    cases_index = load_cases_index()
    
    # 遍历所有书籍查找案例
    for book_data in cases_index.get("books", []):
        book_slug = book_data.get("slug", "")
        for case in book_data.get("cases", []):
            if case.get("id") == case_id:
                # 找到案例，返回完整信息
                case_dir = BOOKS_BASE_DIR / "books" / book_slug / "code" / "examples" / case_id
                
                # 读取README
                readme_file = case_dir / "README.md"
                readme_content = ""
                if readme_file.exists():
                    readme_content = readme_file.read_text(encoding='utf-8')
                
                return {
                    **case,
                    "book_slug": book_slug,
                    "readme": readme_content,
                    "path": str(case_dir)
                }
    
    raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")

@app.get("/api/cases/{case_id}/diagram.png")
async def get_case_diagram(case_id: str):
    """获取案例示意图"""
    cases_index = load_cases_index()
    
    # 查找案例所属的书籍
    for book_data in cases_index.get("books", []):
        book_slug = book_data.get("slug", "")
        for case in book_data.get("cases", []):
            if case.get("id") == case_id:
                # 找到案例
                case_dir = BOOKS_BASE_DIR / "books" / book_slug / "code" / "examples" / case_id
                diagram_file = case_dir / "diagram.png"
                
                if diagram_file.exists():
                    return FileResponse(
                        diagram_file,
                        media_type="image/png",
                        headers={"Cache-Control": "public, max-age=3600"}
                    )
                else:
                    raise HTTPException(status_code=404, detail="Diagram not found")
    
    raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")

@app.post("/api/run")
async def run_case_by_id(request: dict):
    """通过case_id运行案例"""
    case_id = request.get("case_id")
    if not case_id:
        raise HTTPException(status_code=400, detail="case_id is required")
    
    cases_index = load_cases_index()
    
    # 查找案例
    for book_data in cases_index.get("books", []):
        book_slug = book_data.get("slug", "")
        for case in book_data.get("cases", []):
            if case.get("id") == case_id:
                # 找到案例，运行它
                case_dir = BOOKS_BASE_DIR / "books" / book_slug / "code" / "examples" / case_id
                
                try:
                    result = subprocess.run(
                        [sys.executable, "main.py"],
                        cwd=str(case_dir),
                        capture_output=True,
                        text=True,
                        timeout=60,
                        encoding='utf-8',
                        errors='replace'
                    )
                    
                    return {
                        "success": result.returncode == 0,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "returncode": result.returncode
                    }
                except subprocess.TimeoutExpired:
                    return {
                        "success": False,
                        "error": "Execution timeout (60s)"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": str(e)
                    }
    
    raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")

@app.get("/api/results/{case_id}")
async def get_case_results(case_id: str):
    """获取案例的结果文件列表"""
    cases_index = load_cases_index()
    
    # 查找案例
    for book_data in cases_index.get("books", []):
        book_slug = book_data.get("slug", "")
        for case in book_data.get("cases", []):
            if case.get("id") == case_id:
                # 找到案例
                case_dir = BOOKS_BASE_DIR / "books" / book_slug / "code" / "examples" / case_id
                results_dir = case_dir / "results"
                
                if not results_dir.exists():
                    return []
                
                result_files = []
                for file in results_dir.iterdir():
                    if file.is_file() and file.suffix in ['.png', '.jpg', '.pdf', '.txt', '.csv']:
                        result_files.append({
                            "name": file.name,
                            "size": file.stat().st_size,
                            "type": file.suffix[1:],
                            "url": f"/api/cases/{case_id}/results/{file.name}"
                        })
                
                return result_files
    
    raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")

@app.get("/api/files/{case_id}")
async def list_case_files(case_id: str):
    """列出案例的所有文件"""
    cases_index = load_cases_index()
    
    # 查找案例
    for book_data in cases_index.get("books", []):
        book_slug = book_data.get("slug", "")
        for case in book_data.get("cases", []):
            if case.get("id") == case_id:
                # 找到案例
                case_dir = BOOKS_BASE_DIR / "books" / book_slug / "code" / "examples" / case_id
                
                if not case_dir.exists():
                    return []
                
                files = []
                for file in case_dir.iterdir():
                    if file.is_file():
                        files.append({
                            "name": file.name,
                            "size": file.stat().st_size,
                            "type": "file",
                            "extension": file.suffix
                        })
                
                return files
    
    raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")

@app.get("/api/file_content")
async def get_file_content(case_id: str, file_path: str):
    """获取文件内容"""
    cases_index = load_cases_index()
    
    # 查找案例
    for book_data in cases_index.get("books", []):
        book_slug = book_data.get("slug", "")
        for case in book_data.get("cases", []):
            if case.get("id") == case_id:
                # 找到案例
                case_dir = BOOKS_BASE_DIR / "books" / book_slug / "code" / "examples" / case_id
                file = case_dir / file_path
                
                if not file.exists() or not file.is_file():
                    raise HTTPException(status_code=404, detail="File not found")
                
                try:
                    content = file.read_text(encoding='utf-8')
                    return {"content": content}
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")
    
    raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")

@app.post("/api/terminal/execute")
async def execute_terminal_command(request: dict):
    """执行终端命令"""
    case_id = request.get("case_id")
    command = request.get("command")
    
    if not case_id or not command:
        raise HTTPException(status_code=400, detail="case_id and command are required")
    
    cases_index = load_cases_index()
    
    # 查找案例
    for book_data in cases_index.get("books", []):
        book_slug = book_data.get("slug", "")
        for case in book_data.get("cases", []):
            if case.get("id") == case_id:
                # 找到案例
                case_dir = BOOKS_BASE_DIR / "books" / book_slug / "code" / "examples" / case_id
                
                try:
                    result = subprocess.run(
                        command,
                        cwd=str(case_dir),
                        capture_output=True,
                        text=True,
                        timeout=30,
                        shell=True,
                        encoding='utf-8',
                        errors='replace'
                    )
                    
                    return {
                        "output": result.stdout + result.stderr,
                        "returncode": result.returncode
                    }
                except subprocess.TimeoutExpired:
                    return {
                        "output": "Command timeout (30s)",
                        "returncode": -1
                    }
                except Exception as e:
                    return {
                        "output": f"Error: {str(e)}",
                        "returncode": -1
                    }
    
    raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")

# ==================== 书籍管理API ====================

@app.get("/api/v1/books")
async def list_books():
    """获取所有书籍列表"""
    catalog = load_books_catalog()
    cases_index = load_cases_index()
    
    books = catalog.get("books", [])
    for book in books:
        for book_cases in cases_index.get("books", []):
            if book_cases["slug"] == book["slug"]:
                book["actual_cases"] = book_cases.get("cases_count", 0)
                break
    
    return {
        "success": True,
        "books": books,
        "statistics": catalog.get("statistics", {}),
        "total_scanned_cases": cases_index.get("total_cases", 0)
    }

@app.get("/api/v1/books/{book_slug}")
async def get_book_detail(book_slug: str):
    """获取书籍详细信息"""
    catalog = load_books_catalog()
    cases_index = load_cases_index()
    
    book = None
    for b in catalog.get("books", []):
        if b["slug"] == book_slug:
            book = b.copy()
            break
    
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    
    for book_cases in cases_index.get("books", []):
        if book_cases["slug"] == book_slug:
            book["cases"] = book_cases.get("cases", [])
            book["actual_cases"] = book_cases.get("cases_count", 0)
            break
    
    return {
        "success": True,
        "book": book
    }

@app.get("/api/v1/books/{book_slug}/cases")
async def list_book_cases(book_slug: str, skip: int = 0, limit: int = 100):
    """获取书籍的所有案例"""
    cases_index = load_cases_index()
    
    for book_cases in cases_index.get("books", []):
        if book_cases["slug"] == book_slug:
            cases = book_cases.get("cases", [])
            return {
                "success": True,
                "book_slug": book_slug,
                "total": len(cases),
                "cases": cases[skip:skip + limit]
            }
    
    raise HTTPException(status_code=404, detail="书籍案例不存在")

@app.get("/api/v1/books/{book_slug}/cases/{case_id}")
async def get_case_detail(book_slug: str, case_id: str):
    """获取案例详细信息"""
    cases_index = load_cases_index()
    
    for book_cases in cases_index.get("books", []):
        if book_cases["slug"] == book_slug:
            cases = book_cases.get("cases", [])
            
            for case in cases:
                if case["id"] == case_id:
                    case_path = BOOKS_BASE_DIR / case["path"]
                    readme_path = case_path / "README.md"
                    main_path = case_path / "main.py"
                    
                    case_detail = case.copy()
                    
                    if readme_path.exists():
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            case_detail["readme"] = f.read()
                    
                    if main_path.exists():
                        with open(main_path, 'r', encoding='utf-8') as f:
                            case_detail["code"] = f.read()
                    
                    return {
                        "success": True,
                        "case": case_detail
                    }
            
            raise HTTPException(status_code=404, detail="案例不存在")
    
    raise HTTPException(status_code=404, detail="书籍不存在")

class CodeRunRequest(BaseModel):
    """代码运行请求"""
    code: Optional[str] = None  # 如果提供，使用自定义代码；否则使用文件中的代码

class AIAnalyzeRequest(BaseModel):
    """AI分析请求"""
    code: str
    case_id: str
    question: Optional[str] = None

@app.post("/api/v1/books/{book_slug}/cases/{case_id}/run")
async def run_case(book_slug: str, case_id: str, request: CodeRunRequest = None, timeout: int = 60):
    """运行案例脚本（支持自定义代码）"""
    cases_index = load_cases_index()
    
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
    
    # 如果提供了自定义代码，创建临时文件
    temp_file = None
    if request and request.code:
        temp_file = case_path / "main_custom.py"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(request.code)
            script_to_run = temp_file
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"保存自定义代码失败: {str(e)}")
    else:
        if not main_file.exists():
            raise HTTPException(status_code=400, detail="案例脚本不存在")
        script_to_run = main_file
    
    try:
        # 先删除旧的结果图片文件（不删除示意图）
        # 保留以下文件：water_tower_diagram.png, *_diagram.png, *_schematic.png
        preserved_patterns = ['diagram', 'schematic', 'structure']
        for old_img in case_path.glob("*.png"):
            # 检查是否是需要保留的示意图
            should_preserve = any(pattern in old_img.stem.lower() for pattern in preserved_patterns)
            if not should_preserve:
                try:
                    old_img.unlink()
                    print(f"删除旧结果图: {old_img.name}")
                except Exception as e:
                    print(f"删除图片失败: {old_img.name}, 错误: {e}")
            else:
                print(f"保留示意图: {old_img.name}")
        
        # 设置环境变量强制UTF-8编码
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            [sys.executable, str(script_to_run)],
            cwd=str(case_path),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        
        # 等待文件系统同步（等待图片完全写入磁盘）
        import time
        time.sleep(2.0)  # 增加到2秒，确保图片完全写入
        
        # 扫描生成的图片文件
        images = []
        print(f"扫描路径: {case_path}")
        for img_file in case_path.glob("*.png"):
            print(f"找到图片: {img_file.name}")
            images.append({
                "filename": img_file.name,
                "url": f"/api/v1/books/{book_slug}/cases/{case_id}/images/{img_file.name}"
            })
        print(f"共找到 {len(images)} 张图片")
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "output": result.stdout,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "message": "代码运行成功" if result.returncode == 0 else "代码运行失败",
            "case_id": case_id,
            "images": images
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
    finally:
        # 清理临时文件
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
            except:
                pass

@app.post("/api/v1/ai/analyze")
async def analyze_code(request: AIAnalyzeRequest):
    """AI代码分析和建议"""
    import re
    
    code = request.code
    case_id = request.case_id
    question = request.question
    
    # 提取参数
    params = {}
    param_patterns = {
        'A': r'A\s*=\s*([\d.]+)',
        'R': r'R\s*=\s*([\d.]+)',
        'K': r'K\s*=\s*([\d.]+)',
        'Kp': r'Kp\s*=\s*([\d.]+)',
        'Ki': r'Ki\s*=\s*([\d.]+)',
        'Kd': r'Kd\s*=\s*([\d.]+)',
        'h0': r'h0\s*=\s*([\d.]+)',
        'setpoint': r'setpoint\s*=\s*([\d.]+)',
        'low_threshold': r'low_threshold\s*=\s*([\d.]+)',
        'high_threshold': r'high_threshold\s*=\s*([\d.]+)',
    }
    
    for key, pattern in param_patterns.items():
        match = re.search(pattern, code)
        if match:
            params[key] = float(match.group(1))
    
    # 根据案例类型生成建议
    suggestions = generate_ai_suggestions(case_id, params)
    
    # 如果有问题，生成回答
    answer = None
    if question:
        answer = generate_ai_answer(question, case_id, params)
    
    return {
        "success": True,
        "params": params,
        "suggestions": suggestions,
        "answer": answer
    }

def generate_ai_suggestions(case_id, params):
    """生成AI建议"""
    suggestions = []
    
    if 'case_01' in case_id:
        # 案例1: 开关控制
        low = params.get('low_threshold', 2.5)
        high = params.get('high_threshold', 3.5)
        hysteresis = high - low
        
        suggestions.append({
            "icon": "🎯",
            "title": "滞环宽度优化",
            "description": f"当前滞环宽度为 {hysteresis:.1f}m。建议：宽度在0.5-1.5m之间可平衡开关频率和波动幅度",
            "priority": "high",
            "params": {
                "low_threshold": {"current": low, "suggested": [2.3, 2.5, 2.7], "range": [2.0, 3.0]},
                "high_threshold": {"current": high, "suggested": [3.3, 3.5, 3.7], "range": [3.0, 4.0]}
            }
        })
        
        K = params.get('K', 1.0)
        suggestions.append({
            "icon": "⚡",
            "title": "泵流量调整",
            "description": f"当前泵流量增益K={K:.1f}。增大K可加快响应，但会增加超调",
            "priority": "medium",
            "params": {
                "K": {"current": K, "suggested": [0.8, 1.0, 1.2, 1.5], "range": [0.5, 2.0]}
            }
        })
        
    elif 'case_02' in case_id:
        # 案例2: 比例控制
        Kp = params.get('Kp', 1.0)
        
        if Kp < 0.5:
            priority = "high"
            desc = f"Kp={Kp:.2f}过小，系统响应太慢，建议增大到0.8-1.2"
        elif Kp > 2.0:
            priority = "high"
            desc = f"Kp={Kp:.2f}过大，可能导致振荡，建议减小到0.8-1.5"
        else:
            priority = "medium"
            desc = f"Kp={Kp:.2f}在合理范围内，可微调以优化性能"
        
        suggestions.append({
            "icon": "📊",
            "title": "比例增益Kp调整",
            "description": desc,
            "priority": priority,
            "params": {
                "Kp": {"current": Kp, "suggested": [0.6, 0.8, 1.0, 1.2, 1.5], "range": [0.3, 2.5]}
            }
        })
        
        setpoint = params.get('setpoint', 3.0)
        suggestions.append({
            "icon": "🎚️",
            "title": "目标水位设定",
            "description": f"当前目标水位={setpoint:.1f}m。注意比例控制会有稳态误差",
            "priority": "low",
            "params": {
                "setpoint": {"current": setpoint, "suggested": [2.5, 3.0, 3.5], "range": [2.0, 4.0]}
            }
        })
        
    elif 'case_03' in case_id or 'case_04' in case_id:
        # 案例3/4: PI/PID控制
        Kp = params.get('Kp', 1.0)
        Ki = params.get('Ki', 0.1)
        Kd = params.get('Kd', 0.0)
        
        suggestions.append({
            "icon": "🎛️",
            "title": "PID参数整体评估",
            "description": f"当前参数 Kp={Kp:.2f}, Ki={Ki:.3f}, Kd={Kd:.3f}",
            "priority": "high",
            "params": {
                "Kp": {"current": Kp, "suggested": [0.8, 1.0, 1.2], "range": [0.3, 2.0]},
                "Ki": {"current": Ki, "suggested": [0.05, 0.1, 0.15, 0.2], "range": [0.01, 0.5]},
                "Kd": {"current": Kd, "suggested": [0.0, 0.05, 0.1], "range": [0.0, 0.3]}
            }
        })
        
        # Ziegler-Nichols建议
        if Kp > 0:
            suggestions.append({
                "icon": "📐",
                "title": "Ziegler-Nichols整定法建议",
                "description": "可尝试：先增大Kp直到临界振荡，然后Kp=0.6*Kp_critical, Ki=1.2*Kp/T, Kd=0.075*Kp*T",
                "priority": "medium",
                "tips": [
                    "1. 先设Ki=0, Kd=0，调Kp",
                    "2. 当系统出现持续振荡时记录Kp和周期T",
                    "3. 按公式计算最终参数"
                ]
            })
    
    # 通用建议
    A = params.get('A', 2.0)
    R = params.get('R', 2.0)
    tau = A * R
    
    suggestions.append({
        "icon": "⚙️",
        "title": "系统特性分析",
        "description": f"当前系统参数：A={A:.1f}m², R={R:.1f}min/m², 时间常数τ={tau:.1f}分钟",
        "priority": "low",
        "params": {
            "A": {"current": A, "suggested": [1.5, 2.0, 2.5, 3.0], "range": [1.0, 5.0]},
            "R": {"current": R, "suggested": [1.5, 2.0, 2.5, 3.0, 5.0], "range": [1.0, 10.0]}
        },
        "tips": [
            f"• 时间常数τ={tau:.1f}分钟，表示系统响应速度",
            "• A越大系统惯性越大，响应越慢",
            "• R越大流出阻力越大，水位变化越慢"
        ]
    })
    
    return suggestions

def generate_ai_answer(question, case_id, params):
    """生成AI回答"""
    q = question.lower()
    
    answers = {
        "参数": {
            "answer": "控制参数的选择需要平衡多个性能指标：",
            "points": [
                "• **Kp（比例增益）**：控制响应速度，增大Kp可加快响应但可能振荡",
                "• **Ki（积分增益）**：消除稳态误差，但过大会超调和振荡",
                "• **Kd（微分增益）**：抑制振荡，改善稳定性，但对噪声敏感",
                "• 建议从小到大逐步调整，观察系统响应"
            ]
        },
        "效果": {
            "answer": "评估控制效果需要关注以下指标：",
            "points": [
                "• **超调量**：首次峰值超过目标值的百分比，一般要求<25%",
                "• **调节时间**：达到并保持在目标值±5%范围内的时间",
                "• **稳态误差**：稳定后与目标值的偏差，理想为0",
                "• **振荡次数**：过多振荡说明参数需要优化"
            ]
        },
        "优化": {
            "answer": "参数优化的一般流程：",
            "points": [
                "1. 先确定系统模型参数（A, R, K）",
                "2. 使用经验法或整定法获得初值",
                "3. 运行并观察响应曲线",
                "4. 根据性能指标微调参数",
                "5. 重复3-4直到满意"
            ]
        }
    }
    
    for keyword, content in answers.items():
        if keyword in q:
            return content
    
    # 默认回答
    return {
        "answer": "我可以帮你分析代码和优化参数。",
        "points": [
            "• 查看左侧AI助手面板的智能建议",
            "• 尝试修改参数并运行观察效果",
            "• 对比不同参数下的结果图表",
            "• 有具体问题欢迎继续提问"
        ]
    }

@app.get("/api/v1/books/{book_slug}/cases/{case_id}/images/{filename}")
async def get_case_image(book_slug: str, case_id: str, filename: str):
    """获取案例生成的图片"""
    from fastapi.responses import FileResponse
    
    cases_index = load_cases_index()
    
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
    
    image_path = case_path / filename
    if not image_path.exists() or image_path.suffix != '.png':
        raise HTTPException(status_code=404, detail="图片不存在")
    
    return FileResponse(image_path, media_type="image/png")

# ==================== 代码验证API ====================

class CodeValidate(BaseModel):
    code: str

@app.post("/api/v1/code/validate")
async def validate_code(data: CodeValidate):
    """验证代码"""
    try:
        compile(data.code, '<string>', 'exec')
        return {
            "success": True,
            "is_valid": True,
            "message": "代码语法正确",
            "errors": []
        }
    except SyntaxError as e:
        return {
            "success": True,
            "is_valid": False,
            "message": "语法错误",
            "errors": [{
                "line": e.lineno,
                "message": e.msg
            }]
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

