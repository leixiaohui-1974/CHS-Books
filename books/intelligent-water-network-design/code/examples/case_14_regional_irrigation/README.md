# 案例14：区域灌区群联调设计

**难度等级**：⭐⭐⭐⭐⭐⭐ 高级（Level 3）  
**学习时间**：32学时（12学时建模 + 14学时控制 + 6学时测试）  
**智能化等级**：L3-L4（协调控制到优化调度）  
**工程类型**：区域灌区群联合调度

---

## 📖 工程背景

### 项目概况

某区域灌区群联调工程：
- **灌区数**：5个（总60万亩）
- **水库数**：3座（总库容5000万m³）
- **泵站数**：8座
- **渠系**：干渠5条+支渠20条
- **作物**：水稻+小麦+玉米+果树
- **调度范围**：跨3个县

### Level 3特点：从单灌区→灌区群

| 对比项 | Level 2（案例10） | Level 3（案例14） | 升级 |
|-------|-----------------|------------------|------|
| **灌区数** | 1个（2万亩） | 5个（60万亩） | ×30 |
| **水库** | 0 | 3座（5000万m³） | ⬆️⬆️⬆️ |
| **泵站** | 0 | 8座 | ⬆️⬆️ |
| **优化** | 配水公平 | 水源-灌区优化配置 | ⬆️⬆️⬆️ |
| **智能化** | L3 | L3-L4 | ⬆️ |

### 现状问题

传统调度（各灌区独立）：
- ❌ **水资源浪费**：上游多用，下游不够
- ❌ **水库调度无序**：各自为政，总体不优
- ❌ **灌溉效率低**：无统一轮灌，重复灌溉
- ❌ **应急差**：旱情响应慢

### 改造目标

- ✅ 区域灌区群联合调度（5灌区+3水库）
- ✅ 水库群优化调度（最大化灌溉保证率）
- ✅ 灌区间配水公平（变异系数<0.15）
- ✅ 节水15%（区域轮灌优化）
- ✅ 智能化等级L3-L4

---

## 📐 设计依据（中国标准）

### 主要标准

1. **GB 50288-2018** 《灌溉与排水工程设计标准》⭐⭐⭐
2. **SL 13-2015** 《灌区规划规范》⭐⭐

---

## 🔧 复用案例10+13

### 高度复用（75%）

```python
# ✅ 复用案例10（单灌区轮灌）
from case_10_irrigation_system import (
    RotationScheduler,
    IrrigationSystemCoordinator
)

# ✅ 复用案例13（多水源优化）
from case_13_multi_source_water_supply import MultiSourceOptimizer

# 扩展：5灌区+3水库群优化
```

**复用率**：75%（案例10 40% + 案例13 35%）

### 本案例创新

```python
# 1. 水库群优化调度器（新增）⭐⭐⭐
class ReservoirGroupOptimizer:
    """
    水库群优化调度器（本案例核心创新）
    
    功能：
    - 3个水库联合调度
    - 最大化灌溉保证率
    - 考虑来水不确定性
    
    优化目标：
    max 灌溉保证率
    """
    pass

# 2. 区域轮灌协调器（新增）⭐⭐
class RegionalRotationCoordinator:
    """
    区域轮灌协调器
    
    功能：
    - 5个灌区轮灌协调
    - 配水公平性保障
    """
    pass
```

---

## 📋 设计任务

### 第一部分：区域灌区群系统建模

#### 1.1 系统拓扑

```
水库层（3座）
├─ 水库1：上游（2000万m³）
├─ 水库2：中游（1800万m³）
└─ 水库3：下游（1200万m³）
    │
    ▼ 输水+泵站
灌区层（5个）
├─ 灌区1：15万亩，水稻（需水多）
├─ 灌区2：12万亩，水稻+小麦
├─ 灌区3：10万亩，小麦
├─ 灌区4：13万亩，玉米
└─ 灌区5：10万亩，果树
    │
总计：60万亩
```

#### 1.2 灌区参数

| 灌区 | 面积 [万亩] | 作物 | 灌溉定额 [m³/亩] | 优先级 |
|------|------------|------|----------------|--------|
| 灌区1 | 15 | 水稻 | 600 | 高 |
| 灌区2 | 12 | 水稻+小麦 | 500 | 高 |
| 灌区3 | 10 | 小麦 | 400 | 中 |
| 灌区4 | 13 | 玉米 | 350 | 中 |
| 灌区5 | 10 | 果树 | 300 | 低 |

---

### 第二部分：区域灌区群优化调度控制设计（L3-L4核心）

#### 2.1 水库群+灌区群联合调度

```python
class RegionalIrrigationCoordinator:
    """
    区域灌区群协调控制器（L3-L4）
    
    功能：
    1. 水库群优化调度（3水库）⭐⭐⭐
    2. 区域轮灌协调（5灌区）⭐⭐
    3. 配水公平性保障
    4. 旱情应急调度
    
    优化目标：
    - 最大化灌溉保证率
    - 配水公平（CV<0.15）
    - 节水15%
    
    创新：水库群+灌区群双层优化
    """
    
    def __init__(self):
        # 水库群优化器
        self.reservoir_optimizer = ReservoirGroupOptimizer()
        
        # 区域轮灌协调器
        self.rotation_coordinator = RegionalRotationCoordinator()
        
        # 5个灌区控制器
        self.irrigation_controllers = [
            IrrigationSystemCoordinator() for _ in range(5)
        ]
    
    def update(self, reservoir_levels: list, irrigation_demands: list, t: float, dt: float):
        """
        区域灌区群联合调度
        
        Parameters:
        -----------
        reservoir_levels : list
            3个水库水位 [m]
        irrigation_demands : list
            5个灌区需水 [m³/s]
        t : float
            当前时间 [s]
        dt : float
            时间步长 [s]
        
        Returns:
        --------
        allocations : list
            5个灌区分配水量 [m³/s]
        """
        # 1. 水库群优化（决定总供水能力）
        total_available = self.reservoir_optimizer.optimize(
            reservoir_levels, irrigation_demands
        )
        
        # 2. 区域轮灌协调（分配给各灌区）
        allocations = self.rotation_coordinator.allocate(
            total_available, irrigation_demands, t
        )
        
        return allocations
```

---

## 💡 关键设计参数

| 参数 | 水库1 | 水库2 | 水库3 | 单位 |
|------|------|------|------|------|
| **库容** | 2000 | 1800 | 1200 | 万m³ |
| **死水位** | 5 | 5 | 5 | m |

---

## 💻 运行方式

```bash
cd code/examples/case_14_regional_irrigation
python main.py
```

---

**案例14开发状态**: 🔄 开发中  
**预计完成时间**: 2小时  
**最后更新**: 2025-10-31
