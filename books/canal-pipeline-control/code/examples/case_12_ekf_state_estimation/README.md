# 案例12：扩展卡尔曼滤波状态估计

## 问题描述

在实际的运河和管道控制系统中，我们往往无法直接测量所有需要的状态变量，或者测量值受到噪声干扰。例如：
- 只能在有限位置安装水位传感器
- 流量传感器可能存在测量噪声
- 某些状态（如渠底摩阻系数）无法直接测量
- 传感器可能存在故障或漂移

**状态估计**的目标是利用有限的、含噪声的测量数据，结合系统的数学模型，最优地估计出系统的完整状态。

卡尔曼滤波器是最优状态估计的经典方法，而扩展卡尔曼滤波（EKF）将其推广到非线性系统，是水利工程中数字孪生技术的核心组件。

---

## 理论基础

### 1. 卡尔曼滤波（Kalman Filter）

对于**线性离散系统**：

$$
\begin{aligned}
\mathbf{x}_{k} &= \mathbf{A} \mathbf{x}_{k-1} + \mathbf{B} \mathbf{u}_{k-1} + \mathbf{w}_{k-1} \quad \text{(状态方程)} \\
\mathbf{y}_{k} &= \mathbf{C} \mathbf{x}_{k} + \mathbf{v}_{k} \quad \text{(观测方程)}
\end{aligned}
$$

其中：
- $\mathbf{x}_k \in \mathbb{R}^n$ 是状态向量
- $\mathbf{y}_k \in \mathbb{R}^p$ 是测量向量
- $\mathbf{u}_k \in \mathbb{R}^m$ 是控制输入
- $\mathbf{w}_k \sim \mathcal{N}(0, \mathbf{Q})$ 是过程噪声（系统不确定性）
- $\mathbf{v}_k \sim \mathcal{N}(0, \mathbf{R})$ 是测量噪声

**卡尔曼滤波递推算法**分为两步：

#### 1.1 预测步（Prediction）

基于上一时刻的估计和系统模型，预测当前状态：

$$
\begin{aligned}
\hat{\mathbf{x}}_{k|k-1} &= \mathbf{A} \hat{\mathbf{x}}_{k-1|k-1} + \mathbf{B} \mathbf{u}_{k-1} \quad \text{(先验状态估计)} \\
\mathbf{P}_{k|k-1} &= \mathbf{A} \mathbf{P}_{k-1|k-1} \mathbf{A}^T + \mathbf{Q} \quad \text{(先验协方差)}
\end{aligned}
$$

#### 1.2 更新步（Update）

当新的测量到来时，融合测量信息修正预测：

$$
\begin{aligned}
\mathbf{K}_k &= \mathbf{P}_{k|k-1} \mathbf{C}^T \left( \mathbf{C} \mathbf{P}_{k|k-1} \mathbf{C}^T + \mathbf{R} \right)^{-1} \quad \text{(卡尔曼增益)} \\
\hat{\mathbf{x}}_{k|k} &= \hat{\mathbf{x}}_{k|k-1} + \mathbf{K}_k \left( \mathbf{y}_k - \mathbf{C} \hat{\mathbf{x}}_{k|k-1} \right) \quad \text{(后验状态估计)} \\
\mathbf{P}_{k|k} &= (\mathbf{I} - \mathbf{K}_k \mathbf{C}) \mathbf{P}_{k|k-1} \quad \text{(后验协方差)}
\end{aligned}
$$

**关键概念**：
- **先验估计**（a priori）：基于模型预测的估计，记为 $\hat{\mathbf{x}}_{k|k-1}$
- **后验估计**（a posteriori）：融合测量后的估计，记为 $\hat{\mathbf{x}}_{k|k}$
- **卡尔曼增益** $\mathbf{K}_k$：权衡模型预测和测量的可信度
  - 当 $\mathbf{R}$ 很小（测量准确）时，$\mathbf{K}_k$ 大，更相信测量
  - 当 $\mathbf{Q}$ 很小（模型准确）时，$\mathbf{K}_k$ 小，更相信模型

---

### 2. 扩展卡尔曼滤波（Extended Kalman Filter, EKF）

对于**非线性系统**：

$$
\begin{aligned}
\mathbf{x}_{k} &= f(\mathbf{x}_{k-1}, \mathbf{u}_{k-1}) + \mathbf{w}_{k-1} \quad \text{(非线性状态方程)} \\
\mathbf{y}_{k} &= h(\mathbf{x}_{k}) + \mathbf{v}_{k} \quad \text{(非线性观测方程)}
\end{aligned}
$$

EKF的核心思想是**局部线性化**：在当前估计点附近对非线性函数进行泰勒展开，取一阶项（雅可比矩阵）。

#### 2.1 雅可比矩阵

定义状态转移雅可比矩阵 $\mathbf{F}_k$ 和观测雅可比矩阵 $\mathbf{H}_k$：

