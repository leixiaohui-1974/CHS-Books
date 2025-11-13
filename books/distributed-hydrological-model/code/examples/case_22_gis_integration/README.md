# 案例22：GIS集成应用

## 概述

本案例演示**分布式水文模型与GIS的集成应用**，实现空间数据处理、流域分析、参数提取和专题图制作等功能。

## 核心概念

### 1. GIS在水文模型中的作用

**空间数据管理**：
- DEM（数字高程模型）
- 土地利用/土地覆盖
- 土壤类型分布
- 河网水系

**空间分析**：
- 流域自动划分
- 子流域属性提取
- 空间插值
- 地形分析

**可视化**：
- 专题图制作
- 空间分布展示
- 结果对比

### 2. 空间数据结构

#### 2.1 栅格数据

```python
class SpatialData:
    """空间栅格数据类"""
    
    data: np.ndarray      # 栅格值矩阵
    extent: tuple         # 空间范围 (xmin, xmax, ymin, ymax)
    crs: str             # 坐标参考系统
    shape: tuple         # 数组形状 (rows, cols)
    dx, dy: float        # 栅格分辨率
```python

**特点**：
- 规则网格
- 易于数值计算
- 存储空间较大

#### 2.2 矢量数据

```python
class SubBasin:
    """子流域矢量数据类"""
    
    basin_id: int        # 流域编号
    boundary: np.ndarray # 边界坐标
    area: float         # 面积
    centroid: np.ndarray # 质心
    attributes: dict    # 属性字典
```python

**特点**：
- 精确边界
- 拓扑关系
- 属性丰富

### 3. 流域自动划分

#### 3.1 划分原理

```
DEM → 填洼 → 流向 → 流量累积 → 河网提取 → 子流域划分
```python

**关键步骤**：
1. **DEM预处理**：填平洼地
2. **流向计算**：D8算法
3. **流量累积**：上游汇流面积
4. **河网提取**：流量阈值
5. **流域划分**：分水岭算法

#### 3.2 本案例简化实现

由于完整流域划分算法复杂，本案例采用**预定义子流域边界**：

```python
def create_subbasins(n_basins=5):
    """创建子流域（简化版）"""
    # 根据空间位置定义5个子流域
    boundaries = [
        np.array([[0,0], [40,0], [40,40], [0,40]]),      # 左下
        np.array([[40,0], [80,0], [80,40], [40,40]]),    # 右下
        np.array([[0,40], [40,40], [40,80], [0,80]]),    # 左中
        np.array([[40,40], [80,40], [70,80], [40,80]]),  # 右中
        np.array([[20,80], [70,80], [50,90], [20,100]])  # 上
    ]
    
    for boundary in boundaries:
        basin = SubBasin(id, boundary)
        basins.append(basin)
```python

### 4. 空间属性提取

#### 4.1 点判断（射线法）

判断点是否在多边形内：

```python
def contains_point(self, x, y):
    """射线法判断点是否在多边形内"""
    inside = False
    for i in range(n):
        if 射线与边相交:
            inside = not inside
    return inside
```python

#### 4.2 统计量提取

```python
def extract_basin_statistics(layer_name):
    """提取子流域统计量"""
    for basin in basins:
        values = []
        for each pixel in layer:
            if basin.contains_point(pixel.x, pixel.y):
                values.append(pixel.value)
        
        basin.mean = np.mean(values)
        basin.std = np.std(values)
        basin.min = np.min(values)
        basin.max = np.max(values)
```python

### 5. 空间插值应用

#### 5.1 IDW插值

```python
Z(x,y) = Σ wᵢ·zᵢ / Σ wᵢ
wᵢ = 1 / dᵢᵖ
```python

**特点**：
- 光滑过渡
- 考虑所有站点
- 参数p控制权重衰减

#### 5.2 Thiessen多边形（最近邻）

```python
Z(x,y) = zₙₑₐᵣₑₛₜ
```python

**特点**：
- 分区均匀
- 不光滑
- 适合离散变化

## 案例实现

### 1. 核心类设计

#### 1.1 SpatialData类

