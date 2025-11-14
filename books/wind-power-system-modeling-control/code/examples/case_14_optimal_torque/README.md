# 案例14: 最优转矩控制

## 简介

本案例研究最优转矩控制策略，这是工业应用中最实用的MPPT实现方法。通过预先计算或测量得到最优转矩表(Torque Look-Up Table)，运行时根据当前转速查表获得转矩指令。本案例演示最优转矩表的生成方法、查表法控制实现以及分区控制策略(启动区、MPPT区、额定区、停机区)。最优转矩控制结合了PSF控制的无风速测量优点和查表法的计算高效性，是现代风力发电机组广泛采用的控制方案。

## 理论背景

最优转矩控制基于预先建立的转速-转矩映射关系T_opt(ω)。该映射可通过三种方法获得：(1)理论计算：基于BEM理论计算Cp-λ曲线，推导T_opt = Kopt×ω²；(2)风洞测试或现场测试：实测功率曲线，离线优化得到最优转矩表；(3)仿真优化：在Simulink等仿真环境中优化参数。查表法的优点是实时计算量小，适合嵌入式控制器。分区控制将风力机运行范围划分为四个区域：Region I(启动，T≈0)、Region II(MPPT，T=Kopt×ω²)、Region III(额定功率，T=P_rated/ω)、Region IV(切出/停机，T=大转矩制动)。各区域间平滑切换对控制性能至关重要。

## 代码说明

### 主要类

**OptimalTorqueController**: 最优转矩查表控制器类
- `__init__(omega_table, T_table)`: 初始化查找表
  - omega_table: 转速数组 (rad/s)
  - T_table: 对应的最优转矩数组 (N·m)

- `compute_torque(omega)`: 查表计算转矩
  - 输入: 当前转速ω
  - 输出: 转矩指令T_opt
  - 方法: 线性插值

### 演示函数

- `demo_optimal_torque_table()`: 最优转矩表生成
  - 转速范围离散化(0.5-3.0 rad/s, 50点)
  - 计算每个转速的最优转矩
  - 转矩-功率关系曲线

- `demo_lookup_control()`: 查表法控制
  - 风速变化响应
  - 转矩指令曲线
  - 功率输出

- `demo_region_control()`: 分区控制策略
  - Region I: 启动区(ω < 0.5 rad/s)
  - Region II: MPPT区(0.5 < ω < 2.5 rad/s)
  - Region III: 额定区(2.5 < ω < 3.0 rad/s)
  - Region IV: 停机区(ω > 3.0 rad/s)

## 运行方法

```bash
# 进入案例目录
cd /home/user/CHS-Books/books/wind-power-system-modeling-control/code/examples/case_14_optimal_torque

# 运行案例
python main.py
```

## 参数说明

### 转矩表参数
- **转速范围**: 0.5-3.0 rad/s (约5-30 RPM)
- **采样点数**: 50点
- **插值方法**: 线性插值

### 分区参数
- **ω_cut_in**: 切入转速 = 0.5 rad/s
- **ω_rated**: 额定转速 = 2.5 rad/s
- **ω_cut_out**: 切出转速 = 3.0 rad/s
- **T_rated**: 额定转矩 = 800 kN·m
- **P_rated**: 额定功率 = 2 MW

### 转矩计算公式
- Region I: T = 0
- Region II: T = Kopt × ω²
- Region III: T = P_rated / ω
- Region IV: T = 2 × T_rated (制动)

## 预期结果说明

运行本案例后将生成3张图表：

1. **case14_optimal_torque_table.png** (三图):
   - 最优转矩查找表:
     - T_opt vs ω曲线
     - 二次函数关系(MPPT区)
     - 离散采样点标注

   - 最优功率曲线:
     - P_opt vs ω
     - 三次函数关系: P = T × ω = Kopt × ω³

   - 转矩-功率关系:
     - T vs P
     - 用于性能分析

2. **case14_lookup_control.png** (四图):
   - 风速输入:
     - 正弦变化8±3 m/s

   - 转速响应:
     - 跟随风速波动
     - 惯性延迟

   - 转矩指令:
     - 查表得到
     - T ∝ ω²

   - 输出功率:
     - 随风速和转速变化

3. **case14_region_control.png** (两图):
   - 分区转矩控制:
     - Region I(灰色): T=0
     - Region II(绿色): T=Kopt×ω² (MPPT)
     - Region III(蓝色): T=P_rated/ω (恒功率)
     - Region IV(红色): T=大转矩 (制动)
     - 额定转矩参考线

   - 分区功率曲线:
     - Region I: P=0
     - Region II: P∝ω³ (抛物线)
     - Region III: P=常数(额定功率)
     - Region IV: P超过额定(制动)
     - 额定功率参考线

### 控制台输出
- 转矩表样本数据
- 查表控制性能统计
- 分区定义和切换点

## 工程应用

最优转矩控制的实际应用：

### 优点
1. **实时性好**: 查表计算快(μs级)
2. **无风速依赖**: 仅需转速测量
3. **灵活性高**: 可融合实测数据优化
4. **可靠性强**: 分区控制处理边界

### 实现要点

#### 1. 转矩表生成
- **离线计算**:
  - BEM仿真得到Cp-λ曲线
  - 计算T_opt(ω)关系
- **现场优化**:
  - 在风电场实测功率-转速数据
  - 曲线拟合得到最优表
- **混合方法**:
  - 设计值初始化
  - 运行数据微调

#### 2. 插值方法
- **线性插值**: 简单、快速
- **样条插值**: 平滑、精确
- **分段多项式**: 计算效率高

#### 3. 分区切换
- **平滑过渡**:
  - 避免转矩突变
  - 低通滤波或斜坡函数
- **滞环控制**:
  - 防止临界点抖动
  - 设置上下阈值

### 实际部署

#### 控制器配置
```python
# 转速采样
omega_sensor = get_generator_speed()  # rad/s

# 查表
T_ref = lookup_table(omega_sensor)

# 转矩限制
T_ref = clip(T_ref, T_min, T_max)

# 发送指令
set_generator_torque(T_ref)
```

#### 表格存储
- **存储格式**: 数组或函数拟合系数
- **内存占用**: 50点×2 = 100字节
- **更新机制**: OTA远程更新

### 性能优化
1. **表格精度**: 增加采样点(100-200点)
2. **边界处理**: 转速限制保护
3. **功率限幅**: 硬件保护
4. **故障检测**: 转速传感器冗余

## 对比其他方法

| 方法 | 计算量 | 存储需求 | 精度 | 鲁棒性 |
|-----|--------|----------|------|--------|
| **查表** | 低 | 低(kB) | 高 | 高 |
| **PSF** | 低 | 极低 | 中 | 中 |
| **HCS** | 低 | 极低 | 中低 | 高 |
| **TSR** | 中 | 低 | 最高 | 低 |

## 参考文献

1. Bianchi, F. D., De Battista, H., & Mantz, R. J. (2007). *Wind Turbine Control Systems*. Springer.
2. Johnson, K. E., et al. (2006). Control of variable-speed wind turbines. *IEEE Control Systems Magazine*, 26(3), 70-81.
3. Pao, L. Y., & Johnson, K. E. (2011). Control of wind turbines. *IEEE Control Systems Magazine*, 31(2), 44-62.
