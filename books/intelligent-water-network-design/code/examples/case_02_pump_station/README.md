# 案例2：提水泵站智能化设计

**难度等级**：⭐⭐ 中级  
**学习时间**：12学时（4学时水力设计 + 4学时控制设计 + 4学时在环测试）  
**智能化等级**：L2（单泵）→ L3（多泵协调）  
**工程类型**：灌区首部提水泵站

---

## 📖 工程背景

### 项目概况

某县级灌区首部提水泵站：
- **功能**：从河道提水至总干渠，供应5000亩灌区
- **设计扬程**：15m（从河道ΔZ=50m至渠首ΔZ=65m）
- **设计流量**：3.6 m³/s（灌溉高峰期）
- **装机方案**：3台立式轴流泵，单泵流量1.2 m³/s
- **总装机功率**：250kW（单泵80-85kW）
- **年运行时间**：2000小时（灌溉季）
- **年电费**：约35万元（按0.7元/kWh）

### 现状问题

- ❌ **人工启停**：需要1人24小时值守，劳动强度大
- ❌ **能耗高**：启停不合理，低效区运行多
- ❌ **水锤风险**：手动关闭太快，管道易损坏
- ❌ **应急能力弱**：夜间故障无法及时响应

### 改造目标

- ✅ 自动启停，无人值守
- ✅ 能耗优化，节电15%以上
- ✅ 水锤保护，延长管道寿命
- ✅ 远程监控，故障及时报警
- ✅ 智能化等级达到L2-L3

---

## 📐 设计依据（中国标准）

### 主要标准

1. **GB 50265-2022** 《泵站设计标准》⭐⭐⭐
   - §4.2.3 泵站设计流量计算
   - §5.3.1 水泵选型原则
   - §6.2.4 进出水池设计
   - §8.1 泵站自动化与信息化

2. **SL 285-2003** 《泵站安全鉴定规程》
   - 泵站安全等级划分
   - 设备安全评价标准

3. **GB/T 29529-2013** 《泵送系统能效评估导则》
   - 泵送系统能效评价方法
   - 节能潜力分析

### 参考标准
- GB 50289-2016 《城市工程管线综合规划规范》
- DL/T 5151-2014 《泵站技术改造规范》

---

## 🔧 复用前序教材成果

### 从第2本书复用（明渠水力学）

```python
# 1. 复用第2本书案例10：泵站设计计算
from books.open_channel_hydraulics.code.models.pump import (
    Pump,                    # 泵模型
    compute_system_curve,    # 系统特性曲线
    find_operating_point     # 工况点计算
)

# 2. 复用第2本书案例25-27：水锤分析
from books.open_channel_hydraulics.code.solvers.unsteady.water_hammer import (
    WaterHammerAnalyzer,     # 水锤分析器
    compute_hammer_pressure  # 水锤压力计算
)

# 使用示例
pump = Pump(
    Q_rated=1.2,   # 额定流量1.2 m³/s
    H_rated=15.0,  # 额定扬程15m
    P_rated=80.0,  # 额定功率80kW
    speed=1450     # 转速rpm
)

# 计算工况点
H, eta, P = pump.compute_operating_point(Q=1.0)
print(f"流量1.0m³/s时：扬程{H:.2f}m, 效率{eta:.2%}, 功率{P:.2f}kW")
```

### 从第1本书复用（水系统控制）

```python
# 复用第1本书案例4：PID控制器
from books.water_system_control.code.control.pid import PIDController

# 进水池水位控制器
level_controller = PIDController(
    Kp=1.5,           # 比例系数
    Ki=0.3,           # 积分系数
    Kd=0.05,          # 微分系数
    setpoint=3.5,     # 目标水位3.5m
    output_limits=(0, 3),  # 输出0-3台泵
    windup_limit=2.0  # 抗积分饱和
)

# 复用第1本书案例6：阶跃响应分析
from books.water_system_control.code.examples.case_06_step_response import (
    calculate_step_response_metrics
)
```

