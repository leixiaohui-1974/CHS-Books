# 案例4：调压阀站智能控制设计

**难度等级**：⭐⭐ 中级  
**学习时间**：10学时（3学时水力设计 + 4学时控制设计 + 3学时在环测试）  
**智能化等级**：L2（压力PID控制）  
**工程类型**：城市供水管网调压阀站

---

## 📖 工程背景

### 项目概况

某市高区供水调压阀站：
- **功能**：将主管高压水（0.6MPa）调压至高区用户所需压力（0.3MPa）
- **服务人口**：5000户（约1.5万人）
- **设计流量**：80 L/s（峰时）
- **管径**：DN300（进水）→ DN250（出水）
- **调压方式**：电动调节阀 + 压力PID控制
- **工作制度**：24小时连续运行
- **控制目标**：出口压力稳定在0.30 ± 0.02 MPa

### 现状问题

- ❌ **手动调节**：需人工开关阀门，调节滞后
- ❌ **压力波动大**：用水高峰期压力不足，低峰期超压
- ❌ **水锤频发**：快速关阀引起管道振动
- ❌ **能量浪费**：超压导致管网漏损增加15%
- ❌ **用户投诉多**：高层水压不稳，影响生活

### 改造目标

- ✅ 自动调压，出口压力稳定在±0.02 MPa
- ✅ 响应快速，30秒内调整到位
- ✅ 避免水锤，缓慢启闭（5-10秒）
- ✅ 能耗优化，减少管网漏损10%以上
- ✅ 智能化等级达到L2

---

## 📐 设计依据（中国标准）

### 主要标准

1. **CJJ 92-2016** 《城镇供水厂运行、维护及安全技术规程》⭐⭐⭐
   - §5.3.2 管网压力控制
   - §6.2.1 调压设施设计

2. **GB 50015-2019** 《建筑给水排水设计标准》
   - §3.3.5 供水压力要求
   - §3.3.6 减压设施

3. **GB/T 50331-2014** 《城市居民生活用水量标准》
   - 用水量预测
   - 高峰系数

4. **CJ/T 219-2017** 《电动调节阀》
   - 阀门技术规范

### 参考标准
- GB 50013-2018 《室外给水设计标准》
- CJJ 207-2013 《城镇供水管网运行、维护及安全技术规程》

---

## 🔧 复用前序教材成果

### 从第2本书复用（明渠水力学）

```python
# 复用第2本书案例21-22：管道流动计算
from books.open_channel_hydraulics.code.solvers.steady.pipe_flow import (
    compute_pipe_flow_resistance,   # 管道阻力计算
    compute_pressure_drop           # 压力损失计算
)

# 复用水锤分析模块
from books.open_channel_hydraulics.code.solvers.unsteady.water_hammer import (
    WaterHammerAnalyzer,
    compute_surge_pressure
)

# 使用示例
pressure_drop = compute_pressure_drop(
    L=500,      # 管长500m
    D=0.3,      # 管径DN300
    Q=0.08,     # 流量80 L/s
    roughness=0.0002  # 钢管粗糙度
)
```python

### 从第1本书复用（水系统控制）

```python
# 复用第1本书案例4：PID控制器
from books.water_system_control.code.control.pid import PIDController

# 出口压力控制器
pressure_controller = PIDController(
    Kp=50.0,          # 比例系数（压力控制需要较大Kp）
    Ki=10.0,          # 积分系数
    Kd=2.0,           # 微分系数
    setpoint=0.30,    # 目标压力0.30 MPa
    output_limits=(0, 100),  # 阀门开度0-100%
    windup_limit=20.0
)
```python

### 从案例2复用（泵站）

```python
# 复用数字孪生仿真思想
# 复用在环测试框架
# 复用性能评估方法
```python

---

## 📋 设计任务

### 第一部分：水力设计

#### 1.1 用水量计算（GB/T 50331-2014）

