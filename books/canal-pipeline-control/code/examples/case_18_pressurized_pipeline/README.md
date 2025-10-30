# 案例18：有压管道控制（水锤防护与压力控制）

## 1. 案例简介

本案例演示**有压管道系统**的控制技术，重点关注**水锤现象**的预测、防护和压力控制。有压管道（Pressurized Pipeline）是指管道内水流充满整个管道断面，水流在压力作用下流动的管道系统。

### 应用背景

有压管道广泛应用于：
- **长距离输水工程**：南水北调、西气东输配套供水
- **水电站引水系统**：高压引水管道、尾水系统
- **城市供水网络**：泵站至用户的配水管网
- **工业管道**：石油、天然气、化工流体输送

### 水锤现象（Water Hammer）

**水锤**是有压管道中最危险的瞬态流动现象：

```
定义：
当管道中流体的流速突然改变时，由于流体惯性和管道弹性，
会产生压力波动并沿管道传播，形成"锤击"效应。

危害：
- 压力骤升：可达正常压力的数倍甚至数十倍
- 压力骤降：可能产生负压，导致管道吸瘪或汽蚀
- 管道破裂、设备损坏、人员伤亡

典型触发事件：
- 阀门快速关闭或开启
- 泵站突然停机
- 负荷突变
```

### 关键挑战

- ⚠️ **压力波传播**：波速可达1000-1500 m/s，反应时间极短
- ⚠️ **多次反射**：压力波在管道两端反复反射，形成复杂波动
- ⚠️ **非线性**：管道弹性、流体压缩性、摩阻等非线性因素
- ⚠️ **安全第一**：必须确保压力不超过管道承压能力

---

## 2. 水锤理论基础

### 2.1 Joukowsky公式（直接水锤）

最简单的水锤压力计算公式：

```
ΔP = ρ·a·ΔV

其中：
    ΔP: 压力升高（Pa）
    ρ: 流体密度（kg/m³，水约1000）
    a: 压力波速（m/s）
    ΔV: 流速变化（m/s）

压力波速：
    a = √(K/ρ) / √(1 + (K·D)/(E·e))

    K: 流体体积弹性模量（水约2.2×10⁹ Pa）
    E: 管道弹性模量（钢管约2.0×10¹¹ Pa）
    D: 管道直径（m）
    e: 管壁厚度（m）

典型波速：
    钢管：1000-1200 m/s
    铸铁管：900-1100 m/s
    混凝土管：800-1000 m/s
```

**例子**：
```python
# 钢管，D=1m，e=10mm，流速突然减小2 m/s
ρ = 1000  # kg/m³
a = 1200  # m/s
ΔV = 2    # m/s

ΔP = ρ * a * ΔV = 1000 * 1200 * 2 = 2,400,000 Pa = 2.4 MPa = 24 bar

# 这相当于增加了约240米的水头！
```

### 2.2 水锤相长（Phase Duration）

```
相长（Phase） = 2L / a

其中：
    L: 管道长度（m）
    a: 压力波速（m/s）

物理意义：
- 压力波从阀门传播到末端，再反射回来所需的时间
- 如果阀门关闭时间 Tc < 相长，则为"直接水锤"（最严重）
- 如果阀门关闭时间 Tc > 相长，则为"间接水锤"（压力波衰减）

设计准则：
    阀门关闭时间应大于 3-5 倍相长
```

### 2.3 弹性水锤方程组

完整的水锤数学模型基于**双曲型偏微分方程**：

```
连续性方程（质量守恒）：
    ∂H/∂t + (a²/g)·∂V/∂x = 0

动量方程（动量守恒）：
    ∂V/∂t + g·∂H/∂x + f·V·|V|/(2D) = 0

其中：
    H: 压力水头（m）
    V: 流速（m/s）
    t: 时间（s）
    x: 沿管道的距离（m）
    a: 压力波速（m/s）
    g: 重力加速度（9.81 m/s²）
    f: 摩阻系数（Darcy-Weisbach）
    D: 管道直径（m）

边界条件：
    上游：H = H_reservoir（水库水头）或 Q = Q_pump（泵流量）
    下游：V = 0（阀门关闭）或 Q = Q_load（负荷流量）
```

### 2.4 特征线法（Method of Characteristics, MOC）

求解水锤方程的经典数值方法：

