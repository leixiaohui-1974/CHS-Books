import sqlite3

conn = sqlite3.connect('data/textbooks.db')
cursor = conn.cursor()

# 查找关联案例
cursor.execute("SELECT case_id, relation_type, relevance_score, description FROM chapter_case_mappings WHERE chapter_id = 'c94f25d8-6b9d-4f9e-bf32-b0b562d72b59'")
cases = cursor.fetchall()
print(f'Related cases ({len(cases)}):')
for case in cases:
    print(f'  - {case}')

# 查找所有关联
cursor.execute("SELECT COUNT(*) FROM chapter_case_mappings")
total = cursor.fetchone()[0]
print(f'\n总关联案例数: {total}')

conn.close()

