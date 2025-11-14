# 案例3：小型水电站智能发电设计

**难度等级**：⭐⭐⭐ 中高级  
**学习时间**：16学时（5学时水力设计 + 6学时控制设计 + 5学时在环测试）  
**智能化等级**：L3（多目标协调控制）  
**工程类型**：农村小水电站

---

## 📖 工程背景

### 项目概况

某县山区小型水电站：
- **功能**：河流径流式发电，为500户农村供电
- **装机容量**：2×500kW = 1000kW（2台机组）
- **设计水头**：40m（上游水库至厂房）
- **设计流量**：2.8 m³/s（单机1.4 m³/s）
- **发电机**：同步发电机，额定转速n=750 rpm
- **水轮机**：混流式水轮机
- **年发电量**：350万kWh
- **上网电价**：0.42元/kWh，年收益147万元

### 现状问题

- ❌ **人工调节**：调速器手动操作，频率波动大
- ❌ **频率不稳**：50 Hz ± 1.5 Hz，超出国标（±0.2 Hz）
- ❌ **功率波动**：负荷变化时功率跟踪慢
- ❌ **弃水严重**：汛期来水大，调节不及时，弃水30%
- ❌ **水库管理粗放**：不考虑下游生态需水

### 改造目标

- ✅ 频率控制精度：50 Hz ± 0.1 Hz（符合GB/T 15945）
- ✅ 功率响应速度：<10秒调整到目标功率
- ✅ 水位稳定控制：上游水库水位稳定
- ✅ 弃水减少：>20%（通过优化调度）
- ✅ 生态流量保障：下游最小流量>0.3 m³/s
- ✅ 智能化等级达到L3

---

## 📐 设计依据（中国标准）

### 主要标准

1. **GB/T 15945-2008** 《电能质量 电力系统频率偏差》⭐⭐⭐
   - §5.1 频率偏差允许值：±0.2 Hz（正常运行）
   - §5.2 频率偏差允许值：±0.5 Hz（事故后）

2. **DL/T 5186-2004** 《水电站机电设计规范》⭐⭐⭐
   - §6.3 水轮机调速系统
   - §7.2 发电机励磁系统

3. **SL 279-2002** 《水利水电工程等级划分及洪水标准》
   - 小型水电站等级划分

4. **NB/T 10506-2021** 《小水电站生态流量监测技术导则》
   - 生态流量计算与监测

### 参考标准
- GB/T 12666-2008 《水轮机基本参数系列》
- DL/T 5155-2016 《水电站压力钢管设计规范》

---

## 🔧 复用前序教材成果

### 从第2本书复用（明渠水力学）

```python
# 1. 复用水力计算模块
from books.open_channel_hydraulics.code.solvers.steady.pipe_flow import (
    compute_head_loss,        # 压力管道损失
    compute_flow_velocity     # 流速计算
)

# 2. 复用非恒定流模块（水库水量平衡）
# 类似案例13-15的非恒定流计算
```python

### 从第1本书复用（水系统控制）

```python
# 复用PID控制器
from books.water_system_control.code.control.pid import PIDController

# 频率控制器（调速器PID）
frequency_controller = PIDController(
    Kp=0.5,           # 比例系数
    Ki=0.1,           # 积分系数
    Kd=0.05,          # 微分系数
    setpoint=50.0,    # 目标频率50 Hz
    output_limits=(-100, 100),  # 导叶开度变化量
    windup_limit=50.0
)
```python

### 从案例1/2复用

```python
# 复用数字孪生框架
# 复用在环测试方法
# 复用性能评估方法
```matlab

---

## 📋 设计任务

### 第一部分：水力设计（基于DL/T 5186-2004）

#### 1.1 水轮机选型

**类型选择**：混流式水轮机（Francis Turbine）

**原因**：
- 水头H=40m，适合混流式（20-700m）
- 流量Q=1.4 m³/s，适合中小型机组
- 运行稳定，效率高

**型号**：HL110-WJ-70型混流式水轮机
- 额定水头：H_r = 40 m
- 额定流量：Q_r = 1.4 m³/s
- 额定转速：n_r = 750 rpm
- 额定功率：P_r = 500 kW
- 额定效率：η = 92%
- 比转速：n_s = 110

