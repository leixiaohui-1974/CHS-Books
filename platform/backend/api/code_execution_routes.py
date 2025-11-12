"""
代码在线执行API
提供安全的Python代码执行环境
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import subprocess
import sys
import os
import tempfile
import time
import json
from pathlib import Path
import traceback

router = APIRouter(prefix="/api/code", tags=["Code Execution"])

# 配置
MAX_EXECUTION_TIME = 30  # 最大执行时间（秒）
MAX_OUTPUT_SIZE = 10 * 1024 * 1024  # 最大输出大小（10MB）

class CodeExecutionRequest(BaseModel):
    """代码执行请求"""
    code: str = Field(..., description="要执行的Python代码")
    input_data: Optional[str] = Field(None, description="标准输入数据")
    timeout: Optional[int] = Field(30, description="超时时间（秒）", ge=1, le=60)
    save_plots: Optional[bool] = Field(True, description="是否保存matplotlib图表")
    case_id: Optional[str] = Field(None, description="关联的案例ID")

class CodeExecutionResponse(BaseModel):
    """代码执行响应"""
    success: bool
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    error: Optional[str] = None
    execution_time: float
    plots: Optional[List[str]] = None  # 生成的图表文件路径
    files: Optional[List[str]] = None  # 生成的其他文件

@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """
    执行Python代码
    
    安全措施：
    - 在临时目录中执行
    - 限制执行时间
    - 限制输出大小
    - 捕获所有异常
    """
    start_time = time.time()
    
    # 创建临时工作目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 保存代码到临时文件
        code_file = temp_path / "user_code.py"
        
        # 添加图表保存的包装代码
        wrapped_code = request.code
        if request.save_plots and 'matplotlib' in request.code:
            wrapped_code = """
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import os

# 设置图表保存目录
_plot_dir = os.getcwd()
_plot_counter = [0]

# 重写plt.show()来保存图表
_original_show = plt.show
def _custom_show(*args, **kwargs):
    _plot_counter[0] += 1
    filename = f'plot_{_plot_counter[0]}.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f'[PLOT_SAVED] {filename}')
    plt.close()
plt.show = _custom_show

""" + request.code
        
        try:
            code_file.write_text(wrapped_code, encoding='utf-8')
        except Exception as e:
            return CodeExecutionResponse(
                success=False,
                error=f"写入代码文件失败: {str(e)}",
                execution_time=time.time() - start_time
            )
        
        # 准备执行环境
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # 执行代码
        try:
            process = subprocess.Popen(
                [sys.executable, str(code_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE if request.input_data else None,
                cwd=str(temp_path),
                env=env,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # 设置超时
            timeout = min(request.timeout or MAX_EXECUTION_TIME, MAX_EXECUTION_TIME)
            
            try:
                stdout, stderr = process.communicate(
                    input=request.input_data,
                    timeout=timeout
                )
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return CodeExecutionResponse(
                    success=False,
                    stdout=stdout[:1000] if stdout else None,
                    stderr=stderr[:1000] if stderr else None,
                    error=f"执行超时（超过{timeout}秒）",
                    execution_time=time.time() - start_time
                )
            
            # 检查返回码
            success = process.returncode == 0
            
            # 限制输出大小
            if stdout and len(stdout) > MAX_OUTPUT_SIZE:
                stdout = stdout[:MAX_OUTPUT_SIZE] + "\n...[输出过长，已截断]"
            if stderr and len(stderr) > MAX_OUTPUT_SIZE:
                stderr = stderr[:MAX_OUTPUT_SIZE] + "\n...[输出过长，已截断]"
            
            # 查找生成的图表文件
            plots = []
            files = []
            for file in temp_path.iterdir():
                if file.is_file() and file.name != "user_code.py":
                    if file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.svg']:
                        plots.append(file.name)
                    else:
                        files.append(file.name)
            
            # 如果需要保存图表，复制到永久目录
            saved_plots = []
            if plots and request.save_plots:
                # 保存到backend/outputs目录
                output_dir = Path(__file__).parent.parent / "outputs" / "plots"
                output_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = int(time.time())
                for plot in plots:
                    src = temp_path / plot
                    dst = output_dir / f"{timestamp}_{plot}"
                    try:
                        import shutil
                        shutil.copy2(src, dst)
                        saved_plots.append(f"/api/code/plot/{dst.name}")
                    except Exception as e:
                        print(f"保存图表失败: {e}")
            
            execution_time = time.time() - start_time
            
            return CodeExecutionResponse(
                success=success,
                stdout=stdout,
                stderr=stderr if stderr else None,
                error=None if success else "程序执行出错，请查看stderr",
                execution_time=execution_time,
                plots=saved_plots if saved_plots else None,
                files=files if files else None
            )
            
        except Exception as e:
            return CodeExecutionResponse(
                success=False,
                error=f"执行异常: {str(e)}\n{traceback.format_exc()}",
                execution_time=time.time() - start_time
            )

@router.get("/plot/{filename}")
async def get_plot(filename: str):
    """
    获取生成的图表
    """
    from fastapi.responses import FileResponse
    
    output_dir = Path(__file__).parent.parent / "outputs" / "plots"
    file_path = output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="图表文件不存在")
    
    # 安全检查：确保文件在正确的目录下
    if not str(file_path.resolve()).startswith(str(output_dir.resolve())):
        raise HTTPException(status_code=403, detail="非法访问")
    
    return FileResponse(
        file_path,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=3600"}
    )

@router.post("/validate")
async def validate_code(code: str):
    """
    验证Python代码语法
    """
    try:
        compile(code, '<string>', 'exec')
        return {
            "success": True,
            "valid": True,
            "message": "代码语法正确"
        }
    except SyntaxError as e:
        return {
            "success": True,
            "valid": False,
            "error": {
                "type": "SyntaxError",
                "message": str(e),
                "line": e.lineno,
                "offset": e.offset,
                "text": e.text
            }
        }
    except Exception as e:
        return {
            "success": True,
            "valid": False,
            "error": {
                "type": type(e).__name__,
                "message": str(e)
            }
        }

@router.get("/stats")
async def get_execution_stats():
    """
    获取代码执行统计信息
    """
    output_dir = Path(__file__).parent.parent / "outputs" / "plots"
    
    stats = {
        "plots_directory": str(output_dir),
        "total_plots": 0,
        "total_size_mb": 0.0
    }
    
    if output_dir.exists():
        plots = list(output_dir.glob("*.png"))
        stats["total_plots"] = len(plots)
        stats["total_size_mb"] = sum(p.stat().st_size for p in plots) / (1024 * 1024)
    
    return {
        "success": True,
        **stats
    }

@router.delete("/cleanup")
async def cleanup_old_plots(keep_recent: int = 50):
    """
    清理旧的图表文件
    """
    output_dir = Path(__file__).parent.parent / "outputs" / "plots"
    
    if not output_dir.exists():
        return {
            "success": True,
            "deleted": 0,
            "message": "输出目录不存在"
        }
    
    # 按修改时间排序
    plots = sorted(output_dir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    # 删除旧文件
    deleted = 0
    for plot in plots[keep_recent:]:
        try:
            plot.unlink()
            deleted += 1
        except Exception as e:
            print(f"删除文件失败 {plot}: {e}")
    
    return {
        "success": True,
        "deleted": deleted,
        "remaining": len(plots) - deleted
    }

# 代码模板
CODE_TEMPLATES = {
    "hello_world": {
        "name": "Hello World",
        "description": "简单的打印示例",
        "code": """print("Hello, World!")
