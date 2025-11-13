# 案例23：分布式水文-水动力全耦合

## 概述

本案例演示**完整的分布式水文-水动力耦合模型**，实现网格化产汇流与一维河道水动力的双向耦合，展示完整物理过程的高精度模拟。

## 核心概念

### 1. 完全耦合模型

```python
降雨 → 网格产流 → 坡面汇流 → 河道水动力 → 出口流量
       (XAJ)     (线性水库)   (Saint-Venant)
```

**耦合方式**：
- **单向耦合**：坡面→河道（侧向入流）
- **双向耦合**：河道→坡面（回水顶托）[本案例为单向]

### 2. 网格化流域模型

```python
class GridCell:
    """网格单元"""
    elevation: float      # 高程
    area: float          # 面积
    flow_direction: int  # 流向
    is_channel: bool     # 是否河道
    runoff: float        # 产流量
    discharge: float     # 出流
```python

**关键算法**：
- D8流向：最陡下坡方向
- 流量累积：上游汇流面积
- 河网提取：流量阈值

### 3. 分布式产流

每个网格单元独立运行XAJ模型：
```python
for each grid_cell:
    model = XinAnJiangModel(params)
    runoff[i,j,:] = model.run(rainfall[i,j,:], evap[i,j,:])
```python

### 4. 坡面汇流

线性水库法：
```
dS/dt = I(t) - Q(t)
Q(t) = S(t) / K
```python

其中K为调蓄系数。

### 5. 河道水动力

Saint-Venant方程（简化Muskingum-Cunge）：
```
∂A/∂t + ∂Q/∂x = q_lateral
∂Q/∂t + ∂(Q²/A)/∂x + gA∂h/∂x = -gASf
```python

### 6. 耦合接口

```python
# 坡面→河道
lateral_inflow = aggregate_slope_runoff()

# 河道演进
for t in time_steps:
    h_new, Q_new = channel.solve_step(Q_upstream, lateral_inflow)
```python

## 案例实现

### 1. 系统结构

```python
DistributedHydroModel:  # 分布式水文模型
  - create_watershed()  # 创建流域网格
  - compute_flow_directions()  # 计算流向
  - run_runoff_generation()  # 产流计算
  - run_slope_routing()  # 坡面汇流

FullyCoupledModel:  # 耦合模型
  - setup_channel_model()  # 设置河道
  - run_coupled_simulation()  # 耦合模拟
```python

### 2. 模拟场景

**流域设置**：
- 网格：10×20（200个单元）
- 分辨率：500m
- 面积：50 km²
- 高程：80-104 m

**河道设置**：
- 长度：10 km
- 宽度：50 m
- 坡度：0.001
- Manning糙率：0.03

**降雨场景**：
- 时长：48小时
- 基准降雨：2 mm/h
- 暴雨中心：40 mm/h（10-20h，流域中上游）

### 3. 运行结果

```
【产流】
  总产流量: 2408.2 mm
  最大产流强度: 30.4 mm/h
  平均产流量: 0.25 mm/h

【河道流量】
  出口最大流量: 1.4 m³/s
  出口峰现时间: 12小时

【河道水深】
  最大水深: 0.50 m
  平均水深: 0.16 m
```python

### 4. 技术要点

**数值稳定性**：
- XAJ模型：参数有效性检查
- 坡面汇流：非负约束
- 河道水动力：Muskingum-Cunge稳定格式

**计算效率**：
- 网格循环：可矢量化优化
- 时间步长：3600s（1小时）
- 简化处理：均匀侧向入流分配

**耦合策略**：
- 单向耦合：坡面→河道
- 时间同步：统一时间步长
- 空间匹配：网格单元→河道断面

## 可视化

生成7幅图表：
1. DEM与河道位置
2. 累积降雨空间分布
3. 累积产流空间分布
4. 河道流量过程（多断面）
5. 河道水深过程
6. 河道纵剖面（峰值时刻）
7. 流量-水深关系

## 工程意义

### 1. 精细化模拟

- 空间分布特征
- 物理过程完整
- 水动力精确

### 2. 应用场景

- 洪水演进预报
- 内涝模拟
- 防洪规划
- 水资源评估

### 3. 扩展方向

- 二维漫流耦合
- 地下水耦合
- 实时同化
- 并行计算

## 运行方式

```bash
cd code/examples/case_23_full_coupling
python main.py
```

**注意**：计算量较大，需等待几分钟。

---

**作者**: CHS-Books项目组  
**日期**: 2025-11-02  
**版本**: v1.0