```python
# 沿正特征线（C+）：dx/dt = +a
C_plus: H_P = C_p + B·Q_P

其中：
    C_p = H_A + B·Q_A - R·Q_A·|Q_A|
    B = a / (g·A)
    R = f·Δx / (2·g·D·A²)

    H_A, Q_A: 上一时刻点A的水头和流量
    H_P, Q_P: 当前时刻点P的水头和流量

# 沿负特征线（C-）：dx/dt = -a
C_minus: H_P = C_m - B·Q_P

其中：
    C_m = H_B - B·Q_B + R·Q_B·|Q_B|

    H_B, Q_B: 上一时刻点B的水头和流量

# 解方程组得到P点的水头和流量
联立 C+ 和 C- 方程：
    H_P = (C_p + C_m) / 2
    Q_P = (C_p - C_m) / (2B)
```

---

## 3. 水锤防护措施

### 3.1 调压塔（Surge Tank）

**原理**：在管道中设置开放水面的塔，吸收和释放水量，缓冲压力波动。

```
类型：
1. 简单调压塔：直立圆柱体
2. 阻抗式调压塔：带阻抗孔的调压塔
3. 差动式调压塔：上下腔室不同直径

设计要点：
- 塔截面积 A_s = f(Q_max, H_max, 管道参数)
- 位置：靠近泵站或阀门，减小受保护管段长度
- 高度：需考虑最高涌浪高度和最低下降高度

优点：
    ✅ 防护效果好
    ✅ 可视化监测

缺点：
    ❌ 占地大，投资高
    ❌ 仅适用于低水头系统（<200m）
```

### 3.2 安全阀（Relief Valve）

**原理**：当压力超过设定值时自动开启，释放流体，降低压力。

```python
# 安全阀特性
if P > P_set:
    Q_valve = C_v * A_valve * sqrt(2 * g * (P - P_set))
else:
    Q_valve = 0

其中：
    P: 当前压力
    P_set: 设定压力（开启压力）
    C_v: 流量系数
    A_valve: 阀门面积

设计准则：
    P_set = P_normal + ΔP_allowable * 0.8
    （设定压力 = 正常压力 + 80%允许增压）

优点：
    ✅ 结构简单，成本低
    ✅ 响应快速

缺点：
    ❌ 只能防止超压，无法防止负压
    ❌ 频繁动作可能影响寿命
```

### 3.3 缓闭阀（Slow-Closing Valve）

**原理**：延长阀门关闭时间，使 Tc > 相长，减小水锤压力。

```python
# 分段关闭策略
Stage 1: 快速关闭至 80% 开度（时间短）
Stage 2: 缓慢关闭至 0% 开度（时间 > 3-5 倍相长）

# 优化关闭曲线
θ(t) = θ_0 * (1 - (t/T_c)^n)

其中：
    θ: 阀门开度（0-1）
    T_c: 总关闭时间
    n: 曲线指数（n=1线性，n>1前快后慢，n<1前慢后快）

推荐：n = 2（抛物线关闭）

优点：
    ✅ 简单有效
    ✅ 适用于各种工况

缺点：
    ❌ 需要精确控制阀门动作
    ❌ 关闭时间长，不适用于紧急停机
```

### 3.4 空气罐（Air Vessel）

**原理**：利用空气的可压缩性，吸收压力波动。

```
工作原理：
- 正常运行：空气罐充满压缩空气（P ≈ P_normal）
- 压力升高：空气被压缩，罐内水位上升，吸收能量
- 压力降低：压缩空气膨胀，向管道补水，防止负压

设计参数：
    V_air = f(Q_max, ΔP_max, 气体多变指数)

优点：
    ✅ 防护效果好，响应快
    ✅ 占地小

缺点：
    ❌ 结构复杂，成本高
    ❌ 需要定期维护（补气）
```

### 3.5 飞轮（Flywheel）

**原理**：增大泵组转动惯量，延长停机时间，减缓流速变化。

```
设计公式：
    GD² = k · (Q² · H · L) / (n² · a · ΔH_allowable)

其中：
    GD²: 飞轮惯量（kg·m²）
    Q: 流量（m³/s）
    H: 水头（m）
    L: 管长（m）
    n: 转速（r/min）
    a: 波速（m/s）
    k: 经验系数

优点：
    ✅ 机械可靠，无需维护
    ✅ 适用于泵站停机工况

缺点：
    ❌ 增加泵组重量和成本
    ❌ 仅对停机有效，对阀门关闭无效
```

---

## 4. 有压管道控制策略

### 4.1 阀门优化控制

#### 分段关闭策略