$$
\mathbf{F}_k = \left. \frac{\partial f}{\partial \mathbf{x}} \right|_{\mathbf{x} = \hat{\mathbf{x}}_{k-1|k-1}} \quad , \quad
\mathbf{H}_k = \left. \frac{\partial h}{\partial \mathbf{x}} \right|_{\mathbf{x} = \hat{\mathbf{x}}_{k|k-1}}
$$

#### 2.2 EKF递推算法

**预测步**：

$$
\begin{aligned}
\hat{\mathbf{x}}_{k|k-1} &= f(\hat{\mathbf{x}}_{k-1|k-1}, \mathbf{u}_{k-1}) \\
\mathbf{P}_{k|k-1} &= \mathbf{F}_k \mathbf{P}_{k-1|k-1} \mathbf{F}_k^T + \mathbf{Q}
\end{aligned}
$$

**更新步**：

$$
\begin{aligned}
\mathbf{K}_k &= \mathbf{P}_{k|k-1} \mathbf{H}_k^T \left( \mathbf{H}_k \mathbf{P}_{k|k-1} \mathbf{H}_k^T + \mathbf{R} \right)^{-1} \\
\hat{\mathbf{x}}_{k|k} &= \hat{\mathbf{x}}_{k|k-1} + \mathbf{K}_k \left( \mathbf{y}_k - h(\hat{\mathbf{x}}_{k|k-1}) \right) \\
\mathbf{P}_{k|k} &= (\mathbf{I} - \mathbf{K}_k \mathbf{H}_k) \mathbf{P}_{k|k-1}
\end{aligned}
$$

**EKF的局限性**：
1. 一阶泰勒近似可能不准确（高度非线性系统）
2. 需要计算雅可比矩阵（复杂系统可能难以解析求导）
3. 线性化误差可能导致协方差估计不准确

---

### 3. 无迹卡尔曼滤波（Unscented Kalman Filter, UKF）

UKF通过**确定性采样**（Unscented Transform）避免显式线性化：

#### 3.1 Unscented Transform原理

对于随机变量 $\mathbf{x} \sim \mathcal{N}(\bar{\mathbf{x}}, \mathbf{P})$ 经过非线性变换 $\mathbf{y} = g(\mathbf{x})$：

1. **选择sigma点**：在均值周围选择 $2n+1$ 个采样点
   $$
   \begin{aligned}
   \mathcal{X}^{(0)} &= \bar{\mathbf{x}} \\
   \mathcal{X}^{(i)} &= \bar{\mathbf{x}} + \left( \sqrt{(n+\lambda)\mathbf{P}} \right)_i, \quad i=1,\ldots,n \\
   \mathcal{X}^{(i+n)} &= \bar{\mathbf{x}} - \left( \sqrt{(n+\lambda)\mathbf{P}} \right)_i, \quad i=1,\ldots,n
   \end{aligned}
   $$
   其中 $\lambda = \alpha^2(n+\kappa) - n$ 是缩放参数

2. **传播sigma点**：通过非线性函数
   $$
   \mathcal{Y}^{(i)} = g(\mathcal{X}^{(i)})
   $$

3. **统计重构**：用加权平均计算均值和协方差
   $$
   \begin{aligned}
   \bar{\mathbf{y}} &= \sum_{i=0}^{2n} W_m^{(i)} \mathcal{Y}^{(i)} \\
   \mathbf{P}_y &= \sum_{i=0}^{2n} W_c^{(i)} (\mathcal{Y}^{(i)} - \bar{\mathbf{y}})(\mathcal{Y}^{(i)} - \bar{\mathbf{y}})^T
   \end{aligned}
   $$

权重设置：
$$
\begin{aligned}
W_m^{(0)} &= \frac{\lambda}{n+\lambda}, \quad W_c^{(0)} = \frac{\lambda}{n+\lambda} + (1-\alpha^2+\beta) \\
W_m^{(i)} &= W_c^{(i)} = \frac{1}{2(n+\lambda)}, \quad i=1,\ldots,2n
\end{aligned}
$$

典型参数：$\alpha=0.001$（控制sigma点分布），$\beta=2$（高斯分布最优），$\kappa=0$。

#### 3.2 UKF递推算法

**预测步**：
1. 生成sigma点：$\mathcal{X}_{k-1|k-1}$
2. 传播：$\mathcal{X}_{k|k-1}^{(i)} = f(\mathcal{X}_{k-1|k-1}^{(i)}, \mathbf{u}_{k-1})$
3. 重构：
   $$
   \begin{aligned}
   \hat{\mathbf{x}}_{k|k-1} &= \sum_{i=0}^{2n} W_m^{(i)} \mathcal{X}_{k|k-1}^{(i)} \\
   \mathbf{P}_{k|k-1} &= \sum_{i=0}^{2n} W_c^{(i)} (\mathcal{X}_{k|k-1}^{(i)} - \hat{\mathbf{x}}_{k|k-1})(\mathcal{X}_{k|k-1}^{(i)} - \hat{\mathbf{x}}_{k|k-1})^T + \mathbf{Q}
   \end{aligned}
   $$

