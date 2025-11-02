# 水资源规划与管理教材

> 案例驱动 | 理论与实践结合 | 42个算法 | 20个工程案例

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Complete-success.svg)](PROJECT_COMPLETED.txt)

## 📖 项目简介

本教材是一本**完整、系统、实用**的水资源规划与管理教材，采用案例驱动的教学模式，整合了水利工程、系统工程、运筹学、控制理论、人工智能等多学科的先进理论和方法。

### 核心特色

- 🎯 **8大核心模块**：完整的技术栈
- 🔬 **42个核心算法**：从传统到AI
- 📚 **20个工程案例**：真实问题导向
- 💻 **14,000+行代码**：高质量实现
- 📊 **100+专业图表**：可视化丰富
- 📝 **详细文档**：每个案例都有完整README

## 🚀 快速开始

### 环境要求

```bash
Python >= 3.7
numpy >= 1.19.0
scipy >= 1.5.0
matplotlib >= 3.3.0
pandas >= 1.1.0
scikit-learn >= 0.23.0
```

### 安装依赖

```bash
# 进入项目目录
cd water-resource-planning-management

# 安装依赖（如果需要）
pip install numpy scipy matplotlib pandas scikit-learn
```

### 运行案例

```bash
# 进入任意案例目录
cd code/examples/case01_frequency_analysis

# 运行案例
python main.py

# 查看结果
# - 控制台会输出分析结果
# - results/figures/ 目录下会生成可视化图表
```

## 📚 目录结构

```
water-resource-planning-management/
├── code/
│   ├── core/                    # 核心模块（8个）
│   │   ├── hydrology/          # 水文分析（825行）
│   │   ├── forecasting/        # 预测方法（691行）
│   │   ├── decision/           # 决策分析（583行）
│   │   ├── optimization/       # 优化算法（876行）
│   │   ├── control/            # 控制理论（860行）
│   │   ├── ml/                 # 机器学习（919行）
│   │   ├── digital_twin/       # 数字孪生（711行）
│   │   └── risk/               # 风险管理（1186行）
│   │
│   └── examples/               # 案例代码（20个）
│       ├── case01_frequency_analysis/
│       ├── case02_runoff_forecast/
│       ├── ...
│       └── case20_basin_management/
│
├── PROJECT_COMPLETED.txt       # 项目完成标记
├── 项目100%完成-最终报告.md   # 详细完成报告
├── 最终总结.md                 # 教材使用指南
└── README.md                   # 本文件
```

## 🎓 教材内容

### 第1章：水资源评价（基础）

**案例1.1：水文频率分析**
- Pearson-III分布
- 设计洪水计算
- 重现期分析

**案例1.2：径流预测**
- 移动平均（MA）
- 灰色预测（GM）
- ARIMA模型

**案例1.3：水资源承载力评价**
- AHP层次分析
- TOPSIS评价
- 熵权法
- 模糊综合评价

### 第2章：水资源优化分配（基础-中级）

**案例2.1：多目标水资源分配**
- 线性规划（LP）
- 遗传算法（GA）
- 粒子群优化（PSO）
- NSGA-II多目标优化

**案例2.2：梯级水库优化调度**
- 动态规划（DP）
- 逐步优化算法（POA）

**案例2.3：不确定性优化**
- 随机规划（SP）
- 鲁棒优化（RO）
- 风险度量

### 第3章：水库调度与实时控制（中级）

**案例3.1：渠道控制**
- PID控制
- 圣维南方程

**案例3.2：供水管网优化调度**
- 线性规划
- 非线性规划
- 模型预测控制（MPC）

**案例3.3：梯级水库实时调度**
- MPC滚动优化
- 实时反馈控制

### 第4章：智能方法与机器学习（中级-高级）

**案例4.1：深度学习需水预测**
- 多层感知机（MLP）
- 长短期记忆网络（LSTM）
- 时间序列深度学习

**案例4.2：水质异常检测**
- 隔离森林（Isolation Forest）
- 自编码器（Autoencoder）
- 统计方法

**案例4.3：强化学习水库调度**
- Q-Learning
- 强化学习环境
- 策略优化

