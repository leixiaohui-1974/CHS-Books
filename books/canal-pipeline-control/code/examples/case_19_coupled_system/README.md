# 案例19：运河-管道耦合系统

## 1. 案例简介

本案例演示**运河-管道耦合系统**的建模、仿真和控制技术。在实际工程中，长距离输水系统往往同时包含明渠段（运河）和压力管道段，两种水力系统的耦合带来了独特的挑战和控制问题。

### 典型应用场景

1. **南水北调工程**：明渠+隧洞+管道组合输水
2. **跨流域调水**：山区段管道+平原段运河
3. **灌区配水系统**：干渠+支渠+田间管道
4. **水电站引水**：明渠引水+压力管道+尾水渠道

### 系统特点

```
明渠段（Open Channel）:
    ✓ 自由水面，大气压
    ✓ 水力半径小，流速慢
    ✓ 响应慢，惯性大
    ✓ 可视化，易监测
    ✗ 占地大，蒸发渗漏
    ✗ 易受环境影响

压力管道（Pressurized Pipeline）:
    ✓ 密闭，无蒸发
    ✓ 占地小，输水高效
    ✓ 可跨越地形障碍
    ✗ 水锤风险
    ✗ 泄漏难以发现
    ✗ 维护成本高

耦合点（Interface）:
    ⚠️ 流态转换（明流↔压力流）
    ⚠️ 压力不连续
    ⚠️ 控制策略差异
    ⚠️ 动态响应时间尺度不同
```

---

## 2. 耦合系统数学模型

### 2.1 明渠段（Saint-Venant方程）

```
连续性方程:
    ∂A/∂t + ∂Q/∂x = 0

动量方程:
    ∂Q/∂t + ∂(Q²/A)/∂x + gA·∂h/∂x + gAS_f = 0

其中:
    A: 过水断面积 (m²)
    Q: 流量 (m³/s)
    h: 水位 (m)
    g: 重力加速度 (9.81 m/s²)
    S_f: 摩阻坡度

摩阻项（Manning公式）:
    S_f = n²Q|Q|/(A²R_h^(4/3))

    n: 糙率系数
    R_h: 水力半径
```

### 2.2 管道段（水锤方程）

```
连续性方程:
    ∂H/∂t + (a²/g)·∂V/∂x = 0

动量方程:
    ∂V/∂t + g·∂H/∂x + f·V|V|/(2D) = 0

其中:
    H: 压力水头 (m)
    V: 流速 (m/s)
    a: 压力波速 (m/s)
    f: 摩阻系数
    D: 管径 (m)
```

### 2.3 耦合边界条件

#### 类型1：明渠→管道（进水口）

```
场景: 运河通过闸门进入压力管道

边界条件:
    Q_canal = Q_pipe                    (流量连续)
    H_pipe_inlet = h_canal - h_loss     (能量方程)

其中:
    h_loss = K_entrance · V²/(2g)  (进口损失)
    K_entrance ≈ 0.5 (突扩)

控制变量: 闸门开度 θ
    Q = C_d · A_gate · √(2g·Δh)
```

#### 类型2：管道→明渠（出水口）

```
场景: 压力管道出流到运河

边界条件:
    Q_pipe = Q_canal                    (流量连续)

    if H_pipe > h_canal + D_pipe:
        # 淹没出流
        Q = C_d · A_outlet · √(2g·(H_pipe - h_canal))
    else:
        # 自由出流
        Q = C_d · A_outlet · √(2g·H_pipe)

控制变量: 阀门开度或水位
```

#### 类型3：泵站（提升）

```
场景: 从明渠抽水进入高位管道

泵特性曲线:
    H_pump = H₀ - K·Q²

边界条件:
    H_pipe = h_canal + H_pump - h_loss
    Q_canal = Q_pump

控制变量: 泵转速 n 或台数
```

---

## 3. 数值求解方法

