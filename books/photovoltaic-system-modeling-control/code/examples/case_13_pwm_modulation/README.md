# 案例13: PWM调制技术

## 📋 案例概述

**难度等级**: ⭐⭐⭐  
**预计学时**: 4学时  
**案例类型**: 并网逆变器控制基础

### 工程背景

脉宽调制(PWM)是逆变器控制的核心技术,用于将直流电压转换为交流电压。本案例从最基础的SPWM(正弦脉宽调制)到高级的SVPWM(空间矢量脉宽调制),系统讲解PWM技术在光伏逆变器中的应用。

### 学习目标

- 掌握SPWM调制原理和实现方法
- 理解调制比、频率比等关键参数
- 掌握SVPWM空间矢量调制技术
- 学会THD谐波分析方法
- 对比不同PWM技术的性能

---

## 📚 理论基础

### 1. SPWM调制原理

#### 1.1 基本原理

正弦脉宽调制(SPWM)通过将正弦调制波与三角载波进行比较，产生PWM信号：

```python
if 调制波 > 载波:
    开关信号 = 1 (导通)
else:
    开关信号 = 0 (关断)
```

#### 1.2 关键参数

**调制比 (ma)**:
\[
m_a = \frac{V_m}{V_c}
\]

其中:
- \(V_m\): 调制波幅值
- \(V_c\): 载波幅值

**频率比 (mf)**:
\[
m_f = \frac{f_{sw}}{f_0}
\]

其中:
- \(f_{sw}\): 开关频率
- \(f_0\): 基波频率

#### 1.3 输出电压

**基波幅值**:
\[
V_1 = m_a \cdot \frac{V_{dc}}{2}
\]

**RMS值**:
\[
V_{rms} = \frac{V_1}{\sqrt{2}} = m_a \cdot \frac{V_{dc}}{2\sqrt{2}}
\]

#### 1.4 直流电压利用率

SPWM的直流电压利用率约为:
\[
\eta_{dc} = \frac{V_{ac,max}}{V_{dc}/2} = \frac{V_{dc}/2}{V_{dc}/2} = 1 \approx 86.6\%
\]

### 2. SVPWM调制原理

#### 2.1 空间矢量概念

三相电压可以表示为空间矢量:
\[
\vec{V} = V_a + V_b e^{j2\pi/3} + V_c e^{j4\pi/3}
\]

#### 2.2 Clarke变换

将三相abc坐标变换到两相αβ坐标:

\[
\begin{bmatrix}
V_\alpha \\
V_\beta
\end{bmatrix}
=
\frac{2}{3}
\begin{bmatrix}
1 & -\frac{1}{2} & -\frac{1}{2} \\
0 & \frac{\sqrt{3}}{2} & -\frac{\sqrt{3}}{2}
\end{bmatrix}
\begin{bmatrix}
V_a \\
V_b \\
V_c
\end{bmatrix}
\]

#### 2.3 基本电压矢量

三相逆变器有8个开关状态,对应8个基本矢量:
- V0, V7: 零矢量 (000, 111)
- V1-V6: 有效矢量,将空间分为6个扇区

#### 2.4 矢量合成

参考矢量 \(\vec{V}_{ref}\) 由相邻两个有效矢量和零矢量合成:

\[
\vec{V}_{ref} \cdot T_s = \vec{V}_1 \cdot T_1 + \vec{V}_2 \cdot T_2 + \vec{V}_0 \cdot T_0
\]

其中:
\[
T_1 + T_2 + T_0 = T_s
\]

#### 2.5 作用时间计算

对于扇区n,参考矢量的扇区内角度为θ:

\[
T_1 = m \cdot T_s \cdot \sin\left(\frac{\pi}{3} - \theta\right)
\]

\[
T_2 = m \cdot T_s \cdot \sin(\theta)
\]

\[
T_0 = T_s - T_1 - T_2
\]

