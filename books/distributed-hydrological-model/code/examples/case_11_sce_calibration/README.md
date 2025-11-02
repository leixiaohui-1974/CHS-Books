# 案例11：SCE-UA参数率定算法

**难度等级**: ⭐⭐⭐  
**预计学习时间**: 4小时  
**前置知识**: 案例4（新安江模型），案例9（敏感性分析），优化算法基础

---

## 📋 案例概述

本案例演示**SCE-UA（Shuffled Complex Evolution - University of Arizona）算法**在水文模型参数自动率定中的应用。

### 学习目标

- 理解参数率定的必要性和挑战
- 掌握SCE-UA算法原理
- 学会设计目标函数
- 理解复合体进化过程
- 掌握率定结果分析方法

### 案例特色

✨ **全局优化**：避免陷入局部最优  
✨ **鲁棒性强**：适合高维非凸问题  
✨ **自动率定**：无需人工干预  
✨ **可视化完整**：4种专业图表  
✨ **工程实用**：广泛应用于水文模型

---

## 🎯 核心内容

### 1. 参数率定问题

**什么是参数率定？**

通过观测数据，寻找使模型模拟结果与观测最接近的参数值。

**数学表达**:
```
min  f(θ) = ||Y_obs - Y_sim(θ)||
 θ

s.t. θ_min ≤ θ ≤ θ_max
```

**挑战**:
- 高维搜索空间
- 目标函数非凸
- 多个局部最优解
- 参数相互作用

### 2. SCE-UA算法原理

**算法特点**:
- 结合随机搜索和确定性搜索
- 竞争复合体进化（CCE）
- 适合水文模型特点

**核心步骤**:

1. **初始化种群**（拉丁超立方采样）
```
P = {θ₁, θ₂, ..., θₙ}
n = m × p  (m个复合体，每个p个点)
```

2. **划分复合体**（按序号分配）
```
C₁ = {θ₁, θ_{m+1}, θ_{2m+1}, ...}
C₂ = {θ₂, θ_{m+2}, θ_{2m+2}, ...}
...
```

3. **复合体进化**（CCE）
   - 选择子复合体（三角分布）
   - Nelder-Mead simplex演化
   - 替换最差点

4. **复合体混合**（Shuffling）
   - 合并所有复合体
   - 重新排序
   - 重新划分

5. **收敛判断**
   - 目标函数变化 < 容差
   - 达到最大迭代次数

### 3. 拉丁超立方采样

**LHS原理**:
- 将每个参数范围划分为n个区间
- 在每个区间随机采样一次
- 随机排列组合

**优势**:
- 覆盖整个参数空间
- 比随机采样更均匀
- 初始种群多样性好

### 4. Nelder-Mead算法

**Simplex操作**:
1. **反射**：质心对称
```
θ_r = θ_c + α(θ_c - θ_worst)
α = 1
```

2. **收缩**：向质心靠拢
```
θ_s = θ_c + β(θ_worst - θ_c)
β = 0.5
```

### 5. 目标函数设计

**常用指标**:

1. **NSE（Nash-Sutcliffe Efficiency）**:
```
NSE = 1 - Σ(Q_obs - Q_sim)² / Σ(Q_obs - Q̄_obs)²
```
- 最大化
- 范围：(-∞, 1]
- 1为完美

2. **RMSE（均方根误差）**:
```
RMSE = √(Σ(Q_obs - Q_sim)² / n)
```
- 最小化

3. **多目标函数**:
```
F = w₁×NSE + w₂×(1-RMSE_norm) + w₃×PBias
```

---

## 💻 代码实现

### 1. 目标函数包装

