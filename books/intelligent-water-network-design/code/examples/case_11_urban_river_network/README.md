# 案例11：城市河湖水系联调设计

**难度等级**：⭐⭐⭐⭐⭐ 高级（Level 2）  
**学习时间**：28学时（10学时建模 + 12学时控制 + 6学时测试）  
**智能化等级**：L3-L4（协调控制到优化调度）  
**工程类型**：城市河湖水系联合调度

---

## 📖 工程背景

### 项目概况

某市城市河湖水系联调工程：
- **水体数**：5个（3条河道+2个湖泊）
- **闸站数**：8座（连接各水体）
- **水面积**：10 km²
- **功能**：防洪+景观+生态+调蓄
- **控制目标**：水位、水质、景观协调

### Level 2特点：从单闸→水系

| 对比项 | Level 1（案例5/6） | Level 2（案例11） | 升级 |
|-------|-------------------|------------------|------|
| **水体数** | 1个 | 5个（3河+2湖） | ×5 |
| **闸站数** | 1-3 | 8个 | ×8 |
| **功能** | 单一 | 防洪+景观+生态 | ⬆️⬆️⬆️ |
| **拓扑** | 简单 | 复杂网络 | ⬆️⬆️ |
| **智能化** | L3 | L3-L4 | ⬆️ |

### 现状问题

传统管理（人工调度）：
- ❌ **水位不协调**：雨季湖泊溢出，河道干涸
- ❌ **水质恶化**：缺乏流动，富营养化
- ❌ **景观差**：水位波动大，影响景观
- ❌ **调度滞后**：人工决策，延迟半天

### 改造目标

- ✅ 水位协调（各水体水位在景观范围）
- ✅ 水质改善（保证流动，换水周期<7天）
- ✅ 防洪安全（暴雨期快速泄洪）
- ✅ 生态保障（最小生态流量）
- ✅ 智能化等级L3-L4

---

## 📐 设计依据（中国标准）

### 主要标准

1. **GB 50513-2009** 《城市水系规划规范》⭐⭐⭐
   - §5 水系调蓄

2. **CJJ 124-2008** 《城市河道绿化设计规范》
   - 景观水位要求

3. **GB 3838-2002** 《地表水环境质量标准》
   - 水质要求

---

## 🔧 复用案例5+6

### 高度复用（80%）

```python
# ✅ 复用案例5（排涝闸站）
from case_05_drainage_gate import (
    DrainageSchedulingController,
    RainfallForecast
)

# ✅ 复用案例6（多功能水闸）
from case_06_multi_function_gate import (
    MultiFunctionGateController
)

# 扩展：5个水体+8个闸站（网络拓扑）
```

**复用率**：80%（案例5 40% + 案例6 40%）

### 本案例创新

```python
# 1. 水系网络拓扑（新增）⭐⭐⭐
class RiverNetworkTopology:
    """
    河湖水系网络拓扑
    
    功能：定义5个水体+8个闸站的连接关系
    """
    pass

# 2. 水质模型（新增）⭐⭐
class WaterQualityModel:
    """
    水质模型（简化）
    
    功能：计算换水周期，评估水质
    """
    pass

# 3. 景观水位约束（新增）⭐⭐
class LandscapeConstraint:
    """
    景观水位约束
    
    功能：确保各水体水位在景观范围
    """
    pass
```

---

## 📋 设计任务

### 第一部分：水系网络建模

#### 1.1 系统拓扑

```
        河道1（5km）
           │
    ┌──────┼──────┐
    │      │      │
  湖泊1   河道2   湖泊2
  (2km²) (3km)   (1.5km²)
    │      │      │
    └──┬───┴───┬──┘
       │       │
     河道3（4km）
       │
     外江（泄洪）

闸站分布：
- 闸1-3：河道1 → 湖泊1/河道2/湖泊2
- 闸4-5：湖泊1/湖泊2 → 河道3
- 闸6：河道2 → 河道3
- 闸7：河道3 → 外江（泄洪闸）
- 闸8：外江 → 河道1（进水闸）
```

#### 1.2 水体参数

