# 案例6：多功能水闸设计

**难度等级**：⭐⭐⭐⭐ 高级  
**学习时间**：18学时（5学时水力设计 + 8学时多目标控制 + 5学时在环测试）  
**智能化等级**：L3（多目标冲突协调）  
**工程类型**：综合性水利枢纽

---

## 📖 工程背景

### 项目概况

某市城郊综合水利枢纽：
- **功能1**：灌溉供水（春夏季，3000亩农田）
- **功能2**：排涝防洪（汛期，保护5000亩低洼地）
- **功能3**：航运通航（III级航道，100吨级船舶）
- **功能4**：生态补水（常年保证下游生态流量）
- **闸门**：3孔×4m×3m（宽×高），电动弧形闸门
- **设计流量**：
  - 灌溉：5 m³/s
  - 排涝：15 m³/s
  - 通航：保证水位稳定±0.1m
  - 生态：最小0.8 m³/s

### 多功能冲突

| 功能 | 季节 | 水位要求 | 流量 | 冲突点 |
|------|------|---------|------|--------|
| 灌溉 | 春夏 | 上游高水位（4.0m） | 5 m³/s | ⚔️ 排涝需要低水位 |
| 排涝 | 汛期 | 上游低水位（2.5m） | 15 m³/s | ⚔️ 灌溉需要高水位 |
| 通航 | 全年 | 水位稳定（±0.1m） | - | ⚔️ 灌排需要调节 |
| 生态 | 全年 | 下游最小流量0.8 m³/s | 0.8+ m³/s | ⚔️ 枯季水量紧张 |

### 改造目标

- ✅ 多目标优先级管理（汛期排涝>生态>灌溉>通航）
- ✅ 冲突协调机制（灌溉期vs汛期）
- ✅ 通航期水位稳定控制（±0.1m）
- ✅ 生态流量保障（100%满足）
- ✅ 智能化等级达到L3

---

## 📐 设计依据（中国标准）

### 主要标准

1. **SL 13-2015** 《水闸设计规范》⭐⭐⭐
   - 综合利用水闸设计

2. **GB 50139-2014** 《内河通航标准》⭐⭐
   - §3.2 III级航道技术标准
   - §5.3 船闸最小尺度

3. **GB 50201-2014** 《防洪标准》
   - 防护等级

4. **SL 723-2016** 《排涝泵站工程技术规范》
   - 排涝计算

5. **NB/T 10506-2021** 《小水电站生态流量监测导则》
   - 生态流量保障

---

## 🔧 复用前序教材成果

### 整合案例1和案例5

```python
# ✅ 复用案例1（灌溉功能）
from case_01_irrigation_gate import (
    TrapezoidalChannel,
    gate_irrigation_control
)

# ✅ 复用案例5（排涝功能）
from case_05_drainage_gate import (
    DrainageSchedulingController,
    RainfallForecast
)

# ✅ 复用案例3（优先级管理思想）
# 多目标协调控制方法
```

**复用率**：约60%（整合两个案例）

---

## 📋 设计任务

### 第一部分：多功能设计

#### 1.1 功能需求分析

**时间分配**（全年8760小时）：
```python
# 灌溉期（4-9月，180天）
irrigation_hours = 180 * 24 = 4320 h  # 49%

# 汛期排涝（6-8月，90天）
drainage_hours = 90 * 24 = 2160 h  # 25%
# 其中与灌溉重叠：60天 × 24 = 1440 h

# 通航期（除冰冻期，300天）
navigation_hours = 300 * 24 = 7200 h  # 82%

# 生态补水（全年）
ecology_hours = 365 * 24 = 8760 h  # 100%
```

**优先级排序**：
```
1. 防洪安全（最高）
2. 生态流量（法定要求）
3. 灌溉供水（生产需求）
4. 航运通航（经济需求）
```

#### 1.2 冲突协调策略

**汛期（6-8月）**：
```
排涝 > 生态 > 灌溉 > 通航

决策：
- 暴雨期：全力排涝，暂停通航
- 平水期：保证生态，适当灌溉
- 水位恢复后：恢复通航
```

**灌溉期（4-5月，9月）**：
```
生态 > 灌溉 > 通航 > （无排涝需求）

决策：
- 保证下游生态流量>0.8 m³/s
- 满足灌溉需水
- 维持通航水位稳定
```

**枯水期（11-3月）**：
```
生态 > 通航

决策：
- 最小开度保证生态流量
- 尽量维持通航水位
```

---

### 第二部分：多目标控制系统设计（L3核心）

#### 2.1 控制架构

```
┌─────────────────────────────────────────┐
│  综合调度决策层                         │
│  - 季节识别                             │
│  - 优先级管理                           │
│  - 冲突协调                             │
│  - 长期调度计划                         │
└───────────────┬─────────────────────────┘
                │
┌───────────────┴─────────────────────────┐
│  功能控制层                             │
│  - 灌溉控制器（案例1）                  │
│  - 排涝控制器（案例5）                  │
│  - 通航控制器（新增）                   │
│  - 生态流量控制器（新增）               │
└───────────────┬─────────────────────────┘
                │
┌───────────────┴─────────────────────────┐
│  执行层                                 │
│  - 闸门启闭机                           │
│  - 传感器                               │
└─────────────────────────────────────────┘
```

