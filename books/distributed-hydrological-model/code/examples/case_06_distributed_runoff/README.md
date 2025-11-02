# 案例6：分布式产流网格模型

**难度等级**: ⭐⭐⭐  
**预计学习时间**: 3-4小时  
**前置知识**: 案例2、案例3、案例4

---

## 📋 案例概述

本案例演示如何构建完整的**分布式水文模型**，将空间插值、产流计算、网格化等技术综合应用，实现真正的分布式产流模拟。

### 学习目标

- 理解分布式水文模型的基本概念
- 掌握流域网格化方法
- 学会将点雨量插值到网格
- 理解参数空间变异性
- 掌握网格化产流计算
- 学会可视化空间分布结果

### 案例特色

✨ **完整的分布式建模流程**  
✨ **网格化技术应用**  
✨ **空间变异性处理**  
✨ **精美的空间可视化**  
✨ **工程实用价值高**

---

## 🎯 核心内容

### 1. 分布式水文模型概念

#### 什么是分布式模型？

分布式水文模型将流域划分为许多小单元（网格），对每个单元独立计算水文过程，最后汇总得到流域响应。

**优势**：
- 考虑空间异质性
- 物理机制清晰
- 可输出空间分布
- 适合复杂流域

**与集总式模型对比**：

| 特征 | 集总式模型 | 分布式模型 |
|------|-----------|-----------|
| 空间尺度 | 整个流域 | 网格单元 |
| 参数 | 平均值 | 空间分布 |
| 计算量 | 小 | 大 |
| 物理意义 | 概念性 | 物理性 |
| 空间输出 | 否 | 是 |

#### 分布式建模流程

```
1. 流域网格化
   └─> 划分规则网格（本案例）或不规则网格

2. 空间数据准备
   ├─> 降雨站点数据
   ├─> DEM数据（高程）
   ├─> 土壤类型
   └─> 土地利用

3. 空间插值
   └─> 将站点数据插值到网格

4. 参数空间化
   └─> 根据下垫面特征确定参数分布

5. 网格化计算
   └─> 对每个网格独立计算

6. 结果汇总
   └─> 空间分布 + 流域总量
```

---

## 🔬 理论基础

### 1. 流域网格化

#### 规则网格（本案例采用）

**定义**：将流域划分为大小相同的正方形网格。

**网格大小选择**：
- 太大：损失空间细节
- 太小：计算量大
- 经验值：50m - 500m

**网格编号**：
```
(0,0)  (0,1)  (0,2) ... (0,nx-1)
(1,0)  (1,1)  (1,2) ... (1,nx-1)
...
(ny-1,0) ... ... ... (ny-1,nx-1)
```

#### 流域边界处理

本案例采用**掩膜（mask）**方法：
```python
basin_mask[i, j] = True   # 网格在流域内
basin_mask[i, j] = False  # 网格在流域外
```

### 2. 降雨空间插值

#### IDW插值到网格

对每个网格中心点 $(x_g, y_g)$：

$$
P_g = \frac{\sum_{i=1}^{n} w_i P_i}{\sum_{i=1}^{n} w_i}
$$

其中权重：
$$
w_i = \frac{1}{d_i^p}
$$

$d_i$ 是站点到网格中心的距离。

#### 插值方法选择

| 方法 | 优势 | 劣势 | 适用场景 |
|------|------|------|---------|
| IDW | 简单快速 | 不平滑 | 站点密集 |
| Kriging | 最优无偏 | 计算复杂 | 站点稀疏 |
| Thiessen | 极简单 | 阶梯状 | 快速估算 |

### 3. 参数空间变异

#### 参数空间化方法

**方法1：基于地形**
```python
# 蒸散发随高程减小
ET_param = base_value * (1 - 0.1 * elevation / max_elevation)
```

**方法2：基于土壤**
```python
# 不同土壤类型不同参数
if soil_type == 'clay':
    WM = 150
elif soil_type == 'loam':
    WM = 120
```