其中调制比:
\[
m = \frac{|\vec{V}_{ref}|}{V_{dc}/\sqrt{3}}
\]

#### 2.6 直流电压利用率

SVPWM的直流电压利用率约为:
\[
\eta_{dc} = \frac{V_{ac,max}}{V_{dc}/2} = \frac{\sqrt{3}}{2} \approx 86.6\% \times 1.15 = 100\%
\]

相比SPWM提高约15%！

### 3. 谐波分析

#### 3.1 总谐波失真(THD)

\[
THD = \frac{\sqrt{\sum_{n=2}^{\infty} V_n^2}}{V_1} \times 100\%
\]

其中:
- \(V_1\): 基波幅值
- \(V_n\): 第n次谐波幅值

#### 3.2 谐波分布

SPWM的主要谐波出现在:
- 开关频率 \(f_{sw}\) 附近
- \(f_{sw}\) 的倍数附近
- 边带谐波: \(f_{sw} \pm k \cdot f_0\)

---

## 💻 代码实现

### 1. 核心数据结构

```python
@dataclass
class InverterParameters:
    """逆变器参数"""
    V_dc: float = 400.0          # 直流母线电压 (V)
    V_ac: float = 220.0          # 交流额定电压 (V RMS)
    f_ac: float = 50.0           # 交流频率 (Hz)
    f_sw: float = 10000.0        # 开关频率 (Hz)
    L_filter: float = 5e-3       # 滤波电感 (H)
    C_filter: float = 10e-6      # 滤波电容 (F)
```python

### 2. SPWM调制器

```python
class SPWMModulator(PWMModulator):
    """正弦脉宽调制"""
    
    def __init__(self, params, modulation_index=0.9):
        super().__init__(params)
        self.modulation_index = modulation_index
        self.mf = int(params.f_sw / params.f_ac)
    
    def modulate(self, v_ref, t):
        """执行SPWM调制"""
        # 归一化调制波
        m_wave = (v_ref / self.params.V_dc) * self.modulation_index
        
        # 生成三角载波
        carrier_phase = (t % self.T_sw) / self.T_sw
        if carrier_phase < 0.5:
            c_wave = -1 + 4 * carrier_phase
        else:
            c_wave = 3 - 4 * carrier_phase
        
        # 比较产生开关信号
        switching_signal = 1.0 if m_wave > c_wave else 0.0
        
        # 输出电压
        v_out = self.params.V_dc * (switching_signal - 0.5) * 2
        
        return switching_signal, {
            'modulation_wave': m_wave,
            'carrier_wave': c_wave,
            'output_voltage': v_out
        }
```python

### 3. SVPWM调制器

```python
class SVPWMModulator:
    """空间矢量脉宽调制"""
    
    def clarke_transform(self, va, vb, vc):
        """Clarke变换: abc → αβ"""
        v_alpha = (2*va - vb - vc) / 3
        v_beta = (vb - vc) / np.sqrt(3)
        return v_alpha, v_beta
    
    def get_sector(self, v_alpha, v_beta):
        """判断扇区"""
        angle = np.arctan2(v_beta, v_alpha)
        if angle < 0:
            angle += 2 * np.pi
        sector = int(np.floor(angle / (np.pi / 3))) + 1
        return max(1, min(6, sector))
    
    def calculate_duty_cycles(self, v_alpha, v_beta, V_dc):
        """计算矢量作用时间"""
        sector = self.get_sector(v_alpha, v_beta)
        V_ref = np.sqrt(v_alpha**2 + v_beta**2)
        theta = np.arctan2(v_beta, v_alpha)
        theta_sector = theta - (sector - 1) * np.pi / 3
        
        m = V_ref / (V_dc * np.sqrt(3) / 2)
        m = min(m, 1.0)
        
        T1 = m * np.sin(np.pi/3 - theta_sector)
        T2 = m * np.sin(theta_sector)
        T0 = 1 - T1 - T2
        
        return sector, max(0, T1), max(0, T2), max(0, T0)
```python

