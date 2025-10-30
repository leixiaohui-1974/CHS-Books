# 案例14：模型预测控制（MPC）

## 问题描述

运河和管道系统的控制面临多重挑战：
- **多变量耦合**：水位、流量相互影响
- **时间延迟**：水流传播需要时间
- **物理约束**：流量有上下限、水位不能溢出
- **扰动频繁**：降雨、用水需求变化
- **多目标优化**：既要跟踪目标，又要节能、平稳

传统控制方法的局限：
- **PID控制**：难以处理约束，多变量调参困难
- **LQR控制**：无法显式处理约束
- **前馈控制**：对模型精度要求高，鲁棒性差

**模型预测控制（MPC）**通过在线优化，显式处理约束，实现多目标协调，是水利工程中先进控制的首选方案。

---

## 理论基础

### 1. MPC核心思想

MPC的三大要素：

```
┌─────────────────────────────────────────────────────┐
│                  预测模型（Model）                    │
│     基于当前状态，预测未来N步的系统行为              │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│                滚动优化（Optimization）               │
│   在预测时域内，求解最优控制序列（考虑约束）          │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│                反馈校正（Feedback）                   │
│     只执行第一步控制，下一时刻根据新状态重新优化       │
└─────────────────────────────────────────────────────┘
```

**滚动时域策略**（Receding Horizon）：
- 在每个采样时刻，求解有限时域优化问题
- 只执行第一个控制动作
- 下一时刻，时域向前滚动，重新优化

这种"在线优化 + 反馈校正"的机制赋予MPC强大的鲁棒性。

---

### 2. 线性MPC数学描述

#### 2.1 预测模型

离散时间线性系统：
$$
\begin{aligned}
\mathbf{x}(k+1) &= \mathbf{A} \mathbf{x}(k) + \mathbf{B} \mathbf{u}(k) \\
\mathbf{y}(k) &= \mathbf{C} \mathbf{x}(k)
\end{aligned}
$$

在当前时刻 $k$，预测未来 $N_p$ 步（预测时域）的状态：
$$
\begin{aligned}
\mathbf{x}(k+1|k) &= \mathbf{A} \mathbf{x}(k) + \mathbf{B} \mathbf{u}(k|k) \\
\mathbf{x}(k+2|k) &= \mathbf{A} \mathbf{x}(k+1|k) + \mathbf{B} \mathbf{u}(k+1|k) \\
&\vdots \\
\mathbf{x}(k+N_p|k) &= \mathbf{A} \mathbf{x}(k+N_p-1|k) + \mathbf{B} \mathbf{u}(k+N_p-1|k)
\end{aligned}
$$

其中 $\mathbf{x}(k+i|k)$ 表示在时刻 $k$ 基于当前信息预测的 $k+i$ 时刻状态。

#### 2.2 优化目标

标准MPC的代价函数（二次型）：
$$
J = \sum_{i=1}^{N_p} \left\| \mathbf{y}(k+i|k) - \mathbf{r}(k+i) \right\|_{\mathbf{Q}}^2 + \sum_{i=0}^{N_c-1} \left\| \mathbf{u}(k+i|k) \right\|_{\mathbf{R}}^2 + \sum_{i=0}^{N_c-1} \left\| \Delta \mathbf{u}(k+i|k) \right\|_{\mathbf{S}}^2
$$

其中：
- $N_p$：预测时域（prediction horizon）
- $N_c$：控制时域（control horizon），$N_c \leq N_p$
- $\mathbf{r}(k+i)$：参考轨迹（setpoint）
- $\mathbf{Q}$：跟踪误差权重矩阵
- $\mathbf{R}$：控制量权重矩阵（抑制控制幅度）
- $\mathbf{S}$：控制增量权重矩阵（平滑控制，$\Delta \mathbf{u}(k) = \mathbf{u}(k) - \mathbf{u}(k-1)$）

#### 2.3 约束

MPC的最大优势：**显式处理约束**

**状态约束**：
$$
\mathbf{x}_{\min} \leq \mathbf{x}(k+i|k) \leq \mathbf{x}_{\max}, \quad i=1,\ldots,N_p
$$

**输出约束**：
$$
\mathbf{y}_{\min} \leq \mathbf{y}(k+i|k) \leq \mathbf{y}_{\max}, \quad i=1,\ldots,N_p
$$

**控制约束**：
$$
\mathbf{u}_{\min} \leq \mathbf{u}(k+i|k) \leq \mathbf{u}_{\max}, \quad i=0,\ldots,N_c-1
$$

**控制增量约束**（限制变化率）：
$$
\Delta \mathbf{u}_{\min} \leq \Delta \mathbf{u}(k+i|k) \leq \Delta \mathbf{u}_{\max}, \quad i=0,\ldots,N_c-1
$$

#### 2.4 优化问题

