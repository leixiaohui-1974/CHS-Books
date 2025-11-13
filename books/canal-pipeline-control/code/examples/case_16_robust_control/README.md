# 案例16：鲁棒控制（H∞ & 滑模控制）

## 1. 案例简介

本案例演示**鲁棒控制**技术在运河系统中的应用。鲁棒控制是一类专门处理系统不确定性和外部扰动的控制方法，能够在参数摄动、未建模动态、外部干扰等不利因素下保持良好的性能。

本案例重点介绍两种经典的鲁棒控制方法：
1. **H∞控制**：频域鲁棒控制，优化最坏情况下的性能
2. **滑模控制**：时域鲁棒控制，基于变结构系统理论

### 应用场景

在运河-管道系统中，鲁棒控制适用于以下场景：

1. **参数不确定性**：渠道糙率、底坡等参数存在±20%的误差
2. **未建模动态**：简化模型忽略的高频动态、非线性效应
3. **外部扰动**：降雨、渗漏、侧向入流等随机扰动
4. **工况变化**：流量、水位的大范围变化导致工作点迁移
5. **执行器约束**：闸门开度限制、响应延迟

### 关键优势

- ✅ **保证性能**：在不确定性范围内保证闭环稳定和性能指标
- ✅ **无需在线辨识**：离线设计，在线直接应用（不同于自适应控制）
- ✅ **抗扰能力强**：对外部扰动和测量噪声有强抑制能力
- ✅ **理论完备**：有严格的数学理论支撑（H∞优化、Lyapunov稳定性）

---

## 2. H∞控制理论

### 2.1 H∞控制基本思想

**核心目标**：在最坏的扰动情况下，使系统输出偏差最小化。

```python
给定系统：
    x' = Ax + B₁w + B₂u
    z = C₁x + D₁₁w + D₁₂u
    y = C₂x + D₂₁w

其中：
    x: 状态
    u: 控制输入
    w: 扰动输入（外生、最坏情况）
    z: 被控输出（期望优化的性能指标）
    y: 测量输出

H∞目标：设计控制器 u=K(s)y 使得：
    ||T_zw||_∞ = sup_{w≠0} ||z||₂ / ||w||₂ < γ

即：从扰动w到输出z的传递函数的H∞范数小于γ
```

**物理意义**：
- 如果 `||T_zw||_∞ < γ`，则对任何能量有限的扰动w，输出z的能量被放大不超过γ倍
- γ越小，鲁棒性越好（扰动抑制能力强）
- γ = ∞ 相当于无约束（普通控制）

### 2.2 标准H∞问题

**问题设定**：

```python
      w ───→ ┌─────────┐ ───→ z
              │  P(s)   │
      u ───→ │ (对象) │ ───→ y
              └─────────┘
                  │
                  ↓
              ┌─────────┐
              │  K(s)   │
              │ (控制器)│
              └─────────┘
```

系统P(s)的状态空间表示：
```json
P(s) = [ A  | B₁  B₂ ]
        [ ---|--------- ]
        [ C₁ | D₁₁ D₁₂ ]
        [ C₂ | D₂₁  0  ]
```

**设计目标**：找到控制器K(s)使得：
1. 闭环系统稳定
2. `||F_l(P, K)||_∞ < γ`（从w到z的闭环传递函数）

### 2.3 H∞控制器求解

#### 方法1：代数Riccati方程（ARE）

经典H∞控制器通过求解两个Riccati方程得到：

**状态反馈H∞控制器：**
```python
求解ARE：
    A'X + XA + C₁'C₁ + X(γ⁻²B₁B₁' - B₂B₂')X = 0

控制律：
    u = -B₂'X·x

充要条件：
    1. (A, B₂) 可稳定
    2. (C₁, A) 可检测
    3. X ≥ 0
```

**输出反馈H∞控制器：**
```python
需要同时求解两个Riccati方程（状态反馈 + 观测器）

控制器形式：
    ẋ_c = A_c·x_c + B_c·y
    u = C_c·x_c + D_c·y
```

#### 方法2：LMI（线性矩阵不等式）

现代H∞控制器设计多采用LMI方法：

```json
存在控制器 K(s) 使得 ||T_zw||_∞ < γ 等价于存在矩阵 P>0 使得：

[ A'P + PA + C₁'C₁    PB₁ ]
[                          ] < 0
[      B₁'P         -γ²I  ]

优点：
- 可以加入额外约束（极点配置、H₂性能、执行器饱和等）
- 数值稳定性好
- 容易扩展到多目标优化
```

### 2.4 混合灵敏度问题

