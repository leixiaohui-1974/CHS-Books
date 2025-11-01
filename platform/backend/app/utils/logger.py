"""
完整的日志系统
支持结构化日志、多级别、多输出
"""

import sys
import os
from pathlib import Path
from loguru import logger
from datetime import datetime


class LoggerSetup:
    """日志配置类"""
    
    @staticmethod
    def setup_logger(
        log_level: str = "INFO",
        log_dir: str = "logs",
        rotation: str = "100 MB",
        retention: str = "30 days",
        json_format: bool = False
    ):
        """
        配置日志系统
        
        Args:
            log_level: 日志级别
            log_dir: 日志目录
            rotation: 日志轮转大小
            retention: 日志保留时间
            json_format: 是否使用JSON格式
        """
        # 创建日志目录
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True, parents=True)
        
        # 移除默认handler
        logger.remove()
        
        # 控制台输出（彩色）
        logger.add(
            sys.stdout,
            level=log_level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # 通用日志文件
        if json_format:
            # JSON格式（生产环境）
            logger.add(
                log_path / "app_{time:YYYY-MM-DD}.json",
                level=log_level,
                rotation=rotation,
                retention=retention,
                compression="zip",
                serialize=True,  # JSON格式
                backtrace=True,
                diagnose=False
            )
        else:
            # 文本格式（开发环境）
            logger.add(
                log_path / "app_{time:YYYY-MM-DD}.log",
                level=log_level,
                rotation=rotation,
                retention=retention,
                compression="zip",
                format=(
                    "{time:YYYY-MM-DD HH:mm:ss} | "
                    "{level: <8} | "
                    "{name}:{function}:{line} | "
                    "{message}"
                ),
                backtrace=True,
                diagnose=True
            )
        
        # 错误日志单独文件
        logger.add(
            log_path / "error_{time:YYYY-MM-DD}.log",
            level="ERROR",
            rotation=rotation,
            retention=retention,
            compression="zip",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | "
                "{level: <8} | "
                "{name}:{function}:{line} | "
                "{message}\n{exception}"
            ),
            backtrace=True,
            diagnose=True
        )
        
        # API访问日志
        logger.add(
            log_path / "access_{time:YYYY-MM-DD}.log",
            level="INFO",
            rotation=rotation,
            retention=retention,
            compression="zip",
            filter=lambda record: "api_access" in record["extra"],
            format="{time:YYYY-MM-DD HH:mm:ss} | {extra[method]} {extra[path]} | {extra[status]} | {extra[duration]}ms"
        )
        
        # 数据库查询日志
        logger.add(
            log_path / "database_{time:YYYY-MM-DD}.log",
            level="DEBUG",
            rotation=rotation,
            retention=retention,
            compression="zip",
            filter=lambda record: "database" in record["extra"]
        )
        
        logger.info(f"✅ 日志系统初始化完成 - 级别: {log_level}, 目录: {log_dir}")
    
    @staticmethod
    def log_api_access(
        method: str,
        path: str,
        status: int,
        duration: float,
        user_id: int = None
    ):
        """
        记录API访问日志
        
        Args:
            method: HTTP方法
            path: 请求路径
            status: 响应状态码
            duration: 处理时长（毫秒）
            user_id: 用户ID（可选）
        """
        logger.bind(
            api_access=True,
            method=method,
            path=path,
            status=status,
            duration=duration,
            user_id=user_id
        ).info(f"{method} {path} - {status} - {duration}ms")
    
    @staticmethod
    def log_database_query(query: str, duration: float):
        """
        记录数据库查询日志
        
        Args:
            query: SQL查询
            duration: 查询时长（毫秒）
        """
        logger.bind(
            database=True,
            query=query,
            duration=duration
        ).debug(f"DB Query: {duration}ms - {query[:100]}...")
    
    @staticmethod
    def log_user_action(
        user_id: int,
        action: str,
        resource: str,
        details: dict = None
    ):
        """
        记录用户行为日志
        
        Args:
            user_id: 用户ID
            action: 操作类型
            resource: 资源类型
            details: 详细信息
        """
        logger.bind(
            user_action=True,
            user_id=user_id,
            action=action,
            resource=resource
        ).info(f"用户{user_id} {action} {resource}", details=details or {})


# 全局实例
log_setup = LoggerSetup()


# 便捷函数
def setup_logger(log_level: str = "INFO", json_format: bool = False):
    """配置日志"""
    log_setup.setup_logger(log_level=log_level, json_format=json_format)


def log_api(method: str, path: str, status: int, duration: float, user_id: int = None):
    """记录API访问"""
    log_setup.log_api_access(method, path, status, duration, user_id)


def log_db_query(query: str, duration: float):
    """记录数据库查询"""
    log_setup.log_database_query(query, duration)


def log_user(user_id: int, action: str, resource: str, details: dict = None):
    """记录用户行为"""
    log_setup.log_user_action(user_id, action, resource, details)


# 日志装饰器
def log_function_call(func):
    """函数调用日志装饰器"""
    import functools
    import time
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.debug(f"函数调用: {func.__name__} - {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"函数异常: {func.__name__} - {duration:.2f}ms - {e}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.debug(f"函数调用: {func.__name__} - {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"函数异常: {func.__name__} - {duration:.2f}ms - {e}")
            raise
    
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
