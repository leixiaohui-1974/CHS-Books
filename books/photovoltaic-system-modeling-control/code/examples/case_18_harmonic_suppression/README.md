# 案例18: 谐波抑制

## 📖 教学目标

掌握谐波分析方法和抑制技术，理解谐波对电网的影响，实现高质量并网电流输出。

**核心内容**:
1. 谐波的产生与危害
2. FFT谐波分析
3. THD计算与评价
4. 多谐振PR控制器

---

## 🎯 核心理论

### 1. 谐波基础

#### 谐波定义

谐波是指频率为基波整数倍的正弦波分量：
\[
f_n = n \cdot f_0
\]

其中：
- \( f_n \): n次谐波频率
- \( f_0 \): 基波频率 (50Hz或60Hz)
- \( n \): 谐波次数 (2, 3, 4, ...)

#### 谐波来源

并网逆变器的谐波主要来源：
1. **PWM开关**: 载波频率及其倍频
2. **死区效应**: 低次谐波(3次、5次、7次)
3. **控制误差**: 电流跟踪不完美
4. **电网畸变**: 背景谐波

### 2. 谐波分析

#### FFT (快速傅里叶变换)

将时域信号分解为频域分量：
\[
X(k) = \sum_{n=0}^{N-1} x(n) e^{-j2\pi kn/N}
\]

#### 谐波幅值计算

对于n次谐波：
\[
I_n = 2 \left| \frac{1}{N} \sum_{k=0}^{N-1} i(k) e^{-j2\pi n k/N} \right|
\]

#### 总谐波畸变率 (THD)

\[
THD = \frac{\sqrt{\sum_{n=2}^{\infty} I_n^2}}{I_1} \times 100\%
\]

其中：
- \( I_1 \): 基波电流
- \( I_n \): n次谐波电流

### 3. 谐波标准

#### 并网标准 (IEEE 1547, GB/T 19964)

| 谐波次数 | 限值 (% of I1) |
|----------|----------------|
| 奇次 3-9次 | < 4.0% |
| 奇次 11-15次 | < 2.0% |
| 奇次 17-21次 | < 1.5% |
| 奇次 23-33次 | < 0.6% |
| 偶次 2-8次 | < 1.0% |
| 偶次 10-32次 | < 0.5% |
| **总THD** | **< 5.0%** |

---

## 💻 代码实现

### 1. 谐波分析

```python
from models.inverter_control import HarmonicAnalyzer

# 创建分析器
analyzer = HarmonicAnalyzer(f0=50.0)

# 采集数据
fs = 10000  # 采样频率10kHz
t = np.arange(0, 0.1, 1/fs)  # 100ms数据
signal = i_a_measured  # 实测电流

# FFT分析
result = analyzer.analyze(signal, fs, n_harmonics=20)

# 查看结果
print(f"基波幅值: {result['fundamental']:.2f} A")
print(f"THD: {result['thd']*100:.2f}%")

# 各次谐波
for n in range(2, 11):
    if n in result['harmonics']:
        h = result['harmonics'][n]
        print(f"{n}次谐波: {h['magnitude']:.2f} A ({h['magnitude']/result['fundamental']*100:.2f}%)")
```python

### 2. 多谐振PR控制器

```python
from models.inverter_control import MultiPRController

# 创建多谐振PR控制器
ctrl = MultiPRController(
    Kp=0.5,                      # 比例增益
    Kr_base=100.0,               # 谐振增益基准
    omega_0=2*np.pi*50,          # 基波角频率
    Ts=1e-4,                     # 采样周期
    harmonic_orders=[1, 3, 5, 7],  # 抑制的谐波次数
    v_limit=400.0                # 输出限幅
)

# 控制循环
dt = 1e-4
for t in time:
    # 参考电流 (通常来自功率控制)
    i_ref = I_peak * np.sin(omega * t)
    
    # 测量电流
    i_measured = measure_current()
    
    # 控制输出
    v_out = ctrl.update(i_ref, i_measured, dt)
    
    # 应用到逆变器
    apply_voltage(v_out)
```python

### 3. THD评估

```python
# 评估THD
def evaluate_thd(current_signal, fs):
    analyzer = HarmonicAnalyzer(f0=50.0)
    result = analyzer.analyze(current_signal, fs)
    thd = result['thd']
    
    if thd < 0.03:
        grade = "优秀"
    elif thd < 0.05:
        grade = "合格"
    else:
        grade = "不合格"
    
    print(f"THD: {thd*100:.2f}% - {grade}")
    return thd
```matlab

---

## 🧪 实验内容

### 实验1: FFT谐波分析

**实验目的**: 学习FFT分析含谐波信号

**实验步骤**:
1. 生成含多次谐波的测试信号
2. 使用FFT分析信号
3. 识别各次谐波的幅值和频率
4. 计算THD

**预期结果**:
- 准确检测基波和各次谐波
- THD计算准确
- 频谱图清晰

### 实验2: THD对比分析

**实验目的**: 比较不同谐波含量的THD

**测试工况**:
1. 纯正弦波 (THD ≈ 0%)
2. 含3次谐波 (10%)
3. 含3、5次谐波 (10%, 5%)
4. 含3、5、7次谐波 (10%, 5%, 3%)

**观察要点**:
- THD随谐波含量增加而增大
- 低次谐波影响更显著
- 并网标准要求THD < 5%

