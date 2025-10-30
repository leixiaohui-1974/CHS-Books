# 案例5：动态模态分解（DMD）

## 问题描述

在案例4中，我们学习了POD降阶方法，通过SVD提取空间模态。POD关注的是**空间结构**——哪些空间模态包含最多能量。

**DMD（Dynamic Mode Decomposition，动态模态分解）** 则关注**时间演化**——系统如何随时间变化，包含哪些频率成分。DMD不仅提供空间模态，还提供每个模态的**时间演化特性**（增长率和频率）。

POD与DMD的区别：

| 特性 | POD | DMD |
|------|-----|-----|
| 理论基础 | SVD，能量最优 | Koopman算子，动力学最优 |
| 模态性质 | 静态空间模态 | 动态时空模态 |
| 时间信息 | 需要额外拟合 | 直接包含频率和增长率 |
| 预测能力 | 较弱 | 强（短期预测） |
| 适用场景 | 快照压缩、静态降阶 | 动力学分析、预测、控制 |

```
DMD应用示意图：

数据采集
┌────────────────────────────┐
│ 时间序列快照                │
│ x₀ → x₁ → x₂ → ... → xₘ    │
└────────┬───────────────────┘
         │
         ↓
DMD分解
┌────────────────────────────┐
│ 提取动态模态                │
│ φ₁, φ₂, ..., φᵣ            │
│ 特征值λ₁, λ₂, ..., λᵣ      │
│ (包含频率和增长率)          │
└────────┬───────────────────┘
         │
    ┌────┴────┐
    ↓         ↓
动力学分析   预测未来
┌─────────┐ ┌─────────┐
│频率谱   │ │短期预测 │
│增长率   │ │用于MPC  │
│主导模态 │ │实时控制 │
└─────────┘ └─────────┘
```

## 理论基础

### 1. Koopman算子理论

考虑动力系统：
$$\mathbf{x}_{k+1} = \mathbf{F}(\mathbf{x}_k)$$

其中$\mathbf{F}$可以是非线性的。

**Koopman算子**是一个线性算子$\mathcal{K}$，作用于观测函数$g(\mathbf{x})$：
$$\mathcal{K}g(\mathbf{x}) = g(\mathbf{F}(\mathbf{x}))$$

关键洞察：虽然$\mathbf{F}$可能是非线性的，但Koopman算子$\mathcal{K}$是**线性**的（作用于函数空间）。

如果我们选择观测函数为状态本身（$g(\mathbf{x}) = \mathbf{x}$），则：
$$\mathbf{x}_{k+1} \approx \mathbf{A} \mathbf{x}_k$$

其中$\mathbf{A}$是Koopman算子在有限维空间的近似。DMD的目标就是从数据中估计这个算子$\mathbf{A}$。

### 2. DMD算法

假设我们有时间序列数据：
$$\mathbf{X} = \begin{bmatrix} \mathbf{x}_0 & \mathbf{x}_1 & \cdots & \mathbf{x}_{m-1} \end{bmatrix}$$
$$\mathbf{Y} = \begin{bmatrix} \mathbf{x}_1 & \mathbf{x}_2 & \cdots & \mathbf{x}_m \end{bmatrix}$$

其中$\mathbf{Y} = \mathbf{AX}$（近似），我们要找$\mathbf{A}$。

**步骤1：SVD分解$\mathbf{X}$**
$$\mathbf{X} = \mathbf{U} \boldsymbol{\Sigma} \mathbf{V}^*$$

**步骤2：计算降阶算子$\tilde{\mathbf{A}}$**
$$\tilde{\mathbf{A}} = \mathbf{U}^* \mathbf{Y} \mathbf{V} \boldsymbol{\Sigma}^{-1}$$

这是$\mathbf{A}$在POD模态空间中的投影。

**步骤3：特征分解$\tilde{\mathbf{A}}$**
$$\tilde{\mathbf{A}} \mathbf{W} = \mathbf{W} \boldsymbol{\Lambda}$$

其中：
- $\boldsymbol{\Lambda} = \text{diag}(\lambda_1, \lambda_2, \ldots, \lambda_r)$：特征值（DMD特征值）
- $\mathbf{W}$：特征向量

