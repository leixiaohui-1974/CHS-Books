"""
案例1：DEM分析与河网提取

本案例演示如何进行DEM（数字高程模型）分析：
1. 生成简化的DEM数据
2. 计算地形坡度和坡向
3. D8流向算法
4. 汇流累积计算
5. 河网提取
6. 子流域划分

注：本案例使用纯NumPy实现，不依赖GDAL等GIS库

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
import os
import sys

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def generate_synthetic_dem(nx=50, ny=50, seed=42):
    """
    生成合成DEM数据（模拟山地地形）
    
    参数:
    ----
    nx, ny : int
        网格大小
    seed : int
        随机种子
    
    返回:
    ----
    dem : ndarray
        DEM高程数据(m)
    dx, dy : float
        网格分辨率(m)
    """
    np.random.seed(seed)
    
    # 网格坐标
    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)
    X, Y = np.meshgrid(x, y)
    
    # 创建山谷地形（从左上到右下）
    # 主趋势：从高到低
    trend = 100 * (1 - 0.7*X - 0.3*Y)
    
    # 添加山脊和山谷
    ridges = 20 * np.sin(3 * np.pi * X) * np.sin(2 * np.pi * Y)
    
    # 添加随机噪声
    noise = 5 * np.random.randn(ny, nx)
    
    # 合成DEM
    dem = trend + ridges + noise
    
    # 确保非负
    dem = np.maximum(dem, 0)
    
    # 网格分辨率(m)
    dx = dy = 10.0
    
    return dem, dx, dy


def calculate_slope_aspect(dem, dx, dy):
    """
    计算坡度和坡向
    
    参数:
    ----
    dem : ndarray
        DEM数据
    dx, dy : float
        网格分辨率
    
    返回:
    ----
    slope : ndarray
        坡度(度)
    aspect : ndarray
        坡向(度, 0-360, 北为0)
    """
    ny, nx = dem.shape
    
    # 计算梯度（中心差分）
    dzdx = np.zeros_like(dem)
    dzdy = np.zeros_like(dem)
    
    # 内部网格
    dzdx[1:-1, 1:-1] = (dem[1:-1, 2:] - dem[1:-1, :-2]) / (2 * dx)
    dzdy[1:-1, 1:-1] = (dem[2:, 1:-1] - dem[:-2, 1:-1]) / (2 * dy)
    
    # 边界（单侧差分）
    dzdx[0, :] = (dem[1, :] - dem[0, :]) / dx
    dzdx[-1, :] = (dem[-1, :] - dem[-2, :]) / dx
    dzdy[:, 0] = (dem[:, 1] - dem[:, 0]) / dy
    dzdy[:, -1] = (dem[:, -1] - dem[:, -2]) / dy
    
    # 坡度（度）
    slope = np.arctan(np.sqrt(dzdx**2 + dzdy**2)) * 180 / np.pi
    
    # 坡向（度，顺时针，北为0）
    aspect = np.arctan2(-dzdy, dzdx) * 180 / np.pi
    aspect = (90 - aspect) % 360
    
    return slope, aspect


def d8_flow_direction(dem):
    """
    D8流向算法
    
    8个方向编码:
    32  64  128
    16  *   1
    8   4   2
    
    参数:
    ----
    dem : ndarray
        DEM数据
    
    返回:
    ----
    flow_dir : ndarray
        流向编码(0表示汇点/边界)
    """
    ny, nx = dem.shape
    flow_dir = np.zeros((ny, nx), dtype=np.int32)
    
    # 8个方向的偏移
    directions = [
        (0, 1, 1),    # 东: 1
        (1, 1, 2),    # 东南: 2
        (1, 0, 4),    # 南: 4
        (1, -1, 8),   # 西南: 8
        (0, -1, 16),  # 西: 16
        (-1, -1, 32), # 西北: 32
        (-1, 0, 64),  # 北: 64
        (-1, 1, 128)  # 东北: 128
    ]
    
    # 对每个网格计算流向
    for i in range(ny):
        for j in range(nx):
            # 边界设为0
            if i == 0 or i == ny-1 or j == 0 or j == nx-1:
                flow_dir[i, j] = 0
                continue
            
            # 找最陡下降方向
            max_slope = -np.inf
            max_dir = 0
            
            for di, dj, code in directions:
                ni, nj = i + di, j + dj
                if 0 <= ni < ny and 0 <= nj < nx:
                    # 计算坡降
                    distance = np.sqrt(di**2 + dj**2)
                    slope = (dem[i, j] - dem[ni, nj]) / distance
                    
                    if slope > max_slope:
                        max_slope = slope
                        max_dir = code
            
            flow_dir[i, j] = max_dir if max_slope > 0 else 0
    
    return flow_dir


def flow_accumulation(flow_dir):
    """
    汇流累积计算（改进版，从高到低递归）
    
    参数:
    ----
    flow_dir : ndarray
        流向数据
    
    返回:
    ----
    flow_acc : ndarray
        汇流累积值(网格数)
    """
    ny, nx = flow_dir.shape
    flow_acc = np.ones((ny, nx), dtype=np.int32)
    visited = np.zeros((ny, nx), dtype=bool)
    
    # 方向偏移量
    dir_offset = {
        1: (0, 1),    # 东
        2: (1, 1),    # 东南
        4: (1, 0),    # 南
        8: (1, -1),   # 西南
        16: (0, -1),  # 西
        32: (-1, -1), # 西北
        64: (-1, 0),  # 北
        128: (-1, 1)  # 东北
    }
    
    def accumulate(i, j):
        """递归计算汇流累积"""
        if visited[i, j]:
            return flow_acc[i, j]
        
        visited[i, j] = True
        
        if flow_dir[i, j] == 0:
            return flow_acc[i, j]
        
        # 累加所有流向当前网格的上游贡献
        total = 1
        for code, (di, dj) in dir_offset.items():
            ni, nj = i - di, j - dj  # 反向查找上游
            if 0 <= ni < ny and 0 <= nj < nx:
                if flow_dir[ni, nj] == code:  # 上游网格流向当前网格
                    total += accumulate(ni, nj)
        
        flow_acc[i, j] = total
        return total
    
    # 从所有网格开始递归计算
    for i in range(ny):
        for j in range(nx):
            if not visited[i, j]:
                accumulate(i, j)
    
    return flow_acc


def extract_stream_network(flow_acc, threshold=50):
    """
    提取河网
    
    参数:
    ----
    flow_acc : ndarray
        汇流累积
    threshold : float
        河网阈值(网格数)
    
    返回:
    ----
    stream : ndarray, bool
        河网掩膜
    """
    stream = flow_acc >= threshold
    return stream


def identify_outlet(flow_dir, flow_acc):
    """
    识别流域出口
    
    参数:
    ----
    flow_dir : ndarray
        流向
    flow_acc : ndarray
        汇流累积
    
    返回:
    ----
    outlet_i, outlet_j : int
        出口坐标
    """
    # 边界上汇流累积最大的点
    ny, nx = flow_dir.shape
    
    max_acc = -1
    outlet_i, outlet_j = 0, 0
    
    # 检查四条边界
    for i in [0, ny-1]:
        for j in range(nx):
            if flow_acc[i, j] > max_acc:
                max_acc = flow_acc[i, j]
                outlet_i, outlet_j = i, j
    
    for j in [0, nx-1]:
        for i in range(ny):
            if flow_acc[i, j] > max_acc:
                max_acc = flow_acc[i, j]
                outlet_i, outlet_j = i, j
    
    return outlet_i, outlet_j


def plot_dem(dem, dx, dy, save_path=None):
    """
    绘制DEM
    """
    fig, ax = plt.subplots(figsize=(10, 9))
    
    # 创建地形颜色映射
    colors_terrain = ['#2E7D32', '#66BB6A', '#FFEB3B', '#FF9800', '#795548', '#FFFFFF']
    cmap_terrain = LinearSegmentedColormap.from_list('terrain', colors_terrain, N=256)
    
    im = ax.imshow(dem, cmap=cmap_terrain, origin='lower', 
                   extent=[0, dem.shape[1]*dx, 0, dem.shape[0]*dy])
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('高程 (m)', fontsize=12)
    
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.set_title('数字高程模型 (DEM)', fontsize=14, fontweight='bold')
    
    # 添加等高线
    ny, nx = dem.shape
    X = np.arange(nx) * dx
    Y = np.arange(ny) * dy
    X, Y = np.meshgrid(X, Y)
    contours = ax.contour(X, Y, dem, levels=10, colors='black', 
                          alpha=0.3, linewidths=0.5)
    ax.clabel(contours, inline=True, fontsize=8)
    
    # 统计信息
    info_text = f'最小高程: {np.min(dem):.1f} m\n'
    info_text += f'最大高程: {np.max(dem):.1f} m\n'
    info_text += f'平均高程: {np.mean(dem):.1f} m\n'
    info_text += f'高差: {np.max(dem) - np.min(dem):.1f} m'
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()


def plot_slope_aspect(slope, aspect, dx, dy, save_path=None):
    """
    绘制坡度和坡向
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # 坡度
    ax = axes[0]
    im1 = ax.imshow(slope, cmap='YlOrRd', origin='lower',
                    extent=[0, slope.shape[1]*dx, 0, slope.shape[0]*dy])
    cbar1 = plt.colorbar(im1, ax=ax)
    cbar1.set_label('坡度 (°)', fontsize=11)
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.set_title('地形坡度', fontsize=13, fontweight='bold')
    
    # 统计
    info_text = f'平均: {np.mean(slope):.2f}°\n最大: {np.max(slope):.2f}°'
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # 坡向
    ax = axes[1]
    im2 = ax.imshow(aspect, cmap='hsv', origin='lower', vmin=0, vmax=360,
                    extent=[0, aspect.shape[1]*dx, 0, aspect.shape[0]*dy])
    cbar2 = plt.colorbar(im2, ax=ax)
    cbar2.set_label('坡向 (°)', fontsize=11)
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.set_title('地形坡向', fontsize=13, fontweight='bold')
    
    # 添加指北针说明
    info_text = '0° = 北\n90° = 东\n180° = 南\n270° = 西'
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()


