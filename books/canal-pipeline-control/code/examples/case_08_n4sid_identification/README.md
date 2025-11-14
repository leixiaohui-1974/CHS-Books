# 案例8：N4SID子空间辨识

## 问题描述

在前面的案例中，我们使用的是**已知的数学模型**（Saint-Venant方程）进行仿真和控制设计。但在实际工程中，很多时候我们无法准确建立物理模型，或者模型参数不确定。

**系统辨识（System Identification）**是从输入输出数据中构建系统数学模型的方法。对于水利系统，辨识出的模型可以用于：
- 控制器设计（MPC、H∞控制等）
- 系统分析（稳定性、响应特性）
- 故障检测（实际vs模型偏差）
- 数字孪生（实时状态估计）

```python
系统辨识流程：

实际系统                输入输出数据            数学模型
┌────────┐             ┌──────────┐           ┌────────┐
│ 渠道   │  →  采集  →  │ u(t), y(t)│  →  辨识 → │ 状态空间│
│ 闸门   │             │          │           │  模型   │
└────────┘             └──────────┘           └────────┘
 真实但复杂              数据驱动               简洁可用
```

**N4SID（Numerical algorithms for Subspace State Space System Identification）**是最成功的子空间辨识方法之一，优点包括：

1. **不需要迭代优化**：基于SVD，数值稳定
2. **自动确定模型阶数**：通过奇异值分析
3. **适合多输入多输出系统**：MIMO系统辨识
4. **处理噪声能力强**：使用投影技术
5. **计算效率高**：线性代数运算

**N4SID vs 其他方法**：

| 方法 | 类型 | 优点 | 缺点 |
|------|------|------|------|
| 最小二乘法 | 参数估计 | 简单直观 | 需要模型结构 |
| 预测误差法 | 参数估计 | 精度高 | 需要迭代优化 |
| N4SID | 子空间 | 数值稳定、快速 | 线性模型 |
| ARX/ARMAX | 参数估计 | 成熟工具 | 输入输出形式 |

## 理论基础

### 1. 状态空间模型

**离散时间状态空间模型**：

$$\begin{aligned}
\mathbf{x}(k+1) &= \mathbf{A} \mathbf{x}(k) + \mathbf{B} \mathbf{u}(k) + \mathbf{w}(k) \\
\mathbf{y}(k) &= \mathbf{C} \mathbf{x}(k) + \mathbf{D} \mathbf{u}(k) + \mathbf{v}(k)
\end{aligned}$$

其中：
- $\mathbf{x}(k) \in \mathbb{R}^n$：状态向量（n维）
- $\mathbf{u}(k) \in \mathbb{R}^m$：输入向量（m维）
- $\mathbf{y}(k) \in \mathbb{R}^p$：输出向量（p维）
- $\mathbf{w}(k), \mathbf{v}(k)$：过程噪声和测量噪声
- $\mathbf{A}, \mathbf{B}, \mathbf{C}, \mathbf{D}$：系统矩阵

**辨识目标**：给定输入输出数据$\{u(k), y(k)\}_{k=1}^{N}$，估计矩阵$\mathbf{A}, \mathbf{B}, \mathbf{C}, \mathbf{D}$和状态序列$\{\mathbf{x}(k)\}$。

### 2. Hankel矩阵

Hankel矩阵是子空间方法的核心数据结构。

**输出Hankel矩阵**：

$$\mathbf{Y}_{0|2i-1} = \begin{bmatrix}
y(0) & y(1) & \cdots & y(j-1) \\
y(1) & y(2) & \cdots & y(j) \\
\vdots & \vdots & \ddots & \vdots \\
y(2i-1) & y(2i) & \cdots & y(j+2i-2)
\end{bmatrix}$$

**分块形式**：

$$\mathbf{Y}_{0|2i-1} = \begin{bmatrix}
\mathbf{Y}_p \\
\mathbf{Y}_f
\end{bmatrix}$$

其中：
- $\mathbf{Y}_p$：过去数据（past）
- $\mathbf{Y}_f$：未来数据（future）
- $i$：用户参数，通常取$i > n$

类似地构造输入Hankel矩阵$\mathbf{U}_{0|2i-1}$。

### 3. 可观测性矩阵

**可观测性矩阵**（Observability matrix）：

$$\mathbf{\Gamma}_i = \begin{bmatrix}
\mathbf{C} \\
\mathbf{CA} \\
\mathbf{CA}^2 \\
\vdots \\
\mathbf{CA}^{i-1}
\end{bmatrix} \in \mathbb{R}^{ip \times n}$$

**关键性质**：
$$\mathbf{Y}_f = \mathbf{\Gamma}_i \mathbf{X}_f + \mathbf{H}_i \mathbf{U}_f + \text{noise}$$

