# 案例9：参数敏感性分析

**难度等级**: ⭐⭐  
**预计学习时间**: 2-3小时  
**前置知识**: 案例4（新安江模型）

---

## 📋 案例概述

本案例演示如何对水文模型进行**参数敏感性分析**，识别关键参数，为参数率定和模型优化提供依据。

### 学习目标

- 理解参数敏感性分析的意义
- 掌握三种敏感性分析方法
- 学会计算敏感性指标
- 理解敏感性可视化方法
- 学会参数重要性排序

---

## 🎯 核心内容

### 1. 参数敏感性分析概念

#### 什么是敏感性分析？

敏感性分析评估模型输入参数对输出结果的影响程度，帮助：
- **识别关键参数**：哪些参数最重要
- **指导率定**：优先率定敏感参数
- **简化模型**：去除不敏感参数
- **不确定性分析**：评估参数不确定性影响

#### 敏感性类型

**局部敏感性（OAT）**：
- 一次改变一个参数
- 其他参数保持不变
- 计算简单，结果直观

**全局敏感性（Morris, Sobol）**：
- 同时变化多个参数
- 考虑参数交互作用
- 更全面但计算量大

---

## 🔬 三种分析方法

### 方法1：OAT（One-At-a-Time）

**原理**：固定其他参数，逐个改变目标参数，观察输出变化。

**敏感性指标**：
```
相对敏感性系数 S = (ΔY/Y₀) / (ΔX/X₀)
```

**优点**：
- 简单直观
- 易于实现
- 结果清晰

**缺点**：
- 只考虑单参数效应
- 忽略参数交互

### 方法2：Morris筛选法

**原理**：通过随机轨迹采样，估计参数的平均效应和交互作用。

**Morris指标**：
- **μ\* (mu-star)**：平均绝对效应，衡量重要性
- **σ (sigma)**：标准差，衡量交互作用或非线性

**分类**：
- 高μ\*, 低σ：线性且重要
- 高μ\*, 高σ：非线性或有交互
- 低μ\*：不重要

### 方法3：相关系数法

**原理**：大量随机采样，计算参数与输出的相关系数。

**指标**：
- **Pearson相关**：线性相关
- **Spearman秩相关**：单调相关

**采样方法**：
- 简化拉丁超立方采样（LHS）
- 均匀分布或正态分布

---

## 💻 代码实现

### 1. OAT敏感性分析

```python
def one_at_a_time_sensitivity(model_func, base_params, param_ranges, 
                               rainfall, n_samples=10):
    """
    单参数敏感性分析
    """
    results = {'param_values': {}, 'outputs': {}, 'sensitivity_indices': {}}
    
    # 基准输出
    base_output = np.sum(model_func(base_params, rainfall))
    
    # 对每个参数
    for param_name, (pmin, pmax) in param_ranges.items():
        # 参数值序列
        param_values = np.linspace(pmin, pmax, n_samples)
        outputs = []
        
        for param_value in param_values:
            test_params = base_params.copy()
            test_params[param_name] = param_value
            output = np.sum(model_func(test_params, rainfall))
            outputs.append(output)
        
        # 计算敏感性系数
        relative_change = (outputs - base_output) / base_output
        param_relative_change = (param_values - base_params[param_name]) / base_params[param_name]
        sensitivity_coef = np.polyfit(param_relative_change, relative_change, 1)[0]
        
        results['param_values'][param_name] = param_values
        results['outputs'][param_name] = outputs
        results['sensitivity_indices'][param_name] = {
            'coefficient': sensitivity_coef,
            'output_range': (np.max(outputs) - np.min(outputs)) / base_output
        }
    
    return results
```

### 2. Morris筛选法