### 3.1 分区耦合法（Domain Decomposition）

```
基本思路:
    1. 明渠段: Preissmann格式（隐式）
    2. 管道段: 特征线法（显式）
    3. 耦合点: 迭代求解边界条件

算法流程:
    for time_step in simulation:
        # Step 1: 明渠段（隐式求解）
        solve_canal_equations(boundary_from_pipe)

        # Step 2: 提取耦合边界信息
        Q_interface, h_interface = get_canal_boundary()

        # Step 3: 管道段（特征线法）
        solve_pipe_equations(Q_interface, h_interface)

        # Step 4: 检查耦合边界收敛
        if not converged:
            iterate_boundary()
```

### 3.2 Preissmann隐式格式（明渠）

```python
# 空间差分点: i-1, i
# 时间层: n, n+1

# 连续性方程离散
(A[i,n+1] - A[i,n])/Δt +
    θ·(Q[i,n+1] - Q[i-1,n+1])/Δx +
    (1-θ)·(Q[i,n] - Q[i-1,n])/Δx = 0

# 动量方程离散
(Q[i,n+1] - Q[i,n])/Δt +
    对流项 + 压力项 + 摩阻项 = 0

# 组成非线性方程组，牛顿迭代求解
F(A[n+1], Q[n+1]) = 0
J·ΔX = -F  （雅可比矩阵）
```

### 3.3 特征线法（管道）

```python
# 已在Case 18中详细介绍

# 内部节点
C⁺: H[i] = C_p + B·Q[i]
C⁻: H[i] = C_m - B·Q[i]

# 求解
H[i] = (C_p + C_m) / 2
Q[i] = (C_p - C_m) / (2B)
```

### 3.4 耦合迭代

```python
def couple_iteration(canal_state, pipe_state, max_iter=10):
    """耦合边界迭代求解"""

    for iter in range(max_iter):
        # 从明渠侧计算流量
        Q_canal = compute_canal_discharge(canal_state)

        # 传递给管道侧
        H_pipe_inlet = compute_pipe_inlet_head(Q_canal, pipe_state)

        # 从管道侧计算压力
        # 反馈给明渠侧
        h_canal_boundary = H_pipe_inlet + losses

        # 检查收敛
        if abs(Q_canal - Q_pipe) < tol:
            break

    return Q_interface, H_interface
```

---

## 4. 耦合系统控制策略

### 4.1 分层控制架构

```
Level 3: 优化调度层
    ├─ 全局优化（24小时调度计划）
    ├─ 需水预测
    └─ 能耗优化

Level 2: 协调控制层
    ├─ 多段协调
    ├─ 泵站-阀门协调
    └─ 明渠-管道协调

Level 1: 局部控制层
    ├─ 明渠段: PID/MPC水位控制
    ├─ 管道段: 压力/流量控制
    └─ 泵站: 转速/台数控制
```

### 4.2 前馈-反馈控制

```python
class FeedforwardFeedbackController:
    """前馈-反馈控制器"""

    def __init__(self, canal_model, pipe_model):
        self.canal_model = canal_model
        self.pipe_model = pipe_model

        # 反馈控制器（PID）
        self.pid = PIDController(Kp=2.0, Ki=0.5, Kd=1.0)

        # 前馈补偿
        self.feedforward_gain = 1.0

    def compute_control(self, h_measured, h_setpoint, Q_disturbance):
        """
        计算控制输入

        前馈部分: 补偿已知扰动（如下游需水变化）
        反馈部分: 修正测量误差和未知扰动
        """
        # 反馈控制
        error = h_setpoint - h_measured
        u_feedback = self.pid.compute(error)

        # 前馈控制（基于模型）
        u_feedforward = self.feedforward_gain * Q_disturbance

        # 总控制
        u_total = u_feedback + u_feedforward

        return u_total
```

### 4.3 MPC协调控制

