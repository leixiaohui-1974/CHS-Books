"""
案例相关API路由
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
import re

router = APIRouter(prefix="/api/cases", tags=["cases"])

def find_case_directory(case_id: str) -> Path:
    """查找案例目录"""
    books_root = Path(__file__).parent.parent.parent.parent / 'books'
    
    for book_dir in books_root.iterdir():
        if not book_dir.is_dir():
            continue
        
        examples_dir = book_dir / 'code' / 'examples'
        if not examples_dir.exists():
            continue
        
        # 完全匹配
        case_dir = examples_dir / case_id
        if case_dir.exists():
            return case_dir
        
        # 部分匹配（fallback）
        for d in examples_dir.iterdir():
            if d.is_dir() and case_id in d.name:
                return d
    
    return None

@router.get("/{case_id}/readme")
async def get_case_readme(case_id: str):
    """获取案例的README文档"""
    try:
        case_dir = find_case_directory(case_id)
        
        if not case_dir:
            raise HTTPException(status_code=404, detail=f"案例 {case_id} 未找到")
        
        readme_file = case_dir / 'README.md'
        if not readme_file.exists():
            raise HTTPException(status_code=404, detail=f"案例 {case_id} 的README.md未找到")
        
        content = readme_file.read_text(encoding='utf-8')
        
        # 提取标题
        title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        title = title_match.group(1) if title_match else case_id
        
        return {
            "success": True,
            "case_id": case_id,
            "title": title,
            "content": content,
            "path": str(case_dir)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"读取案例文档失败: {str(e)}")

@router.get("/{case_id}/code")
async def get_case_code(case_id: str):
    """获取案例的代码文件"""
    try:
        case_dir = find_case_directory(case_id)
        
        if not case_dir:
            raise HTTPException(status_code=404, detail=f"案例 {case_id} 未找到")
        
        # 查找Python文件
        code_files = []
        for pattern in ['main.py', 'demo*.py', '*.py']:
            code_files.extend(case_dir.glob(pattern))
        
        if not code_files:
            raise HTTPException(status_code=404, detail=f"案例 {case_id} 没有找到Python代码文件")
        
        # 使用第一个找到的文件
        main_file = code_files[0]
        code = main_file.read_text(encoding='utf-8')
        
        return {
            "success": True,
            "case_id": case_id,
            "filename": main_file.name,
            "code": code,
            "path": str(case_dir)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"读取案例代码失败: {str(e)}")

@router.get("/{case_id}/info")
async def get_case_info(case_id: str):
    """获取案例的完整信息"""
    try:
        case_dir = find_case_directory(case_id)
        
        if not case_dir:
            raise HTTPException(status_code=404, detail=f"案例 {case_id} 未找到")
        
        # 读取README
        readme_file = case_dir / 'README.md'
        readme_content = ""
        title = case_id
        if readme_file.exists():
            readme_content = readme_file.read_text(encoding='utf-8')
            title_match = re.search(r'^#\s+(.+)', readme_content, re.MULTILINE)
            if title_match:
                title = title_match.group(1)
        
        # 查找代码文件
        code_files = list(case_dir.glob('*.py'))
        
        # 查找图片
        images = []
        for pattern in ['*.png', '*.jpg', '*.jpeg', '*.gif']:
            images.extend(case_dir.glob(pattern))
        
        return {
            "success": True,
            "case_id": case_id,
            "title": title,
            "path": str(case_dir),
            "has_readme": readme_file.exists(),
            "code_files": [f.name for f in code_files],
            "images": [f.name for f in images]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取案例信息失败: {str(e)}")

