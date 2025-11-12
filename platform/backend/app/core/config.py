"""
核心配置
使用Pydantic Settings管理所有配置
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List, Optional
import secrets


class Settings(BaseSettings):
    """应用配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ========================================
    # 应用基本配置
    # ========================================
    APP_NAME: str = "Engineering Learning Platform"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_VERSION: str = "1.0.0"
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    
    # ========================================
    # 数据库配置
    # ========================================
    # DATABASE_URL: 可以直接在.env中设置完整URL，或使用下面的分离配置
    DATABASE_URL: Optional[str] = None

    # PostgreSQL（当DATABASE_URL未设置时使用）
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "elp_db"
    POSTGRES_USER: str = "elp_user"
    POSTGRES_PASSWORD: str = "elp_password"

    @property
    def database_url(self) -> str:
        """生成数据库URL"""
        # 如果.env中直接设置了DATABASE_URL，则使用它
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # 否则使用PostgreSQL配置生成URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # MongoDB
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_DB: str = "elp_content"
    MONGODB_USER: str = "elp_mongo_user"
    MONGODB_PASSWORD: str = "elp_mongo_password"
    
    @property
    def MONGODB_URL(self) -> str:
        """生成MongoDB URL"""
        if self.MONGODB_USER and self.MONGODB_PASSWORD:
            return (
                f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}"
                f"@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"
            )
        return f"mongodb://{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    @property
    def REDIS_URL(self) -> str:
        """生成Redis URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ========================================
    # JWT配置
    # ========================================
    JWT_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ========================================
    # OAuth配置
    # ========================================
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    
    # ========================================
    # 支付配置
    # ========================================
    # 微信支付
    WECHAT_PAY_MCHID: Optional[str] = None
    WECHAT_PAY_API_KEY: Optional[str] = None
    
    # 支付宝
    ALIPAY_APP_ID: Optional[str] = None
    ALIPAY_PRIVATE_KEY: Optional[str] = None
    
    # Stripe
    STRIPE_PUBLIC_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # ========================================
    # AI服务配置
    # ========================================
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Anthropic Claude
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    
    # 百度文心一言
    BAIDU_API_KEY: Optional[str] = None
    BAIDU_SECRET_KEY: Optional[str] = None
    
    # 向量数据库
    WEAVIATE_URL: str = "http://localhost:8080"
    WEAVIATE_API_KEY: Optional[str] = None
    
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-east-1-aws"
    PINECONE_INDEX_NAME: str = "elp-embeddings"
    
    # ========================================
    # 对象存储配置
    # ========================================
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "elp-storage"
    S3_REGION: str = "us-east-1"
    S3_USE_SSL: bool = False
    
    # ========================================
    # 邮件配置
    # ========================================
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@example.com"
    SMTP_FROM_NAME: str = "Engineering Learning Platform"
    SMTP_TLS: bool = True
    
    # ========================================
    # 短信配置
    # ========================================
    SMS_PROVIDER: str = "aliyun"
    ALIYUN_ACCESS_KEY: Optional[str] = None
    ALIYUN_ACCESS_SECRET: Optional[str] = None
    SMS_SIGN_NAME: str = "工程学习平台"
    SMS_TEMPLATE_CODE: Optional[str] = None
    
    # ========================================
    # CDN配置
    # ========================================
    CDN_DOMAIN: Optional[str] = None
    CDN_ENABLED: bool = False
    
    # ========================================
    # 脚本执行引擎配置
    # ========================================
    EXECUTOR_TYPE: str = "docker"
    DOCKER_IMAGE: str = "elp-python-runner:latest"
    EXECUTOR_TIMEOUT: int = 30
    EXECUTOR_MAX_MEMORY: str = "512m"
    EXECUTOR_MAX_CPU: str = "1"
    
    # ========================================
    # 内容扫描器配置
    # ========================================
    BOOKS_PATH: str = "/workspace/books"
    SCANNER_INTERVAL: int = 300
    AUTO_SCAN_ENABLED: bool = True
    
    # ========================================
    # Celery配置
    # ========================================
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    @property
    def CELERY_BROKER(self) -> str:
        """Celery broker URL"""
        return self.CELERY_BROKER_URL or f"{self.REDIS_URL.replace('/0', '/1')}"
    
    @property
    def CELERY_BACKEND(self) -> str:
        """Celery result backend URL"""
        return self.CELERY_RESULT_BACKEND or f"{self.REDIS_URL.replace('/0', '/2')}"
    
    # ========================================
    # 监控配置
    # ========================================
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    PROMETHEUS_PORT: int = 9090
    
    # ========================================
    # 速率限制
    # ========================================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # ========================================
    # CORS配置
    # ========================================
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    @field_validator("CORS_ORIGINS", mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """解析CORS origins"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # ========================================
    # 安全配置
    # ========================================
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    @field_validator("ALLOWED_HOSTS", mode='before')
    @classmethod
    def parse_allowed_hosts(cls, v):
        """解析允许的主机"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    # ========================================
    # 功能开关
    # ========================================
    FEATURE_AI_ASSISTANT: bool = True
    FEATURE_SOCIAL_LOGIN: bool = True
    FEATURE_PAYMENT: bool = True
    FEATURE_COMMUNITY: bool = True
    FEATURE_CERTIFICATE: bool = False
    FEATURE_LIVE_CLASS: bool = False
    
    # ========================================
    # 商业配置
    # ========================================
    FREE_TRIAL_DAYS: int = 7
    SUBSCRIPTION_PRICE_MONTHLY: int = 99
    SUBSCRIPTION_PRICE_YEARLY: int = 899
    BOOK_PRICE_DEFAULT: int = 299


# 创建全局配置实例
settings = Settings()