### 从第3本书复用（渠道管道控制）

```python
# 复用第3本书的数字孪生思想（案例13）
# 复用多智能体协调控制方法
```

---

## 📋 设计任务

### 第一部分：水力设计（基于GB 50265-2022）

#### 1.1 设计参数确定

**设计流量计算**（GB 50265-2022 §4.2.3）:
```python
# 灌溉设计流量
Q_design = irrigation_area * unit_flow_rate
Q_design = 5000亩 × (1.67/666.7亩) m³/s = 12.5 m³/s

# 考虑渠系利用系数
eta_canal = 0.85  # 渠道水利用系数
Q_pump_station = Q_design / eta_canal = 14.7 m³/s

# 考虑轮灌制度（3个轮灌组）
Q_actual = Q_pump_station / 3 = 4.9 m³/s

# 取整后：设计流量 Q = 5.0 m³/s
# 装机方案：3×1.2 = 3.6 m³/s（2开1备）
```

**设计扬程计算**:
```python
# 复用第2本书的水力计算
from books.open_channel_hydraulics.code.solvers.steady.pipe_flow import (
    compute_friction_loss,  # 沿程损失
    compute_local_loss      # 局部损失
)

# 总扬程 = 净扬程 + 管道损失
H_static = 15.0  # 静扬程（高差）
h_f = compute_friction_loss(L=500, D=0.8, Q=2.4, roughness=0.0002)
h_m = compute_local_loss(v=3.0, loss_coef=[0.5, 1.0, 0.2])  # 进口、弯头、阀门

H_design = H_static + h_f + h_m + margin
print(f"设计扬程 H = {H_design:.2f} m")
```

#### 1.2 水泵选型

**型号选择**（查水泵型谱）:
```
初选：ZLB立式轴流泵
- 流量范围：0.6-1.5 m³/s
- 扬程范围：12-18 m
- 比转速：ns = 500-700
- 效率：>75%

最终选型：ZLB-1200型
- 额定流量：1.2 m³/s
- 额定扬程：15 m
- 额定效率：78%
- 额定功率：80 kW
- 转速：1450 rpm
```

**特性曲线数据**:
```python
# 泵特性曲线（厂家提供）
pump_curve_data = {
    'Q': [0.6, 0.8, 1.0, 1.2, 1.4, 1.6],  # 流量 m³/s
    'H': [17.5, 16.8, 16.0, 15.0, 13.8, 12.2],  # 扬程 m
    'eta': [0.65, 0.72, 0.76, 0.78, 0.75, 0.68],  # 效率
    'P': [65, 70, 75, 80, 85, 90]  # 功率 kW
}
```

#### 1.3 进出水池设计

**进水池设计**（GB 50265 §6.2.4）:
```python
# 有效容积计算
V_inlet = Q_max * T_switch
V_inlet = 3.6 m³/s × 5分钟 = 1080 m³

# 池体尺寸
# 平面：15m × 15m = 225 m²
# 深度：5.0m（有效水深3.0-4.5m）
# 有效容积：225 × 1.5 = 337.5 m³（调整为500 m³）
```

**出水池设计**:
```python
# 出水池容积
V_outlet = Q_pump * T_stabilize
V_outlet = 2.4 m³/s × 3分钟 = 432 m³

# 池体尺寸：12m × 12m × 4m
```

---

### 第二部分：智能体系统设计

#### 2.1 系统架构

```
┌─────────────────────────────────────────┐
│  监控中心（云端/本地机房）               │
│  - 实时监控界面                         │
│  - 历史数据分析                         │
│  - 远程启停控制                         │
│  - 报警管理                             │
└───────────────┬─────────────────────────┘
                │ 4G/以太网
┌───────────────┴─────────────────────────┐
│  泵站PLC控制柜（边缘计算）               │
│  - PID控制算法                          │
│  - 启停逻辑                             │
│  - 保护逻辑                             │
│  - 数据采集                             │
└───────────────┬─────────────────────────┘
                │ 4-20mA / RS485
┌───────────────┴─────────────────────────┐
│  传感器与执行器                         │
│  - 进水池水位（2个冗余）                │
│  - 出水池水位                           │
│  - 出口流量计                           │
│  - 出口压力表                           │
│  - 3台泵电机（变频器/软启动器）         │
│  - 电流、电压、功率检测                 │
│  - 振动、温度监测                       │
└─────────────────────────────────────────┘
```

