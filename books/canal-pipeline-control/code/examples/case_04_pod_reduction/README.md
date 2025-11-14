# 案例4：POD降阶 - 本征正交分解

## 问题描述

在案例1-3中，我们使用Saint-Venant方程（偏微分方程PDE）描述渠道水力学，然后使用有限差分法进行空间离散，得到一组常微分方程（ODE）。对于长度L=1000m、节点数N=21的渠道，状态维数为42（21个水位+21个流量）。

随着系统规模增大（更长的渠道、更多的节点），计算复杂度急剧增加：
- 仿真时间变长
- 控制器设计困难
- 实时控制难以实现

**模型降阶（Model Order Reduction, MOR）** 的目标是：在保持主要动力学特性的前提下，将高维系统降维到低维空间，从而：
- 加速仿真
- 简化控制器设计
- 实现实时控制

**POD（Proper Orthogonal Decomposition，本征正交分解）** 是最经典的模型降阶方法之一，也称为Karhunen-Loève展开或主成分分析（PCA）。

```matlab
模型降阶示意图：

全阶模型（High-dimensional）
┌────────────────────────────┐
│  Saint-Venant PDE          │
│  空间离散: N=100节点        │
│  状态维数: n=200           │
│  计算时间: 100s            │
└────────┬───────────────────┘
         │
         │ POD降阶
         │ (SVD + Galerkin投影)
         ↓
降阶模型（Low-dimensional）
┌────────────────────────────┐
│  降阶ODE                   │
│  状态维数: r=10            │
│  计算时间: 1s              │
│  精度损失: <5%             │
└────────────────────────────┘
```

## 理论基础

### 1. POD方法概述

POD的核心思想：**从数据中提取主导模态**

假设我们有系统在不同时刻的状态快照：
$$\mathbf{h}(x, t_1), \mathbf{h}(x, t_2), \ldots, \mathbf{h}(x, t_M)$$

其中每个快照是一个空间分布的水位场（N维向量）。

POD寻找一组**最优正交基** $\{\phi_1(x), \phi_2(x), \ldots, \phi_r(x)\}$，使得：
$$\mathbf{h}(x, t) \approx \sum_{i=1}^{r} a_i(t) \phi_i(x) = \boldsymbol{\Phi} \mathbf{a}(t)$$

其中：
- $\boldsymbol{\Phi} = [\phi_1, \phi_2, \ldots, \phi_r]$：POD基矩阵（N×r）
- $\mathbf{a}(t) = [a_1(t), a_2(t), \ldots, a_r(t)]^T$：低维状态（r维）
- $r \ll N$：降阶维数

"最优"的含义：在所有r维子空间中，POD基能够**捕获最多的系统能量**。

### 2. POD算法（基于SVD）

**步骤1：收集快照数据**

运行全阶模型，收集M个时刻的状态快照，构造快照矩阵：
$$\mathbf{X} = [\mathbf{h}^{(1)}, \mathbf{h}^{(2)}, \ldots, \mathbf{h}^{(M)}] \in \mathbb{R}^{N \times M}$$

**步骤2：奇异值分解（SVD）**

对快照矩阵进行SVD分解：
$$\mathbf{X} = \mathbf{U} \boldsymbol{\Sigma} \mathbf{V}^T$$

其中：
- $\mathbf{U} \in \mathbb{R}^{N \times N}$：左奇异向量（POD模态）
- $\boldsymbol{\Sigma} \in \mathbb{R}^{N \times M}$：奇异值对角矩阵，$\sigma_1 \geq \sigma_2 \geq \ldots \geq 0$
- $\mathbf{V} \in \mathbb{R}^{M \times M}$：右奇异向量（时间系数）

**步骤3：选择主导模态**

根据能量捕获率选择前r个模态：
$$\boldsymbol{\Phi}_r = \mathbf{U}[:, 1:r] = [\phi_1, \phi_2, \ldots, \phi_r]$$

能量捕获率：
$$\eta_r = \frac{\sum_{i=1}^{r} \sigma_i^2}{\sum_{i=1}^{N} \sigma_i^2}$$

通常选择 $\eta_r > 99\%$ 或 $\eta_r > 99.9\%$。

**步骤4：Galerkin投影**

