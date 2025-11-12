#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为缺失README的案例批量生成模板
"""
import sys
import io
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json
from pathlib import Path
from datetime import datetime

def generate_readme_template(title, case_id, category="控制系统"):
    """生成README模板"""
    template = f"""# {title}

**难度等级**: ⭐⭐⭐ 中级  
**学习时间**: 4-6学时  
**前置知识**: Python基础、数学基础  
**案例类别**: {category}

---

## 📖 案例背景

### 实际应用场景

（请补充实际应用场景描述，300-500字）

本案例针对...的实际需求，设计并实现了...系统。该系统在...领域具有重要应用价值。

### 面临的挑战

- 挑战1: （待补充）
- 挑战2: （待补充）
- 挑战3: （待补充）

---

## 🎯 学习目标

完成本案例后，你将能够：

- [ ] 理解...的基本原理
- [ ] 掌握...的设计方法
- [ ] 实现...的控制算法
- [ ] 分析...的性能指标

---

## 🔬 理论基础

### 核心概念

（请补充核心理论说明，500-800字）

#### 数学模型

```
（请补充数学公式）
```

### 系统示意图

![系统示意图](diagram.png)

*图说明: （请补充图片说明）*

---

## 💻 代码实现

### 快速开始

```bash
cd {case_id}
python main.py
```

### 核心代码说明

（请补充代码实现说明，500-800字）

```python
# 关键代码片段
# （请补充）
```

### 参数配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| param1 | 待补充 | 0.0 |
| param2 | 待补充 | 0.0 |

---

## 📊 实验结果

### 运行结果

（请补充实验结果描述，300-500字）

### 结果图表

![实验结果1](results/result1.png)
![实验结果2](results/result2.png)

*图说明: （请补充图片说明）*

### 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 指标1 | 待补充 | 待补充 |
| 指标2 | 待补充 | 待补充 |

---

## 💡 讨论与思考

### 优点

- ✅ 优点1: （待补充）
- ✅ 优点2: （待补充）

### 局限性

- ❌ 局限1: （待补充）
- ❌ 局限2: （待补充）

### 改进方向

1. 改进方向1: （待补充）
2. 改进方向2: （待补充）

### 思考题

**Q1**: （请补充思考题）

<details>
<summary>点击查看答案</summary>
（待补充答案）
</details>

**Q2**: （请补充思考题）

<details>
<summary>点击查看答案</summary>
（待补充答案）
</details>

---

## 🔗 相关资源

### 代码文件

- `main.py` - 主程序
- `config.py` - 配置文件（如有）
- `utils.py` - 工具函数（如有）

### 相关案例

- 前置案例: （待补充）
- 后续案例: （待补充）

### 参考文献

1. （待补充参考文献）
2. （待补充参考文献）

---

## ⏭️ 下一步学习

建议按以下顺序学习：

1. 完成本案例代码运行
2. 修改参数观察变化
3. 完成思考题
4. 学习下一个案例: （待补充）

---

**状态**: 🚧 模板待完善  
**最后更新**: {datetime.now().strftime('%Y-%m-%d')}  
**完善进度**: 0%

---

*注：本README使用模板生成，请根据实际情况完善内容。*
"""
    return template

def main():
    print("\n" + "="*80)
    print("  📝 批量生成README模板")
    print("="*80 + "\n")
    
    # 读取测试报告
    report_file = Path(__file__).parent.parent / "all_236_cases_test_report.json"
    if not report_file.exists():
        print("❌ 未找到测试报告文件")
        return
    
    with open(report_file, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # 找出需要补充README的案例
    cases_to_fix = []
    for result in report['results']:
        checks = result.get('checks', {})
        readme_check = checks.get('readme', {})
        
        if readme_check.get('status') != 'pass':
            cases_to_fix.append({
                'id': result['case_id'],
                'title': result['title']
            })
    
    print(f"找到 {len(cases_to_fix)} 个需要补充README的案例\n")
    
    # 询问是否生成
    print("将为以下案例生成README模板:")
    for i, case in enumerate(cases_to_fix[:10], 1):
        print(f"  {i}. {case['title']}")
    if len(cases_to_fix) > 10:
        print(f"  ... 还有 {len(cases_to_fix)-10} 个")
    
    print("\n📝 生成模板文件到当前目录的 'readme_templates' 文件夹")
    
    # 创建输出目录
    output_dir = Path(__file__).parent.parent / "readme_templates"
    output_dir.mkdir(exist_ok=True)
    
    # 生成模板
    generated_count = 0
    for case in cases_to_fix:
        case_id = case['id']
        title = case['title']
        
        # 生成文件名
        filename = f"{case_id}_README.md"
        filepath = output_dir / filename
        
        # 生成内容
        content = generate_readme_template(title, case_id)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        generated_count += 1
    
    print(f"\n✅ 成功生成 {generated_count} 个README模板")
    print(f"📁 保存位置: {output_dir}")
    
    # 生成统计文件
    stats_file = output_dir / "_generation_stats.md"
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write(f"# README模板生成统计\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**生成数量**: {generated_count}\n\n")
        f.write(f"## 待完善案例列表\n\n")
        for i, case in enumerate(cases_to_fix, 1):
            f.write(f"{i}. {case['title']} (`{case['id']}`)\n")
    
    print(f"📄 统计文件: {stats_file}")
    
    print("\n" + "="*80)
    print("  ✅ 模板生成完成")
    print("="*80)
    
    print("\n💡 下一步:")
    print("  1. 查看生成的模板文件")
    print("  2. 根据实际案例内容填充模板")
    print("  3. 将完成的README复制到对应案例目录")
    print("  4. 重新运行测试验证")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 操作被用户中断")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

