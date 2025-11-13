# 案例7：PEST方法实现

## 学习目标

1. ✅ 理解PEST参数率定框架
2. ✅ 掌握参数组和观测组管理
3. ✅ 学习SVD辅助参数估计
4. ✅ 理解Tikhonov正则化
5. ✅ 掌握病态问题的处理

## 问题描述

使用PEST风格的框架率定二维非均质含水层模型：
- 左区水力传导度 K1
- 右区水力传导度 K2
- 左边界水头 h_left
- 右边界水头 h_right

**特点**：
- 参数分组管理
- 观测分组管理
- SVD辅助估计
- 正则化约束

## PEST简介

**PEST** (Parameter ESTimation) 是国际广泛使用的参数率定软件。

### 核心概念

**1. 参数组（Parameter Groups）**
- 将参数按物理意义分组
- 每组可设置不同的变换和约束
- 便于管理复杂模型

**2. 观测组（Observation Groups）**
- 将观测按类型分组（水头、流量等）
- 每组可设置不同的权重
- 支持多目标率定

**3. 参数变换**
- `none`: 无变换
- `log`: 对数变换 (适合K值)
- `fixed`: 固定参数

**4. SVD辅助**
- 处理参数相关性
- 避免小特征值引起的不稳定
- 自动确定可识别参数数量

## 理论基础

### SVD（奇异值分解）

**定义**：
对Jacobian矩阵J进行SVD分解：
```python
J = U Σ V^T
```

其中：
- U: 左奇异向量矩阵 (m × m)
- Σ: 奇异值对角矩阵 (m × n)
- V: 右奇异向量矩阵 (n × n)

**参数更新**：
```python
Δp = V Σ^{-1} U^T W^{1/2} r
```

### SVD辅助估计

**问题**：
- Jacobian矩阵J可能病态（条件数很大）
- 小奇异值对应不可识别或弱可识别参数
- 小奇异值的倒数会放大噪声

**解决**：
1. 计算奇异值 σ_1 ≥ σ_2 ≥ ... ≥ σ_n
2. 设置阈值 ε（如 ε = 10^{-6} σ_1）
3. 保留 σ_i > ε 的奇异值
4. 舍弃小奇异值，使用截断SVD

**效果**：
```python
条件数: κ_trunc = σ_1 / σ_k << κ_full = σ_1 / σ_n
```

大大降低条件数，提高稳定性。

### Tikhonov正则化

**正则化目标函数**：
```python
Φ_reg(p) = ||W^{1/2}(h_obs - h_sim)||² + α²||p - p_prior||²
```

其中：
- 第一项：数据拟合项
- 第二项：正则化项（参数偏离先验的惩罚）
- α: 正则化参数（权衡两项）

**正规方程**：
```python
(J^T W J + α²I) Δp = J^T W r
```

**作用**：
- 稳定参数估计
- 减小参数不确定性
- 约束参数在合理范围

### 条件数

**定义**：
```python
κ(A) = ||A|| · ||A^{-1}|| = σ_max / σ_min
```

**意义**：
- κ ≈ 1: 良态问题
- κ >> 1: 病态问题
- κ = ∞: 奇异矩阵

**典型值**：
- κ < 10²: 良好
- 10² < κ < 10⁶: 可接受
- κ > 10⁶: 严重病态

## 参数变换

### 对数变换

**为什么对K使用对数变换？**

**原因**：
1. K值跨越多个数量级 (10^{-5} ~ 10^3 m/day)
2. K不能为负
3. 对K的相对变化更关心

**变换**：
```python
p_transform = log(K)
K = exp(p_transform)
```

**优点**：
- 保证K > 0
- 将乘性问题转化为加性问题
- 更均匀的参数空间

## 运行代码

```bash
cd code/examples/case_07
python3 case_07_pest.py
```matlab

## 输出结果

程序将生成：

1. **case_07_convergence.png**: 收敛历史对比
2. **case_07_svd_analysis.png**: SVD奇异值分析
3. **case_07_fitted_results.png**: 观测值拟合结果
4. **case_07_parameter_comparison.png**: 参数率定对比

## 预期结果

### 率定精度

| 参数 | 真值 | SVD | SVD+正则化 | L-M |
|------|------|-----|------------|-----|
| K1 | 10.0 | ~9.8 | ~9.9 | ~10.1 |
| K2 | 5.0 | ~5.1 | ~5.0 | ~4.9 |
| h_left | 25.0 | ~24.9 | ~25.0 | ~25.0 |
| h_right | 15.0 | ~15.1 | ~15.0 | ~15.0 |

### SVD分析

**奇异值**：
- σ_1 ≈ 10: 最大奇异值
- σ_2 ≈ 5: 次要奇异值
- σ_3, σ_4: 较小奇异值

**保留成分**：
- 通常保留 2-3 个成分
- 解释方差 > 99%

**条件数**：
- 完整：κ ≈ 10⁴ (病态)
- 截断：κ ≈ 10² (良好)

## 实验探索

### 实验1：参数相关性

增加参数相关性：
```python
# K1和K2设为相近值
K1_true = 10.0
K2_true = 9.5  # 很接近K1
```python

**观察**：
- 奇异值变化
- 保留成分减少
- 参数不确定性增大

### 实验2：正则化强度

尝试不同正则化参数：
```python
regularization_alpha = 0.01  # 弱正则化
regularization_alpha = 0.1   # 中等
regularization_alpha = 1.0   # 强正则化
```python

