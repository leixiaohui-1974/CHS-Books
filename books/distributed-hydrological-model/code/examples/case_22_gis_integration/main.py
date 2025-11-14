"""
案例22：GIS集成应用
==================

演示分布式水文模型与GIS的集成应用，
包括空间数据处理、流域分析、专题图制作。

核心内容：
1. 空间数据结构
2. 流域自动划分
from pathlib import Path
3. 子流域参数提取
4. 空间插值应用
5. 专题图制作与导出

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import sys
import os
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.interpolation.idw import inverse_distance_weighting

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SpatialData:
    """空间数据类"""
    
    def __init__(self, data: np.ndarray, extent: Tuple[float, float, float, float],
                 crs: str = "EPSG:4326"):
        """
        初始化空间数据
        
        Parameters
        ----------
        data : np.ndarray
            栅格数据（2D数组）
        extent : tuple
            空间范围 (xmin, xmax, ymin, ymax)
        crs : str
            坐标参考系统
        """
        self.data = data
        self.extent = extent
        self.crs = crs
        self.shape = data.shape
        
        # 计算分辨率
        self.dx = (extent[1] - extent[0]) / data.shape[1]
        self.dy = (extent[3] - extent[2]) / data.shape[0]
    
    def get_coordinates(self):
        """获取栅格中心坐标"""
        xmin, xmax, ymin, ymax = self.extent
        x = np.linspace(xmin + self.dx/2, xmax - self.dx/2, self.shape[1])
        y = np.linspace(ymin + self.dy/2, ymax - self.dy/2, self.shape[0])
        return np.meshgrid(x, y)
    
    def extract_value(self, x: float, y: float) -> float:
        """提取指定坐标的值"""
        xmin, xmax, ymin, ymax = self.extent
        if not (xmin <= x <= xmax and ymin <= y <= ymax):
            return np.nan
        
        col = int((x - xmin) / self.dx)
        row = int((ymax - y) / self.dy)  # y轴反向
        
        col = np.clip(col, 0, self.shape[1] - 1)
        row = np.clip(row, 0, self.shape[0] - 1)
        
        return self.data[row, col]


class SubBasin:
    """子流域类"""
    
    def __init__(self, basin_id: int, boundary: np.ndarray):
        """
        初始化子流域
        
        Parameters
        ----------
        basin_id : int
            流域编号
        boundary : np.ndarray
            边界坐标数组 [[x1,y1], [x2,y2], ...]
        """
        self.basin_id = basin_id
        self.boundary = boundary
        self.area = self._calculate_area()
        self.centroid = self._calculate_centroid()
        self.attributes = {}
    
    def _calculate_area(self) -> float:
        """计算面积（Shoelace公式）"""
        x = self.boundary[:, 0]
        y = self.boundary[:, 1]
        return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
    
    def _calculate_centroid(self) -> np.ndarray:
        """计算质心"""
        return np.mean(self.boundary, axis=0)
    
    def add_attribute(self, name: str, value: float):
        """添加属性"""
        self.attributes[name] = value
    
    def contains_point(self, x: float, y: float) -> bool:
        """判断点是否在多边形内（射线法）"""
        n = len(self.boundary)
        inside = False
        
        p1x, p1y = self.boundary[0]
        for i in range(1, n + 1):
            p2x, p2y = self.boundary[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside


class WatershedGIS:
    """流域GIS分析系统"""
    
    def __init__(self):
        """初始化GIS系统"""
        self.dem = None
        self.basins = []
        self.layers = {}
    
    def add_layer(self, name: str, data: SpatialData):
        """添加图层"""
        self.layers[name] = data
    
    def create_subbasins(self, n_basins: int = 5) -> List[SubBasin]:
        """
        创建子流域（简化版）
        
        Parameters
        ----------
        n_basins : int
            子流域数量
        """
        # 在工作区域内生成随机子流域
        basins = []
        
        # 主流域范围
        main_boundary = np.array([
            [0, 0], [100, 0], [100, 80], [80, 100], 
            [50, 90], [20, 100], [0, 80]
        ])
        
        # 根据流域数量划分（简化为矩形子流域）
        if n_basins == 5:
            # 五个子流域的边界（模拟真实流域形状）
            boundaries = [
                np.array([[0, 0], [40, 0], [40, 40], [0, 40]]),      # 左下
                np.array([[40, 0], [80, 0], [80, 40], [40, 40]]),    # 右下
                np.array([[0, 40], [40, 40], [40, 80], [0, 80]]),    # 左中
                np.array([[40, 40], [80, 40], [70, 80], [40, 80]]),  # 右中
                np.array([[20, 80], [70, 80], [50, 90], [30, 100], [20, 100]])  # 上
            ]
        else:
            # 默认简单网格划分
            cols = int(np.sqrt(n_basins))
            rows = (n_basins + cols - 1) // cols
            dx = 100 / cols
            dy = 100 / rows
            
            boundaries = []
            for i in range(n_basins):
                row = i // cols
                col = i % cols
                x0, y0 = col * dx, row * dy
                boundaries.append(np.array([
                    [x0, y0], [x0 + dx, y0], [x0 + dx, y0 + dy], [x0, y0 + dy]
                ]))
        
        for i, boundary in enumerate(boundaries):
            basin = SubBasin(i + 1, boundary)
            basins.append(basin)
        
        self.basins = basins
        return basins
    
    def extract_basin_statistics(self, layer_name: str):
        """提取各子流域的统计值"""
        if layer_name not in self.layers:
            return
        
        layer = self.layers[layer_name]
        X, Y = layer.get_coordinates()
        
        for basin in self.basins:
            values = []
            for i in range(layer.shape[0]):
                for j in range(layer.shape[1]):
                    x, y = X[i, j], Y[i, j]
                    if basin.contains_point(x, y):
                        val = layer.data[i, j]
                        if not np.isnan(val):
                            values.append(val)
            
            if values:
                basin.add_attribute(f'{layer_name}_mean', np.mean(values))
                basin.add_attribute(f'{layer_name}_std', np.std(values))
                basin.add_attribute(f'{layer_name}_min', np.min(values))
                basin.add_attribute(f'{layer_name}_max', np.max(values))
    
    def spatial_interpolation(self, stations: np.ndarray, values: np.ndarray,
                             grid_size: Tuple[int, int] = (50, 50),
                             method: str = 'idw') -> SpatialData:
        """
        空间插值
        
        Parameters
        ----------
        stations : np.ndarray
            站点坐标 [[x1,y1], [x2,y2], ...]
        values : np.ndarray
            站点值 [v1, v2, ...]
        grid_size : tuple
            插值网格大小
        method : str
            插值方法 ('idw', 'thiessen')
        """
        # 创建插值网格
        xmin, xmax = stations[:, 0].min() - 10, stations[:, 0].max() + 10
        ymin, ymax = stations[:, 1].min() - 10, stations[:, 1].max() + 10
        
        x = np.linspace(xmin, xmax, grid_size[1])
        y = np.linspace(ymin, ymax, grid_size[0])
        X, Y = np.meshgrid(x, y)
        
        # 插值
        Z = np.zeros(grid_size)
        
        if method == 'idw':
            target_points = np.column_stack([X.ravel(), Y.ravel()])
            Z_flat = inverse_distance_weighting(stations, values, target_points, power=2)
            Z = Z_flat.reshape(grid_size)
        elif method == 'thiessen':
            # 简化Thiessen插值（最近邻）
            for i in range(grid_size[0]):
                for j in range(grid_size[1]):
                    point = np.array([X[i, j], Y[i, j]])
                    distances = np.linalg.norm(stations - point, axis=1)
                    nearest_idx = np.argmin(distances)
                    Z[i, j] = values[nearest_idx]
        
        extent = (xmin, xmax, ymin, ymax)
        return SpatialData(Z, extent)


def run_gis_integration():
    """运行GIS集成应用"""
    print("\n" + "="*70)
    print("案例22：GIS集成应用")
    print("="*70 + "\n")
    
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 创建流域GIS系统
    print("1. 初始化流域GIS系统...")
    gis = WatershedGIS()
    
    # 2. 生成DEM数据
    print("2. 生成DEM数据...")
    nx, ny = 100, 100
    x = np.linspace(0, 100, nx)
    y = np.linspace(0, 100, ny)
    X, Y = np.meshgrid(x, y)
    
    # 模拟山地地形（从东南向西北递增）
    Z = 500 + 300 * (X / 100) + 400 * (Y / 100) + \
        50 * np.sin(2 * np.pi * X / 50) * np.cos(2 * np.pi * Y / 50)
    
    dem = SpatialData(Z, extent=(0, 100, 0, 100))
    gis.add_layer('DEM', dem)
    
    print(f"   DEM尺寸: {dem.shape}")
    print(f"   高程范围: {Z.min():.1f} - {Z.max():.1f} m\n")
    
    # 3. 创建子流域
    print("3. 创建子流域...")
    basins = gis.create_subbasins(n_basins=5)
    
    print(f"   子流域数量: {len(basins)}")
    for basin in basins:
        print(f"   流域{basin.basin_id}: 面积 {basin.area:.1f} km², "
              f"质心 ({basin.centroid[0]:.1f}, {basin.centroid[1]:.1f})")
    print()
    
    # 4. 生成土地利用数据
    print("4. 生成土地利用数据...")
    # 模拟土地利用类型（1-林地, 2-草地, 3-农田, 4-城市）
    landuse = np.ones((ny, nx))
    landuse[Y > 60] = 1  # 上游林地
    landuse[(Y > 30) & (Y <= 60) & (X < 50)] = 2  # 中游草地
    landuse[(Y > 30) & (Y <= 60) & (X >= 50)] = 3  # 中游农田
    landuse[Y <= 30] = 3  # 下游农田
    landuse[(Y <= 30) & (X > 60)] = 4  # 下游城市
    
    landuse_data = SpatialData(landuse, extent=(0, 100, 0, 100))
    gis.add_layer('Landuse', landuse_data)
    
    print("   土地利用类型: 林地(1), 草地(2), 农田(3), 城市(4)\n")
    
    # 5. 生成降雨站点数据
    print("5. 生成降雨站点数据...")
    np.random.seed(42)
    n_stations = 8
    stations = np.random.uniform([10, 10], [90, 90], (n_stations, 2))
    
    # 模拟降雨量（随海拔增加而增加）
    rainfall = np.array([dem.extract_value(s[0], s[1]) for s in stations])
    rainfall = 500 + (rainfall - rainfall.min()) / (rainfall.max() - rainfall.min()) * 300
    rainfall += np.random.normal(0, 20, n_stations)  # 添加随机性
    
    print(f"   雨量站数量: {n_stations}")
    print(f"   降雨范围: {rainfall.min():.1f} - {rainfall.max():.1f} mm\n")
    
    # 6. 空间插值
    print("6. 进行空间插值...")
    rainfall_idw = gis.spatial_interpolation(stations, rainfall, 
                                             grid_size=(50, 50), method='idw')
    gis.add_layer('Rainfall_IDW', rainfall_idw)
    
    rainfall_thiessen = gis.spatial_interpolation(stations, rainfall,
                                                  grid_size=(50, 50), method='thiessen')
    gis.add_layer('Rainfall_Thiessen', rainfall_thiessen)
    
    print("   IDW插值完成")
    print("   Thiessen插值完成\n")
    
    # 7. 提取子流域统计
    print("7. 提取子流域统计...")
    gis.extract_basin_statistics('DEM')
    gis.extract_basin_statistics('Rainfall_IDW')
    
    print("\n子流域属性统计:")
    print("-" * 70)
    print(f"{'流域ID':^8} {'面积(km²)':^12} {'平均高程(m)':^14} {'平均降雨(mm)':^14}")
    print("-" * 70)
    for basin in basins:
        print(f"{basin.basin_id:^8d} {basin.area:^12.1f} "
              f"{basin.attributes.get('DEM_mean', 0):^14.1f} "
              f"{basin.attributes.get('Rainfall_IDW_mean', 0):^14.1f}")
    print("-" * 70 + "\n")
    
    # 8. 可视化
    print("8. 生成GIS专题图...")
    
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)
    
    # 图1: DEM
    ax1 = fig.add_subplot(gs[0, 0])
    im1 = ax1.imshow(dem.data, extent=dem.extent, cmap='terrain', origin='lower')
    ax1.plot(stations[:, 0], stations[:, 1], 'k^', markersize=8, 
            markerfacecolor='red', markeredgewidth=1.5, label='雨量站')
    ax1.set_xlabel('X (km)', fontsize=10)
    ax1.set_ylabel('Y (km)', fontsize=10)
    ax1.set_title('数字高程模型 (DEM)', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    plt.colorbar(im1, ax=ax1, label='高程 (m)')
    
    # 图2: 土地利用
    ax2 = fig.add_subplot(gs[0, 1])
    landuse_cmap = colors.ListedColormap(['darkgreen', 'yellowgreen', 'gold', 'gray'])
    im2 = ax2.imshow(landuse_data.data, extent=landuse_data.extent, 
                    cmap=landuse_cmap, origin='lower', vmin=1, vmax=4)
    ax2.set_xlabel('X (km)', fontsize=10)
    ax2.set_ylabel('Y (km)', fontsize=10)
    ax2.set_title('土地利用类型', fontsize=12, fontweight='bold')
    cbar2 = plt.colorbar(im2, ax=ax2, ticks=[1, 2, 3, 4])
    cbar2.set_ticklabels(['林地', '草地', '农田', '城市'])
    
    # 图3: 子流域划分
    ax3 = fig.add_subplot(gs[0, 2])
    
    # 绘制子流域边界
    patches = []
    colors_list = plt.cm.Set3(np.linspace(0, 1, len(basins)))
    for i, basin in enumerate(basins):
        polygon = Polygon(basin.boundary, closed=True, 
                         facecolor=colors_list[i], edgecolor='black', linewidth=2, alpha=0.7)
        patches.append(polygon)
        # 标注流域编号
        ax3.text(basin.centroid[0], basin.centroid[1], str(basin.basin_id),
                fontsize=14, fontweight='bold', ha='center', va='center')
    
    for patch in patches:
        ax3.add_patch(patch)
    
    ax3.set_xlim(0, 100)
    ax3.set_ylim(0, 100)
    ax3.set_xlabel('X (km)', fontsize=10)
    ax3.set_ylabel('Y (km)', fontsize=10)
    ax3.set_title('子流域划分', fontsize=12, fontweight='bold')
    ax3.set_aspect('equal')
    
    # 图4: 降雨站点与观测值
    ax4 = fig.add_subplot(gs[1, 0])
    scatter = ax4.scatter(stations[:, 0], stations[:, 1], c=rainfall,
                         s=200, cmap='Blues', edgecolors='black', linewidth=1.5)
    for i, (x, y, r) in enumerate(zip(stations[:, 0], stations[:, 1], rainfall)):
        ax4.text(x, y+5, f'{r:.0f}', fontsize=9, ha='center', fontweight='bold')
    ax4.set_xlim(0, 100)
    ax4.set_ylim(0, 100)
    ax4.set_xlabel('X (km)', fontsize=10)
    ax4.set_ylabel('Y (km)', fontsize=10)
    ax4.set_title('雨量站观测值', fontsize=12, fontweight='bold')
    plt.colorbar(scatter, ax=ax4, label='降雨 (mm)')
    ax4.set_aspect('equal')
    
    # 图5: IDW插值结果
    ax5 = fig.add_subplot(gs[1, 1])
    im5 = ax5.imshow(rainfall_idw.data, extent=rainfall_idw.extent, 
                    cmap='Blues', origin='lower')
    ax5.plot(stations[:, 0], stations[:, 1], 'k^', markersize=6,
            markerfacecolor='red', markeredgewidth=1)
    ax5.set_xlabel('X (km)', fontsize=10)
    ax5.set_ylabel('Y (km)', fontsize=10)
    ax5.set_title('IDW插值结果', fontsize=12, fontweight='bold')
    plt.colorbar(im5, ax=ax5, label='降雨 (mm)')
    
    # 图6: Thiessen插值结果
    ax6 = fig.add_subplot(gs[1, 2])
    im6 = ax6.imshow(rainfall_thiessen.data, extent=rainfall_thiessen.extent,
                    cmap='Blues', origin='lower')
    ax6.plot(stations[:, 0], stations[:, 1], 'k^', markersize=6,
            markerfacecolor='red', markeredgewidth=1)
    ax6.set_xlabel('X (km)', fontsize=10)
    ax6.set_ylabel('Y (km)', fontsize=10)
    ax6.set_title('Thiessen插值结果', fontsize=12, fontweight='bold')
    plt.colorbar(im6, ax=ax6, label='降雨 (mm)')
    
    # 图7: 子流域平均高程
    ax7 = fig.add_subplot(gs[2, 0])
    basin_ids = [b.basin_id for b in basins]
    basin_elevs = [b.attributes.get('DEM_mean', 0) for b in basins]
    bars1 = ax7.bar(basin_ids, basin_elevs, color='brown', alpha=0.7, edgecolor='black')
    ax7.set_xlabel('子流域ID', fontsize=10)
    ax7.set_ylabel('平均高程 (m)', fontsize=10)
    ax7.set_title('子流域平均高程', fontsize=12, fontweight='bold')
    ax7.grid(True, alpha=0.3, axis='y')
    # 添加数值标签
    for bar in bars1:
        height = bar.get_height()
        ax7.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f}', ha='center', va='bottom', fontsize=9)
    
    # 图8: 子流域平均降雨
    ax8 = fig.add_subplot(gs[2, 1])
    basin_rainfall = [b.attributes.get('Rainfall_IDW_mean', 0) for b in basins]
    bars2 = ax8.bar(basin_ids, basin_rainfall, color='blue', alpha=0.7, edgecolor='black')
    ax8.set_xlabel('子流域ID', fontsize=10)
    ax8.set_ylabel('平均降雨 (mm)', fontsize=10)
    ax8.set_title('子流域平均降雨', fontsize=12, fontweight='bold')
    ax8.grid(True, alpha=0.3, axis='y')
    for bar in bars2:
        height = bar.get_height()
        ax8.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f}', ha='center', va='bottom', fontsize=9)
    
    # 图9: 高程-降雨关系
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.scatter(basin_elevs, basin_rainfall, s=200, c=basin_ids,
               cmap='viridis', edgecolors='black', linewidth=1.5)
    for i, (elev, rain, bid) in enumerate(zip(basin_elevs, basin_rainfall, basin_ids)):
        ax9.text(elev, rain+5, f'流域{bid}', fontsize=9, ha='center')
    
    # 拟合线性关系
    if len(basin_elevs) > 1:
        z = np.polyfit(basin_elevs, basin_rainfall, 1)
        p = np.poly1d(z)
        x_fit = np.linspace(min(basin_elevs), max(basin_elevs), 100)
        ax9.plot(x_fit, p(x_fit), 'r--', linewidth=2, alpha=0.7,
                label=f'y = {z[0]:.2f}x + {z[1]:.1f}')
    
    ax9.set_xlabel('平均高程 (m)', fontsize=10)
    ax9.set_ylabel('平均降雨 (mm)', fontsize=10)
    ax9.set_title('高程-降雨关系', fontsize=12, fontweight='bold')
    ax9.legend(fontsize=9)
    ax9.grid(True, alpha=0.3)
    
    plt.savefig(f'{output_dir}/gis_integration.png', 
                dpi=300, bbox_inches='tight')
    print(f"   专题图已保存: {output_dir}/gis_integration.png")
    plt.close()
    
    print(f"\n专题图已保存到 {output_dir}/ 目录")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_gis_integration()