**更新步**：
1. 传播观测：$\mathcal{Y}_{k|k-1}^{(i)} = h(\mathcal{X}_{k|k-1}^{(i)})$
2. 重构观测统计：
   $$
   \begin{aligned}
   \hat{\mathbf{y}}_{k|k-1} &= \sum_{i=0}^{2n} W_m^{(i)} \mathcal{Y}_{k|k-1}^{(i)} \\
   \mathbf{P}_{yy} &= \sum_{i=0}^{2n} W_c^{(i)} (\mathcal{Y}_{k|k-1}^{(i)} - \hat{\mathbf{y}}_{k|k-1})(\mathcal{Y}_{k|k-1}^{(i)} - \hat{\mathbf{y}}_{k|k-1})^T + \mathbf{R} \\
   \mathbf{P}_{xy} &= \sum_{i=0}^{2n} W_c^{(i)} (\mathcal{X}_{k|k-1}^{(i)} - \hat{\mathbf{x}}_{k|k-1})(\mathcal{Y}_{k|k-1}^{(i)} - \hat{\mathbf{y}}_{k|k-1})^T
   \end{aligned}
   $$
3. 卡尔曼更新：
   $$
   \begin{aligned}
   \mathbf{K}_k &= \mathbf{P}_{xy} \mathbf{P}_{yy}^{-1} \\
   \hat{\mathbf{x}}_{k|k} &= \hat{\mathbf{x}}_{k|k-1} + \mathbf{K}_k (\mathbf{y}_k - \hat{\mathbf{y}}_{k|k-1}) \\
   \mathbf{P}_{k|k} &= \mathbf{P}_{k|k-1} - \mathbf{K}_k \mathbf{P}_{yy} \mathbf{K}_k^T
   \end{aligned}
   $$

**UKF的优势**：
- 精度达到二阶（EKF只有一阶）
- 不需要计算雅可比矩阵
- 对高度非线性系统更鲁棒

---

### 4. 运河系统状态估计问题

#### 4.1 非线性运河模型

简化的单渠段动态模型（基于Saint-Venant方程简化）：

**状态方程**：
$$
\begin{aligned}
\frac{dh}{dt} &= \frac{Q_{in} - Q_{out}}{A_s} - \frac{C_d \cdot w \cdot \sqrt{2g}}{A_s} \cdot h^{3/2} \\
\frac{dQ_{out}}{dt} &= \frac{g \cdot A_c}{L} (h - h_{ds}) - \frac{f \cdot Q_{out}^2}{2 D_h A_c}
\end{aligned}
$$

其中：
- $h$ = 水位 (m)
- $Q_{out}$ = 出流流量 (m³/s)
- $Q_{in}$ = 入流流量 (控制输入，m³/s)
- $A_s$ = 水面面积 (m²)
- $A_c$ = 过流断面积 (m²)
- $C_d$ = 堰流系数
- $f$ = 摩阻系数
- $L$ = 渠段长度 (m)
- $h_{ds}$ = 下游水位 (m)

**非线性特性**：
- 堰流项 $h^{3/2}$
- 摩阻项 $Q_{out}^2$

#### 4.2 测量方程

假设我们可以测量：
1. 上游水位 $h$ （有噪声）
2. 部分位置的流量 $Q$ （有噪声）

$$
\mathbf{y}_k = \begin{bmatrix} h_k \\ Q_{out,k} \end{bmatrix} + \mathbf{v}_k
$$

#### 4.3 实际应用场景

**场景1：传感器故障诊断**
- 利用冗余传感器和模型预测检测异常
- 当某传感器失效时，仍能维持状态估计

**场景2：未测量状态重构**
- 通过有限测点推断整个渠道的水位分布
- 估计难以直接测量的参数（如摩阻系数）

**场景3：数字孪生**
- 实时状态估计 + 模型预测 = 数字孪生
- 支持预测性维护和优化控制

---

## 工程意义

### 1. 为什么需要状态估计？

**传统方法的局限**：
- **纯测量**：传感器数量有限、成本高、存在噪声
- **纯仿真**：模型误差、参数不确定性、初始条件不准

**状态估计的优势**：
- **数据融合**：结合模型和测量的优点
- **最优性**：在统计意义上最小化估计误差
- **容错性**：部分传感器故障仍能工作

### 2. 卡尔曼滤波的工程价值