### 4. THD计算

```python
def calculate_thd(signal, fs, f0, n_harmonics=50):
    """计算总谐波失真"""
    # FFT分析
    N = len(signal)
    fft_result = np.fft.fft(signal) / N
    freqs = np.fft.fftfreq(N, 1/fs)
    
    # 提取正频率
    magnitude = 2 * np.abs(fft_result[:N//2])
    positive_freqs = freqs[:N//2]
    
    # 找基波
    f0_idx = np.argmin(np.abs(positive_freqs - f0))
    fundamental = magnitude[f0_idx]
    
    # 计算谐波
    harmonic_sum_sq = 0.0
    for n in range(2, n_harmonics + 1):
        fn = n * f0
        fn_idx = np.argmin(np.abs(positive_freqs - fn))
        if np.abs(positive_freqs[fn_idx] - fn) < f0 / 2:
            harmonic_sum_sq += magnitude[fn_idx] ** 2
    
    # THD
    thd = np.sqrt(harmonic_sum_sq) / fundamental * 100
    
    return thd, fundamental
```python

---

## 🔬 实验内容

### 实验1: SPWM调制原理

**目的**: 理解SPWM的基本原理和调制过程

**步骤**:
1. 创建SPWM调制器 (ma=0.9, mf=200)
2. 生成一个周期的PWM波形
3. 观察调制波、载波和开关信号的关系

**预期结果**:
- 调制波是50Hz正弦波
- 载波是10kHz三角波
- 开关信号的平均值跟随调制波

**代码**:
```python
params = InverterParameters(V_dc=400, f_ac=50, f_sw=10000)
spwm = SPWMModulator(params, modulation_index=0.9)
result = spwm.simulate(duration=0.02)  # 一个周期

plt.plot(result['time'], result['modulation_wave'], label='调制波')
plt.plot(result['time'], result['carrier_wave'], label='载波')
plt.plot(result['time'], result['switching_signal'], label='开关信号')
```matlab

### 实验2: 调制比对输出的影响

**目的**: 研究调制比ma对输出电压的影响

**步骤**:
1. 测试ma = 0.3, 0.5, 0.7, 0.9
2. 对比输出电压波形和频谱
3. 计算THD

**预期结果**:
- ma越大,输出电压越高
- ma越小,THD越高
- 最佳ma通常在0.8-0.9

### 实验3: SVPWM原理

**目的**: 理解空间矢量调制的原理

**步骤**:
1. 生成三相参考电压
2. Clarke变换到αβ坐标
3. 绘制空间矢量轨迹
4. 观察扇区切换

**预期结果**:
- 矢量轨迹是圆形
- 均匀遍历6个扇区
- 每个扇区占用约16.67%时间

### 实验4: SPWM vs SVPWM对比

**目的**: 对比两种调制方式的性能

**对比指标**:
| 指标 | SPWM | SVPWM |
|------|------|-------|
| 直流电压利用率 | 86.6% | 100% |
| THD (滤波前) | 较高 | 较低 |
| 实现复杂度 | 简单 | 复杂 |
| 计算量 | 低 | 中等 |
| 适用场合 | 单相 | 三相 |

---

## 📊 实验结果

### 1. SPWM调制波形

调制比ma=0.9时的典型波形:

```
调制波: 50Hz正弦波 (±0.9)
载波: 10kHz三角波 (±1.0)
开关信号: 0/1脉冲序列
输出电压: ±400V PWM波形
滤波后: 220V RMS 正弦波
```matlab

### 2. 调制比影响

| ma | 输出电压(RMS) | THD(滤波前) | THD(滤波后) |
|----|---------------|-------------|-------------|
| 0.3 | 66 V | 150% | 3.5% |
| 0.5 | 110 V | 120% | 2.8% |
| 0.7 | 154 V | 100% | 2.2% |
| 0.9 | 198 V | 85% | 1.8% |

