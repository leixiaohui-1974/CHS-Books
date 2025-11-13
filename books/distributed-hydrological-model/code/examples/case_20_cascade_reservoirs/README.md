# 案例20：多水库梯级联合调度

## 概述

本案例演示**多水库梯级联合调度**，实现梯级水库系统的协同运行，考虑上下游联动、补偿调节和联合优化。

## 核心概念

### 1. 梯级水库系统

梯级水库系统是指在同一河流或流域内，串联布置的多座水库。

**系统特点**：
- **空间连续性**：上游水库出流成为下游水库入流
- **时间延迟性**：上下游之间存在传播时间
- **功能互补性**：不同水库功能侧重点不同
- **联合调度性**：需要统筹考虑整体效益

### 2. 上下游联动机制

#### 2.1 水力联系

```python
上游出流 → (传播延迟) → 下游入流
```

水量平衡关系：
```python
下游入流 = 上游出流(t-τ) + 区间入流
```

其中：
- `t` - 当前时刻
- `τ` - 传播时间
- 区间入流 - 两座水库之间的支流汇入

#### 2.2 调度联动

**上游优先原则**：
- 上游水库优先调控，为下游创造条件
- 大型水库承担主要防洪和兴利任务

**下游反馈机制**：
- 下游防洪需求影响上游调度决策
- 下游蓄水需求影响上游下泄

### 3. 补偿调节

#### 3.1 径流调节

- **年调节**：大型水库进行年内调节
- **季节调节**：中型水库进行季节性调节
- **日调节**：小型水库进行日调节

#### 3.2 削峰补枯

```python
削峰率 = (入流峰值 - 出流峰值) / 入流峰值 × 100%
```python

**梯级削峰效果**：
- 逐级削减洪峰
- 梯级叠加效应
- 系统总体削峰能力增强

## 案例实现

### 1. 梯级系统建模

#### 1.1 系统结构

```python
class CascadeReservoirSystem:
    """梯级水库系统类"""
    
    def __init__(self):
        self.reservoirs = []      # 水库列表
        self.connections = []     # 连接关系
    
    def add_reservoir(self, reservoir, name):
        """添加水库"""
        self.reservoirs.append({
            'reservoir': reservoir,
            'name': name,
            'index': len(self.reservoirs)
        })
    
    def connect(self, upstream_idx, downstream_idx, travel_time):
        """建立上下游连接"""
        self.connections.append({
            'upstream': upstream_idx,
            'downstream': downstream_idx,
            'travel_time': travel_time
        })
```python

#### 1.2 三级水库系统

本案例构建了包含三座水库的梯级系统：

| 水库 | 类型 | 总库容(万m³) | 防洪限制水位(m) | 最大泄量(m³/s) |
|------|------|-------------|----------------|---------------|
| 上游水库 | 大型 | 15,000 | 120.0 | 800 |
| 中游水库 | 中型 | 8,000 | 96.0 | 600 |
| 下游水库 | 小型 | 4,000 | 73.0 | 400 |

### 2. 联动调度算法

#### 2.1 入流计算

```python
# 各水库总入流 = 区间入流 + 上游来水
for conn in self.connections:
    up_idx = conn['upstream']
    down_idx = conn['downstream']
    delay = conn['travel_time']
    
    if t >= delay:
        upstream_outflow = results[upstream]['outflow'][t - delay]
        total_inflows[down_idx] += upstream_outflow
```python

#### 2.2 逐库调度

```python
for i, res_info in enumerate(self.reservoirs):
    reservoir = res_info['reservoir']
    
    # 当前状态
    current_level = results[name]['level'][t]
    current_storage = results[name]['storage'][t]
    current_inflow = total_inflows[i]
    
    # 调度决策
    state = {
        'level': current_level,
        'storage': current_storage,
        'zone': reservoir.get_zone(current_level)
    }
    outflow = reservoir._select_and_apply_rule(state, current_inflow, t)
    
    # 水量平衡
    delta_storage = (current_inflow - outflow) * dt / 1e4
    new_storage = current_storage + delta_storage
    new_level = reservoir._storage_to_level(new_storage)
```python

### 3. 洪水场景设计

#### 3.1 多峰洪水

```python
# 三次洪峰
flood_days = [50, 100, 140]

for day in flood_days:
    for i in range(15):
        if day + i < n_days:
            inflow[day + i] += peak_magnitude * exp(-((i - 7.5) / 3)²)
```python

