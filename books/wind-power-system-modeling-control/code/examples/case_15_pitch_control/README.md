# 案例15: 变桨距控制

## 简介

本案例研究风力机变桨距控制系统，这是超额定风速下功率调节和载荷控制的关键技术。通过调节叶片桨距角β，可以改变叶片攻角和气动特性，实现功率限制和转速调节。本案例演示桨距角对功率的影响机理、PI桨距角控制器设计以及MPPT与变桨的综合控制策略(全风速范围控制)。变桨控制不仅用于功率限制，还是载荷减缓、紧急停机的重要手段，是现代大型风力机不可或缺的核心控制功能。

## 理论背景

叶片桨距角β定义为叶片弦线与旋转平面的夹角。当β=0°时，叶片处于最大捕能状态(Cp_max)；增大β会降低攻角，减小升力系数和功率系数，功率近似关系为Cp(β) ≈ Cp_max × (1 - β/β_max)²。变桨控制通常采用PI控制器：β = Kp×(ω - ω_rated) + Ki×∫(ω - ω_rated)dt，通过调节β使转速稳定在额定值，从而实现功率限制。PI参数设计需要考虑：(1)执行器限制：桨距角速率通常限制在3-10°/s；(2)系统延迟：液压或电动执行器响应时间0.2-0.5s；(3)稳定性：避免与塔架或传动系统模态耦合。全风速范围控制将Region II(MPPT, β=0°)和Region III(变桨限功率, β>0°)无缝衔接。

## 代码说明

### 主要类

**PitchController**: 变桨距控制器类
- `__init__(P_rated, omega_rated, Kp_pitch, Ki_pitch, beta_max)`: 初始化
  - P_rated: 额定功率 (W)
  - omega_rated: 额定转速 (rad/s)
  - Kp_pitch: 比例增益 (度/(rad/s))
  - Ki_pitch: 积分增益 (度/(rad/s)/s)
  - beta_max: 最大桨距角 (度)

- `compute_pitch_angle(omega, dt)`: 计算桨距角
  - 输入: 转速ω、时间步dt
  - 输出: 桨距角β
  - PI控制 + 限幅

**RegionController**: 分区综合控制器
- 结合MPPT控制器和变桨控制器
- 自动切换Region II和Region III

### 演示函数

- `demo_pitch_effect()`: 桨距角对功率的影响
  - 不同β下的功率曲线
  - β=0, 5, 10, 15, 20度对比
  - Cp随β的降低

- `demo_pitch_control()`: 变桨距控制器
  - 超额定风速响应(12→16→20 m/s)
  - β调节过程
  - 转速和功率限制效果

- `demo_full_range_control()`: 全风速范围综合控制
  - Region II: MPPT (β=0°)
  - Region III: 变桨限功率 (β>0°)
  - 5-20 m/s线性扫描

## 运行方法

```bash
# 进入案例目录
cd /home/user/CHS-Books/books/wind-power-system-modeling-control/code/examples/case_15_pitch_control

# 运行案例
python main.py
```

## 参数说明

### 额定参数
- **P_rated**: 额定功率 = 2 MW
- **v_rated**: 额定风速 = 12 m/s
- **omega_rated**: 额定转速 = 2.5 rad/s (约24 RPM)

### PI参数
- **Kp_pitch**: 比例增益 = 3.0 度/(rad/s)
  - 过大: 超调、振荡
  - 过小: 响应慢
- **Ki_pitch**: 积分增益 = 0.3 度/(rad/s)/s
  - 消除稳态误差
  - 过大: 积分饱和

### 桨距角限制
- **beta_min**: 最小桨距角 = 0° (MPPT区)
- **beta_max**: 最大桨距角 = 25° (安全限制)
- **beta_rate**: 变化速率 ≤ 8°/s (执行器限制)

## 预期结果说明

运行本案例后将生成3张图表：

