# 案例16: 并网同步控制 - 锁相环(PLL)设计

## 📖 教学目标

掌握光伏并网系统的同步控制技术，理解锁相环(PLL)的工作原理及其在电网同步中的应用。

**核心内容**:
1. 锁相环基本原理
2. 同步参考坐标系PLL (SRF-PLL)
3. 频率与相位检测
4. 电网扰动响应

---

## 🎯 核心理论

### 1. 并网同步的重要性

并网逆变器必须满足：
- **相位同步**: 与电网电压同相位
- **频率跟踪**: 准确检测电网频率
- **快速响应**: 适应电网扰动

**不同步的后果**:
- 相位差 → 大电流冲击
- 频率偏差 → 功率振荡
- 响应慢 → 保护动作

### 2. 锁相环(PLL)基本原理

```python
电网电压 → [相位检测] → [环路滤波器] → 频率/相位 → [积分器] → 输出相位
                ↑                ↓                              ↓
                └──────────────── 反馈 ──────────────────────────┘
```

**工作原理**:
1. 检测相位误差
2. PI控制器调节频率
3. 积分得到相位角
4. 反馈形成闭环

---

### 3. SRF-PLL (同步参考坐标系PLL)

#### 数学模型

三相电网电压：
\[
\begin{cases}
v_a = V_m \sin(\theta_g) \\
v_b = V_m \sin(\theta_g - \frac{2\pi}{3}) \\
v_c = V_m \sin(\theta_g + \frac{2\pi}{3})
\end{cases}
\]

#### Clarke变换 (abc → αβ)
\[
\begin{bmatrix}
v_\alpha \\
v_\beta
\end{bmatrix}
=
\begin{bmatrix}
1 & 0 \\
\frac{1}{\sqrt{3}} & \frac{2}{\sqrt{3}}
\end{bmatrix}
\begin{bmatrix}
v_a \\
v_b
\end{bmatrix}
\]

#### Park变换 (αβ → dq)
\[
\begin{bmatrix}
v_d \\
v_q
\end{bmatrix}
=
\begin{bmatrix}
\cos\theta & \sin\theta \\
-\sin\theta & \cos\theta
\end{bmatrix}
\begin{bmatrix}
v_\alpha \\
v_\beta
\end{bmatrix}
\]

#### PLL控制

当 \( \theta \approx \theta_g \) 时：
- \( v_d \approx V_m \) (DC量)
- \( v_q \approx 0 \) (误差信号)

频率调节：
\[
\begin{cases}
\omega = \omega_0 + K_p v_q + K_i \int v_q \, dt \\
\theta = \int \omega \, dt
\end{cases}
\]

#### 参数设计

基于期望带宽 \( \omega_c \):
\[
\begin{cases}
K_p = 2\zeta\omega_c \\
K_i = \omega_c^2
\end{cases}
\]

通常: \( \zeta = 0.707 \) (临界阻尼), \( \omega_c = 2\pi \times 30 \text{Hz} \)

---

## 💻 代码实现

### 1. SRF-PLL实现

```python
from models.inverter_control import SRFPLL

# 创建PLL
pll = SRFPLL(
    Kp=50.0,           # 比例增益
    Ki=1000.0,         # 积分增益
    omega_nominal=2*np.pi*50.0  # 额定角频率
)

# 仿真循环
dt = 1e-4
for i in range(N):
    # 三相电网电压
    va = V_grid * np.sin(omega_grid * t)
    vb = V_grid * np.sin(omega_grid * t - 2*np.pi/3)
    vc = V_grid * np.sin(omega_grid * t + 2*np.pi/3)
    
    # PLL更新
    theta, omega, frequency = pll.update(va, vb, vc, dt)
    
    # theta: 检测到的相位角 (rad)
    # omega: 检测到的角频率 (rad/s)
    # frequency: 检测到的频率 (Hz)
```python

### 2. 单相PLL实现

```python
from models.inverter_control import SinglePhasePLL

# 创建单相PLL
pll = SinglePhasePLL(Kp=50.0, Ki=1000.0)

# 更新
theta, omega, frequency = pll.update(v, dt)
```python

### 3. 状态监控

```python
# 获取PLL状态
status = pll.get_status()
print(f"相位: {status['theta_deg']:.2f}°")
print(f"频率: {status['frequency']:.3f} Hz")
print(f"v_q误差: {status['v_q']:.2f} V")
```matlab

---

## 🧪 实验内容

### 实验1: SRF-PLL基本原理

**实验目的**: 验证PLL的锁相过程和稳态性能

**实验步骤**:
1. 设置三相平衡电网电压 (V=311V, f=50Hz)
2. 创建PLL (Kp=50, Ki=1000)
3. 运行200ms，观察相位跟踪过程
4. 分析dq坐标系电压变化

**预期结果**:
- 相位快速跟踪电网相位
- v_d收敛到幅值 (311V)
- v_q收敛到0 (误差消除)
- 频率稳定在50Hz

### 实验2: 频率阶跃响应

**实验目的**: 测试PLL对电网频率变化的跟踪能力

**实验步骤**:
1. 初始频率50Hz
2. t=0.1s时阶跃到50.5Hz
3. t=0.25s时阶跃到49.5Hz
4. 记录频率跟踪过程

**预期结果**:
- 快速跟踪频率变化
- 响应时间 < 50ms
- 相位误差瞬间增大后收敛

### 实验3: 相位跳变响应

**实验目的**: 测试PLL对相位突变的适应能力

**实验步骤**:
1. 稳定运行在50Hz
2. t=0.1s时相位跳变+30°
3. 观察恢复过程

**预期结果**:
- 相位误差快速收敛
- 恢复时间 < 100ms (误差<2°)
- 频率短暂波动后稳定

---

