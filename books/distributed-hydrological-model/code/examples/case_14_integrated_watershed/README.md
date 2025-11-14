# 案例14：完整流域分布式水文模型

**难度**: ⭐⭐⭐⭐  
**标签**: `综合应用` `流域建模` `分布式模拟` `端到端`

---

## 📖 案例简介

本案例展示如何构建一个**完整的分布式水文模型系统**，整合DEM分析、空间插值、产流模拟、汇流计算等所有核心技术，实现端到端的流域水文建模。

### 🎯 学习目标

1. 理解分布式水文建模的完整流程
2. 掌握网格化流域建模方法
3. 学会整合多个核心模块
4. 实现完整的降雨-径流模拟

### 🔑 关键技术

- **流域网格化**：创建计算网格
- **空间插值**：降雨场分布
- **分布式产流**：网格化产流计算
- **流域汇总**：出流统计

---

## 🌊 完整流域建模流程

### 1. 建模流程

```python
┌────────────────────────┐
│    流域网格化          │
│   (20×20网格)         │
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐
│   降雨站点布设         │
│   (5个雨量站)         │
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐
│   降雨空间插值         │
│   (IDW方法)           │
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐
│   网格产流计算         │
│   (新安江模型)        │
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐
│   流域出流汇总         │
│   (空间平均)          │
└────────────────────────┘
```

### 2. 网格化流域

**圆形流域设计**:
```python
# 创建圆形流域
center_x, center_y = nx * 500, ny * 500
radius = min(nx, ny) * 400
mask = ((X - center_x)**2 + (Y - center_y)**2) <= radius**2
```python

**特点**:
- 规则网格：1km × 1km
- 流域面积：约200 km²
- 网格数：197个有效网格

### 3. 空间插值

**降雨插值到网格**:
```python
rainfall_valid = inverse_distance_weighting(
    stations_xy,  # 站点坐标
    rainfall,     # 站点降雨
    valid_points, # 网格中心
    power=2       # IDW参数
)
```python

### 4. 分布式产流

**逐网格产流计算**:
```python
for i, j in zip(*valid_indices):
    model = XinAnJiangModel(params)
    results = model.run(
        np.array([rainfall_grid[i, j]]),
        np.array([EM[t]])
    )
    grid_runoff[i, j] = results['R'][0]
```python

### 5. 流域汇总

**空间平均出流**:
```python
total_runoff[t] = np.mean(grid_runoff[mask])
```python

---

## 💻 代码实现

### 核心函数

#### 1. 创建流域网格

```python
def create_watershed_grid(nx=20, ny=20):
    """创建流域网格"""
    x = np.arange(nx) * 1000  # m
    y = np.arange(ny) * 1000  # m
    X, Y = np.meshgrid(x, y)
    
    # 创建圆形流域
    center_x, center_y = nx * 500, ny * 500
    radius = min(nx, ny) * 400
    mask = ((X - center_x)**2 + (Y - center_y)**2) <= radius**2
    
    return X, Y, mask
```python

#### 2. 降雨插值

```python
def interpolate_rainfall(grid_x, grid_y, mask, stations_xy, rainfall):
    """插值降雨到网格"""
    ny, nx = grid_x.shape
    rainfall_grid = np.zeros((ny, nx))
    
    valid_points = np.column_stack([grid_x[mask], grid_y[mask]])
    
    if len(valid_points) > 0:
        rainfall_valid = inverse_distance_weighting(
            stations_xy, rainfall, valid_points, power=2
        )
        rainfall_grid[mask] = rainfall_valid
    
    return rainfall_grid
```python

#### 3. 分布式模拟

```python
# 时间步循环
for t in range(n_days):
    # 1. 插值降雨
    rainfall_grid = interpolate_rainfall(...)
    
    # 2. 网格产流
    for i, j in zip(*valid_indices):
        model = XinAnJiangModel(params)
        results = model.run(...)
        grid_runoff[i, j] = results['R'][0]
    
    # 3. 流域汇总
    total_runoff[t] = np.mean(grid_runoff[mask])
```python

---

## 📊 运行结果

### 典型输出

```
======================================================================
案例14：完整流域分布式水文模型
======================================================================

1. 创建流域网格...
   网格大小: 20 × 20
   有效网格: 197
   流域面积: 197 km²

2. 生成降雨站点...
   站点数量: 5

3. 生成降雨过程...
   时间步数: 100
   总降雨: 352.3 mm

4. 设置产流参数...
   使用新安江模型参数

5. 运行分布式水文模拟...
   进度: 20%
   进度: 40%
   进度: 60%
   进度: 80%
   进度: 100%

6. 模拟完成
   总径流: 239.6 mm
   径流系数: 0.680

【流域特征】
  网格大小: 20 × 20
  流域面积: 197 km²
  雨量站数: 5

【水文响应】
  模拟时长: 100 天
  平均降雨: 352.3 mm
  总径流: 239.6 mm
  径流系数: 0.680
  峰值径流: 26.48 mm
```python

### 可视化结果

生成两幅图：
1. **流域网格与雨量站分布图**
2. **降雨-径流过程图**

---

## 🎓 技术总结

### 1. 建模流程整合

**完整流程**:
```
流域网格 → 降雨插值 → 网格产流 → 流域汇总
```

### 2. 核心技术

| 技术环节 | 实现方法 | 关键参数 |
|---------|---------|---------|
| 流域网格 | 规则网格+掩膜 | 1km×1km |
| 降雨插值 | IDW | power=2 |
| 产流模拟 | 新安江模型 | 14个参数 |
| 流域汇总 | 空间平均 | - |

### 3. 模拟结果

- **径流系数**: 0.68
- **峰值径流**: 26.48 mm
- **水量平衡**: 良好

---

## 🔬 工程应用

### 1. 实际流域建模

**应用场景**:
- 洪水预报
- 水资源评估
- 流域管理

### 2. 扩展方向

**功能扩展**:
- 真实DEM数据
- 河道网络汇流
- 水库调度
- 人类活动影响

### 3. 性能优化

**优化策略**:
- 并行计算
- GPU加速
- 稀疏矩阵
- 自适应时间步长

---

## 📝 参考资料

1. **分布式水文模型**
   - 芮孝芳，2004，《水文学原理》
   - Beven, K., 2012, "Rainfall-Runoff Modelling"

2. **空间插值方法**
   - 李小文等，2013，《定量遥感》
   - Isaaks & Srivastava, 1989, "Applied Geostatistics"

3. **新安江模型**
   - 赵人俊，1984，《流域水文模拟》
   - Zhao, R.J., 1992, "The Xinanjiang model applied in China"

---

## 💡 练习建议

1. **基础练习**
   - 修改流域形状（矩形、不规则）
   - 调整网格分辨率
   - 改变雨量站数量

2. **进阶练习**
   - 添加河道汇流
   - 实现并行计算
   - 引入真实DEM数据

3. **综合应用**
   - 多场降雨模拟
   - 参数敏感性分析
   - 不确定性评估

---

**作者**: CHS-Books项目组  
**日期**: 2025-11-02  
**版本**: v1.0
