# 案例12：调水工程水量调度设计

**难度等级**：⭐⭐⭐⭐⭐⭐ 高级+（Level 2最复杂）  
**学习时间**：32学时（12学时建模 + 14学时控制 + 6学时测试）  
**智能化等级**：L3-L4（协调控制到优化调度）  
**工程类型**：长距离调水工程联合调度

---

## 📖 工程背景

### 项目概况

某跨流域调水工程：
- **线路长度**：300 km
- **渠段**：3段（有压+无压）
- **泵站**：3座（提水）
- **调蓄水库**：2座
- **输水能力**：50 m³/s
- **功能**：供水+调蓄+发电

### Level 2特点：复杂系统集成

| 对比项 | Level 1 | Level 2（案例12） | 升级 |
|-------|---------|-----------------|------|
| **子系统** | 单一 | 泵站+渠道+水库混合 | ⬆️⬆️⬆️ |
| **尺度** | 局部 | 300 km长距离 | ⬆️⬆️⬆️ |
| **控制** | 单体 | 多级联合调度 | ⬆️⬆️ |
| **优化** | 单目标 | 多目标（成本+时间） | ⬆️⬆️ |
| **智能化** | L3 | L3-L4 | ⬆️ |

### 现状问题

传统调度（人工）：
- ❌ **调度滞后**：人工决策，延迟1天
- ❌ **能耗高**：无优化，电费高30%
- ❌ **水量损失**：无协调，蒸发损失大
- ❌ **应急响应差**：突发需求响应慢

### 改造目标

- ✅ 自动联合调度（3泵站+2水库）
- ✅ 节能优化（降低电费20%）
- ✅ 水量精确控制（损失<5%）
- ✅ 智能化等级L3-L4

---

## 📐 设计依据（中国标准）

### 主要标准

1. **GB 50288-2018** 《灌溉与排水工程设计标准》⭐⭐⭐
2. **SL 430-2008** 《泵站设计规范》⭐⭐
3. **DL/T 5178-2003** 《水利水电工程调度设计规范》⭐⭐

---

## 🔧 复用案例2+7+8+10

### 高度复用（75%）

```python
# ✅ 复用案例2（泵站）
from case_02_pump_station import Pump, MultiPumpController

# ✅ 复用案例7（串级渠道）
from case_07_cascade_canals import CascadeController

# ✅ 复用案例8（多级泵站）
from case_08_multi_pump_stations import MultiStationCoordinator

# ✅ 复用案例10（配水）
from case_10_irrigation_system import IrrigationSystemCoordinator

# 扩展：泵站+渠道+水库混合系统
```

**复用率**：75%（案例2 25% + 案例7 20% + 案例8 20% + 案例10 10%）

### 本案例创新

```python
# 1. 泵站-渠道-水库混合系统（新增）⭐⭐⭐
class HybridSystem:
    """泵站+渠道+水库混合系统"""
    pass

# 2. 长距离延迟补偿（新增）⭐⭐⭐
class LongDistanceDelayCompensator:
    """长距离输水延迟补偿（300km）"""
    pass

# 3. 调水调度优化器（新增）⭐⭐
class DiversionOptimizer:
    """能耗优化+时间优化"""
    pass
```

---

## 📋 设计任务

### 第一部分：调水系统建模

#### 1.1 系统拓扑

```
取水口（Q=50 m³/s）
    │
    ▼
┌──────┐  渠道1   ┌──────┐
│泵站1 │─────────→│水库1 │（调蓄）
│3泵   │ 100km    │50万m³│
└──────┘          └──────┘
                      │
                      ▼ 渠道2（100km）
                  ┌──────┐
                  │泵站2 │
                  │3泵   │
                  └──────┘
                      │
                      ▼ 渠道3（100km）
                  ┌──────┐  ┌──────┐
                  │水库2 │→│用户  │
                  │30万m³│  │需求  │
                  └──────┘  └──────┘
```

#### 1.2 系统参数

