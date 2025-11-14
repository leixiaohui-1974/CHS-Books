# 案例6.3：鲁棒优化调度

## 工程背景

在入流、负荷等不确定因素下，传统确定性优化可能产生"最优但脆弱"的调度方案。鲁棒优化追求在最坏情景下仍能保持可接受性能的方案，提高系统抗风险能力。

## 案例目标

1. 理解鲁棒优化的基本思想
2. 掌握Min-Max和Min-Max Regret方法
3. 学习风险厌恶权衡
4. 能够设计鲁棒调度方案

## 主要内容

### 1. 鲁棒优化思想

**确定性优化**：
```python
min E[f(x, ξ)]
```
追求期望最优，但可能在坏情景下表现很差

**鲁棒优化**：
```python
min max_ξ f(x, ξ)
```
追求最坏情景最优，保守但稳健

### 2. 鲁棒优化方法

**Min-Max（最坏情景）**：
```python
min_x max_s∈S f(x, s)
```

**Min-Max Regret（最小后悔）**：
```python
min_x max_s∈S [f(x,s) - f^*(s)]
```

**加权鲁棒**：
```python
min_x [α*E[f(x,s)] + (1-α)*max_s f(x,s)]
```

**CVaR优化**：
```python
min_x CVaR_α[f(x,s)]
```

## 技术路线

```python
水库调度问题
  ├─ 目标：最大化发电
  ├─ 约束：水量平衡、库容
  └─ 不确定性：入流
         ↓
情景集合
  ├─ 丰水（P=30%）
  ├─ 平水（P=50%）
  └─ 枯水（P=20%）
         ↓
方法1：确定性优化
  ├─ 期望值入流
  ├─ 单一方案
  └─ 可能失效
         ↓
方法2：鲁棒优化
  ├─ Min-Max
  ├─ Min-Regret
  ├─ 加权鲁棒
  └─ CVaR优化
         ↓
性能评估
  ├─ 期望性能
  ├─ 最坏性能
  ├─ 后悔值
  └─ 稳健性
```

## 核心算法

### 1. Min-Max鲁棒优化

```python
def robust_minmax(x0, scenarios):
    def worst_case_objective(x):
        values = [f(x, s) for s in scenarios]
        return max(values)  # 最坏情景
    
    result = minimize(worst_case_objective, x0)
    return result
```python

### 2. Min-Max Regret

```python
def robust_regret(x0, scenarios):
    # 计算各情景最优值
    optimal_values = [minimize(lambda x: f(x, s), x0).fun 
                     for s in scenarios]
    
    def regret_objective(x):
        regrets = [f(x, s) - opt 
                  for s, opt in zip(scenarios, optimal_values)]
        return max(regrets)
    
    result = minimize(regret_objective, x0)
    return result
```python

### 3. 加权鲁棒

```python
def weighted_robust(x0, scenarios, alpha):
    def objective(x):
        values = [f(x, s) for s in scenarios]
        expected = np.mean(values)
        worst = max(values)
        return (1-alpha) * expected + alpha * worst
    
    result = minimize(objective, x0)
    return result
```python

## 运行方法

```bash
cd code/examples/case18_robust_dispatch
python main.py
```

## 预期结果

### 不同方法对比

**确定性优化**：
- 期望发电：1200万kWh
- 最坏发电：850万kWh（枯水）
- 后悔值：200万kWh

**Min-Max鲁棒**：
- 期望发电：1100万kWh
- 最坏发电：1050万kWh
- 后悔值：80万kWh

**Min-Regret鲁棒**：
- 期望发电：1150万kWh
- 最坏发电：980万kWh
- 后悔值：50万kWh

**加权鲁棒（α=0.3）**：
- 期望发电：1180万kWh
- 最坏发电：920万kWh
- 综合平衡

## 思考题

1. 鲁棒优化会牺牲多少期望性能？
2. 如何选择合适的风险厌恶系数α？
3. Min-Max和Min-Regret哪个更合理？
4. 鲁棒优化适用于哪些场景？
5. 如何平衡鲁棒性和经济性？

## 扩展方向

1. **分布鲁棒优化**：仅知分布信息
2. **自适应鲁棒**：两阶段决策
3. **多目标鲁棒**：Pareto前沿
4. **数据驱动鲁棒**：机器学习
5. **实时鲁棒MPC**：滚动优化

## 参考文献

1. Ben-Tal A, Nemirovski A. Robust Optimization[M]. Princeton University Press, 2009.
2. Bertsimas D, et al. Theory and Applications of Robust Optimization[J]. SIAM Review, 2011, 53(3): 464-501.

## 作者信息

- 案例编号：Case 6.3
- 难度等级：⭐⭐⭐⭐⭐ (高级)
- 所需时间：8-10小时
- 更新日期：2025-11-02