工程中常用的H∞设计框架是**混合灵敏度问题**：

```python
目标：同时优化三个传递函数

||W_S(s)·S(s)||_∞ < 1  （跟踪性能）
||W_T(s)·T(s)||_∞ < 1  （鲁棒稳定性）
||W_U(s)·K(s)S(s)||_∞ < 1  （控制能量）

其中：
    S(s) = (I+GK)⁻¹ : 灵敏度函数（跟踪误差对参考输入的响应）
    T(s) = GK(I+GK)⁻¹ : 补灵敏度函数（输出对参考输入的响应）
    K(s)S(s) : 控制灵敏度函数

    W_S, W_T, W_U : 频率加权函数（设计者指定）
```

**加权函数选择指南**：

```python
# 低频段（<0.01 rad/s）：跟踪性能
W_S(s) = (s/M_s + ω_b) / (s + ω_b·ε)
    M_s: 峰值灵敏度（通常1.5-2.0）
    ω_b: 带宽（期望的响应速度）
    ε: 小常数（0.001）

# 高频段（>10 rad/s）：鲁棒稳定性和噪声抑制
W_T(s) = (s + ω_b/M_t) / (ε·s + ω_b)
    M_t: 高频增益（通常0.1-0.5）

# 全频段：控制能量限制
W_U(s) = ρ
    ρ: 控制惩罚权重（0.01-1.0）
```python

---

## 3. 滑模控制理论

### 3.1 滑模控制基本思想

**核心思想**：通过设计特殊的切换控制律，使系统状态在有限时间内到达**滑模面**，然后沿着滑模面滑向平衡点。

```
系统：
    ẋ = f(x,t) + g(x,t)·u + d(t)

滑模面：
    s(x) = 0  （例如：s = c'·x）

控制律：
    u = u_eq + u_sw

    u_eq: 等效控制（维持在滑模面上）
    u_sw: 切换控制（驱动状态到达滑模面）

切换律：
    u_sw = -K·sgn(s)  （符号函数）
```python

**滑模控制的三个阶段**：
1. **到达阶段**：从初始状态到达滑模面
2. **滑动阶段**：沿滑模面运动到平衡点
3. **平衡阶段**：保持在平衡点附近

### 3.2 滑模面设计

滑模面决定了滑动模态的动态特性。

#### 线性滑模面

最简单的形式：
```
s = c'·x = c₁x₁ + c₂x₂ + ... + c_n·x_n = 0

选择原则：
- 使得滑动模态（s=0约束下的动态）是稳定的
- 期望的收敛速度快
```python

#### 积分滑模面

包含积分项，消除稳态误差：
```
s = c'·x + λ∫(x-x_d)dt

优点：
- 零稳态误差
- 对常值扰动有更好的抑制
```python

#### 终端滑模面

有限时间收敛：
```
s = x₁ + β|x₂|^α·sgn(x₂)

其中 0 < α < 1

特点：
- 状态在有限时间内精确到达原点（不仅仅是渐近收敛）
- 收敛时间可预先计算
```python

### 3.3 到达条件

确保系统状态能够到达滑模面的充分条件。

#### 经典到达条件

```
s·ṡ < -η|s|  （η > 0）

推导：
    d/dt(½s²) = s·ṡ < -η|s| = -η·√(2·½s²)

积分后得到有限时间到达：
    t_reach ≤ |s(0)| / η
```python

#### Lyapunov到达条件

```
选择Lyapunov函数：
    V = ½s²

要求：
    V̇ = s·ṡ ≤ -k·s²  （k > 0）

这保证了指数收敛：s(t) = s(0)·exp(-kt)
```python

### 3.4 抖振问题与解决

**抖振（Chattering）**：由于符号函数的不连续切换，导致高频振荡。

**原因**：
- 符号函数sgn(s)在s=0处不连续
- 采样延迟、执行器惯性
- 测量噪声

**解决方法**：

#### (1) 边界层法
```
用饱和函数代替符号函数：
    sgn(s) → sat(s/φ) = { s/φ,     |s|<φ
                          sgn(s),  |s|≥φ

其中φ是边界层厚度
```python

#### (2) 高阶滑模控制
```
使用高阶导数信息平滑控制：
    u = u(s, ṡ, s̈, ...)

例如Super-Twisting算法（二阶滑模）：
    u = -k₁|s|^(1/2)·sgn(s) + u₁
    u̇₁ = -k₂·sgn(s)

连续控制，无抖振
```python