**方法3：基于土地利用**
```python
# 不同地类不同参数
if land_use == 'forest':
    IMP = 0.01  # 不透水面积比例
elif land_use == 'urban':
    IMP = 0.6
```

**方法4：随机场（本案例）**
```python
# 添加空间趋势 + 随机扰动
param = base_value * trend_factor * random_factor
```

### 4. 网格化产流计算

#### 独立网格假设

假设各网格水文过程独立：

```python
for each grid (i, j):
    if grid is in basin:
        P_grid = interpolated_rainfall[i, j]
        params_grid = parameter_field[i, j]
        R_grid = runoff_model(P_grid, params_grid)
```

#### 流域总产流

面积加权平均：

$$
R_{total} = \frac{1}{N} \sum_{i,j \in basin} R_{i,j}
$$

其中 $N$ 是流域内网格总数。

---

## 💻 代码实现

### 1. 流域网格创建

```python
def create_basin_grid(nx=20, ny=20, dx=100, dy=100):
    """
    创建规则网格
    
    参数:
    ----
    nx, ny : int
        网格数量
    dx, dy : float
        网格大小(m)
    
    返回:
    ----
    grid_x, grid_y : ndarray
        网格中心坐标
    """
    x = np.arange(0, nx * dx, dx) + dx / 2
    y = np.arange(0, ny * dy, dy) + dy / 2
    grid_x, grid_y = np.meshgrid(x, y)
    return grid_x, grid_y
```

**说明**：
- 网格中心坐标，便于插值
- meshgrid生成二维坐标数组

### 2. 圆形流域边界

```python
def create_circular_basin(grid_x, grid_y, center_x, center_y, radius):
    """创建圆形流域"""
    distance = np.sqrt((grid_x - center_x)**2 + (grid_y - center_y)**2)
    mask = distance <= radius
    return mask
```

**说明**：
- 简化实例，实际应用可用DEM提取流域边界
- mask数组标识网格是否在流域内

### 3. 降雨插值到网格

```python
def interpolate_rainfall_to_grid(grid_x, grid_y, basin_mask, 
                                  stations_xy, rainfall_t, method='idw'):
    """
    将站点降雨插值到网格
    """
    ny, nx = grid_x.shape
    grid_rainfall = np.full((ny, nx), np.nan)
    
    # 收集流域内的网格点
    valid_points = []
    for i in range(ny):
        for j in range(nx):
            if basin_mask[i, j]:
                valid_points.append([grid_x[i, j], grid_y[i, j]])
    
    valid_points = np.array(valid_points)
    
    # 插值
    if method == 'idw':
        interpolated = inverse_distance_weighting(
            stations_xy, rainfall_t, valid_points, power=2.0
        )
    
    # 填充回网格
    idx = 0
    for i in range(ny):
        for j in range(nx):
            if basin_mask[i, j]:
                grid_rainfall[i, j] = interpolated[idx]
                idx += 1
    
    return grid_rainfall
```

**关键点**：
1. 只对流域内网格插值（节省计算）
2. 流域外设为NaN
3. 支持多种插值方法

### 4. 参数空间分布

```python
def create_parameter_field(grid_x, grid_y, basin_mask, param_name='WM', 
                           base_value=120, variability=0.2):
    """
    创建参数空间场
    
    空间变异 = 趋势 + 随机扰动
    """
    ny, nx = grid_x.shape
    param_field = np.full((ny, nx), np.nan)
    
    # 添加空间趋势（从上游到下游）
    trend = (grid_y - grid_y.min()) / (grid_y.max() - grid_y.min())
    
    for i in range(ny):
        for j in range(nx):
            if basin_mask[i, j]:
                # 随机扰动 [-variability, +variability]
                random_factor = 1.0 + variability * (2 * np.random.rand() - 1)
                # 趋势因子 [0.9, 1.1]
                trend_factor = 0.9 + 0.2 * trend[i, j]
                param_field[i, j] = base_value * random_factor * trend_factor
    
    return param_field
```