### 第5章：数字孪生与状态估计（高级）

**案例5.1：水库数字孪生系统**
- 卡尔曼滤波（KF）
- 物理模型
- 虚拟传感器

**案例5.2：供水管网状态估计**
- 扩展卡尔曼滤波（EKF）
- 非线性系统
- 全网状态推算

**案例5.3：实时数据同化**
- 数据同化原理
- 预测-校正循环
- 模型与观测融合

### 第6章：风险管理与鲁棒优化（高级）

**案例6.1：洪水风险评估**
- 蒙特卡洛模拟
- VaR/CVaR
- 风险-成本权衡

**案例6.2：供水安全风险分析**
- 情景分析
- 可靠性评估
- 应急预案

**案例6.3：鲁棒优化调度**
- Min-Max优化
- Min-Max Regret
- 加权鲁棒优化

### 第7章：决策支持系统（综合）

**案例7.1：智能决策支持系统**
- 方案生成
- AHP-TOPSIS评估
- 多准则决策
- 敏感性分析

### 第8章：综合案例（压轴）

**案例8.1：流域水资源综合管理**
- 整合8大核心模块
- 完整管理流程
- 6大阶段分析
- 综合决策支持

## 🔬 核心模块

### 1. hydrology - 水文分析

```python
from core.hydrology import frequency_analysis, calculate_water_balance

# 频率分析
result = frequency_analysis(data, distribution='pearson3')

# 水量平衡
balance = calculate_water_balance(supply, demand)
```

### 2. forecasting - 预测方法

```python
from core.forecasting import MovingAverage, GreyPredictor

# 移动平均
ma = MovingAverage(window=3)
forecast = ma.fit(data).predict(steps=5)

# 灰色预测
gm = GreyPredictor()
forecast = gm.fit(data).predict(steps=5)
```

### 3. decision - 决策分析

```python
from core.decision import ahp, topsis

# AHP权重
weights, cr = ahp(judgment_matrix)

# TOPSIS评估
scores, ranking = topsis(decision_matrix, weights, criteria_types)
```

### 4. optimization - 优化算法

```python
from core.optimization import GeneticAlgorithm, solve_linear_programming

# 线性规划
result = solve_linear_programming(c, A_ub, b_ub)

# 遗传算法
ga = GeneticAlgorithm(objective, n_variables, bounds)
best_x, best_fitness = ga.optimize()
```

### 5. control - 控制理论

```python
from core.control import PIDController, MPCController

# PID控制
controller = PIDController(kp=2.0, ki=0.5, kd=0.1)
output = controller.compute(current_value)

# MPC控制
mpc = MPCController(model, prediction_horizon=10)
u_optimal = mpc.compute(x_current)
```

### 6. ml - 机器学习

```python
from core.ml import NeuralNetwork, LSTMPredictor

# 神经网络
nn = NeuralNetwork(layers=[10, 20, 1])
nn.train(X_train, y_train)

# LSTM预测
lstm = LSTMPredictor(input_dim=5, hidden_dim=20)
forecast = lstm.predict(X_test)
```

### 7. digital_twin - 数字孪生

```python
from core.digital_twin import KalmanFilter, VirtualSensor

# 卡尔曼滤波
kf = KalmanFilter(dim_x=2, dim_z=1)
kf.predict()
kf.update(measurement)

# 虚拟传感器
sensor = VirtualSensor(model=physical_model)
value = sensor.measure(inputs)
```

### 8. risk - 风险管理

```python
from core.risk import MonteCarloSimulator, VaRCalculator, RobustOptimizer

# 蒙特卡洛模拟
simulator = MonteCarloSimulator()
result = simulator.simulate(model, parameters, n_simulations=10000)

# VaR计算
var_calc = VaRCalculator(confidence_level=0.95)
var = var_calc.calculate_historical(returns)

# 鲁棒优化
optimizer = RobustOptimizer(objective, constraints)
result = optimizer.optimize_worst_case(scenarios, x0)
```

## 📊 案例特色

### 完整的分析流程