**水轮机特性曲线**：
```python
# η-Q曲线（效率-流量）
# P-Q曲线（功率-流量）
# n-Q曲线（转速-流量）
```python

#### 1.2 水力计算

**可用水头计算**：
```python
# 总水头
H_total = Z_reservoir - Z_tailrace  # 上游水库 - 尾水位
H_total = 40 m

# 沿程损失
h_f = f * (L/D) * (v^2 / 2g)
f = 0.02  # 摩阻系数（钢管）
L = 500   # 引水管长度 [m]
D = 1.2   # 管径 [m]
v = Q / A = 1.4 / (π * 0.6^2) = 1.24 m/s
h_f = 0.02 * (500/1.2) * (1.24^2 / 19.6) = 0.65 m

# 局部损失
h_m = Σξ * v^2 / 2g
h_m = 0.3 m  # 进口、弯头、阀门

# 净水头
H_net = H_total - h_f - h_m = 40 - 0.65 - 0.3 = 39.05 m

# 水轮机出力
P = 9.81 * Q * H_net * η
P = 9.81 * 1.4 * 39.05 * 0.92 = 493 kW ≈ 500 kW
```python

#### 1.3 上游水库设计

**水库参数**：
- 正常蓄水位：ΔZ = 442 m
- 死水位：ΔZ = 438 m
- 有效库容：V = 50,000 m³
- 调节性能：日调节
- 库面面积：A = 20,000 m²

**水量平衡**：
```
dV/dt = Q_in - Q_turbine - Q_overflow - Q_eco
```python

---

### 第二部分：控制系统设计

#### 2.1 系统架构

```
┌─────────────────────────────────────────┐
│  水电站监控系统（SCADA）                 │
│  - 实时监控（频率、功率、水位）          │
│  - 历史数据分析                         │
│  - 优化调度                             │
│  - 报表生成                             │
└───────────────┬─────────────────────────┘
                │ 以太网
┌───────────────┴─────────────────────────┐
│  励磁调节器（AVR）+ 调速器（Governor）   │
│  - 频率PID控制                          │
│  - 功率PID控制                          │
│  - 水位监测                             │
│  - 协调控制                             │
└───────────────┬─────────────────────────┘
                │ 4-20mA / 脉冲
┌───────────────┴─────────────────────────┐
│  传感器与执行器                         │
│  - 发电机频率表                         │
│  - 发电机功率表                         │
│  - 上游水位计                           │
│  - 下游流量计                           │
│  - 导叶伺服机构                         │
│  - 进水阀门                             │
└─────────────────────────────────────────┘
```matlab

#### 2.2 传感器配置

| 测点 | 类型 | 规格 | 数量 | 精度 |
|------|------|------|------|------|
| 发电机频率 | 频率表 | 45-55Hz | 1 | ±0.01Hz |
| 发电机功率 | 功率表 | 0-600kW | 1 | ±0.5% |
| 上游水位 | 超声波 | 438-442m | 1 | ±5mm |
| 下游流量 | 流量计 | 0-3 m³/s | 1 | ±1% |
| 导叶开度 | 位移传感器 | 0-100% | 2 | ±0.5% |
| 水轮机转速 | 转速表 | 0-1000rpm | 1 | ±1rpm |

**总计**：8个传感器

#### 2.3 调速器设计（频率控制）

**控制目标**：保持频率f = 50 Hz ± 0.1 Hz

