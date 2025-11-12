#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教材数据库管理
处理教材数据的数据库连接和会话管理
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os

from .models import Base

# 数据库配置
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv("TEXTBOOK_DB_URL", f"sqlite:///{DB_DIR}/textbooks.db")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    echo=DEBUG,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """初始化数据库（创建所有表）"""
    Base.metadata.create_all(bind=engine)
    print(f"[OK] 教材数据库已初始化: {DATABASE_URL}")


def get_db_session():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    print("初始化教材数据库...")
    init_database()
    print("完成!")