```python
class SpatialData:
    def __init__(self, data, extent, crs="EPSG:4326"):
        """初始化空间数据"""
        self.data = data
        self.extent = extent
        self.crs = crs
        self.shape = data.shape
        self.dx = (extent[1] - extent[0]) / shape[1]
        self.dy = (extent[3] - extent[2]) / shape[0]
    
    def get_coordinates(self):
        """获取栅格坐标网格"""
        x = np.linspace(xmin + dx/2, xmax - dx/2, nx)
        y = np.linspace(ymin + dy/2, ymax - dy/2, ny)
        return np.meshgrid(x, y)
    
    def extract_value(self, x, y):
        """提取指定坐标的值"""
        col = int((x - xmin) / dx)
        row = int((ymax - y) / dy)
        return data[row, col]
```python

#### 1.2 SubBasin类

```python
class SubBasin:
    def __init__(self, basin_id, boundary):
        """初始化子流域"""
        self.basin_id = basin_id
        self.boundary = boundary
        self.area = self._calculate_area()
        self.centroid = self._calculate_centroid()
        self.attributes = {}
    
    def _calculate_area(self):
        """Shoelace公式计算多边形面积"""
        x = boundary[:, 0]
        y = boundary[:, 1]
        return 0.5 * abs(dot(x, roll(y,1)) - dot(y, roll(x,1)))
    
    def contains_point(self, x, y):
        """射线法判断点是否在内"""
        # ... (射线法实现)
```python

#### 1.3 WatershedGIS类

```python
class WatershedGIS:
    def __init__(self):
        """初始化GIS系统"""
        self.dem = None
        self.basins = []
        self.layers = {}
    
    def add_layer(self, name, data):
        """添加图层"""
        self.layers[name] = data
    
    def create_subbasins(self, n_basins):
        """创建子流域"""
        # ... (边界定义)
    
    def extract_basin_statistics(self, layer_name):
        """提取子流域统计"""
        # ... (遍历像素，统计)
    
    def spatial_interpolation(self, stations, values, method):
        """空间插值"""
        # ... (IDW或Thiessen)
```python

### 2. 模拟数据生成

#### 2.1 DEM

```python
# 模拟山地地形（东南低、西北高）
X, Y = np.meshgrid(x, y)
Z = 500 + 300*(X/100) + 400*(Y/100) + 
    50*sin(2πX/50)*cos(2πY/50)
```python

**特点**：
- 高程范围：500-1200m
- 地形起伏：周期性波动
- 梯度明显：符合自然规律

#### 2.2 土地利用

```python
landuse = np.ones((ny, nx))
landuse[Y > 60] = 1     # 上游林地
landuse[30 < Y <= 60, X < 50] = 2   # 中游草地
landuse[30 < Y <= 60, X >= 50] = 3  # 中游农田
landuse[Y <= 30] = 3    # 下游农田
landuse[Y <= 30, X > 60] = 4  # 下游城市
```python

**分区逻辑**：
- 上游（高程高）→ 林地
- 中游 → 草地/农田
- 下游 → 农田/城市

#### 2.3 降雨站点

```python
# 随机生成8个站点
stations = np.random.uniform([10,10], [90,90], (8,2))

# 降雨量随高程增加
rainfall = 500 + (elevation - elev_min) / (elev_max - elev_min) * 300
rainfall += np.random.normal(0, 20, 8)  # 添加随机噪声
```python

**特点**：
- 站点随机分布
- 降雨与高程正相关
- 范围：500-800mm

### 3. 工作流程

```
1. 初始化GIS系统
2. 加载DEM图层
3. 加载土地利用图层
4. 创建子流域
5. 生成雨量站数据
6. 空间插值 (IDW & Thiessen)
7. 提取子流域统计
8. 生成专题图 (9幅)
```python

## 运行结果

### 1. 数据概况

```
DEM尺寸: 100×100
高程范围: 500 - 1200 m
土地利用: 林地(1), 草地(2), 农田(3), 城市(4)
雨量站数量: 8个
降雨范围: 489 - 782 mm
```python

### 2. 子流域属性

| 流域ID | 面积(km²) | 平均高程(m) | 平均降雨(mm) |
|--------|-----------|-------------|--------------|
| 1 | 1600 | 637 | 649 |
| 2 | 1600 | 757 | 706 |
| 3 | 1600 | 800 | 574 |
| 4 | 1400 | 911 | 637 |
| 5 | 600 | 960 | 560 |