#### 2.2 传感器配置

| 测点 | 类型 | 规格 | 数量 | 精度 |
|------|------|------|------|------|
| 进水池水位 | 超声波/压力式 | 0-5m | 2 | ±5mm |
| 出水池水位 | 超声波 | 0-5m | 1 | ±5mm |
| 出口流量 | 电磁流量计 | DN800 | 1 | ±0.5% |
| 出口压力 | 压力变送器 | 0-1.0MPa | 1 | ±0.2% |
| 泵电流 | 电流互感器 | 0-200A | 3 | ±0.5% |
| 泵振动 | 振动传感器 | - | 3 | - |
| 泵温度 | 温度传感器 | 0-100°C | 3 | ±1°C |

**总计**：14个传感器

#### 2.3 控制器设计

**2.3.1 单泵控制（L2）**

```python
# 单台泵的PID水位控制
from books.water_system_control.code.control.pid import PIDController

single_pump_controller = PIDController(
    Kp=0.8,           # 比例系数（调试获得）
    Ki=0.2,           # 积分系数
    Kd=0.05,          # 微分系数
    setpoint=3.5,     # 进水池目标水位3.5m
    output_limits=(0, 1),  # 开/停
    windup_limit=0.5
)

# 控制逻辑
def control_single_pump(water_level, dt):
    """单泵控制"""
    u = single_pump_controller.update(water_level, dt)
    
    if u > 0.5:
        pump_command = 'ON'
    else:
        pump_command = 'OFF'
    
    return pump_command
```

**2.3.2 多泵协调控制（L3）**

```python
class MultiPumpController:
    """
    多泵协调控制器（L3）
    
    功能：
    1. 根据水位决定开泵台数（0-3台）
    2. 轮换运行（均衡磨损）
    3. 避免频繁启停（最小运行/停机时间）
    4. 考虑峰谷电价（如有调蓄能力）
    """
    
    def __init__(self, n_pumps=3):
        self.n_pumps = n_pumps
        
        # 水位控制器（输出0-3）
        self.level_pid = PIDController(
            Kp=1.5, Ki=0.3, Kd=0.05,
            setpoint=3.5,
            output_limits=(0, n_pumps)
        )
        
        # 泵状态记录
        self.pump_status = [0] * n_pumps  # 0=停, 1=运行
        self.run_time = [0] * n_pumps     # 累计运行时间（小时）
        self.last_switch_time = [0] * n_pumps  # 上次启停时间
        
        # 保护参数
        self.min_run_time = 5 * 60    # 最小运行时间5分钟
        self.min_stop_time = 10 * 60  # 最小停机时间10分钟
        
        self.current_time = 0
    
    def update(self, water_level, dt):
        """
        控制更新
        
        Parameters:
        -----------
        water_level : float
            进水池当前水位 [m]
        dt : float
            时间步长 [s]
        
        Returns:
        --------
        pump_status : list
            各泵运行状态 [0/1, 0/1, 0/1]
        """
        self.current_time += dt
        
        # PID计算需要开几台泵
        control_signal = self.level_pid.update(water_level, dt)
        n_target = round(control_signal)
        n_target = max(0, min(self.n_pumps, n_target))
        
        # 当前运行台数
        n_current = sum(self.pump_status)
        
        # 需要启动
        if n_target > n_current:
            self._start_pumps(n_target - n_current)
        # 需要停止
        elif n_target < n_current:
            self._stop_pumps(n_current - n_target)
        
        # 更新运行时间
        for i in range(self.n_pumps):
            if self.pump_status[i] == 1:
                self.run_time[i] += dt / 3600  # 转换为小时
        
        return self.pump_status.copy()
    
    def _start_pumps(self, n):
        """
        启动n台泵（轮换运行策略）
        优先启动运行时间最短的泵
        """
        # 找出停机的泵
        stopped_pumps = [i for i in range(self.n_pumps) if self.pump_status[i] == 0]
        
        # 按运行时间排序（运行时间短的优先）
        stopped_pumps.sort(key=lambda i: self.run_time[i])
        
        # 启动前n台（检查最小停机时间）
        started = 0
        for i in stopped_pumps:
            if started >= n:
                break
            
            # 检查最小停机时间
            time_since_stop = self.current_time - self.last_switch_time[i]
            if time_since_stop >= self.min_stop_time:
                self.pump_status[i] = 1
                self.last_switch_time[i] = self.current_time
                started += 1
                print(f"  ✓ 启动泵#{i+1}（累计运行{self.run_time[i]:.1f}h）")
    
    def _stop_pumps(self, n):
        """
        停止n台泵
        优先停止运行时间最长的泵
        """
        # 找出运行的泵
        running_pumps = [i for i in range(self.n_pumps) if self.pump_status[i] == 1]
        
        # 按运行时间排序（运行时间长的优先停）
        running_pumps.sort(key=lambda i: self.run_time[i], reverse=True)
        
        # 停止前n台（检查最小运行时间）
        stopped = 0
        for i in running_pumps:
            if stopped >= n:
                break
            
            # 检查最小运行时间
            time_since_start = self.current_time - self.last_switch_time[i]
            if time_since_start >= self.min_run_time:
                self.pump_status[i] = 0
                self.last_switch_time[i] = self.current_time
                stopped += 1
                print(f"  ✓ 停止泵#{i+1}（累计运行{self.run_time[i]:.1f}h）")
```