**说明**：
- 组合确定性趋势和随机变异
- 实际应用应基于物理特征

### 5. 分布式产流模型

```python
def run_distributed_runoff_model(grid_x, grid_y, basin_mask, 
                                  rainfall_grid, param_fields, 
                                  model_type='xaj'):
    """
    运行分布式产流模型
    
    核心思想：为每个网格创建独立的模型实例
    """
    n_time, ny, nx = rainfall_grid.shape
    runoff_grid = np.zeros((n_time, ny, nx))
    
    # 为每个网格创建模型实例
    models = {}
    for i in range(ny):
        for j in range(nx):
            if basin_mask[i, j]:
                params = create_default_xaj_params()
                # 更新为该网格的参数
                for param_name, param_field in param_fields.items():
                    params[param_name] = param_field[i, j]
                
                models[(i, j)] = XinAnJiangModel(params)
    
    # 时间循环
    for t in range(n_time):
        for i in range(ny):
            for j in range(nx):
                if (i, j) in models:
                    P = rainfall_grid[t, i, j]
                    if P > 0:
                        results = models[(i, j)].run(np.array([P]), np.array([0.0]))
                        runoff_grid[t, i, j] = results['total_runoff'][0]
    
    # 流域总产流
    n_valid = np.sum(basin_mask)
    total_runoff = np.zeros(n_time)
    for t in range(n_time):
        total_runoff[t] = np.nanmean(runoff_grid[t, basin_mask])
    
    return runoff_grid, total_runoff
```

**关键设计**：
1. 每个网格独立的模型实例（保持状态）
2. 每个网格独立的参数
3. 时间循环 + 空间循环
4. 面积加权汇总

---

## 📊 实验演示

### 实验1：流域网格划分

**目的**：展示网格化方法和流域边界

**设置**：
- 流域：圆形，半径800m
- 网格：20×20，100m×100m
- 雨量站：5个，随机分布

**输出**：
- `basin_setup.png` - 网格和站点分布图

**关键信息**：
- 网格总数：约200个
- 流域面积：约2 km²
- 网格分辨率：100m

### 实验2：降雨空间插值

**目的**：展示IDW插值效果

**设置**：
- 站点降雨：3-9 mm/h（空间变异）
- 插值方法：IDW，幂指数2
- 时刻：峰值时刻（t=10h）

**输出**：
- `rainfall_interpolation.png` - 插值结果和统计

**观察要点**：
1. 插值场光滑连续
2. 站点附近值接近实测
3. 边界效应（边缘网格值偏低）
4. 统计分布（均值、标准差、变异系数）

### 实验3：产流空间分布

**目的**：展示产流的空间异质性

**设置**：
- 产流模型：新安江模型
- 参数：WM、B、SM空间分布
- 时刻：峰值时刻（t=10h）

**输出**：
- `runoff_spatial.png` - 产流空间分布

**观察要点**：
1. 产流与降雨的空间相关性
2. 参数影响（WM大的网格产流少）
3. 产流比例（有产流网格/总网格）
4. 产流统计（均值、最大值、标准差）

### 实验4：产流过程线

**目的**：展示流域总产流随时间的变化

**输出**：
- `runoff_time_series.png` - 降雨和产流过程

**关键指标**：
- 累计降雨：约100 mm
- 累计产流：约40-50 mm
- 产流系数：0.4-0.5
- 峰值产流：3-5 mm/h
- 峰现时间：约10-11h

---

## 📐 参数说明

### 网格参数

| 参数 | 符号 | 单位 | 本案例取值 | 说明 |
|------|------|------|-----------|------|
| 网格数（x方向） | nx | - | 20 | 可调整 |
| 网格数（y方向） | ny | - | 20 | 可调整 |
| 网格大小（x） | dx | m | 100 | 分辨率 |
| 网格大小（y） | dy | m | 100 | 分辨率 |
| 流域半径 | R | m | 800 | 简化圆形 |