#### 2.2 多目标控制器设计

```python
class MultiFunctionGateController:
    """
    多功能水闸控制器（L3智能化等级）
    
    功能：
    1. 季节/工况识别
    2. 优先级动态调整
    3. 多目标冲突协调
    4. 平滑切换
    
    创新：多目标优先级管理 + 冲突协调
    """
    
    def __init__(self):
        # 各功能控制器
        self.irrigation_controller = IrrigationController()  # 案例1
        self.drainage_controller = DrainageController()      # 案例5
        self.navigation_controller = NavigationController()  # 新增
        self.ecology_controller = EcologyController()        # 新增
        
        # 当前工况
        self.current_mode = 'normal'  # normal/irrigation/drainage/navigation
        
        # 优先级权重（动态调整）
        self.weights = {
            'drainage': 1.0,    # 排涝（汛期最高）
            'ecology': 0.9,     # 生态（法定要求）
            'irrigation': 0.7,  # 灌溉
            'navigation': 0.5   # 通航
        }
    
    def identify_mode(self, month, h_upstream, rainfall):
        """
        工况识别
        
        Parameters:
        -----------
        month : int
            当前月份（1-12）
        h_upstream : float
            上游水位 [m]
        rainfall : float
            降雨强度 [mm/h]
        
        Returns:
        --------
        mode : str
            当前工况
        """
        # 汛期（6-8月）且有降雨
        if 6 <= month <= 8 and rainfall > 10:
            return 'drainage'  # 排涝模式
        
        # 汛期但无降雨
        elif 6 <= month <= 8:
            return 'normal'
        
        # 灌溉期（4-5月，9月）
        elif month in [4, 5, 9]:
            return 'irrigation'  # 灌溉模式
        
        # 通航期（水位稳定要求高）
        elif h_upstream > 3.5:
            return 'navigation'  # 通航模式
        
        else:
            return 'normal'
    
    def update(self, month, h_upstream, h_downstream, rainfall, flow_eco, dt):
        """
        多目标协调控制
        
        Parameters:
        -----------
        month : int
            月份
        h_upstream : float
            上游水位 [m]
        h_downstream : float
            下游水位 [m]
        rainfall : float
            降雨强度 [mm/h]
        flow_eco : float
            下游当前流量 [m³/s]
        dt : float
            时间步长 [s]
        
        Returns:
        --------
        gate_opening : float
            闸门开度 [m]
        """
        # 1. 识别当前工况
        mode = self.identify_mode(month, h_upstream, rainfall)
        self.current_mode = mode
        
        # 2. 根据工况选择控制策略
        if mode == 'drainage':
            # 排涝模式：优先排水
            opening_drainage = self.drainage_controller.update(h_upstream, h_downstream, dt)
            opening = opening_drainage
            
        elif mode == 'irrigation':
            # 灌溉模式：保证灌溉 + 生态
            opening_irrigation = self.irrigation_controller.update(h_downstream, dt)
            
            # 检查生态流量
            if flow_eco < 0.8:
                # 生态流量不足，强制加大开度
                opening = max(opening_irrigation, 0.5)
            else:
                opening = opening_irrigation
        
        elif mode == 'navigation':
            # 通航模式：水位稳定
            opening_navigation = self.navigation_controller.update(h_upstream, dt)
            opening = opening_navigation
        
        else:
            # 正常模式：只保证生态流量
            if flow_eco < 0.8:
                opening = 0.5  # 最小开度保证生态
            else:
                opening = 0.3  # 减小开度
        
        # 3. 生态流量底线保护（全局约束）
        if flow_eco < 0.5:  # 严重不足
            opening = max(opening, 1.0)  # 强制加大
        
        return opening, mode
```

#### 2.3 通航控制器（新增）

```python
class NavigationController:
    """
    通航水位控制器
    
    要求：上游水位稳定在3.5±0.1m（船闸运行要求）
    """
    
    def __init__(self):
        self.target_level = 3.5
        
        # 高精度PID（水位波动要求严格）
        self.pid = SimplePIDController(
            Kp=1.0, Ki=0.2, Kd=0.15,  # 大Kd抑制波动
            setpoint=self.target_level,
            output_limits=(0.2, 1.5)  # 小开度范围，避免大调节
        )
    
    def update(self, h_upstream, dt):
        """通航水位控制"""
        opening = self.pid.update(h_upstream, dt)
        return opening
```

#### 2.4 生态流量控制器（新增）

