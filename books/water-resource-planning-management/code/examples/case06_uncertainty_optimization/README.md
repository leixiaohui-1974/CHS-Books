# 案例2.3：考虑不确定性的水资源配置

## 工程背景

在实际水资源配置中，径流、需水量等参数存在显著的不确定性。传统确定性优化方法无法充分应对这些不确定性，可能导致配置方案的风险过高或经济性差。本案例探讨如何在不确定性条件下进行水资源优化配置。

## 案例目标

1. 理解不确定性对水资源配置的影响
2. 掌握随机规划的基本原理
3. 学习鲁棒优化方法
4. 能够进行情景分析和风险评估

## 主要内容

### 1. 不确定性来源

**径流不确定性**：
- 年际变化大
- 气候变化影响
- 预测误差

**需水不确定性**：
- 经济发展波动
- 人口增长变化
- 政策调整影响

**系统不确定性**：
- 工程可靠性
- 水质变化
- 运行损失

### 2. 问题描述

**基本配置问题**（案例2.1的扩展）：
- 3个水源（地表水、地下水、再生水）
- 4个用户（城市、工业、农业、生态）

**不确定参数**：
- 径流：正态分布 N(μ, σ)
- 需水：情景离散分布
- 成本：区间不确定性

**决策目标**：
- 经济效益最大化
- 风险最小化
- 鲁棒性最优

### 3. 方法对比

| 方法 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| 确定性优化 | 参数已知 | 简单、最优 | 忽略不确定性 |
| 随机规划 | 概率分布已知 | 期望最优 | 计算复杂 |
| 鲁棒优化 | 仅知范围 | 最坏情况优 | 过于保守 |
| 情景分析 | 有限情景 | 直观易懂 | 情景选择难 |

## 技术路线

```python
不确定性建模
  ├─ 径流不确定性（正态分布）
  ├─ 需水不确定性（情景）
  └─ 成本不确定性（区间）
         ↓
方法1：确定性优化（基准）
  ├─ 均值参数
  ├─ LP求解
  └─ 单一方案
         ↓
方法2：随机规划（Two-Stage）
  ├─ 第一阶段：配置容量
  ├─ 第二阶段：实际调度
  ├─ 期望值最优
  └─ 蒙特卡洛采样
         ↓
方法3：鲁棒优化
  ├─ 最坏情况
  ├─ 不确定集合
  ├─ min-max优化
  └─ 保守方案
         ↓
方法4：情景分析
  ├─ 丰水年
  ├─ 平水年
  ├─ 枯水年
  └─ 方案比较
         ↓
风险评估
  ├─ CVaR计算
  ├─ 可靠性分析
  ├─ 敏感性分析
  └─ 决策建议
```

## 数据说明

### 输入数据

**uncertainty_parameters.yaml** - 不确定性参数
- runoff_uncertainty: 径流不确定性（均值、标准差）
- demand_scenarios: 需水情景（概率、值）
- cost_ranges: 成本区间

**base_config.yaml** - 基础配置
- 水源能力
- 基准需水
- 基准成本

### 输出结果

- `deterministic_solution.csv` - 确定性方案
- `stochastic_solution.csv` - 随机规划方案
- `robust_solution.csv` - 鲁棒方案
- `scenario_analysis.csv` - 情景分析
- `risk_assessment.csv` - 风险评估
- `figures/` - 可视化图表

## 运行方法

```bash
cd code/examples/case06_uncertainty_optimization
python main.py
```python

## 核心算法

### 1. 两阶段随机规划

**数学模型**：
```
min E[c₁ᵀx + E_ξ[Q(x, ξ)]]
s.t. A₁x ≥ b₁
     x ≥ 0
```python

其中：
- x: 第一阶段决策（配置容量）
- Q(x, ξ): 第二阶段目标函数值
- ξ: 随机参数（径流、需水）

**求解方法**：
- 样本平均近似（SAA）
- 蒙特卡洛采样
- 情景树生成

