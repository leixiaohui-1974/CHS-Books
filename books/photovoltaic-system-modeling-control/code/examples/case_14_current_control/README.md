# 案例14: 电流控制

## 📋 案例概述

**难度等级**: ⭐⭐⭐⭐  
**预计学时**: 4学时  
**案例类型**: 并网逆变器核心控制

### 工程背景

电流控制是并网逆变器的核心，直接影响并网电流质量和系统稳定性。本案例从经典PI控制到高级PR控制，再到dq坐标系解耦控制，系统讲解电流控制技术。

### 学习目标

- 掌握PI控制器设计与整定方法
- 理解PR控制器的谐振原理
- 掌握dq坐标变换和Park变换
- 学会解耦控制的前馈补偿
- 对比不同控制方法的性能

---

## 📚 核心理论

### 1. PI控制器

**控制律**:
\[
u(t) = K_p \cdot e(t) + K_i \int e(t) dt
\]

**参数整定** (根据RL电路):
\[
K_p = L \cdot \omega_c, \quad K_i = R \cdot \omega_c
\]

其中ω_c是期望带宽。

**特点**:
- ✅ 简单实用
- ✅ 稳态误差为0
- ⚠️ 对交流信号有相位滞后
- 适用场合: dq坐标系

### 2. PR控制器

**控制律**:
\[
u(s) = K_p + \frac{K_r s}{s^2 + \omega_0^2}
\]

**离散化** (Tustin变换):
\[
H_r(z) = K_r \cdot \frac{b_0 + b_1 z^{-1} + b_2 z^{-2}}{1 + a_1 z^{-1} + a_2 z^{-2}}
\]

**特点**:
- ✅ 对ω₀频率无穷大增益
- ✅ 零稳态误差
- ⚠️ 对其他频率响应有限
- 适用场合: abc坐标系

### 3. dq坐标系控制

**Park变换** (abc → dq):
\[
\begin{bmatrix} i_d \\ i_q \end{bmatrix} = 
\begin{bmatrix} \cos\theta & \sin\theta \\ -\sin\theta & \cos\theta \end{bmatrix}
\begin{bmatrix} i_\alpha \\ i_\beta \end{bmatrix}
\]

**解耦控制**:
\[
v_d = v_{d,PI} - \omega L i_q
\]
\[
v_q = v_{q,PI} + \omega L i_d
\]

**特点**:
- ✅ 交流量→直流量
- ✅ dq轴独立控制
- ✅ 前馈解耦消除耦合
- 适用场合: 三相系统

---

## 💻 代码实现

### 1. PI控制器

```python
class PIController:
    def __init__(self, Kp, Ki, v_limit=None):
        self.Kp = Kp
        self.Ki = Ki
        self.v_limit = v_limit
        self.integral = 0.0
    
    def update(self, i_ref, i_measured, dt):
        error = i_ref - i_measured
        
        # 比例项
        p_term = self.Kp * error
        
        # 积分项
        self.integral += error * dt
        i_term = self.Ki * self.integral
        
        # 输出
        v_out = p_term + i_term
        
        # 限幅
        if self.v_limit:
            v_out = np.clip(v_out, -self.v_limit, self.v_limit)
        
        return v_out
```python

### 2. PR控制器

```python
class PRController:
    def __init__(self, Kp, Kr, omega_0, Ts, v_limit=None):
        self.Kp = Kp
        self.Kr = Kr
        self.omega_0 = omega_0
        self.Ts = Ts
        
        # Tustin离散化
        omega_sq = omega_0 ** 2
        Ts_sq = Ts ** 2
        
        self.b0 = Kr * 2 / Ts
        self.b1 = 0.0
        self.b2 = -Kr * 2 / Ts
        
        denom = 4 / Ts_sq + omega_sq
        self.a1 = (2 * omega_sq - 8 / Ts_sq) / denom
        self.a2 = (4 / Ts_sq - omega_sq) / denom
        
        # 状态变量
        self.e_k1 = 0.0
        self.e_k2 = 0.0
        self.u_r_k1 = 0.0
        self.u_r_k2 = 0.0
    
    def update(self, i_ref, i_measured, dt):
        error = i_ref - i_measured
        
        # 比例项
        p_term = self.Kp * error
        
        # 谐振项 (IIR滤波器)
        u_r = (self.b0 * error + 
               self.b1 * self.e_k1 + 
               self.b2 * self.e_k2 - 
               self.a1 * self.u_r_k1 - 
               self.a2 * self.u_r_k2)
        
        # 更新状态
        self.e_k2 = self.e_k1
        self.e_k1 = error
        self.u_r_k2 = self.u_r_k1
        self.u_r_k1 = u_r
        
        return p_term + u_r
```python

### 3. dq控制器