---

### 第三部分：动态设计特点（本书创新）

#### 3.1 水锤防护设计

**传统设计**：
- 简单计算水锤压力
- 设置止回阀、安全阀

**动态设计**：
```python
# 实时水锤分析与控制
class WaterHammerProtection:
    """水锤保护系统"""
    
    def safe_shutdown(self, pump, valve, current_flow):
        """
        安全关闭策略（避免水锤）
        """
        # 计算安全关闭时间
        c = 1000  # 水锤波速 m/s
        L = 500   # 管道长度 m
        T_critical = 2 * L / c  # 临界时间
        
        # 缓慢关闭（3倍临界时间）
        T_close = 3 * T_critical  # 约3秒
        
        # 生成关闭曲线（线性）
        n_steps = int(T_close / 0.1)
        closure_curve = np.linspace(current_flow, 0, n_steps)
        
        return closure_curve
```

#### 3.2 能耗优化调度

**考虑峰谷电价**（如果进水池有调蓄能力）:
```python
def optimize_pump_schedule(water_level, electricity_price, storage_capacity):
    """
    能耗优化调度
    
    策略：
    - 峰电（07:00-11:00, 18:00-23:00）：少开泵或不开
    - 平电：正常开泵
    - 谷电（23:00-07:00）：多开泵，充满进水池
    
    约束：
    - 进水池水位 2.5-4.5m
    - 满足灌溉需求
    """
    hour = get_current_hour()
    
    if electricity_price == 'peak' and water_level > 3.0:
        # 峰电且水位够，少开或不开
        return 0  # 停机
    elif electricity_price == 'valley':
        # 谷电，尽量多开泵蓄水
        if water_level < 4.0:
            return 3  # 开3台
        else:
            return 2
    else:
        # 平电，正常控制
        return normal_control(water_level)
```

#### 3.3 预测性维护