**步骤4：计算DMD模态**
$$\boldsymbol{\Phi} = \mathbf{Y} \mathbf{V} \boldsymbol{\Sigma}^{-1} \mathbf{W}$$

这些是DMD模态（空间模式）。

**步骤5：计算初始系数**
$$\mathbf{b} = \boldsymbol{\Phi}^{\dagger} \mathbf{x}_0$$

其中$\boldsymbol{\Phi}^{\dagger}$是伪逆。

**步骤6：时间演化与预测**

系统状态的DMD重构：
$$\mathbf{x}(t) \approx \sum_{k=1}^{r} b_k \phi_k e^{\lambda_k t}$$

或离散形式：
$$\mathbf{x}_n = \sum_{k=1}^{r} b_k \phi_k \lambda_k^n = \boldsymbol{\Phi} \boldsymbol{\Lambda}^n \mathbf{b}$$

这提供了**显式的时间演化公式**，可以用于预测未来状态。

### 3. DMD特征值的物理意义

每个DMD特征值$\lambda_k$是复数：
$$\lambda_k = |\lambda_k| e^{i\omega_k \Delta t}$$

可以提取：
- **增长率/衰减率**：$\sigma_k = \ln(|\lambda_k|) / \Delta t$
  - $\sigma_k > 0$：模态增长（不稳定）
  - $\sigma_k < 0$：模态衰减（稳定）
  - $\sigma_k \approx 0$：模态持续振荡

- **频率**：$\omega_k = \text{Im}(\ln(\lambda_k)) / \Delta t$
  - 振荡频率（rad/s）

- **周期**：$T_k = 2\pi / \omega_k$

这些信息对于理解系统动力学非常重要。

### 4. DMD vs POD

**POD模态**：
- 按能量排序
- 正交
- 静态，不包含时间演化信息

**DMD模态**：
- 按动力学重要性排序
- 一般不正交
- 动态，每个模态有自己的频率和增长率

**何时使用POD**：
- 需要压缩大规模数据
- 关注空间结构
- 构建降阶模型（需要额外工作估计时间演化）

**何时使用DMD**：
- 需要理解系统动力学
- 需要短期预测
- 需要识别主导频率
- 用于MPC（模型预测控制）

## 实验设计

### Part 1: DMD模态提取与分析

**实验目的**：从渠道水位数据中提取DMD模态，分析频率和增长率

**步骤**：
1. 运行全阶模型，收集时间序列数据（M=180个快照）
2. 应用DMD算法，提取DMD模态
3. 计算特征值的频率和增长率
4. 可视化前4个DMD模态

**预期结果**：
- 模态1：通常对应主导的低频振荡
- 模态2-3：高频振荡或瞬态响应
- 通过频率谱了解系统的主要振荡特性

### Part 2: DMD vs POD对比

**实验目的**：对比DMD和POD的模态和性能

**对比维度**：
1. **模态形状**：DMD模态 vs POD模态
2. **重构精度**：使用相同维数r重构状态
3. **预测能力**：预测未来5分钟的水位变化

**评价指标**：
- 重构误差
- 预测误差（短期）
- 计算时间

**预期现象**：
- POD重构精度更高（能量最优）
- DMD预测能力更强（动力学最优）
- DMD更适合用于控制

### Part 3: DMD预测与验证

**实验目的**：测试DMD的短期预测能力

**场景**：
- 训练阶段：使用前15分钟数据构建DMD模型
- 预测阶段：预测未来1-5分钟的水位
- 验证：与实际仿真对比

**预测方法**：
$$\mathbf{x}(t_0 + n\Delta t) = \boldsymbol{\Phi} \boldsymbol{\Lambda}^n \mathbf{b}$$

**评价指标**：
- 不同预测步数的误差
- 预测误差随时间的增长

**预期结果**：
- 短期预测（1-2分钟）精度高
- 长期预测误差累积
- 验证DMD在MPC中的应用潜力

### Part 4: DMD用于模型预测控制

**实验目的**：将DMD模型集成到MPC框架

**MPC基本思想**：
1. 在当前时刻，使用模型预测未来N步
2. 求解优化问题，找到最优控制序列
3. 只执行第一步控制
4. 在下一时刻重复