#### (3) 模糊滑模控制
```
用模糊逻辑平滑切换增益：
    u_sw = -K(s)·sat(s/φ)

其中K(s)根据|s|的大小动态调整
```python

---

## 4. 运河系统的鲁棒控制设计

### 4.1 运河系统不确定性建模

#### 参数不确定性

```
标称模型：
    ẋ = A₀·x + B₀·u

实际模型：
    ẋ = (A₀ + ΔA)·x + (B₀ + ΔB)·u

其中：
    ΔA ∈ [-α·A₀, α·A₀]  （例如α=0.2表示±20%不确定性）
    ΔB ∈ [-β·B₀, β·B₀]
```python

**运河系统的主要不确定参数**：
- 糙率系数n：±30%（植物生长、淤积）
- 底坡S₀：±10%（测量误差、淤积）
- 渠道几何：±15%（断面不规则、老化）

#### 外部扰动

```
ẋ = A·x + B·u + E·d(t)

其中d(t)包括：
    - 侧向入流：d_lateral(t)
    - 降雨径流：d_rain(t)
    - 渗漏损失：d_seepage(t)
    - 蒸发损失：d_evap(t)

假设：||d||₂ ≤ D_max（能量有界）
```python

### 4.2 H∞控制器设计步骤

#### Step 1：建立广义对象P(s)

```python
# 定义性能输出 z
z = [W_S·e,    # 跟踪误差（加权）
     W_U·u]    # 控制输入（加权）

# 定义扰动输入 w
w = [r,        # 参考输入
     d]        # 外部扰动

# 构建状态空间模型
A = ...  # 系统矩阵
B1 = ... # 扰动输入矩阵
B2 = ... # 控制输入矩阵
C1 = ... # 性能输出矩阵
C2 = ... # 测量输出矩阵
```python

#### Step 2：选择加权函数

```python
# 运河系统的典型加权函数
from scipy import signal

# 跟踪性能加权（强调低频）
omega_b = 0.05  # 带宽 rad/s（运河响应慢）
M_s = 1.8
epsilon = 0.001
W_S = (s/M_s + omega_b) / (s + omega_b*epsilon)

# 鲁棒稳定性加权（抑制高频）
M_t = 0.3
W_T = (s + omega_b/M_t) / (epsilon*s + omega_b)

# 控制能量加权
rho = 0.1
W_U = rho
```python

#### Step 3：求解H∞控制器

```python
# 方法1：使用control库的hinfsyn函数
import control
K, gamma_opt, info = control.hinfsyn(P, nmeas=1, ncon=1)

# 方法2：使用LMI工具箱（cvxpy）
import cvxpy as cp
P = cp.Variable((n, n), PSD=True)
gamma = cp.Variable(pos=True)
# ... 定义LMI约束
prob = cp.Problem(cp.Minimize(gamma), constraints)
prob.solve()
```python

#### Step 4：验证和仿真

```python
# 验证闭环H∞范数
T_zw_cl = control.feedback(...)
gamma_achieved = control.hinfnorm(T_zw_cl)
print(f"实现的γ: {gamma_achieved:.3f}")

# 时域仿真
t, y = control.forced_response(T_cl, T=t_sim, U=u_input)
```python

### 4.3 滑模控制器设计步骤

#### Step 1：选择滑模面

```python
# 对于运河系统：x = [h, Q]'，期望水位h_d

# 简单线性滑模面
c1 = 1.0
c2 = 0.5  # 调节收敛速度
s = c1*(h - h_d) + c2*(Q - Q_d)

# 或者积分滑模面（消除稳态误差）
lambda_int = 0.1
s = (h - h_d) + c2*(Q - Q_d) + lambda_int*∫(h - h_d)dt
```python

#### Step 2：设计等效控制

```python
# 等效控制使得 ṡ = 0

# ṡ = c1·ḣ + c2·Q̇ = 0
# 代入系统方程 ẋ = f(x) + g(x)·u
# 求解 u_eq

u_eq = -1/(c'·g) * (c'·f)
```python

#### Step 3：设计切换控制

```python
# 保证到达条件 s·ṡ < -η|s|

# 传统符号函数（会抖振）
K = 5.0
u_sw = -K * np.sign(s)

# 边界层法（减少抖振）
phi = 0.1  # 边界层厚度
u_sw = -K * np.tanh(s/phi)  # 或者 sat(s/phi)

# 自适应增益（根据|s|调整）
K_adaptive = K0 + K1*|s|
u_sw = -K_adaptive * np.tanh(s/phi)
```python

#### Step 4：完整控制律

```python
u = u_eq + u_sw

# 加入控制约束
u = np.clip(u, u_min, u_max)
```python