**分析**：
- 流域5位于上游，高程最高(960m)
- 流域2降雨最多(706mm)，与高程相关
- 流域面积差异反映地形复杂性

### 3. 高程-降雨关系

拟合线性关系：
```
y = 0.22x + 440
```python

**解读**：
- 正相关但不显著
- 地形和气候共同作用
- 需更多站点提高精度

## 可视化

生成9幅专题图：

1. **DEM**：数字高程模型，标注雨量站位置
2. **土地利用**：不同类型分区着色
3. **子流域划分**：边界和编号
4. **雨量站观测值**：散点大小和颜色表示降雨量
5. **IDW插值结果**：光滑连续分布
6. **Thiessen插值结果**：分区均匀分布
7. **子流域平均高程**：柱状图对比
8. **子流域平均降雨**：柱状图对比
9. **高程-降雨关系**：散点图+拟合线

## 工程意义

### 1. 模型参数化

**空间参数提取**：
- 地形参数：坡度、坡向、汇流长度
- 土地利用：不透水面积、植被覆盖
- 土壤参数：质地、饱和导水率

**子流域离散化**：
- 计算单元划分
- 参数空间分布
- 模型计算效率

### 2. 输入数据处理

**降雨空间插值**：
- 站点数据 → 面雨量
- 考虑地形影响
- 提高模拟精度

**边界条件**：
- 流域出口定位
- 上下游关系
- 侧向入流

### 3. 结果展示

**专题图制作**：
- 空间分布可视化
- 多情景对比
- 决策支持

**报告自动化**：
- 批量制图
- 标准化输出
- 版本管理

## 技术要点

### 1. 空间数据结构

**栅格 vs 矢量**：
- 栅格：适合计算，DEM、土地利用
- 矢量：适合边界，子流域、河网

**坐标系统**：
- 地理坐标系（经纬度）
- 投影坐标系（平面坐标）
- 坐标变换

### 2. 空间分析算法

**点在多边形内判断**：
- 射线法：O(n)复杂度
- 边界框预筛选
- 提高效率

**面积计算**：
- Shoelace公式
- 梯形法
- 精度保证

### 3. 插值方法选择

| 方法 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| IDW | 连续变化 | 光滑 | 计算量大 |
| Thiessen | 离散变化 | 快速 | 不光滑 |
| Kriging | 空间相关 | 最优 | 需变异函数 |

### 4. 可视化技巧

**颜色方案**：
- 高程：terrain（棕-绿-白）
- 降雨：Blues（浅-深蓝）
- 土地利用：分类色（离散）

**图层叠加**：
- 底图（DEM）
- 主题（降雨分布）
- 标注（站点、编号）

## 扩展方向

### 1. 完整流域划分

实现基于DEM的自动流域划分：
```python
def watershed_delineation(dem):
    """自动流域划分"""
    dem_filled = fill_depressions(dem)
    flow_dir = compute_flow_direction(dem_filled)
    flow_acc = compute_flow_accumulation(flow_dir)
    streams = extract_streams(flow_acc, threshold)
    basins = delineate_watersheds(flow_dir, streams)
    return basins
```python

### 2. 三维可视化

```python
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, cmap='terrain')
```python

### 3. 交互式GIS

使用Plotly或Folium实现交互式地图：
```python
import plotly.graph_objects as go

fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y)])
fig.show()
```python

### 4. 与专业GIS软件集成

```python
# 使用GDAL读取真实GIS数据
from osgeo import gdal, ogr

# 栅格
dataset = gdal.Open('dem.tif')
dem_array = dataset.ReadAsArray()

# 矢量
vector = ogr.Open('basins.shp')
layer = vector.GetLayer()
```python

## 运行方式

```bash
cd code/examples/case_22_gis_integration
python main.py
```

## 参考文献

1. Burrough, P.A., McDonnell, R.A. (1998). Principles of Geographical Information Systems
2. Jones, K.H. (1998). A comparison of algorithms used to compute hill slope as a property of the DEM
3. Tarboton, D.G. (1997). A new method for the determination of flow directions and upslope areas in grid digital elevation models
4. 汤国安等. (2005). 数字高程模型及地学分析的原理与方法. 科学出版社

---

**作者**: CHS-Books项目组  
**日期**: 2025-11-02  
**版本**: v1.0
