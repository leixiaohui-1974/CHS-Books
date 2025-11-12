# 快速开始指南

**5分钟上手《Python编程实战》**

---

## 🚀 第一步：环境配置

### 安装Python

```bash
# Windows用户
# 1. 访问 python.org
# 2. 下载Python 3.8+
# 3. 安装时勾选"Add Python to PATH"

# Mac/Linux用户
# 通常已预装Python
python3 --version
```

### 安装依赖

```bash
# 安装核心库
pip install numpy matplotlib pandas scipy sympy

# 或使用requirements.txt（如果提供）
pip install -r requirements.txt
```

---

## 📝 第二步：运行第一个程序

### 方式1：命令行运行

```bash
# 进入代码目录
cd codes/part1_basics

# 运行第一个项目
python project_01_data_types.py
```

**预期输出**:
```
╔══════════════════════════════════════════════════════════╗
║               Python数据类型工程应用                ║
║            案例：流域水文站网数据管理              ║
╚══════════════════════════════════════════════════════════╝

1. 基本数据类型演示
============================================================
...
```

### 方式2：Jupyter Notebook

```bash
# 启动Jupyter
jupyter notebook

# 在浏览器中打开
# notebooks/part1_basics/Notebook_01_数据类型.ipynb
```

---

## 💡 第三步：理解代码结构

### 典型项目结构

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目标题

课程目标：
1. 目标1
2. 目标2
...

工程案例：
案例描述

作者：Python编程实战教材组
日期：2025-11-12
"""

# 导入库
import numpy as np

# 定义函数
def function_name():
    """函数说明"""
    pass

# 工程案例
def engineering_example():
    """工程案例"""
    pass

# 主函数
def main():
    """主函数"""
    # 调用各个函数
    pass

# 程序入口
if __name__ == "__main__":
    main()
```

---

## 🎯 第四步：修改和实践

### 实践1：修改参数

```python
# 原代码
water_level = 125.68

# 修改为自己的数据
water_level = 130.0  # 改成其他值试试
```

### 实践2：添加功能

```python
# 在原代码基础上添加
def my_function():
    """我自己的函数"""
    # 你的代码
    pass
```

### 实践3：完整项目

```python
# 参考教材代码，编写自己的项目
# 例如：管理你所在地区的水文站数据
```

---

## 📚 第五步：系统学习

### 学习路线

```
Week 1: 项目1-2  → Python基础语法
Week 2: 项目3-4  → 函数与文件
Week 3: 项目5    → 面向对象
Week 4: 项目6-10 → 科学计算库
```

### 学习方法

1. **看**: 阅读代码和注释
2. **运行**: 执行代码，观察输出
3. **改**: 修改参数，观察变化
4. **写**: 自己编写类似程序
5. **问**: 遇到问题及时查资料

---

## 🛠️ 常见问题

### Q: 运行出错怎么办？

```bash
# 检查Python版本
python --version  # 应该是3.8+

# 检查库是否安装
pip list | grep numpy

# 重新安装库
pip install --upgrade numpy
```

### Q: 中文显示乱码？

```python
# 在代码开头添加
# -*- coding: utf-8 -*-

# Matplotlib中文显示
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
```

### Q: 找不到文件？

```bash
# 确保在正确的目录
pwd  # Linux/Mac
cd    # Windows

# 使用绝对路径
python /完整路径/project_01_data_types.py
```

---

## 🎓 学习资源

### 必读文档

- `README.md` - 教材总览
- `LEARNING_GUIDE.md` - 学习指南
- `PROJECT_OUTLINE.md` - 项目大纲

### 推荐阅读

- Python官方教程: docs.python.org
- NumPy文档: numpy.org
- Matplotlib画廊: matplotlib.org/gallery

---

## 🎉 你已经准备好了！

现在你可以：

✅ 运行教材代码  
✅ 理解代码结构  
✅ 修改和实践  
✅ 开始系统学习  

**下一步**: 运行 `project_02_control_flow.py`

**祝学习愉快！** 🚀

---

*快速开始指南 v1.0*  
*更新时间: 2025-11-12*
