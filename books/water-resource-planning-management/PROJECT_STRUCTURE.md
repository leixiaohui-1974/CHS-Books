# 水资源规划与管理教材 - 项目结构规划

## 完整目录结构

```
water-resource-planning-management/
│
├── README.md                           # 项目说明文档
├── 教程提纲-v1.0.md                    # 详细教材提纲
├── CASES_OVERVIEW.md                   # 案例总览
├── PROJECT_STRUCTURE.md                # 本文件：项目结构说明
├── requirements.txt                    # Python依赖列表
├── setup.py                            # 安装配置
├── LICENSE                             # 许可证
│
├── code/                               # 核心代码目录
│   │
│   ├── core/                           # 核心模块库
│   │   ├── __init__.py
│   │   ├── hydrology/                  # 水文模块
│   │   │   ├── __init__.py
│   │   │   ├── water_balance.py        # 水量平衡
│   │   │   ├── frequency_analysis.py   # 频率分析
│   │   │   ├── runoff_model.py         # 径流模型
│   │   │   └── forecast.py             # 水文预报
│   │   │
│   │   ├── optimization/               # 优化算法模块
│   │   │   ├── __init__.py
│   │   │   ├── linear_programming.py   # 线性规划
│   │   │   ├── nonlinear_programming.py # 非线性规划
│   │   │   ├── dynamic_programming.py  # 动态规划
│   │   │   ├── genetic_algorithm.py    # 遗传算法
│   │   │   ├── particle_swarm.py       # 粒子群算法
│   │   │   ├── nsga2.py                # NSGA-II
│   │   │   └── robust_optimization.py  # 鲁棒优化
│   │   │
│   │   ├── control/                    # 控制算法模块
│   │   │   ├── __init__.py
│   │   │   ├── pid_controller.py       # PID控制
│   │   │   ├── mpc_controller.py       # 模型预测控制
│   │   │   ├── fuzzy_controller.py     # 模糊控制
│   │   │   └── feedforward_control.py  # 前馈控制
│   │   │
│   │   ├── ml/                         # 机器学习模块
│   │   │   ├── __init__.py
│   │   │   ├── preprocessing.py        # 数据预处理
│   │   │   ├── regression.py           # 回归模型
│   │   │   ├── classification.py       # 分类模型
│   │   │   ├── clustering.py           # 聚类
│   │   │   ├── neural_networks.py      # 神经网络
│   │   │   ├── lstm_model.py           # LSTM
│   │   │   ├── transformer_model.py    # Transformer
│   │   │   ├── reinforcement_learning.py # 强化学习
│   │   │   └── ensemble.py             # 集成学习
│   │   │
│   │   ├── digital_twin/               # 数字孪生模块
│   │   │   ├── __init__.py
│   │   │   ├── physical_model.py       # 物理模型
│   │   │   ├── virtual_model.py        # 虚拟模型
│   │   │   ├── state_estimator.py      # 状态估计
│   │   │   ├── parameter_identifier.py # 参数识别
│   │   │   ├── data_assimilation.py    # 数据同化
│   │   │   └── virtual_sensor.py       # 虚拟传感器
│   │   │
│   │   ├── risk/                       # 风险分析模块
│   │   │   ├── __init__.py
│   │   │   ├── probability.py          # 概率分析
│   │   │   ├── copula.py               # Copula函数
│   │   │   ├── fault_tree.py           # 故障树
│   │   │   ├── bayesian_network.py     # 贝叶斯网络
│   │   │   └── resilience.py           # 韧性分析
│   │   │
│   │   ├── decision/                   # 决策支持模块
│   │   │   ├── __init__.py
│   │   │   ├── ahp.py                  # 层次分析法
│   │   │   ├── topsis.py               # TOPSIS
│   │   │   ├── electre.py              # ELECTRE
│   │   │   ├── fuzzy_evaluation.py     # 模糊评价
│   │   │   └── scenario_analysis.py    # 情景分析
│   │   │
│   │   └── utils/                      # 工具函数
│   │       ├── __init__.py
│   │       ├── data_io.py              # 数据读写
│   │       ├── time_series.py          # 时间序列处理
│   │       ├── statistics.py           # 统计函数
│   │       ├── visualization.py        # 可视化
│   │       └── gis_tools.py            # GIS工具
│   │
│   ├── examples/                       # 20个案例实现
│   │   │
│   │   ├── case01_water_resources_assessment/
│   │   │   ├── README.md
│   │   │   ├── data/
│   │   │   ├── src/
│   │   │   ├── results/
│   │   │   ├── main.py
│   │   │   └── config.yaml
│   │   │
│   │   ├── case02_water_demand_forecasting/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case03_carrying_capacity/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case04_multi_objective_allocation/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case05_cascade_reservoirs/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case06_uncertainty_allocation/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case07_single_reservoir/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case08_short_term_dispatch/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case09_rl_reservoir_dispatch/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case10_water_transfer_dispatch/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case11_canal_water_distribution/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case12_water_supply_risk/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case13_drought_risk_management/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case14_resilience_assessment/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case15_decision_support_system/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case16_deep_learning_forecasting/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case17_digital_twin_reservoirs/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case18_digital_twin_water_network/
│   │   │   └── [类似结构]
│   │   │
│   │   ├── case19_basin_comprehensive_planning/
│   │   │   └── [类似结构]
│   │   │
│   │   └── case20_smart_basin_platform/
│   │       └── [类似结构]
│   │
│   └── models/                         # 预训练模型
│       ├── lstm_runoff_forecast.pth
│       ├── transformer_demand_forecast.pth
│       ├── rl_reservoir_agent.pth
│       └── README.md
│
├── data/                               # 数据集
│   ├── README.md                       # 数据说明
│   ├── case01/                         # 案例1数据
│   ├── case02/                         # 案例2数据
│   ├── ...
│   └── case20/                         # 案例20数据
│
├── docs/                               # 文档
│   │
│   ├── zh/                             # 中文文档
│   │   ├── README.md
│   │   │
│   │   ├── chapter01/                  # 第1章
│   │   │   ├── 1.1_水资源系统概述.md
│   │   │   ├── 1.2_水资源调查与评价.md
│   │   │   ├── 1.3_需水预测方法.md
│   │   │   ├── 1.4_水资源系统建模.md
│   │   │   └── 案例详解/
│   │   │       ├── 案例1.1.md
│   │   │       ├── 案例1.2.md
│   │   │       └── 案例1.3.md
│   │   │
│   │   ├── chapter02/                  # 第2章
│   │   │   ├── 2.1_水资源配置概念.md
│   │   │   ├── 2.2_优化配置模型.md
│   │   │   ├── 2.3_求解算法.md
│   │   │   ├── 2.4_配置方案评价.md
│   │   │   └── 案例详解/
│   │   │
│   │   ├── chapter03/                  # 第3章
│   │   │   └── [类似结构]
│   │   │
│   │   ├── chapter04/                  # 第4章
│   │   │   └── [类似结构]
│   │   │
│   │   ├── chapter05/                  # 第5章
│   │   │   └── [类似结构]
│   │   │
│   │   ├── chapter06/                  # 第6章
│   │   │   └── [类似结构]
│   │   │
│   │   ├── chapter07/                  # 第7章
│   │   │   └── [类似结构]
│   │   │
│   │   └── chapter08/                  # 第8章
│   │       └── [类似结构]
│   │
│   ├── figures/                        # 图表
│   │   ├── chapter01/
│   │   ├── chapter02/
│   │   └── ...
│   │
│   ├── standards/                      # 标准规范
│   │   ├── GB_T_50429_水资源评价.pdf
│   │   ├── SL_525_水资源调度管理.pdf
│   │   └── ...
│   │
│   └── references/                     # 参考文献
│       ├── 水资源规划类.md
│       ├── 优化理论类.md
│       ├── 人工智能类.md
│       └── 数字孪生类.md
│
├── tests/                              # 测试
│   ├── __init__.py
│   ├── test_installation.py            # 安装测试
│   ├── test_core/                      # 核心模块测试
│   │   ├── test_hydrology.py
│   │   ├── test_optimization.py
│   │   ├── test_control.py
│   │   └── ...
│   └── test_examples/                  # 案例测试
│       ├── test_case01.py
│       ├── test_case02.py
│       └── ...
│
├── notebooks/                          # Jupyter教学笔记
│   ├── chapter01/
│   │   ├── 1.1_水资源评价.ipynb
│   │   ├── 1.2_需水预测.ipynb
│   │   └── 1.3_案例1实战.ipynb
│   ├── chapter02/
│   │   └── ...
│   └── tutorials/                      # 专题教程
│       ├── Python基础.ipynb
│       ├── NumPy_Pandas入门.ipynb
│       ├── 优化算法入门.ipynb
│       └── 深度学习入门.ipynb
│
├── scripts/                            # 脚本工具
│   ├── install_dependencies.sh         # 依赖安装
│   ├── download_data.sh                # 数据下载
│   ├── run_all_tests.sh                # 运行所有测试
│   └── generate_docs.sh                # 生成文档
│
├── deployment/                         # 部署配置
│   ├── docker/
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── requirements.docker.txt
│   ├── kubernetes/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── cloud/
│       ├── aws_deploy.md
│       └── azure_deploy.md
│
└── examples_extended/                  # 扩展案例（用于进一步学习）
    ├── case21_climate_change_impact/
    ├── case22_groundwater_conjunctive_use/
    ├── case23_transboundary_water_allocation/
    └── ...
```

