"""
pytest配置文件
=============
自动设置正确的导入路径
"""

import sys
from pathlib import Path

# 将书籍根目录添加到路径
book_root = Path(__file__).parent.parent
sys.path.insert(0, str(book_root))
