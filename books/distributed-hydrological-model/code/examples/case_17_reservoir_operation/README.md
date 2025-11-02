# 案例17：水库优化调度（基于规则）

**难度**: ⭐⭐⭐⭐  
**标签**: `水库调度` `规则库` `防洪` `兴利` `多目标优化`

---

## 📖 案例简介

本案例演示**基于规则的水库优化调度方法**，实现防洪、兴利等多目标协调优化，是水资源管理的重要应用。

### 🎯 学习目标

1. 理解水库调度的基本原理
2. 掌握调度规则设计方法
3. 学会水位-库容关系建模
4. 实现多目标优化调度

### 🔑 关键技术

- **调度规则**：防洪规则、兴利规则
- **水库分区**：死库容、兴利库容、防洪库容
- **水量平衡**：入流-出流-库容变化
- **多目标优化**：防洪与兴利协调

---

## 🌊 水库调度原理

### 1. 水库分区

```
┌─────────────────┐ 校核洪水位
│  超蓄库容       │
├─────────────────┤ 设计洪水位
│  防洪库容       │
├─────────────────┤ 防洪限制水位
│  防洪高水位库容 │
├─────────────────┤ 正常蓄水位
│  兴利库容       │
├─────────────────┤ 死水位
│  死库容         │
└─────────────────┘
```

### 2. 调度规则

**防洪调度**:
```
IF 水位 > 设计洪水位 THEN
    出流 = min(入流 × 1.2, 最大泄流)
ELSE IF 水位 > 防洪限制水位 THEN
    出流 = 入流 × (0.8 + 0.4 × 比例)
ELSE
    出流 = 入流 × 0.6
```

**兴利调度**:
```
IF 水位 < 死水位 + 2m THEN
    出流 = 最小出流
ELSE IF 水位 > 正常蓄水位 THEN
    出流 = max(入流, 目标出流)
ELSE
    出流 = 目标出流
```

### 3. 水量平衡

```
ΔS = (Q_in - Q_out) × Δt
```

其中:
- S: 库容 (m³)
- Q_in: 入库流量 (m³/s)
- Q_out: 出库流量 (m³/s)
- Δt: 时间步长 (s)

---

## 💻 代码实现

### 核心类

#### 1. ReservoirRules类

```python
class ReservoirRules:
    """水库调度规则集"""
    
    def set_characteristics(self, dead_level, normal_level, 
                           flood_limit_level, ...):
        """设置水库特征参数"""
        self.characteristics = {
            'dead_level': dead_level,
            'normal_level': normal_level,
            ...
        }
    
    def operate(self, initial_level, inflow_series, dt):
        """执行水库调度"""
        for t in range(n_steps):
            # 应用调度规则
            outflow = self._select_and_apply_rule(...)
            
            # 水量平衡更新
            delta_storage = (inflow - outflow) * dt
            new_storage = storage + delta_storage
            
            # 反算水位
            new_level = self._storage_to_level(new_storage)
        
        return results
```

#### 2. 调度规则

```python
class FloodControlRule(OperationRule):
    """防洪调度规则"""
    
    def apply(self, state, inflow, time_step):
        level = state['level']
        
        if level >= self.design_flood_level:
            return min(inflow * 1.2, self.max_outflow)
        elif level > self.flood_limit_level:
            ratio = (level - self.flood_limit_level) / \
                   (self.design_flood_level - self.flood_limit_level)
            return inflow * (0.8 + 0.4 * ratio)
        else:
            return min(inflow * 0.6, self.max_outflow * 0.5)
```

---

## 📊 运行结果

### 模拟结果

```
【水位变化】
  初始水位: 108.00 m
  最高水位: 110.55 m
  最低水位: 96.96 m
  平均水位: 107.03 m

【库容变化】
  初始库容: 4111 万m³
  最大库容: 4821 万m³
  最小库容: 1045 万m³
  库容利用率: 48.0%

【出流过程】
  平均出流: 130.1 m³/s
  最大出流: 580.6 m³/s
  削峰率: (根据实际洪峰计算)

【分区统计】
  兴利库容: 67 天 (37.2%)
  限制水位: 113 天 (62.8%)
  防洪库容: 0 天 (0.0%)
```

### 关键发现

1. **水位控制**:
   - 水位主要在兴利库容和限制水位之间波动
   - 未超过防洪限制水位，防洪安全得到保障

2. **库容利用**:
   - 库容利用率48.0%，合理利用水资源
   - 保持一定调节能力应对洪水

3. **调度效果**:
   - 平稳出流，避免剧烈波动
   - 兼顾防洪与兴利需求

### 可视化结果

生成5幅子图：
1. **入库与出库流量过程**
2. **水位变化过程**
3. **库容变化过程**
4. **水库分区运行时间占比**
5. **削峰效果对比**

---

## 🎓 技术总结

### 1. 调度规则设计

| 规则类型 | 触发条件 | 调度策略 |
|---------|---------|---------|
| 防洪调度 | 水位 > 防洪限制 | 加大泄流 |
| 兴利调度 | 正常运行 | 稳定出流 |
| 应急调度 | 超设计洪水位 | 全力泄洪 |

### 2. 水库特征参数

```python
characteristics = {
    'dead_level': 95.0,          # 死水位
    'normal_level': 108.0,       # 正常蓄水位
    'flood_limit_level': 113.0,  # 防洪限制水位
    'design_flood_level': 118.0, # 设计洪水位
    'max_level': 122.0,          # 校核洪水位
    'total_storage': 8000.0,     # 总库容
    'max_outflow': 600.0         # 最大泄流
}
```

### 3. 调度目标

**多目标平衡**:
- 防洪安全：不超防洪限制水位
- 兴利效益：保持合理库容
- 生态需求：维持最小生态流量
- 供水保障：稳定出流

---

## 🔬 工程应用

### 1. 防洪调度

**应用场景**:
- 实时洪水调度
- 应急响应
- 风险控制

### 2. 兴利调度

**应用场景**:
- 灌溉供水
- 发电调度
- 生态补水

### 3. 优化扩展

**改进方向**:
- 预报调度
- 多水库联合调度
- 考虑不确定性
- 机器学习优化

---

## 📝 参考资料

1. **水库调度原理**
   - 水利部，2000，《水库调度规程》
   - Yeh, W.W., 1985, "Reservoir Management"

2. **优化方法**
   - Labadie, J.W., 2004, "Optimal Operation"
   - Wurbs, R.A., 1993, "Reservoir System Simulation"

3. **多目标优化**
   - Chang, L.C., 2008, "Multi-objective Optimization"
   - Reddy, M.J., 2007, "Multi-objective Reservoir Operation"

---

## 💡 练习建议

1. **基础练习**
   - 修改水库特征参数
   - 调整调度规则系数
   - 测试不同入流情景

2. **进阶练习**
   - 实现预报调度
   - 多水库串联
   - 考虑发电效益

3. **综合应用**
   - 真实水库数据
   - 历史洪水重现
   - 优化算法改进

---

**作者**: CHS-Books项目组  
**日期**: 2025-11-02  
**版本**: v1.0
