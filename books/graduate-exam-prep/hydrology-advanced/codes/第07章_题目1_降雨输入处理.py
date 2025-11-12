"""
第7章 降雨径流预报
题目1：降雨输入处理与面雨量计算

知识点：
- 面雨量概念
- 算术平均法
- 泰森多边形法
- 距离倒数加权法（IDW）
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy.spatial import Voronoi, voronoi_plot_2d
from matplotlib.patches import Polygon as MplPolygon

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 数据
F = 200  # 流域面积，km²
stations = np.array([
    [5, 3],   # 站1
    [15, 3],  # 站2
    [5, 7],   # 站3
    [15, 7]   # 站4
])
rainfall = np.array([45, 52, 38, 48])  # mm
station_names = ['站1', '站2', '站3', '站4']

# 流域边界
basin_x = [0, 20, 20, 0, 0]
basin_y = [0, 0, 10, 10, 0]

print("="*70)
print("题目1：降雨输入处理与面雨量计算")
print("="*70)
print(f"\n流域信息：")
print(f"  流域面积 F = {F} km²")
print(f"  流域形状：长20km × 宽10km")
print(f"\n雨量站观测数据：")
for i, (name, pos, p) in enumerate(zip(station_names, stations, rainfall)):
    print(f"  {name}: 位置({pos[0]}, {pos[1]}) km, 雨量={p} mm")

# 方法1：算术平均法
P_arithmetic = np.mean(rainfall)
print(f"\n方法1：算术平均法")
print(f"  P̄ = (45+52+38+48)/4")
print(f"  P̄ = {P_arithmetic:.2f} mm")

# 方法2：泰森多边形法
# 由于站点对称分布，手动计算
areas = np.array([50, 50, 50, 50])  # 各站控制面积
P_thiessen = np.sum(rainfall * areas) / F
print(f"\n方法2：泰森多边形法")
print(f"  各站控制面积：{areas} km²")
print(f"  P̄ = Σ(Pᵢ·Aᵢ)/F")
print(f"  P̄ = {P_thiessen:.2f} mm")

# 方法3：IDW法（流域中心点）
center = np.array([10, 5])
distances = np.sqrt(np.sum((stations - center)**2, axis=1))
p_power = 2  # IDW指数
weights = (1 / distances**p_power) / np.sum(1 / distances**p_power)
P_idw_center = np.sum(weights * rainfall)

print(f"\n方法3：距离倒数加权法（IDW）")
print(f"  流域中心：({center[0]}, {center[1]}) km")
print(f"  各站到中心距离：")
for i, (name, d) in enumerate(zip(station_names, distances)):
    print(f"    {name}: {d:.2f} km")
print(f"  权重：{weights}")
print(f"  P̄ = {P_idw_center:.2f} mm")

# 方法3：IDW法（网格平均）
nx, ny = 20, 10  # 网格数
x_grid = np.linspace(1, 19, nx)
y_grid = np.linspace(1, 9, ny)
X, Y = np.meshgrid(x_grid, y_grid)

# 计算每个网格点的雨量
P_grid = np.zeros_like(X)
for i in range(ny):
    for j in range(nx):
        point = np.array([X[i, j], Y[i, j]])
        dists = np.sqrt(np.sum((stations - point)**2, axis=1))
        # 避免除零
        dists = np.maximum(dists, 0.1)
        w = (1 / dists**p_power) / np.sum(1 / dists**p_power)
        P_grid[i, j] = np.sum(w * rainfall)

P_idw_grid = np.mean(P_grid)
print(f"\n  网格平均法（{nx}×{ny}网格）：")
print(f"  P̄ = {P_idw_grid:.2f} mm")

print(f"\n三种方法对比：")
print(f"  算术平均法：{P_arithmetic:.2f} mm")
print(f"  泰森多边形法：{P_thiessen:.2f} mm")
print(f"  IDW法（中心点）：{P_idw_center:.2f} mm")
print(f"  IDW法（网格）：{P_idw_grid:.2f} mm")
print("="*70)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

# 子图1：站点分布和降雨量
ax1 = fig.add_subplot(gs[0, :2])
ax1.plot(basin_x, basin_y, 'k-', linewidth=2, label='流域边界')
ax1.fill(basin_x, basin_y, alpha=0.1, color='cyan')

# 绘制雨量站
scatter = ax1.scatter(stations[:, 0], stations[:, 1], 
                      c=rainfall, s=rainfall*10, cmap='Blues',
                      edgecolors='black', linewidth=2, zorder=5)

# 标注站名和雨量
for i, (name, pos, p) in enumerate(zip(station_names, stations, rainfall)):
    ax1.text(pos[0], pos[1]-0.8, f'{name}\n{p}mm',
             ha='center', fontsize=10, fontweight='bold')

ax1.set_xlabel('X (km)', fontsize=11)
ax1.set_ylabel('Y (km)', fontsize=11)
ax1.set_title('题目1-1：雨量站分布和观测雨量', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(-1, 21)
ax1.set_ylim(-1, 11)
ax1.set_aspect('equal')
cbar = plt.colorbar(scatter, ax=ax1)
cbar.set_label('雨量 (mm)', fontsize=10)

# 子图2：三种方法对比
ax2 = fig.add_subplot(gs[0, 2])
methods = ['算术\n平均', '泰森\n多边形', 'IDW\n(中心)', 'IDW\n(网格)']
values = [P_arithmetic, P_thiessen, P_idw_center, P_idw_grid]
colors_bar = ['blue', 'green', 'red', 'purple']

bars = ax2.bar(methods, values, color=colors_bar, alpha=0.7, edgecolor='black')
for bar, val in zip(bars, values):
    ax2.text(bar.get_x() + bar.get_width()/2, val + 0.5,
             f'{val:.2f}mm', ha='center', fontsize=10, fontweight='bold')

ax2.set_ylabel('面雨量 (mm)', fontsize=11)
ax2.set_title('题目1-2：三种方法计算结果对比', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_ylim(0, 50)

# 子图3：泰森多边形
ax3 = fig.add_subplot(gs[1, :2])
ax3.plot(basin_x, basin_y, 'k-', linewidth=2)
ax3.fill(basin_x, basin_y, alpha=0.1, color='cyan')

# 绘制泰森多边形边界（手动，因为对称分布）
ax3.plot([10, 10], [0, 10], 'r--', linewidth=2, label='泰森多边形边界')
ax3.plot([0, 20], [5, 5], 'r--', linewidth=2)

# 标注控制面积
ax3.text(5, 2.5, f'A₁=50km²\nP₁=45mm', ha='center', fontsize=10,
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
ax3.text(15, 2.5, f'A₂=50km²\nP₂=52mm', ha='center', fontsize=10,
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
ax3.text(5, 7.5, f'A₃=50km²\nP₃=38mm', ha='center', fontsize=10,
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
ax3.text(15, 7.5, f'A₄=50km²\nP₄=48mm', ha='center', fontsize=10,
         bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))

# 站点
ax3.scatter(stations[:, 0], stations[:, 1], c='red', s=100,
            edgecolors='black', linewidth=2, zorder=5)

ax3.set_xlabel('X (km)', fontsize=11)
ax3.set_ylabel('Y (km)', fontsize=11)
ax3.set_title('题目1-3：泰森多边形法', fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.set_xlim(-1, 21)
ax3.set_ylim(-1, 11)
ax3.set_aspect('equal')

# 子图4：IDW权重可视化
ax4 = fig.add_subplot(gs[1, 2])
ax4.bar(station_names, weights, color=colors_bar, alpha=0.7, edgecolor='black')
for i, (name, w) in enumerate(zip(station_names, weights)):
    ax4.text(i, w + 0.01, f'{w:.3f}',
             ha='center', fontsize=10, fontweight='bold')

ax4.set_ylabel('权重', fontsize=11)
ax4.set_title('题目1-4：IDW法权重分布', fontsize=11, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')
ax4.set_ylim(0, 0.35)

# 子图5：IDW空间插值结果
ax5 = fig.add_subplot(gs[2, :2])
contour = ax5.contourf(X, Y, P_grid, levels=15, cmap='Blues')
ax5.plot(basin_x, basin_y, 'k-', linewidth=2)
ax5.scatter(stations[:, 0], stations[:, 1], c='red', s=100,
            edgecolors='black', linewidth=2, zorder=5, label='雨量站')
ax5.plot(center[0], center[1], 'y*', markersize=20, label='流域中心')

ax5.set_xlabel('X (km)', fontsize=11)
ax5.set_ylabel('Y (km)', fontsize=11)
ax5.set_title('题目1-5：IDW空间插值结果', fontsize=12, fontweight='bold')
ax5.legend(fontsize=10)
cbar2 = plt.colorbar(contour, ax=ax5)
cbar2.set_label('雨量 (mm)', fontsize=10)
ax5.set_xlim(0, 20)
ax5.set_ylim(0, 10)
ax5.set_aspect('equal')

# 子图6：距离影响示意
ax6 = fig.add_subplot(gs[2, 2])
dist_range = np.linspace(0.1, 20, 100)
p_values = [1, 2, 3]
for p in p_values:
    weight_curve = 1 / dist_range**p
    weight_curve = weight_curve / weight_curve[0]  # 归一化
    ax6.plot(dist_range, weight_curve, linewidth=2, label=f'p={p}')

ax6.set_xlabel('距离 (km)', fontsize=11)
ax6.set_ylabel('相对权重', fontsize=11)
ax6.set_title('题目1-6：IDW距离权重函数', fontsize=11, fontweight='bold')
ax6.legend(fontsize=10)
ax6.grid(True, alpha=0.3)
ax6.set_xlim(0, 20)

plt.savefig('题目1_降雨输入处理.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目1图形已生成：题目1_降雨输入处理.png")
plt.show()