将原始PDE投影到POD子空间：
$$\frac{d\mathbf{h}}{dt} = \mathbf{f}(\mathbf{h}, u)$$

替换 $\mathbf{h} = \boldsymbol{\Phi}_r \mathbf{a}$：
$$\boldsymbol{\Phi}_r \frac{d\mathbf{a}}{dt} = \mathbf{f}(\boldsymbol{\Phi}_r \mathbf{a}, u)$$

左乘 $\boldsymbol{\Phi}_r^T$（Galerkin投影）：
$$\frac{d\mathbf{a}}{dt} = \boldsymbol{\Phi}_r^T \mathbf{f}(\boldsymbol{\Phi}_r \mathbf{a}, u)$$

这就是降阶模型，状态维数从N降到r。

### 3. POD降阶模型的性质

**优点**：
1. **数学最优**：在L²范数意义下，POD基是最优的
2. **数据驱动**：不需要对系统有深入理解
3. **计算高效**：SVD计算快速
4. **能量保持**：主要能量被保留

**缺点**：
1. **线性假设**：适用于线性或弱非线性系统
2. **快照依赖**：需要代表性的训练数据
3. **全局基**：不适合多尺度或局部变化剧烈的问题
4. **控制输入**：对不同控制输入，可能需要重新计算POD基

### 4. 渠道系统的POD降阶

对于渠道系统：
$$\frac{\partial h}{\partial t} + \frac{\partial Q}{\partial x} = 0$$

离散后：
$$\frac{d\mathbf{h}}{dt} = -\mathbf{D} \mathbf{Q} + \mathbf{B}_q q_{lat}$$

其中：
- $\mathbf{h} \in \mathbb{R}^N$：水位向量
- $\mathbf{Q} \in \mathbb{R}^N$：流量向量
- $\mathbf{D}$：空间差分矩阵
- $\mathbf{B}_q$：侧向入流分布矩阵

POD降阶：
$$\mathbf{h} \approx \boldsymbol{\Phi}_r \mathbf{a}$$

降阶模型：
$$\frac{d\mathbf{a}}{dt} = \boldsymbol{\Phi}_r^T \left( -\mathbf{D} \mathbf{Q}(\boldsymbol{\Phi}_r \mathbf{a}) + \mathbf{B}_q q_{lat} \right)$$

控制输入通过边界条件 $Q_{in}$ 影响系统。

## 实验设计

### Part 1: POD基提取与可视化

**实验目的**：从快照数据中提取POD模态，可视化主导模态

**步骤**：
1. 运行全阶模型，收集M=300个快照（30分钟仿真，每6秒一个快照）
2. 对快照矩阵进行SVD分解
3. 计算能量捕获率
4. 可视化前4个POD模态

**预期结果**：
- 第1个模态：捕获主要的空间分布（通常是平均值或主趋势）
- 第2-3个模态：捕获主要的动力学模式
- 高阶模态：捕获小尺度波动

### Part 2: 不同降阶维数性能对比

**实验目的**：分析降阶维数r对精度和计算时间的影响

**测试场景**：
- 测试不同r：r = 2, 5, 10, 15, 20
- 控制输入：阶跃响应（目标水位从1.8m变为2.0m）
- 评价指标：
  - 重构误差：$\epsilon = \|\mathbf{h}_{full} - \mathbf{h}_{ROM}\| / \|\mathbf{h}_{full}\|$
  - 计算时间加速比：$speedup = t_{full} / t_{ROM}$
  - 能量捕获率：$\eta_r$

**预期现象**：
- r太小：精度差，丢失重要动力学
- r太大：计算时间长，降阶优势不明显
- 存在最优r：平衡精度和效率

### Part 3: 降阶模型控制器设计

**实验目的**：在降阶模型上设计PID控制器，对比全阶模型

**场景**：
- 目标：维持下游水位h_d = 2.0 m
- 扰动：t=300s时，中段引入q_d = 2 m³/s侧向入流
- 对比：
  1. 全阶模型 + PID控制
  2. 降阶模型(r=10) + PID控制

**性能指标**：
- 控制性能：IAE, ISE, 调节时间
- 计算效率：仿真时间对比

**预期结果**：
- 降阶模型能够保持主要的控制性能
- 计算时间大幅减少（10-50倍加速）

### Part 4: 不同工况的泛化能力

