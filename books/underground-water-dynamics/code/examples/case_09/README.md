# 案例9：敏感性分析深入

## 学习目标

1. ✅ 理解全局vs局部敏感性
2. ✅ 掌握Sobol敏感性分析
3. ✅ 学习Morris筛选法
4. ✅ 理解参数交互作用
5. ✅ 对比不同敏感性方法

## 问题描述

使用全局敏感性分析方法研究地下水模型参数：
- K (水力传导度)
- h_left (左边界)
- h_right (右边界)

**方法**：
- Sobol敏感性指数
- Morris筛选法
- 参数交互作用分析
- 与局部敏感性对比

## 敏感性分析分类

### 局部敏感性 vs 全局敏感性

| 方面 | 局部敏感性 | 全局敏感性 |
|------|-----------|-----------|
| 评估点 | 单个参数点 | 整个参数空间 |
| 方法 | 偏导数 | 方差分解/采样 |
| 信息 | 局部影响 | 全局影响 |
| 非线性 | 假设线性 | 考虑非线性 |
| 交互 | 不考虑 | 可量化 |
| 成本 | 低 | 高 |

### 主要全局敏感性方法

1. **Sobol方法** - 方差分解
2. **Morris方法** - 筛选
3. **FAST方法** - 傅里叶变换
4. **回归方法** - 统计回归

## Sobol敏感性分析

### 理论基础

**方差分解**：

```
V(Y) = Σ V_i + Σ V_ij + ... + V_12...n
```

其中：
- V(Y): 输出总方差
- V_i: 参数i的方差贡献
- V_ij: 参数i和j的交互方差贡献

### Sobol指数

**一阶指数 S_i**：
```
S_i = V_i / V(Y)
```

**含义**：
- 参数i对输出方差的直接贡献
- 主效应（main effect）
- 范围：[0, 1]

**总效应指数 ST_i**：
```
ST_i = (V(Y) - V_{~i}) / V(Y)
```

其中V_{~i}是固定参数i后的剩余方差。

**含义**：
- 参数i的总贡献（包括交互）
- 范围：[0, 1]
- ST_i ≥ S_i

**交互效应指数**：
```
I_i = ST_i - S_i
```

**含义**：
- I_i = 0: 无交互
- I_i > 0: 有交互作用

**二阶指数 S_ij**：
```
S_ij = V_ij / V(Y)
```

**含义**：参数i和j的二阶交互

### 计算方法

**Saltelli采样方案**：

需要两个独立的采样矩阵A和B：
```
A = [a_1, a_2, ..., a_n]  (N × n)
B = [b_1, b_2, ..., b_n]  (N × n)
```

构造C_i矩阵（第i列从B取，其余从A取）：
```
C_i = [a_1, ..., a_{i-1}, b_i, a_{i+1}, ..., a_n]
```

**总模型运行次数**: N × (2 + n)

### 优势与限制

**优势**：
- ✅ 完整的方差分解
- ✅ 量化主效应和交互
- ✅ 模型独立
- ✅ 理论严格

**限制**：
- ❌ 计算成本高
- ❌ 需要大量样本
- ❌ 对高维问题困难

## Morris筛选法

### 方法原理

**OAT策略** (One-At-a-Time)：
- 每次只改变一个参数
- 沿随机轨迹采样
- 计算基本效应

### 基本效应

对于参数i：
```
EE_i = [f(x + Δe_i) - f(x)] / Δ
```

其中：
- e_i: 第i个坐标轴单位向量
- Δ: 扰动步长

### Morris指标

从r条轨迹得到r个基本效应，计算：

**μ (均值)**：
```
μ_i = (1/r) Σ EE_i
```
- 主效应的度量
- 可正可负

**μ* (绝对均值)**：
```
μ*_i = (1/r) Σ |EE_i|
```
- 总效应的度量
- 总是正值

**σ (标准差)**：
```
σ_i = sqrt[(1/r) Σ (EE_i - μ_i)²]
```
- 非线性/交互的度量
- 标准差大表示非线性强或有交互

### Morris筛选图

绘制(μ*, σ)散点图：

**四个区域**：
1. **高μ*，高σ**: 重要且非线性/交互
2. **高μ*，低σ**: 重要且线性
3. **低μ*，高σ**: 不重要但非线性
4. **低μ*，低σ**: 不重要

### 优势与限制

