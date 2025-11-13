# 项目6：GIS水文分析系统

**项目时长**: 1.5周  
**难度**: ⭐⭐⭐⭐⭐  
**技术栈**: NumPy, SciPy, Matplotlib, Shapely, GeoPandas

---

## 一、项目目标

开发基于DEM的水文分析系统，实现：
1. 流域自动提取
2. 水系网络生成
3. 地形特征分析
4. 汇流路径模拟
5. 可视化与GIS输出

---

## 二、核心算法实现

### 2.1 DEM处理与洼地填充

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.interpolate import griddata
import warnings
warnings.filterwarnings('ignore')

class DEMProcessor:
    """
    DEM处理与分析
    """
    
    def __init__(self, dem):
        """
        参数:
            dem: 高程数据（2D数组）
        """
        self.dem = dem.astype(float)
        self.rows, self.cols = dem.shape
    
    def fill_depressions(self, max_iter=1000):
        """
        洼地填充（Priority-Flood算法）
        
        返回:
            填充后的DEM
        """
        filled_dem = self.dem.copy()
        
        # 简化算法：逐步提升洼地
        for iteration in range(max_iter):
            changed = False
            
            for i in range(1, self.rows - 1):
                for j in range(1, self.cols - 1):
                    # 当前高程
                    h_center = filled_dem[i, j]
                    
                    # 8邻域最小高程
                    neighbors = [
                        filled_dem[i-1, j-1], filled_dem[i-1, j], filled_dem[i-1, j+1],
                        filled_dem[i, j-1],                        filled_dem[i, j+1],
                        filled_dem[i+1, j-1], filled_dem[i+1, j], filled_dem[i+1, j+1]
                    ]
                    h_min_neighbor = min(neighbors)
                    
                    # 如果低于邻域最小值，提升到最小值
                    if h_center < h_min_neighbor:
                        filled_dem[i, j] = h_min_neighbor
                        changed = True
            
            if not changed:
                break
        
        return filled_dem
    
    def flow_direction_d8(self, filled_dem):
        """
        流向分析（D8算法）
        
        编码：
        32  64  128
        16   0    1
         8   4    2
        
        返回:
            流向矩阵
        """
        flow_dir = np.zeros_like(filled_dem, dtype=int)
        
        # 方向编码
        directions = {
            (0, 1): 1,    # 东
            (1, 1): 2,    # 东南
            (1, 0): 4,    # 南
            (1, -1): 8,   # 西南
            (0, -1): 16,  # 西
            (-1, -1): 32, # 西北
            (-1, 0): 64,  # 北
            (-1, 1): 128  # 东北
        }
        
        for i in range(1, self.rows - 1):
            for j in range(1, self.cols - 1):
                h_center = filled_dem[i, j]
                
                # 找最陡下降方向
                max_slope = -np.inf
                best_dir = 0
                
                for (di, dj), code in directions.items():
                    h_neighbor = filled_dem[i + di, j + dj]
                    
                    # 距离（对角线 √2）
                    distance = np.sqrt(di**2 + dj**2)
                    
                    # 坡度
                    slope = (h_center - h_neighbor) / distance
                    
                    if slope > max_slope:
                        max_slope = slope
                        best_dir = code
                
                flow_dir[i, j] = best_dir
        
        return flow_dir
    
    def flow_accumulation(self, flow_dir):
        """
        汇流累积分析
        
        返回:
            汇流累积矩阵（每个栅格的上游栅格数）
        """
        flow_acc = np.ones_like(flow_dir, dtype=int)
        
        # 按高程从高到低处理
        elevation_order = np.argsort(-self.dem.ravel())
        
        # 方向偏移
        dir_offset = {
            1: (0, 1),
            2: (1, 1),
            4: (1, 0),
            8: (1, -1),
            16: (0, -1),
            32: (-1, -1),
            64: (-1, 0),
            128: (-1, 1)
        }
        
        for idx in elevation_order:
            i, j = np.unravel_index(idx, (self.rows, self.cols))
            
            # 获取流向
            direction = flow_dir[i, j]
            
            if direction == 0:
                continue
            
            # 下游栅格
            di, dj = dir_offset.get(direction, (0, 0))
            next_i, next_j = i + di, j + dj
            
            # 边界检查
            if 0 <= next_i < self.rows and 0 <= next_j < self.cols:
                flow_acc[next_i, next_j] += flow_acc[i, j]
        
        return flow_acc
    
    def extract_stream_network(self, flow_acc, threshold=100):
        """
        提取河网
        
        参数:
            flow_acc: 汇流累积矩阵
            threshold: 河网阈值（栅格数）
        
        返回:
            河网矩阵（0/1）
        """
        stream_network = (flow_acc >= threshold).astype(int)
        return stream_network
    
    def plot_analysis(self, filled_dem, flow_dir, flow_acc, stream_network):
        """
        可视化水文分析结果
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # 1. 填充后的DEM
        im1 = axes[0, 0].imshow(filled_dem, cmap='terrain', 
                               interpolation='bilinear')
        axes[0, 0].set_title('填充后的DEM', fontsize=14)
        axes[0, 0].axis('off')
        plt.colorbar(im1, ax=axes[0, 0], label='高程 (m)')
        
        # 2. 流向
        # 可视化：用箭头表示（简化）
        flow_dir_vis = flow_dir.copy()
        flow_dir_vis[flow_dir_vis == 0] = np.nan
        im2 = axes[0, 1].imshow(flow_dir_vis, cmap='hsv')
        axes[0, 1].set_title('流向（D8）', fontsize=14)
        axes[0, 1].axis('off')
        plt.colorbar(im2, ax=axes[0, 1], label='方向编码')
        
        # 3. 汇流累积（对数尺度）
        flow_acc_log = np.log10(flow_acc + 1)
        im3 = axes[1, 0].imshow(flow_acc_log, cmap='Blues')
        axes[1, 0].set_title('汇流累积（log10）', fontsize=14)
        axes[1, 0].axis('off')
        plt.colorbar(im3, ax=axes[1, 0], label='log10(栅格数)')
        
        # 4. 河网叠加
        axes[1, 1].imshow(filled_dem, cmap='terrain', alpha=0.7)
        stream_mask = np.ma.masked_where(stream_network == 0, stream_network)
        axes[1, 1].imshow(stream_mask, cmap='Blues', alpha=0.8)
        axes[1, 1].set_title('提取的河网', fontsize=14)
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig('gis_hydro_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()


# 使用示例
print("="*60)
print("GIS水文分析示例")
print("="*60)

# 生成模拟DEM（带洼地）
np.random.seed(42)
x = np.linspace(0, 100, 50)
y = np.linspace(0, 100, 50)
X, Y = np.meshgrid(x, y)

# 基础地形（向中心倾斜）
dem_base = 100 - 0.5 * np.sqrt((X - 50)**2 + (Y - 50)**2)

# 添加随机起伏
dem_noise = 5 * np.random.randn(50, 50)

# 添加人工洼地
dem_base[20:25, 20:25] -= 10

dem = dem_base + dem_noise

print(f"DEM尺寸: {dem.shape}")
print(f"高程范围: {dem.min():.1f} ~ {dem.max():.1f} m")

# 创建处理器
processor = DEMProcessor(dem)

# 1. 洼地填充
print("\n1. 洼地填充...")
filled_dem = processor.fill_depressions()
print(f"   填充完成，填充量: {(filled_dem - dem).sum():.1f} m³")

# 2. 流向分析
print("\n2. 流向分析（D8）...")
flow_dir = processor.flow_direction_d8(filled_dem)
print(f"   流向计算完成")

# 3. 汇流累积
print("\n3. 汇流累积分析...")
flow_acc = processor.flow_accumulation(flow_dir)
print(f"   最大汇流累积: {flow_acc.max()} 个栅格")
print(f"   出口位置: {np.unravel_index(flow_acc.argmax(), flow_acc.shape)}")

# 4. 河网提取
threshold = 50
print(f"\n4. 河网提取（阈值={threshold}）...")
stream_network = processor.extract_stream_network(flow_acc, threshold)
stream_cells = stream_network.sum()
print(f"   河网栅格数: {stream_cells}")
print(f"   河网密度: {stream_cells / dem.size * 100:.2f}%")

# 可视化
processor.plot_analysis(filled_dem, flow_dir, flow_acc, stream_network)
```

### 2.2 流域划分

```python
class WatershedDelineation:
    """
    流域划分
    """
    
    def __init__(self, flow_dir, flow_acc):
        """
        参数:
            flow_dir: 流向矩阵
            flow_acc: 汇流累积矩阵
        """
        self.flow_dir = flow_dir
        self.flow_acc = flow_acc
        self.rows, self.cols = flow_dir.shape
    
    def find_pour_points(self, threshold=100):
        """
        查找出水口（汇流累积高的点）
        
        返回:
            出水口列表 [(i, j), ...]
        """
        # 找局部最大值
        local_max = (flow_acc == ndimage.maximum_filter(flow_acc, size=5))
        
        # 高于阈值
        candidates = np.where((local_max) & (flow_acc >= threshold))
        
        pour_points = list(zip(candidates[0], candidates[1]))
        
        return pour_points
    
    def trace_upstream(self, pour_i, pour_j):
        """
        追溯上游（确定流域边界）
        
        参数:
            pour_i, pour_j: 出水口坐标
        
        返回:
            流域掩膜
        """
        watershed = np.zeros_like(self.flow_dir, dtype=bool)
        
        # 反向流向
        reverse_dir = {
            1: 16,    # 东 -> 西
            2: 32,    # 东南 -> 西北
            4: 64,    # 南 -> 北
            8: 128,   # 西南 -> 东北
            16: 1,    # 西 -> 东
            32: 2,    # 西北 -> 东南
            64: 4,    # 北 -> 南
            128: 8    # 东北 -> 西南
        }
        
        # 方向偏移
        dir_offset = {
            1: (0, 1),
            2: (1, 1),
            4: (1, 0),
            8: (1, -1),
            16: (0, -1),
            32: (-1, -1),
            64: (-1, 0),
            128: (-1, 1)
        }
        
        # BFS追溯
        from collections import deque
        queue = deque([(pour_i, pour_j)])
        watershed[pour_i, pour_j] = True
        
        while queue:
            i, j = queue.popleft()
            
            # 检查8邻域
            for direction, (di, dj) in dir_offset.items():
                ni, nj = i + di, j + dj
                
                # 边界检查
                if not (0 <= ni < self.rows and 0 <= nj < self.cols):
                    continue
                
                # 已访问
                if watershed[ni, nj]:
                    continue
                
                # 检查邻居是否流向当前点
                neighbor_dir = self.flow_dir[ni, nj]
                if neighbor_dir == reverse_dir.get(direction, 0):
                    watershed[ni, nj] = True
                    queue.append((ni, nj))
        
        return watershed


# 流域划分示例
print("\n" + "="*60)
print("流域划分示例")
print("="*60)

# 使用上面的流向和汇流累积
delineation = WatershedDelineation(flow_dir, flow_acc)

# 查找主要出水口
pour_points = delineation.find_pour_points(threshold=80)
print(f"找到 {len(pour_points)} 个潜在出水口")

# 划分主流域
if pour_points:
    main_pour = pour_points[0]  # 最大的
    print(f"主出水口: {main_pour}")
    
    watershed = delineation.trace_upstream(main_pour[0], main_pour[1])
    
    basin_area = watershed.sum()
    print(f"流域面积: {basin_area} 个栅格")
    
    # 可视化
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(filled_dem, cmap='terrain', alpha=0.6)
    
    # 流域边界
    watershed_mask = np.ma.masked_where(~watershed, watershed)
    ax.imshow(watershed_mask, cmap='Blues', alpha=0.5)
    
    # 出水口
    ax.plot(main_pour[1], main_pour[0], 'r*', markersize=20,
           label='出水口')
    
    # 河网
    stream_in_basin = stream_network & watershed
    stream_mask = np.ma.masked_where(stream_in_basin == 0, 
                                     stream_in_basin)
    ax.imshow(stream_mask, cmap='Blues', alpha=0.9)
    
    ax.set_title(f'流域划分结果（面积={basin_area}栅格）', fontsize=14)
    ax.axis('off')
    ax.legend()
    plt.tight_layout()
    plt.savefig('watershed_delineation.png', dpi=300, bbox_inches='tight')
    plt.show()
```

---

## 三、地形特征分析

```python
class TerrainAnalysis:
    """
    地形特征分析
    """
    
    @staticmethod
    def slope_aspect(dem, cell_size=30):
        """
        坡度与坡向分析
        
        参数:
            dem: DEM数据
            cell_size: 栅格大小 (m)
        
        返回:
            坡度（度）, 坡向（度）
        """
        # 梯度计算
        dy, dx = np.gradient(dem, cell_size)
        
        # 坡度（弧度转度）
        slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
        slope_deg = np.degrees(slope_rad)
        
        # 坡向（0-360度，正北为0）
        aspect_rad = np.arctan2(dy, dx)
        aspect_deg = np.degrees(aspect_rad)
        aspect_deg = (90 - aspect_deg) % 360
        
        return slope_deg, aspect_deg
    
    @staticmethod
    def plot_terrain_features(dem, slope, aspect):
        """
        可视化地形特征
        """
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        
        # DEM
        im1 = axes[0].imshow(dem, cmap='terrain')
        axes[0].set_title('高程', fontsize=14)
        axes[0].axis('off')
        plt.colorbar(im1, ax=axes[0], label='高程 (m)')
        
        # 坡度
        im2 = axes[1].imshow(slope, cmap='YlOrRd')
        axes[1].set_title('坡度', fontsize=14)
        axes[1].axis('off')
        plt.colorbar(im2, ax=axes[1], label='坡度 (°)')
        
        # 坡向
        im3 = axes[2].imshow(aspect, cmap='hsv')
        axes[2].set_title('坡向', fontsize=14)
        axes[2].axis('off')
        plt.colorbar(im3, ax=axes[2], label='坡向 (°)')
        
        plt.tight_layout()
        plt.savefig('terrain_features.png', dpi=300, bbox_inches='tight')
        plt.show()


# 地形分析
print("\n" + "="*60)
print("地形特征分析")
print("="*60)

slope, aspect = TerrainAnalysis.slope_aspect(filled_dem, cell_size=100)

print(f"坡度统计:")
print(f"  均值: {slope.mean():.2f}°")
print(f"  最大: {slope.max():.2f}°")

print(f"\n坡向统计:")
print(f"  均值: {aspect.mean():.2f}°")

TerrainAnalysis.plot_terrain_features(filled_dem, slope, aspect)
```

---

## 四、项目总结

### 学习要点

1. **DEM处理**：洼地填充是基础
2. **流向分析**：D8算法最常用
3. **汇流累积**：识别河网关键
4. **流域划分**：上游追溯法
5. **地形分析**：梯度计算

### 技术栈

- NumPy：数组运算
- SciPy：图像处理
- Matplotlib：可视化
- 算法：BFS、梯度下降

### 扩展方向

- 集成真实GIS数据（GDAL）
- 3D可视化（Mayavi）
- Web GIS（Leaflet）
- 分布式水文模型

---

**下一项目**：项目7 - 水利工程优化调度系统