---

## 各目录详细说明

### 1. code/core/ - 核心模块库

这是整个教材的核心代码库，提供可复用的功能模块，所有案例都基于这些模块构建。

**设计原则**：
- 模块化设计，低耦合高内聚
- 统一的接口规范
- 完整的文档字符串（docstring）
- 完善的单元测试
- 遵循PEP8代码规范

**主要模块**：
- `hydrology/`：水文计算、频率分析、径流模型、预报
- `optimization/`：各类优化算法实现
- `control/`：控制理论算法
- `ml/`：机器学习与深度学习
- `digital_twin/`：数字孪生相关技术
- `risk/`：风险分析方法
- `decision/`：决策支持方法
- `utils/`：通用工具函数

---

### 2. code/examples/ - 20个案例实现

每个案例都是一个独立的子项目，有完整的文档、数据、代码、结果。

**案例标准结构**：
```
caseXX_name/
├── README.md               # 案例说明
│   - 工程背景
│   - 问题描述
│   - 技术路线
│   - 运行方法
│   - 预期结果
│   - 思考题
│
├── data/                   # 输入数据
│   ├── input_data.csv
│   ├── parameters.yaml
│   └── README.md           # 数据说明
│
├── src/                    # 源代码
│   ├── __init__.py
│   ├── data_loader.py      # 数据加载
│   ├── model.py            # 模型定义
│   ├── solver.py           # 求解器
│   └── visualization.py    # 可视化
│
├── results/                # 输出结果
│   ├── figures/            # 图表
│   ├── tables/             # 表格
│   └── summary.txt         # 结果摘要
│
├── tests/                  # 单元测试
│   └── test_case.py
│
├── main.py                 # 主程序入口
├── config.yaml             # 配置文件
└── requirements.txt        # 案例专用依赖
```