MPC在每个时刻求解以下优化问题：

$$
\begin{aligned}
\min_{\mathbf{U}} \quad & J(\mathbf{U}) \\
\text{s.t.} \quad & \mathbf{x}(k+i+1|k) = \mathbf{A} \mathbf{x}(k+i|k) + \mathbf{B} \mathbf{u}(k+i|k) \\
& \mathbf{y}(k+i|k) = \mathbf{C} \mathbf{x}(k+i|k) \\
& \mathbf{x}_{\min} \leq \mathbf{x}(k+i|k) \leq \mathbf{x}_{\max} \\
& \mathbf{y}_{\min} \leq \mathbf{y}(k+i|k) \leq \mathbf{y}_{\max} \\
& \mathbf{u}_{\min} \leq \mathbf{u}(k+i|k) \leq \mathbf{u}_{\max} \\
& \Delta \mathbf{u}_{\min} \leq \Delta \mathbf{u}(k+i|k) \leq \Delta \mathbf{u}_{\max}
\end{aligned}
$$

其中决策变量是控制序列：
$$
\mathbf{U} = \begin{bmatrix} \mathbf{u}(k|k) \\ \mathbf{u}(k+1|k) \\ \vdots \\ \mathbf{u}(k+N_c-1|k) \end{bmatrix}
$$

对于**线性系统+二次代价+线性约束**，这是一个**二次规划（QP）**问题，可以高效求解。

---

### 3. MPC矩阵形式（快速计算）

为了提高计算效率，将预测方程写成矩阵形式。

#### 3.1 预测矩阵

定义：
$$
\begin{aligned}
\mathbf{X} &= \begin{bmatrix} \mathbf{x}(k+1|k) \\ \mathbf{x}(k+2|k) \\ \vdots \\ \mathbf{x}(k+N_p|k) \end{bmatrix}, \quad
\mathbf{Y} = \begin{bmatrix} \mathbf{y}(k+1|k) \\ \mathbf{y}(k+2|k) \\ \vdots \\ \mathbf{y}(k+N_p|k) \end{bmatrix}, \quad
\mathbf{U} = \begin{bmatrix} \mathbf{u}(k|k) \\ \mathbf{u}(k+1|k) \\ \vdots \\ \mathbf{u}(k+N_c-1|k) \end{bmatrix}
\end{aligned}
$$

通过递推，可以得到：
$$
\mathbf{X} = \mathbf{S}_x \mathbf{x}(k) + \mathbf{S}_u \mathbf{U}
$$

其中预测矩阵：
$$
\mathbf{S}_x = \begin{bmatrix} \mathbf{A} \\ \mathbf{A}^2 \\ \vdots \\ \mathbf{A}^{N_p} \end{bmatrix}, \quad
\mathbf{S}_u = \begin{bmatrix}
\mathbf{B} & \mathbf{0} & \cdots & \mathbf{0} \\
\mathbf{A}\mathbf{B} & \mathbf{B} & \cdots & \mathbf{0} \\
\vdots & \vdots & \ddots & \vdots \\
\mathbf{A}^{N_p-1}\mathbf{B} & \mathbf{A}^{N_p-2}\mathbf{B} & \cdots & \mathbf{A}^{N_p-N_c}\mathbf{B}
\end{bmatrix}
$$

输出预测：
$$
\mathbf{Y} = \mathbf{C} \mathbf{X} = \mathbf{C} \mathbf{S}_x \mathbf{x}(k) + \mathbf{C} \mathbf{S}_u \mathbf{U} = \mathbf{\Psi} \mathbf{x}(k) + \mathbf{\Theta} \mathbf{U}
$$

#### 3.2 QP标准形式

代价函数可以写成：
$$
J = \frac{1}{2} \mathbf{U}^T \mathbf{H} \mathbf{U} + \mathbf{f}^T \mathbf{U} + \text{const}
$$

其中：
$$
\begin{aligned}
\mathbf{H} &= 2 (\mathbf{\Theta}^T \mathbf{Q} \mathbf{\Theta} + \mathbf{R}) \\
\mathbf{f} &= 2 \mathbf{\Theta}^T \mathbf{Q} (\mathbf{\Psi} \mathbf{x}(k) - \mathbf{R}_{\text{ref}})
\end{aligned}
$$

约束写成：
$$
\mathbf{A}_{\text{ineq}} \mathbf{U} \leq \mathbf{b}_{\text{ineq}}
$$

这是标准的QP问题，可以调用成熟的求解器（如`quadprog`、`OSQP`等）。

---

### 4. 稳定性保证

标准MPC不保证稳定性。为了保证稳定性，常用方法：

#### 4.1 终端约束

在预测时域末端添加约束：
$$
\mathbf{x}(k+N_p|k) = \mathbf{0} \quad \text{或} \quad \mathbf{x}(k+N_p|k) \in \mathcal{X}_f
$$

