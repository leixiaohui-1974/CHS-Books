# 案例3：前馈-反馈复合控制

## 问题描述

在实际的渠道系统中，常常存在可测量的扰动（如支渠汇入、降雨径流等）。传统的反馈控制虽然能够消除偏差，但属于"事后补救"——必须等到水位偏离目标后才能进行调整，导致调节过程缓慢且可能产生较大波动。

**前馈控制**的思想是：如果能够测量到扰动，就可以根据扰动的大小提前调整控制量，从而在扰动影响系统之前就进行补偿。前馈控制的优势在于响应快速、超调小，但对模型精度要求高，且无法消除模型误差和未知扰动。

**前馈-反馈复合控制**结合了两者的优点：
- 前馈控制快速补偿已知扰动
- 反馈控制消除残余误差和未知扰动影响

```python
渠道系统示意图：

上游          中段(扰动点)              下游
┌──────┬──────┬──────┬──────┬──────┬──────┐
│ 闸门 │      │      │ q_d  │      │      │  → 堰
└──────┴──────┴──────┴──────┴──────┴──────┘
   ↑                    ↑                  ↑
 Q_in               侧向入流              h_d(测量)
(控制量)           (可测扰动)          (控制目标)

复合控制结构：
              ┌──────────────┐
    q_d  →    │  前馈控制器   │
(侧向入流)    │   K_ff       │
              └───────┬──────┘
                      │ u_ff
                      ↓
    h_d  →    ┌──────+──────┐
  (测量值)    │  PID控制器  │  →  Q_in
    h_sp →    │  (反馈)     │    (上游流量)
  (设定值)    └─────────────┘
                     u_fb

u_total = u_ff + u_fb

前馈部分：u_ff = K_ff * q_d
反馈部分：u_fb = PID(e)，其中 e = h_sp - h_d
```

## 理论基础

### 1. 前馈控制原理

对于渠道系统，如果在x_d位置有侧向入流q_d(t)，为了维持下游水位不变，理想情况下上游流量应增加相同的量：

$$\Delta Q_{in}(t) = q_d(t)$$

但实际系统存在：
- 时间滞后：扰动从x_d传播到下游需要时间
- 水力特性：渠道的蓄水和调蓄作用
- 非线性：流量-水位关系是非线性的

因此，实际的前馈控制律为：

$$u_{ff}(t) = K_{ff} \cdot q_d(t - \tau_d)$$

其中：
- $K_{ff}$：前馈增益（需要设计/调整）
- $\tau_d$：扰动测量的时滞（通常很小，可忽略）

### 2. 前馈增益设计

前馈增益K_ff的设计有多种方法：

#### 方法1：稳态补偿
基于质量守恒，稳态时：
$$K_{ff} = 1$$

#### 方法2：基于模型的设计
如果知道系统的传递函数：
- 扰动到输出：$G_d(s)$
- 控制到输出：$G_p(s)$

理想前馈控制器：
$$K_{ff}(s) = -\frac{G_d(s)}{G_p(s)}$$

对于渠道系统（简化为一阶+时滞）：
$$G_p(s) = \frac{K_p e^{-\tau_1 s}}{\tau_p s + 1}$$
$$G_d(s) = \frac{K_d e^{-\tau_2 s}}{\tau_d s + 1}$$

则：
$$K_{ff}(s) = -\frac{K_d}{K_p} \cdot \frac{\tau_p s + 1}{\tau_d s + 1} \cdot e^{-(\tau_2 - \tau_1)s}$$

简化实现（只考虑稳态增益）：
$$K_{ff} = \frac{K_d}{K_p}$$

#### 方法3：实验调整
通过仿真或实验，测试不同K_ff值，选择性能最优的增益。

性能指标：
- IAE（积分绝对误差）
- ISE（积分平方误差）
- 超调量
- 调节时间

### 3. 复合控制律

完整的复合控制律为：

$$u(t) = u_{ff}(t) + u_{fb}(t)$$

其中：

**前馈部分**：
$$u_{ff}(t) = K_{ff} \cdot q_d(t)$$

**反馈部分**（PID）：
$$u_{fb}(t) = K_p e(t) + K_i \int_0^t e(\tau) d\tau + K_d \frac{de(t)}{dt}$$

误差：
$$e(t) = h_{sp} - h_d(t)$$

最终控制量需要转换为流量：
$$Q_{in}(t) = \text{GateModel}(u(t))$$

### 4. 控制系统性能分析

#### 纯反馈控制
- **优点**：对所有扰动都有效，鲁棒性强
- **缺点**：响应慢，可能有超调，属于"事后补救"

#### 纯前馈控制
- **优点**：响应快，超调小，主动补偿
- **缺点**：依赖模型精度，无法消除未知扰动和模型误差

#### 复合控制
- **优点**：结合两者优势，快速响应+误差消除
- **缺点**：需要设计和调整两套参数

性能比较（理想情况）：
$$\text{IAE}_{复合} < \text{IAE}_{反馈} < \text{IAE}_{前馈}$$
$$\text{调节时间}_{复合} < \text{调节时间}_{反馈}$$