```python
# 服务人口5000户，按3人/户
population = 5000 * 3  # 15000人

# 人均综合用水定额（中等城市）
unit_consumption = 180  # L/(人·d)

# 日平均用水量
Q_avg_day = population * unit_consumption / (24 * 3600)  # L/s
# = 31.25 L/s

# 时变化系数（CJJ 92-2016表3.3.5）
K_h = 2.5  # 高峰系数

# 设计流量（高峰时）
Q_design = Q_avg_day * K_h  # = 78 L/s ≈ 80 L/s
```python

#### 1.2 压力设计

```python
# 上游主管压力（由水厂或加压泵站提供）
P_upstream = 0.60  # MPa

# 下游所需压力（GB 50015-2019 §3.3.5）
# 高层住宅（6层）：
# - 1层高3m，6层高18m
# - 水头 = 18m × 0.001 MPa/m = 0.018 MPa
# - 末端水龙头最小压力 = 0.05 MPa
# - 管道损失 = 0.03 MPa
# - 安全裕量 = 0.02 MPa
P_required = 0.018 + 0.05 + 0.03 + 0.02  # = 0.118 MPa

# 考虑同时用水系数，取0.30 MPa
P_downstream = 0.30  # MPa

# 需要减压
delta_P = P_upstream - P_downstream  # = 0.30 MPa
```python

#### 1.3 阀门选型

**调压阀类型**：电动调节阀
- **型号**：ZDL-300型电动套筒调节阀
- **公称通径**：DN300
- **公称压力**：PN16（1.6 MPa）
- **调节范围**：0-100%开度
- **流量系数**：Kv = 400（全开时）
- **响应时间**：30秒（0-100%）
- **控制信号**：4-20mA

**阀门流量特性**（等百分比）:
```python
# Q = Kv * sqrt(delta_P / rho)
# 其中开度-流量系数关系：
# Kv(x) = Kv_max * R^((x-100)/100)
# R为可调比，取50

R = 50  # 可调比
Kv_max = 400

def valve_Kv(opening_percent):
    """
    阀门流量系数
    
    Parameters:
    -----------
    opening_percent : float
        阀门开度 [%]，范围0-100
    
    Returns:
    --------
    Kv : float
        流量系数
    """
    return Kv_max * R**((opening_percent - 100) / 100)
```python

---

### 第二部分：智能控制系统设计

#### 2.1 系统架构

```
┌─────────────────────────────────────────┐
│  SCADA系统（云端/供水公司调度中心）      │
│  - 实时监控阀站                         │
│  - 历史数据分析                         │
│  - 远程设定压力                         │
│  - 报警管理                             │
└───────────────┬─────────────────────────┘
                │ 4G/光纤
┌───────────────┴─────────────────────────┐
│  阀站PLC控制柜（边缘计算）               │
│  - 压力PID控制                          │
│  - 阀门开度计算                         │
│  - 水锤保护逻辑                         │
│  - 数据采集                             │
└───────────────┬─────────────────────────┘
                │ 4-20mA / RS485
┌───────────────┴─────────────────────────┐
│  传感器与执行器                         │
│  - 进口压力表（2个冗余）                │
│  - 出口压力表（2个冗余）                │
│  - 流量计                               │
│  - 电动调节阀（带阀位反馈）             │
│  - 温度传感器                           │
│  - 泄漏检测                             │
└─────────────────────────────────────────┘
```matlab

#### 2.2 传感器配置

| 测点 | 类型 | 规格 | 数量 | 精度 |
|------|------|------|------|------|
| 进口压力 | 压力变送器 | 0-1.0MPa | 2 | ±0.2% |
| 出口压力 | 压力变送器 | 0-0.6MPa | 2 | ±0.2% |
| 流量 | 电磁流量计 | DN300 | 1 | ±0.5% |
| 阀位 | 阀位反馈 | 4-20mA | 1 | ±1% |
| 温度 | 温度传感器 | 0-50°C | 1 | ±0.5°C |

**总计**：7个传感器

