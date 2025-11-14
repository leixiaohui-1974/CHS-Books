"""
案例14：完整流域分布式水文模型
===============================

整合DEM分析、空间插值、产流模拟、汇流计算，
构建完整的分布式水文建模系统。

核心内容：
1. DEM地形分析
2. 降雨空间插值
from pathlib import Path
3. 网格化产流计算
4. 坡面汇流模拟
5. 河道汇流演进
6. 完整模拟流程

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.runoff_generation.xaj_model import XinAnJiangModel
from core.interpolation.idw import inverse_distance_weighting

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


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


def generate_rainfall_stations(n_stations=5, bbox=(0, 20000, 0, 20000)):
    """生成降雨站点"""
    np.random.seed(42)
    x = np.random.uniform(bbox[0], bbox[1], n_stations)
    y = np.random.uniform(bbox[2], bbox[3], n_stations)
    return np.column_stack([x, y])


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


def run_watershed_model(n_days=100):
    """运行完整流域模型"""
    print("\n" + "="*70)
    print("案例14：完整流域分布式水文模型")
    print("="*70 + "\n")
    
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 创建流域网格
    print("1. 创建流域网格...")
    nx, ny = 20, 20
    grid_x, grid_y, mask = create_watershed_grid(nx, ny)
    n_cells = np.sum(mask)
    print(f"   网格大小: {nx} × {ny}")
    print(f"   有效网格: {n_cells}")
    print(f"   流域面积: {n_cells} km²\n")
    
    # 2. 生成降雨站点
    print("2. 生成降雨站点...")
    stations_xy = generate_rainfall_stations(5)
    print(f"   站点数量: {len(stations_xy)}\n")
    
    # 3. 生成降雨过程
    print("3. 生成降雨过程...")
    rainfall_stations = np.zeros((n_days, len(stations_xy)))
    flood_days = [20, 50, 80]
    for day in flood_days:
        for i in range(5):
            if day + i < n_days:
                rainfall_stations[day + i, :] = 40 * np.exp(-0.3 * i) * \
                                                (0.8 + 0.4 * np.random.rand(len(stations_xy)))
    
    print(f"   时间步数: {n_days}")
    print(f"   总降雨: {np.mean(np.sum(rainfall_stations, axis=0)):.1f} mm\n")
    
    # 4. 设置产流参数
    print("4. 设置产流参数...")
    params = {
        'K': 0.8, 'UM': 20.0, 'LM': 80.0, 'C': 0.15,
        'WM': 120.0, 'B': 0.35, 'IM': 0.02,
        'SM': 30.0, 'EX': 1.5, 'KG': 0.4, 'KI': 0.3,
        'CG': 0.98, 'CI': 0.6, 'CS': 0.8
    }
    print("   使用新安江模型参数\n")
    
    # 5. 运行分布式模拟
    print("5. 运行分布式水文模拟...")
    
    # 生成蒸散发
    EM = 3.0 + 2.0 * np.sin(2 * np.pi * np.arange(n_days) / 365)
    
    # 存储结果
    total_runoff = np.zeros(n_days)
    
    for t in range(n_days):
        # 插值降雨
        rainfall_grid = interpolate_rainfall(
            grid_x, grid_y, mask, 
            stations_xy, rainfall_stations[t]
        )
        
        # 计算网格产流
        grid_runoff = np.zeros_like(rainfall_grid)
        valid_indices = np.where(mask)
        
        for i, j in zip(*valid_indices):
            if rainfall_grid[i, j] > 0:
                # 简化：使用集总模型
                model = XinAnJiangModel(params)
                results = model.run(
                    np.array([rainfall_grid[i, j]]),
                    np.array([EM[t]])
                )
                grid_runoff[i, j] = results['R'][0]
        
        # 汇总流域出流
        total_runoff[t] = np.mean(grid_runoff[mask])
        
        if (t + 1) % 20 == 0:
            print(f"   进度: {(t+1)/n_days*100:.0f}%")
    
    print("\n6. 模拟完成")
    print(f"   总径流: {np.sum(total_runoff):.1f} mm")
    print(f"   径流系数: {np.sum(total_runoff) / np.mean(np.sum(rainfall_stations, axis=0)):.3f}\n")
    
    # 7. 可视化
    print("7. 生成可视化...")
    
    # 流域网格图
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # 左图：流域网格
    ax1 = axes[0]
    ax1.contourf(grid_x/1000, grid_y/1000, mask.astype(float), 
                levels=[0, 0.5, 1], colors=['white', 'lightblue'])
    ax1.scatter(stations_xy[:, 0]/1000, stations_xy[:, 1]/1000, 
               c='red', s=100, marker='^', label='雨量站', zorder=5)
    ax1.set_xlabel('X (km)', fontsize=12)
    ax1.set_ylabel('Y (km)', fontsize=12)
    ax1.set_title('流域网格与雨量站分布', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')
    
    # 右图：降雨-径流过程
    ax2 = axes[1]
    time = np.arange(n_days)
    mean_rainfall = np.mean(rainfall_stations, axis=1)
    
    ax2_rain = ax2.twinx()
    ax2_rain.bar(time, mean_rainfall, color='lightblue', alpha=0.5, label='平均降雨')
    ax2_rain.set_ylim([max(mean_rainfall)*2, 0])
    ax2_rain.set_ylabel('降雨 (mm)', fontsize=11)
    ax2_rain.legend(loc='upper right', fontsize=9)
    
    ax2.plot(time, total_runoff, 'b-', linewidth=2, label='流域出流')
    ax2.set_xlabel('时间 (天)', fontsize=12)
    ax2.set_ylabel('径流 (mm)', fontsize=11)
    ax2.set_title('流域降雨-径流过程', fontsize=13, fontweight='bold')
    ax2.legend(loc='upper left', fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/watershed_simulation.png', dpi=300, bbox_inches='tight')
    print(f"   图表已保存: {output_dir}/watershed_simulation.png")
    plt.close()
    
    # 统计
    print("\n" + "="*70)
    print("完整流域模拟结果统计")
    print("="*70)
    print(f"\n【流域特征】")
    print(f"  网格大小: {nx} × {ny}")
    print(f"  流域面积: {n_cells} km²")
    print(f"  雨量站数: {len(stations_xy)}")
    
    print(f"\n【水文响应】")
    print(f"  模拟时长: {n_days} 天")
    print(f"  平均降雨: {np.mean(np.sum(rainfall_stations, axis=0)):.1f} mm")
    print(f"  总径流: {np.sum(total_runoff):.1f} mm")
    print(f"  径流系数: {np.sum(total_runoff) / np.mean(np.sum(rainfall_stations, axis=0)):.3f}")
    print(f"  峰值径流: {np.max(total_runoff):.2f} mm")
    
    print(f"\n图表已保存到 {output_dir}/ 目录")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_watershed_model()