```python
def create_calibration_objective(rainfall, EM, observed, 
                                 param_names, fixed_params):
    def objective(params_array):
        # 组装参数
        params = fixed_params.copy()
        for i, name in enumerate(param_names):
            params[name] = params_array[i]
        
        # 运行模型
        model = XinAnJiangModel(params)
        results = model.run(rainfall, EM)
        simulated = results['R']
        
        # 计算NSE
        nse = 1 - sum((observed - simulated)**2) / sum((observed - mean(observed))**2)
        
        return nse  # 最大化
    
    return objective
```

### 2. SCE-UA优化

```python
optimizer = SCEUA(
    objective_func=objective_func,
    bounds=bounds,
    n_complexes=2,
    n_points_per_complex=8
)

result = optimizer.optimize(
    max_iterations=20,
    tolerance=1e-4,
    verbose=True
)
```

### 3. 结果分析

```python
best_params = result['best_params']
best_score = result['best_score']  # NSE
n_iterations = result['n_iterations']
converged = result['converged']
```

---

## 📊 实验结果

### 率定设置
- 数据长度：365天
- 待率定参数：WM, B
- 参数维度：2
- 种群大小：16
- 复合体数：2
- 最大迭代：20次

### 率定结果
- 初始NSE：约-0.5
- 率定NSE：0.82
- 迭代次数：3次
- 收敛状态：是

### 参数对比

| 参数 | 真实值 | 初始值 | 率定值 | 误差 |
|------|--------|--------|--------|------|
| WM   | 120.0  | 140.0  | 172.8  | 44.0% |
| B    | 0.35   | 0.30   | 0.50   | 42.9% |

**说明**:
- NSE显著提升（-0.5 → 0.82）
- 参数恢复误差较大是正常的
- 水文模型参数通常存在等效性

---

## 🎨 可视化说明

### 1. 率定收敛过程 (`calibration_progress.png`)
- 横轴：迭代次数
- 纵轴：目标函数值（NSE）
- 展示快速收敛过程
- 标注最终值

### 2. 参数演变过程 (`parameter_evolution.png`)
- 每个参数一个子图
- 展示参数搜索轨迹
- 对比真实值（红色虚线）
- 标注最终误差

### 3. 模拟对比图 (`simulation_comparison.png`)
- 上图：时间序列对比
  - 降雨（倒置柱状图）
  - 观测径流（黑色）
  - 初始模拟（蓝色虚线）
  - 率定模拟（红色）
- 下图：散点对比
  - 初始参数（蓝点）
  - 率定参数（红点）
  - 1:1线
  - NSE值标注

### 4. 参数对比柱状图 (`parameter_comparison.png`)
- 初始值（浅蓝）
- 率定值（浅红）
- 真实值（浅绿）
- 数值标签

---

## 💡 工程应用

### 1. 模型参数优化

**适用场景**:
- 新安江模型率定
- SWAT模型率定
- HEC-HMS模型率定
- 任何需要参数优化的水文模型

**优势**:
- 自动化
- 全局搜索
- 鲁棒性强

### 2. 多目标优化

**组合目标函数**:
```python
F = 0.5×NSE + 0.3×(1-PBIAS/100) + 0.2×LogNSE
```

**权重选择**:
- 洪峰精度：增大NSE权重
- 水量平衡：增大PBIAS权重
- 低流模拟：增大LogNSE权重

### 3. 不确定性分析

**参数不确定性**:
- 保存所有Pareto最优解
- 分析参数分布
- 估计置信区间

---

## 📝 练习题

### 基础练习

1. **理解算法**:
   - 解释SCE-UA中"Shuffled"的含义
   - 说明复合体数量和种群大小的关系
   - 解释为什么使用拉丁超立方采样

2. **参数设置**:
   - 将复合体数改为3，观察效果
   - 将迭代次数改为50，观察收敛
   - 调整容差到1e-3，比较结果

3. **目标函数**:
   - 改用RMSE作为目标函数
   - 尝试多目标函数（NSE+RMSE）
   - 分析不同目标函数的效果

### 进阶练习

1. **更多参数**:
   - 率定4个参数（WM, B, KI, KG）
   - 分析计算时间变化
   - 比较参数恢复精度