```python
class OptimalValveControl:
    """优化阀门关闭策略"""

    def __init__(self, L, a, P_max, P_min):
        self.phase = 2 * L / a  # 相长
        self.P_max = P_max      # 最大允许压力
        self.P_min = P_min      # 最小允许压力

    def compute_closure_curve(self, T_total):
        """
        计算最优关闭曲线

        目标：最小化 max(|P - P_normal|)
        约束：T_total > 3 * phase
        """
        # 分段关闭
        T1 = 0.2 * T_total  # 快速关闭至80%
        T2 = T_total - T1   # 缓慢关闭至0%

        def theta(t):
            if t < T1:
                return 1.0 - 0.2 * (t / T1)
            else:
                return 0.8 * (1 - ((t - T1) / T2)**2)

        return theta

    def feedback_control(self, P_measured, theta_current):
        """
        基于压力反馈的实时调整

        如果 P > P_max：减缓关闭速度
        如果 P < P_min：加速关闭速度（防止过度负压）
        """
        if P_measured > self.P_max * 0.9:
            # 接近超压，减速关闭
            dtheta_dt = -0.5 * dtheta_dt_nominal
        elif P_measured < self.P_min * 1.1:
            # 接近负压，加速关闭（但不能太快）
            dtheta_dt = -0.8 * dtheta_dt_nominal
        else:
            # 正常关闭
            dtheta_dt = dtheta_dt_nominal

        return dtheta_dt
```

### 4.2 泵站协调控制

```python
# 多泵运行时，优化启停顺序
def optimal_pump_shutdown_sequence(pumps, priority='pressure'):
    """
    优化泵站关机顺序

    策略：
    1. 先停靠近水源的泵（减小关机水锤）
    2. 逐台停机，每台间隔 > 相长
    3. 监测压力，动态调整
    """
    if priority == 'pressure':
        # 按压力影响排序
        sorted_pumps = sorted(pumps, key=lambda p: p.distance_from_source)
    else:
        # 按流量影响排序
        sorted_pumps = sorted(pumps, key=lambda p: p.flow_rate, reverse=True)

    shutdown_schedule = []
    for i, pump in enumerate(sorted_pumps):
        t_shutdown = i * phase * 1.5  # 每台间隔1.5倍相长
        shutdown_schedule.append((pump, t_shutdown))

    return shutdown_schedule
```

### 4.3 MPC在水锤控制中的应用

```python
# 模型预测控制考虑未来压力波动
class WaterHammerMPC:
    """水锤预测控制"""

    def __init__(self, model, N_p, N_c):
        self.model = model  # 水锤模型（MOC或简化模型）
        self.N_p = N_p      # 预测时域
        self.N_c = N_c      # 控制时域

    def optimize_control(self, current_state, reference):
        """
        优化控制序列

        目标函数：
            min Σ[(P_k - P_ref)² + λ·(u_k - u_{k-1})²]

        约束：
            P_min ≤ P_k ≤ P_max  （压力约束）
            u_min ≤ u_k ≤ u_max  （阀门开度约束）
            Δu_min ≤ u_k - u_{k-1} ≤ Δu_max  （关闭速度约束）
        """
        # 预测未来N_p步的压力
        P_predicted = []
        for k in range(self.N_p):
            P_k = self.model.predict(current_state, u_sequence)
            P_predicted.append(P_k)

        # 求解优化问题
        u_optimal = self.solve_qp(P_predicted, reference)

        return u_optimal[0]  # 返回第一个控制动作
```

---

## 5. 数值仿真方法

### 5.1 特征线法实现

