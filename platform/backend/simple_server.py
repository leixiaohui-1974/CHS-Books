"""
简化的测试服务器 - 无需数据库依赖
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import asyncio
import ast

# 创建FastAPI应用
app = FastAPI(
    title="智能知识平台 V2.0 - 测试服务器",
    description="功能测试和演示服务器",
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

# ==================== 数据模型 ====================

class SessionCreate(BaseModel):
    user_id: str
    book_slug: str
    case_slug: str

class CodeLoad(BaseModel):
    book_slug: str
    case_slug: str

class CodeValidate(BaseModel):
    code: str

class CodeExplain(BaseModel):
    code: str
    context: Optional[str] = None

class ErrorDiagnose(BaseModel):
    code: str
    error: str

class ExecutionStart(BaseModel):
    session_id: str
    script_path: str
    parameters: Optional[Dict] = None

# ==================== 根路径和系统端点 ====================

@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "🎓 智能知识平台 V2.0 测试服务器",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "features": [
            "会话管理",
            "代码智能",
            "代码执行",
            "AI助手",
            "结果解析"
        ]
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": "test",
        "database": "in-memory"
    }

@app.get("/info")
async def system_info():
    """系统信息"""
    return {
        "project": "智能知识平台 V2.0",
        "version": "2.0.0",
        "features": {
            "session_management": "✅ V2.0",
            "code_execution": "✅ V2.0",
            "code_intelligence": "✅ V2.0",
            "ai_assistant": "✅ V2.0",
            "result_parser": "✅ V2.0"
        },
        "endpoints": {
            "会话管理": "/api/v2/sessions/*",
            "代码管理": "/api/v2/code/*",
            "代码执行": "/api/v2/execution/*",
            "AI助手": "/api/v2/ai/*"
        }
    }

# ==================== V2 API端点 ====================

@app.post("/api/v2/sessions/create")
async def create_session(session: SessionCreate):
    """创建学习会话"""
    import time
    session_id = f"session_{int(time.time())}"
    
    return {
        "success": True,
        "session_id": session_id,
        "user_id": session.user_id,
        "book_slug": session.book_slug,
        "case_slug": session.case_slug,
        "status": "active",
        "created_at": time.time(),
        "expires_at": time.time() + 3600
    }

@app.get("/api/v2/sessions/{session_id}")
async def get_session(session_id: str):
    """获取会话信息"""
    return {
        "success": True,
        "session_id": session_id,
        "status": "active",
        "user_id": "test_user",
        "book_slug": "water-environment-simulation",
        "case_slug": "case_01_diffusion"
    }

@app.post("/api/v2/code/load")
async def load_code(request: CodeLoad):
    """加载案例代码"""
    return {
        "success": True,
        "book_slug": request.book_slug,
        "case_slug": request.case_slug,
        "files": [
            {
                "path": "main.py",
                "content": "print('Hello from test case!')\nresult = 42\nprint(f'Result: {result}')",
                "language": "python",
                "size": 100
            }
        ],
        "total_files": 1
    }

@app.post("/api/v2/code/validate")
async def validate_code(request: CodeValidate):
    """验证代码"""
    try:
        ast.parse(request.code)
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
            "message": "代码存在语法错误",
            "errors": [
                {
                    "line": e.lineno,
                    "message": str(e.msg),
                    "type": "SyntaxError"
                }
            ]
        }

@app.post("/api/v2/code/analyze")
async def analyze_code(request: CodeValidate):
    """分析代码"""
    try:
        tree = ast.parse(request.code)
        
        # 统计代码元素
        functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        imports = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))
        
        return {
            "success": True,
            "analysis": {
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "lines": len(request.code.split('\n')),
                "complexity": "moderate"
            },
            "suggestions": [
                "代码结构清晰",
                "建议添加文档字符串",
                "考虑添加类型注解"
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/v2/execution/start")
async def start_execution(request: ExecutionStart):
    """启动代码执行"""
    import time
    execution_id = f"exec_{int(time.time())}"
    
    # 模拟执行
    await asyncio.sleep(0.5)
    
    return {
        "success": True,
        "execution_id": execution_id,
        "session_id": request.session_id,
        "status": "completed",
        "output": {
            "stdout": "Hello from test case!\nResult: 42\n",
            "stderr": "",
            "return_code": 0
        },
        "metrics": {
            "execution_time": 0.5,
            "memory_used": "10MB",
            "cpu_time": 0.2
        },
        "results": {
            "L2误差": "1.23e-4",
            "计算时间": "0.5s",
            "精度": "99.5%"
        }
    }

@app.get("/api/v2/execution/{execution_id}")
async def get_execution(execution_id: str):
    """获取执行状态"""
    return {
        "success": True,
        "execution_id": execution_id,
        "status": "completed",
        "output": {
            "stdout": "Execution completed successfully",
            "stderr": "",
            "return_code": 0
        }
    }

@app.post("/api/v2/ai/explain-code")
async def explain_code(request: CodeExplain):
    """AI代码讲解"""
    return {
        "success": True,
        "explanation": f"""
# 代码讲解

这段代码的功能是: {request.context or '执行Python代码'}

## 主要步骤:
1. 导入必要的模块
2. 定义变量和函数
3. 执行计算逻辑
4. 输出结果

## 关键点:
- 代码使用了Python的基本语法
- 逻辑清晰，易于理解
- 适合初学者学习

## 改进建议:
- 可以添加错误处理
- 建议添加注释说明
- 考虑优化性能
        """.strip(),
        "complexity": "simple",
        "estimated_time": "5分钟"
    }

@app.post("/api/v2/ai/diagnose-error")
async def diagnose_error(request: ErrorDiagnose):
    """AI错误诊断"""
    return {
        "success": True,
        "diagnosis": "这是一个常见的Python错误",
        "error_type": "NameError",
        "cause": "变量未定义就被使用",
        "suggestions": [
            "检查变量名拼写是否正确",
            "确保变量在使用前已经定义",
            "查看变量的作用域是否正确"
        ],
        "example_fix": f"""
# 修复前:
{request.code}

# 修复后:
x = 10  # 定义变量
print(x)
        """.strip()
    }

@app.post("/api/v2/ai/ask")
async def ask_question(request: Dict):
    """AI问答"""
    question = request.get("question", "")
    return {
        "success": True,
        "question": question,
        "answer": f"关于 '{question}' 的回答: 这是一个很好的问题。根据上下文分析，建议您参考相关文档和示例代码。",
        "confidence": 0.85,
        "sources": [
            "官方文档",
            "教程案例",
            "最佳实践"
        ]
    }

# ==================== 统计端点 ====================

@app.get("/api/v2/stats")
async def get_stats():
    """获取平台统计信息"""
    return {
        "success": True,
        "stats": {
            "total_sessions": 150,
            "total_executions": 1250,
            "total_users": 45,
            "active_sessions": 8,
            "success_rate": 0.98
        },
        "performance": {
            "avg_response_time": "0.25ms",
            "uptime": "99.95%",
            "cpu_usage": "15%",
            "memory_usage": "127MB"
        }
    }

# ==================== 启动服务器 ====================

if __name__ == "__main__":
    import uvicorn
    print("=" * 80)
    print(" 启动智能知识平台 V2.0 测试服务器")
    print("=" * 80)
    print()
    print(" API文档: http://localhost:8000/docs")
    print(" 健康检查: http://localhost:8000/health")
    print(" 系统信息: http://localhost:8000/info")
    print()
    print("=" * 80)
    
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