def plot_flow_direction(dem, flow_dir, dx, dy, save_path=None):
    """
    绘制流向
    """
    fig, ax = plt.subplots(figsize=(10, 9))
    
    # 背景DEM
    colors_terrain = ['#2E7D32', '#66BB6A', '#FFEB3B', '#FF9800', '#795548']
    cmap_terrain = LinearSegmentedColormap.from_list('terrain', colors_terrain, N=256)
    ax.imshow(dem, cmap=cmap_terrain, origin='lower', alpha=0.5,
              extent=[0, dem.shape[1]*dx, 0, dem.shape[0]*dy])
    
    # 流向箭头（采样显示）
    ny, nx = dem.shape
    step = max(nx // 20, 1)
    
    # 方向向量
    dir_vectors = {
        1: (1, 0),     # 东
        2: (1, -1),    # 东南
        4: (0, -1),    # 南
        8: (-1, -1),   # 西南
        16: (-1, 0),   # 西
        32: (-1, 1),   # 西北
        64: (0, 1),    # 北
        128: (1, 1)    # 东北
    }
    
    for i in range(0, ny, step):
        for j in range(0, nx, step):
            if flow_dir[i, j] in dir_vectors:
                dx_arrow, dy_arrow = dir_vectors[flow_dir[i, j]]
                ax.arrow(j*dx, i*dy, dx_arrow*dx*0.8, dy_arrow*dy*0.8,
                        head_width=dx*0.5, head_length=dx*0.3,
                        fc='blue', ec='blue', alpha=0.6)
    
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.set_title('D8流向分析', fontsize=14, fontweight='bold')
    
    # 添加说明
    info_text = '箭头: 水流方向\n蓝色箭头指向下游'
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()


def plot_flow_accumulation(flow_acc, dx, dy, save_path=None):
    """
    绘制汇流累积
    """
    fig, ax = plt.subplots(figsize=(10, 9))
    
    # 对数尺度显示
    flow_acc_log = np.log10(flow_acc + 1)
    
    im = ax.imshow(flow_acc_log, cmap='Blues', origin='lower',
                   extent=[0, flow_acc.shape[1]*dx, 0, flow_acc.shape[0]*dy])
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('log10(汇流累积+1)', fontsize=11)
    
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.set_title('汇流累积分析', fontsize=14, fontweight='bold')
    
    # 统计
    info_text = f'最小: {np.min(flow_acc):.0f}\n'
    info_text += f'最大: {np.max(flow_acc):.0f}\n'
    info_text += f'平均: {np.mean(flow_acc):.1f}'
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()


def plot_stream_network(dem, stream, outlet_i, outlet_j, dx, dy, save_path=None):
    """
    绘制河网
    """
    fig, ax = plt.subplots(figsize=(10, 9))
    
    # 背景DEM
    colors_terrain = ['#2E7D32', '#66BB6A', '#FFEB3B', '#FF9800', '#795548']
    cmap_terrain = LinearSegmentedColormap.from_list('terrain', colors_terrain, N=256)
    ax.imshow(dem, cmap=cmap_terrain, origin='lower', alpha=0.6,
              extent=[0, dem.shape[1]*dx, 0, dem.shape[0]*dy])
    
    # 河网（蓝色）
    stream_plot = np.where(stream, 1, np.nan)
    ax.imshow(stream_plot, cmap='Blues_r', origin='lower', alpha=0.8,
              extent=[0, dem.shape[1]*dx, 0, dem.shape[0]*dy])
    
    # 出口（红色星号）
    ax.plot(outlet_j*dx, outlet_i*dy, 'r*', markersize=20, 
            markeredgecolor='black', markeredgewidth=2,
            label='流域出口')
    
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.set_title('河网提取结果', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    
    # 统计
    n_stream = np.sum(stream)
    total_cells = stream.size
    stream_ratio = n_stream / total_cells * 100
    
    info_text = f'河网网格数: {n_stream}\n'
    info_text += f'河网密度: {stream_ratio:.2f}%\n'
    info_text += f'出口坐标: ({outlet_i}, {outlet_j})'
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9))
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()