**经典PID调速器**：
```python
class GovernorController:
    """
    水轮机调速器（L3智能化等级）
    
    功能：
    1. 频率PID控制（主回路）
    2. 功率前馈控制（辅助）
    3. 开度限制保护
    4. 速率限制（防止水锤）
    
    原理：
    频率偏差 → PID → 导叶开度调整 → 流量变化 → 功率变化 → 频率恢复
    """
    
    def __init__(self, rated_frequency=50.0):
        self.rated_frequency = rated_frequency
        
        # 频率PID控制器
        self.frequency_pid = PIDController(
            Kp=0.5,       # 比例系数（频率敏感）
            Ki=0.1,       # 积分系数（消除稳态误差）
            Kd=0.05,      # 微分系数（抑制震荡）
            setpoint=rated_frequency,
            output_limits=(-100, 100),  # 导叶开度变化量 [%]
            windup_limit=50.0
        )
        
        # 功率前馈控制器（负荷变化时快速响应）
        self.power_feedforward_gain = 0.2
        
        # 导叶参数
        self.guide_vane_opening = 50.0  # 当前开度 [%]
        self.max_opening_rate = 5.0     # 最大变化率 [%/s]（防水锤）
        
        # 保护参数
        self.opening_min = 10.0   # 最小开度（防空载）
        self.opening_max = 95.0   # 最大开度（防过载）
    
    def update(self, frequency, power_demand, dt):
        """
        调速器更新
        
        Parameters:
        -----------
        frequency : float
            当前发电机频率 [Hz]
        power_demand : float
            目标功率 [kW]
        dt : float
            时间步长 [s]
        
        Returns:
        --------
        guide_vane_opening : float
            导叶开度指令 [%]
        """
        # 1. 频率PID控制（主回路）
        frequency_error = self.rated_frequency - frequency
        opening_change_pid = self.frequency_pid.update(frequency, dt)
        
        # 2. 功率前馈（负荷变化时快速调整）
        # 功率增加 → 开大导叶
        opening_change_ff = self.power_feedforward_gain * (power_demand - 500)
        
        # 3. 总控制量
        opening_change = opening_change_pid + opening_change_ff
        
        # 4. 限制变化率（防水锤）
        max_change = self.max_opening_rate * dt
        opening_change = np.clip(opening_change, -max_change, max_change)
        
        # 5. 更新开度
        self.guide_vane_opening += opening_change
        self.guide_vane_opening = np.clip(
            self.guide_vane_opening, 
            self.opening_min, 
            self.opening_max
        )
        
        return self.guide_vane_opening
```python

#### 2.4 三目标协调控制（L3核心）

**目标**：
1. **频率控制**：f = 50 Hz ± 0.1 Hz（最高优先级）
2. **功率控制**：P = P_demand（根据负荷需求）
3. **水位控制**：维持水库水位在安全范围

**协调策略**：
```python
class CoordinatedController:
    """
    三目标协调控制器（L3）
    
    协调策略：
    1. 优先级：频率 > 功率 > 水位
    2. 冲突处理：
       - 频率异常：优先恢复频率，暂时牺牲功率和水位
       - 水位过高：增大发电，即使超出功率需求
       - 水位过低：减小发电，即使低于功率需求
    """
    
    def __init__(self):
        self.governor = GovernorController()
        
        # 水位控制器（次级）
        self.water_level_pid = PIDController(
            Kp=2.0, Ki=0.5, Kd=0.1,
            setpoint=440.0,  # 目标水位440m
            output_limits=(-0.5, 0.5)  # 功率调整量 [m³/s]
        )
        
        # 优先级权重
        self.w_frequency = 1.0   # 频率权重（最高）
        self.w_power = 0.5       # 功率权重
        self.w_water_level = 0.3 # 水位权重
    
    def update(self, frequency, power, water_level, power_demand, dt):
        """协调控制"""
        
        # 1. 频率控制（始终优先）
        opening = self.governor.update(frequency, power_demand, dt)
        
        # 2. 水位反馈调整
        water_level_adjustment = self.water_level_pid.update(water_level, dt)
        
        # 3. 协调决策
        if abs(frequency - 50.0) > 0.3:
            # 频率严重偏差，全力恢复
            pass  # 使用频率控制器输出
        elif water_level > 441.5:
            # 水位过高，增大发电（开大导叶）
            opening = min(opening + 10, 95)
        elif water_level < 438.5:
            # 水位过低，减小发电（关小导叶）
            opening = max(opening - 10, 10)
        
        return opening
```python

---

### 第三部分：动态设计特点（本书创新）

#### 3.1 水轮机动态模型

传统设计：只计算额定工况  
动态设计：建立全工况动态模型

