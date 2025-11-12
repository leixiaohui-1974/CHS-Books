"""
增强版代码执行引擎
支持容器池、WebSocket实时通信、依赖管理
"""

import asyncio
import docker
import uuid
import os
import json
import tempfile
import shutil
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
from datetime import datetime
from loguru import logger
from queue import Queue
import time


class ContainerPool:
    """
    容器池管理器
    复用容器以提升性能
    """
    
    def __init__(
        self,
        docker_image: str = "python:3.11-slim",
        pool_size: int = 5,
        max_idle_time: int = 300  # 5分钟
    ):
        """
        初始化容器池
        
        Args:
            docker_image: Docker镜像名
            pool_size: 池大小
            max_idle_time: 最大空闲时间（秒）
        """
        try:
            self.client = docker.from_env()
            logger.info("✅ Docker客户端连接成功")
        except Exception as e:
            logger.error(f"❌ Docker客户端连接失败: {e}")
            self.client = None
        
        self.docker_image = docker_image
        self.pool_size = pool_size
        self.max_idle_time = max_idle_time
        
        self.available_containers: Queue = Queue(maxsize=pool_size)
        self.in_use = {}  # container_id -> timestamp
        
        # 启动预热任务
        asyncio.create_task(self._warm_up_pool())
    
    async def _warm_up_pool(self):
        """预热容器池"""
        if not self.client:
            logger.warning("⚠️  Docker客户端未初始化，跳过容器池预热")
            return
        
        logger.info(f"🔥 开始预热容器池 (大小: {self.pool_size})...")
        
        for i in range(self.pool_size):
            try:
                container = await self._create_container(f"pool_{i}")
                self.available_containers.put(container)
                logger.info(f"  ✓ 容器 {i+1}/{self.pool_size} 就绪")
            except Exception as e:
                logger.error(f"  ✗ 创建容器失败: {e}")
        
        logger.info("✅ 容器池预热完成")
    
    async def _create_container(self, name_suffix: str):
        """创建新容器"""
        if not self.client:
            raise Exception("Docker客户端未初始化")
        
        container_name = f"exec_container_{name_suffix}_{uuid.uuid4().hex[:8]}"
        
        # 在线程池中执行Docker操作（同步转异步）
        loop = asyncio.get_event_loop()
        container = await loop.run_in_executor(
            None,
            lambda: self.client.containers.create(
                image=self.docker_image,
                name=container_name,
                command="tail -f /dev/null",  # 保持运行
                detach=True,
                mem_limit="1g",
                cpu_quota=200000,  # 2核
                network_mode="none",
                remove=False
            )
        )
        
        # 启动容器
        await loop.run_in_executor(None, container.start)
        
        return container
    
    async def acquire(self, timeout: float = 30.0):
        """
        获取容器
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            容器对象
        """
        start_time = time.time()
        
        # 尝试从池中获取
        while time.time() - start_time < timeout:
            try:
                container = self.available_containers.get_nowait()
                
                # 检查容器是否还活着
                loop = asyncio.get_event_loop()
                try:
                    await loop.run_in_executor(None, container.reload)
                    if container.status == "running":
                        self.in_use[container.id] = time.time()
                        logger.debug(f"📦 从池中获取容器: {container.id[:12]}")
                        return container
                except:
                    # 容器已失效，创建新的
                    pass
            except:
                pass
            
            await asyncio.sleep(0.1)
        
        # 超时，创建临时容器
        logger.warning("⚠️  容器池已满，创建临时容器")
        container = await self._create_container(f"temp_{uuid.uuid4().hex[:8]}")
        self.in_use[container.id] = time.time()
        return container
    
    async def release(self, container):
        """
        释放容器
        
        Args:
            container: 容器对象
        """
        if container.id in self.in_use:
            del self.in_use[container.id]
        
        try:
            # 清理容器
            await self._cleanup_container(container)
            
            # 放回池中
            if self.available_containers.qsize() < self.pool_size:
                self.available_containers.put(container)
                logger.debug(f"📦 释放容器到池: {container.id[:12]}")
            else:
                # 池已满，销毁容器
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: container.remove(force=True))
                logger.debug(f"🗑️  销毁多余容器: {container.id[:12]}")
        except Exception as e:
            logger.error(f"❌ 释放容器失败: {e}")
    
    async def _cleanup_container(self, container):
        """清理容器状态"""
        loop = asyncio.get_event_loop()
        
        try:
            # 停止所有进程
            await loop.run_in_executor(
                None,
                lambda: container.exec_run("pkill -9 python", detach=False)
            )
            
            # 清理临时文件
            await loop.run_in_executor(
                None,
                lambda: container.exec_run("rm -rf /workspace/* /tmp/*", detach=False)
            )
        except Exception as e:
            logger.warning(f"⚠️  清理容器时出错: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """获取容器池统计信息"""
        return {
            "available": self.available_containers.qsize(),
            "in_use": len(self.in_use),
            "total": self.pool_size
        }


class EnhancedExecutionEngine:
    """
    增强版执行引擎
    """
    
    def __init__(
        self,
        docker_image: str = "python:3.11-slim",
        timeout: int = 300,
        max_memory: str = "1g",
        pool_size: int = 5
    ):
        """
        初始化执行引擎
        
        Args:
            docker_image: Docker镜像
            timeout: 超时时间（秒）
            max_memory: 最大内存
            pool_size: 容器池大小
        """
        self.docker_image = docker_image
        self.timeout = timeout
        self.max_memory = max_memory
        
        # 创建容器池
        self.container_pool = ContainerPool(
            docker_image=docker_image,
            pool_size=pool_size
        )
        
        # WebSocket回调
        self.ws_callbacks: Dict[str, Callable] = {}
    
    def register_ws_callback(self, execution_id: str, callback: Callable):
        """
        注册WebSocket回调函数
        
        Args:
            execution_id: 执行ID
            callback: 回调函数
        """
        self.ws_callbacks[execution_id] = callback
    
    def unregister_ws_callback(self, execution_id: str):
        """注销WebSocket回调"""
        if execution_id in self.ws_callbacks:
            del self.ws_callbacks[execution_id]
    
    async def _send_ws_message(self, execution_id: str, message_type: str, data: Any):
        """发送WebSocket消息"""
        if execution_id in self.ws_callbacks:
            try:
                callback = self.ws_callbacks[execution_id]
                await callback({
                    "type": message_type,
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.error(f"❌ WebSocket消息发送失败: {e}")
    
    async def execute_script(
        self,
        execution_id: str,
        script_path: str,
        input_params: Dict[str, Any],
        code_files: Optional[Dict[str, str]] = None,
        dependencies: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        执行Python脚本
        
        Args:
            execution_id: 执行ID
            script_path: 脚本文件路径
            input_params: 输入参数
            code_files: 修改的代码文件 {path: content}
            dependencies: 依赖列表
            
        Returns:
            执行结果字典
        """
        logger.info(f"🚀 开始执行: {execution_id}")
        logger.info(f"   脚本: {script_path}")
        logger.info(f"   参数: {input_params}")
        
        result = {
            "execution_id": execution_id,
            "status": "pending",
            "output_data": None,
            "console_output": "",
            "error_message": None,
            "execution_time": 0.0,
            "result_files": []
        }
        
        container = None
        temp_dir = None
        
        try:
            # 发送开始消息
            await self._send_ws_message(execution_id, "status", {"status": "starting"})
            
            # 1. 准备工作目录
            temp_dir = tempfile.mkdtemp(prefix=f"exec_{execution_id}_")
            workspace_dir = Path(temp_dir) / "workspace"
            workspace_dir.mkdir()
            
            # 2. 复制脚本和相关文件
            await self._prepare_workspace(
                workspace_dir,
                script_path,
                code_files
            )
            
            # 3. 保存参数
            params_file = workspace_dir / "params.json"
            with open(params_file, 'w') as f:
                json.dump(input_params, f)
            
            # 4. 获取容器
            container = await self.container_pool.acquire(timeout=30.0)
            
            # 5. 安装依赖（如果需要）
            if dependencies:
                await self._send_ws_message(execution_id, "status", {"status": "installing_dependencies"})
                await self._install_dependencies(container, dependencies)
            
            # 6. 执行脚本
            await self._send_ws_message(execution_id, "status", {"status": "running"})
            
            start_time = time.time()
            
            execution_result = await self._run_in_container(
                container=container,
                workspace_dir=workspace_dir,
                script_path=script_path,
                execution_id=execution_id
            )
            
            execution_time = time.time() - start_time
            
            # 7. 处理结果
            result["execution_time"] = execution_time
            result["console_output"] = execution_result.get("stdout", "")
            result["error_message"] = execution_result.get("stderr", "")
            
            if execution_result.get("exit_code") == 0:
                result["status"] = "completed"
                
                # 收集结果文件
                result["result_files"] = await self._collect_result_files(workspace_dir)
                
                # 发送完成消息
                await self._send_ws_message(execution_id, "completed", {
                    "execution_time": execution_time,
                    "result_files": result["result_files"]
                })
                
                logger.info(f"✅ 执行成功: {execution_id} ({execution_time:.2f}s)")
            else:
                result["status"] = "failed"
                await self._send_ws_message(execution_id, "failed", {
                    "error": result["error_message"]
                })
                logger.error(f"❌ 执行失败: {execution_id}")
        
        except asyncio.TimeoutError:
            result["status"] = "timeout"
            result["error_message"] = f"执行超时（{self.timeout}秒）"
            await self._send_ws_message(execution_id, "timeout", {})
            logger.error(f"⏱️  执行超时: {execution_id}")
        
        except Exception as e:
            result["status"] = "failed"
            result["error_message"] = str(e)
            await self._send_ws_message(execution_id, "error", {"error": str(e)})
            logger.error(f"❌ 执行异常: {execution_id}, {e}")
        
        finally:
            # 清理资源
            if container:
                await self.container_pool.release(container)
            
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            # 注销回调
            self.unregister_ws_callback(execution_id)
        
        return result
    
    async def _prepare_workspace(
        self,
        workspace_dir: Path,
        script_path: str,
        code_files: Optional[Dict[str, str]] = None
    ):
        """准备工作空间"""
        # 复制脚本目录结构
        script_path_obj = Path(script_path)
        
        if script_path_obj.exists():
            # 复制案例目录
            case_dir = script_path_obj.parent
            target_dir = workspace_dir / "code"
            
            shutil.copytree(case_dir, target_dir, dirs_exist_ok=True)
            
            # 应用用户修改的文件
            if code_files:
                for file_path, content in code_files.items():
                    target_file = target_dir / file_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    target_file.write_text(content)
    
    async def _install_dependencies(self, container, dependencies: list):
        """安装依赖"""
        if not dependencies:
            return
        
        # 创建requirements.txt
        requirements = "\n".join(dependencies)
        
        loop = asyncio.get_event_loop()
        
        # 写入requirements.txt
        exec_result = await loop.run_in_executor(
            None,
            lambda: container.exec_run(
                f"bash -c 'echo \"{requirements}\" > /tmp/requirements.txt'",
                workdir="/workspace"
            )
        )
        
        # 安装依赖
        exec_result = await loop.run_in_executor(
            None,
            lambda: container.exec_run(
                "pip install -r /tmp/requirements.txt --quiet",
                workdir="/workspace"
            )
        )
        
        logger.info(f"✅ 依赖安装完成")
    
    async def _run_in_container(
        self,
        container,
        workspace_dir: Path,
        script_path: str,
        execution_id: str
    ) -> Dict[str, Any]:
        """在容器中运行脚本"""
        loop = asyncio.get_event_loop()
        
        # 挂载工作目录（Docker API方式）
        # 注意：这里需要先复制文件到容器
        
        # 复制工作目录到容器
        import tarfile
        import io
        
        # 创建tar文件
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            tar.add(workspace_dir, arcname='workspace')
        tar_stream.seek(0)
        
        # 上传到容器
        await loop.run_in_executor(
            None,
            lambda: container.put_archive('/', tar_stream.read())
        )
        
        # 执行命令
        script_name = Path(script_path).name
        command = f"cd /workspace/code && python {script_name}"
        
        # 执行
        exec_result = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: container.exec_run(
                    command,
                    workdir="/workspace/code",
                    stream=True,
                    demux=True
                )
            ),
            timeout=self.timeout
        )
        
        # 收集输出
        stdout_lines = []
        stderr_lines = []
        
        for stdout, stderr in exec_result.output:
            if stdout:
                line = stdout.decode('utf-8')
                stdout_lines.append(line)
                # 实时发送输出
                await self._send_ws_message(execution_id, "output", {"text": line})
            
            if stderr:
                line = stderr.decode('utf-8')
                stderr_lines.append(line)
                await self._send_ws_message(execution_id, "error_output", {"text": line})
        
        return {
            "exit_code": exec_result.exit_code,
            "stdout": "".join(stdout_lines),
            "stderr": "".join(stderr_lines) if stderr_lines else None
        }
    
    async def _collect_result_files(self, workspace_dir: Path) -> List[Dict]:
        """收集结果文件"""
        result_files = []
        
        # 扫描输出目录
        output_patterns = [
            "*.png", "*.jpg", "*.svg",  # 图片
            "*.csv", "*.xlsx",  # 表格
            "*.json",  # 数据
            "*.md", "*.txt",  # 报告
            "*.mp4", "*.gif"  # 动画
        ]
        
        for pattern in output_patterns:
            for file_path in workspace_dir.rglob(pattern):
                if file_path.is_file():
                    file_info = {
                        "type": self._detect_file_type(file_path),
                        "name": file_path.name,
                        "path": str(file_path.relative_to(workspace_dir)),
                        "size": file_path.stat().st_size
                    }
                    result_files.append(file_info)
        
        return result_files
    
    def _detect_file_type(self, file_path: Path) -> str:
        """检测文件类型"""
        ext = file_path.suffix.lower()
        
        type_map = {
            '.png': 'plot', '.jpg': 'plot', '.svg': 'plot',
            '.csv': 'table', '.xlsx': 'table',
            '.json': 'data',
            '.md': 'report', '.txt': 'report',
            '.mp4': 'video', '.gif': 'animation'
        }
        
        return type_map.get(ext, 'unknown')
    
    def get_pool_stats(self) -> Dict[str, int]:
        """获取容器池统计"""
        return self.container_pool.get_stats()


# 全局执行引擎实例
enhanced_execution_engine = EnhancedExecutionEngine(
    docker_image="python:3.11-slim",
    timeout=300,
    max_memory="1g",
    pool_size=5
)
