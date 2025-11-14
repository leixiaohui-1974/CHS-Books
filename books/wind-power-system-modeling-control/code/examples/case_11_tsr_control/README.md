# 案例11: 最佳叶尖速比控制 (TSR Control)

## 简介

本案例研究最佳叶尖速比(Tip-Speed Ratio, TSR)控制策略，这是风力发电领域最常用的最大功率点跟踪(MPPT)方法。TSR控制通过测量风速和转速，计算参考转速使叶尖速比保持在最优值λ_opt，从而确保风轮始终工作在最大功率系数Cp_max点。本案例演示TSR控制原理、参考转速计算、PI转速控制器设计以及在风速变化条件下的跟踪性能。掌握TSR控制对于实现风能高效捕获、提升发电量具有重要意义。

## 理论背景

叶尖速比λ = ωR/v，定义为叶尖线速度与来流风速的比值。对于给定的风轮设计，存在一个最优叶尖速比λ_opt(典型值7-9)使得功率系数Cp达到最大值Cp_max。TSR控制的核心思想是：测量实时风速v，计算参考转速ω_ref = λ_opt×v/R，通过PI控制器调节发电机转矩T_g使实际转速跟踪参考转速。转矩指令T_g = Kp×(ω_ref - ω) + Ki×∫(ω_ref - ω)dt，其中Kp和Ki为PI参数。TSR控制的优点是理论简单、跟踪精确；缺点是依赖风速测量，而风速计通常安装在机舱后方，存在测量误差和延迟。实际应用中常采用滤波和补偿技术提高精度。

## 代码说明

### 主要类

**TSRController**: TSR控制器类
- `__init__(lambda_opt, R, Kp, Ki)`: 初始化控制器
  - lambda_opt: 最优叶尖速比 (无量纲)
  - R: 风轮半径 (m)
  - Kp: 比例增益 (N·m·s)
  - Ki: 积分增益 (N·m)

- `compute_torque(v_wind, omega, dt)`: 计算转矩指令
  - 输入: 风速v、转速ω、时间步dt
  - 输出: 转矩指令T_ref、实际λ

### 演示函数

- `demo_tsr_principle()`: TSR控制原理
  - 参考转速与风速的线性关系
  - ω_ref = λ_opt × v / R

- `demo_tsr_tracking()`: TSR跟踪性能
  - 风速阶跃响应(8→10→12 m/s)
  - 转速跟踪曲线
  - λ跟踪精度
  - 功率捕获

- `demo_tsr_disturbance()`: 湍流风扰动响应
  - 脉动风速输入
  - λ波动统计
  - Cp波动分析

## 运行方法

```bash
# 进入案例目录
cd /home/user/CHS-Books/books/wind-power-system-modeling-control/code/examples/case_11_tsr_control

# 运行案例
python main.py
```

## 参数说明

### 风轮参数
- **R**: 风轮半径 = 40 m
- **lambda_opt**: 最优叶尖速比 = 8.0
- **Cp_max**: 最大功率系数 = 0.48

### 控制器参数
- **Kp**: 比例增益 = 50,000-100,000 N·m·s
  - 过大: 超调、振荡
  - 过小: 响应慢
- **Ki**: 积分增益 = 500-1000 N·m
  - 消除稳态误差
  - 过大可能引起积分饱和

### 仿真参数
- **转动惯量**: J = 10^7 kg·m²
- **风速范围**: 5-15 m/s
- **参考转速范围**: 1-3 rad/s (约10-30 RPM)

## 预期结果说明

运行本案例后将生成3张图表：

1. **case11_tsr_principle.png** (两图):
   - 参考转速-风速关系:
     - 线性关系: ω_ref ∝ v
     - 斜率 = λ_opt / R
     - v=6m/s → ω≈1.2 rad/s
     - v=14m/s → ω≈2.8 rad/s

   - RPM单位转换:
     - 便于工程理解
     - 典型范围10-30 RPM

2. **case11_tsr_tracking.png** (四图):
   - 风速阶跃输入:
     - 8→10→12 m/s

   - 转速跟踪:
     - 实际转速(蓝色)跟踪参考转速(红色)
     - 响应时间约5-10秒
     - 超调小于5%

   - λ跟踪:
     - 稳态λ ≈ 8.0
     - 暂态偏差小于10%

   - 功率输出:
     - 功率随风速阶跃增加
     - P ∝ v³关系

3. **case11_tsr_disturbance.png** (四图):
   - 湍流风速:
     - 平均10 m/s
     - 湍流强度约20%

   - 转速响应:
     - 跟随风速波动
     - 滤波效果(惯性延迟)

   - λ波动:
     - 平均值≈8.0
     - 标准差约0.5-1.0
     - 大部分时间在λ_opt±0.5范围内

   - Cp波动:
     - 平均Cp接近Cp_max
     - 湍流导致Cp波动

### 控制台输出
- 不同风速下的参考转速
- 跟踪性能指标(误差、超调)
- 湍流条件下的统计特性(平均λ、Cp)

## 工程应用

TSR控制的实际应用：

### 优点
1. **理论最优**: 直接跟踪Cp_max
2. **精度高**: 稳态误差小
3. **响应快**: 带宽可达0.1-0.5 Hz

### 缺点与改进
1. **风速测量误差**:
   - 机舱位置测量偏差
   - 解决: 风速估算器、多点测量
2. **湍流影响**:
   - 高频波动难以跟踪
   - 解决: 低通滤波、限幅
3. **风速计维护**:
   - 结冰、故障
   - 解决: 无风速计MPPT(PSF/HCS)

### 参数调优
- **Kp选择**: 根据惯量J和响应时间要求
- **Ki选择**: 消除稳态误差，防止饱和
- **滤波器**: 风速信号低通滤波(截止频率0.1-0.5 Hz)

## 对比其他MPPT方法
- **TSR**: 需风速，精度高
- **PSF**: 无需风速，鲁棒性好
- **HCS**: 自适应，响应慢

## 参考文献

1. Bianchi, F. D., De Battista, H., & Mantz, R. J. (2007). *Wind Turbine Control Systems: Principles, Modelling and Gain Scheduling Design*. Springer.
2. Johnson, K. E., et al. (2006). Control of variable-speed wind turbines: standard and adaptive techniques for maximizing energy capture. *IEEE Control Systems Magazine*, 26(3), 70-81.
3. Pao, L. Y., & Johnson, K. E. (2011). Control of wind turbines. *IEEE Control Systems Magazine*, 31(2), 44-62.
