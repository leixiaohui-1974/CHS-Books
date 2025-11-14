# 案例12: 功率信号反馈控制 (PSF Control)

## 简介

本案例研究功率信号反馈(Power Signal Feedback, PSF)控制策略，这是一种无需风速测量的最大功率点跟踪(MPPT)方法。PSF控制基于最优转矩曲线T_opt = Kopt×ω²，通过测量转速直接计算转矩指令，避免了TSR控制对风速计的依赖。本案例演示PSF控制原理、Kopt系数计算、最优转矩曲线以及与TSR控制的性能对比。PSF控制具有实现简单、鲁棒性强的优点，是工业应用中的主流MPPT方案之一。

## 理论背景

PSF控制的理论基础是：当风轮工作在最优叶尖速比λ_opt时，功率P = (1/2)ρπR²v³Cp_max，而λ_opt = ωR/v，代入消去风速v可得P = (1/2)ρπR⁵(ω/λ_opt)³Cp_max，转矩T = P/ω = Kopt×ω²，其中Kopt = (1/2)ρπR⁵Cp_max/λ_opt³。这意味着只要测量转速ω，就可以直接计算最优转矩指令T_opt，无需测量风速。PSF控制的优点包括：(1)无需风速计，降低成本和维护；(2)不受风速测量误差影响；(3)控制算法简单，易于实现。缺点是：(1)依赖准确的Kopt参数，需要风轮特性数据；(2)在低风速或高风速边界可能需要额外限制。

## 代码说明

### 主要类

**PSFController**: PSF控制器类
- `__init__(Kopt, R)`: 初始化控制器
  - Kopt: 最优转矩系数 (N·m·s²)
  - R: 风轮半径 (m)

- `compute_torque(omega)`: 计算最优转矩
  - 输入: 转速ω (rad/s)
  - 输出: 转矩指令T_opt = Kopt × ω²

- 静态方法:
  - `compute_Kopt(R, rho, Cp_max, lambda_opt)`: 计算Kopt系数
    - 公式: Kopt = 0.5 × ρ × π × R⁵ × Cp_max / λ_opt³

### 演示函数

- `demo_psf_principle()`: PSF控制原理
  - 最优转矩曲线T = Kopt × ω²
  - 不同风速下的最优工作点
  - 功率曲线P = T × ω = Kopt × ω³

- `demo_psf_tracking()`: PSF跟踪性能
  - 风速阶跃响应
  - 转速和功率动态
  - Cp跟踪精度

- `demo_psf_vs_tsr()`: PSF vs TSR对比
  - 测量噪声影响
  - Cp跟踪对比
  - 性能统计分析

## 运行方法

```bash
# 进入案例目录
cd /home/user/CHS-Books/books/wind-power-system-modeling-control/code/examples/case_12_psf_control

# 运行案例
python main.py
```

## 参数说明

### 风轮参数
- **R**: 风轮半径 = 40 m
- **rho**: 空气密度 = 1.225 kg/m³
- **Cp_max**: 最大功率系数 = 0.48
- **lambda_opt**: 最优叶尖速比 = 8.0

### Kopt计算
Kopt = 0.5 × ρ × π × R⁵ × Cp_max / λ_opt³
    = 0.5 × 1.225 × π × 40⁵ × 0.48 / 8³
    ≈ 2.88×10⁶ N·m·s²

### 转矩指令
T_opt = Kopt × ω²
- ω = 1.0 rad/s → T ≈ 2.88 MN·m
- ω = 2.0 rad/s → T ≈ 11.5 MN·m
- ω = 3.0 rad/s → T ≈ 25.9 MN·m

## 预期结果说明

运行本案例后将生成3张图表：

1. **case12_psf_principle.png** (两图):
   - 最优转矩曲线:
     - 二次曲线T = Kopt × ω²
     - 标注不同风速的最优工作点
     - 6、8、10、12、14 m/s对应不同转速

   - 功率曲线:
     - P = T × ω = Kopt × ω³
     - 三次曲线关系
     - 功率随转速快速增长

2. **case12_psf_tracking.png** (四图):
   - 风速输入:
     - 阶跃8→10→12 m/s

   - 转速响应:
     - 平滑增长
     - 惯性延迟约5-10秒

   - 功率输出:
     - 随风速阶跃增加
     - P ∝ v³关系

   - Cp跟踪:
     - 稳态Cp接近Cp_max(0.48)
     - 暂态波动小于5%

3. **case12_psf_vs_tsr.png** (四图):
   - 风速信号:
     - 实际风速(平滑)
     - 测量风速(含噪声)
     - TSR受测量误差影响

   - 转速对比:
     - PSF: 平滑稳定
     - TSR: 受噪声干扰波动

   - Cp对比:
     - PSF平均Cp: 约0.47-0.48
     - TSR平均Cp: 约0.46-0.47
     - PSF标准差更小

   - Cp分布直方图:
     - PSF分布更集中
     - TSR分布更分散

### 控制台输出
- Kopt计算值
- 不同风速下的最优工作点
- PSF和TSR性能对比统计
  - 平均Cp
  - Cp标准差

## 工程应用

PSF控制的实际应用：

### 优点
1. **无需风速计**:
   - 降低成本约5,000-10,000元/台
   - 减少维护(无结冰、故障问题)
2. **鲁棒性强**:
   - 不受风速测量误差影响
   - 不受风速计位置影响(机舱后方偏差)
3. **实现简单**:
   - 仅需转速测量
   - 算法简单: T = Kopt × ω²

### 缺点与改进
1. **参数依赖**:
   - 需要准确的Cp-λ曲线
   - Kopt参数标定重要
2. **边界处理**:
   - 低风速: 需设置最小转速
   - 高风速: 需切换到额定功率控制
3. **性能略逊于TSR**:
   - 在理想风速测量下，TSR理论更优
   - 但实际应用中PSF更可靠

### Kopt标定方法
1. **设计值计算**: 基于BEM或实测Cp-λ数据
2. **现场调优**: 在实际风电场微调Kopt
3. **自适应方法**: 在线估计和更新Kopt

## 应用场景选择

| 控制方法 | 优势 | 适用场景 |
|---------|------|---------|
| **TSR** | 精度高、理论最优 | 风速测量准确的陆上风电场 |
| **PSF** | 鲁棒、低成本 | 海上风电、高寒地区、低成本项目 |
| **HCS** | 自适应性强 | 未知风轮特性、老旧机组改造 |

## 参考文献

1. Morimoto, S., et al. (2005). Sensorless output maximization control for variable-speed wind generation system using IPMSG. *IEEE Transactions on Industry Applications*, 41(1), 60-67.
2. Koutroulis, E., & Kalaitzakis, K. (2006). Design of a maximum power tracking system for wind-energy-conversion applications. *IEEE Transactions on Industrial Electronics*, 53(2), 486-494.
3. Abdullah, M. A., et al. (2012). A review of maximum power point tracking algorithms for wind energy systems. *Renewable and Sustainable Energy Reviews*, 16(5), 3220-3227.
