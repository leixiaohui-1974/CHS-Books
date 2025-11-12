# coding: utf-8
import sqlite3

conn = sqlite3.connect('data/textbooks.db')
cursor = conn.cursor()

chapter_id = 'c94f25d8-6b9d-4f9e-bf32-b0b562d72b59'

print("查询章节案例关联:")
cursor.execute("""
    SELECT case_id, relation_type, relevance_score, description 
    FROM chapter_case_mappings 
    WHERE chapter_id = ?
""", (chapter_id,))

cases = cursor.fetchall()
print(f"找到 {len(cases)} 个案例:")
for i, case in enumerate(cases, 1):
    case_id, rel_type, score, desc = case
    print(f"{i}. {case_id}")
    print(f"   类型: {rel_type}")
    print(f"   评分: {score}")
    print(f"   描述: {desc[:50] if desc else 'N/A'}...")
    print()

conn.close()