---

## 5. 工程实现要点

### 5.1 H∞控制器实现

```python
class HInfinityController:
    def __init__(self, A, B, C, D, K_hinf):
        """
        H∞控制器

        参数：
            A, B, C, D: 控制器状态空间矩阵
            K_hinf: 从hinfsyn得到的控制器
        """
        self.A_c = K_hinf.A
        self.B_c = K_hinf.B
        self.C_c = K_hinf.C
        self.D_c = K_hinf.D

        self.x_c = np.zeros(self.A_c.shape[0])

    def compute_control(self, y, dt):
        """
        计算控制输入

        参数：
            y: 测量输出
            dt: 时间步长
        """
        # 更新控制器状态
        dx_c = self.A_c @ self.x_c + self.B_c * y
        self.x_c += dt * dx_c

        # 计算控制输入
        u = (self.C_c @ self.x_c + self.D_c * y).item()

        return u
```python

### 5.2 滑模控制器实现

```python
class SlidingModeController:
    def __init__(self, c, K, phi, lambda_int=0.0):
        """
        滑模控制器

        参数：
            c: 滑模面参数 [c1, c2]
            K: 切换增益
            phi: 边界层厚度
            lambda_int: 积分项系数
        """
        self.c = np.array(c)
        self.K = K
        self.phi = phi
        self.lambda_int = lambda_int

        self.integral_error = 0.0

    def compute_control(self, x, x_d, f, g, dt):
        """
        计算滑模控制

        参数：
            x: 当前状态
            x_d: 期望状态
            f, g: 系统动态 ẋ = f(x) + g(x)·u
            dt: 时间步长
        """
        # 状态误差
        e = x - x_d

        # 更新积分项
        self.integral_error += e[0] * dt

        # 计算滑模变量
        s = self.c @ e + self.lambda_int * self.integral_error

        # 等效控制
        c_dot_f = self.c @ f
        c_dot_g = self.c @ g
        u_eq = -c_dot_f / (c_dot_g + 1e-6)

        # 切换控制（边界层法）
        u_sw = -self.K * np.tanh(s / self.phi)

        # 总控制
        u = u_eq + u_sw

        return u, s
```python

### 5.3 鲁棒性能评估

```python
def evaluate_robustness(controller, system, uncertainties, disturbances):
    """
    评估鲁棒性能

    参数：
        controller: 控制器对象
        system: 被控系统
        uncertainties: 参数不确定性范围
        disturbances: 扰动信号
    """
    results = []

    # 蒙特卡洛仿真
    for trial in range(N_trials):
        # 随机采样不确定参数
        system.randomize_parameters(uncertainties)

        # 仿真
        t, y, u = simulate(controller, system, disturbances)

        # 性能指标
        iae = np.mean(np.abs(y - y_ref))
        control_effort = np.sum(u**2) * dt

        results.append({
            'iae': iae,
            'control_effort': control_effort
        })

    # 统计分析
    mean_iae = np.mean([r['iae'] for r in results])
    max_iae = np.max([r['iae'] for r in results])

    print(f"鲁棒性能:")
    print(f"  平均IAE: {mean_iae:.4f}")
    print(f"  最坏IAE: {max_iae:.4f}")

    return results
```

---

## 6. 本案例演示内容

本案例包含4个演示部分：

### Part 1: H∞控制基础 - 标准问题
- 二阶系统的H∞控制器设计
- 混合灵敏度问题
- 频域分析（Bode图、灵敏度函数）
- 不同γ值的影响

### Part 2: 滑模控制基础 - 标量系统
- 一阶和二阶滑模面设计
- 到达过程和滑动过程可视化
- 抖振现象和边界层法
- 参数不确定性测试

### Part 3: 运河系统H∞鲁棒控制
- 含不确定性的运河模型
- H∞控制器设计和实现
- 参数摄动测试（蒙特卡洛仿真）
- 与PID、LQR对比

### Part 4: 运河系统滑模控制
- 积分滑模面设计
- 等效控制+切换控制
- 外部扰动抑制测试
- 自适应边界层

---

## 7. 与其他控制方法对比

| 控制方法 | 不确定性处理 | 扰动抑制 | 实时性 | 调试难度 | 抖振问题 |
|---------|------------|---------|--------|---------|---------|
| PID | 弱（需要重新整定）| 中 | 极高 | 容易 | 无 |
| LQR | 无（需精确模型）| 中 | 高 | 中 | 无 |
| **H∞控制** | **强（离线保证）** | **强** | 高 | 难 | 无 |
| **滑模控制** | **极强（在线鲁棒）** | **极强** | 中 | 中 | **有** |
| MRAC | 强（在线学习）| 中 | 中 | 中 | 无 |
| MPC | 中（需要模型）| 强 | 低 | 难 | 无 |