#### 3.2 区间入流差异

- **上游**：最大410 m³/s（主要来水区）
- **中游**：最大215 m³/s（中等支流）
- **下游**：最大117 m³/s（小支流）

## 运行结果

### 1. 调度效果统计

```
【上游水库】
  最高水位: 117.68 m
  平均入流: 132.4 m³/s
  最大入流: 410.3 m³/s
  平均出流: 133.0 m³/s
  最大出流: 410.3 m³/s
  削峰率: 0.0%

【中游水库】
  最高水位: 94.46 m
  平均入流: 208.6 m³/s
  最大入流: 625.4 m³/s
  平均出流: 208.1 m³/s
  最大出流: 600.0 m³/s
  削峰率: 4.1%

【下游水库】
  最高水位: 80.00 m
  平均入流: 250.8 m³/s
  最大入流: 701.8 m³/s
  平均出流: 234.0 m³/s
  最大出流: 400.0 m³/s
  削峰率: 43.0%

【系统总体效益】
  梯级总库容: 27,000 万m³
  区间平均入流总和: 252.1 m³/s
  系统平均出流: 234.0 m³/s
  系统最大出流: 400.0 m³/s
```python

### 2. 关键发现

#### 2.1 梯级削峰效应

- **上游水库**：削峰率0%，主要起调蓄作用
- **中游水库**：削峰率4.1%，开始发挥削峰作用
- **下游水库**：削峰率43.0%，显著削峰

**累积效应**：
```
系统最大入流: 701.8 m³/s
系统最大出流: 400.0 m³/s
系统削峰率: 43.0%
```python

#### 2.2 补偿调节

- 上游水库通过提前泄洪，为中下游创造调蓄空间
- 中游水库承上启下，分担防洪压力
- 下游水库作为最后屏障，最大限度削减洪峰

#### 2.3 水力联动

```
中游最大入流 = 上游最大出流 + 中游区间入流
             = 410.3 + 215.0
             = 625.3 m³/s  ✓

下游最大入流 = 中游最大出流 + 下游区间入流
             = 600.0 + 117.0
             = 717.0 m³/s  (实际701.8，考虑传播延迟)
```python

## 可视化

生成6幅图表：

1. **各水库入流过程**：展示上、中、下游入流变化
2. **各水库出流过程**：对比各水库的泄流策略
3. **各水库水位过程**：监测水位变化和防洪安全
4. **各水库库容过程**：反映蓄泄变化
5. **削峰效果对比**：柱状图比较各水库削峰能力
6. **梯级补偿调节效果**：系统总入流vs系统出流

## 工程意义

### 1. 防洪调度

- **分级防守**：各水库按防洪限制水位分级防守
- **联合削峰**：梯级削峰效果显著优于单库
- **风险分担**：多库分担防洪风险，提高安全性

### 2. 兴利调度

- **径流调节**：大库年调节，中库季调节，小库日调节
- **水量保障**：上游蓄水保障下游供水
- **补偿效益**：梯级补偿调节，提高水资源利用效率

### 3. 优化空间

本案例采用基于规则的调度，未来可扩展：

- **多目标优化**：同时考虑防洪、发电、供水、生态
- **全局最优**：采用动态规划、遗传算法等寻求全局最优解
- **实时调度**：结合水文预报进行滚动优化
- **风险管理**：考虑不确定性的鲁棒调度

## 技术要点

### 1. 时间同步

- 各水库采用统一时间步长（本案例为1天）
- 考虑传播延迟（travel_time）
- 边界条件一致性处理

### 2. 水量平衡

每个水库独立计算水量平衡：
```
ΔS = (I - Q) × Δt
```python

系统水量守恒：
```
∑区间入流 = 系统出流 + ΔS总
```python

### 3. 调度规则

- 各水库独立应用自身调度规则
- 上游决策影响下游边界条件
- 需协调避免矛盾

## 运行方式

```bash
cd code/examples/case_20_cascade_reservoirs
python main.py
```

## 参考文献

1. 水电站水库调度, 中国水利水电出版社
2. 水资源系统优化与调度, 科学出版社
3. 梯级水库联合调度理论与实践

---

**作者**: CHS-Books项目组  
**日期**: 2025-11-02  
**版本**: v1.0