```python
class MOCSimulator:
    """特征线法水锤仿真器"""

    def __init__(self, L, D, a, f, N_sections):
        self.L = L              # 管道长度
        self.D = D              # 管道直径
        self.a = a              # 波速
        self.f = f              # 摩阻系数
        self.N = N_sections     # 分段数

        # 空间步长
        self.dx = L / N_sections

        # 时间步长（CFL条件）
        self.dt = self.dx / a

        # 管道参数
        self.A = np.pi * D**2 / 4
        self.B = a / (9.81 * self.A)
        self.R = f * self.dx / (2 * 9.81 * D * self.A**2)

        # 初始化网格
        self.H = np.zeros(N_sections + 1)
        self.Q = np.zeros(N_sections + 1)

    def compute_internal_points(self):
        """计算内部节点（特征线交点）"""
        H_new = np.zeros_like(self.H)
        Q_new = np.zeros_like(self.Q)

        for i in range(1, self.N):
            # C+ 特征线（来自左侧）
            C_p = self.H[i-1] + self.B * self.Q[i-1] - \
                  self.R * self.Q[i-1] * abs(self.Q[i-1])

            # C- 特征线（来自右侧）
            C_m = self.H[i+1] - self.B * self.Q[i+1] + \
                  self.R * self.Q[i+1] * abs(self.Q[i+1])

            # 求解
            H_new[i] = (C_p + C_m) / 2
            Q_new[i] = (C_p - C_m) / (2 * self.B)

        return H_new, Q_new

    def apply_boundary_conditions(self, H_new, Q_new, bc_upstream, bc_downstream):
        """应用边界条件"""
        # 上游边界（水库或泵）
        if bc_upstream['type'] == 'constant_head':
            H_new[0] = bc_upstream['value']
            # 从C+特征线计算流量
            C_p = self.H[1] + self.B * self.Q[1] - \
                  self.R * self.Q[1] * abs(self.Q[1])
            Q_new[0] = (C_p - H_new[0]) / self.B

        # 下游边界（阀门）
        if bc_downstream['type'] == 'valve':
            theta = bc_downstream['opening']  # 阀门开度
            C_v = bc_downstream['flow_coeff']

            # 从C-特征线和阀门方程联立求解
            C_m = self.H[-2] - self.B * self.Q[-2] + \
                  self.R * self.Q[-2] * abs(self.Q[-2])

            # 阀门方程：Q = theta * C_v * sqrt(H)
            # 联立求解（迭代法）
            for _ in range(5):
                Q_new[-1] = theta * C_v * np.sqrt(max(H_new[-1], 0))
                H_new[-1] = C_m + self.B * Q_new[-1]

        return H_new, Q_new

    def step(self, bc_upstream, bc_downstream):
        """单步仿真"""
        # 计算内部节点
        H_new, Q_new = self.compute_internal_points()

        # 应用边界条件
        H_new, Q_new = self.apply_boundary_conditions(
            H_new, Q_new, bc_upstream, bc_downstream
        )

        # 更新状态
        self.H = H_new
        self.Q = Q_new

        return self.H.copy(), self.Q.copy()
```

### 5.2 简化刚性水柱模型

对于短管道或初步分析，可使用简化的刚性水柱模型：

```python
class RigidColumnModel:
    """刚性水柱模型（忽略管道弹性）"""

    def __init__(self, L, D, f, H_res):
        self.L = L
        self.A = np.pi * D**2 / 4
        self.f = f
        self.D = D
        self.H_res = H_res
        self.g = 9.81

        # 状态：流速
        self.V = 0

    def step(self, theta_valve, dt):
        """
        动量方程积分：
            dV/dt = g * (H_res - H_valve - h_f) / L

        其中：
            h_f = f * L * V² / (2 * g * D)  摩阻损失
            H_valve = K_v * V² / (2*g)      阀门损失
            K_v = 1 / theta²                阀门系数
        """
        # 摩阻损失
        h_f = self.f * self.L * self.V**2 / (2 * self.g * self.D)

        # 阀门损失
        if theta_valve > 0:
            K_v = 1.0 / theta_valve**2
        else:
            K_v = 1e6  # 阀门关闭

        H_valve = K_v * self.V**2 / (2 * self.g)

        # 动量方程
        dV_dt = self.g * (self.H_res - H_valve - h_f) / self.L

        # 积分
        self.V += dV_dt * dt
        self.V = max(0, self.V)  # 流速非负

        # 计算压力
        H_pipe = self.H_res - h_f - K_v * self.V**2 / (2 * self.g)

        return self.V, H_pipe
```

---

## 6. 本案例演示内容

本案例包含4个演示部分：

### Part 1: 水锤基础 - Joukowsky公式验证
- 阀门瞬时关闭的压力计算
- 压力波传播过程
- 不同管道参数的影响
- 与理论公式对比

### Part 2: 特征线法仿真 - 阀门缓闭
- 完整MOC仿真器实现
- 不同关闭时间的压力响应
- 最优关闭曲线
- 压力时空分布图

### Part 3: 水锤防护措施对比
- 无防护措施（基准）
- 安全阀防护
- 调压塔防护
- 缓闭阀门防护
- 效果对比

### Part 4: 泵站停机优化控制
- 多泵协调停机
- 飞轮+缓闭阀组合
- MPC预测控制
- 压力安全监测

---

## 7. 工程设计指南

### 7.1 水锤计算流程