#### 2.3 控制器设计

**压力PID控制（L2）**:

```python
class ValveStationController:
    """
    调压阀站控制器（L2智能化等级）
    
    功能：
    1. 出口压力PID控制
    2. 阀门开度限速（防水锤）
    3. 压力越限保护
    4. 流量自适应（增益调度）
    """
    
    def __init__(self, target_pressure=0.30):
        self.target_pressure = target_pressure
        
        # 压力PID控制器
        self.pid = PIDController(
            Kp=50.0,      # 比例系数（需整定）
            Ki=10.0,      # 积分系数
            Kd=2.0,       # 微分系数
            setpoint=target_pressure,
            output_limits=(0, 100),  # 阀门开度0-100%
            windup_limit=20.0
        )
        
        # 阀门参数
        self.valve_opening = 50.0  # 当前开度 [%]
        self.max_opening_rate = 2.0  # 最大变化率 [%/s]（防水锤）
        
        # 保护参数
        self.P_max = 0.50  # 出口最大压力 [MPa]
        self.P_min = 0.20  # 出口最小压力 [MPa]
    
    def update(self, outlet_pressure, dt):
        """
        控制器更新
        
        Parameters:
        -----------
        outlet_pressure : float
            出口实测压力 [MPa]
        dt : float
            时间步长 [s]
        
        Returns:
        --------
        valve_opening : float
            阀门开度指令 [%]
        """
        # PID计算
        valve_opening_target = self.pid.update(outlet_pressure, dt)
        
        # 限制阀门变化率（防水锤）
        max_change = self.max_opening_rate * dt
        opening_change = valve_opening_target - self.valve_opening
        opening_change = np.clip(opening_change, -max_change, max_change)
        
        self.valve_opening += opening_change
        self.valve_opening = np.clip(self.valve_opening, 0, 100)
        
        # 压力越限保护
        if outlet_pressure > self.P_max:
            # 紧急开大阀门
            self.valve_opening = min(100, self.valve_opening + 10)
            print(f"  ⚠️ 出口压力过高({outlet_pressure:.3f}MPa)，紧急开阀")
        elif outlet_pressure < self.P_min:
            # 紧急关小阀门
            self.valve_opening = max(0, self.valve_opening - 10)
            print(f"  ⚠️ 出口压力过低({outlet_pressure:.3f}MPa)，紧急关阀")
        
        return self.valve_opening
```python

#### 2.4 阀门水力模型

```python
class ElectricValve:
    """
    电动调节阀模型
    
    功能：
    - 根据开度和压差计算流量
    - 等百分比流量特性
    - 阀位反馈模拟
    """
    
    def __init__(self, Kv_max=400, R=50):
        self.Kv_max = Kv_max  # 最大流量系数
        self.R = R            # 可调比
        self.rho = 1000       # 水密度 [kg/m³]
    
    def compute_Kv(self, opening):
        """
        计算流量系数
        
        Parameters:
        -----------
        opening : float
            阀门开度 [%]
        
        Returns:
        --------
        Kv : float
            流量系数
        """
        if opening < 1:
            return self.Kv_max / self.R  # 最小Kv
        else:
            return self.Kv_max * self.R**((opening - 100) / 100)
    
    def compute_flow(self, opening, P_upstream, P_downstream):
        """
        计算通过阀门的流量
        
        Parameters:
        -----------
        opening : float
            阀门开度 [%]
        P_upstream : float
            上游压力 [MPa]
        P_downstream : float
            下游压力 [MPa]
        
        Returns:
        --------
        Q : float
            流量 [m³/s]
        """
        delta_P = (P_upstream - P_downstream) * 1e6  # 转换为Pa
        if delta_P <= 0:
            return 0
        
        Kv = self.compute_Kv(opening)
        
        # Kv定义：Q[m³/h] = Kv * sqrt(delta_P[bar])
        Q_m3h = Kv * np.sqrt(delta_P / 1e5)
        Q_m3s = Q_m3h / 3600  # 转换为m³/s
        
        return Q_m3s
```python