| 应用领域 | 具体场景 |
|---------|---------|
| **水利调度** | 实时水情监测、洪水预报、水库调度 |
| **输水管道** | 泄漏检测、压力状态监测、阀门优化 |
| **灌溉系统** | 土壤墒情估计、需水预测、精准灌溉 |
| **污水处理** | 水质参数软测量、过程优化控制 |

### 3. EKF vs UKF选择准则

| 特性 | EKF | UKF |
|-----|-----|-----|
| **适用性** | 弱非线性系统 | 强非线性系统 |
| **计算量** | 较小（需要求导） | 较大（2n+1次函数评估） |
| **精度** | 一阶近似 | 二阶近似 |
| **实现难度** | 需要推导雅可比 | 无需求导，实现简单 |
| **工程推荐** | 实时性要求高 | 精度要求高 |

---

## 算法流程图

```python
初始化：x̂₀, P₀, Q, R
    │
    ├─→ [预测步 Prediction]
    │   ├─ 状态预测：x̂ₖ₍ₖ₋₁₎ = f(x̂ₖ₋₁₍ₖ₋₁₎, uₖ₋₁)
    │   ├─ 雅可比：Fₖ = ∂f/∂x (EKF) 或 Sigma点采样 (UKF)
    │   └─ 协方差预测：Pₖ₍ₖ₋₁₎ = FₖPₖ₋₁₍ₖ₋₁₎Fₖᵀ + Q
    │
    ├─→ [更新步 Update] (当测量到来)
    │   ├─ 观测预测：ŷₖ₍ₖ₋₁₎ = h(x̂ₖ₍ₖ₋₁₎)
    │   ├─ 雅可比：Hₖ = ∂h/∂x (EKF) 或 Sigma点观测 (UKF)
    │   ├─ 卡尔曼增益：Kₖ = Pₖ₍ₖ₋₁₎Hₖᵀ(HₖPₖ₍ₖ₋₁₎Hₖᵀ + R)⁻¹
    │   ├─ 状态更新：x̂ₖ₍ₖ₎ = x̂ₖ₍ₖ₋₁₎ + Kₖ(yₖ - ŷₖ₍ₖ₋₁₎)
    │   └─ 协方差更新：Pₖ₍ₖ₎ = (I - KₖHₖ)Pₖ₍ₖ₋₁₎
    │
    └─→ 返回第一步，k = k+1
```

---

## 代码实现说明

### Part 1: 标量系统EKF演示
- 经典的非线性标量系统（Sensor Fusion问题）
- 展示EKF的预测-更新循环
- 可视化先验/后验估计、协方差演化

### Part 2: 运河系统状态估计
- 基于Saint-Venant简化模型
- 双状态估计（水位 + 流量）
- 处理强非线性（堰流 + 摩阻）

### Part 3: 多传感器融合
- 3个水位传感器 + 1个流量传感器
- 演示传感器冗余的优势
- 模拟传感器故障场景

### Part 4: EKF vs UKF性能对比
- 相同运河系统，不同滤波器
- 对比估计精度和计算时间
- 给出工程选择建议

---

## 性能指标

1. **估计误差（RMSE）**：
   $$
   \text{RMSE} = \sqrt{\frac{1}{N} \sum_{k=1}^{N} (\hat{x}_k - x_k)^2}
   $$

2. **一致性检验（NIS）**：归一化新息平方（Normalized Innovation Squared）
   $$
   \epsilon_k = (\mathbf{y}_k - \hat{\mathbf{y}}_k)^T \mathbf{S}_k^{-1} (\mathbf{y}_k - \hat{\mathbf{y}}_k)
   $$
   其中 $\mathbf{S}_k = \mathbf{H}_k \mathbf{P}_{k|k-1} \mathbf{H}_k^T + \mathbf{R}$ 是新息协方差。

   理论上 $\epsilon_k$ 应服从 $\chi^2$ 分布，用于检验滤波器是否一致。

3. **计算效率**：单步运行时间（ms）

---

## 参考文献

1. Kalman, R. E. (1960). "A New Approach to Linear Filtering and Prediction Problems"
2. Julier, S. J., & Uhlmann, J. K. (1997). "New extension of the Kalman filter to nonlinear systems"
3. Simon, D. (2006). "Optimal State Estimation: Kalman, H∞, and Nonlinear Approaches"
4. Durán, R. et al. (2017). "State estimation techniques in water distribution networks"
5. Litrico, X., & Fromion, V. (2009). "Modeling and Control of Hydrosystems"

---

## 运行说明

```bash
cd /home/user/CHS-Books/books/canal-pipeline-control/code/examples/case_12_ekf_state_estimation
python main.py
```

生成4个PNG图像文件：
- `part1_scalar_ekf.png` - 标量系统EKF演示
- `part2_canal_estimation.png` - 运河状态估计
- `part3_sensor_fusion.png` - 多传感器融合
- `part4_ekf_vs_ukf.png` - EKF与UKF对比