## 📊 性能指标

### 1. 稳态性能

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 相位精度 | < 1° | 相位跟踪误差 |
| 频率精度 | < 10mHz | 频率估计误差 |
| v_q误差 | < 5V | dq坐标系误差信号 |

### 2. 动态性能

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 频率阶跃响应 | < 50ms | 频率变化1Hz时 |
| 相位跳变恢复 | < 100ms | 相位跳变30°时 |
| 超调量 | < 10% | 频率响应超调 |

### 3. SRF-PLL优势

| 对比项 | 传统方法 | SRF-PLL |
|--------|----------|---------|
| 实现复杂度 | 高 | 中 |
| 相位精度 | 中 | 高 |
| 动态响应 | 慢 | 快 |
| 谐波抑制 | 差 | 好 |

---

## ⚙️ 工程应用

### 1. 参数整定

**步骤1: 确定带宽**
- 典型值: 20-50Hz
- 太低 → 响应慢
- 太高 → 噪声敏感

**步骤2: 计算PI参数**
\[
\begin{cases}
K_p = 2\zeta\omega_c \\
K_i = \omega_c^2 \\
\zeta = 0.707
\end{cases}
\]

示例 (带宽30Hz):
```python
omega_c = 2 * np.pi * 30  # 188.5 rad/s
zeta = 0.707
Kp = 2 * zeta * omega_c  # ≈ 266
Ki = omega_c ** 2         # ≈ 35530
```python

**步骤3: 仿真验证**
- 频率阶跃响应
- 相位跳变响应
- 谐波干扰抑制

### 2. 频率限幅

```python
# 防止频率越界
omega_min = 2 * np.pi * 45  # 45Hz
omega_max = 2 * np.pi * 55  # 55Hz
omega = np.clip(omega, omega_min, omega_max)
```python

### 3. 初始化策略

**方法1: 开环初始化**
```python
# 使用电网电压的Clarke变换估计初始相位
v_alpha, v_beta = clarke_transform(va, vb, vc)
theta_init = np.arctan2(v_beta, v_alpha)
pll.theta = theta_init
```python

**方法2: 预同步**
```python
# 运行一段时间后再启动逆变器
for _ in range(5000):  # 0.5秒 @ dt=1e-4
    pll.update(va, vb, vc, dt)
# 此时PLL已稳定
```python

### 4. 抗干扰措施

**滤波器**:
```python
# 对电网电压进行低通滤波
fc = 500  # 截止频率500Hz
alpha = dt * 2 * np.pi * fc / (1 + dt * 2 * np.pi * fc)
va_filtered = alpha * va + (1 - alpha) * va_filtered_prev
```python

**积分器抗饱和**:
```python
if abs(omega - omega_nominal) > omega_limit:
    integral = 0  # 重置积分
```

---

## 🎓 作业练习

### 练习1: 参数影响分析
对比不同带宽(10Hz, 30Hz, 50Hz)的PLL性能：
1. 计算对应的Kp和Ki
2. 仿真频率阶跃响应
3. 分析响应时间和超调量
4. 给出最优参数建议

### 练习2: 不平衡电网
模拟电网三相不平衡 (va=1.0, vb=0.9, vc=1.1):
1. 观察v_d和v_q的波动
2. 分析对频率估计的影响
3. 提出改进方案 (双同步坐标系PLL)

### 练习3: 谐波干扰
在电网电压中叠加5次谐波 (幅值10%):
1. 观察PLL输出的波动
2. 计算频率估计误差
3. 设计滤波器抑制谐波

### 练习4: 单相PLL优化
改进单相PLL的正交信号生成：
1. 实现T/4延迟法
2. 实现二阶广义积分器(SOGI)
3. 对比性能差异

---

## 📚 扩展阅读

### PLL变种
- **DSRF-PLL**: 双同步坐标系PLL (不平衡电网)
- **MAF-PLL**: 移动平均滤波器PLL (谐波抑制)
- **EPLL**: 增强型PLL
- **SOGI-PLL**: 二阶广义积分器PLL (单相)

### 进阶算法
- 自适应PLL
- 模糊PLL
- 神经网络PLL
- 滑模观测器

### 工程实践
- 数字实现 (量化、采样延迟)
- 电网故障检测
- 孤岛检测配合

---

## ❓ 常见问题

**Q1: 为什么选择SRF-PLL?**
A: SRF-PLL将AC量转为DC量，PI控制器可实现零稳态误差，结构简单性能好，是三相系统的首选。

**Q2: PLL带宽如何选择?**
A: 太低响应慢，太高易受噪声影响。典型值20-50Hz，根据具体应用调整。

**Q3: 电网不平衡时PLL会怎样?**
A: 标准SRF-PLL会在dq坐标系产生2倍频波动，影响频率估计。需使用DSRF-PLL或滤波器改进。

**Q4: 如何验证PLL性能?**
A: 关键指标：
- 稳态: 相位误差<1°, 频率误差<10mHz
- 动态: 频率阶跃响应<50ms
- 鲁棒性: 谐波抑制、不平衡适应

**Q5: 单相PLL精度为何较低?**
A: 单相需人工构造正交信号，引入误差。改进方法：SOGI、T/4延迟、锁频环(FLL)辅助。

---

## 📖 参考文献

1. Kaura, V., et al. "Operation of a Phase Locked Loop System Under Distorted Utility Conditions"
2. Rodriguez, P., et al. "New Positive-sequence Voltage Detector for Grid Synchronization"
3. Golestan, S., et al. "Three-Phase PLLs: A Review"
4. IEEE Std 1547-2018 "Standard for Interconnection"

---

**实验时间**: 1-2小时  
**难度等级**: ⭐⭐⭐⭐  
**前置知识**: 案例14(电流控制), dq坐标变换
