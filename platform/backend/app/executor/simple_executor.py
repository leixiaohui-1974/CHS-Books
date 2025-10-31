"""
简化的工具执行引擎
不依赖Docker，直接在Python环境中执行
"""

import asyncio
import json
import sys
from typing import Dict, Any, Optional
from pathlib import Path
import traceback
from datetime import datetime
from loguru import logger


class SimpleExecutor:
    """简化的执行引擎"""
    
    def __init__(self, workspace_root: str = "/workspace"):
        """
        初始化执行引擎
        
        Args:
            workspace_root: 工作空间根目录
        """
        self.workspace_root = Path(workspace_root)
        self.books_root = self.workspace_root / "books"
    
    async def execute_script(
        self,
        book_slug: str,
        case_slug: str,
        input_params: Dict[str, Any],
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        执行脚本
        
        Args:
            book_slug: 书籍slug
            case_slug: 案例slug
            input_params: 输入参数
            timeout: 超时时间（秒）
            
        Returns:
            执行结果
        """
        start_time = datetime.now()
        
        try:
            # 查找脚本文件
            script_path = self._find_script(book_slug, case_slug)
            if not script_path:
                return {
                    "status": "error",
                    "error": f"未找到脚本: {book_slug}/{case_slug}",
                    "execution_time": 0
                }
            
            logger.info(f"🚀 执行脚本: {script_path}")
            logger.info(f"📥 输入参数: {input_params}")
            
            # 执行脚本
            result = await self._run_script(script_path, input_params, timeout)
            
            # 计算执行时间
            execution_time = (datetime.now() - start_time).total_seconds()
            result["execution_time"] = round(execution_time, 3)
            
            logger.info(f"✅ 脚本执行成功，耗时: {execution_time:.3f}秒")
            
            return result
            
        except asyncio.TimeoutError:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ 脚本执行超时: {timeout}秒")
            return {
                "status": "error",
                "error": f"执行超时（{timeout}秒）",
                "execution_time": round(execution_time, 3)
            }
        
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ 脚本执行失败: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "execution_time": round(execution_time, 3)
            }
    
    def _find_script(self, book_slug: str, case_slug: str) -> Optional[Path]:
        """
        查找脚本文件
        
        Args:
            book_slug: 书籍slug
            case_slug: 案例slug
            
        Returns:
            脚本路径，如果不存在返回None
        """
        # 可能的路径
        possible_paths = [
            self.books_root / book_slug / "code" / "examples" / case_slug / "main.py",
            self.books_root / book_slug / "code" / "examples" / f"{case_slug}.py",
            self.books_root / book_slug / "examples" / case_slug / "main.py",
            self.books_root / book_slug / "examples" / f"{case_slug}.py",
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    async def _run_script(
        self,
        script_path: Path,
        input_params: Dict[str, Any],
        timeout: int
    ) -> Dict[str, Any]:
        """
        运行Python脚本
        
        Args:
            script_path: 脚本路径
            input_params: 输入参数
            timeout: 超时时间
            
        Returns:
            执行结果
        """
        # 读取脚本内容
        script_content = script_path.read_text(encoding='utf-8')
        
        # 准备执行环境
        exec_globals = {
            '__name__': '__main__',
            '__file__': str(script_path),
            'params': input_params
        }
        
        # 执行脚本
        try:
            exec(script_content, exec_globals)
            
            # 尝试调用main函数（如果存在）
            if 'main' in exec_globals and callable(exec_globals['main']):
                result = exec_globals['main'](input_params)
                
                # 如果返回协程，则await
                if asyncio.iscoroutine(result):
                    result = await asyncio.wait_for(result, timeout=timeout)
                
                return {
                    "status": "success",
                    "result": result
                }
            else:
                # 没有main函数，返回全局变量中的result
                if 'result' in exec_globals:
                    return {
                        "status": "success",
                        "result": exec_globals['result']
                    }
                else:
                    return {
                        "status": "success",
                        "result": {"message": "脚本执行成功，但未返回结果"}
                    }
        
        except Exception as e:
            raise
    
    def get_script_info(self, book_slug: str, case_slug: str) -> Optional[Dict[str, Any]]:
        """
        获取脚本信息
        
        Args:
            book_slug: 书籍slug
            case_slug: 案例slug
            
        Returns:
            脚本信息
        """
        script_path = self._find_script(book_slug, case_slug)
        if not script_path:
            return None
        
        return {
            "path": str(script_path),
            "exists": script_path.exists(),
            "size": script_path.stat().st_size if script_path.exists() else 0
        }


# 全局执行器实例
simple_executor = SimpleExecutor()


# 测试函数
async def test_executor():
    """测试执行器"""
    executor = SimpleExecutor()
    
    # 测试参数
    test_params = {
        "tank_capacity": 10,
        "inflow_rate": 5,
        "outflow_rate": 3,
        "high_level": 80,
        "low_level": 30,
        "simulation_time": 24
    }
    
    # 执行
    result = await executor.execute_script(
        book_slug="water-system-control",
        case_slug="case-1",
        input_params=test_params
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(test_executor())