---

### 3. data/ - 数据集

提供所有案例的完整数据，支持教学和研究。

**数据特点**：
- 真实性：基于实际工程或合理模拟
- 完整性：包含完整的输入输出数据
- 标准化：统一的数据格式（CSV、YAML、JSON、NetCDF、Shapefile）
- 文档化：每个数据集都有详细说明

**数据组织**：
```
data/
├── README.md               # 总体说明
├── case01/
│   ├── README.md           # 数据说明
│   ├── runoff_series.csv   # 径流序列
│   └── spatial_data/       # 空间数据
├── case02/
└── ...
```

---

### 4. docs/ - 教材文档

完整的教材内容，包括理论讲解、案例详解、标准规范、参考文献。

**文档结构**：
- 每章独立目录
- 小节对应独立Markdown文件
- 案例详解独立文档
- 大量插图和公式
- 引用标准规范

**文档格式**：
- Markdown格式，易于版本控制
- 支持生成PDF、HTML等格式
- 数学公式使用LaTeX语法
- 代码示例使用语法高亮

---

### 5. tests/ - 测试

全面的测试体系，保证代码质量。

**测试类型**：
- 单元测试：测试各个函数和类
- 集成测试：测试模块间交互
- 案例测试：验证案例可正常运行
- 性能测试：测试算法效率

**测试框架**：
- pytest
- unittest
- 覆盖率：目标 > 80%

---

### 6. notebooks/ - Jupyter教学笔记

交互式教学内容，适合课堂演示和自学。

**内容**：
- 理论知识讲解
- 算法原理演示
- 案例逐步实现
- 可视化结果展示
- 练习题

**特点**：
- 可在线运行（Binder、Colab）
- 支持导出为HTML、PDF
- 嵌入视频和动画