---

### 第三部分：动态设计特点（本书创新）

#### 3.1 流量自适应控制

传统设计：固定PID参数

动态设计：根据流量调整PID参数（增益调度）

```python
def adaptive_gain_scheduling(Q_current, Q_design):
    """
    增益调度
    
    流量大时，需要更aggressive的控制
    流量小时，需要更gentle的控制
    """
    Q_ratio = Q_current / Q_design
    
    if Q_ratio > 0.8:
        # 高流量：增大增益
        Kp = 60.0
        Ki = 12.0
        Kd = 3.0
    elif Q_ratio < 0.3:
        # 低流量：减小增益
        Kp = 30.0
        Ki = 5.0
        Kd = 1.0
    else:
        # 中流量：标准增益
        Kp = 50.0
        Ki = 10.0
        Kd = 2.0
    
    return Kp, Ki, Kd
```python

#### 3.2 水锤预防

```python
class WaterHammerPrevention:
    """水锤预防系统"""
    
    def safe_valve_closure(self, current_opening, target_opening, Q_current):
        """
        安全阀门关闭策略
        
        关闭时间 T > 2L/c （临界时间）
        """
        # 管道参数
        L = 500  # 管长 [m]
        c = 1000  # 水锤波速 [m/s]
        T_critical = 2 * L / c  # 临界时间 = 1秒
        
        # 关闭时间取3倍临界时间
        T_close = 3 * T_critical  # 3秒
        
        # 计算关闭速率
        closing_rate = (current_opening - target_opening) / T_close
        
        # 限制最大速率
        max_rate = 2.0  # %/s
        closing_rate = min(closing_rate, max_rate)
        
        return closing_rate
```python

#### 3.3 管网漏损优化

```python
def leakage_estimation(P_avg, P_design=0.30):
    """
    管网漏损估算
    
    漏损与压力的关系：
    Q_leak ∝ P^α （α≈1.15-1.18）
    """
    alpha = 1.15
    leakage_ratio = (P_avg / P_design) ** alpha
    
    # 如果压力降低10%，漏损减少约11.5%
    return leakage_ratio
```matlab

---

### 第四部分：在环测试（本书核心）

#### 4.1 测试工况设计

**测试矩阵**（30种工况）:

| 工况类型 | 数量 | 描述 |
|---------|------|------|
| **正常工况** | 10 | |
| - 恒定流量 | 3 | 低、中、高流量 |
| - 流量渐变 | 3 | 早、晚高峰模拟 |
| - 流量阶跃 | 4 | 突然用水/停水 |
| **扰动工况** | 10 | |
| - 上游压力波动 | 5 | ±10% 波动 |
| - 需求波动 | 5 | 周期性变化 |
| **故障工况** | 5 | |
| - 压力传感器故障 | 2 | 降级运行 |
| - 阀门卡顿 | 2 | 响应滞后 |
| - 通信中断 | 1 | 本地控制 |
| **极端工况** | 5 | |
| - 停电恢复 | 1 | 快速启动 |
| - 火灾用水 | 2 | 瞬时大流量 |
| - 夜间零流量 | 2 | 长时间低流量 |

#### 4.2 性能评估指标

**控制性能**:
- 压力控制精度：±0.02 MPa
- 响应时间：<30秒
- 超调量：<10%
- 稳态误差：<1%

**水锤保护**:
- 最大水锤压力：<1.5倍工作压力
- 阀门关闭时间：>3秒（临界时间的3倍）

**能耗与漏损**:
- 平均出口压力：0.30 ± 0.01 MPa
- 估算漏损减少：>10%

**可靠性**:
- 故障处理成功率：>90%
- 传感器冗余切换：<5秒

---

## 📊 设计成果

### 设计文件清单

