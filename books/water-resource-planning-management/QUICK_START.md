# 快速开始指南

> 5分钟上手水资源规划与管理教材

## 📋 前提条件

确保您的系统已安装：
- Python 3.7 或更高版本
- 基本的Python科学计算库

## 🚀 第一步：验证环境

```bash
# 检查Python版本
python --version

# 应该显示：Python 3.7.x 或更高
```

## 📦 第二步：安装依赖（如果需要）

```bash
# 安装必需的库
pip install numpy scipy matplotlib pandas scikit-learn

# 或者批量安装
pip install -r requirements.txt  # 如果提供了requirements.txt
```

## 🎯 第三步：运行第一个案例

### 案例1：水文频率分析

```bash
# 1. 进入案例目录
cd code/examples/case01_frequency_analysis

# 2. 运行案例
python main.py

# 3. 查看结果
# - 控制台会输出分析结果
# - results/figures/ 目录下会生成图表
```

**预期输出**：
```
============================================================
水文频率分析（Pearson-III分布）
============================================================

历史数据统计:
  样本数: 30年
  均值: 6.52 亿m³
  标准差: 1.82 亿m³
  ...

设计洪水:
  P=1%（百年一遇）: 10.23 亿m³
  P=2%（五十年一遇）: 9.45 亿m³
  ...
```

## 🎓 第四步：探索更多案例

### 推荐学习顺序

#### 1️⃣ 基础案例（第1-2章）

**案例1.2：径流预测**
```bash
cd code/examples/case02_runoff_forecast
python main.py
```
学习：移动平均、灰色预测、ARIMA

**案例2.1：多目标优化**
```bash
cd code/examples/case04_multi_objective_allocation
python main.py
```
学习：线性规划、遗传算法、NSGA-II

#### 2️⃣ 中级案例（第3-4章）

**案例3.1：渠道控制**
```bash
cd code/examples/case07_canal_control
python main.py
```
学习：PID控制、圣维南方程

**案例4.1：深度学习预测**
```bash
cd code/examples/case10_deep_learning_forecast
python main.py
```
学习：神经网络、LSTM

#### 3️⃣ 高级案例（第5-6章）

**案例5.1：数字孪生**
```bash
cd code/examples/case13_digital_twin
python main.py
```
学习：卡尔曼滤波、虚拟传感器

**案例6.1：洪水风险评估**
```bash
cd code/examples/case16_flood_risk
python main.py
```
学习：蒙特卡洛、VaR/CVaR

#### 4️⃣ 综合案例（第8章）

**案例8.1：流域综合管理（压轴）**
```bash
cd code/examples/case20_basin_management
python main.py
```
整合全部8个核心模块

## 🔍 第五步：理解案例结构

每个案例目录结构：
```
case01_frequency_analysis/
├── README.md           # 详细说明文档
├── main.py            # 主程序
├── data/              # 数据和配置
│   └── runoff_data.csv
└── results/           # 结果输出
    └── figures/       # 可视化图表
```

## 📚 第六步：深入学习

### 阅读文档

1. **案例README**：每个案例的详细说明
   ```bash
   # 在案例目录下
   cat README.md
   ```

2. **核心模块文档**：查看算法实现
   ```bash
   # 查看模块代码
   cat code/core/hydrology/frequency_analysis.py
   ```

### 修改参数

1. **编辑配置文件**（如果有）：
   ```bash
   # 案例的配置文件通常在data/目录
   nano data/parameters.yaml
   ```

2. **修改主程序**：
   ```bash
   nano main.py
   ```

### 使用自己的数据

1. **替换数据文件**：
   ```bash
   # 将您的数据保存为CSV格式
   cp your_data.csv data/runoff_data.csv
   ```

2. **运行案例**：
   ```bash
   python main.py
   ```

## 💻 第七步：使用核心模块

### 在自己的代码中使用

```python
import sys
sys.path.insert(0, 'path/to/code')

# 导入核心模块
from core.hydrology import frequency_analysis
from core.forecasting import MovingAverage
from core.optimization import GeneticAlgorithm

# 使用示例
result = frequency_analysis(data, distribution='pearson3')
```

## 🎯 常见任务

### 任务1：快速查看某个算法的实现

```bash
# 例如：查看AHP算法
cat code/core/decision/ahp.py
```

### 任务2：对比两个案例的结果

```bash
# 运行案例A
cd code/examples/case02_runoff_forecast
python main.py

# 运行案例B
cd ../case10_deep_learning_forecast
python main.py

# 对比results/figures/下的图表
```

### 任务3：测试所有案例

```bash
# 创建测试脚本（示例）
for case in code/examples/case*/; do
    echo "Testing $case"
    cd $case
    python main.py > /dev/null 2>&1 && echo "✓ Pass" || echo "✗ Fail"
    cd -
done
```

## 🐛 故障排除

### 问题1：找不到模块

**错误**：`ModuleNotFoundError: No module named 'core'`

**解决**：
```python
# 在main.py开头添加
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))
```

### 问题2：缺少依赖库

**错误**：`ModuleNotFoundError: No module named 'numpy'`

**解决**：
```bash
pip install numpy scipy matplotlib pandas scikit-learn
```

### 问题3：图表无法显示

**原因**：可能是后端问题

**解决**：
```python
# 在代码中添加
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
```

### 问题4：数据文件找不到

**原因**：工作目录不对

**解决**：
```bash
# 确保在案例目录下运行
cd code/examples/case01_frequency_analysis
python main.py
```

## 📞 获取帮助

### 查看文档

1. **项目总README**：`README.md`
2. **完整报告**：`项目100%完成-最终报告.md`
3. **使用指南**：`最终总结.md`
4. **案例文档**：各案例的`README.md`

### 学习资源

1. **代码注释**：每个函数都有详细docstring
2. **算法说明**：README中的核心算法部分
3. **参考文献**：README末尾的文献列表

## 🎉 下一步

恭喜！您已经完成了快速开始。

### 推荐学习路径：

**初学者**：
1. 按顺序学习第1-2章（基础）
2. 尝试修改参数，观察结果变化
3. 理解核心算法的实现

**有基础**：
1. 直接学习感兴趣的高级案例
2. 深入研究算法细节
3. 扩展到自己的应用

**工程师**：
1. 根据实际问题选择案例
2. 使用真实数据测试
3. 集成到实际系统

---

**快速开始完成！** 🚀

现在您可以：
- ✅ 运行任何案例
- ✅ 理解代码结构
- ✅ 修改参数和数据
- ✅ 使用核心模块

**祝学习愉快！** 🎓