```
Step 1: 确定基本参数
    - 管道：L, D, e, E, K
    - 流体：ρ, ν
    - 工况：Q, H, P_normal

Step 2: 计算波速
    a = √(K/ρ) / √(1 + (K·D)/(E·e))

Step 3: 计算相长
    T_phase = 2L / a

Step 4: 初步估算水锤压力
    ΔP = ρ·a·ΔV  （Joukowsky）

Step 5: 判断是否需要防护
    if ΔP > 0.3 * P_allowable:
        需要水锤防护措施

Step 6: 选择防护措施
    根据工况、投资、场地选择合适方案

Step 7: 详细数值仿真
    使用MOC或CFD验证设计
```

### 7.2 防护措施选择准则

| 工况 | 推荐措施 | 备选方案 |
|------|---------|---------|
| 泵站停机（低水头<200m） | 调压塔 | 飞轮+缓闭阀 |
| 泵站停机（高水头>200m） | 空气罐 | 飞轮+安全阀 |
| 阀门关闭 | 缓闭阀 | 安全阀 |
| 负荷突变 | 旁通管+调节阀 | MPC+快速响应阀 |
| 长距离输水 | 多级调压 | 分段保护+监控 |

### 7.3 安全裕度

```python
# 设计压力
P_design = P_normal + max(ΔP_waterhammer, ΔP_surge) * 安全系数

# 安全系数推荐值
安全系数 = 1.3 - 1.5  （重要管道）
安全系数 = 1.2 - 1.3  （一般管道）

# 管道选型
P_rating ≥ P_design

# 阀门动作时间
T_closure ≥ 3 * T_phase  （推荐5倍）
```

---

## 8. 工程案例

### 8.1 南水北调中线工程

```
挑战：
- 总长1432km，世界最长调水工程
- 落差100m，多级泵站
- 大流量（350 m³/s）

解决方案：
- 分段设置调压设施
- 泵站采用飞轮+缓停
- SCADA实时监控
- 分级预警系统

效果：
- 无一起水锤事故
- 安全运行10年+
```

### 8.2 某水电站引水管道

```
参数：
- L = 5000m
- D = 4m
- H = 600m（高水头）
- Q = 80 m³/s

水锤分析：
- 波速 a ≈ 1100 m/s
- 相长 T = 9.1 s
- 理论水锤压力 ΔP ≈ 8 MPa

防护措施：
- 主阀缓闭（60秒，6.6倍相长）
- 调压井（位于L/3处）
- 安全阀（1.2倍正常压力开启）

结果：
- 实测最大压力 7.2 MPa（< 8 MPa设计值）
- 未发生超压
```

---

## 9. 扩展阅读

### 经典教材

1. Wylie, E. B., & Streeter, V. L. (1993). *Fluid Transients in Systems*. Prentice Hall.
2. Chaudhry, M. H. (2014). *Applied Hydraulic Transients* (3rd ed.). Springer.
3. 严宗毅, 等. (2004). *水力瞬变与调节*. 中国水利水电出版社.

### 工程规范

4. SL 37-2006《水电站压力管道设计规范》
5. GB 50265-2010《泵站设计规范》
6. ASME B31.3《工艺管道设计规范》

### 仿真软件

- **Hammer**（Bentley）：管网水锤仿真
- **AFT Impulse**：瞬态流动分析
- **WANDA**（Deltares）：水力瞬变仿真

---

## 10. 总结

### 核心要点

1. **水锤危害**：压力骤升骤降，可能导致管道爆裂
2. **Joukowsky公式**：ΔP = ρ·a·ΔV，快速估算
3. **相长概念**：2L/a，设计关闭时间的关键参数
4. **防护措施**：调压塔、安全阀、缓闭阀、飞轮、空气罐
5. **控制策略**：优化关闭曲线、多泵协调、预测控制

### 学习目标

通过本案例，你将掌握：
- ✅ 水锤现象的物理机理和数学模型
- ✅ 压力波传播和反射的特征
- ✅ 特征线法（MOC）的原理和实现
- ✅ 各种水锤防护措施的原理和适用场景
- ✅ 有压管道的控制策略设计

### 实际意义

在水利工程中，水锤控制能够：
- 🎯 保护管道和设备免受破坏
- 🎯 确保供水安全和稳定
- 🎯 延长管道使用寿命
- 🎯 降低维护成本和事故风险
- 🎯 提高系统整体可靠性

---

**下一步**：运行 `main.py` 查看水锤仿真和防护措施的效果！
