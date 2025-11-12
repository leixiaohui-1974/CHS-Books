#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速添加新书籍的脚本
用于快速创建新书的目录结构和导入到数据库
"""

import sys
import io
from pathlib import Path
import shutil

# 设置UTF-8输出
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

EXAM_PREP_DIR = Path(__file__).parent.parent.parent.parent / "books" / "graduate-exam-prep"


def create_book_structure(book_slug, book_title, num_chapters=10):
    """创建新书的目录结构"""
    
    book_dir = EXAM_PREP_DIR / book_slug
    
    if book_dir.exists():
        print(f"[WARN] 目录已存在: {book_dir}")
        response = input("是否覆盖？(y/N): ")
        if response.lower() != 'y':
            print("[CANCEL] 取消操作")
            return False
        shutil.rmtree(book_dir)
    
    print(f"\n[CREATE] 创建书籍目录结构...")
    print(f"路径: {book_dir}")
    
    # 创建目录
    book_dir.mkdir(parents=True, exist_ok=True)
    chapters_dir = book_dir / "chapters"
    chapters_dir.mkdir(exist_ok=True)
    codes_dir = book_dir / "codes"
    codes_dir.mkdir(exist_ok=True)
    
    # 创建README
    readme_content = f"""# {book_title}

## 📚 教材简介

**定位**: [填写教材定位]  
**目标读者**: 水利类考研学生  
**内容规模**: {num_chapters}章，约XXX题

---

## 📖 目录结构

"""
    
    for i in range(1, num_chapters + 1):
        readme_content += f"### 第{i}章 [章节名称]\n\n"
    
    readme_content += """---

## 🚀 快速开始

1. 阅读各章节内容
2. 完成课后习题
3. 运行配套Python代码

---

## 💻 代码使用

```bash
cd codes
python chapter01/example01.py
```

---

## 📝 学习路径

- 基础篇：第1-3章
- 强化篇：第4-7章
- 提高篇：第8-10章

---

**创建日期**: {Path(__file__).stat().st_mtime}  
**状态**: 开发中
"""
    
    (book_dir / "README.md").write_text(readme_content, encoding='utf-8')
    print(f"[OK] 创建 README.md")
    
    # 创建章节模板
    for i in range(1, num_chapters + 1):
        chapter_file = chapters_dir / f"第{i:02d}章_[章节名称].md"
        chapter_content = f"""# 第{i}章 [章节名称]

## 本章目标

- 目标1
- 目标2
- 目标3

---

## 核心内容

### 1. 知识点1

内容...

### 2. 知识点2

内容...

---

## 典型例题

### 例题{i}.1 [题目标题]

**题目**：

[题目内容]

**解答**：

[解答过程]

**Python代码**：

```python
# 代码示例
import numpy as np
import matplotlib.pyplot as plt

# 参数设置
# ...

# 计算过程
# ...

# 可视化
plt.figure(figsize=(10, 6))
# ...
plt.show()
```

---

## 课后习题

1. [习题1]
2. [习题2]
3. [习题3]

---

## 本章小结

本章主要内容：
- 知识点1
- 知识点2
- 知识点3
"""
        
        chapter_file.write_text(chapter_content, encoding='utf-8')
        print(f"[OK] 创建 {chapter_file.name}")
    
    # 创建代码目录示例
    for i in range(1, min(4, num_chapters + 1)):
        code_dir = codes_dir / f"chapter{i:02d}"
        code_dir.mkdir(exist_ok=True)
        
        readme = code_dir / "README.md"
        readme.write_text(f"""# 第{i}章 代码示例

## 示例列表

- `example01.py` - 示例1
- `example02.py` - 示例2
""", encoding='utf-8')
        
        example_code = code_dir / "example01.py"
        example_code.write_text("""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
第X章 示例1
\"\"\"

import numpy as np
import matplotlib.pyplot as plt

def main():
    # 参数设置
    pass
    
    # 计算
    pass
    
    # 可视化
    plt.figure(figsize=(10, 6))
    plt.show()

if __name__ == "__main__":
    main()
""", encoding='utf-8')
        
        print(f"[OK] 创建 codes/chapter{i:02d}/")
    
    print(f"\n✅ 书籍目录结构创建完成！")
    print(f"\n下一步:")
    print(f"1. 编辑 {book_dir}/README.md")
    print(f"2. 填充各章节内容到 {chapters_dir}/")
    print(f"3. 运行导入脚本: python import_exam_books.py")
    print()
    
    return True


def main():
    print("\n" + "="*80)
    print("  📚 快速创建考研书籍")
    print("="*80 + "\n")
    
    # 获取用户输入
    book_slug = input("书籍目录名 (如 hydrology-exam): ").strip()
    if not book_slug:
        print("[ERROR] 目录名不能为空")
        return
    
    book_title = input("书籍标题 (如 水文学考研高分突破): ").strip()
    if not book_title:
        print("[ERROR] 标题不能为空")
        return
    
    num_chapters_str = input("章节数量 (默认10): ").strip()
    num_chapters = int(num_chapters_str) if num_chapters_str else 10
    
    # 创建目录结构
    success = create_book_structure(book_slug, book_title, num_chapters)
    
    if success:
        print(f"\n📂 书籍位置: {EXAM_PREP_DIR / book_slug}")


if __name__ == "__main__":
    main()