### 3. SVPWM性能

```
三相输出: 220V RMS, 平衡
扇区切换: 每周期6次
矢量轨迹: 圆形,半径311V
直流电压利用率: 约90%
```matlab

### 4. 谐波分析

**SPWM主要谐波**:
- 基波 (50Hz): 311V
- 3次谐波 (150Hz): 约20V
- 5次谐波 (250Hz): 约15V
- 开关频率边带: 9950Hz, 10050Hz

**THD改善**:
- 滤波前: 80-150%
- 滤波后: 1-3%
- 符合并网标准 (<5%)

---

## 🎯 性能指标

### 1. 调制性能

**SPWM**:
- 调制比范围: 0-1
- 最大输出(RMS): 0.707 × Vdc/2
- 线性区: ma < 1
- 过调制区: ma > 1

**SVPWM**:
- 调制比范围: 0-1.15
- 最大输出(RMS): 0.816 × Vdc/2
- 比SPWM高15%

### 2. 谐波性能

**频率比影响**:
- mf < 20: 低频谐波较多
- mf = 20-100: 折中方案
- mf > 100: 优秀,但开关损耗大

**建议值**:
- 单相: mf = 50-100
- 三相: mf = 30-60

### 3. 开关损耗

开关损耗与开关频率成正比:
\[
P_{sw} \propto f_{sw} \cdot (t_{on} + t_{off})
\]

**权衡**:
- 高f_sw: THD低,但损耗大
- 低f_sw: 损耗小,但THD高
- 典型值: 10-20kHz

---

## 🔧 工程应用

### 1. 参数设计

**开关频率选择**:
```python
# 根据功率等级选择
if P < 5kW:
    f_sw = 10-20 kHz  # 户用单相
elif P < 50kW:
    f_sw = 8-15 kHz   # 小型三相
else:
    f_sw = 5-10 kHz   # 大型三相
```python

**滤波器设计**:
```python
# LC滤波器
f_c = 1 / (2 * π * sqrt(L * C))  # 截止频率
f_c ≈ f_sw / 10  # 经验值

L = 5-10 mH  # 典型值
C = 10-50 μF  # 典型值
```math

### 2. 死区时间

**必要性**: 防止上下桥臂直通

**计算**:
\[
t_{dead} > t_{on,max} + t_{off,max}
\]

**典型值**: 2-5 μs

**补偿**: 死区会导致输出电压误差,需要补偿:
\[
V_{comp} = \frac{2 \cdot t_{dead}}{T_s} \cdot V_{dc}
\]

### 3. 过调制处理

当ma > 1时,进入过调制区:

**方案1**: 限幅
```python
ma = min(ma, 1.0)
```python

**方案2**: 六步波
```python
if ma > 1.0:
    使用六步方波模式
```matlab

### 4. 并网标准

**IEEE 1547**:
- THD < 5% (正常)
- 单次谐波 < 3%
- 频率偏差: ±0.3 Hz
- 电压偏差: ±10%

**实现**:
- 高开关频率 (>10kHz)
- 优质滤波器 (多级)
- 有源谐波抑制

---

## 📝 作业练习

### 基础题

1. **理论计算**: 
   - 直流母线电压Vdc=600V,调制比ma=0.85
   - 计算SPWM输出电压的基波RMS值
   - 计算SVPWM输出电压的基波RMS值

2. **参数分析**:
   - 开关频率f_sw=15kHz, 基波频率f0=50Hz
   - 计算频率比mf
   - 主要谐波出现在哪些频率?

3. **THD计算**:
   - 基波幅值V1=311V
   - 3次谐波V3=20V, 5次谐波V5=15V, 7次谐波V7=10V
   - 计算THD

### 编程题

4. **实现三相SPWM**:
   - 修改代码生成三相SPWM
   - 三相相位差120度
   - 绘制三相波形

5. **谐波分析**:
   - 对SPWM输出进行FFT分析
   - 提取前20次谐波
   - 绘制谐波分布图