### 降雨参数

| 参数 | 符号 | 单位 | 说明 |
|------|------|------|------|
| 雨量站数 | n_stations | - | 5 |
| 时间步长 | Δt | h | 1 |
| 模拟时长 | T | h | 24 |
| 总雨量 | P_total | mm | 100 |
| 雨型 | - | - | 芝加哥雨型 |

### 产流模型参数

采用新安江模型，主要参数见案例4。

**空间变异性**：
- WM：120 ± 20%
- B：0.3 ± 15%
- SM：30 ± 20%

---

## 🎨 可视化说明

### 1. 流域设置图

**元素**：
- 网格：浅蓝色方块
- 边界：蓝色实线
- 雨量站：红色三角
- 站点编号：S1-S5

### 2. 降雨插值图

**左图**：空间分布
- 颜色映射：白色→蓝色（低→高）
- 等值线：15个层次
- 站点：彩色圆点（实测值）

**右图**：统计直方图
- 蓝色柱状图：频率分布
- 红色虚线：平均值
- 橙色虚线：中位数

### 3. 产流分布图

**左图**：空间分布
- 颜色映射：白色→红色（低→高）
- 叠加网格线：灰色
- 流域外：空白

**右图**：统计直方图
- 橙色柱状图：只统计有产流网格
- 统计信息：产流网格比例等

### 4. 过程线图

**上图**：降雨过程
- 蓝色柱状：倒置显示
- 平均降雨强度

**下图**：产流过程
- 红色线：产流变化
- 红色填充：累计效果
- 星号标注：峰值位置

---

## 🔍 结果分析

### 1. 空间异质性

**降雨异质性来源**：
- 站点降雨差异（3-9 mm/h）
- 插值引入的空间变化

**产流异质性来源**：
- 降雨空间分布
- 参数空间变异
- 土壤含水量初值差异

### 2. 产流系数分析

**影响因素**：
1. 参数WM（蓄水容量）
   - WM大 → 产流少
   - WM小 → 产流多

2. 土壤初始含水量
   - 湿润 → 产流多
   - 干燥 → 产流少

3. 降雨强度
   - 强度大 → 产流系数大
   - 强度小 → 产流系数小

**典型值**：
- 湿润地区：0.5-0.7
- 半湿润地区：0.3-0.5
- 半干旱地区：0.1-0.3

### 3. 峰值分析

**峰值产流时间**：
- 通常滞后于降雨峰值1-2小时
- 受土壤蓄水影响

**峰值大小**：
- 与降雨强度正相关
- 与前期含水量正相关
- 与参数WM负相关

---

## 🚀 扩展方向

### 1. 不规则网格

```python
# 基于DEM的不规则三角网
from scipy.spatial import Delaunay
tri = Delaunay(points)
```

### 2. 汇流计算

```python
# 计算每个网格到出口的汇流
for each grid:
    flow_direction = calculate_flow_dir(DEM)
    travel_time = calculate_travel_time(distance, slope)
    routed_flow = route_runoff(runoff, travel_time)
```

### 3. 多分辨率网格

```python
# 重点区域细网格，其他区域粗网格
if is_critical_area(x, y):
    dx = 50  # 细网格
else:
    dx = 200  # 粗网格
```

### 4. 实际数据应用

- DEM数据读取（GeoTIFF）
- 土壤数据库接入
- 土地利用分类
- 实测降雨数据

---

## 🎓 学习建议

### 初学者路线

1. **理解概念**（30分钟）
   - 什么是分布式模型
   - 为什么需要网格化
   - 空间变异性的意义

2. **运行代码**（30分钟）
   ```bash
   cd case_06_distributed_runoff
   python main.py
   ```

3. **查看结果**（30分钟）
   - 分析4张图表
   - 理解空间分布特征
   - 对比降雨和产流

4. **参数实验**（1小时）
   - 改变网格大小
   - 改变雨量站数量
   - 改变参数空间变异性

### 进阶者路线