| 水体 | 类型 | 面积/长度 | 景观水位 | 防洪水位 |
|------|------|----------|---------|---------|
| 河道1 | 河 | 5 km | 3.0 m | 4.0 m |
| 湖泊1 | 湖 | 2 km² | 3.5 m | 4.5 m |
| 河道2 | 河 | 3 km | 2.8 m | 3.8 m |
| 湖泊2 | 湖 | 1.5 km² | 3.2 m | 4.2 m |
| 河道3 | 河 | 4 km | 2.5 m | 3.5 m |

---

### 第二部分：水系联调控制设计（L3-L4核心）

#### 2.1 多目标协调

```python
class RiverNetworkCoordinator:
    """
    河湖水系联调控制器（L3-L4）
    
    功能：
    1. 防洪优先（暴雨期）
    2. 景观水位保障（平时）
    3. 水质改善（流动循环）
    4. 生态流量保障
    
    优先级：
    - 汛期：防洪 > 生态 > 景观 > 水质
    - 平时：景观 > 水质 > 生态 > （无防洪）
    
    创新：水系网络协调，多目标优化
    """
    
    def __init__(self):
        # 8个闸站PID控制器（简化）
        self.gate_controllers = [
            SimplePIDController(Kp=0.8, Ki=0.15, Kd=0.08,
                               setpoint=3.0, output_limits=(0, 2.0))
            for _ in range(8)
        ]
        
        # 降雨预报
        self.rainfall_forecast = RainfallForecast()
        
        # 当前模式
        self.current_mode = 'normal'  # normal/flood/landscape/ecology
        
        # 统计
        self.mode_counts = {
            'flood': 0,
            'landscape': 0,
            'ecology': 0,
            'circulation': 0,
            'normal': 0
        }
    
    def identify_mode(self, water_levels: list, rainfall: float) -> str:
        """工况识别"""
        # 防洪模式（暴雨或水位超警）
        if rainfall > 30 or max(water_levels) > 4.0:
            return 'flood'
        
        # 水质改善模式（流动循环）
        elif min(water_levels) < 2.5:
            return 'ecology'  # 补水
        
        # 景观模式
        else:
            return 'landscape'
    
    def update(self, water_levels: list, rainfall: float, dt: float) -> list:
        """
        水系联调控制
        
        Parameters:
        -----------
        water_levels : list
            5个水体水位 [m]
        rainfall : float
            降雨强度 [mm/h]
        dt : float
            时间步长 [s]
        
        Returns:
        --------
        gate_openings : list
            8个闸门开度 [m]
        """
        # 1. 识别模式
        mode = self.identify_mode(water_levels, rainfall)
        self.current_mode = mode
        self.mode_counts[mode] += 1
        
        # 2. 根据模式设定闸门开度
        if mode == 'flood':
            # 防洪模式：全力泄洪
            # 闸7（泄洪闸）全开，其他闸引导水流向河道3
            openings = [1.5, 0.5, 0.5, 1.5, 1.5, 1.5, 2.0, 0.2]
            
        elif mode == 'ecology':
            # 生态补水模式：闸8开启补水
            openings = [0.5, 0.5, 0.5, 0.3, 0.3, 0.3, 0.2, 1.0]
            
        else:  # landscape
            # 景观模式：维持各水体景观水位
            # 简化：各闸小开度，保持微流动
            openings = [0.5] * 8
        
        return openings
```

---

### 第三部分：动态设计特点（本书创新）

#### 3.1 与前序案例对比

| 对比项 | 案例5 | 案例6 | 案例10 | 案例11 |
|-------|------|------|--------|--------|
| **拓扑** | 单闸 | 单闸 | 树形 | 网络 ⭐ |
| **水体** | 1 | 1 | 6 | 5 |
| **功能** | 排涝 | 4功能 | 灌溉 | 4功能 |
| **控制** | 预报-调度 | 多目标 | 轮灌 | 多目标+网络 |
| **复用** | - | - | 85%案例1+7 | 80%案例5+6 |

---

## 💻 运行方式

```bash
cd code/examples/case_11_urban_river_network
python main.py
```

---

**案例11开发状态**: 🔄 开发中  
**预计完成时间**: 2小时  
**最后更新**: 2025-10-31