其中：
- $\mathbf{X}_f$：未来状态矩阵
- $\mathbf{H}_i$：Toeplitz矩阵（由Markov参数构成）

**目标**：从数据中估计$\mathbf{\Gamma}_i$和$\mathbf{X}_f$，然后提取$\mathbf{A}, \mathbf{C}$。

### 4. N4SID算法步骤

**Step 1: 构造Hankel矩阵**

从输入输出数据$\{u(k), y(k)\}_{k=0}^{N-1}$构造：
- $\mathbf{U}_p, \mathbf{U}_f$：输入的过去和未来
- $\mathbf{Y}_p, \mathbf{Y}_f$：输出的过去和未来

参数选择：
- $i$：用户参数，推荐$i = 10 \sim 20$
- $j$：样本数，$j = N - 2i + 1$

**Step 2: 投影（Projection）**

目标：从$\mathbf{Y}_f$中去除输入$\mathbf{U}_f$的直接影响，得到状态驱动的部分。

**正交投影**：
$$\mathbf{O}_i = \mathbf{Y}_f / \begin{bmatrix} \mathbf{U}_f \\ \mathbf{U}_p \\ \mathbf{Y}_p \end{bmatrix}$$

其中$\mathbf{A}/\mathbf{B}$表示$\mathbf{A}$在$\mathbf{B}$的列空间上的正交投影。

**计算方法**（QR分解）：

构造增广矩阵：
$$\begin{bmatrix}
\mathbf{U}_f \\
\mathbf{U}_p \\
\mathbf{Y}_p \\
\mathbf{Y}_f
\end{bmatrix} = \begin{bmatrix}
\mathbf{R}_{11} & 0 & 0 & 0 \\
\mathbf{R}_{21} & \mathbf{R}_{22} & 0 & 0 \\
\mathbf{R}_{31} & \mathbf{R}_{32} & \mathbf{R}_{33} & 0 \\
\mathbf{R}_{41} & \mathbf{R}_{42} & \mathbf{R}_{43} & \mathbf{R}_{44}
\end{bmatrix} \begin{bmatrix}
\mathbf{Q}_1^T \\
\mathbf{Q}_2^T \\
\mathbf{Q}_3^T \\
\mathbf{Q}_4^T
\end{bmatrix}$$

则：
$$\mathbf{O}_i = \mathbf{R}_{43} \mathbf{Q}_3^T$$

**Step 3: SVD分解**

对投影矩阵进行SVD：
$$\mathbf{O}_i = \mathbf{U}_s \mathbf{\Sigma}_s \mathbf{V}_s^T$$

其中$\mathbf{\Sigma}_s = \text{diag}(\sigma_1, \sigma_2, \ldots, \sigma_n)$，奇异值按降序排列。

**模型阶数选择**：

观察奇异值：
- 大的奇异值对应真实动态
- 小的奇异值对应噪声

选择$n$使得：
$$\frac{\sum_{i=1}^{n} \sigma_i}{\sum_{i=1}^{\text{all}} \sigma_i} > 0.95$$

或者观察奇异值图中的"拐点"（elbow）。

**Step 4: 估计可观测性矩阵和状态**

取前$n$个奇异值：
$$\mathbf{\Gamma}_i = \mathbf{U}_s(:, 1:n) \mathbf{\Sigma}_s(1:n, 1:n)^{1/2}$$

$$\mathbf{X}_f = \mathbf{\Sigma}_s(1:n, 1:n)^{1/2} \mathbf{V}_s(:, 1:n)^T$$

**Step 5: 估计系统矩阵A和C**

从可观测性矩阵提取：
$$\mathbf{C} = \mathbf{\Gamma}_i(1:p, :)$$

$$\mathbf{A} = \mathbf{\Gamma}_i^{\dagger}(1:(i-1)p, :) \mathbf{\Gamma}_i(p+1:ip, :)$$

其中$\mathbf{\Gamma}_i^{\dagger}$是Moore-Penrose伪逆。

**Step 6: 估计系统矩阵B和D**

线性最小二乘：
$$\begin{bmatrix}
\mathbf{B} \\
\mathbf{D}
\end{bmatrix} = \begin{bmatrix}
\mathbf{X}(k+1) \\
\mathbf{Y}(k)
\end{bmatrix} / \begin{bmatrix}
\mathbf{X}(k) \\
\mathbf{U}(k)
\end{bmatrix}$$

