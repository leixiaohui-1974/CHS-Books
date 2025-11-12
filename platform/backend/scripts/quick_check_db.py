import sqlite3

conn = sqlite3.connect('data/textbooks.db')
cursor = conn.cursor()

# 查找章节
cursor.execute("SELECT id, title FROM textbook_chapters WHERE id = 'c94f25d8-6b9d-4f9e-bf32-b0b562d72b59'")
chapter = cursor.fetchone()
print(f'Chapter: {chapter}')

# 查找关联案例
cursor.execute("SELECT case_id, relation_type, relevance_score, description FROM chapter_case_mapping WHERE chapter_id = 'c94f25d8-6b9d-4f9e-bf32-b0b562d72b59'")
cases = cursor.fetchall()
print(f'\nRelated cases ({len(cases)}):')
for case in cases:
    print(f'  - {case}')

conn.close()