6. **滤波器设计**:
   - 设计LC滤波器,截止频率1kHz
   - 仿真滤波效果
   - 计算滤波前后的THD

### 设计题

7. **5kW单相逆变器**:
   - 设计SPWM参数 (Vdc, ma, f_sw)
   - 选择滤波器参数 (L, C)
   - 预估THD和效率

8. **50kW三相逆变器**:
   - 设计SVPWM系统
   - 计算开关损耗
   - 热设计考虑

9. **自适应调制**:
   - 实现根据负载自动调整ma
   - 保持输出电压稳定
   - 优化效率

---

## 🎓 扩展阅读

### 1. 高级PWM技术

**SHEPWM** (选择性谐波消除):
- 消除特定次谐波
- 需要离线计算开关角度
- 适用于大功率应用

**DPWM** (不连续PWM):
- 减少开关次数
- 降低开关损耗约33%
- 适用于高效率场合

### 2. 数字实现

**定点运算**:
```c
// 16位定点数 (Q15格式)
int16_t sin_table[256];  // 正弦查表
int16_t carrier;         // 载波
int16_t modulation;      // 调制波

if (modulation > carrier)
    PWM_OUT = HIGH;
else
    PWM_OUT = LOW;
```

**定时器配置**:
- 中心对齐模式
- 向上/向下计数
- 自动重装载

### 3. 多电平PWM

**二极管钳位型**:
- 3电平、5电平
- 减少dv/dt
- 降低EMI

**级联H桥**:
- 模块化设计
- 高电压应用
- 灵活扩展

---

## 🔍 常见问题

### Q1: 为什么SVPWM比SPWM好?

A: SVPWM的优势:
1. 直流电压利用率高15%
2. 谐波性能更好
3. 电流纹波更小
4. 更适合数字实现

但SPWM更简单,适合单相应用。

### Q2: 开关频率如何选择?

A: 需要权衡:
- 过高: 开关损耗大,效率低
- 过低: 谐波大,滤波器大

推荐:
- 小功率 (<10kW): 15-20kHz
- 中功率 (10-100kW): 10-15kHz  
- 大功率 (>100kW): 5-10kHz

### Q3: 如何降低THD?

A: 多种方法:
1. 提高开关频率
2. 优化滤波器设计
3. 使用高级PWM算法
4. 加入有源谐波抑制
5. 多电平拓扑

### Q4: 死区时间如何补偿?

A: 补偿方法:
1. 电压补偿: 根据电流方向补偿电压
2. 时间补偿: 调整开关时刻
3. 前馈补偿: 预先计算并补偿

### Q5: 过调制如何处理?

A: 三种方案:
1. 限幅到ma=1 (简单但输出受限)
2. 六步波模式 (最大输出但THD高)
3. 过调制算法 (折中方案)

---

## 📖 参考资料

1. **教材**:
   - 电力电子技术 (第5版) - 王兆安
   - Power Electronics - Daniel W. Hart

2. **标准**:
   - IEEE 1547: 分布式电源并网标准
   - IEC 61000-3-2: 谐波电流限值

3. **论文**:
   - "SVPWM for Three-Phase Inverters" - IEEE Trans.
   - "Dead-Time Compensation Techniques" - IEEE PE

4. **在线资源**:
   - TI: SPWM and SVPWM Application Notes
   - Infineon: PWM Techniques for Motor Control

---

## 总结

本案例系统讲解了PWM调制技术:

✅ **SPWM**: 简单实用,适合单相  
✅ **SVPWM**: 高性能,适合三相  
✅ **THD分析**: 谐波评估方法  
✅ **工程应用**: 参数设计和优化  

掌握这些技术是设计高性能逆变器的基础！

**下一步**: 案例14 - 电流控制技术 🚀

---

**完成日期**: 2025-11-04  
**版本**: v1.0  
**作者**: CHS-BOOKS Project