| 组件 | 参数 | 值 | 单位 |
|------|------|-----|------|
| **泵站** | | | |
| 泵站1-3 | 泵数量 | 3 | 台 |
|  | 单泵流量 | 20 | m³/s |
|  | 扬程 | 50 | m |
| **水库** | | | |
| 水库1 | 容量 | 50万 | m³ |
| 水库2 | 容量 | 30万 | m³ |
| **渠道** | | | |
| 延迟 | 100km | 6 | h |

---

### 第二部分：调水联合调度控制设计（L3-L4核心）

#### 2.1 联合调度策略

```python
class WaterDiversionCoordinator:
    """
    调水工程联合调度控制器（L3-L4）
    
    功能：
    1. 需水预测（未来24h）
    2. 泵站优化调度（最小能耗）
    3. 水库调蓄优化（削峰填谷）
    4. 长距离延迟补偿（6h×3=18h）
    
    创新：长距离延迟补偿+能耗优化
    """
    
    def __init__(self):
        # 泵站控制器（3个）
        self.pump_controllers = [
            MultiPumpController(n_pumps=3) for _ in range(3)
        ]
        
        # 需水预测
        self.demand_forecast = DemandForecast()
        
        # 延迟补偿
        self.delay_compensator = LongDistanceDelayCompensator(
            delay_hours=[6, 6, 6]  # 各段延迟
        )
        
        # 能耗优化器
        self.optimizer = EnergyOptimizer()
    
    def update(self, levels: list, demand: float, t: float, dt: float):
        """
        联合调度
        
        Parameters:
        -----------
        levels : list
            [泵站1前池, 水库1, 泵站2前池, 水库2]水位 [m]
        demand : float
            用户需水 [m³/s]
        t : float
            当前时间 [s]
        dt : float
            时间步长 [s]
        
        Returns:
        --------
        pump_commands : list
            3个泵站的开泵数量
        """
        # 1. 需水预测（未来24h）
        demand_24h = self.demand_forecast.predict(t)
        
        # 2. 延迟补偿（提前18h调度）
        adjusted_demand = self.delay_compensator.compensate(
            demand_24h, t
        )
        
        # 3. 能耗优化（峰谷电价）
        optimal_schedule = self.optimizer.optimize(
            adjusted_demand, levels, t
        )
        
        # 4. 泵站控制
        pump_commands = []
        for i, ctrl in enumerate(self.pump_controllers):
            n_pumps = optimal_schedule[i]
            pump_commands.append(n_pumps)
        
        return pump_commands
```

---

### 第三部分：动态设计特点（本书创新）

#### 3.1 Level 2集大成

案例12是Level 2最复杂案例，综合了前11个案例的技术：

| 技术 | 来源 | 应用 |
|------|------|------|
| 泵站控制 | 案例2/8 | 3个泵站 |
| 串级控制 | 案例7 | 3段串联 |
| 配水优化 | 案例10 | 需水分配 |
| 调蓄优化 | 案例11 | 水库调蓄 |
| 预测调度 | 案例5 | 需水预测 |
| 多目标 | 案例6 | 能耗+时间 |

#### 3.2 延迟补偿创新

**长距离输水延迟**：
- 渠道1：100km，延迟6h
- 渠道2：100km，延迟6h
- 渠道3：100km，延迟6h
- **总延迟**：18h ⭐

**传统调度 vs 延迟补偿**：

| 对比项 | 传统 | 本案例 |
|-------|------|--------|
| **预见性** | 无 | 24h预测 |
| **延迟处理** | 忽略 | 18h补偿 |
| **响应速度** | 慢（18h） | 快（<1h） |
| **水量损失** | 10% | <5% |

---

## 💡 关键设计参数

| 参数 | 泵站1 | 泵站2 | 泵站3 | 单位 |
|------|------|------|------|------|
| **泵站参数** | | | | |
| 泵数量 | 3 | 3 | 3 | 台 |
| 单泵流量 | 20 | 20 | 20 | m³/s |
| 扬程 | 50 | 50 | 50 | m |
| **控制参数** | | | | |
| PID_Kp | 1.0 | 1.0 | 1.0 | - |

---

## 💻 运行方式

```bash
cd code/examples/case_12_water_diversion
python main.py
```

---

**案例12开发状态**: 🔄 开发中  
**预计完成时间**: 2.5小时  
**最后更新**: 2025-10-31
