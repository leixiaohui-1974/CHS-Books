# coding: utf-8
"""
代码执行API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import tempfile
import os

router = APIRouter(prefix="/api/execute", tags=["code-execution"])

class CodeExecutionRequest(BaseModel):
    code: str
    language: str = "python"

@router.post("/python")
async def execute_python(request: dict):
    """执行Python代码"""
    try:
        code = request.get('code', '')
        
        if not code:
            return {"output": "", "error": "代码为空"}
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # 执行代码
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = result.stdout
            error = result.stderr
            
            if error:
                return {"output": output, "error": error}
            else:
                return {"output": output or "执行完成,无输出"}
                
        finally:
            # 删除临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
    except subprocess.TimeoutExpired:
        return {"output": "", "error": "执行超时(>10秒)"}
    except Exception as e:
        return {"output": "", "error": f"执行失败: {str(e)}"}

