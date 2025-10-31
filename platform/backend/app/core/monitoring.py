"""
监控和指标收集
"""

from prometheus_client import Counter, Histogram, Gauge
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from .config import settings
from loguru import logger


# Prometheus指标
request_count = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"]
)

active_users = Gauge(
    "active_users_total",
    "Total active users"
)

tool_executions = Counter(
    "tool_executions_total",
    "Total tool executions",
    ["case_id", "status"]
)

ai_requests = Counter(
    "ai_requests_total",
    "Total AI requests",
    ["model", "status"]
)

database_connections = Gauge(
    "database_connections_active",
    "Active database connections"
)


def setup_monitoring():
    """设置监控系统"""
    
    # 初始化Sentry（错误追踪）
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=1.0 if settings.APP_ENV == "development" else 0.1,
            profiles_sample_rate=1.0 if settings.APP_ENV == "development" else 0.1,
        )
        logger.info("✅ Sentry监控已启动")
    else:
        logger.warning("⚠️  未配置Sentry DSN，错误追踪功能未启用")
    
    logger.info("✅ Prometheus指标已注册")
