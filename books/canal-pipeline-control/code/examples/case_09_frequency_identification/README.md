# 案例9：频域辨识方法

## 问题描述

在案例8中，我们学习了N4SID这一**时域辨识方法**，从时间序列数据构建状态空间模型。本案例将介绍**频域辨识方法**，它在频率域中分析系统的输入输出关系。

```python
辨识方法分类：

时域方法                    频域方法
┌──────────┐              ┌──────────┐
│ N4SID    │              │ ETFE     │
│ ARX      │              │ SPA      │
│ 最小二乘  │              │ Bode拟合 │
└──────────┘              └──────────┘
   时间序列                  频率响应
   直接估计参数              先估计频响再参数化
   需要长数据                处理周期信号
```

**频域方法的优势**：

1. **物理直观**：频率响应有明确的物理意义（增益、相位、带宽）
2. **噪声处理**：频域平均可以降低随机噪声影响
3. **非参数方法**：不需要预先假设模型结构
4. **频率选择性**：可以在特定频段精确辨识
5. **适合控制器设计**：Bode图、Nyquist图直接用于频域设计

**应用场景**：

- **频率响应测试**：扫频实验（chirp信号）
- **振动分析**：结构模态识别
- **控制系统调试**：闭环频率响应
- **滤波器设计**：频率特性要求
- **PID参数整定**：基于频域指标

**渠道系统的频域特性**：

- **低频特性**：主要动态（0.001-0.1 Hz）
- **幅值特性**：水位变化vs流量变化的增益
- **相位特性**：滞后时间（波动传播）
- **带宽**：系统响应速度

## 理论基础

### 1. 频率响应函数

**传递函数**（拉普拉斯域）：
$$G(s) = \frac{Y(s)}{U(s)}$$

**频率响应**（$s = j\omega$）：
$$G(j\omega) = |G(j\omega)| e^{j\angle G(j\omega)}$$

其中：
- $|G(j\omega)|$：幅频特性（magnitude）
- $\angle G(j\omega)$：相频特性（phase）

**Bode图**：
- 幅频图：$20\log_{10}|G(j\omega)|$ vs $\log_{10}\omega$（dB vs Hz）
- 相频图：$\angle G(j\omega)$ vs $\log_{10}\omega$（度 vs Hz）

**物理意义**：

对于正弦输入$u(t) = A\sin(\omega t)$，稳态输出为：
$$y(t) = A|G(j\omega)|\sin(\omega t + \angle G(j\omega))$$

即：
- 幅值放大：$|G(j\omega)|$倍
- 相位滞后：$\angle G(j\omega)$弧度

### 2. 经验传递函数估计（ETFE）

**Empirical Transfer Function Estimate**是最简单的频域辨识方法。

**基本思路**：

输入输出的傅里叶变换：
$$U(\omega) = \mathcal{F}\{u(t)\}, \quad Y(\omega) = \mathcal{F}\{y(t)\}$$

传递函数估计：
$$\hat{G}(\omega) = \frac{Y(\omega)}{U(\omega)}$$

**实现步骤**：

1. **采集数据**：输入$u(t)$和输出$y(t)$
2. **FFT计算**：$U(\omega) = \text{FFT}(u)$，$Y(\omega) = \text{FFT}(y)$
3. **相除得频响**：$\hat{G}(\omega_k) = Y(\omega_k) / U(\omega_k)$

**优点**：
- 简单直观
- 非参数方法
- 快速计算（FFT）

**缺点**：
- 噪声敏感（直接相除）
- 频率分辨率受限（$\Delta f = 1/T$）
- 需要足够激励（避免$U(\omega) \approx 0$）

### 3. 谱分析方法（SPA）

**Spectral Analysis**通过功率谱密度估计频率响应。

**交叉功率谱**：
$$\Phi_{yu}(\omega) = \mathbb{E}[Y(\omega) U^*(\omega)]$$

**自功率谱**：
$$\Phi_{uu}(\omega) = \mathbb{E}[U(\omega) U^*(\omega)]$$

**传递函数估计**：
$$\hat{G}(\omega) = \frac{\Phi_{yu}(\omega)}{\Phi_{uu}(\omega)}$$

**Welch方法**（改进的周期图法）：

1. **分段**：将数据分为$K$段，每段长度$L$，重叠50%
2. **加窗**：对每段应用窗函数（Hanning、Hamming）
3. **FFT**：计算每段的FFT
4. **平均**：对$K$段的功率谱平均

$$\Phi_{uu}(\omega) = \frac{1}{K} \sum_{k=1}^{K} |U_k(\omega)|^2$$

**优点**：
- 降低方差（平均多个估计）
- 减少频谱泄漏（窗函数）
- 更稳定的估计

**缺点**：
- 频率分辨率降低（分段后每段更短）
- 需要更多数据

### 4. 相干函数

**相干函数**衡量输入输出在某频率的线性相关性：
$$\gamma^2(\omega) = \frac{|\Phi_{yu}(\omega)|^2}{\Phi_{uu}(\omega) \Phi_{yy}(\omega)}$$