```python
# 设备健康监测
class PredictiveMaintenance:
    """预测性维护"""
    
    def monitor_pump_health(self, pump_id):
        """
        泵健康状态监测
        
        监测指标：
        - 振动趋势（渐变故障预警）
        - 温度异常（轴承磨损）
        - 电流波动（叶轮磨损）
        - 效率下降（需检修）
        """
        vibration = get_sensor_data(f'pump_{pump_id}_vibration')
        temperature = get_sensor_data(f'pump_{pump_id}_temperature')
        current = get_sensor_data(f'pump_{pump_id}_current')
        
        # 异常检测
        if vibration > THRESHOLD_VIBRATION:
            trigger_alarm('振动过大，建议检修')
        
        if temperature > THRESHOLD_TEMP:
            trigger_alarm('温度过高，立即停机')
        
        # 效率计算
        eta_current = compute_efficiency(current, flow, head)
        eta_rated = 0.78
        
        if eta_current < 0.9 * eta_rated:
            trigger_warning('效率下降>10%，建议检修')
```

---

### 第四部分：在环测试（本书核心）

#### 4.1 测试工况设计

**测试矩阵**（100种工况）:

| 工况类型 | 数量 | 描述 |
|---------|------|------|
| **正常工况** | 30 | |
| - 恒定流量 | 10 | Q = 1.2, 2.4, 3.6 m³/s |
| - 流量渐变 | 10 | 线性增减 |
| - 流量波动 | 10 | 正弦波动 |
| **扰动工况** | 30 | |
| - 上游来水变化 | 10 | 丰水期/枯水期 |
| - 下游需求波动 | 10 | 高峰期/低谷期 |
| - 管道阻力变化 | 10 | 淤积、磨损 |
| **故障工况** | 20 | |
| - 单泵故障 | 10 | 各种时刻 |
| - 传感器失效 | 5 | 水位计故障 |
| - 通信中断 | 5 | 降级运行 |
| **极端工况** | 20 | |
| - 停电恢复 | 5 | 自启动测试 |
| - 紧急停机 | 5 | 快速关闭 |
| - 超负荷运行 | 10 | 3台全开 |

#### 4.2 性能评估指标

**水力性能**:
- 扬程满足率：>95%
- 流量稳定性：波动<±5%
- 水池不溢出/不干涸：100%保证

**控制性能**:
- 水位控制精度：±10cm
- 响应时间：<10分钟
- 超调量：<20%

**能耗性能**:
- 平均效率：>75%
- 年能耗：<50万kWh
- 单位水量能耗：<0.14 kWh/m³

**可靠性**:
- 故障处理成功率：>95%
- 设备利用率：>90%
- 均衡运行：各泵运行时间差<10%

#### 4.3 在环测试脚本

```python
# run_hil_test.py
def run_all_scenarios():
    """运行全部100种测试工况"""
    
    # 创建泵站数字孪生
    twin = create_pump_station_twin()
    
    # 生成测试工况
    scenarios = generate_test_scenarios(n=100)
    
    # 批量运行
    results = []
    for i, scenario in enumerate(scenarios):
        print(f"[{i+1}/100] 运行工况：{scenario['name']}")
        result = twin.simulate(scenario)
        results.append(result)
    
    # 性能评估
    performance = evaluate_performance(results)
    
    # 智能化等级评估
    from books.intelligent_water_network_design.code.tools.intelligence_grader import IntelligenceGrader
    
    grader = IntelligenceGrader()
    grade = grader.evaluate(
        n_sensors=14,
        n_controllers=3,
        steady_state_errors=[0.08, 0.06, 0.09],  # 3个泵的控制误差
        setpoints=[3.5, 3.5, 3.5],
        rise_times=[8, 7, 9],  # 响应时间（分钟）
        target_level='L3'
    )
    
    # 生成报告
    generate_report(performance, grade)
```

---

## 📊 设计成果

### 设计文件清单

1. **设计说明书.pdf**（40页）
   - 第1章：工程概况与设计依据
   - 第2章：泵站水力设计（符合GB 50265）
   - 第3章：智能控制系统设计
   - 第4章：动态设计创新点
   - 第5章：在环测试报告
   - 第6章：投资概算与经济分析
   - 附录A：泵特性曲线
   - 附录B：控制逻辑图
   - 附录C：设备清单