1. **设计说明书.pdf**（30页）
   - 第1章：工程概况与设计依据
   - 第2章：用水量计算与压力设计
   - 第3章：阀门选型与水力计算
   - 第4章：智能控制系统设计
   - 第5章：水锤分析与防护
   - 第6章：在环测试报告
   - 附录A：阀门流量特性曲线
   - 附录B：PID参数整定

2. **代码包**
   - main.py - 主仿真程序
   - models/ - 阀门模型
   - controllers/ - 压力控制器
   - simulator/ - 数字孪生
   - tests/ - 测试脚本

3. **在环测试报告.pdf**（15页）
   - 30种工况测试结果
   - 性能指标统计
   - 智能化等级L2认证

4. **投资概算表.xlsx**
   - 阀门及配件：15万元
   - 控制系统：12万元
   - 传感器：8万元
   - 安装调试：10万元
   - 总投资：45万元

---

## 💡 关键设计参数表

| 参数类别 | 参数名 | 数值 | 单位 | 依据 |
|---------|--------|------|------|------|
| **水力参数** | | | | CJJ 92-2016 |
| 设计流量（高峰） | Q | 80 | L/s | 计算 |
| 上游压力 | P_up | 0.60 | MPa | 实测 |
| 下游压力 | P_down | 0.30 | MPa | GB 50015 |
| 压差 | ΔP | 0.30 | MPa | 计算 |
| **阀门参数** | | | | CJ/T 219 |
| 型号 | - | ZDL-300 | - | 选型 |
| 公称通径 | DN | 300 | mm | |
| 公称压力 | PN | 16 | bar | |
| 流量系数（全开） | Kv_max | 400 | - | 厂家 |
| 可调比 | R | 50 | - | |
| 响应时间 | T | 30 | s | |
| **控制参数** | | | | 仿真整定 |
| PID比例系数 | Kp | 50.0 | - | |
| PID积分系数 | Ki | 10.0 | - | |
| PID微分系数 | Kd | 2.0 | - | |
| 目标压力 | setpoint | 0.30 | MPa | |
| **保护参数** | | | | 经验值 |
| 最大开度变化率 | rate_max | 2.0 | %/s | 防水锤 |
| 出口压力上限 | P_max | 0.50 | MPa | 保护 |
| 出口压力下限 | P_min | 0.20 | MPa | 保护 |

---

## 🎯 与前序案例的对比

| 对比项 | 案例1（闸站） | 案例2（泵站） | 案例4（阀站） |
|-------|-------------|-------------|-------------|
| **控制对象** | 闸门开度 | 泵启停 | 阀门开度 |
| **控制目标** | 下游水位 | 进水池水位 | 出口压力 |
| **控制难度** | 简单 | 中等 | 中等 |
| **响应速度** | 慢（分钟级） | 中等（分钟级） | 快（秒级）⬆️ |
| **保护要求** | 启闭限位 | 水锤、最小启停时间 | 水锤、限速 |
| **中国标准** | SL 13 | GB 50265 | CJJ 92、GB 50015 |
| **代码量** | 500行 | 1200行 | 900行（预计） |

---

## 💻 运行方式

```bash
cd /workspace/books/intelligent-water-network-design/code/examples/case_04_valve_station

# 运行主程序
python main.py

# 运行在环测试
python run_hil_test.py
```

---

## 🔗 与其他案例的关系

**前序案例**:
- 案例1：学习了PID控制基础
- 案例2：学习了保护逻辑和在环测试

**后续案例**:
- 案例14：供水管网（复用案例4作为调压站）
- 案例16：智慧水务（复用案例4×10个阀站协同）

**复用价值**:
- 压力控制算法可复用到所有供水案例
- 阀门模型可复用到各种阀门控制

---

## ⏭️ 下一个案例

**案例3：小型水电站智能发电设计（L3）**
- 学习水轮机调速
- 引入频率控制
- 多目标优化（功率+频率+水位）

---

**案例4开发状态**: 🔄 开发中  
**预计完成时间**: 2周后  
**最后更新**: 2025-10-31