2. **实际数据**:
   - 使用真实流域观测数据
   - 进行参数率定
   - 验证模拟精度

3. **算法对比**:
   - 实现遗传算法
   - 实现粒子群算法
   - 对比三种算法性能

### 挑战练习

1. **多目标SCE-UA**:
   - 实现Pareto前沿搜索
   - 可视化Pareto解集
   - 分析参数权衡关系

2. **自适应参数**:
   - 实现自适应复合体数
   - 动态调整进化步数
   - 提高收敛效率

3. **并行计算**:
   - 并行评估种群
   - 使用multiprocessing
   - 分析加速效果

---

## 🔍 常见问题

### Q1: SCE-UA与遗传算法有何区别？

**A**: 主要区别：

| 方面 | SCE-UA | 遗传算法 |
|------|--------|---------|
| 搜索策略 | 复合体进化 | 遗传操作 |
| 局部搜索 | Nelder-Mead | 无 |
| 混合机制 | Shuffling | 交叉 |
| 收敛速度 | 较快 | 较慢 |
| 适用性 | 水文模型 | 通用 |

### Q2: 如何选择复合体数量？

**A**: 经验准则：

```
m = max(2, min(5, n_params // 2))
```

- 参数少（<5）：m=2
- 参数中等（5-10）：m=3-4
- 参数多（>10）：m=5

### Q3: 为什么率定参数与真值差异大？

**A**: 原因：

1. **参数等效性**：不同参数组合可能产生相似结果
2. **数据误差**：观测误差导致参数偏移
3. **模型结构**：模型简化导致参数补偿
4. **目标函数**：单一目标无法约束所有参数

解决方法：
- 多目标函数
- 先验信息约束
- 正则化

### Q4: 如何判断率定结果可靠？

**A**: 检查项：

1. **模拟精度**：NSE > 0.7
2. **水量平衡**：PBIAS < 10%
3. **物理合理性**：参数在合理范围
4. **稳定性**：多次率定结果一致
5. **验证期**：验证期NSE > 0.6

---

## 📚 参考资料

### 经典文献

1. **Duan et al. (1992)**. "Effective and efficient global optimization for conceptual rainfall-runoff models." *Water Resources Research*, 28(4), 1015-1031.
   - SCE-UA算法原始论文

2. **Duan et al. (1994)**. "Optimal use of the SCE-UA global optimization method for calibrating watershed models." *Journal of Hydrology*, 158(3-4), 265-284.
   - SCE-UA在水文模型中的应用

3. **Vrugt et al. (2003)**. "Shuffled complex evolution Metropolis algorithm for optimization and uncertainty assessment of hydrologic model parameters." *Water Resources Research*, 39(8).
   - SCE-UA的改进版本（SCEM-UA）

### 中文教材

1. **李致家等 (2012)**. 《流域水文模型》. 中国水利水电出版社.
   - 第8章：参数率定方法

2. **芮孝芳 (2004)**. 《水文学原理》. 中国水利水电出版社.
   - 水文模型参数识别

### 软件工具

- **PEST** - 参数估计工具
- **SPOTPY** - Python参数优化库
- **pyswarm** - Python粒子群优化

---

## ✅ 学习检查清单

- [ ] 理解参数率定的必要性
- [ ] 掌握SCE-UA算法流程
- [ ] 理解拉丁超立方采样
- [ ] 理解复合体进化机制
- [ ] 掌握目标函数设计
- [ ] 会使用SCE-UA进行率定
- [ ] 能分析率定结果
- [ ] 理解参数等效性问题
- [ ] 了解算法的优缺点
- [ ] 能进行实际应用

---

**案例11完成！** 🎉

下一步：案例12 - GLUE不确定性分析

---

**作者**: CHS-Books项目组  
**日期**: 2025-11-02  
**版本**: v1.0
