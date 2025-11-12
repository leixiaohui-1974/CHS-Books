"""
数据库连接和会话管理
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from .models import Base

# 数据库配置
DATABASE_URL = os.getenv("KNOWLEDGE_DB_URL", "sqlite:///./knowledge.db")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 创建数据库引擎
if DATABASE_URL.startswith("sqlite"):
    # SQLite需要特殊配置
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=DEBUG
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        echo=DEBUG
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功！")


def get_db() -> Session:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_default_categories(db: Session):
    """初始化默认分类"""
    from .models import Category
    
    # 检查是否已有分类
    if db.query(Category).count() > 0:
        return
    
    # 一级分类
    categories_data = [
        {
            "name": "水利工程",
            "description": "水利工程相关知识",
            "children": [
                {"name": "水资源规划与管理", "description": ""},
                {"name": "水工建筑物", "description": ""},
                {"name": "水利水电工程施工", "description": ""},
                {"name": "水利工程测量", "description": ""},
                {"name": "水利工程经济", "description": ""},
            ]
        },
        {
            "name": "水电工程",
            "description": "水电工程相关知识",
            "children": [
                {"name": "水电站设计", "description": ""},
                {"name": "水轮机及辅助设备", "description": ""},
                {"name": "水电站电气设备", "description": ""},
                {"name": "水电站自动化", "description": ""},
                {"name": "新能源发电", "description": ""},
            ]
        },
        {
            "name": "水务工程",
            "description": "水务工程相关知识",
            "children": [
                {"name": "城市给排水", "description": ""},
                {"name": "污水处理", "description": ""},
                {"name": "水质监测", "description": ""},
                {"name": "供水管网", "description": ""},
                {"name": "智慧水务", "description": ""},
            ]
        },
        {
            "name": "基础学科",
            "description": "基础学科知识",
            "children": [
                {"name": "水力学", "description": ""},
                {"name": "工程力学", "description": ""},
                {"name": "土力学", "description": ""},
                {"name": "工程地质", "description": ""},
                {"name": "工程测量", "description": ""},
                {"name": "自动控制", "description": ""},
            ]
        },
        {
            "name": "规范标准",
            "description": "国家和国际规范标准",
            "children": [
                {"name": "国家标准", "description": "中国国家标准"},
                {"name": "行业标准", "description": "水利水电行业标准"},
                {"name": "地方标准", "description": "各省市地方标准"},
                {"name": "国际标准", "description": "ISO、IEC等国际标准"},
            ]
        }
    ]
    
    # 创建分类
    for idx, cat_data in enumerate(categories_data):
        parent_cat = Category(
            name=cat_data["name"],
            description=cat_data["description"],
            level=0,
            order_num=idx
        )
        db.add(parent_cat)
        db.flush()
        
        # 创建子分类
        for child_idx, child_data in enumerate(cat_data.get("children", [])):
            child_cat = Category(
                name=child_data["name"],
                description=child_data["description"],
                parent_id=parent_cat.id,
                level=1,
                order_num=child_idx
            )
            db.add(child_cat)
    
    db.commit()
    print("默认分类创建成功！")
