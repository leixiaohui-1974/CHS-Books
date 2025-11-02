# ❓ 常见问题解答（FAQ）

> 使用教材过程中的常见问题及解决方案

---

## 📋 目录

- [安装与环境](#安装与环境)
- [运行案例](#运行案例)
- [代码理解](#代码理解)
- [数据与配置](#数据与配置)
- [错误排查](#错误排查)
- [扩展开发](#扩展开发)
- [学习建议](#学习建议)

---

## 安装与环境

### Q1: 需要什么Python版本？

**A:** Python 3.7 或更高版本。

```bash
# 检查Python版本
python --version
# 或
python3 --version
```

推荐使用Python 3.8或3.9以获得最佳兼容性。

---

### Q2: 如何安装依赖库？

**A:** 使用pip安装：

```bash
pip install numpy scipy matplotlib pandas scikit-learn
```

或使用requirements.txt：

```bash
pip install -r requirements.txt
```

---

### Q3: 能在Windows/Mac/Linux上运行吗？

**A:** 可以！所有代码都是跨平台的。

- **Windows**: 使用CMD或PowerShell
- **Mac/Linux**: 使用终端

---

### Q4: 需要安装什么IDE吗？

**A:** 不是必需的，但推荐：

- **VSCode** - 轻量级，插件丰富
- **PyCharm** - 功能强大
- **Jupyter Notebook** - 交互式学习

也可以直接用文本编辑器+命令行。

---

## 运行案例

### Q5: 如何运行第一个案例？

**A:** 三步走：

```bash
# 1. 进入案例目录
cd code/examples/case01_frequency_analysis

# 2. 运行
python main.py

# 3. 查看结果
ls results/figures/
```

---

### Q6: 运行案例提示"找不到模块"怎么办？

**A:** 原因是Python找不到core模块。

**解决方案1**：确保在案例目录下运行
```bash
cd code/examples/case01_frequency_analysis
python main.py  # 在案例目录下运行
```

**解决方案2**：检查main.py开头是否有路径设置
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))
```

---

### Q7: 案例运行很慢怎么办？

**A:** 部分案例（如遗传算法、神经网络）计算量较大。

可以：
- 减少迭代次数（修改配置参数）
- 减少样本数量
- 使用更快的计算机
- 关闭不必要的可视化

---

### Q8: 如何跳过某些案例？

**A:** 直接跳到感兴趣的案例即可，案例间基本独立。

建议学习顺序但非强制：第1章→第2章→...

---

## 代码理解

### Q9: 代码看不懂怎么办？

**A:** 按以下顺序学习：

1. **先看README**：了解案例背景和目标
2. **看技术路线**：理解解决思路
3. **看核心算法**：掌握关键方法
4. **看main.py**：理解代码流程
5. **看注释**：理解具体实现

---

### Q10: 某个算法的原理在哪里？

**A:** 三个地方：

1. **案例README**："核心算法"部分
2. **代码注释**：函数的docstring
3. **参考文献**：README末尾的文献列表

---

### Q11: 如何快速找到某个算法的实现？

**A:** 使用PROJECT_INDEX.md或命令行：

```bash
# 使用索引文件
cat PROJECT_INDEX.md

# 或用grep搜索
grep -r "class GeneticAlgorithm" code/
```

---

## 数据与配置

### Q12: 如何使用自己的数据？

**A:** 替换data目录下的数据文件：

```bash
# 1. 查看原数据格式
cat code/examples/case01_frequency_analysis/data/runoff_data.csv

# 2. 准备相同格式的数据
# 3. 替换文件
cp your_data.csv code/examples/case01_frequency_analysis/data/runoff_data.csv

# 4. 运行
python main.py
```

---

### Q13: 如何修改参数？

**A:** 两种方式：

**方式1**：编辑配置文件（如果有）
```bash
nano data/parameters.yaml
```

**方式2**：直接修改main.py中的变量
```python
# 找到参数定义的地方
n_generations = 100  # 改为你想要的值
```

---

### Q14: 数据格式要求是什么？

**A:** 通常使用CSV格式：

- 第一行：列名
- 后续行：数据
- 分隔符：逗号
- 编码：UTF-8

示例：
```csv
year,runoff
2000,5.2
2001,6.8
...
```

---

## 错误排查

### Q15: ImportError: No module named 'numpy'

**A:** 缺少依赖库。

```bash
pip install numpy scipy matplotlib pandas scikit-learn
```

---

### Q16: FileNotFoundError: data/xxx.csv

**A:** 工作目录不对。

```bash
# 确保在案例目录下运行
cd code/examples/case01_frequency_analysis
python main.py

# 而不是
cd code/examples
python case01_frequency_analysis/main.py  # ✗ 错误
```

---

### Q17: 图表无法显示

**A:** 后端问题。

在代码开头添加：
```python
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
```

图表会保存到results/figures/目录。

---

### Q18: UnicodeDecodeError

**A:** 编码问题。

打开文件时指定编码：
```python
pd.read_csv('data.csv', encoding='utf-8')
# 或
pd.read_csv('data.csv', encoding='gbk')  # Windows中文
```

---

## 扩展开发

### Q19: 如何添加新算法？

**A:** 步骤：

1. 在对应核心模块创建新文件
2. 实现算法类或函数
3. 添加docstring
4. 在`__init__.py`中导出
5. 编写测试代码

---

### Q20: 如何创建新案例？

**A:** 参考现有案例结构：

```
new_case/
├── README.md       # 案例说明
├── main.py         # 主程序
├── data/           # 数据
└── results/        # 结果
    └── figures/
```

---

### Q21: 能否集成到自己的项目？

**A:** 可以！

```python
import sys
sys.path.insert(0, '/path/to/water-resource-planning-management/code')

from core.optimization import GeneticAlgorithm
from core.forecasting import GreyPredictor

# 使用
ga = GeneticAlgorithm(...)
```

---

## 学习建议

### Q22: 零基础能学吗？

**A:** 建议先具备：

- Python基础语法
- 基本的数学知识（线性代数、概率统计）
- 简单的水资源概念

然后从第1章开始学习。

---

### Q23: 学习顺序是什么？

**A:** 推荐路径：

**初学者**：
1. 第1章（基础）
2. 第2章（优化）
3. 第3章（控制）
4. 逐步深入

**有基础**：
- 直接学感兴趣的章节

**工程师**：
- 根据问题选择案例

---

### Q24: 每个案例需要多长时间？

**A:** 取决于深度：

- **快速浏览**：30分钟
- **理解代码**：2-3小时
- **深入掌握**：5-8小时
- **扩展应用**：1-2天

---

### Q25: 如何获得帮助？

**A:** 多种途径：

1. **查看文档**：README、FAQ等
2. **搜索问题**：Google、Stack Overflow
3. **查看源码**：代码注释很详细
4. **参考文献**：各案例的参考文献

---

## 其他问题

### Q26: 可以商业使用吗？

**A:** 可以！MIT许可证允许商业使用。

但请：
- 保留版权声明
- 适当引用来源

---

### Q27: 可以修改代码吗？

**A:** 完全可以！

鼓励：
- 根据需求修改
- 添加新功能
- 改进算法

如果愿意，欢迎分享你的改进！

---

### Q28: 有没有视频教程？

**A:** 当前版本暂无。

但文档已经很详细：
- README有技术路线
- 代码有完整注释
- 图表直观清晰

---

### Q29: 如何反馈问题？

**A:** 可以通过：

1. 提交Issue（如果有GitHub）
2. 发送邮件
3. 在代码注释中标注TODO

---

### Q30: 未来会更新吗？

**A:** 可能的更新方向：

- 修复bug
- 添加新案例
- 改进文档
- 性能优化

查看CHANGELOG.md了解更新历史。

---

## 💡 快速查找

没找到你的问题？试试：

- **查看README.md**：项目总览
- **查看QUICK_START.md**：快速开始
- **查看PROJECT_INDEX.md**：内容索引
- **查看案例README**：具体案例文档

---

**FAQ更新日期**: 2025-11-02  
**版本**: v1.0

---

🎯 **还有问题？欢迎补充到本FAQ！**