**实验目的**：测试POD降阶模型对不同工况的适应性

**场景**：
- **训练数据**：使用场景A的快照构建POD基
  - 目标水位：2.0m
  - 扰动：阶跃扰动2 m³/s

- **测试数据**：在不同场景下测试
  - 场景B：目标水位2.5m
  - 场景C：扰动3 m³/s
  - 场景D：斜坡扰动

**评价指标**：
- 不同场景下的重构误差
- 泛化能力分析

**预期现象**：
- 在训练工况附近，降阶模型精度高
- 远离训练工况，精度下降
- 需要多工况快照来提高泛化能力

## 工程意义

### 1. POD降阶的应用场景

**适合的场景**：
1. **大规模系统**：节点数多（N>100）、计算耗时
2. **实时控制**：需要快速预测和优化
3. **参数优化**：需要多次运行仿真（如MPC的预测）
4. **数字孪生**：需要与实际系统同步运行

**不适合的场景**：
1. **强非线性系统**：POD假设线性组合有效
2. **多尺度问题**：时空尺度差异大
3. **激波/间断**：突变现象难以捕捉
4. **训练数据不足**：快照不能代表所有工况

### 2. POD降阶流程

**步骤1：数据采集**
```python
# 运行全阶模型，收集快照
snapshots = []
for scenario in training_scenarios:
    h, Q = run_full_order_model(scenario)
    snapshots.append(h)
```python

**步骤2：SVD分解**
```python
# 构造快照矩阵
X = np.column_stack(snapshots)  # N × M

# SVD分解
U, S, Vt = np.linalg.svd(X, full_matrices=False)

# 选择前r个模态
r = 10
Phi = U[:, :r]  # POD基
```python

**步骤3：降阶模型构建**
```python
# Galerkin投影
def reduced_dynamics(a, t, u):
    # 重构全阶状态
    h_full = Phi @ a

    # 计算全阶右端项
    f_full = full_order_rhs(h_full, u)

    # 投影到低维
    da_dt = Phi.T @ f_full

    return da_dt
```python

**步骤4：控制器设计**
```python
# 在降阶模型上设计控制器
pid = PIDController(Kp=2, Ki=0.1, Kd=5)

# 闭环控制
a_current = ...  # 低维状态
h_reconstructed = Phi @ a_current  # 重构到全阶
h_d = h_reconstructed[-1]  # 下游水位
u = pid.compute(2.0, h_d)
```bash

### 3. 降阶维数选择指南

**方法1：能量阈值**
- 设定阈值：$\eta_r \geq 99\%$ 或 $99.9\%$
- 自动确定r

**方法2：奇异值衰减曲线**
- 绘制 $\sigma_i$ vs $i$ 曲线
- 找到"肘点"（elbow point）
- 在衰减变缓处截断

**方法3：交叉验证**
- 使用训练集构建POD基
- 在验证集上测试不同r的精度
- 选择精度-效率平衡点

### 4. 精度提升技巧

**技巧1：多工况快照**
```python
# 收集多种工况的快照
snapshots = []
for Q_in in [8, 10, 12]:  # 不同流量
    for h_target in [1.8, 2.0, 2.2]:  # 不同目标水位
        h = simulate(Q_in, h_target)
        snapshots.append(h)
```python

**技巧2：增量POD**
```python
# 在线更新POD基
if reconstruction_error > threshold:
    # 添加新快照
    snapshots.append(h_new)
    # 重新计算POD基
    Phi = update_POD(Phi, h_new)
```python

**技巧3：局部POD**
```python
# 对不同区域使用不同POD基
Phi_upstream = POD(snapshots_upstream)
Phi_downstream = POD(snapshots_downstream)
```bash

## 参数说明

### 渠道参数
| 参数 | 符号 | 数值 | 单位 |
|------|------|------|------|
| 渠道长度 | L | 1000 | m |
| 渠道宽度 | B | 5 | m |
| 渠底坡度 | i₀ | 0.001 | - |
| 曼宁糙率 | n | 0.025 | s/m^(1/3) |
| 全阶节点数 | N | 51 | - |

### POD参数
| 参数 | 数值 | 说明 |
|------|------|------|
| 快照数量 M | 300 | 30分钟仿真，每6秒一个快照 |
| 降阶维数 r | 2-20 | 测试不同维数 |
| 能量阈值 | 99% | 能量捕获率 |
| 最优r | 10 | 平衡精度和效率 |

