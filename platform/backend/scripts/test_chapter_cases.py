"""
测试章节关联案例数据
"""
import sys
from pathlib import Path

# 添加路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# 切换工作目录
import os
os.chdir(backend_path)

from services.database import SessionLocal
from services.textbook.models import TextbookChapter, ChapterCaseMapping

def main():
    db = SessionLocal()
    
    try:
        # 查找"明渠水力学计算 - 快速开始指南"章节
        chapter = db.query(TextbookChapter).filter(
            TextbookChapter.title.like('%明渠水力学计算%快速开始%')
        ).first()
        
        if not chapter:
            print('[失败] 未找到章节')
            return
        
        print(f'[成功] 找到章节: {chapter.title}')
        print(f'  - ID: {chapter.id}')
        print(f'  - 教材ID: {chapter.textbook_id}')
        
        # 查找关联案例
        case_mappings = db.query(ChapterCaseMapping).filter(
            ChapterCaseMapping.chapter_id == chapter.id
        ).all()
        
        print(f'\n[成功] 找到 {len(case_mappings)} 个关联案例')
        
        for mapping in case_mappings:
            print(f'  - 案例ID: {mapping.case_id}')
            print(f'    关系类型: {mapping.relation_type}')
            print(f'    相关度: {mapping.relevance_score}')
            print(f'    说明: {mapping.description}')
            print()
        
        # 测试 get_case_info_from_file
        if case_mappings:
            from api.textbook_routes import get_case_info_from_file
            case_id = case_mappings[0].case_id
            print(f'\n测试 get_case_info_from_file(\'{case_id}\')...')
            case_info = get_case_info_from_file(case_id)
            if case_info:
                print(f'[成功] 案例信息:')
                print(f'  - 标题: {case_info.get("title")}')
                print(f'  - 图标: {case_info.get("icon")}')
                print(f'  - 描述: {case_info.get("description", "")[:100]}...')
            else:
                print(f'[失败] 无法读取案例信息')
        
    except Exception as e:
        import traceback
        print(f'[错误] {e}')
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    main()