每个案例都包含：
1. **工程背景**：真实问题描述
2. **技术路线**：清晰的解决思路
3. **核心算法**：详细的算法实现
4. **代码实现**：可运行的完整代码
5. **结果分析**：定量的性能评估
6. **可视化**：专业的图表展示
7. **思考题**：深入理解的引导
8. **扩展方向**：进一步研究的建议

### 多方法对比

每个案例都包含2-3种方法的对比：
- **基准方法** vs **优化方法**
- **传统方法** vs **智能方法**
- **确定性** vs **随机性**
- **单目标** vs **多目标**

## 🎯 适用对象

### 高校教学
- **本科生**：水利工程、环境工程、系统工程、计算机科学
- **研究生**：水文水资源、系统分析、人工智能、决策科学
- **博士生**：方法研究、算法开发、应用研究

### 工程应用
- **规划人员**：水资源规划、流域管理
- **调度人员**：水库调度、供水管理
- **技术人员**：系统开发、软件设计
- **管理人员**：决策支持、风险管理

### 科学研究
- **研究人员**：理论研究、方法创新
- **算法工程师**：AI应用、优化算法
- **数据科学家**：数据分析、预测建模

## 🌟 学习路径

### 初学者（建议顺序学习）

1. **第1章**：水资源评价（掌握基础方法）
2. **第2章**：优化分配（理解优化理论）
3. **第3章**：实时控制（学习控制方法）
4. **第4-6章**：高级方法（AI、数字孪生、风险）
5. **第7-8章**：综合应用（系统化思维）

### 有基础（选择性学习）

1. 直接学习感兴趣的章节
2. 重点关注算法实现细节
3. 研究对比实验结果
4. 扩展到自己的应用场景

### 工程师（问题导向）

1. 根据实际问题选择案例
2. 修改参数适配工程需求
3. 使用真实数据验证
4. 集成到实际系统

## 📈 项目统计

```
总代码量:         14,554行
核心模块:          7,223行
案例代码:          7,331行
Python文件:           80个
README文档:           20个
算法实现:             42个
可视化图表:          100+个
```

## 💡 技术亮点

### 1. 系统化设计
- 从评价→预测→优化→控制→风险→决策
- 完整的技术链条
- 模块协同应用

### 2. 智能化融合
- 传统方法与AI结合
- 物理模型与数据驱动融合
- 确定性与不确定性统一

### 3. 数字孪生技术
- 物理系统虚拟映射
- 实时状态估计
- 预测仿真一体化

### 4. 工程实用性
- 真实问题导向
- 可操作的解决方案
- 定量的评价指标

## 🔧 常见问题

### Q1: 如何运行案例？

```bash
cd code/examples/case01_frequency_analysis
python main.py
```

### Q2: 缺少依赖库怎么办？

```bash
pip install numpy scipy matplotlib pandas scikit-learn
```

### Q3: 如何修改参数？

编辑案例目录下的`data/`文件夹中的配置文件（YAML格式）。

### Q4: 如何使用自己的数据？

替换案例目录下的`data/`文件夹中的数据文件（CSV格式）。

### Q5: 如何扩展算法？

参考`code/core/`中的模块，添加新的算法实现。

## 📝 参考文献

1. Loucks DP, van Beek E. Water Resource Systems Planning and Management[M]. Springer, 2017.
2. ReVelle CS, McGarity AE. Design and Operation of Civil and Environmental Engineering Systems[M]. Wiley, 1997.
3. Wurbs RA, James WP. Water Resources Engineering[M]. Prentice Hall, 2002.
4. Bishop CM. Pattern Recognition and Machine Learning[M]. Springer, 2006.
5. Sutton RS, Barto AG. Reinforcement Learning: An Introduction[M]. MIT Press, 2018.

## 🙏 致谢

感谢所有为水资源管理事业做出贡献的前辈和同仁！

本教材参考了大量经典文献和前沿研究，整合了多个学科的先进理论和方法。

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 联系方式

如有问题或建议，欢迎交流！

---

**项目状态**: ✅ 100%完成  
**完成日期**: 2025-11-02  
**版本**: v1.0

---

🎉 **祝您学习愉快，应用成功！** 🚀