**优势**：
- ✅ 计算效率高
- ✅ 适合参数筛选
- ✅ 检测非线性和交互
- ✅ 适合高维问题

**限制**：
- ❌ 定性而非定量
- ❌ 精度低于Sobol
- ❌ 依赖轨迹选择

**总运行次数**: r × (n + 1)

## 参数交互作用

### 定义

两个参数有交互作用，如果：
```
f(x_i, x_j) ≠ f(x_i, x̄_j) + f(x̄_i, x_j) - f(x̄_i, x̄_j)
```

即效应不可加。

### 量化方法

**Sobol二阶指数**：
```
S_ij = V_ij / V(Y)
```

**交互强度**：
```
I(i,j) = f(1,1) + f(0,0) - f(1,0) - f(0,1)
```

其中0和1表示参数的下界和上界。

### 解释

- S_ij > 0: 显著交互
- S_ij ≈ 0: 无交互或弱交互
- 高交互意味着参数不能独立调节

## 运行代码

```bash
cd code/examples/case_09
python3 case_09_global_sensitivity.py
```

**注意**：Sobol分析需要较长时间（2-5分钟）。

## 输出结果

程序将生成：

1. **case_09_sobol_indices.png**: Sobol敏感性指数
2. **case_09_morris_screening.png**: Morris筛选图
3. **case_09_second_order_indices.png**: 二阶交互指数热图
4. **case_09_global_vs_local.png**: 全局vs局部敏感性对比

## 预期结果

### Sobol指数

| 参数 | S_i (一阶) | ST_i (总效应) | I_i (交互) |
|------|-----------|--------------|-----------|
| K | ~0.05 | ~0.08 | ~0.03 |
| h_left | ~0.45 | ~0.48 | ~0.03 |
| h_right | ~0.45 | ~0.48 | ~0.03 |

**解释**：
- h_left和h_right最敏感
- K相对不敏感
- 交互作用较弱（< 5%）

### Morris指标

| 参数 | μ | μ* | σ | 重要性 |
|------|---|----|----|--------|
| K | ~-0.15 | ~0.20 | ~0.05 | 低 |
| h_left | ~0.45 | ~0.45 | ~0.02 | 高 |
| h_right | ~-0.45 | ~0.45 | ~0.02 | 高 |

### 方法对比

三种方法得到一致的参数排序：
```
h_left ≈ h_right > K
```

## 实验探索

### 实验1：非线性模型

修改为非线性模型：
```python
def nonlinear_model(params):
    K, h_left, h_right = params
    # 非线性关系
    return K**2 * (h_left - h_right) / 1000
```

**观察**：
- Morris的σ增大
- 局部敏感性点依赖性强

### 实验2：强交互模型

```python
def interactive_model(params):
    K, h_left, h_right = params
    # K与边界有强交互
    return K * h_left * h_right / 1000
```

**观察**：
- ST_i - S_i显著增大
- 二阶Sobol指数S_ij增大

### 实验3：高维问题

增加参数：
```python
# 5个参数
bounds = [
    (5, 20),    # K
    (15, 25),   # h_left
    (8, 15),    # h_right
    (0, 10),    # 补给
    (0.1, 0.3)  # 储水系数
]
```

**观察**：
- Sobol计算时间急剧增加
- Morris仍然高效
- 参数筛选的重要性

### 实验4：采样数影响

改变Sobol采样数：
```python
n_samples = 100   # 少：结果不稳定
n_samples = 500   # 中等：通常足够
n_samples = 1000  # 多：结果稳定但慢
```

**观察**：
- 采样越多，结果越稳定
- 收敛性检查很重要

### 实验5：Morris轨迹数

```python
n_trajectories = 5    # 少：粗略估计
n_trajectories = 20   # 中等：一般足够
n_trajectories = 50   # 多：精确但成本高
```

**观察**：
- 轨迹越多，μ*和σ越稳定

## 常见问题

### Q1: 什么时候使用全局敏感性？

**A**:

**适合全局敏感性的情况**：
- ✅ 参数范围大
- ✅ 模型非线性强
- ✅ 需要考虑交互
- ✅ 参数筛选
- ✅ 不确定性量化

**可用局部敏感性的情况**：
- 模型线性或弱非线性
- 参数范围小
- 仅关心特定点
- 计算资源有限

### Q2: Sobol vs Morris如何选择？