**使用DMD的优势**：
- 预测快速（显式公式）
- 线性模型（优化容易）

**简化实现**（演示用）：
- 目标：维持下游水位2.0m
- 预测范围：未来3步（3分钟）
- 成本函数：$J = \sum (h_d^{pred} - 2.0)^2 + \rho \sum (\Delta u)^2$

## 工程意义

### 1. DMD的应用场景

**频率分析**：
- 识别系统的主导振荡频率
- 检测异常振荡（如水锤效应）
- 共振频率分析

**短期预测**：
- 预测未来几分钟的水位
- 预警系统（洪水、溢出）
- 为控制决策提供前瞻信息

**模型预测控制（MPC）**：
- 快速预测模型
- 滚动优化
- 约束处理

**系统健康监测**：
- 跟踪DMD特征值变化
- 检测系统退化（如渠道淤积、闸门磨损）

### 2. DMD实施步骤

**步骤1：数据采集**
```python
# 收集高质量时间序列数据
# 确保采样频率足够（Nyquist定理）
fs = 0.1  # 采样频率 [Hz]，每10秒一个快照
T_total = 1800  # 总时长30分钟
```

**步骤2：构建DMD模型**
```python
dmd = DMD(svd_rank=10)  # 保留前10个模态
dmd.fit(X, Y)

# 提取结果
Phi = dmd.modes         # DMD模态
Lambda = dmd.eigenvalues  # 特征值
b = dmd.amplitudes      # 初始系数
```

**步骤3：分析频率和增长率**
```python
omega = np.angle(Lambda) / dt  # 频率 [rad/s]
sigma = np.log(np.abs(Lambda)) / dt  # 增长率 [1/s]

# 识别主导模态
dominant_modes = np.argsort(np.abs(sigma))[:5]
```

**步骤4：预测**
```python
def dmd_predict(x0, n_steps):
    b = np.linalg.lstsq(Phi, x0, rcond=None)[0]
    predictions = []
    for n in range(n_steps):
        x_pred = np.real(Phi @ (Lambda**n * b))
        predictions.append(x_pred)
    return predictions
```

### 3. DMD参数选择

**SVD秩（降阶维数r）**：
- 方法1：能量阈值（类似POD，保留99%能量）
- 方法2：通过交叉验证选择
- 方法3：保留增长率大的模态（$|\sigma_k|$大）

**时间窗口长度**：
- 太短：无法捕获低频动力学
- 太长：包含过多瞬态，不利于预测
- 经验：包含2-3个主导周期

**采样频率**：
- 满足Nyquist定理：$f_s > 2 f_{max}$
- 对于渠道系统，主要频率通常<0.01 Hz

### 4. DMD的局限性

**线性假设**：
- DMD假设$\mathbf{x}_{k+1} = \mathbf{A}\mathbf{x}_k$
- 对于强非线性系统，可能不准确
- 解决：Extended DMD, Kernel DMD

**预测范围有限**：
- 短期预测准确
- 长期预测误差累积
- 只能预测训练数据范围内的动力学

**对噪声敏感**：
- 噪声可能产生虚假模态
- 需要数据预处理或正则化
- 解决：Optimized DMD, Total DMD

**控制输入处理**：
- 标准DMD不包含控制输入
- 需要扩展：DMD with Control (DMDc)

## 参数说明

### 渠道参数
| 参数 | 符号 | 数值 | 单位 |
|------|------|------|------|
| 渠道长度 | L | 1000 | m |
| 渠道宽度 | B | 5 | m |
| 渠底坡度 | i₀ | 0.001 | - |
| 曼宁糙率 | n | 0.025 | s/m^(1/3) |
| 节点数 | N | 51 | - |

### DMD参数
| 参数 | 数值 | 说明 |
|------|------|------|
| 快照数量 M | 180 | 30分钟，每10秒一个 |
| 降阶维数 r | 10 | DMD保留的模态数 |
| 时间步长 Δt | 10 s | 快照间隔 |
| 预测步数 | 5-30 | 预测0.5-5分钟 |

## 性能评估

### 评价指标