```python
def morris_screening(model_func, param_ranges, rainfall, 
                     n_trajectories=10, n_levels=4):
    """
    Morris筛选法
    """
    param_names = list(param_ranges.keys())
    elementary_effects = {name: [] for name in param_names}
    
    for _ in range(n_trajectories):
        # 生成基础点
        base_point = {}
        for name, (pmin, pmax) in param_ranges.items():
            level = np.random.randint(0, n_levels)
            base_point[name] = pmin + (pmax - pmin) * level / (n_levels - 1)
        
        base_output = np.sum(model_func(base_point, rainfall))
        
        # 扰动每个参数
        for param_name in param_names:
            delta_point = base_point.copy()
            pmin, pmax = param_ranges[param_name]
            delta = (pmax - pmin) / (n_levels - 1)
            delta_point[param_name] = min(delta_point[param_name] + delta, pmax)
            
            delta_output = np.sum(model_func(delta_point, rainfall))
            ee = (delta_output - base_output) / delta
            elementary_effects[param_name].append(ee)
    
    # 计算Morris指标
    results = {}
    for param_name in param_names:
        ee_array = np.array(elementary_effects[param_name])
        results[param_name] = {
            'mu_star': np.mean(np.abs(ee_array)),
            'sigma': np.std(ee_array)
        }
    
    return results
```

### 3. 相关系数法

```python
def correlation_based_sensitivity(model_func, param_ranges, rainfall, n_samples=1000):
    """
    基于相关系数的敏感性分析
    """
    param_names = list(param_ranges.keys())
    n_params = len(param_names)
    
    # LHS采样
    param_samples = np.zeros((n_samples, n_params))
    for i, (name, (pmin, pmax)) in enumerate(param_ranges.items()):
        intervals = np.linspace(0, 1, n_samples + 1)
        samples = np.random.uniform(intervals[:-1], intervals[1:])
        np.random.shuffle(samples)
        param_samples[:, i] = pmin + samples * (pmax - pmin)
    
    # 运行模型
    outputs = np.zeros(n_samples)
    for i in range(n_samples):
        params = {name: param_samples[i, j] for j, name in enumerate(param_names)}
        outputs[i] = np.sum(model_func(params, rainfall))
    
    # 计算相关系数
    results = {}
    for i, param_name in enumerate(param_names):
        pearson_r = np.corrcoef(param_samples[:, i], outputs)[0, 1]
        rank_param = np.argsort(np.argsort(param_samples[:, i]))
        rank_output = np.argsort(np.argsort(outputs))
        spearman_r = np.corrcoef(rank_param, rank_output)[0, 1]
        
        results[param_name] = {
            'pearson': pearson_r,
            'spearman': spearman_r
        }
    
    return results
```

---

## 📊 实验结果

### 新安江模型参数敏感性排序

#### OAT方法（输出变化范围）
1. **WM (蓄水容量)**: 50.23% - 极高敏感
2. **IM (不透水面积比)**: 0.55% - 低敏感
3. **B (蓄水容量曲线指数)**: 0.08% - 极低敏感
4. **SM, KG, KI**: <0.01% - 几乎不敏感

#### Morris方法（μ\*指标）
1. **IM**: 6.603 - 最高
2. **WM**: 0.213
3. **B**: 0.076
4. **SM, KG, KI**: 0.000

#### 相关系数法（Pearson）
1. **WM**: 0.995 - 极强正相关
2. **B**: 0.082 - 弱正相关
3. **IM**: 0.044 - 弱正相关
4. **KI, SM, KG**: <0.04

### 结果解读

**一致性结论**：
- **WM是最敏感参数**（所有方法一致）
- 原因：直接控制流域蓄水能力
- 建议：率定时优先调整WM

**方法差异**：
- OAT和相关系数法：WM最敏感
- Morris法：IM最敏感（可能因交互作用）
- 说明：需综合多种方法判断

---

## 🎨 可视化说明

### 1. OAT敏感性曲线图
- 6个子图，每个参数一条曲线
- x轴：参数值
- y轴：累计径流(mm)
- 红色虚线：基准输出

### 2. 龙卷风图（Tornado Chart）
- 参数按敏感性排序
- 柱长：输出变化幅度
- 颜色：敏感性高低（红→黄→绿）

### 3. Morris散点图
- x轴：μ\* (重要性)
- y轴：σ (交互作用)
- 右上区域：重要且有交互
- 右下区域：重要但线性