1. **case15_pitch_effect.png** (两图):
   - 桨距角对功率的影响:
     - β=0°: P_max ≈ 2.5 MW @ 15m/s
     - β=5°: P ≈ 2.0 MW @ 15m/s
     - β=10°: P ≈ 1.5 MW @ 15m/s
     - β=15°: P ≈ 1.0 MW @ 15m/s
     - β=20°: P ≈ 0.5 MW @ 15m/s

   - 桨距角对Cp的影响:
     - β增大 → Cp快速降低
     - 二次关系: Cp(β) ∝ (1-β/30)²

2. **case15_pitch_control.png** (四图):
   - 风速输入:
     - 12→16→20 m/s阶跃

   - 桨距角响应:
     - v=12 m/s: β≈0° (额定风速)
     - v=16 m/s: β≈8-10° (调节中)
     - v=20 m/s: β≈15-18° (高风速)

   - 转速调节:
     - 稳定在额定转速附近
     - 超调 < 5%

   - 功率限制:
     - 额定功率以上稳定在2 MW
     - 波动 < 3%

3. **case15_full_range_control.png** (四图):
   - 风速与分区:
     - 5-20 m/s线性增加
     - 12 m/s为额定风速分界线
     - 绿色: Region II (MPPT)
     - 橙色: Region III (变桨)

   - 转速变化:
     - Region II: 转速随风速增加
     - Region III: 转速稳定在额定值

   - 桨距角调节:
     - Region II: β=0°
     - Region III: β逐渐增大(0-20°)

   - 功率输出:
     - Region II: P ∝ v³
     - Region III: P = P_rated = 2 MW

### 控制台输出
- 不同风速和桨距角下的功率
- PI控制器参数
- 控制效果统计

## 工程应用

变桨控制的实际应用：

### 主要功能
1. **功率限制**: 超额定风速下稳定功率
2. **载荷减缓**:
   - 单桨控制(IPC): 减少1P载荷
   - 塔架阻尼: 减少塔架FA振动
3. **紧急停机**: 顺桨至90°快速停机
4. **启动控制**: 初始桨距角设置

### PI参数调优

#### 增益计算方法
基于线化模型调优:
- Kp ≈ J × ω_rated / (∂P/∂β)
- Ki ≈ Kp / Ti，Ti=5-10s

#### 增益调度
根据运行点调整PI参数:
- 低风速: 增大增益(快速响应)
- 高风速: 减小增益(稳定性)

### 执行器

#### 液压执行器
- **优点**: 力矩大、响应快
- **缺点**: 维护复杂、漏油风险
- **速率**: 8-10°/s

#### 电动执行器
- **优点**: 维护简单、精度高
- **缺点**: 成本高、故障率稍高
- **速率**: 5-8°/s

### 先进控制策略

#### 1. 单桨控制(IPC)
- 三个叶片独立控制
- 目标: 减少1P载荷
- 效果: 疲劳载荷降低10-20%

#### 2. 塔架阻尼控制
- 检测塔架振动
- 集体变桨抑制FA振动
- 效果: 塔底载荷降低5-10%

#### 3. 激光雷达前馈控制
- 上游风速预测
- 前馈补偿变桨
- 效果: 功率波动降低20-30%

### 故障保护
1. **超速保护**: ω > 1.2×ω_rated → 紧急顺桨
2. **过功率保护**: P > 1.1×P_rated → 增大β
3. **执行器故障**: 单个失效 → 集体顺桨
4. **传感器故障**: 转速传感器冗余

## 典型参数

### 2 MW机组
- ω_rated: 15-20 RPM
- β_rate: 8°/s
- Kp: 3-5
- Ki: 0.3-0.5

### 5 MW机组
- ω_rated: 12-15 RPM
- β_rate: 5-8°/s
- Kp: 2-4
- Ki: 0.2-0.4

## 参考文献

1. Bossanyi, E. A. (2000). The design of closed loop controllers for wind turbines. *Wind Energy*, 3(3), 149-163.
2. Bianchi, F. D., De Battista, H., & Mantz, R. J. (2007). *Wind Turbine Control Systems*. Springer.
3. van der Hooft, E. L., & van Engelen, T. G. (2004). Estimated wind speed feed forward control for wind turbine operation optimisation. *Proceedings of EWEC*, 22-25.
