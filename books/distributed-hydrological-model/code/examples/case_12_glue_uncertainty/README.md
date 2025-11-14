# 案例12: GLUE不确定性分析

## 案例简介

本案例演示广义似然不确定性估计(GLUE)方法在水文模型参数不确定性分析中的应用。GLUE方法通过蒙特卡洛采样生成大量参数组合，基于模型性能识别"行为参数集"，量化模型预测的不确定性范围。该方法不依赖于参数先验分布假设，适用于高度非线性的水文模型。

## 理论背景

### GLUE方法原理

GLUE方法由Beven和Binley(1992)提出，基于以下核心思想：

1. **蒙特卡洛采样**：在参数空间内随机生成N组参数
2. **行为参数集识别**：运行模型计算似然值，保留超过阈值的参数组
3. **参数后验分布**：基于似然值构建参数的后验概率分布
4. **预测不确定性**：使用行为参数集进行预报，统计置信区间

似然函数定义为：

```
L(θ) = 1 - |NSE(θ)|  if NSE(θ) > threshold
L(θ) = 0              otherwise
```

其中NSE为Nash-Sutcliffe效率系数。

### 不确定性置信区间

对于任意时刻t的流量预测，95%置信区间为：

```
[Q_2.5%(t), Q_97.5%(t)]
```

即所有行为参数集模拟结果的2.5%和97.5%分位数。

### 参数敏感性

参数敏感性通过后验分布的方差评估：

```
Sensitivity_i = Var(θ_i | L > threshold) / Var(θ_i)
```

## 代码说明

### 主要类

1. **GLUEAnalyzer**: GLUE不确定性分析器
   - `__init__(model, param_ranges, likelihood_threshold)`: 初始化模型和参数范围
   - `run_monte_carlo(n_samples)`: 蒙特卡洛采样
   - `identify_behavioral_sets()`: 识别行为参数集
   - `compute_uncertainty_bounds(percentiles)`: 计算预测不确定性界限
   - `parameter_sensitivity()`: 参数敏感性分析

2. **XinAnJiangModel**: 新安江模型（简化版）
   - 包含蓄水容量曲线、产流计算等核心函数

### 演示函数

- `demonstrate_glue()`: 完整演示GLUE分析流程
  - 生成10000组参数样本
  - 识别NSE>0.5的行为参数集
  - 绘制参数后验分布
  - 计算90%置信区间
  - 评估参数敏感性

## 运行方法

```bash
cd /home/user/CHS-Books/books/distributed-hydrological-model/code/examples/case_12_glue_uncertainty
python main.py
```

**注意**：蒙特卡洛采样需要较长计算时间（~5-10分钟）。

## 参数说明

| 参数 | 含义 | 取值范围 | 单位 |
|------|------|----------|------|
| WM | 蓄水容量 | [80, 180] | mm |
| B | 蓄水容量曲线指数 | [0.1, 0.5] | - |
| IM | 不透水面积占比 | [0.01, 0.1] | - |
| KG | 地下水出流系数 | [0.2, 0.7] | 1/day |
| KI | 壤中流出流系数 | [0.15, 0.7] | 1/day |
| n_samples | 蒙特卡洛样本数 | 10000 | - |
| threshold | NSE阈值 | 0.5 | - |

## 预期结果说明

程序将生成以下可视化结果：

### 1. 参数后验分布图
- 5个参数的概率密度分布
- 显示参数的不确定性范围
- 峰值对应最可能的参数值

### 2. 流量过程不确定性带
- 黑线：观测流量
- 蓝色阴影：90%置信区间
- 红线：中值预测
- 包含率通常>85%

### 3. 参数敏感性雷达图
- 显示5个参数的相对敏感性
- WM和B通常最敏感
- IM敏感性相对较低

### 4. 似然值-参数散点图
- 横轴：参数值
- 纵轴：似然值
- 识别参数与性能的关系

典型输出：
- 行为参数集数量：800-1500（占8-15%）
- 90%置信区间宽度：峰值处约为均值的±30%
- 包含率：85-95%

## 工程应用

1. **洪水预报不确定性量化**：为防洪决策提供风险信息
2. **水库调度风险评估**：考虑入库流量预报的不确定性
3. **模型结构诊断**：识别模型结构性缺陷
4. **数据质量评估**：区分参数不确定性和数据误差

## 参考文献

1. Beven K, Binley A. The future of distributed models: Model calibration and uncertainty prediction[J]. Hydrological Processes, 1992, 6(3): 279-298.
2. Blasone R S, Vrugt J A, Madsen H, et al. Generalized likelihood uncertainty estimation (GLUE) using adaptive Markov Chain Monte Carlo sampling[J]. Advances in Water Resources, 2008, 31(4): 630-648.
3. 李致家, 姚成. 水文模型不确定性分析理论与方法[M]. 中国水利水电出版社, 2012.
4. Xiong L, Wan M, Wei X, et al. Indices for assessing the prediction bounds of hydrological models and application by generalised likelihood uncertainty estimation[J]. Hydrological Sciences Journal, 2009, 54(5): 852-871.