def main():
    """主函数"""
    print("=" * 70)
    print("案例1：DEM分析与河网提取")
    print("=" * 70)
    
    # 创建输出目录
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 生成DEM
    print("\n1. 生成合成DEM数据...")
    dem, dx, dy = generate_synthetic_dem(nx=50, ny=50)
    ny, nx = dem.shape
    print(f"   DEM大小: {ny} × {nx}")
    print(f"   网格分辨率: {dx} m × {dy} m")
    print(f"   高程范围: {np.min(dem):.1f} - {np.max(dem):.1f} m")
    
    # 绘制DEM
    plot_dem(dem, dx, dy, save_path=f'{output_dir}/dem.png')
    
    # 2. 计算坡度和坡向
    print("\n2. 计算地形坡度和坡向...")
    slope, aspect = calculate_slope_aspect(dem, dx, dy)
    print(f"   平均坡度: {np.mean(slope):.2f}°")
    print(f"   最大坡度: {np.max(slope):.2f}°")
    
    # 绘制坡度和坡向
    plot_slope_aspect(slope, aspect, dx, dy, 
                     save_path=f'{output_dir}/slope_aspect.png')
    
    # 3. 计算流向
    print("\n3. 计算D8流向...")
    flow_dir = d8_flow_direction(dem)
    n_valid_flow = np.sum(flow_dir > 0)
    print(f"   有效流向网格数: {n_valid_flow}")
    
    # 绘制流向
    plot_flow_direction(dem, flow_dir, dx, dy,
                       save_path=f'{output_dir}/flow_direction.png')
    
    # 4. 计算汇流累积
    print("\n4. 计算汇流累积...")
    flow_acc = flow_accumulation(flow_dir)
    print(f"   最大汇流累积: {np.max(flow_acc):.0f} 个网格")
    print(f"   平均汇流累积: {np.mean(flow_acc):.1f} 个网格")
    
    # 绘制汇流累积
    plot_flow_accumulation(flow_acc, dx, dy,
                          save_path=f'{output_dir}/flow_accumulation.png')
    
    # 5. 提取河网
    print("\n5. 提取河网...")
    threshold = 20  # 阈值：20个网格
    stream = extract_stream_network(flow_acc, threshold=threshold)
    n_stream = np.sum(stream)
    stream_density = n_stream / (nx * ny) * 100
    print(f"   河网阈值: {threshold} 个网格")
    print(f"   河网网格数: {n_stream}")
    print(f"   河网密度: {stream_density:.2f}%")
    
    # 6. 识别流域出口
    print("\n6. 识别流域出口...")
    outlet_i, outlet_j = identify_outlet(flow_dir, flow_acc)
    print(f"   出口坐标: ({outlet_i}, {outlet_j})")
    print(f"   出口高程: {dem[outlet_i, outlet_j]:.1f} m")
    print(f"   出口汇流累积: {flow_acc[outlet_i, outlet_j]:.0f} 个网格")
    
    # 绘制河网
    plot_stream_network(dem, stream, outlet_i, outlet_j, dx, dy,
                       save_path=f'{output_dir}/stream_network.png')
    
    # 7. 统计输出
    print("\n" + "=" * 70)
    print("DEM分析结果统计")
    print("=" * 70)
    
    print(f"\n【地形特征】")
    print(f"  流域面积: {nx * ny * dx * dy / 1e6:.3f} km²")
    print(f"  最小高程: {np.min(dem):.1f} m")
    print(f"  最大高程: {np.max(dem):.1f} m")
    print(f"  平均高程: {np.mean(dem):.1f} m")
    print(f"  高差: {np.max(dem) - np.min(dem):.1f} m")
    print(f"  平均坡度: {np.mean(slope):.2f}°")
    print(f"  最大坡度: {np.max(slope):.2f}°")
    
    print(f"\n【水系特征】")
    print(f"  河网密度: {stream_density:.2f}%")
    print(f"  河网长度: {n_stream * dx / 1000:.2f} km（近似）")
    print(f"  流域出口: ({outlet_i}, {outlet_j})")
    print(f"  出口高程: {dem[outlet_i, outlet_j]:.1f} m")
    
    print("\n所有图表已保存到 outputs/ 目录")
    print("=" * 70)


if __name__ == '__main__':
    main()