即：
$$\begin{bmatrix}
\hat{\mathbf{x}}(1) & \hat{\mathbf{x}}(2) & \cdots & \hat{\mathbf{x}}(N-1) \\
\mathbf{y}(0) & \mathbf{y}(1) & \cdots & \mathbf{y}(N-2)
\end{bmatrix} = \begin{bmatrix}
\mathbf{A} & \mathbf{B} \\
\mathbf{C} & \mathbf{D}
\end{bmatrix} \begin{bmatrix}
\hat{\mathbf{x}}(0) & \hat{\mathbf{x}}(1) & \cdots & \hat{\mathbf{x}}(N-2) \\
\mathbf{u}(0) & \mathbf{u}(1) & \cdots & \mathbf{u}(N-2)
\end{bmatrix}$$

使用最小二乘求解。

### 5. 模型验证

辨识出模型后，必须验证其有效性。

**验证指标**：

1. **拟合度（Fit percentage）**：
$$\text{Fit} = 100 \times \left(1 - \frac{\|\mathbf{y} - \hat{\mathbf{y}}\|}{\|\mathbf{y} - \bar{\mathbf{y}}\|}\right)$$

其中$\hat{\mathbf{y}}$是模型预测，$\bar{\mathbf{y}}$是均值。

2. **均方根误差（RMSE）**：
$$\text{RMSE} = \sqrt{\frac{1}{N}\sum_{k=1}^{N}(\mathbf{y}(k) - \hat{\mathbf{y}}(k))^2}$$

3. **归一化均方根误差（NRMSE）**：
$$\text{NRMSE} = \frac{\text{RMSE}}{\sigma_y}$$

其中$\sigma_y$是输出的标准差。

4. **Akaike信息准则（AIC）**：
$$\text{AIC} = 2n + N \ln(\text{RSS}/N)$$

其中$\text{RSS}$是残差平方和，$n$是参数个数。

**交叉验证**：
- 训练集：用于辨识
- 验证集：用于选择模型阶数
- 测试集：最终评估（不同工况）

**残差分析**：
- 白噪声检验：自相关函数
- 正态性检验：QQ图
- 独立性检验：与输入的互相关

### 6. 应用于渠道系统

**简化模型**：

对于单个渠段，输入输出关系为：
- 输入：$u(t)$（闸门开度）
- 输出：$y(t)$（下游水位）

线性化后可以建立状态空间模型：
$$\begin{bmatrix}
\Delta h(k+1) \\
\Delta Q(k+1)
\end{bmatrix} = \mathbf{A} \begin{bmatrix}
\Delta h(k) \\
\Delta Q(k)
\end{bmatrix} + \mathbf{B} \Delta u(k)$$

$$\Delta y(k) = \mathbf{C} \begin{bmatrix}
\Delta h(k) \\
\Delta Q(k)
\end{bmatrix}$$

**数据采集**：
- 激励信号设计：PRBS（伪随机二进制序列）、chirp信号
- 采样频率：满足Nyquist准则
- 数据长度：至少$N > 10n/p$（n是阶数，p是输出维数）

**工程应用**：
1. **模型预测控制（MPC）**：辨识模型用于预测
2. **自适应控制**：在线更新模型参数
3. **故障检测**：监控残差
4. **性能评估**：对比不同控制策略

## 实验设计

### Part 1: N4SID算法实现与验证

**实验目的**：实现N4SID算法，在简单系统上验证

**步骤**：
1. 生成标准测试系统（如二阶振荡系统）
2. 添加噪声
3. 应用N4SID辨识
4. 对比辨识模型与真实模型

**评价指标**：
- 特征值误差
- 频率响应对比
- 阶跃响应对比

### Part 2: 模型阶数选择

**实验目的**：研究如何选择合适的模型阶数

**方法**：
- 奇异值分析
- AIC/BIC准则
- 交叉验证

### Part 3: 渠道系统辨识

**实验目的**：将N4SID应用于渠道系统

**步骤**：
1. 使用Saint-Venant仿真生成"真实"数据
2. 设计激励信号（PRBS）
3. 应用N4SID辨识低阶模型
4. 验证模型精度

**对比**：
- 全阶模型（Saint-Venant）
- 辨识模型（N4SID）
- 降阶模型（POD）

### Part 4: 噪声鲁棒性与模型验证

**实验目的**：测试N4SID对噪声的鲁棒性

**场景**：
- 不同信噪比（SNR = 20, 10, 5 dB）
- 测量异常值
- 不同工况验证

## 工程意义

### 1. 为何需要系统辨识？

**场景1：模型不确定性**

物理建模存在诸多不确定性：
- 渠道糙率n随时间变化（淤积、植被）
- 实际几何与设计不符
- 闸门特性漂移

辨识可以从实际数据更新模型。

**场景2：复杂系统**

对于大型渠系：
- 数百个渠段
- 复杂拓扑结构
- 全物理建模不现实

辨识可以得到简洁的输入输出模型。

**场景3：控制器设计**

