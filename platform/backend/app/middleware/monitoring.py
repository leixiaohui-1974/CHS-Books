"""
性能监控中间件
收集API请求的性能指标
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
from prometheus_client import Counter, Histogram, Gauge
import psutil


# Prometheus指标
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Number of active HTTP requests'
)

MEMORY_USAGE = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes'
)

CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)


class MonitoringMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 跳过健康检查和指标端点
        if request.url.path in ["/api/v1/health", "/api/v1/metrics", "/api/v1/live", "/api/v1/ready"]:
            return await call_next(request)
        
        # 增加活跃请求计数
        ACTIVE_REQUESTS.inc()
        
        # 记录开始时间
        start_time = time.time()
        
        # 处理请求
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            status_code = 500
            raise
        finally:
            # 计算请求耗时
            duration = time.time() - start_time
            
            # 记录指标
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            # 减少活跃请求计数
            ACTIVE_REQUESTS.dec()
            
            # 更新系统资源指标
            try:
                memory = psutil.virtual_memory()
                MEMORY_USAGE.set(memory.used)
                CPU_USAGE.set(psutil.cpu_percent(interval=0))
            except:
                pass
            
            # 记录慢请求
            if duration > 1.0:  # 超过1秒
                logger.warning(
                    f"Slow request: {request.method} {request.url.path} "
                    f"took {duration:.2f}s"
                )
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 跳过健康检查端点的日志
        if request.url.path in ["/api/v1/health", "/api/v1/live", "/api/v1/ready"]:
            return await call_next(request)
        
        # 记录请求开始
        start_time = time.time()
        
        logger.info(
            f"→ {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # 处理请求
        response = await call_next(request)
        
        # 计算耗时
        duration = (time.time() - start_time) * 1000  # 转换为毫秒
        
        # 记录请求完成
        logger.info(
            f"← {request.method} {request.url.path} "
            f"[{response.status_code}] {duration:.2f}ms"
        )
        
        # 添加响应头
        response.headers["X-Process-Time"] = f"{duration:.2f}ms"
        
        return response
