import sqlite3

conn = sqlite3.connect('data/textbooks.db')
cursor = conn.cursor()

# 列出所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('数据库中的表:')
for table in tables:
    print(f'  - {table[0]}')
    
    # 列出表结构
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    for col in columns:
        print(f'      {col[1]} ({col[2]})')

conn.close()