取值范围：$0 \leq \gamma^2(\omega) \leq 1$

**物理意义**：
- $\gamma^2 \approx 1$：输出完全由输入决定（线性关系好）
- $\gamma^2 \approx 0$：输出与输入无关（噪声、非线性、未测干扰）

**应用**：
- 识别有效频段
- 检测非线性
- 评估信噪比

### 5. 参数化模型拟合

ETFE和SPA给出**非参数**频率响应估计。为了得到**参数化模型**（传递函数），需要拟合。

**一阶系统**：
$$G(s) = \frac{K}{Ts + 1}$$

Bode图特征：
- 低频增益：$K$（dB：$20\log_{10}K$）
- 截止频率：$\omega_c = 1/T$
- 高频衰减：-20 dB/decade

**二阶系统**：
$$G(s) = \frac{K\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$

Bode图特征：
- 谐振峰：$\zeta < 0.7$时出现
- 谐振频率：$\omega_r = \omega_n\sqrt{1-2\zeta^2}$
- 高频衰减：-40 dB/decade

**延迟系统**：
$$G(s) = \frac{K}{Ts + 1} e^{-\tau s}$$

相位：
$$\angle G(j\omega) = -\arctan(\omega T) - \omega \tau$$

**拟合方法**：

1. **非线性最小二乘**：
$$\min_{\theta} \sum_{\omega} |G(\omega; \theta) - \hat{G}(\omega)|^2$$

2. **对数域拟合**：
$$\min_{\theta} \sum_{\omega} \left[\left(20\log|G(\omega; \theta)| - 20\log|\hat{G}(\omega)|\right)^2 + w_{\phi}(\angle G(\omega; \theta) - \angle \hat{G}(\omega))^2\right]$$

3. **Levy方法**：线性化的频域拟合

### 6. 激励信号设计

频域辨识的质量取决于激励信号的频谱。

**扫频信号（Chirp）**：

线性扫频：
$$u(t) = A\sin\left(2\pi\left(f_0 t + \frac{f_1 - f_0}{2T}t^2\right)\right)$$

从$f_0$扫到$f_1$，持续时间$T$。

**多正弦信号（Multisine）**：
$$u(t) = \sum_{k=1}^{N} A_k\sin(2\pi f_k t + \phi_k)$$

选择频率$f_k$覆盖感兴趣的频段。

**伪随机信号（PRBS）**：

时域看是随机跳变，频域看是宽带激励。

**白噪声**：

理论上频谱平坦，但需要长时间才能覆盖所有频率。

**选择原则**：

1. **频率覆盖**：包含系统主要动态的频段
2. **能量分布**：在感兴趣频段集中能量
3. **幅值限制**：满足系统约束（如闸门开度$[0, 1]$）
4. **持续时间**：至少覆盖几个最慢的时间常数

### 7. 频域方法的局限性

**适用条件**：
- 线性时不变系统（LTI）
- 稳定系统（闭环测试需小心）
- 平稳信号

**局限性**：

1. **非线性系统**：
   - 频率响应依赖于幅值
   - 出现高次谐波
   - 相干函数下降

2. **时变系统**：
   - 频率响应随时间变化
   - 需要短时傅里叶变换（STFT）

3. **瞬态响应**：
   - 频域方法关注稳态
   - 起动、大扰动等瞬态难以捕捉

4. **计算量**：
   - FFT虽快，但大数据量仍耗时
   - 参数拟合需要优化

## 实验设计

### Part 1: ETFE方法实现

**实验目的**：实现ETFE算法，在简单系统上验证

**步骤**：
1. 生成一阶或二阶测试系统
2. 激励信号：chirp扫频
3. ETFE估计频率响应
4. 与理论Bode图对比

### Part 2: Welch谱估计

**实验目的**：使用Welch方法改善频率响应估计

**对比**：
- 原始周期图（variance高）
- Welch方法（variance低，分辨率降低）
- 相干函数分析

### Part 3: 渠道系统频域辨识

**实验目的**：在渠道系统上应用频域辨识

**步骤**：
1. 设计chirp激励（频率范围0.001-0.1 Hz）
2. Saint-Venant仿真生成数据
3. ETFE/Welch估计频率响应
4. 拟合低阶传递函数模型
5. 验证模型（时域和频域）

### Part 4: 参数化模型拟合

**实验目的**：从频率响应拟合参数化模型

**模型**：
- 一阶+延迟：$G(s) = Ke^{-\tau s}/(Ts+1)$
- 二阶+延迟

**方法**：
- 非线性最小二乘（scipy.optimize）
- 对数域加权拟合

## 工程意义

### 1. 频域方法的优势

**场景1：周期性扰动**

渠道系统常受周期性扰动：
- 潮汐（12小时周期）
- 灌溉需求（日周期）
- 泵站启停

频域方法能精确分析特定频率的响应。

**场景2：控制器整定**

经典PID整定方法基于频域：
- Ziegler-Nichols频率响应法
- 相位裕度、增益裕度
- 带宽要求

**场景3：模态分析**

大型渠道网络的振荡模态：
- 识别振荡频率
- 阻尼比估计
- 模态形状

### 2. 与时域方法对比

| 特性 | 时域方法（N4SID） | 频域方法（ETFE/SPA） |
|------|-------------------|---------------------|
| 直观性 | 抽象（状态空间） | 直观（Bode图） |
| 噪声处理 | 中等 | 好（频域平均） |
| 非线性 | 局部线性化 | 需要小信号假设 |
| 瞬态响应 | 好 | 差（关注稳态） |
| 控制器设计 | 需转换 | 直接使用 |
| 计算量 | SVD较重 | FFT较快 |

**结合使用**：
1. 频域方法：快速了解系统特性（带宽、增益、相位）
2. 时域方法：精确建模（状态空间模型用于MPC）

### 3. 实际应用建议

**激励信号设计**：

对于渠道系统（慢动态）：
- 频率范围：0.001-0.1 Hz（周期10s-1000s）
- Chirp信号：线性或对数扫频
- 幅值：±10-20%额定开度
- 持续时间：至少1小时（覆盖低频）

**数据采集**：
- 采样频率：至少10倍最高频率
- 去趋势：移除均值和线性趋势
- 预滤波：抗混叠滤波器

**频率响应平滑**：
- 相邻频点平均
- 样条插值
- 低通滤波

**模型验证**：
- 时域验证：阶跃响应、脉冲响应
- 频域验证：残差分析
- 相干函数检查

### 4. 工程案例

**案例1：南水北调渠道**

- 问题：长距离调水，波动传播复杂
- 方法：扫频测试，识别各渠段频率响应
- 结果：获得简化模型用于分布式控制

**案例2：水电站调压室**

- 问题：水力振荡威胁稳定
- 方法：频域识别阻尼比和振荡频率
- 结果：设计阻尼器，提高稳定性

**案例3：管道系统水锤**

- 问题：高频压力波动
- 方法：宽带激励+频谱分析
- 结果：识别共振频率，避免激发

## 参数说明

### 渠道参数
| 参数 | 数值 | 单位 |
|------|------|------|
| 长度 L | 1000 | m |
| 宽度 B | 5 | m |
| 坡度 i₀ | 0.001 | - |
| 糙率 n | 0.025 | s/m^(1/3) |

### 频域辨识参数
| 参数 | 数值 | 说明 |
|------|------|------|
| 频率范围 | 0.001-0.1 Hz | 感兴趣频段 |
| FFT点数 | 2048 | 频率分辨率 |
| Welch分段数 | 8 | 平均次数 |
| 重叠率 | 50% | 分段重叠 |
| 窗函数 | Hanning | 减少泄漏 |

### Chirp信号参数
| 参数 | 数值 | 说明 |
|------|------|------|
| 起始频率 f₀ | 0.001 Hz | 低频 |
| 终止频率 f₁ | 0.1 Hz | 高频 |
| 持续时间 | 3600 s | 1小时 |
| 幅值 | 0.15 | 闸门开度变化 |

## 运行说明

```bash
python main.py
```

输出：
- `part1_etfe_method.png`: ETFE方法验证
- `part2_welch_spectrum.png`: Welch谱估计
- `part3_canal_frequency.png`: 渠道系统频域辨识
- `part4_model_fitting.png`: 参数化模型拟合

## 总结

案例9展示了频域辨识方法在渠道系统中的应用。关键要点：

1. **频域方法提供直观的物理洞察**：Bode图、相干函数
2. **ETFE是最简单的非参数方法**，但噪声敏感
3. **Welch方法通过平均降低方差**，提高估计质量
4. **相干函数用于验证**线性假设和识别有效频段
5. **参数化拟合得到简洁模型**，用于控制器设计
6. **激励信号设计很关键**：频率覆盖、能量分布
7. **与时域方法互补**：快速分析vs精确建模

频域方法在控制工程中有悠久历史，许多经典方法（Bode、Nyquist、Nichols）都基于频域。对于水利系统，频域方法特别适合：
- 低频动态分析
- 周期性扰动抑制
- PID参数整定
- 稳定性分析

## 参考文献

1. Ljung, L. (1999). *System identification: theory for the user* (2nd ed.). Prentice Hall.

2. Pintelon, R., & Schoukens, J. (2012). *System identification: a frequency domain approach* (2nd ed.). John Wiley & Sons.

3. Welch, P. (1967). The use of fast Fourier transform for the estimation of power spectra: a method based on time averaging over short, modified periodograms. *IEEE Transactions on audio and electroacoustics*, 15(2), 70-73.

4. Schoukens, J., Pintelon, R., & Rolain, Y. (2012). Mastering system identification in 100 exercises. John Wiley & Sons.

5. Åström, K. J., & Hägglund, T. (1995). *PID controllers: theory, design, and tuning* (2nd ed.). Instrument society of America Research Triangle Park, NC.

6. Franklin, G. F., Powell, J. D., & Emami-Naeini, A. (2015). *Feedback control of dynamic systems* (7th ed.). Pearson.