1. **阅读源码**（1小时）
   - 网格化算法
   - 插值算法调用
   - 产流模型集成

2. **修改代码**（1-2小时）
   - 添加Kriging插值
   - 尝试不同雨型
   - 修改参数空间化方法

3. **实际应用**（2-3小时）
   - 使用真实流域数据
   - 接入DEM数据
   - 进行敏感性分析

---

## 💡 常见问题

### Q1: 网格大小如何选择？

**A**: 综合考虑：
- **数据分辨率**：不能比数据精度细
- **计算资源**：网格越小计算量越大
- **流域大小**：大流域可用粗网格
- **经验值**：
  - 小流域（<10 km²）：50-100m
  - 中等流域（10-1000 km²）：100-500m
  - 大流域（>1000 km²）：500-1000m

### Q2: 为什么产流有空间差异？

**A**: 主要原因：
1. **降雨差异**：插值导致空间变化
2. **参数差异**：不同网格不同参数
3. **状态差异**：土壤含水量不同
4. **随机性**：参数空间化引入

### Q3: 如何验证模型结果？

**A**: 验证方法：
1. **水量平衡**：检查累计降雨和产流
2. **物理合理性**：产流系数在合理范围
3. **空间模式**：产流与降雨空间一致性
4. **实测对比**：如有实测流量，计算NSE等指标

### Q4: 插值方法如何选择？

**A**: 选择依据：

| 情况 | 推荐方法 | 原因 |
|------|---------|------|
| 站点密集（>1站/10km²） | IDW | 简单快速 |
| 站点稀疏 | Kriging | 考虑空间相关性 |
| 山区 | Kriging + 地形 | 考虑高程影响 |
| 实时计算 | Thiessen | 最快 |

### Q5: 模型运行慢怎么办？

**A**: 优化方法：
1. **减少网格数**：增大网格尺寸
2. **向量化计算**：避免双重循环
3. **并行计算**：使用multiprocessing
4. **C/Fortran加速**：核心计算用编译语言

---

## 📚 参考资料

### 教材

1. **《分布式水文模型》** - 芮孝芳
2. **《水文模型》** - 赵人俊
3. **"Distributed Hydrological Modelling"** - Abbott & Refsgaard

### 论文

1. Abbott, M. B., et al. (1986). "An introduction to the European Hydrological System — SHE." *Journal of Hydrology*, 87(1-2), 45-59.

2. Beven, K. J., & Kirkby, M. J. (1979). "A physically based, variable contributing area model of basin hydrology." *Hydrological Sciences Bulletin*, 24(1), 43-69.

### 软件

- **SWAT** - 经典分布式模型
- **MIKE SHE** - 全过程分布式模型
- **TOPMODEL** - 基于地形的分布式模型

---

## 📝 练习题

### 基础练习

1. 修改网格大小为50m×50m，观察结果变化
2. 增加雨量站到10个，对比插值效果
3. 修改总雨量为150mm，分析产流系数变化

### 进阶练习

1. 实现Kriging插值替代IDW
2. 添加坡度影响，上游WM参数更大
3. 输出每个网格的产流过程线

### 挑战练习

1. 读取真实DEM数据，提取流域边界
2. 集成坡面汇流模块，计算网格间汇流
3. 实现并行计算，提升大规模网格计算效率

---

## ✅ 学习检查清单

- [ ] 理解分布式模型与集总式模型的区别
- [ ] 掌握流域网格化方法
- [ ] 理解降雨空间插值原理
- [ ] 理解参数空间变异性
- [ ] 掌握网格化产流计算流程
- [ ] 能够运行并修改代码
- [ ] 能够分析空间分布结果
- [ ] 能够解释产流系数
- [ ] 能够进行参数敏感性分析
- [ ] 理解模型的应用价值和局限性

---

**案例6完成！** 🎉

下一步：案例9 - 参数敏感性分析

---

**作者**: CHS-Books项目组  
**日期**: 2025-11-02  
**版本**: v1.0