**Python实现**：
```python
# 生成N个情景
scenarios = []
for i in range(N):
    runoff = np.random.normal(mu, sigma)
    demand = sample_demand()
    scenarios.append((runoff, demand))

# 求解期望问题
def expected_objective(x):
    total = first_stage_cost(x)
    for prob, scenario in scenarios:
        total += prob * second_stage_cost(x, scenario)
    return total

optimize(expected_objective)
```python

### 2. 鲁棒优化

**数学模型**：
```
min  max  cᵀx
 x  ξ∈U
s.t. A(ξ)x ≥ b(ξ), ∀ξ ∈ U
     x ≥ 0
```python

其中：
- U: 不确定集合（区间、椭球）
- 目标：最坏情况最优

**不确定集合**：
- 盒式：ξᵢ ∈ [ξᵢ⁻, ξᵢ⁺]
- 椭球：‖Σ⁻¹/²(ξ - μ)‖ ≤ Ω
- 多面体：Dξ ≤ d

**Python实现**：
```python
# 最坏情况枚举
worst_cost = -np.inf
for ξ in uncertainty_set:
    cost = objective(x, ξ)
    if cost > worst_cost:
        worst_cost = cost
        worst_scenario = ξ

minimize(worst_cost)
```python

### 3. CVaR风险度量

**条件风险价值**：
```
CVaR_α(X) = E[X | X ≥ VaR_α(X)]
```python

其中：
- VaR: 在险价值（分位数）
- α: 置信水平（如95%）

**计算方法**：
```python
# 1. 计算所有情景的损失
losses = [loss(x, scenario) for scenario in scenarios]

# 2. 排序找到VaR
losses_sorted = np.sort(losses)
VaR = np.percentile(losses, 95)

# 3. 计算CVaR
CVaR = np.mean([l for l in losses if l >= VaR])
```

### 4. 情景分析

**典型情景**：
- 丰水年（P=25%）：径流+20%
- 平水年（P=50%）：径流正常
- 枯水年（P=25%）：径流-20%

**评估指标**：
- 各情景下的经济效益
- 缺水风险
- 方案稳健性

## 预期结果

### 方案对比

| 方法 | 期望效益 | 标准差 | 最坏情况 | 可靠性 |
|------|---------|--------|---------|--------|
| 确定性 | 1800 | 350 | 1200 | 85% |
| 随机规划 | 1750 | 280 | 1300 | 90% |
| 鲁棒优化 | 1650 | 180 | 1450 | 95% |

**权衡分析**：
- 确定性：期望最优，但风险大
- 随机规划：平衡期望和风险
- 鲁棒：最安全，但收益低

### 风险分析

**CVaR分析**（α=95%）：
- 确定性方案：CVaR = 1150
- 随机规划：CVaR = 1280
- 鲁棒方案：CVaR = 1420

**结论**：鲁棒方案在极端情况下表现最好

## 思考题

1. 为什么需要考虑不确定性？确定性优化有什么局限？
2. 随机规划和鲁棒优化的区别是什么？
3. CVaR相比VaR有什么优势？
4. 如何选择合适的不确定性建模方法？
5. 实际工程中如何获取不确定性参数？

## 扩展方向

1. **分布鲁棒优化**：考虑分布本身的不确定性
2. **多阶段规划**：滚动优化、信息更新
3. **机会约束**：约束满足概率要求
4. **实物期权**：灵活性价值评估
5. **深度学习**：端到端不确定性决策

## 参考文献

1. Birge JR, Louveaux F. Introduction to Stochastic Programming[M]. Springer, 2011.
2. Ben-Tal A, Nemirovski A. Robust Optimization[M]. Princeton University Press, 2009.
3. Rockafellar RT, Uryasev S. Optimization of Conditional Value-at-Risk[J]. Journal of Risk, 2000.
4. 郭晓军. 水资源系统不确定性优化方法[M]. 科学出版社, 2015.

## 作者信息

- 案例编号：Case 2.3
- 难度等级：⭐⭐⭐⭐⭐ (高级)
- 所需时间：6-8小时
- 更新日期：2025-11-02