其中 $\mathcal{X}_f$ 是**终端不变集**。

#### 4.2 终端代价

在代价函数末端添加终端代价：
$$
J = \sum_{i=1}^{N_p-1} \left\| \mathbf{y}(k+i|k) - \mathbf{r}(k+i) \right\|_{\mathbf{Q}}^2 + \left\| \mathbf{x}(k+N_p|k) \right\|_{\mathbf{P}}^2 + \sum_{i=0}^{N_c-1} \left\| \mathbf{u}(k+i|k) \right\|_{\mathbf{R}}^2
$$

其中 $\mathbf{P}$ 是终端权重矩阵，通常取为代数Riccati方程的解。

#### 4.3 足够长的预测时域

在实践中，如果 $N_p$ 足够长，系统往往是稳定的（即使没有终端约束）。

---

### 5. 非线性MPC（NMPC）

对于非线性系统：
$$
\begin{aligned}
\mathbf{x}(k+1) &= f(\mathbf{x}(k), \mathbf{u}(k)) \\
\mathbf{y}(k) &= h(\mathbf{x}(k))
\end{aligned}
$$

NMPC求解**非线性规划（NLP）**问题：
$$
\begin{aligned}
\min_{\mathbf{U}} \quad & \sum_{i=1}^{N_p} \left\| h(\mathbf{x}(k+i|k)) - \mathbf{r}(k+i) \right\|_{\mathbf{Q}}^2 + \sum_{i=0}^{N_c-1} \left\| \mathbf{u}(k+i|k) \right\|_{\mathbf{R}}^2 \\
\text{s.t.} \quad & \mathbf{x}(k+i+1|k) = f(\mathbf{x}(k+i|k), \mathbf{u}(k+i|k)) \\
& \text{约束条件}
\end{aligned}
$$

求解方法：
- **序列二次规划（SQP）**：迭代线性化，求解一系列QP
- **内点法（Interior Point）**：大规模优化
- **梯度下降**：简单但可能陷入局部最优

NMPC计算量大，但对强非线性系统效果更好。

---

### 6. 运河系统MPC设计

#### 6.1 控制目标

- **水位跟踪**：维持目标水位，满足用水需求
- **流量平滑**：避免大幅度开关闸门
- **节能**：最小化泵站能耗
- **约束满足**：防止溢出、流量不超限

#### 6.2 预测模型

使用案例4-7中的降阶模型（ROM），或简化的Saint-Venant线性化模型。

例如，离散化的线性模型：
$$
\begin{bmatrix} h(k+1) \\ Q(k+1) \end{bmatrix} = \mathbf{A} \begin{bmatrix} h(k) \\ Q(k) \end{bmatrix} + \mathbf{B} u(k)
$$

其中 $u(k)$ 是闸门开度或泵流量。

#### 6.3 约束设置

- **水位约束**：$h_{\min} \leq h(k) \leq h_{\max}$（防溢出、保证最低水位）
- **流量约束**：$Q_{\min} \leq Q(k) \leq Q_{\max}$（物理限制）
- **控制约束**：$u_{\min} \leq u(k) \leq u_{\max}$（闸门开度0-100%）
- **变化率约束**：$|\Delta u(k)| \leq \Delta u_{\max}$（保护执行器）

#### 6.4 参数调优

- **$N_p$**：预测时域，通常取系统时间常数的2-5倍
- **$N_c$**：控制时域，$N_c = N_p$ 或 $N_c < N_p$（减少计算量）
- **$\mathbf{Q}$**：跟踪权重，越大越重视跟踪精度
- **$\mathbf{R}$**：控制权重，越大越平滑
- **$\mathbf{S}$**：控制增量权重，越大变化越慢

调参原则：先调 $N_p$，再调权重矩阵。

---

## 工程意义

### 1. MPC的优势

| 特性 | 传统控制（PID） | MPC |
|------|----------------|-----|
| **约束处理** | ❌ 无法显式处理 | ✅ 优化中直接考虑 |
| **多变量** | ⚠️ 解耦困难 | ✅ 天然支持MIMO |
| **前瞻性** | ❌ 反馈控制 | ✅ 预测未来，提前调节 |
| **多目标** | ❌ 单一目标 | ✅ 统一优化框架 |
| **扰动抑制** | ⚠️ 滞后响应 | ✅ 提前补偿 |
| **稳态精度** | ✅ 积分消除静差 | ✅ 优化保证 |

### 2. 水利工程应用场景

| 系统类型 | MPC应用 | 效果 |
|---------|---------|------|
| **灌溉渠道** | 水位控制、流量分配 | 节水20-30% |
| **城市供水** | 水压调节、泵站调度 | 节能15-25% |
| **水库调度** | 多目标优化（防洪+发电+生态） | 提高综合效益 |
| **污水处理** | 溶解氧控制、曝气优化 | 降低运行成本 |