2. **代码包**
   - main.py - 主仿真程序
   - models/ - 泵、水池模型
   - controllers/ - 控制器
   - simulator/ - 数字孪生
   - tests/ - 测试脚本
   - config.json - 配置文件

3. **在环测试报告.pdf**（20页）
   - 100种工况测试结果
   - 性能指标统计
   - 智能化等级L3认证

4. **投资概算表.xlsx**
   - 土建工程：180万元
   - 机电设备：120万元（泵、电机、变频器等）
   - 智能化系统：50万元（+17%）
   - 总投资：350万元

---

## 💡 关键设计参数表

| 参数类别 | 参数名 | 数值 | 单位 | 依据 |
|---------|--------|------|------|------|
| **水力参数** | | | | GB 50265 |
| 设计流量（2开） | Q | 2.4 | m³/s | §4.2.3 |
| 设计扬程 | H | 15.0 | m | §5.2.1 |
| 净扬程 | H_static | 15.0 | m | 实测 |
| 管道损失 | h_f + h_m | 2.5 | m | 计算 |
| **泵参数** | | | | 厂家资料 |
| 额定流量 | Q_rated | 1.2 | m³/s | ZLB-1200 |
| 额定扬程 | H_rated | 15.0 | m | |
| 额定效率 | eta_rated | 78 | % | |
| 额定功率 | P_rated | 80 | kW | |
| **水池参数** | | | | GB 50265 §6.2 |
| 进水池面积 | A_inlet | 225 | m² | |
| 进水池深度 | D_inlet | 5.0 | m | |
| 有效水深 | 3.0-4.5 | m | |
| 出水池容积 | V_outlet | 500 | m³ | |
| **控制参数** | | | | 仿真整定 |
| PID比例系数 | Kp | 1.5 | - | |
| PID积分系数 | Ki | 0.3 | - | |
| PID微分系数 | Kd | 0.05 | - | |
| 目标水位 | setpoint | 3.5 | m | |
| **保护参数** | | | | 经验值 |
| 最小运行时间 | T_min_run | 5 | 分钟 | 保护电机 |
| 最小停机时间 | T_min_stop | 10 | 分钟 | 避免频繁启停 |

---

## 🎯 与案例1的对比

| 对比项 | 案例1（闸站） | 案例2（泵站） | 复杂度提升 |
|-------|-------------|-------------|----------|
| **物理对象** | 闸门（被动） | 水泵（主动） | ⬆️ |
| **控制目标** | 下游水位 | 进水池水位 | → |
| **控制难度** | 简单（连续调节） | 中等（离散启停） | ⬆️ |
| **能耗** | 无（重力） | 高（250kW） | ⬆️⬆️ |
| **保护要求** | 启闭限位 | 水锤、气蚀、最小启停时间 | ⬆️⬆️ |
| **中国标准** | SL 13 | GB 50265（更复杂） | ⬆️ |
| **代码量** | 500行 | 1200行（预计） | ⬆️⬆️ |

---

## 💻 运行方式

```bash
cd /workspace/books/intelligent-water-network-design/code/examples/case_02_pump_station

# 运行主程序
python main.py

# 运行在环测试
python run_hil_test.py

# 生成设计文档
python generate_design_doc.py
```

---

## 🔗 与其他案例的关系

**前序案例**:
- 案例1：学习了PID控制和数字孪生基础

**后续案例**:
- 案例8：多级泵站串联（复用案例2×4）
- 案例14：供水管网（复用案例2作为加压泵站）
- 案例19：跨流域调水（复用案例2×30）

**复用价值**:
- 案例2的泵模型和控制器将被大量复用
- 这是Level 1最重要的案例之一

---

## ⏭️ 下一个案例

**案例4：调压阀站智能控制设计（L2）**
- 学习压力控制（而非水位控制）
- 引入管网水力学
- 为案例14（供水管网）做准备

---

**案例2开发状态**: 🔄 开发中  
**预计完成时间**: 3周后  
**最后更新**: 2025-10-31