**频域指标**：
1. 主导频率识别精度
2. 频率谱分辨率

**时域指标**：
1. 重构误差：$\epsilon_{rec} = \|\mathbf{X} - \mathbf{X}_{DMD}\| / \|\mathbf{X}\|$
2. 预测误差：$\epsilon_{pred}(n) = \|\mathbf{x}_{true}(t_0+n\Delta t) - \mathbf{x}_{DMD}(t_0+n\Delta t)\|$

**控制性能**：
1. MPC with DMD vs MPC with full model
2. 计算时间对比

### 预期性能

**DMD模型（r=10）**：
- 重构误差：< 5%
- 1分钟预测误差：< 2%
- 5分钟预测误差：< 10%
- 计算速度：比全阶模型快10-50倍

## 扩展思考

### 1. DMD变种

**Exact DMD**：
- 更准确的特征值计算
- 避免$\boldsymbol{\Sigma}^{-1}$的数值问题

**Extended DMD (EDMD)**：
- 使用非线性观测函数
- 捕获非线性动力学

**DMD with Control (DMDc)**：
- 包含控制输入
- 模型形式：$\mathbf{x}_{k+1} = \mathbf{A}\mathbf{x}_k + \mathbf{B}\mathbf{u}_k$

**Optimized DMD**：
- 稀疏优化
- 去除虚假模态

### 2. 在线DMD

固定DMD模型可能过时，在线更新：
```python
# 滑动窗口DMD
def update_dmd(dmd_old, x_new):
    # 移除最旧的快照，添加新快照
    X_new = np.column_stack([X_old[:, 1:], x_new])
    dmd_new = DMD().fit(X_new[:-1], X_new[1:])
    return dmd_new
```

### 3. DMD用于异常检测

跟踪DMD特征值的变化：
```python
# 健康状态
lambda_healthy = dmd_healthy.eigenvalues

# 当前状态
lambda_current = dmd_current.eigenvalues

# 检测异常
deviation = np.linalg.norm(lambda_current - lambda_healthy)
if deviation > threshold:
    raise_alarm("System anomaly detected")
```

### 4. 多分辨率DMD

对不同时间尺度使用不同DMD：
- 快速DMD：捕获高频动力学（秒级）
- 慢速DMD：捕获低频动力学（分钟级）

## 参考文献

1. Schmid, P. J. (2010). Dynamic mode decomposition of numerical and experimental data. *Journal of Fluid Mechanics*, 656, 5-28.
2. Kutz, J. N., Brunton, S. L., Brunton, B. W., & Proctor, J. L. (2016). *Dynamic Mode Decomposition: Data-Driven Modeling of Complex Systems*. SIAM.
3. Tu, J. H., et al. (2014). On dynamic mode decomposition: Theory and applications. *Journal of Computational Dynamics*, 1(2), 391-421.
4. Proctor, J. L., Brunton, S. L., & Kutz, J. N. (2016). Dynamic mode decomposition with control. *SIAM Journal on Applied Dynamical Systems*, 15(1), 142-161.
5. Williams, M. O., Kevrekidis, I. G., & Rowley, C. W. (2015). A data-driven approximation of the koopman operator: Extending dynamic mode decomposition. *Journal of Nonlinear Science*, 25(6), 1307-1346.

## 运行说明

```bash
# 运行完整演示
python main.py

# 输出结果
# - part1_dmd_modes.png: DMD模态可视化
# - part2_dmd_vs_pod.png: DMD与POD对比
# - part3_dmd_prediction.png: DMD预测能力测试
# - part4_dmd_mpc_demo.png: DMD用于MPC演示
# - 性能指标统计表
```

## 总结

案例5展示了DMD的完整流程和应用。关键要点：

1. **DMD关注动力学**，提取包含时间演化信息的模态
2. **DMD特征值**包含频率和增长率信息
3. **DMD预测能力强**，适合短期预测和MPC
4. **DMD是数据驱动的**，基于Koopman算子理论
5. **DMD与POD互补**：POD关注空间，DMD关注时间

DMD是现代数据驱动控制的重要工具，在流体力学、气候科学、金融、生物系统等领域都有广泛应用。