### 3. 实际案例

**荷兰Delta运河MPC**：
- 100+km渠道，20+闸门
- 预测时域24小时
- 节水15%，水位偏差减少50%

**加州中央谷灌溉MPC**：
- 分布式MPC架构
- 实时优化闸门开度
- 节能18%，用户满意度提升

---

## 算法流程

```
初始化：
  - 建立预测模型（状态空间或传递函数）
  - 设定预测时域 Np、控制时域 Nc
  - 设定权重矩阵 Q, R, S
  - 设定约束 (x_min, x_max, u_min, u_max, ...)

主循环（每个采样时刻 k）：
  │
  ├─→ [状态测量/估计]
  │    - 读取传感器数据 y(k)
  │    - 状态估计（如EKF） → x̂(k)
  │
  ├─→ [构建优化问题]
  │    - 预测未来Np步：x(k+1|k), ..., x(k+Np|k)
  │    - 构建代价函数 J(U)
  │    - 构建约束矩阵 A_ineq, b_ineq
  │
  ├─→ [求解QP/NLP]
  │    - min_U  1/2 U' H U + f' U
  │    - s.t.   A_ineq U ≤ b_ineq
  │    - 得到最优控制序列 U* = [u*(k|k), u*(k+1|k), ...]
  │
  ├─→ [执行控制]
  │    - 只执行第一个控制 u(k) = u*(k|k)
  │    - 发送给执行器（闸门、泵）
  │
  ├─→ [反馈校正]
  │    - k = k+1
  │    - 时域向前滚动
  │    - 返回第一步
  │
  └─→ [终止条件]
       - 达到仿真时间或收敛
```

---

## 关键技术

### 1. 快速QP求解

- **稀疏性利用**：预测矩阵 $\mathbf{S}_u$ 是下三角，稀疏QP求解器可以大幅加速
- **热启动**：利用上一时刻的解作为初值
- **显式MPC**：离线计算分段线性控制律，在线查表（牺牲最优性换取速度）

### 2. 模型失配处理

- **自适应MPC**：在线辨识模型参数
- **鲁棒MPC**：考虑模型不确定性，min-max优化
- **学习MPC**：结合机器学习，数据驱动修正

### 3. 分布式MPC

对于大规模系统（长渠道、多闸门）：
- **分散式MPC**：每个子系统独立优化，忽略耦合
- **分布式MPC**：子系统协同优化，通过通信共享信息
- **分层MPC**：上层优化全局目标，下层执行局部控制

---

## 代码实现说明

### Part 1: 线性MPC基础
- 简单的2D系统（质量-弹簧-阻尼）
- 展示MPC的预测-优化-反馈循环
- 对比有/无约束的MPC性能

### Part 2: 运河系统MPC控制
- 基于线性化的运河模型
- 水位跟踪 + 流量平滑
- 处理物理约束（水位上下限、流量限制）

### Part 3: 约束处理与优化
- 展示约束违背的后果
- 软约束 vs 硬约束
- 可行性保证策略

### Part 4: 多目标MPC
- 同时优化：水位跟踪 + 节能 + 平滑
- 权重矩阵调参
- Pareto前沿分析

---

## 性能指标

1. **跟踪误差（ISE）**：
   $$
   \text{ISE} = \sum_{k=0}^{N} (y(k) - r(k))^2
   $$

2. **控制能量**：
   $$
   \text{Energy} = \sum_{k=0}^{N} u(k)^2
   $$

3. **约束违背率**：
   $$
   \text{Violation Rate} = \frac{\# \text{约束违背}}{\# \text{总时间步}} \times 100\%
   $$

4. **计算时间**：单步优化耗时（ms），判断实时性

---

## 参考文献

1. Maciejowski, J. M. (2002). "Predictive Control with Constraints"
2. Camacho, E. F., & Alba, C. B. (2013). "Model Predictive Control"
3. Rawlings, J. B., et al. (2017). "Model Predictive Control: Theory, Computation, and Design"
4. Maestre, J. M., & Negenborn, R. R. (2014). "Distributed Model Predictive Control Made Easy"
5. Litrico, X., et al. (2010). "Automatic Control of Open-Channel Flow Using Model Predictive Control"

---

## 运行说明

```bash
cd /home/user/CHS-Books/books/canal-pipeline-control/code/examples/case_14_mpc_control
python main.py
```

生成4个PNG图像文件：
- `part1_linear_mpc.png` - 线性MPC基础演示
- `part2_canal_mpc.png` - 运河系统MPC控制
- `part3_constraint_handling.png` - 约束处理对比
- `part4_multi_objective_mpc.png` - 多目标MPC优化
