# coding: utf-8
"""
为明渠水力学计算教材添加演示案例关联
"""
import sqlite3
from datetime import datetime

conn = sqlite3.connect('data/textbooks.db')
cursor = conn.cursor()

# 获取明渠水力学计算的所有章节
cursor.execute("""
SELECT id, chapter_number, title 
FROM textbook_chapters 
WHERE textbook_id = '4978a8af-4b89-4d38-8f2e-bb1c3ebc5429'
ORDER BY order_num
LIMIT 5
""")

chapters = cursor.fetchall()
print(f'找到 {len(chapters)} 个章节')

# 为每个章节添加一些案例关联（演示用）
demo_cases = [
    'case_01_tank_simulation',
    'case_02_PID_tank',
    'case_03_cascade_tanks'
]

for chapter in chapters:
    chapter_id, chapter_number, title = chapter
    print(f'\n处理章节: {chapter_number} {title}')
    
    # 为每个章节添加3个案例
    for idx, case_id in enumerate(demo_cases):
        cursor.execute("""
        INSERT INTO chapter_case_mappings 
        (chapter_id, case_id, relation_type, relevance_score, description, order_num, is_auto_generated, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chapter_id,
            case_id,
            'practice',
            0.9 - idx * 0.1,
            f'与章节 {chapter_number} 相关的实践案例',
            idx + 1,
            1,
            datetime.now()
        ))
        print(f'  添加案例: {case_id}')

conn.commit()
print(f'\n成功添加 {len(chapters) * len(demo_cases)} 条关联记录')

# 验证
cursor.execute("SELECT COUNT(*) FROM chapter_case_mappings WHERE chapter_id = ?", (chapters[0][0],))
count = cursor.fetchone()[0]
print(f'验证: 第一个章节现在有 {count} 个关联案例')

conn.close()