## 数学模型

### Saint-Venant方程（同案例1）

连续性方程：
$$\frac{\partial A}{\partial t} + \frac{\partial Q}{\partial x} = q_{lat}(x,t)$$

动量方程（简化）：
$$\frac{\partial Q}{\partial t} + \frac{\partial}{\partial x}\left(\frac{Q^2}{A}\right) + gA\frac{\partial h}{\partial x} = -gAS_f + gAi_0$$

其中侧向入流项：
$$q_{lat}(x,t) = \begin{cases}
q_d(t) & \text{if } x = x_d \\
0 & \text{otherwise}
\end{cases}$$

### 前馈-反馈控制器

```python
class FeedforwardFeedbackController:
    def __init__(self, Kp, Ki, Kd, K_ff, dt):
        # PID参数（反馈）
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        # 前馈增益
        self.K_ff = K_ff

        self.dt = dt
        self.integral = 0.0
        self.error_prev = 0.0

    def compute(self, h_target, h_measured, q_disturbance):
        """
        计算复合控制量

        Parameters:
        -----------
        h_target : float
            目标水位 [m]
        h_measured : float
            测量水位 [m]
        q_disturbance : float
            侧向入流扰动 [m³/s]

        Returns:
        --------
        u_total : float
            总控制量（闸门开度）
        u_ff : float
            前馈部分
        u_fb : float
            反馈部分
        """
        # 前馈控制
        u_ff = self.K_ff * q_disturbance

        # 反馈控制（PID）
        error = h_target - h_measured
        self.integral += error * self.dt
        derivative = (error - self.error_prev) / self.dt

        u_fb = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # 复合控制
        u_total = u_ff + u_fb

        # 限幅
        u_total = np.clip(u_total, 0.1, 1.0)

        # 抗积分饱和
        if u_total != (u_ff + u_fb):
            self.integral -= error * self.dt

        self.error_prev = error

        return u_total, u_ff, u_fb
```python

## 实验设计

### Part 1: 控制策略对比

**实验目的**：比较纯反馈、纯前馈、复合控制的性能

**场景设置**：
- 初始稳态：Q_in = 10 m³/s, h_d = 2.0 m
- 在t=300s时，中段(x=500m)引入阶跃扰动：q_d = 2 m³/s
- 控制目标：维持h_d = 2.0 m

**测试策略**：
1. **纯反馈**：K_ff = 0, PID参数(2.0, 0.1, 5.0)
2. **纯前馈**：K_ff = 0.2, PID关闭(0, 0, 0)
3. **复合控制**：K_ff = 0.2, PID参数(2.0, 0.1, 5.0)

**性能指标**：
- IAE (积分绝对误差)
- ISE (积分平方误差)
- 最大偏差
- 调节时间（进入±2%误差带）
- 超调量

**预期结果**：
- 纯反馈：调节时间长，可能有超调
- 纯前馈：响应快，但有稳态误差（模型不精确）
- 复合控制：响应快，无稳态误差

### Part 2: 前馈增益优化

**实验目的**：找到最优的前馈增益K_ff

**方法**：
- 固定PID参数：Kp=2.0, Ki=0.1, Kd=5.0
- 测试不同K_ff：0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3
- 扰动：阶跃扰动 q_d = 2 m³/s

**评价指标**：
- IAE vs K_ff曲线
- ISE vs K_ff曲线
- 找到最优K_ff*

**分析**：
- K_ff太小：前馈补偿不足，主要靠反馈
- K_ff太大：过度补偿，反向偏差
- K_ff*：达到IAE最小

### Part 3: 扰动位置影响

**实验目的**：分析扰动位置对控制性能的影响

**场景**：
- 固定K_ff = 0.2, PID参数不变
- 在不同位置引入扰动：x_d = 250m, 500m, 750m
- 扰动量相同：q_d = 2 m³/s

**预期现象**：
- 扰动距下游越近，影响越快、越大
- 扰动距上游越近，有更多时间调节
- 前馈+反馈都能处理，但性能略有差异

### Part 4: 时变扰动响应

**实验目的**：测试对不同类型扰动的响应

**扰动类型**：
1. **阶跃扰动**：q_d = 0 → 2 m³/s
2. **斜坡扰动**：q_d = 0.01*t m³/s（缓慢增加）
3. **周期性扰动**：q_d = 1 + sin(2πt/600) m³/s

**对比**：
- 纯反馈 vs 复合控制
- 不同扰动形式下的性能

**预期**：
- 阶跃：复合控制优势最明显
- 斜坡：两者性能接近
- 周期性：复合控制能更好跟踪

## 工程意义

### 1. 前馈控制的应用场景

**适合的场景**：
- 扰动可测量（流量计、雨量计等）
- 扰动占主导地位
- 对控制性能要求高（响应快、超调小）

**实际案例**：
- 灌溉渠道：支渠引水可测
- 排水系统：降雨径流可预测
- 工业用水：取水量已知

### 2. 前馈增益调整指南