**A**:

**Sobol方法**：
- 需要定量结果
- 参数数量不多（< 20）
- 计算资源充足
- 需要方差分解

**Morris方法**：
- 参数筛选阶段
- 参数数量多
- 计算资源有限
- 快速评估

**推荐策略**：
1. Morris筛选 → 识别重要参数
2. Sobol分析 → 量化重要参数

### Q3: 如何判断交互作用显著？

**A**:

**判断标准**：
1. **Sobol指数**：
   ```
   I_i = ST_i - S_i > 0.05  (5%阈值)
   ```

2. **二阶指数**：
   ```
   S_ij > 0.01  (1%阈值)
   ```

3. **Morris图**：
   ```
   σ > σ中位数
   ```

**注意**：
- 阈值可根据问题调整
- 显著性依赖于模型和参数范围

### Q4: 如何加速Sobol分析？

**A**:

**方法**：
1. **准蒙特卡罗**：使用Sobol序列而非随机采样
2. **代理模型**：训练快速代理模型
3. **并行计算**：模型评估并行化
4. **自适应采样**：在重要区域加密采样

**实践**：
```python
# 使用scipy的Sobol序列
from scipy.stats import qmc
sampler = qmc.Sobol(d=n_params)
samples = sampler.random(n_samples)
```

### Q5: 敏感性结果如何应用？

**A**:

**应用**：

1. **参数优先级**：
   - 高敏感性 → 优先率定
   - 低敏感性 → 可固定

2. **不确定性传播**：
   - 高敏感性 → 减小不确定性
   - 低敏感性 → 不确定性影响小

3. **模型简化**：
   - 移除不敏感参数
   - 简化模型结构

4. **实验设计**：
   - 在敏感参数上加密观测
   - 优化观测网络

## 数学推导补充

### Sobol分解定理

**ANOVA分解**：
```
f(x) = f_0 + Σ f_i(x_i) + Σ f_ij(x_i, x_j) + ... + f_12...n(x_1,...,x_n)
```

**方差分解**：
```
V = Σ V_i + Σ V_ij + ... + V_12...n
```

**正交性**：
```
∫ f_i(x_i) dx_i = 0
∫ f_ij(x_i, x_j) dx_j = 0
```

### 一阶Sobol指数推导

**定义**：
```
V_i = V[E(Y|X_i)]
```

**展开**：
```
S_i = V_i / V(Y)
    = V[E(Y|X_i)] / V(Y)
    = [E(E(Y|X_i)²) - E(Y)²] / V(Y)
```

**估计**（使用A, B, C_i矩阵）：
```
S_i ≈ [1/N Σ f_B(x^j) · (f_C_i(x^j) - f_A(x^j))] / V
```

### 总效应指数推导

**定义**：
```
V_{~i} = V[E(Y|X_{~i})]
```

**总效应**：
```
ST_i = 1 - V_{~i} / V(Y)
     = [V(Y) - V[E(Y|X_{~i})]] / V(Y)
     = E[V(Y|X_{~i})] / V(Y)
```

## 代码结构

```python
# 1. Sobol分析
result_sobol = compute_sobol_indices(
    forward_model=my_model,
    bounds=param_bounds,
    n_samples=1000,
    calc_second_order=True
)

# 2. Morris筛选
result_morris = morris_screening(
    forward_model=my_model,
    bounds=param_bounds,
    n_trajectories=20
)

# 3. 结果解释
important_params = [i for i, s in enumerate(result_sobol['S_total'])
                    if s > 0.1]
```

## 延伸阅读

1. Saltelli, A., et al. (2008). *Global Sensitivity Analysis: The Primer*. Wiley.

2. Sobol', I. M. (2001). *Global sensitivity indices for nonlinear mathematical models*. Mathematics and Computers in Simulation, 55(1-3), 271-280.

3. Morris, M. D. (1991). *Factorial sampling plans for preliminary computational experiments*. Technometrics, 33(2), 161-174.

4. Iooss, B., & Lemaître, P. (2015). *A review on global sensitivity analysis methods*. Operations Research/Computer Science Interfaces Series.

## 下一步

完成本案例后，继续学习：
- **案例10**：不确定性量化（GLUE、Monte Carlo）

或者深入敏感性分析：
- FAST方法
- EFAST方法
- 基于回归的方法
- 机器学习方法