```python
class EcologyController:
    """
    生态流量保障控制器
    
    要求：下游流量≥0.8 m³/s（常年）
    """
    
    def __init__(self):
        self.min_eco_flow = 0.8  # m³/s
    
    def compute_required_opening(self, current_flow, target_flow=0.8):
        """
        计算保证生态流量所需的开度
        """
        if current_flow < target_flow:
            # 流量不足，需要加大开度
            opening_adjustment = 0.2 * (target_flow - current_flow)
            return opening_adjustment
        else:
            return 0
```

---

### 第三部分：动态设计特点（本书创新）

#### 3.1 多目标冲突决策树

```
降雨>50mm/h？ ─YES→ 排涝模式（全开）
   │
   NO
   │
生态流量<0.5？ ─YES→ 强制加大开度
   │
   NO
   │
是否通航期？ ─YES→ 通航模式（水位稳定）
   │
   NO
   │
是否灌溉期？ ─YES→ 灌溉模式（下游水位控制）
   │
   NO
   │
正常模式（最小开度保证生态）
```

#### 3.2 功能切换平滑过渡

传统设计：功能切换突变，引起水位波动

**动态设计**：平滑过渡
```python
def smooth_transition(opening_current, opening_target, max_rate=0.1):
    """
    平滑过渡（防止功能切换时水位突变）
    
    Parameters:
    -----------
    opening_current : float
        当前开度 [m]
    opening_target : float
        目标开度 [m]
    max_rate : float
        最大变化率 [m/min]
    
    Returns:
    --------
    opening_new : float
        新开度 [m]
    """
    delta = opening_target - opening_current
    
    if abs(delta) < max_rate:
        return opening_target
    else:
        return opening_current + np.sign(delta) * max_rate
```

---

### 第四部分：在环测试（本书核心）

#### 4.1 测试场景设计

**全年运行模拟**（365天）：

| 阶段 | 时间 | 主要功能 | 测试重点 |
|------|------|---------|---------|
| 春灌期 | 3-5月 | 灌溉+生态 | 水量分配 |
| 汛期 | 6-8月 | 排涝+生态 | 冲突协调 |
| 秋灌期 | 9-10月 | 灌溉+通航 | 水位稳定 |
| 枯水期 | 11-2月 | 生态+通航 | 最小流量保障 |

**典型工况**（20种）：
- 春灌高峰期（5月）
- 汛期暴雨（7月）
- 汛期通航冲突（7月）
- 秋季枯水+灌溉冲突（9月）
- 冬季枯水+生态冲突（12月）
- ...

---

## 💡 关键设计参数

| 参数类别 | 参数名 | 数值 | 单位 |
|---------|--------|------|------|
| **闸门参数** | | | |
| 孔数 | n | 3 | 孔 |
| 单孔宽度 | b | 4.0 | m |
| 单孔高度 | h | 3.0 | m |
| **水位参数** | | | |
| 灌溉目标水位（上游） | Z | 4.0 | m |
| 排涝目标水位（上游） | Z | 2.5 | m |
| 通航水位（上游） | Z | 3.5±0.1 | m |
| **流量参数** | | | |
| 灌溉流量 | Q | 5 | m³/s |
| 排涝流量 | Q | 15 | m³/s |
| 生态流量（最小） | Q | 0.8 | m³/s |

---

## 🎯 与前序案例的对比

| 对比项 | 案例1 | 案例5 | **案例6** |
|-------|------|------|-----------|
| **功能数** | 1（灌溉） | 1（排涝） | **4（灌排航生态）** |
| **目标数** | 1 | 1 | **4（多目标）** |
| **冲突协调** | 无 | 无 | **✅ 核心功能** |
| **优先级管理** | 无 | 简单 | **✅ 动态调整** |
| **时间尺度** | 单一 | 多尺度 | **多尺度** |
| **智能化等级** | L3 | L3 | **L3（多目标协调）** |
| **复杂度** | ⭐⭐ | ⭐⭐⭐ | **⭐⭐⭐⭐** |
| **代码复用** | - | 70%复用案例1 | **60%复用案例1+5** |

**案例6特点**：
- ✅ Level 1最复杂案例（收官之作）
- ✅ 整合多个案例功能
- ✅ 展示多目标冲突协调方法
- ✅ 为Level 2系统级案例做准备

---

## 💻 运行方式

```bash
cd code/examples/case_06_multi_function_gate

# 全年运行模拟
python main.py

# 典型场景测试
python test_scenarios.py
```

---

## 🔗 与其他案例的关系

**前序案例（复用）**:
- 案例1：灌溉控制逻辑
- 案例5：排涝调度逻辑
- 案例3：多目标协调思想

**后续案例（扩展）**:
- 案例15：灌区渠系（复用案例6×多个）
- 案例16：城市河湖水系（复用案例6理念）

**复用价值**：
- 多目标协调方法论可推广到所有复杂案例
- 优先级管理机制通用

---

**案例6开发状态**: 🔄 开发中  
**预计完成时间**: 2天后  
**最后更新**: 2025-10-31