### 仿真参数
| 参数 | 数值 | 说明 |
|------|------|------|
| 仿真时间 | 1800 s | 30分钟 |
| 控制周期 | 60 s | PID采样周期 |
| 仿真步长 | 10 s | Saint-Venant求解步长 |

## 性能评估

### 评价指标

**精度指标**：
1. 相对L²误差：$\epsilon_{L^2} = \|\mathbf{h}_{full} - \mathbf{h}_{ROM}\|_2 / \|\mathbf{h}_{full}\|_2$
2. 最大误差：$\epsilon_{\infty} = \max_i |\mathbf{h}_{full,i} - \mathbf{h}_{ROM,i}|$
3. 能量捕获率：$\eta_r = \sum_{i=1}^r \sigma_i^2 / \sum_{i=1}^N \sigma_i^2$

**效率指标**：
1. 计算时间：$t_{full}$, $t_{ROM}$
2. 加速比：$speedup = t_{full} / t_{ROM}$
3. 存储需求：降阶模型只需存储 $\boldsymbol{\Phi}_r$ (N×r) 和 $\mathbf{a}$ (r×1)

**控制性能**：
1. IAE, ISE, ITAE（与全阶模型控制对比）
2. 调节时间、超调量

### 预期性能

**降阶性能（r=10）**：
- 能量捕获率：> 99.5%
- 重构误差：< 2%
- 加速比：10-30倍
- 控制性能：与全阶模型差异 < 5%

## 扩展思考

### 1. 非线性降阶方法

POD + Galerkin适用于线性或弱非线性系统。对于强非线性系统：
- **DEIM（Discrete Empirical Interpolation Method）**：加速非线性项计算
- **Kernel POD**：使用核技巧处理非线性
- **神经网络降阶**：用自编码器代替线性POD基

### 2. 在线自适应POD

固定POD基在工况变化时可能失效，可以：
- **增量POD**：在线更新POD基
- **参数化POD**：为不同参数构建POD基族
- **自适应选择**：根据状态选择合适的POD基

### 3. 结合控制理论

POD降阶后，可以应用更先进的控制方法：
- **LQR/LQG**：在降阶线性系统上设计最优控制
- **MPC**：利用降阶模型快速预测
- **H∞控制**：保证鲁棒性

### 4. 误差估计与自适应

如何知道降阶模型是否可信？
- **残差估计**：计算Galerkin投影残差
- **误差指示器**：预测重构误差
- **自适应加密**：误差大时增加模态数

## 参考文献

1. Holmes, P., Lumley, J. L., & Berkooz, G. (2012). *Turbulence, Coherent Structures, Dynamical Systems and Symmetry*. Cambridge University Press.
2. Chatterjee, A. (2000). An introduction to the proper orthogonal decomposition. *Current Science*, 78(7), 808-817.
3. Rowley, C. W., & Dawson, S. T. (2017). Model reduction for flow analysis and control. *Annual Review of Fluid Mechanics*, 49, 387-417.
4. Benner, P., Gugercin, S., & Willcox, K. (2015). A survey of projection-based model reduction methods for parametric dynamical systems. *SIAM Review*, 57(4), 483-531.
5. Litrico, X., & Fromion, V. (2009). *Modeling and Control of Hydrosystems*. Springer.

## 运行说明

```bash
# 运行完整演示
python main.py

# 输出结果
# - part1_pod_modes.png: POD模态可视化
# - part2_dimension_comparison.png: 不同降阶维数对比
# - part3_control_performance.png: 控制性能对比
# - part4_generalization.png: 泛化能力测试
# - 性能指标统计表
```

## 总结

案例4展示了POD降阶方法的完整流程。关键要点：

1. **POD是数据驱动的模型降阶方法**，通过SVD提取主导模态
2. **能量捕获率**是选择降阶维数的重要指标
3. **Galerkin投影**将高维PDE降维到低维ODE
4. **降阶模型**能显著加速仿真，同时保持主要动力学特性
5. **泛化能力**依赖于训练快照的代表性

POD降阶是模型预测控制（MPC）、实时优化、数字孪生等高级应用的基础技术。