---

## 📊 性能指标

### 1. 电能质量标准

| 指标 | 要求 | 说明 |
|------|------|------|
| THD | < 5% | 并网基本要求 |
| 单次谐波 | 见表 | 不同次数有不同限值 |
| 功率因数 | > 0.95 | 配合谐波抑制 |

### 2. 控制性能

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 谐波抑制比 | > 20dB | 特定次谐波 |
| 基波跟踪误差 | < 2% | 不影响功率输出 |
| 控制带宽 | > 500Hz | 覆盖低次谐波 |

---

## ⚙️ 工程应用

### 1. 谐波抑制策略选择

**低次谐波 (3, 5, 7次)**:
- 使用多谐振PR控制器
- 针对性强，效果好
- 计算量适中

**高次谐波 (>15次)**:
- LC滤波器衰减
- 提高PWM开关频率
- 优化死区补偿

### 2. 滤波器设计

**LC滤波器参数**:
```python
# 截止频率设计
f_sw = 10000  # 开关频率10kHz
f_cutoff = f_sw / 10  # 截止频率约1kHz

L = 5e-3   # 5mH
C = 5e-6   # 5uF

# 验证截止频率
f_c = 1 / (2 * np.pi * np.sqrt(L * C))
print(f"截止频率: {f_c:.0f} Hz")  # 应约1kHz
```python

### 3. 实时监测

```python
# 实时THD监测
class THDMonitor:
    def __init__(self):
        self.analyzer = HarmonicAnalyzer(f0=50.0)
        self.window = []
        self.fs = 10000
        
    def update(self, sample):
        self.window.append(sample)
        
        # 每个周期计算一次
        if len(self.window) >= self.fs / 50:
            result = self.analyzer.analyze(np.array(self.window), self.fs)
            thd = result['thd']
            
            if thd > 0.05:
                print(f"⚠️ 警告: THD={thd*100:.2f}% 超标！")
            
            self.window = []  # 清空窗口
            return thd
```

---

## 🎓 作业练习

### 练习1: 谐波计算
已知电流信号:
\[
i(t) = 10\sin(100\pi t) + 2\sin(300\pi t) + 1\sin(500\pi t)
\]

1. 识别各次谐波
2. 计算THD
3. 判断是否满足并网标准

### 练习2: 滤波器设计
设计LC滤波器，要求：
- 开关频率: 10kHz
- 截止频率: 1kHz  
- 衰减率: -40dB/decade

计算L和C的值。

### 练习3: 谐波源分析
分析三种谐波产生原因：
1. PWM开关谐波的特点
2. 死区效应产生的谐波
3. 控制误差导致的谐波

### 练习4: 抑制效果评估
使用多谐振PR控制器前后对比：
- 抑制前: THD = 8%
- 抑制3、5、7次谐波后
- 预估THD改善效果

---

## 📚 扩展阅读

### 进阶控制
- 重复控制器 (Repetitive Controller)
- 自适应谐波补偿
- 有源滤波器 (APF)

### 谐波标准
- IEEE 519-2014
- IEC 61000-3-2
- GB/T 14549

### 工程实践
- 谐波潮流分析
- 谐波谐振风险评估
- 多逆变器并联谐波交互

---

## ❓ 常见问题

**Q1: 为什么逆变器会产生谐波？**
A: 主要原因：
- PWM开关的非线性
- 死区时间导致的电压误差
- 电流控制的跟踪误差
- 直流电压波动

**Q2: THD如何影响电网？**
A: 谐波危害：
- 增加线路损耗
- 干扰敏感设备
- 引起谐振过电压
- 降低功率因数

**Q3: 多谐振PR控制器的优势？**
A:
- 针对特定次谐波
- 零稳态误差
- 动态响应快
- 计算量可控

**Q4: 如何选择要抑制的谐波次数？**
A: 优先级：
1. 3、5、7次（幅值大，危害重）
2. 根据FFT分析结果
3. 考虑计算资源限制
4. 满足标准要求即可

**Q5: 谐波抑制和功率输出如何平衡？**
A:
- 基波控制优先（保证功率）
- 谐波抑制作为辅助
- 合理设置控制器增益
- 避免过度抑制影响动态

---

## 🎉 阶段三完成

恭喜完成**阶段三: 并网逆变器控制**全部6个案例！

**已完成**:
1. ✅ 案例13: PWM调制技术
2. ✅ 案例14: 电流控制
3. ✅ 案例15: 电压控制
4. ✅ 案例16: 并网同步
5. ✅ 案例17: 功率因数控制
6. ✅ 案例18: 谐波抑制

**掌握技能**:
- 并网逆变器完整控制链
- 从PWM到谐波抑制的全流程
- 满足并网标准的高质量输出

---

## 📖 参考文献

1. IEEE Std 1547-2018 "Interconnection Standard"
2. IEEE Std 519-2014 "Harmonic Control"
3. Teodorescu, R., et al. "Grid Converters for Photovoltaic Systems"
4. Zmood, D.N., et al. "Stationary Frame Current Regulation"

---

**实验时间**: 1.5小时  
**难度等级**: ⭐⭐⭐  
**前置知识**: 案例14(电流控制)

**🎊 下一步**: 进入阶段四 - 系统集成与优化