**观察**：
- α过小：可能不稳定
- α适中：平衡拟合和稳定性
- α过大：过度约束，拟合变差

### 实验3：观测点数量

改变观测点数量：
```python
# 减少观测点
obs_x = np.array([10, 25, 40])  # 仅3个点
```python

**观察**：
- 观测少：参数不可识别增多
- SVD保留成分减少
- 不确定性增大

### 实验4：参数变换

尝试不同变换：
```python
# K组不使用对数变换
K_group = ParameterGroup(
    transform='none'  # 改为无变换
)
```python

**观察**：
- 对数变换通常更好
- 特别是当参数跨越数量级时

### 实验5：先验信息

添加先验参数约束：
```python
# 在正则化中使用先验值
prior_params = np.array([8.0, 4.0, 24.0, 16.0])
```python

**观察**：
- 先验信息引导参数估计
- 减小参数不确定性
- 需要先验合理

## 常见问题

### Q1: 什么时候使用SVD辅助？

**A**:
- 参数高度相关时
- 观测数据不足时
- 条件数 > 10³ 时
- 出现数值不稳定时

**判断标准**：
1. 计算条件数
2. 观察奇异值谱
3. 检查参数相关性矩阵

### Q2: 如何选择保留的SVD成分数？

**A**:

**方法1**：阈值法
```
σ_i > ε * σ_1,  ε = 10^{-6}
```python

**方法2**：累积方差
```
保留成分使得累积方差 > 95%
```python

**方法3**：L曲线
- 绘制 ||残差|| vs ||参数||
- 选择拐点

### Q3: 正则化参数α如何选择？

**A**:

**方法1**：试错法
- 尝试 α = [0.001, 0.01, 0.1, 1.0, 10.0]
- 选择拟合和稳定性平衡最好的

**方法2**：L曲线
- 绘制 log(||残差||) vs log(||参数||)
- 选择曲线拐点

**方法3**：广义交叉验证（GCV）
- 自动确定最优α
- 基于留一法交叉验证

**经验**：
- 数据质量好：α可小
- 数据噪声大：α应大
- 参数不确定性大：α应大

### Q4: PEST vs 标准方法的优势？

**A**:

**PEST优势**：
1. **组织性**：参数和观测分组管理
2. **灵活性**：支持参数变换
3. **稳定性**：SVD辅助处理病态问题
4. **扩展性**：易于扩展到复杂模型

**适用场景**：
- 大型复杂模型
- 多种参数类型
- 多种观测类型
- 病态问题

### Q5: 如何诊断参数不可识别？

**A**:

**诊断方法**：
1. **奇异值分析**：
   - 很小的奇异值 (< 10^{-6} σ_1)
   - 对应参数组合不可识别

2. **相关性矩阵**：
   - |ρ_ij| ≈ 1：参数高度相关
   - 线性组合可能不可识别

3. **敏感性分析**：
   - 复合敏感性很小
   - 观测对参数不敏感

**解决方法**：
- 增加观测数据
- 固定部分参数
- 使用先验信息
- 改进观测布局

## 数学推导补充

### SVD与参数可识别性

**参数空间分解**：
```
参数空间 = 可识别子空间 ⊕ 不可识别子空间
```python

**可识别子空间**：
- 由大奇异值对应的右奇异向量张成
- 观测对这些参数组合敏感

**不可识别子空间**：
- 由小奇异值对应的右奇异向量张成
- 观测对这些参数组合不敏感

### 正则化的贝叶斯解释

Tikhonov正则化等价于：
```
后验 ∝ 似然 × 先验
Φ_reg = -log(后验)
```python

其中：
- 数据拟合项 = -log(似然)
- 正则化项 = -log(先验)
- α² = σ_noise² / σ_prior²

## 代码结构

```python
# 1. 定义参数组
K_group = ParameterGroup(
    name='hydraulic_conductivity',
    parameters=['K1', 'K2'],
    initial_values=...,
    bounds=...,
    transform='log'
)

# 2. 定义观测组
obs_group = ObservationGroup(
    name='head_observations',
    observations=...,
    weights=...
)

# 3. PEST率定
result = pest_calibrate(
    forward_model,
    param_groups=[K_group, ...],
    obs_groups=[obs_group, ...],
    method='svd',
    regularization_alpha=0.1
)

# 4. 分析结果
parameters = result['parameters']
svd_info = result['history']['svd_info']
```

## 延伸阅读

1. Doherty, J. (2018). *PEST Model-Independent Parameter Estimation User Manual* (7th ed.). Watermark Numerical Computing.

2. Fienen, M. N., et al. (2009). *Using Prediction Uncertainty Analysis to Design Hydrologic Monitoring Networks*. Groundwater, 47(5), 643-655.

3. Moore, C., & Doherty, J. (2005). *Role of the Calibration Process in Reducing Model Predictive Error*. Water Resources Research, 41(5).

4. Hansen, P. C. (1998). *Rank-Deficient and Discrete Ill-Posed Problems*. SIAM.

## 下一步

完成本案例后，继续学习：
- **案例8**：贝叶斯推断与MCMC（全贝叶斯方法）
- **案例9**：敏感性分析（深入）
- **案例10**：不确定性量化

或者：
- 实际PEST软件应用
- 多目标率定
- 预测不确定性分析
