"""
学习进度跟踪API
记录和管理用户的学习进度
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
from pathlib import Path
from collections import defaultdict

router = APIRouter(prefix="/api/progress", tags=["Learning Progress"])

# 数据存储路径
PROGRESS_DATA_DIR = Path(__file__).parent.parent / "data" / "progress"
PROGRESS_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ==================== 数据模型 ====================

class ProgressUpdate(BaseModel):
    """进度更新"""
    user_id: str = Field(default="default_user", description="用户ID")
    item_type: str = Field(..., description="项目类型: textbook, chapter, case, exercise")
    item_id: str = Field(..., description="项目ID")
    status: str = Field(..., description="状态: not_started, in_progress, completed, reviewed")
    progress_percent: Optional[int] = Field(None, description="进度百分比 (0-100)", ge=0, le=100)
    time_spent: Optional[int] = Field(None, description="学习时长（秒）", ge=0)
    notes: Optional[str] = Field(None, description="学习笔记")

class ProgressQuery(BaseModel):
    """进度查询"""
    user_id: str = Field(default="default_user")
    item_type: Optional[str] = None
    status: Optional[str] = None

class StudySession(BaseModel):
    """学习会话"""
    user_id: str = Field(default="default_user")
    item_type: str
    item_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # 秒

# ==================== 工具函数 ====================

def get_progress_file(user_id: str) -> Path:
    """获取用户进度文件路径"""
    return PROGRESS_DATA_DIR / f"{user_id}_progress.json"

def load_user_progress(user_id: str) -> Dict[str, Any]:
    """加载用户进度数据"""
    file_path = get_progress_file(user_id)
    if not file_path.exists():
        return {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "items": {},
            "statistics": {
                "total_items": 0,
                "completed_items": 0,
                "in_progress_items": 0,
                "total_time_spent": 0
            }
        }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载进度数据失败: {e}")
        return load_user_progress(user_id)  # 返回默认数据

def save_user_progress(user_id: str, progress_data: Dict[str, Any]):
    """保存用户进度数据"""
    file_path = get_progress_file(user_id)
    progress_data["last_updated"] = datetime.now().isoformat()
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存进度数据失败: {e}")
        return False

def calculate_statistics(progress_data: Dict[str, Any]) -> Dict[str, Any]:
    """计算统计信息"""
    items = progress_data.get("items", {})
    
    stats = {
        "total_items": len(items),
        "completed_items": 0,
        "in_progress_items": 0,
        "not_started_items": 0,
        "reviewed_items": 0,
        "total_time_spent": 0,
        "by_type": defaultdict(lambda: {
            "total": 0,
            "completed": 0,
            "in_progress": 0
        })
    }
    
    for item_key, item_data in items.items():
        status = item_data.get("status", "not_started")
        item_type = item_data.get("item_type", "unknown")
        time_spent = item_data.get("time_spent", 0)
        
        # 按状态统计
        if status == "completed":
            stats["completed_items"] += 1
            stats["by_type"][item_type]["completed"] += 1
        elif status == "in_progress":
            stats["in_progress_items"] += 1
            stats["by_type"][item_type]["in_progress"] += 1
        elif status == "not_started":
            stats["not_started_items"] += 1
        elif status == "reviewed":
            stats["reviewed_items"] += 1
        
        # 按类型统计
        stats["by_type"][item_type]["total"] += 1
        
        # 总时长
        stats["total_time_spent"] += time_spent
    
    # 转换defaultdict为普通dict
    stats["by_type"] = dict(stats["by_type"])
    
    # 计算完成率
    if stats["total_items"] > 0:
        stats["completion_rate"] = round(stats["completed_items"] / stats["total_items"] * 100, 2)
    else:
        stats["completion_rate"] = 0.0
    
    return stats

# ==================== API端点 ====================

@router.post("/update")
async def update_progress(update: ProgressUpdate):
    """
    更新学习进度
    """
    # 加载用户数据
    progress_data = load_user_progress(update.user_id)
    
    # 构建项目键
    item_key = f"{update.item_type}:{update.item_id}"
    
    # 获取或创建项目记录
    if item_key not in progress_data["items"]:
        progress_data["items"][item_key] = {
            "item_type": update.item_type,
            "item_id": update.item_id,
            "status": "not_started",
            "progress_percent": 0,
            "time_spent": 0,
            "created_at": datetime.now().isoformat(),
            "history": []
        }
    
    item = progress_data["items"][item_key]
    
    # 记录历史
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "old_status": item["status"],
        "new_status": update.status,
        "old_progress": item.get("progress_percent", 0),
        "new_progress": update.progress_percent or item.get("progress_percent", 0)
    }
    item["history"].append(history_entry)
    
    # 更新状态
    item["status"] = update.status
    item["last_updated"] = datetime.now().isoformat()
    
    if update.progress_percent is not None:
        item["progress_percent"] = update.progress_percent
    
    if update.time_spent is not None:
        item["time_spent"] = item.get("time_spent", 0) + update.time_spent
    
    if update.notes:
        if "notes" not in item:
            item["notes"] = []
        item["notes"].append({
            "timestamp": datetime.now().isoformat(),
            "content": update.notes
        })
    
    # 更新统计
    progress_data["statistics"] = calculate_statistics(progress_data)
    
    # 保存
    success = save_user_progress(update.user_id, progress_data)
    
    if success:
        return {
            "success": True,
            "message": "进度已更新",
            "item": item,
            "statistics": progress_data["statistics"]
        }
    else:
        raise HTTPException(status_code=500, detail="保存进度失败")

@router.get("/user/{user_id}")
async def get_user_progress(
    user_id: str,
    item_type: Optional[str] = None,
    status: Optional[str] = None
):
    """
    获取用户进度
    """
    progress_data = load_user_progress(user_id)
    items = progress_data.get("items", {})
    
    # 过滤
    filtered_items = {}
    for key, item in items.items():
        if item_type and item.get("item_type") != item_type:
            continue
        if status and item.get("status") != status:
            continue
        filtered_items[key] = item
    
    return {
        "success": True,
        "user_id": user_id,
        "statistics": progress_data.get("statistics", {}),
        "items": filtered_items,
        "total_items": len(filtered_items)
    }

@router.get("/item/{item_type}/{item_id}")
async def get_item_progress(
    item_type: str,
    item_id: str,
    user_id: str = "default_user"
):
    """
    获取特定项目的进度
    """
    progress_data = load_user_progress(user_id)
    item_key = f"{item_type}:{item_id}"
    
    item = progress_data.get("items", {}).get(item_key)
    
    if not item:
        return {
            "success": True,
            "found": False,
            "item_type": item_type,
            "item_id": item_id,
            "status": "not_started",
            "progress_percent": 0
        }
    
    return {
        "success": True,
        "found": True,
        **item
    }

@router.get("/statistics/{user_id}")
async def get_statistics(user_id: str):
    """
    获取用户学习统计
    """
    progress_data = load_user_progress(user_id)
    
    # 重新计算统计
    statistics = calculate_statistics(progress_data)
    
    # 添加时间统计
    statistics["time_stats"] = {
        "total_hours": round(statistics["total_time_spent"] / 3600, 2),
        "total_minutes": round(statistics["total_time_spent"] / 60, 1),
        "average_per_item": round(statistics["total_time_spent"] / max(statistics["total_items"], 1) / 60, 1)
    }
    
    return {
        "success": True,
        "user_id": user_id,
        "statistics": statistics
    }

@router.post("/session/start")
async def start_study_session(session: StudySession):
    """
    开始学习会话
    """
    session_file = PROGRESS_DATA_DIR / f"{session.user_id}_current_session.json"
    
    session_data = {
        "user_id": session.user_id,
        "item_type": session.item_type,
        "item_id": session.item_id,
        "start_time": datetime.now().isoformat(),
        "active": True
    }
    
    try:
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": "学习会话已开始",
            "session": session_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"开始会话失败: {str(e)}")

@router.post("/session/end")
async def end_study_session(user_id: str = "default_user"):
    """
    结束学习会话并更新进度
    """
    session_file = PROGRESS_DATA_DIR / f"{user_id}_current_session.json"
    
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="没有活动的学习会话")
    
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        if not session_data.get("active"):
            raise HTTPException(status_code=400, detail="会话已结束")
        
        # 计算学习时长
        start_time = datetime.fromisoformat(session_data["start_time"])
        end_time = datetime.now()
        duration = int((end_time - start_time).total_seconds())
        
        # 更新进度
        update = ProgressUpdate(
            user_id=user_id,
            item_type=session_data["item_type"],
            item_id=session_data["item_id"],
            status="in_progress",
            time_spent=duration
        )
        
        result = await update_progress(update)
        
        # 删除会话文件
        session_file.unlink()
        
        return {
            "success": True,
            "message": "学习会话已结束",
            "duration": duration,
            "duration_minutes": round(duration / 60, 1),
            "progress": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"结束会话失败: {str(e)}")

@router.get("/session/current/{user_id}")
async def get_current_session(user_id: str):
    """
    获取当前学习会话
    """
    session_file = PROGRESS_DATA_DIR / f"{user_id}_current_session.json"
    
    if not session_file.exists():
        return {
            "success": True,
            "active": False,
            "message": "没有活动的学习会话"
        }
    
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # 计算已学习时长
        start_time = datetime.fromisoformat(session_data["start_time"])
        duration = int((datetime.now() - start_time).total_seconds())
        
        return {
            "success": True,
            "active": True,
            "session": session_data,
            "duration": duration,
            "duration_minutes": round(duration / 60, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话失败: {str(e)}")

@router.delete("/reset/{user_id}")
async def reset_progress(user_id: str, confirm: bool = False):
    """
    重置用户进度（危险操作）
    """
    if not confirm:
        raise HTTPException(status_code=400, detail="请确认重置操作")
    
    file_path = get_progress_file(user_id)
    
    if file_path.exists():
        try:
            file_path.unlink()
            return {
                "success": True,
                "message": f"用户 {user_id} 的进度已重置"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"重置失败: {str(e)}")
    else:
        return {
            "success": True,
            "message": "用户进度文件不存在"
        }

@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    """
    获取学习排行榜
    """
    leaderboard = []
    
    # 遍历所有用户进度文件
    for progress_file in PROGRESS_DATA_DIR.glob("*_progress.json"):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            stats = data.get("statistics", {})
            leaderboard.append({
                "user_id": data.get("user_id"),
                "completed_items": stats.get("completed_items", 0),
                "total_time_spent": stats.get("total_time_spent", 0),
                "completion_rate": stats.get("completion_rate", 0)
            })
        except Exception as e:
            print(f"读取进度文件失败 {progress_file}: {e}")
            continue
    
    # 按完成数量排序
    leaderboard.sort(key=lambda x: (x["completed_items"], x["total_time_spent"]), reverse=True)
    
    return {
        "success": True,
        "leaderboard": leaderboard[:limit],
        "total_users": len(leaderboard)
    }

@router.get("/health")
async def health_check():
    """
    健康检查
    """
    return {
        "success": True,
        "status": "healthy",
        "data_directory": str(PROGRESS_DATA_DIR),
        "total_users": len(list(PROGRESS_DATA_DIR.glob("*_progress.json")))
    }