```python
class FrancisTurbine:
    """
    混流式水轮机动态模型
    
    功能：
    - 水头-流量-功率-效率关系
    - 转矩-转速特性
    - 惯性时间常数
    - 水锤效应
    """
    
    def __init__(self, rated_head=40, rated_flow=1.4, rated_power=500):
        self.H_rated = rated_head
        self.Q_rated = rated_flow
        self.P_rated = rated_power
        self.eta_rated = 0.92
        
        # 转动惯量
        self.J = 1500  # kg·m² (水轮机+发电机)
        self.Ta = 8.0  # 惯性时间常数 [s]
        
        # 加载特性曲线
        self._load_characteristics()
    
    def compute_power(self, Q, H, opening):
        """
        计算水轮机出力
        
        P = 9.81 * Q * H * η(Q, opening)
        """
        eta = self.compute_efficiency(Q, opening)
        P = 9.81 * Q * H * eta / 1000  # kW
        return P
    
    def compute_efficiency(self, Q, opening):
        """
        效率计算（依赖流量和导叶开度）
        
        最高效率点：Q = Q_rated, opening = 70%
        """
        Q_ratio = Q / self.Q_rated
        opening_ratio = opening / 70.0
        
        # 简化效率模型（实际应用用厂家曲线）
        eta_max = self.eta_rated
        eta = eta_max * np.exp(-((Q_ratio - 1)**2 + (opening_ratio - 1)**2) / 0.5)
        
        return max(0.5, min(eta, 0.95))
```python

#### 3.2 发电机动态模型

```python
class SynchronousGenerator:
    """
    同步发电机模型
    
    摇摆方程：
    J * dω/dt = T_turbine - T_electric - T_damping
    """
    
    def __init__(self, rated_power=500, rated_speed=750):
        self.P_rated = rated_power
        self.n_rated = rated_speed  # rpm
        self.omega_rated = 2 * np.pi * self.n_rated / 60  # rad/s
        
        self.J = 1500  # 转动惯量 [kg·m²]
        self.D = 50    # 阻尼系数
        
        self.omega = self.omega_rated  # 当前角速度
    
    def update(self, T_turbine, P_electric, dt):
        """
        更新发电机状态
        
        Parameters:
        -----------
        T_turbine : float
            水轮机输出转矩 [N·m]
        P_electric : float
            电力负荷 [kW]
        dt : float
            时间步长 [s]
        """
        # 电磁转矩
        T_electric = P_electric * 1000 / self.omega
        
        # 阻尼转矩
        T_damping = self.D * (self.omega - self.omega_rated)
        
        # 摇摆方程
        d_omega = (T_turbine - T_electric - T_damping) / self.J * dt
        self.omega += d_omega
        
        # 限制范围
        self.omega = np.clip(self.omega, 0.9*self.omega_rated, 1.1*self.omega_rated)
        
        # 转换为频率
        frequency = self.omega / (2 * np.pi) * 60 / (750 / 50)  # Hz
        
        return frequency
```python

#### 3.3 生态流量保障

```python
def compute_ecological_flow(month):
    """
    计算生态流量需求（NB/T 10506-2021）
    
    方法：Tennant法（Montana法）
    - 优良生态：40% 多年平均流量
    - 一般生态：30%
    - 最小生态：10%
    """
    Q_avg_annual = 2.5  # 多年平均流量 [m³/s]
    
    # 丰水期（5-10月）vs 枯水期（11-4月）
    if 5 <= month <= 10:
        Q_eco = 0.30 * Q_avg_annual  # 30%
    else:
        Q_eco = 0.20 * Q_avg_annual  # 20%（枯水期可适当降低）
    
    return max(Q_eco, 0.3)  # 绝对最小0.3 m³/s
```matlab

---

### 第四部分：在环测试（本书核心）

#### 4.1 测试工况设计

**测试矩阵**（50种工况）:

| 工况类型 | 数量 | 描述 |
|---------|------|------|
| **正常工况** | 15 | |
| - 恒定负荷 | 5 | 100/200/300/400/500 kW |
| - 负荷渐变 | 5 | 线性增减 |
| - 负荷阶跃 | 5 | 突然甩负荷/加负荷 |
| **扰动工况** | 15 | |
| - 来水变化 | 5 | 丰/平/枯水期 |
| - 水位波动 | 5 | ±1m |
| - 频率扰动 | 5 | 电网频率波动 |
| **故障工况** | 10 | |
| - 调速器故障 | 3 | 响应滞后 |
| - 传感器故障 | 3 | 频率表失效 |
| - 紧急停机 | 4 | 快速关闭导叶 |
| **极端工况** | 10 | |
| - 洪水期 | 3 | 大流量 |
| - 枯水期 | 3 | 小流量 |
| - 冰冻期 | 2 | 低温启动 |
| - 负荷冲击 | 2 | 瞬时短路 |

