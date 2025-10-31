"""
脚本执行引擎
使用Docker容器安全执行Python脚本
"""

import docker
import asyncio
import json
import uuid
import tempfile
import os
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger


class ScriptExecutionEngine:
    """脚本执行引擎"""
    
    def __init__(
        self,
        docker_image: str = "python:3.11-slim",
        timeout: int = 30,
        max_memory: str = "512m",
        max_cpu: str = "1"
    ):
        """
        初始化执行引擎
        
        Args:
            docker_image: Docker镜像名
            timeout: 超时时间（秒）
            max_memory: 最大内存
            max_cpu: 最大CPU核心数
        """
        try:
            self.client = docker.from_env()
            logger.info("✅ Docker客户端连接成功")
        except Exception as e:
            logger.error(f"❌ Docker客户端连接失败: {e}")
            self.client = None
        
        self.docker_image = docker_image
        self.timeout = timeout
        self.max_memory = max_memory
        self.max_cpu = max_cpu
    
    async def execute_script(
        self,
        script_path: str,
        input_params: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行Python脚本
        
        Args:
            script_path: 脚本文件路径
            input_params: 输入参数
            task_id: 任务ID
            
        Returns:
            执行结果字典
        """
        if task_id is None:
            task_id = str(uuid.uuid4())
        
        logger.info(f"🚀 开始执行脚本: task_id={task_id}")
        logger.info(f"   脚本路径: {script_path}")
        logger.info(f"   输入参数: {input_params}")
        
        result = {
            "task_id": task_id,
            "status": "pending",
            "output_data": None,
            "console_output": "",
            "error_message": None,
            "execution_time": 0.0
        }
        
        try:
            # 检查Docker客户端
            if not self.client:
                raise Exception("Docker客户端未初始化")
            
            # 检查脚本文件是否存在
            script_path_obj = Path(script_path)
            if not script_path_obj.exists():
                raise FileNotFoundError(f"脚本文件不存在: {script_path}")
            
            # 准备执行
            import time
            start_time = time.time()
            
            result["status"] = "running"
            
            # 创建临时目录存放参数
            with tempfile.TemporaryDirectory() as temp_dir:
                # 保存参数到JSON文件
                params_file = os.path.join(temp_dir, "params.json")
                with open(params_file, 'w') as f:
                    json.dump(input_params, f)
                
                # 运行Docker容器
                output = await self._run_in_docker(
                    script_path=str(script_path_obj.absolute()),
                    params_file=params_file,
                    temp_dir=temp_dir
                )
                
                result["console_output"] = output.get("stdout", "")
                result["error_message"] = output.get("stderr", None)
                
                # 检查是否有输出文件
                output_file = os.path.join(temp_dir, "output.json")
                if os.path.exists(output_file):
                    with open(output_file, 'r') as f:
                        result["output_data"] = json.load(f)
            
            # 计算执行时间
            result["execution_time"] = time.time() - start_time
            
            # 判断执行结果
            if output.get("exit_code") == 0:
                result["status"] = "completed"
                logger.info(f"✅ 脚本执行成功: task_id={task_id}, time={result['execution_time']:.2f}s")
            else:
                result["status"] = "failed"
                logger.error(f"❌ 脚本执行失败: task_id={task_id}")
            
        except asyncio.TimeoutError:
            result["status"] = "timeout"
            result["error_message"] = f"执行超时（{self.timeout}秒）"
            logger.error(f"⏱️  脚本执行超时: task_id={task_id}")
            
        except Exception as e:
            result["status"] = "failed"
            result["error_message"] = str(e)
            logger.error(f"❌ 脚本执行异常: task_id={task_id}, error={e}")
        
        return result
    
    async def _run_in_docker(
        self,
        script_path: str,
        params_file: str,
        temp_dir: str
    ) -> Dict[str, Any]:
        """
        在Docker容器中运行脚本
        
        Args:
            script_path: 脚本绝对路径
            params_file: 参数文件路径
            temp_dir: 临时目录
            
        Returns:
            执行结果
        """
        # 挂载卷配置
        volumes = {
            os.path.dirname(script_path): {'bind': '/workspace/script', 'mode': 'ro'},
            temp_dir: {'bind': '/workspace/temp', 'mode': 'rw'}
        }
        
        # 执行命令
        script_name = os.path.basename(script_path)
        command = f"python /workspace/script/{script_name} --params /workspace/temp/params.json --output /workspace/temp/output.json"
        
        # 资源限制
        mem_limit = self.max_memory
        cpu_quota = int(float(self.max_cpu) * 100000)  # 1核心 = 100000
        
        try:
            # 创建容器
            container = self.client.containers.run(
                image=self.docker_image,
                command=f"/bin/bash -c '{command}'",
                volumes=volumes,
                mem_limit=mem_limit,
                cpu_quota=cpu_quota,
                network_disabled=True,  # 禁用网络
                remove=True,  # 自动删除
                detach=True
            )
            
            # 等待容器执行完成
            result = await asyncio.wait_for(
                self._wait_container(container),
                timeout=self.timeout
            )
            
            return result
            
        except docker.errors.DockerException as e:
            logger.error(f"Docker执行错误: {e}")
            return {
                "exit_code": 1,
                "stdout": "",
                "stderr": f"Docker error: {str(e)}"
            }
    
    async def _wait_container(self, container) -> Dict[str, Any]:
        """等待容器执行完成"""
        loop = asyncio.get_event_loop()
        
        # 在线程池中等待
        result = await loop.run_in_executor(None, container.wait)
        
        # 获取日志
        logs = container.logs(stdout=True, stderr=True)
        
        return {
            "exit_code": result['StatusCode'],
            "stdout": logs.decode('utf-8') if isinstance(logs, bytes) else str(logs),
            "stderr": None if result['StatusCode'] == 0 else "执行失败"
        }
    
    def close(self):
        """关闭Docker客户端"""
        if self.client:
            self.client.close()
            logger.info("👋 Docker客户端已关闭")


# 全局执行引擎实例
execution_engine = ScriptExecutionEngine()


# 简化的执行函数（用于无Docker环境）
async def execute_script_simple(
    script_path: str,
    input_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    简化版本的脚本执行（直接运行，无Docker隔离）
    仅用于开发测试
    
    Args:
        script_path: 脚本路径
        input_params: 输入参数
        
    Returns:
        执行结果
    """
    import subprocess
    import json
    import tempfile
    import time
    
    logger.warning("⚠️  使用简化执行模式（无Docker隔离）")
    
    start_time = time.time()
    task_id = str(uuid.uuid4())
    
    result = {
        "task_id": task_id,
        "status": "running",
        "output_data": None,
        "console_output": "",
        "error_message": None,
        "execution_time": 0.0
    }
    
    try:
        # 创建临时参数文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(input_params, f)
            params_file = f.name
        
        # 执行脚本
        process = subprocess.run(
            ["python3", script_path, "--params", params_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        result["console_output"] = process.stdout
        result["error_message"] = process.stderr if process.returncode != 0 else None
        result["execution_time"] = time.time() - start_time
        
        if process.returncode == 0:
            result["status"] = "completed"
            # 模拟输出数据
            result["output_data"] = {
                "message": "执行成功（简化模式）",
                "params": input_params
            }
        else:
            result["status"] = "failed"
        
        # 清理临时文件
        os.unlink(params_file)
        
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error_message"] = "执行超时"
    except Exception as e:
        result["status"] = "failed"
        result["error_message"] = str(e)
    
    return result