很多先进控制方法需要状态空间模型：
- MPC：需要预测模型
- LQG：需要状态空间形式
- H∞：需要传递函数

辨识提供控制器设计的基础。

### 2. N4SID的优势

**相比参数估计方法**：
- 不需要初值猜测
- 不需要迭代优化
- 数值稳定性好

**相比频域方法**：
- 直接得到状态空间形式
- 适合MIMO系统
- 处理瞬态响应

**相比神经网络**：
- 模型结构清晰
- 可解释性强
- 数据需求少

### 3. 实际应用建议

**数据采集**：
- 激励要充分（频率范围、幅值）
- 采样频率至少2-5倍最快动态
- 数据长度足够（至少覆盖主要时间常数）
- 预处理：去趋势、去异常值

**模型阶数**：
- 从奇异值图选择
- 交叉验证
- 偏向低阶（避免过拟合）
- 考虑物理意义（如2阶对应h和Q）

**模型更新**：
- 定期重新辨识（如每月）
- 在线递推更新（RLS、Kalman滤波）
- 多工况辨识（覆盖操作范围）

**验证**：
- 独立数据集测试
- 不同工况验证
- 长期追踪误差

### 4. 局限性

**线性假设**：
- N4SID只能辨识线性模型
- 强非线性系统需要其他方法（Hammerstein-Wiener、神经网络）

**数据质量要求**：
- 需要充分激励（持续激励条件）
- 对噪声敏感度中等
- 需要足够长的数据

**计算复杂度**：
- 大规模系统计算量大
- QR和SVD的复杂度

**可以结合其他方法**：
- 物理先验：约束参数范围
- 混合建模：物理+辨识
- 非线性扩展：局部线性化

## 参数说明

### 渠道参数
| 参数 | 数值 | 单位 |
|------|------|------|
| 长度 L | 1000 | m |
| 宽度 B | 5 | m |
| 坡度 i₀ | 0.001 | - |
| 糙率 n | 0.025 | s/m^(1/3) |
| 节点数 N | 51 | - |

### N4SID参数
| 参数 | 数值 | 说明 |
|------|------|------|
| 用户参数 i | 15 | Hankel矩阵块行数 |
| 模型阶数 n | 2-10 | 自动选择 |
| 数据长度 N | 500-2000 | 采样点数 |
| 采样时间 Ts | 10 s | 离散化时间步 |

### 激励信号参数
| 参数 | 数值 | 说明 |
|------|------|------|
| PRBS幅值 | ±0.2 | 闸门开度变化 |
| PRBS周期 | 20 s | 切换周期 |
| 基准开度 | 0.5 | 平衡点 |

### 噪声参数
| 参数 | 数值 | 说明 |
|------|------|------|
| 测量噪声 | SNR=20dB | 信噪比 |
| 噪声类型 | 高斯白噪声 | 统计特性 |

## 运行说明

```bash
python main.py
```

输出：
- `part1_n4sid_validation.png`: N4SID算法验证
- `part2_order_selection.png`: 模型阶数选择
- `part3_canal_identification.png`: 渠道系统辨识
- `part4_noise_robustness.png`: 噪声鲁棒性测试

## 总结

案例8展示了N4SID子空间辨识方法在渠道系统中的应用。关键要点：

1. **N4SID是数据驱动的黑盒辨识方法**，从输入输出数据构建状态空间模型
2. **基于SVD的数值方法**，无需迭代优化，数值稳定
3. **自动选择模型阶数**，通过奇异值分析
4. **适合线性MIMO系统**，是工业过程控制的标准工具
5. **需要充分激励和足够数据**，数据质量影响辨识精度
6. **辨识模型可用于MPC等先进控制**

N4SID与案例4-7的降阶方法不同：
- 降阶方法：已知高阶模型→简化为低阶模型
- N4SID：未知模型+数据→辨识低阶模型

两者可以结合：先用N4SID辨识，再用POD/DMD进一步降阶。

## 参考文献

1. Van Overschee, P., & De Moor, B. (1994). N4SID: Subspace algorithms for the identification of combined deterministic-stochastic systems. *Automatica*, 30(1), 75-93.

2. Van Overschee, P., & De Moor, B. (1996). *Subspace identification for linear systems: Theory—Implementation—Applications*. Springer Science & Business Media.

3. Verhaegen, M., & Verdult, V. (2007). *Filtering and system identification: a least squares approach*. Cambridge university press.

4. Katayama, T. (2005). *Subspace methods for system identification*. Springer Science & Business Media.

5. Ljung, L. (1999). *System identification: theory for the user* (2nd ed.). Prentice Hall.

6. Favoreel, W., De Moor, B., & Van Overschee, P. (2000). Subspace state space system identification for industrial processes. *Journal of Process Control*, 10(2-3), 149-155.