```python
# 预测模型
def predict_coupled_system(x0, u_sequence, N_pred):
    """预测耦合系统未来状态"""

    x = [x0]
    for k in range(N_pred):
        # 明渠段预测
        x_canal_next = canal_dynamics(x[k]['canal'], u_sequence[k])

        # 管道段预测
        x_pipe_next = pipe_dynamics(x[k]['pipe'], u_sequence[k])

        # 耦合
        x_next = couple_states(x_canal_next, x_pipe_next)
        x.append(x_next)

    return x

# MPC优化
def mpc_optimization(x_current, x_ref, N_pred, N_control):
    """
    优化目标:
        min Σ[(h_canal - h_ref)² + (P_pipe - P_ref)² + λ·u²]

    约束:
        h_min ≤ h_canal ≤ h_max
        P_min ≤ P_pipe ≤ P_max
        u_min ≤ u ≤ u_max
        ΔQ_pump ≤ ΔQ_max  （泵站变化率）
    """
    # 预测未来状态
    x_pred = predict_coupled_system(x_current, u_sequence, N_pred)

    # 计算目标函数
    cost = compute_cost(x_pred, x_ref, u_sequence)

    # 优化
    u_optimal = minimize(cost, constraints)

    return u_optimal[0]  # 返回第一个控制动作
```

### 4.4 故障应急控制

```python
def emergency_control(system_state, fault_type):
    """
    故障应急控制

    常见故障:
    1. 泵站停机 → 启动备用泵，关闭下游阀门
    2. 管道爆裂 → 紧急关闭上游阀门
    3. 闸门故障 → 切换到旁通管
    4. 水位异常 → 限流运行
    """

    if fault_type == 'pump_failure':
        # 泵站故障
        actions = [
            ('start_backup_pump', True),
            ('close_downstream_valve', 0.5),  # 关闭50%
            ('reduce_upstream_flow', 0.7)     # 降低30%
        ]

    elif fault_type == 'pipe_burst':
        # 管道爆裂
        actions = [
            ('emergency_valve_closure', 0.0),  # 全关
            ('stop_all_pumps', True),
            ('alert_operators', 'CRITICAL')
        ]

    return actions
```

---

## 5. 工程实践要点

### 5.1 系统设计原则

```
1. 水力匹配
   - 明渠设计流量 = 管道设计流量
   - 避免过度超高或负压
   - 合理设置调节设施

2. 过渡段设计
   - 进口: 渐变段 + 格栅 + 闸门
   - 出口: 消能池 + 稳流段
   - 通气孔（防止虹吸）

3. 控制点布置
   - 关键断面设置水位计
   - 管道关键点设置压力计
   - 流量计布置在稳定段

4. 安全裕度
   - 明渠超高 ≥ 0.5m
   - 管道压力裕度 ≥ 30%
   - 流速限制: 运河<1.5m/s, 管道<3.0m/s
```

### 5.2 启动/停机程序

```
正常启动顺序:
    Step 1: 开启下游阀门至20%
    Step 2: 启动泵站（逐台，间隔5分钟）
    Step 3: 逐步开启上游闸门
    Step 4: 监测水位/压力，达到稳态
    Step 5: 切换到自动控制模式

正常停机顺序:
    Step 1: 切换到手动控制模式
    Step 2: 逐步减小泵站流量
    Step 3: 关闭下游阀门（缓闭，>3×相长）
    Step 4: 停止泵站（逐台）
    Step 5: 关闭上游闸门

紧急停机:
    立即关闭泵站 + 启动水锤防护装置
```

### 5.3 常见问题及对策

| 问题 | 原因 | 对策 |
|------|------|------|
| 明渠水位波动大 | 调节不当 | 增加缓冲容积，优化PID参数 |
| 管道压力过高 | 流量突变 | 安装安全阀，延长阀门动作时间 |
| 管道负压 | 泵站停机 | 安装真空破坏阀，飞轮延迟 |
| 进口淤积 | 泥沙沉积 | 设置冲沙闸，定期清淤 |
| 出口冲刷 | 流速过大 | 加固护底，设置消能设施 |

