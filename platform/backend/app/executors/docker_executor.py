"""
Docker工具执行器
在隔离的Docker容器中执行Python脚本，提供更好的安全性
"""

import asyncio
import os
import tempfile
import json
from typing import Dict, Any, Optional
from pathlib import Path
import docker
from docker.errors import DockerException, ContainerError, ImageNotFound
from loguru import logger


class DockerExecutor:
    """Docker执行器"""
    
    def __init__(self):
        """初始化Docker执行器"""
        try:
            self.client = docker.from_env()
            self.image_name = "python:3.11-slim"
            self.enabled = True
            logger.info("✅ Docker executor initialized")
        except DockerException as e:
            logger.warning(f"⚠️  Docker not available: {e}")
            self.enabled = False
    
    async def execute(
        self,
        script_path: str,
        input_params: Dict[str, Any],
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        在Docker容器中执行脚本
        
        Args:
            script_path: 脚本文件路径
            input_params: 输入参数
            timeout: 超时时间（秒）
        
        Returns:
            执行结果字典
        """
        if not self.enabled:
            return {
                "status": "error",
                "output": None,
                "logs": "Docker executor not available",
                "error": "Docker service is not running"
            }
        
        # 确保镜像存在
        await self._ensure_image()
        
        # 创建临时目录用于存放脚本和参数
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 复制脚本到临时目录
            script_name = Path(script_path).name
            temp_script = temp_path / script_name
            
            with open(script_path, 'r') as f:
                script_content = f.read()
            
            with open(temp_script, 'w') as f:
                f.write(script_content)
            
            # 保存输入参数为JSON
            params_file = temp_path / "input_params.json"
            with open(params_file, 'w') as f:
                json.dump(input_params, f)
            
            # 创建执行脚本
            runner_script = temp_path / "runner.py"
            with open(runner_script, 'w') as f:
                f.write(self._generate_runner_script(script_name))
            
            try:
                # 运行容器
                result = await asyncio.to_thread(
                    self._run_container,
                    temp_dir,
                    timeout
                )
                
                return result
                
            except Exception as e:
                logger.error(f"Docker execution error: {e}")
                return {
                    "status": "error",
                    "output": None,
                    "logs": f"Execution failed: {str(e)}",
                    "error": str(e)
                }
    
    def _generate_runner_script(self, script_name: str) -> str:
        """生成容器内的执行脚本"""
        return f'''
import json
import sys
import traceback
from pathlib import Path

# 读取输入参数
with open('/workspace/input_params.json', 'r') as f:
    params = json.load(f)

# 导入用户脚本
sys.path.insert(0, '/workspace')
import {Path(script_name).stem} as user_script

# 执行脚本
try:
    # 查找main函数或run函数
    if hasattr(user_script, 'main'):
        result = user_script.main(**params)
    elif hasattr(user_script, 'run'):
        result = user_script.run(**params)
    elif hasattr(user_script, 'execute'):
        result = user_script.execute(**params)
    else:
        raise AttributeError("Script must have main(), run(), or execute() function")
    
    # 输出结果
    output = {{
        "status": "success",
        "output": result,
        "logs": "Execution completed successfully"
    }}
    
    with open('/workspace/output.json', 'w') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("EXECUTION_SUCCESS")
    
except Exception as e:
    error_output = {{
        "status": "error",
        "output": None,
        "logs": traceback.format_exc(),
        "error": str(e)
    }}
    
    with open('/workspace/output.json', 'w') as f:
        json.dump(error_output, f, ensure_ascii=False, indent=2)
    
    print("EXECUTION_ERROR")
    sys.exit(1)
'''
    
    def _run_container(self, workspace_dir: str, timeout: int) -> Dict[str, Any]:
        """在容器中运行脚本"""
        try:
            # 容器配置
            container = self.client.containers.run(
                image=self.image_name,
                command="python /workspace/runner.py",
                volumes={
                    workspace_dir: {'bind': '/workspace', 'mode': 'rw'}
                },
                working_dir="/workspace",
                detach=True,
                mem_limit="512m",
                cpu_quota=50000,  # 50% CPU
                network_disabled=True,  # 禁用网络访问
                security_opt=["no-new-privileges"],
                cap_drop=["ALL"],
                read_only=False
            )
            
            # 等待容器执行完成
            result = container.wait(timeout=timeout)
            
            # 获取日志
            logs = container.logs().decode('utf-8', errors='ignore')
            
            # 读取输出
            output_file = Path(workspace_dir) / "output.json"
            if output_file.exists():
                with open(output_file, 'r') as f:
                    output = json.load(f)
            else:
                output = {
                    "status": "error",
                    "output": None,
                    "logs": logs,
                    "error": "No output file generated"
                }
            
            # 清理容器
            container.remove()
            
            return output
            
        except ContainerError as e:
            return {
                "status": "error",
                "output": None,
                "logs": str(e),
                "error": f"Container error: {e.stderr.decode('utf-8', errors='ignore')}"
            }
        
        except asyncio.TimeoutError:
            return {
                "status": "error",
                "output": None,
                "logs": "Execution timeout",
                "error": f"Script execution exceeded {timeout} seconds"
            }
    
    async def _ensure_image(self):
        """确保Docker镜像存在"""
        try:
            self.client.images.get(self.image_name)
        except ImageNotFound:
            logger.info(f"Pulling Docker image: {self.image_name}")
            await asyncio.to_thread(
                self.client.images.pull,
                self.image_name
            )
            logger.info(f"✅ Image pulled: {self.image_name}")
    
    def is_available(self) -> bool:
        """检查Docker是否可用"""
        return self.enabled and self.client.ping()


# 全局实例
docker_executor = DockerExecutor()


# 便捷函数
async def execute_in_docker(
    script_path: str,
    input_params: Dict[str, Any],
    timeout: int = 60
) -> Dict[str, Any]:
    """在Docker中执行脚本"""
    return await docker_executor.execute(script_path, input_params, timeout)


def is_docker_available() -> bool:
    """检查Docker是否可用"""
    return docker_executor.is_available()