### 4. 相关系数散点图
- 6个子图
- 每个参数1000个采样点
- 红色虚线：线性拟合
- 标题显示Pearson和Spearman系数

### 5. 综合敏感性排名
- 三种方法并排对比
- 归一化到0-1范围
- 直观比较方法差异

---

## 💡 工程应用

### 1. 参数率定指导

**率定策略**：
```
第一步：率定WM（最敏感）
第二步：率定IM和B（中等敏感）
第三步：固定SM, KG, KI（不敏感）
```

**好处**：
- 减少率定参数数量
- 提高率定效率
- 避免过度拟合

### 2. 模型简化

**简化原则**：
- 去除不敏感参数
- 使用区域经验值
- 减少计算量

### 3. 不确定性分析

**应用**：
- 识别不确定性来源
- 优先减小敏感参数不确定性
- Monte Carlo模拟输入设计

---

## 📝 练习题

### 基础练习
1. 运行代码，观察6个参数的敏感性排序
2. 修改参数变化范围，观察结果变化
3. 增加采样点数量（OAT：15→30）

### 进阶练习
1. 添加新参数（如EX, KG_base）进行分析
2. 尝试不同降雨情景（大雨、小雨）
3. 对比不同流域参数的敏感性

### 挑战练习
1. 实现Sobol全局敏感性分析
2. 分析参数交互作用（二阶效应）
3. 对比不同模型的参数敏感性

---

## 🔍 常见问题

### Q1: 不同方法结果不一致怎么办？

**A**: 这是正常的：
- OAT：局部线性假设
- Morris：考虑参数空间全局特性
- 相关系数：基于大量采样

**建议**：综合判断，重点关注所有方法都显示敏感的参数。

### Q2: 如何选择参数变化范围？

**A**: 原则：
- 物理意义：不能超出物理合理范围
- 文献经验：参考已发表研究
- ±20-50%：基准值的合理变化
- 实际观测：如有实测数据，基于实测范围

### Q3: 采样数量如何确定？

**A**: 参考值：
- OAT：10-20个点/参数
- Morris：10-50条轨迹
- 相关系数法：500-2000个样本

**原则**：样本越多越准确，但计算量增大。

### Q4: 敏感性会随流域变化吗？

**A**: 会的：
- 湿润流域：WM可能更敏感
- 干旱流域：IM可能更重要
- 山区流域：地形参数更敏感

建议：对每个流域单独分析。

---

## 📚 参考资料

### 经典文献
1. Morris, M. D. (1991). "Factorial sampling plans for preliminary computational experiments." *Technometrics*, 33(2), 161-174.

2. Saltelli, A., et al. (2008). *Global Sensitivity Analysis: The Primer*. John Wiley & Sons.

3. Sobol', I. M. (2001). "Global sensitivity indices for nonlinear mathematical models." *Mathematics and Computers in Simulation*, 55(1-3), 271-280.

### 水文应用
1. van Griensven, A., et al. (2006). "A global sensitivity analysis tool for the parameters of multi-variable catchment models." *Journal of Hydrology*, 324(1-4), 10-23.

2. Tang, Y., et al. (2007). "Comparing sensitivity analysis methods to advance lumped watershed model identification and evaluation." *Hydrology and Earth System Sciences*, 11(2), 793-817.

---

## ✅ 学习检查清单

- [ ] 理解敏感性分析的目的和意义
- [ ] 掌握OAT方法的原理和应用
- [ ] 理解Morris方法的指标（μ\*, σ）
- [ ] 学会使用相关系数评估敏感性
- [ ] 能够解读龙卷风图
- [ ] 理解不同方法的优缺点
- [ ] 能够运行并修改代码
- [ ] 学会综合多种方法判断
- [ ] 理解敏感性在率定中的应用
- [ ] 能够对新模型进行敏感性分析

---

**案例9完成！** 🎉

下一步：案例10 - Muskingum-Cunge方法

---

**作者**: CHS-Books项目组  
**日期**: 2025-11-02  
**版本**: v1.0
