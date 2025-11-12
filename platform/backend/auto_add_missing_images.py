# -*- coding: utf-8 -*-
"""
自动将缺失的图片添加到README中
采用1行2列表格格式，并生成基础说明
"""

import os
import sys
import io
import re
from pathlib import Path

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

# 图片说明模板
IMAGE_TEMPLATES = {
    'diagram': {
        'title': '{case}系统示意图',
        'desc': '''
**系统结构说明**

本图展示了{case}系统的整体结构：

**主要组成部分：**
- 🏗️ **控制对象**：水箱系统
- 📏 **传感器**：实时监测水位
- 🎛️ **控制器**：实现控制算法
- ⚙️ **执行器**：调节输入流量

**工作原理：**
- 传感器测量当前状态
- 控制器计算控制信号
- 执行器调节系统输入
- 系统输出达到期望值

**关键参数：**
- 系统参数：待填充
- 控制参数：待填充
'''
    },
    'control': {
        'title': '控制效果分析图',
        'desc': '''
**控制性能分析**

本图展示了控制系统的运行效果：

**上图：系统响应**
- 蓝色曲线：实际输出
- 红色虚线：目标设定值
- 跟踪效果良好

**下图：控制信号**
- 绿色曲线：控制器输出
- 显示控制动作

**性能指标：**
- 上升时间：待分析
- 超调量：待分析
- 调节时间：待分析
- 稳态误差：待分析
'''
    },
    'comparison': {
        'title': '控制方法对比图',
        'desc': '''
**多种控制方法对比分析**

本图对比了不同控制策略的性能：

**对比方法：**
- 方法1：基础控制策略
- 方法2：改进控制策略
- 方法3：高级控制策略

**对比维度：**
- 响应速度
- 控制精度
- 鲁棒性
- 实现复杂度

**结论：**
根据不同应用场景选择合适的控制方法。
'''
    },
    'tuning': {
        'title': '参数整定分析图',
        'desc': '''
**参数整定效果分析**

本图展示了不同参数对系统性能的影响：

**参数变化：**
- 参数1：影响响应速度
- 参数2：影响超调量
- 参数3：影响稳定性

**整定方法：**
- 经验法
- 试凑法
- 优化算法

**最优参数：**
根据性能指标确定最佳参数组合。
'''
    },
    'other': {
        'title': '分析图',
        'desc': '''
**系统分析**

本图展示了系统的重要特性：

**图表说明：**
- 横轴：时间或参数
- 纵轴：系统输出或性能指标

**分析要点：**
- 系统特征分析
- 性能评估
- 结论总结
'''
    }
}

def classify_image(image_name):
    """根据图片名称分类"""
    name_lower = image_name.lower()
    
    if 'diagram' in name_lower or 'schema' in name_lower or '示意图' in name_lower:
        return 'diagram'
    elif 'comparison' in name_lower or 'vs' in name_lower or '对比' in name_lower:
        return 'comparison'
    elif 'tuning' in name_lower or 'parameter' in name_lower or '整定' in name_lower:
        return 'tuning'
    elif 'control' in name_lower or 'response' in name_lower or '控制' in name_lower:
        return 'control'
    else:
        return 'other'

def generate_image_markdown(image_name, case_name):
    """生成图片的Markdown表格"""
    img_type = classify_image(image_name)
    template = IMAGE_TEMPLATES[img_type]
    
    title = template['title'].format(case=case_name)
    desc = template['desc'].format(case=case_name).strip()
    
    markdown = f'''
### 图：{title}

<table border="0">
<tr>
<td width="50%">

![{title}]({image_name})

</td>
<td width="50%">

**{title}说明**

{desc}

</td>
</tr>
</table>

'''
    return markdown

def add_missing_images_to_readme(case_path, missing_images):
    """将缺失的图片添加到README"""
    readme_path = case_path / "README.md"
    
    if not readme_path.exists():
        print(f"  ⚠️ README不存在，跳过")
        return False
    
    # 读取原README
    content = readme_path.read_text(encoding='utf-8')
    
    # 查找合适的插入位置（在最后一个##标题之前）
    # 通常在"下一步学习"或"相关资源"之前
    markers = ['## ⏭️ 下一步学习', '## 🔗 相关资源', '## 💡 讨论与思考']
    insert_pos = len(content)
    
    for marker in markers:
        pos = content.find(marker)
        if pos != -1 and pos < insert_pos:
            insert_pos = pos
    
    # 如果没找到标记，就插入到文件末尾前
    if insert_pos == len(content):
        insert_pos = len(content.rstrip()) + 2
    
    # 生成案例名称
    case_name = case_path.name.replace('case_', '案例').replace('_', ' ')
    
    # 生成所有缺失图片的Markdown
    new_content = ""
    for img in missing_images:
        new_content += generate_image_markdown(img, case_name)
    
    # 插入新内容
    new_readme = content[:insert_pos] + "\n" + new_content + "\n" + content[insert_pos:]
    
    # 写回文件
    readme_path.write_text(new_readme, encoding='utf-8')
    
    return True

def fix_case(case_id):
    """修复单个案例"""
    case_pattern = f"case_{case_id:02d}_*"
    case_dirs = list(CASES_DIR.glob(case_pattern))
    
    if not case_dirs:
        print(f"❌ 案例{case_id:02d}不存在")
        return False
    
    case_path = case_dirs[0]
    print(f"\n正在处理: 案例{case_id:02d} - {case_path.name}")
    
    # 获取所有图片文件
    image_files = [img.name for img in case_path.glob("*.png")]
    
    # 获取README中已有的图片
    readme_path = case_path / "README.md"
    if not readme_path.exists():
        print("  ⚠️ README不存在")
        return False
    
    content = readme_path.read_text(encoding='utf-8')
    pattern1 = r'!\[.*?\]\((.*?\.png)\)'
    pattern2 = r'<img\s+src="(.*?\.png)"'
    readme_images = list(set(re.findall(pattern1, content) + re.findall(pattern2, content)))
    
    # 找出缺失的图片
    missing = [img for img in image_files if img not in readme_images]
    
    if not missing:
        print("  ✅ 无缺失图片")
        return True
    
    print(f"  📝 发现{len(missing)}张缺失图片: {', '.join(missing)}")
    
    # 添加缺失图片
    if add_missing_images_to_readme(case_path, missing):
        print(f"  ✅ 已添加{len(missing)}张图片到README")
        return True
    else:
        print(f"  ❌ 添加失败")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("自动添加缺失图片到README")
    print("=" * 80)
    
    # 需要修复的案例列表
    cases_to_fix = [2, 3, 4, 8, 9, 10, 11, 16, 17, 18, 19, 20]
    
    success_count = 0
    fail_count = 0
    
    for case_id in cases_to_fix:
        if fix_case(case_id):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 80)
    print("修复完成！")
    print("=" * 80)
    print(f"\n✅ 成功: {success_count}个案例")
    print(f"❌ 失败: {fail_count}个案例")
    print(f"\n总计: {success_count + fail_count}个案例处理完成")

if __name__ == "__main__":
    main()