**步骤1**：从稳态增益开始
- 质量守恒：K_ff = 1.0（闸门开度单位）
- 或转换为流量增量

**步骤2**：实验微调
- 引入阶跃扰动
- 观察水位响应
- 调整K_ff使超调最小

**步骤3**：性能验证
- 测试不同扰动幅值
- 确保K_ff适用范围广

### 3. 传感器配置

**必需传感器**：
- 下游水位计：h_d (反馈)
- 扰动流量计：q_d (前馈)
- 上游流量计：Q_in (监测)

**可选传感器**：
- 多点水位计：改善估计
- 上游水位计：闸门流量计算

### 4. 控制系统实施

**硬件需求**：
- PLC/DCS控制器
- 模拟量输入：4-20mA（水位、流量）
- 模拟量输出：4-20mA（闸门开度）
- 采样周期：1-60秒

**软件实现**：
```c
// 伪代码
float u_total, u_ff, u_fb;
float h_sp = 2.0;  // 设定值
float K_ff = 0.2;  // 前馈增益

// 读取传感器
float h_d = read_level_sensor();
float q_d = read_flow_sensor();

// 前馈
u_ff = K_ff * q_d;

// 反馈（PID）
error = h_sp - h_d;
u_fb = PID_compute(error);

// 复合
u_total = u_ff + u_fb;
u_total = saturate(u_total, 0.1, 1.0);

// 输出
write_gate_opening(u_total);
```matlab

## 参数说明

### 渠道参数
| 参数 | 符号 | 数值 | 单位 |
|------|------|------|------|
| 渠道长度 | L | 1000 | m |
| 渠道宽度 | B | 5 | m |
| 渠底坡度 | i₀ | 0.001 | - |
| 曼宁糙率 | n | 0.025 | s/m^(1/3) |
| 节点数 | N | 21 | - |

### 控制参数
| 参数 | 数值 | 说明 |
|------|------|------|
| Kp | 2.0 | 比例增益 |
| Ki | 0.1 | 积分增益 |
| Kd | 5.0 | 微分增益 |
| K_ff | 0.15 - 0.25 | 前馈增益（需优化） |
| 采样周期 | 60 s | 控制周期 |

### 扰动参数
| 场景 | 位置 x_d | 幅值 q_d | 时间 |
|------|----------|----------|------|
| 阶跃扰动 | 500 m | 2 m³/s | t>300s |
| 斜坡扰动 | 500 m | 0.01t m³/s | 300-900s |
| 周期扰动 | 500 m | 1+sin(2πt/600) | 全程 |

## 性能评估

### 评价指标

**时域指标**：
1. IAE = ∫|e(t)|dt
2. ISE = ∫e²(t)dt
3. ITAE = ∫t|e(t)|dt
4. 调节时间：进入±2%误差带的时间
5. 超调量：max(h) - h_sp

**频域指标**（可选）：
1. 带宽
2. 相位裕度
3. 增益裕度

### 预期性能改善

相对于纯反馈控制，复合控制的性能改善：
- IAE：减少30-50%
- 调节时间：减少40-60%
- 超调量：减少50-70%

## 扩展思考

### 1. 自适应前馈增益

前馈增益可能随工况变化，可以设计自适应算法：
```python
# 基于误差的在线调整
K_ff_new = K_ff_old + α * e(t) * q_d(t)
```bash

### 2. 多扰动情况

如果有多个扰动源：
$$u_{ff} = \sum_{i=1}^n K_{ff,i} \cdot q_{d,i}$$

### 3. 模型预测控制（MPC）

MPC可以看作是更高级的前馈-反馈控制：
- 前馈：通过预测模型预见扰动影响
- 反馈：通过优化消除偏差

## 参考文献

1. Astrom, K. J., & Hagglund, T. (2006). *Advanced PID Control*. ISA.
2. Litrico, X., & Fromion, V. (2009). *Modeling and Control of Hydrosystems*. Springer.
3. Schuurmans, J., et al. (1999). Classification of Water Level Control Structures. *Journal of Irrigation and Drainage Engineering*.
4. Overloop, P. J. V. (2006). *Model Predictive Control on Open Water Systems*. IOS Press.

## 运行说明

```bash
# 运行完整演示
python main.py

# 输出结果
# - part1_strategy_comparison.png: 控制策略对比
# - part2_gain_optimization.png: 前馈增益优化
# - part3_disturbance_location.png: 扰动位置影响
# - part4_time_varying_disturbance.png: 时变扰动响应
# - 性能指标统计表
```

## 总结

案例3展示了前馈-反馈复合控制的设计和实现。关键要点：

1. **前馈控制**能够主动补偿已知扰动，响应快速
2. **反馈控制**能够消除误差，保证鲁棒性
3. **复合控制**结合两者优势，实现高性能
4. **前馈增益**需要根据系统特性设计和调整
5. **实际应用**需要可靠的扰动测量和适当的传感器配置

这种控制策略在水利工程中应用广泛，特别适合扰动可测且对性能要求高的场景。