```python
class DQCurrentController:
    def __init__(self, Kp, Ki, L, omega, v_limit=None):
        self.L = L
        self.omega = omega
        self.pi_d = PIController(Kp, Ki, v_limit)
        self.pi_q = PIController(Kp, Ki, v_limit)
    
    def park_transform(self, i_a, i_b, i_c, theta):
        # Clarke: abc → αβ
        i_alpha = (2*i_a - i_b - i_c) / 3
        i_beta = (i_b - i_c) / np.sqrt(3)
        
        # Park: αβ → dq
        i_d = i_alpha * np.cos(theta) + i_beta * np.sin(theta)
        i_q = -i_alpha * np.sin(theta) + i_beta * np.cos(theta)
        
        return i_d, i_q
    
    def update(self, i_d_ref, i_q_ref, i_a, i_b, i_c, 
               theta, dt, enable_decoupling=True):
        # abc → dq
        i_d, i_q = self.park_transform(i_a, i_b, i_c, theta)
        
        # PI控制
        v_d_pi = self.pi_d.update(i_d_ref, i_d, dt)
        v_q_pi = self.pi_q.update(i_q_ref, i_q, dt)
        
        # 解耦
        if enable_decoupling:
            v_d = v_d_pi - self.omega * self.L * i_q
            v_q = v_q_pi + self.omega * self.L * i_d
        else:
            v_d = v_d_pi
            v_q = v_q_pi
        
        # dq → abc
        v_a, v_b, v_c = self.inverse_park_transform(v_d, v_q, theta)
        
        return v_a, v_b, v_c
```matlab

---

## 🔬 实验内容

### 实验1: PI控制器阶跃响应

**目的**: 观察PI控制器的动态和稳态性能

**步骤**:
1. 设计PI参数 (Kp=5, Ki=500)
2. 施加10A阶跃输入
3. 测量上升时间、超调量、稳态误差

**预期结果**:
- 上升时间: <5ms
- 超调量: <10%
- 稳态误差: <0.01A

### 实验2: PR控制器正弦跟踪

**目的**: 验证PR对50Hz正弦信号的零稳态误差

**步骤**:
1. 创建PR控制器 (Kp=5, Kr=1000)
2. 输入10A/50Hz正弦参考
3. 测量稳态误差

**预期结果**:
- RMS误差: <0.1A
- 误差百分比: <1%

### 实验3: PI vs PR对比

**对比指标**:
- 正弦跟踪误差
- 建立时间
- 实现复杂度

**结论**: PR在交流系统中优于PI

### 实验4: dq解耦控制

**目的**: 验证解耦控制的效果

**步骤**:
1. 设定dq参考电流 (id=10A, iq=0A)
2. 对比有/无解耦的响应
3. 观察dq电流的独立性

**预期结果**:
- d轴误差: <0.1A
- q轴误差: <0.1A
- 解耦后响应更快

---

## 📊 性能对比

| 指标 | PI | PR | dq-PI |
|------|----|----|-------|
| 稳态误差(AC) | 有 | 无 | 无 |
| 实现复杂度 | 低 | 中 | 中 |
| 计算量 | 低 | 中 | 中 |
| 适用场合 | DC/dq | AC | AC三相 |
| 调试难度 | 易 | 中 | 中 |
| 推荐度 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🔧 工程应用

### 1. 参数整定

**PI参数** (经验公式):
```python
# 方法1: 根据带宽
omega_c = 2 * pi * f_c  # 期望带宽
Kp = L * omega_c
Ki = R * omega_c

# 方法2: 根据时间常数
tau = L / R
Kp = alpha / tau
Ki = alpha / (tau * tau)
# alpha: 1-5 (调节系数)
```python

**PR参数**:
```python
Kp = 5-10      # 基础增益
Kr = 500-2000  # 谐振增益
omega_0 = 2 * pi * 50  # 基波
```python

### 2. 抗饱和措施

**积分限幅**:
```python
if integral > integral_max:
    integral = integral_max
```python

**条件积分**:
```python
if abs(error) < threshold:
    integral += error * dt
```

### 3. 实际考虑

- 采样延时补偿
- 数字滤波
- 过流保护
- 快速动态响应

---

## 📝 作业练习

1. 设计5kW逆变器的PI电流控制器
2. 实现多次谐波PR控制器 (3次、5次)
3. 对比不同Kp/Ki组合的性能
4. 实现前馈补偿提高动态响应

---

## 总结

✅ **PI**: 简单实用，适合dq系统  
✅ **PR**: 交流零误差，适合abc系统  
✅ **dq-PI**: 最优方案，三相系统首选  
✅ **解耦控制**: 消除dq耦合，提升性能

**下一步**: 案例15 - 电压控制 🚀

---

**完成日期**: 2025-11-04  
**版本**: v1.0  
**作者**: CHS-BOOKS Project