**H∞控制的独特优势**：
- 系统化的频域设计框架
- 多目标优化（跟踪、鲁棒、能量）
- 理论保证的性能下界

**滑模控制的独特优势**：
- 对参数不确定性完全不敏感（理想情况）
- 有限时间收敛
- 实现简单，计算量小

---

## 8. 工程应用建议

### 8.1 何时使用H∞控制？

✅ **适合场景**：
- 系统模型已知但参数有较大不确定性
- 需要在频域上明确指定性能要求
- 对扰动抑制要求高但控制能量有限
- 系统允许使用高阶控制器

❌ **不适合场景**：
- 完全未知的系统（建模困难）
- 需要极简单的控制器（H∞控制器阶数通常较高）
- 强非线性系统（需要线性化或增益调度）

### 8.2 何时使用滑模控制？

✅ **适合场景**：
- 参数不确定性极大（±50%以上）
- 扰动变化快速且不可预测
- 对收敛时间有严格要求
- 可以接受一定的控制抖振（或有抑制手段）

❌ **不适合场景**：
- 执行器带宽有限（无法实现高频切换）
- 对控制平滑性要求极高
- 测量噪声很大（会放大抖振）

### 8.3 实际部署checklist

**H∞控制器：**
- [ ] 精确建模标称系统（A, B, C矩阵）
- [ ] 量化不确定性范围（参数变化±α%）
- [ ] 合理选择加权函数（W_S, W_T, W_U）
- [ ] 求解H∞问题，检查γ_opt < γ_target
- [ ] 降阶控制器（如果阶数过高）
- [ ] 实时实现（状态空间形式）
- [ ] 蒙特卡洛验证鲁棒性

**滑模控制器：**
- [ ] 设计滑模面（确保滑动模态稳定）
- [ ] 估计扰动上界（用于选择K）
- [ ] 选择边界层厚度φ（权衡抖振和精度）
- [ ] 实现保护机制（防止积分饱和）
- [ ] 测试到达时间（确保有限时间到达）
- [ ] 调试抖振抑制策略
- [ ] 外部扰动下的鲁棒性测试

---

## 9. 扩展阅读

### 经典教材

1. **H∞控制**：
   - Zhou, K., & Doyle, J. C. (1998). *Essentials of Robust Control*. Prentice Hall.
   - Skogestad, S., & Postlethwaite, I. (2007). *Multivariable Feedback Control*. Wiley.

2. **滑模控制**：
   - Utkin, V., Guldner, J., & Shi, J. (2009). *Sliding Mode Control in Electro-Mechanical Systems*. CRC Press.
   - Edwards, C., & Spurgeon, S. (1998). *Sliding Mode Control: Theory and Applications*. CRC Press.

3. **鲁棒控制综合**：
   - Dullerud, G. E., & Paganini, F. (2013). *A Course in Robust Control Theory*. Springer.

### 前沿方向

- **自适应滑模控制**：结合自适应律和滑模控制
- **高阶滑模控制**：消除抖振的新方法
- **分布式H∞控制**：多智能体系统的鲁棒协同控制
- **数据驱动鲁棒控制**：结合机器学习的鲁棒控制器设计

---

## 10. 总结

### 核心要点

1. **H∞控制**：频域优化，保证最坏情况下的性能
2. **滑模控制**：变结构系统，对不确定性不敏感
3. **设计权衡**：鲁棒性 ↔ 性能 ↔ 控制能量
4. **抖振问题**：滑模控制的主要挑战，需要专门处理

### 学习目标

通过本案例，你将掌握：
- ✅ H∞控制的基本概念和标准问题
- ✅ 混合灵敏度问题的设计框架
- ✅ 滑模控制的三要素（滑模面、到达律、抖振抑制）
- ✅ 运河系统的不确定性建模和鲁棒控制器设计
- ✅ 鲁棒性能的评估方法（蒙特卡洛仿真）

### 实际意义

在运河-管道系统中，鲁棒控制能够：
- 🎯 应对季节性和长期的参数变化
- 🎯 抵抗各种外部扰动（降雨、渗漏）
- 🎯 减少模型依赖，降低建模成本
- 🎯 提供性能保证，增强系统可靠性

---

**下一步**：运行 `main.py` 查看H∞和滑模控制的实际效果！