---

## 6. 本案例演示内容

本案例包含4个演示部分：

### Part 1: 耦合系统建模验证
- 明渠段模型（Saint-Venant）
- 管道段模型（MOC）
- 耦合边界条件实现
- 稳态和动态验证

### Part 2: 不同耦合方式对比
- 明渠→管道（闸门控制）
- 管道→明渠（阀门出流）
- 泵站提升（明渠→高位管道）
- 水力特性对比

### Part 3: 协调控制策略
- 独立控制（基准）
- 前馈-反馈协调控制
- MPC预测协调控制
- 性能对比

### Part 4: 综合工况仿真
- 正常运行工况
- 需水变化工况
- 泵站故障工况
- 应急处理效果

---

## 7. 典型工程案例

### 7.1 南水北调中线工程

```
系统特征:
    总长: 1432 km
    明渠: 1196 km
    隧洞: 194 km
    渡槽: 42 km

控制难点:
    - 长距离、大惯性
    - 多级泵站（13座）
    - 复杂地形
    - 多用户需求

解决方案:
    ✓ SCADA集中监控
    ✓ 分段自动控制
    ✓ 智能调度系统
    ✓ 应急预案库

运行效果:
    年调水量: 95亿m³
    输水效率: >90%
    事故率: <0.1次/年
```

### 7.2 某灌区配水系统

```
系统组成:
    干渠: 明渠，L=50km
    支渠: 管道，L=20km
    泵站: 3座，总流量10m³/s

控制目标:
    - 田间需水保证率 >95%
    - 能耗最小化
    - 公平配水

实施方案:
    ✓ 干渠: 恒定水位控制
    ✓ 支渠: 按需配水
    ✓ 泵站: 变频调速
    ✓ 远程监控APP

实施效果:
    节水: 15%
    节能: 20%
    满意度: 提升30%
```

---

## 8. 扩展阅读

### 经典文献

1. Litrico, X., & Fromion, V. (2009). *Modeling and Control of Hydrosystems*. Springer.
2. Chow, V. T. (1959). *Open-Channel Hydraulics*. McGraw-Hill.
3. 王长德. (2012). *输水工程学*. 中国水利水电出版社.

### 数值方法

4. Cunge, J. A., Holly, F. M., & Verwey, A. (1980). *Practical Aspects of Computational River Hydraulics*. Pitman.
5. Wylie, E. B., & Streeter, V. L. (1993). *Fluid Transients in Systems*. Prentice Hall.

### 控制技术

6. Malaterre, P. O., Rogers, D. C., & Schuurmans, J. (1998). Classification of canal control algorithms. *Journal of Irrigation and Drainage Engineering*, 124(1), 3-10.

---

## 9. 总结

### 核心要点

1. **耦合特性**：明流和压力流的转换，压力不连续
2. **数学模型**：Saint-Venant + 水锤方程 + 边界条件
3. **数值方法**：Preissmann + MOC + 迭代耦合
4. **控制策略**：分层架构，前馈-反馈，MPC协调
5. **工程实践**：水力匹配，过渡段设计，启停程序

### 学习目标

通过本案例，你将掌握：
- ✅ 运河-管道耦合系统的建模方法
- ✅ 耦合边界条件的处理技术
- ✅ 分区耦合数值求解方法
- ✅ 协调控制策略的设计和实现
- ✅ 复杂工况下的应急控制

### 实际意义

在长距离输水工程中，耦合系统控制能够：
- 🎯 提高输水效率和可靠性
- 🎯 降低能耗和运行成本
- 🎯 保障供水安全和稳定
- 🎯 适应复杂地形和多样需求
- 🎯 实现智能化管理和优化调度

---

**下一步**：运行 `main.py` 查看运河-管道耦合系统的仿真效果！
