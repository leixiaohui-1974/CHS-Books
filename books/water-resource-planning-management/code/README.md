# 代码目录说明

本目录包含教材的所有代码实现。

## 📂 目录结构

```
code/
├── core/                   # 核心模块（8个）
│   ├── hydrology/         # 水文分析
│   ├── forecasting/       # 预测方法
│   ├── decision/          # 决策分析
│   ├── optimization/      # 优化算法
│   ├── control/           # 控制理论
│   ├── ml/                # 机器学习
│   ├── digital_twin/      # 数字孪生
│   └── risk/              # 风险管理
│
└── examples/              # 案例代码（20个）
    ├── case01_frequency_analysis/
    ├── case02_runoff_forecast/
    ├── ...
    └── case20_basin_management/
```

## 🔬 核心模块

### 1. hydrology - 水文分析（825行）

**文件**：
- `frequency_analysis.py` - 频率分析
- `water_balance.py` - 水量平衡
- `data_processing.py` - 数据处理
- `statistical_tests.py` - 统计检验

**主要功能**：
- Pearson-III频率分析
- 水量平衡计算
- 缺失值插补
- 异常值检测
- 趋势检验

### 2. forecasting - 预测方法（691行）

**文件**：
- `moving_average.py` - 移动平均
- `exponential_smoothing.py` - 指数平滑
- `grey_model.py` - 灰色预测
- `arima.py` - ARIMA模型

**主要功能**：
- 时间序列预测
- 趋势分析
- 季节性分解
- 预测区间估计

### 3. decision - 决策分析（583行）

**文件**：
- `ahp.py` - 层次分析法
- `topsis.py` - TOPSIS方法
- `entropy_weight.py` - 熵权法
- `fuzzy_evaluation.py` - 模糊评价

**主要功能**：
- 多准则决策
- 权重计算
- 方案排序
- 综合评价

### 4. optimization - 优化算法（876行）

**文件**：
- `linear_programming.py` - 线性规划
- `genetic_algorithm.py` - 遗传算法
- `particle_swarm.py` - 粒子群优化
- `multi_objective.py` - 多目标优化
- `dynamic_programming.py` - 动态规划
- `stochastic_programming.py` - 随机规划

**主要功能**：
- 约束优化
- 启发式算法
- 多目标优化
- 不确定性优化

### 5. control - 控制理论（860行）

**文件**：
- `pid_controller.py` - PID控制器
- `mpc_controller.py` - 模型预测控制
- `saint_venant.py` - 圣维南方程求解

**主要功能**：
- 反馈控制
- 预测控制
- 水力模拟
- 实时优化

### 6. ml - 机器学习（919行）

**文件**：
- `neural_networks.py` - 神经网络
- `time_series.py` - 时间序列深度学习
- `anomaly_detection.py` - 异常检测

**主要功能**：
- 深度学习
- LSTM预测
- 强化学习
- 异常检测

### 7. digital_twin - 数字孪生（711行）

**文件**：
- `kalman_filter.py` - 卡尔曼滤波
- `state_estimator.py` - 状态估计
- `virtual_sensor.py` - 虚拟传感器

**主要功能**：
- 状态估计
- 数据融合
- 虚拟测量
- 实时同步

### 8. risk - 风险管理（1186行）

**文件**：
- `risk_metrics.py` - 风险度量
- `monte_carlo.py` - 蒙特卡洛模拟
- `scenario_analysis.py` - 情景分析
- `robust_optimization.py` - 鲁棒优化

**主要功能**：
- VaR/CVaR计算
- 不确定性分析
- 情景生成
- 鲁棒决策

## 📚 案例代码

每个案例包含：
- `README.md` - 详细说明文档
- `main.py` - 主程序
- `data/` - 数据和配置文件
- `src/` - 辅助模块（部分案例）
- `results/` - 结果输出目录

### 案例列表

| 编号 | 名称 | 代码量 | 难度 |
|------|------|--------|------|
| case01 | 水文频率分析 | 267行 | ⭐⭐⭐ |
| case02 | 径流预测 | 308行 | ⭐⭐⭐ |
| case03 | 水资源承载力评价 | 342行 | ⭐⭐⭐ |
| case04 | 多目标水资源分配 | 398行 | ⭐⭐⭐⭐ |
| case05 | 梯级水库优化调度 | 415行 | ⭐⭐⭐⭐ |
| case06 | 不确定性优化 | 380行 | ⭐⭐⭐⭐ |
| case07 | 渠道控制 | 256行 | ⭐⭐⭐⭐ |
| case08 | 供水管网优化调度 | 360行 | ⭐⭐⭐⭐ |
| case09 | 梯级水库实时调度 | 421行 | ⭐⭐⭐⭐ |
| case10 | 深度学习需水预测 | 382行 | ⭐⭐⭐⭐ |
| case11 | 水质异常检测 | 281行 | ⭐⭐⭐⭐ |
| case12 | 强化学习水库调度 | 339行 | ⭐⭐⭐⭐ |
| case13 | 水库数字孪生系统 | 641行 | ⭐⭐⭐⭐⭐ |
| case14 | 供水管网状态估计 | 213行 | ⭐⭐⭐⭐⭐ |
| case15 | 实时数据同化 | 282行 | ⭐⭐⭐⭐⭐ |
| case16 | 洪水风险评估 | 361行 | ⭐⭐⭐⭐ |
| case17 | 供水安全风险分析 | 402行 | ⭐⭐⭐⭐ |
| case18 | 鲁棒优化调度 | 378行 | ⭐⭐⭐⭐⭐ |
| case19 | 智能决策支持系统 | 473行 | ⭐⭐⭐⭐⭐ |
| case20 | 流域水资源综合管理 | 638行 | ⭐⭐⭐⭐⭐ |

## 🚀 使用方法

### 1. 运行案例

```bash
# 进入案例目录
cd examples/case01_frequency_analysis

# 运行主程序
python main.py
```

### 2. 导入核心模块

```python
import sys
sys.path.insert(0, 'path/to/code')

from core.hydrology import frequency_analysis
from core.optimization import GeneticAlgorithm
```

### 3. 修改参数

编辑案例目录下的配置文件：
```bash
nano data/parameters.yaml
```

### 4. 使用自己的数据

替换案例目录下的数据文件：
```bash
cp your_data.csv data/input_data.csv
```

## 📊 代码统计

```
核心模块:      7,223行
案例代码:      7,331行
总代码量:     14,554行
Python文件:       80个
算法实现:         42个
```

## 💡 代码特点

### 1. 模块化设计
- 每个模块独立
- 接口清晰
- 易于复用

### 2. 注释详细
- 函数docstring
- 行内注释
- 算法说明

### 3. 可扩展性
- 面向对象
- 参数化配置
- 易于继承

### 4. 可读性强
- 命名规范
- 结构清晰
- 逻辑简洁

## 🔧 开发建议

### 添加新算法

1. 在对应核心模块添加新文件
2. 实现算法类/函数
3. 添加docstring和注释
4. 在`__init__.py`中导出

### 创建新案例

1. 创建案例目录
2. 编写README.md
3. 实现main.py
4. 准备数据文件
5. 测试运行

### 代码规范

- 遵循PEP 8
- 使用类型提示
- 编写单元测试
- 添加详细注释

## 📞 技术支持

如有问题，请参考：
1. 各模块的docstring
2. 案例的README.md
3. 项目主README.md
4. 完整报告文档

---

**代码目录说明** | 更新日期：2025-11-02