print("欢迎使用CHS-Books代码执行环境！")"""
    },
    "matplotlib_basic": {
        "name": "基础绘图",
        "description": "使用matplotlib绘制简单图表",
        "code": """import matplotlib.pyplot as plt
import numpy as np

# 生成数据
x = np.linspace(0, 10, 100)
y = np.sin(x)

# 绘制图表
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.xlabel('x')
plt.ylabel('y')
plt.title('正弦函数')
plt.legend()
plt.grid(True)
plt.show()

print("图表已生成！")"""
    },
    "control_system": {
        "name": "控制系统仿真",
        "description": "简单的PID控制器示例",
        "code": """import numpy as np
import matplotlib.pyplot as plt

# PID参数
Kp, Ki, Kd = 1.0, 0.5, 0.1

# 仿真参数
dt = 0.01
t = np.arange(0, 10, dt)
setpoint = 1.0

# 初始化
y = np.zeros_like(t)
error_sum = 0
error_prev = 0

# 仿真循环
for i in range(1, len(t)):
    error = setpoint - y[i-1]
    error_sum += error * dt
    error_diff = (error - error_prev) / dt
    
    u = Kp * error + Ki * error_sum + Kd * error_diff
    y[i] = y[i-1] + u * dt
    error_prev = error

# 绘图
plt.figure(figsize=(10, 6))
plt.plot(t, y, 'b-', linewidth=2, label='系统响应')
plt.axhline(y=setpoint, color='r', linestyle='--', label='目标值')
plt.xlabel('时间 (s)')
plt.ylabel('输出')
plt.title('PID控制器响应')
plt.legend()
plt.grid(True)
plt.show()

print(f"稳态误差: {abs(setpoint - y[-1]):.4f}")"""
    },
    "data_analysis": {
        "name": "数据分析",
        "description": "简单的数据分析示例",
        "code": """import numpy as np
import matplotlib.pyplot as plt

# 生成随机数据
np.random.seed(42)
data = np.random.randn(1000)

# 统计分析
mean = np.mean(data)
std = np.std(data)
median = np.median(data)

print(f"均值: {mean:.4f}")
print(f"标准差: {std:.4f}")
print(f"中位数: {median:.4f}")

# 绘制直方图
plt.figure(figsize=(10, 6))
plt.hist(data, bins=50, density=True, alpha=0.7, color='blue', edgecolor='black')
plt.axvline(mean, color='red', linestyle='--', linewidth=2, label=f'均值: {mean:.2f}')
plt.xlabel('值')
plt.ylabel('频率')
plt.title('数据分布直方图')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()"""
    }
}

@router.get("/templates")
async def get_code_templates():
    """
    获取代码模板列表
    """
    return {
        "success": True,
        "templates": CODE_TEMPLATES
    }

@router.get("/template/{template_id}")
async def get_code_template(template_id: str):
    """
    获取特定代码模板
    """
    if template_id not in CODE_TEMPLATES:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    return {
        "success": True,
        "template": CODE_TEMPLATES[template_id]
    }