---

### 7. deployment/ - 部署配置

支持多种部署方式，便于教学和应用。

**部署方式**：
- Docker：容器化部署
- Kubernetes：集群部署
- 云平台：AWS、Azure、阿里云

**应用场景**：
- 在线教学平台
- 科研计算环境
- 工程应用系统

---

## 开发规范

### 代码规范

**Python代码**：
- 遵循PEP8规范
- 使用Black格式化
- 使用Pylint/Flake8检查
- 类型注解（Type Hints）

**文档字符串**：
```python
def calculate_water_balance(inflow: float, outflow: float, 
                           evaporation: float) -> float:
    """
    计算水量平衡
    
    Parameters
    ----------
    inflow : float
        入流量 (m³/s)
    outflow : float
        出流量 (m³/s)
    evaporation : float
        蒸发量 (m³/s)
    
    Returns
    -------
    float
        蓄变量 (m³/s)
    
    Examples
    --------
    >>> calculate_water_balance(100, 80, 5)
    15.0
    """
    return inflow - outflow - evaporation
```

### 提交规范

**Git Commit消息格式**：
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type类型**：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**：
```
feat(case01): 添加频率分析功能

- 实现P-III型曲线拟合
- 添加适线检验
- 完善可视化输出

Closes #12
```

### 版本管理

**语义化版本（Semantic Versioning）**：
- 主版本号：不兼容的API修改
- 次版本号：向后兼容的功能性新增
- 修订号：向后兼容的问题修正

**示例**：v1.2.3

---

## 技术栈总览

### 编程语言
- **Python 3.9+**（主要）
- **JavaScript/TypeScript**（Web前端）
- **SQL**（数据库）

### 核心库（Python）

**科学计算**：
```
numpy >= 1.21.0
scipy >= 1.7.0
pandas >= 1.3.0
```

**优化**：
```
pulp >= 2.5.0
pyomo >= 6.2.0
cvxpy >= 1.2.0
deap >= 1.3.0
```

**机器学习**：
```
scikit-learn >= 1.0.0
xgboost >= 1.5.0
lightgbm >= 3.3.0
```

**深度学习**：
```
tensorflow >= 2.8.0
pytorch >= 1.10.0
keras >= 2.8.0
```

**强化学习**：
```
gym >= 0.21.0
stable-baselines3 >= 1.4.0
```

**可视化**：
```
matplotlib >= 3.5.0
plotly >= 5.5.0
seaborn >= 0.11.0
```

**GIS**：
```
geopandas >= 0.10.0
shapely >= 1.8.0
rasterio >= 1.2.0
```

**水力计算**：
```
wntr >= 0.4.0  # 供水管网
```

**数据库**：
```
sqlalchemy >= 1.4.0
psycopg2 >= 2.9.0  # PostgreSQL
```

**Web框架**：
```
flask >= 2.0.0
fastapi >= 0.75.0
```

---

## 开发计划

### 阶段1：基础框架（3个月）
- [ ] 建立核心模块框架
- [ ] 完成第1-2章内容与案例1-6
- [ ] 建立测试体系
- [ ] 编写基础文档

### 阶段2：核心内容（4个月）
- [ ] 完成第3-5章内容与案例7-14
- [ ] 完善核心模块
- [ ] 扩展测试覆盖
- [ ] 编写进阶文档

### 阶段3：前沿技术（3个月）
- [ ] 完成第6-7章内容与案例15-18
- [ ] 集成AI算法
- [ ] 实现数字孪生
- [ ] 编写高级文档

### 阶段4：综合应用（2个月）
- [ ] 完成第8章内容与案例19-20
- [ ] 系统集成测试
- [ ] 性能优化
- [ ] 编写综合文档

### 阶段5：完善出版（2个月）
- [ ] 全书审校
- [ ] 视频教程录制
- [ ] 在线平台搭建
- [ ] 出版准备

---

## 贡献指南

### 如何贡献

1. **Fork项目**
2. **创建特性分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'feat: Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **开启Pull Request**

### 贡献方向

- 新增案例
- 改进算法
- 完善文档
- 修复bug
- 性能优化
- 添加测试

---

## 许可证

- **代码**：MIT License
- **文档**：CC BY-NC-SA 4.0
- **数据**：自定义许可（仅限学习研究）

---

**最后更新**：2025-11-02  
**版本号**：v1.0  
**维护者**：[待填]
