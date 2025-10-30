"""
pytest配置文件

在测试运行前设置Python路径，使得可以导入books模块和项目模块。

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 添加code目录到Python路径（用于直接导入control、models等模块）
code_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../code'))
if code_dir not in sys.path:
    sys.path.insert(0, code_dir)

print(f"✓ 已添加项目根目录到Python路径: {project_root}")
print(f"✓ 已添加code目录到Python路径: {code_dir}")