#### 4.2 性能评估指标

**频率控制**：
- 稳态频率偏差：<0.1 Hz
- 动态频率偏差：<0.5 Hz（瞬态）
- 频率恢复时间：<10秒

**功率控制**：
- 功率跟踪误差：<5%
- 响应时间：<10秒
- 超调量：<10%

**水位控制**：
- 水位波动：±0.5 m
- 不溢流
- 不低于死水位

**效率与能耗**：
- 平均效率：>88%
- 年发电量：>330万kWh
- 弃水率：<10%

---

## 💡 关键设计参数表

| 参数类别 | 参数名 | 数值 | 单位 | 依据 |
|---------|--------|------|------|------|
| **水力参数** | | | | DL/T 5186 |
| 设计水头 | H | 40 | m | 实测 |
| 设计流量 | Q | 1.4 | m³/s | 计算 |
| 净水头 | H_net | 39.05 | m | 计算 |
| 管道损失 | h_f + h_m | 0.95 | m | 计算 |
| **水轮机参数** | | | | 厂家资料 |
| 型号 | - | HL110-WJ-70 | - | 选型 |
| 额定功率 | P | 500 | kW | |
| 额定效率 | η | 92 | % | |
| 额定转速 | n | 750 | rpm | |
| 比转速 | n_s | 110 | - | |
| **控制参数** | | | | 仿真整定 |
| 频率PID_Kp | Kp | 0.5 | - | |
| 频率PID_Ki | Ki | 0.1 | - | |
| 频率PID_Kd | Kd | 0.05 | - | |
| 目标频率 | f | 50.0 | Hz | GB/T 15945 |
| **保护参数** | | | | 经验值 |
| 最大开度变化率 | rate | 5.0 | %/s | 防水锤 |
| 导叶最小开度 | y_min | 10 | % | 防空载 |
| 导叶最大开度 | y_max | 95 | % | 防过载 |

---

## 🎯 与前序案例的对比

| 对比项 | 案例1（闸站） | 案例2（泵站） | 案例4（阀站） | 案例3（水电站） |
|-------|-------------|-------------|-------------|----------------|
| **控制对象** | 闸门开度 | 泵启停 | 阀门开度 | 导叶开度 |
| **控制目标** | 下游水位 | 进水池水位 | 出口压力 | **频率（主）+功率+水位** |
| **控制难度** | 简单 | 中等 | 中等 | **高（多目标）** |
| **控制层次** | 单目标 | 单目标 | 单目标 | **三目标协调** |
| **动态特性** | 慢（分钟级） | 中（分钟级） | 快（秒级） | **快（秒级，频率敏感）** |
| **智能化等级** | L3 | L2-L3 | L2 | **L3（协调控制）** |
| **复杂度** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | **⭐⭐⭐⭐** |

**案例3特点**：
- ✅ 多目标协调控制（频率、功率、水位）
- ✅ 动态模型最复杂（水轮机+发电机+水库）
- ✅ 实时性要求最高（频率控制秒级响应）
- ✅ 引入前馈控制（功率前馈）

---

## 💻 运行方式

```bash
cd /workspace/books/intelligent-water-network-design/code/examples/case_03_hydropower_station

# 运行主程序
python main.py

# 运行在环测试（50工况）
python run_hil_test.py
```

---

## 🔗 与其他案例的关系

**前序案例**:
- 案例1：学习了PID控制和数字孪生
- 案例2：学习了复杂动力学模型
- 案例4：学习了快速响应控制

**后续案例**:
- 案例20：流域梯级水电站（复用案例3×5）
- 案例22：流域防洪+发电多目标调度

**复用价值**:
- 案例3的调速器可复用到所有水电案例
- 多目标协调方法可推广到其他案例

---

## ⏭️ 下一个案例

**案例5：排涝闸站智能调度设计（L3）**
- 学习排涝优化调度
- 引入预报-调度-反馈闭环
- 多闸站协同

---

**案例3开发状态**: 🔄 开发中  
**预计完成时间**: 2周后  
**最后更新**: 2025-10-31
