"""
API限流中间件
使用滑动窗口算法实现请求频率限制
"""

import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    """API限流中间件"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        """
        初始化限流中间件
        
        Args:
            app: FastAPI应用实例
            requests_per_minute: 每分钟允许的请求数
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 窗口大小（秒）
        
        # 存储每个IP的请求历史 {ip: [(timestamp, count), ...]}
        self.request_history: Dict[str, list] = {}
        
        # 白名单路径（不限流）
        self.whitelist_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/info"
        ]
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        # 优先从X-Forwarded-For获取（考虑代理情况）
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # 从X-Real-IP获取
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 直接连接的IP
        return request.client.host if request.client else "unknown"
    
    def _clean_old_requests(self, ip: str, current_time: float):
        """清理过期的请求记录"""
        if ip not in self.request_history:
            return
        
        # 移除超过窗口期的记录
        self.request_history[ip] = [
            (ts, count) for ts, count in self.request_history[ip]
            if current_time - ts < self.window_size
        ]
        
        # 如果列表为空，删除该IP的记录
        if not self.request_history[ip]:
            del self.request_history[ip]
    
    def _is_rate_limited(self, ip: str) -> Tuple[bool, int]:
        """
        检查IP是否被限流
        
        Returns:
            (is_limited, remaining_requests)
        """
        current_time = time.time()
        
        # 清理过期记录
        self._clean_old_requests(ip, current_time)
        
        # 计算窗口内的请求总数
        if ip not in self.request_history:
            self.request_history[ip] = []
        
        total_requests = sum(count for _, count in self.request_history[ip])
        
        # 判断是否超限
        if total_requests >= self.requests_per_minute:
            remaining = 0
            return True, remaining
        
        # 记录本次请求
        self.request_history[ip].append((current_time, 1))
        
        remaining = self.requests_per_minute - total_requests - 1
        return False, remaining
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 检查是否在白名单中
        if request.url.path in self.whitelist_paths:
            return await call_next(request)
        
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 检查是否限流
        is_limited, remaining = self._is_rate_limited(client_ip)
        
        if is_limited:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "请求过于频繁",
                    "message": f"每分钟最多 {self.requests_per_minute} 个请求",
                    "retry_after": 60
                }
            )
        
        # 添加限流信息到响应头
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        return response


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """IP白名单中间件"""
    
    def __init__(self, app, whitelist: list = None):
        """
        初始化IP白名单中间件
        
        Args:
            app: FastAPI应用实例
            whitelist: IP白名单列表
        """
        super().__init__(app)
        self.whitelist = set(whitelist or [])
        
        # 默认白名单（本地开发）
        self.whitelist.update([
            "127.0.0.1",
            "localhost",
            "::1"
        ])
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        client_ip = self._get_client_ip(request)
        
        # 仅对管理端点进行IP限制
        if request.url.path.startswith("/api/v1/admin"):
            if client_ip not in self.whitelist:
                logger.warning(f"Unauthorized IP access attempt: {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权访问此资源"
                )
        
        return await call_next(request)


# 便捷函数
def add_rate_limit_middleware(app, requests_per_minute: int = 60):
    """添加限流中间件"""
    app.add_middleware(RateLimitMiddleware, requests_per_minute=requests_per_minute)
    logger.info(f"✅ Rate limit middleware enabled: {requests_per_minute} req/min")


def add_ip_whitelist_middleware(app, whitelist: list = None):
    """添加IP白名单中间件"""
    app.add_middleware(IPWhitelistMiddleware, whitelist=whitelist)
    logger.info(f"✅ IP whitelist middleware enabled: {len(whitelist or [])} IPs")
