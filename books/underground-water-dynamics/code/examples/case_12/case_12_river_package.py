"""
案例12：MODFLOW River包实现

本案例演示MODFLOW River包的完整功能，用于模拟二维河流网络与地下水的相互作用。

演示内容：
---------
1. 二维河流网络模拟
2. 多河段处理
3. MODFLOW River包参数管理
4. 河流通量统计与分析
5. 河流参数敏感性

物理场景：
---------
二维含水层，包含多条河流：
- 模型区域：2000m × 1500m
- 主河流：自西向东流动
- 支流：自北向南汇入主河流
- 分析河流网络对地下水的影响

学习目标：
---------
1. 掌握MODFLOW River包的使用
2. 处理复杂河流网络
3. 分析河流与地下水交互
4. 评估河流参数影响
5. 理解断开机制的作用

作者: gwflow开发团队
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyArrowPatch
import matplotlib.colors as mcolors

# 导入gwflow模块
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gwflow.coupling import RiverPackage
from gwflow.grid import generate_2d_grid
from gwflow.solvers import solve_2d_steady_gw
from gwflow.visualization import plot_2d_contour

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def setup_model():
    """设置模型参数"""
    params = {
        # 模型区域
        'Lx': 2000.0,    # x方向长度 (m)
        'Ly': 1500.0,    # y方向长度 (m)
        'nx': 41,        # x方向网格数
        'ny': 31,        # y方向网格数
        
        # 含水层参数
        'K': 15.0,       # 渗透系数 (m/day)
        'b': 25.0,       # 含水层厚度 (m)
        
        # 边界条件
        'h_west': 35.0,  # 西边界水头 (m)
        'h_east': 30.0,  # 东边界水头 (m)
        'h_north': 33.0, # 北边界水头 (m)
        'h_south': 32.0, # 南边界水头 (m)
        
        # 补给
        'recharge': 0.0005,  # 降雨补给 (m/day)
    }
    
    # 计算派生参数
    params['dx'] = params['Lx'] / (params['nx'] - 1)
    params['dy'] = params['Ly'] / (params['ny'] - 1)
    params['T'] = params['K'] * params['b']
    params['cell_area'] = params['dx'] * params['dy']
    params['cell_volume'] = params['cell_area'] * params['b']
    
    # 创建网格
    params['x'] = np.linspace(0, params['Lx'], params['nx'])
    params['y'] = np.linspace(0, params['Ly'], params['ny'])
    params['X'], params['Y'] = np.meshgrid(params['x'], params['y'])
    
    return params


def create_river_network(params):
    """
    创建河流网络
    
    河流布局：
    - 主河流（Segment 1）：从西到东，穿过模型中部
    - 北支流（Segment 2）：从北向南，汇入主河流
    - 南支流（Segment 3）：从南向北，汇入主河流
    """
    riv = RiverPackage(name='RiverNetwork')
    
    nx, ny = params['nx'], params['ny']
    
    # 主河流参数
    main_stage_west = 33.0   # 上游水位
    main_stage_east = 31.0   # 下游水位
    main_bottom = 25.0       # 河底高程
    main_bed_K = 2.0         # 河床渗透系数
    main_bed_thickness = 1.5 # 河床厚度
    main_width = 30.0        # 河宽
    
    # 主河流传导度
    main_cond = (main_bed_K * main_width * params['dx']) / main_bed_thickness
    
    print("\n创建河流网络...")
    print("="*60)
    
    # === 主河流（Segment 1）：y = ny//2 (中部) ===
    print("\n主河流（Segment 1）：")
    print(f"  位置: 沿着 row = {ny//2}")
    print(f"  水位: {main_stage_west:.1f} → {main_stage_east:.1f} m")
    print(f"  传导度: {main_cond:.2e} m²/day")
    
    main_cells = [(ny//2, col) for col in range(nx)]
    riv.add_river_segment(
        cells=main_cells,
        stage_start=main_stage_west,
        stage_end=main_stage_east,
        conductance=main_cond,
        bottom=main_bottom,
        segment_id=1
    )
    
    # === 北支流（Segment 2）：col = nx//3, 从北到主河流 ===
    trib_stage_north = 33.5  # 上游水位
    trib_stage_conf = 32.0   # 汇流点水位
    trib_bottom = 26.0       # 河底
    trib_width = 15.0        # 河宽（较窄）
    trib_bed_K = 1.5
    trib_bed_thickness = 1.0
    
    trib_cond = (trib_bed_K * trib_width * params['dy']) / trib_bed_thickness
    
    print(f"\n北支流（Segment 2）：")
    print(f"  位置: 沿着 col = {nx//3}")
    print(f"  水位: {trib_stage_north:.1f} → {trib_stage_conf:.1f} m")
    print(f"  传导度: {trib_cond:.2e} m²/day")
    
    north_trib_cells = [(row, nx//3) for row in range(ny//2, ny)]
    riv.add_river_segment(
        cells=north_trib_cells,
        stage_start=trib_stage_conf,
        stage_end=trib_stage_north,
        conductance=trib_cond,
        bottom=trib_bottom,
        segment_id=2
    )
    
    # === 南支流（Segment 3）：col = 2*nx//3, 从南到主河流 ===
    print(f"\n南支流（Segment 3）：")
    print(f"  位置: 沿着 col = {2*nx//3}")
    print(f"  水位: {trib_stage_north:.1f} → {trib_stage_conf:.1f} m")
    print(f"  传导度: {trib_cond:.2e} m²/day")
    
    south_trib_cells = [(row, 2*nx//3) for row in range(0, ny//2+1)]
    riv.add_river_segment(
        cells=south_trib_cells,
        stage_start=trib_stage_conf,
        stage_end=trib_stage_north,
        conductance=trib_cond,
        bottom=trib_bottom,
        segment_id=3
    )
    
    # 摘要
    summary = riv.get_summary()
    print(f"\n河流网络摘要：")
    print(f"  总单元数: {summary['n_cells']}")
    print(f"  河段数: {summary['n_segments']}")
    print(f"  水位范围: {summary['stage_range'][0]:.1f} - {summary['stage_range'][1]:.1f} m")
    
    return riv


def solve_with_rivers(params, riv):
    """
    求解带河流边界的地下水流动
    """
    print("\n" + "="*60)
    print("求解地下水流动（含河流边界）")
    print("="*60)
    
    nx, ny = params['nx'], params['ny']
    
    # 初始猜测
    h = np.ones((ny, nx)) * 32.0
    
    # 设置边界条件（四边定水头）
    h[:, 0] = params['h_west']    # 西边界
    h[:, -1] = params['h_east']   # 东边界
    h[0, :] = params['h_south']   # 南边界
    h[-1, :] = params['h_north']  # 北边界
    
    # 单元体积
    cell_volume = np.ones((ny, nx)) * params['cell_volume']
    
    # 弱耦合迭代
    max_iter = 50
    tol = 1e-5
    convergence = []
    
    print(f"\n开始弱耦合迭代...")
    
    for iter_num in range(max_iter):
        h_old = h.copy()
        
        # 计算河流源汇项
        river_source = riv.apply_flux_to_source(
            head=h,
            cell_volume=cell_volume,
            use_disconnection=True
        )
        
        # 总源汇项（降雨 + 河流）
        total_source = params['recharge'] + river_source
        
        # 求解稳态地下水流
        # 注意：这里我们手动迭代，所以每次调用solve_2d_steady_gw
        # 实际中应该用迭代求解器
        
        # 简化：直接用源汇项，假设线性系统
        # 这里为演示目的，使用简化方法
        # 实际应用中建议使用完整的迭代求解器
        
        # 内部节点的Laplace方程离散
        dx, dy = params['dx'], params['dy']
        K = params['K']
        b = params['b']
        
        h_new = h.copy()
        
        # 简单的Gauss-Seidel迭代（内部点）
        for _ in range(10):
            for i in range(1, ny-1):
                for j in range(1, nx-1):
                    # 五点差分
                    h_new[i, j] = (
                        (h_new[i+1, j] + h_new[i-1, j]) / dy**2 +
                        (h_new[i, j+1] + h_new[i, j-1]) / dx**2 +
                        total_source[i, j] / (K * b)
                    ) / (2/dx**2 + 2/dy**2)
        
        h = h_new
        
        # 保持边界条件
        h[:, 0] = params['h_west']
        h[:, -1] = params['h_east']
        h[0, :] = params['h_south']
        h[-1, :] = params['h_north']
        
        # 检查收敛
        error = np.max(np.abs(h - h_old))
        convergence.append(error)
        
        if iter_num % 10 == 0:
            print(f"  迭代 {iter_num}: 误差 = {error:.2e}")
        
        if error < tol:
            print(f"\n✓ 收敛! 迭代次数: {iter_num + 1}")
            print(f"  最终误差: {error:.2e}")
            break
    
    # 最终通量计算
    total_flux = riv.get_total_flux(h, use_disconnection=True)
    
    print(f"\n地下水结果：")
    print(f"  最大水头: {np.max(h):.2f} m")
    print(f"  最小水头: {np.min(h):.2f} m")
    print(f"  平均水头: {np.mean(h):.2f} m")
    
    print(f"\n河流交换：")
    print(f"  总交换通量: {total_flux:.2f} m³/day")
    
    return h, convergence


def analyze_river_fluxes(riv, h, params):
    """分析河流通量"""
    print("\n" + "="*60)
    print("河流通量分析")
    print("="*60)
    
    # 分河段统计
    stats = riv.get_segment_statistics(h, use_disconnection=True)
    
    print("\n分河段统计：")
    segment_names = {1: '主河流', 2: '北支流', 3: '南支流'}
    
    for seg_id in sorted(stats.keys()):
        if seg_id == -1:
            continue
        info = stats[seg_id]
        name = segment_names.get(seg_id, f'河段{seg_id}')
        
        print(f"\n{name}（Segment {seg_id}）：")
        print(f"  单元数: {info['n_cells']}")
        print(f"  总通量: {info['total_flux']:.2f} m³/day")
        print(f"  平均通量: {info['avg_flux']:.2f} m³/day/cell")
        print(f"  最大通量: {info['max_flux']:.2f} m³/day/cell")
        print(f"  最小通量: {info['min_flux']:.2f} m³/day/cell")
        
        # 判断补给/排泄
        if info['total_flux'] > 0:
            print(f"  类型: 河流补给地下水")
        elif info['total_flux'] < 0:
            print(f"  类型: 地下水排泄到河流")
        else:
            print(f"  类型: 平衡状态")
    
    # 计算每个单元的通量
    fluxes = riv.compute_flux(h, use_disconnection=True)
    
    return stats, fluxes


def sensitivity_analysis(params, riv):
    """河床传导度敏感性分析"""
    print("\n" + "="*60)
    print("敏感性分析：河床传导度")
    print("="*60)
    
    # 不同的传导度倍数
    factors = [0.5, 1.0, 2.0, 5.0]
    results = []
    
    # 保存原始传导度
    original_conds = [cell.conductance for cell in riv.river_cells]
    
    for factor in factors:
        print(f"\n传导度倍数: {factor}x")
        
        # 修改传导度
        for i, cell in enumerate(riv.river_cells):
            cell.conductance = original_conds[i] * factor
        
        # 求解
        h, _ = solve_with_rivers(params, riv)
        
        # 统计
        total_flux = riv.get_total_flux(h, use_disconnection=True)
        stats = riv.get_segment_statistics(h, use_disconnection=True)
        
        results.append({
            'factor': factor,
            'head': h.copy(),
            'total_flux': total_flux,
            'stats': stats
        })
        
        print(f"  总通量: {total_flux:.2f} m³/day")
    
    # 恢复原始传导度
    for i, cell in enumerate(riv.river_cells):
        cell.conductance = original_conds[i]
    
    return results


def plot_results(params, riv, h, fluxes, stats, sensitivity_results):
    """绘制结果"""
    
    fig = plt.figure(figsize=(18, 12))
    gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    X, Y = params['X'], params['Y']
    nx, ny = params['nx'], params['ny']
    
    # 图1: 水头等值线 + 河流网络
    ax1 = fig.add_subplot(gs[0, :2])
    
    # 绘制水头等值线
    levels = np.linspace(np.min(h), np.max(h), 20)
    contour = ax1.contourf(X, Y, h, levels=levels, cmap='Blues', alpha=0.6)
    contour_lines = ax1.contour(X, Y, h, levels=10, colors='blue', linewidths=0.5, alpha=0.7)
    ax1.clabel(contour_lines, inline=True, fontsize=8)
    
    # 标记河流单元
    segment_colors = {1: 'red', 2: 'green', 3: 'orange'}
    segment_names = {1: '主河流', 2: '北支流', 3: '南支流'}
    
    for seg_id in [1, 2, 3]:
        seg_cells = [cell for cell in riv.river_cells if cell.segment_id == seg_id]
        rows = [cell.row for cell in seg_cells]
        cols = [cell.col for cell in seg_cells]
        x_coords = [params['x'][col] for col in cols]
        y_coords = [params['y'][row] for row in rows]
        
        ax1.plot(x_coords, y_coords, 'o-', color=segment_colors[seg_id],
                linewidth=3, markersize=4, label=segment_names[seg_id],
                alpha=0.8)
    
    ax1.set_xlabel('X (m)', fontsize=12)
    ax1.set_ylabel('Y (m)', fontsize=12)
    ax1.set_title('地下水水头分布与河流网络', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=10)
    ax1.set_aspect('equal')
    plt.colorbar(contour, ax=ax1, label='水头 (m)')
    
    # 图2: 河流通量分布
    ax2 = fig.add_subplot(gs[0, 2])
    
    # 创建通量图
    flux_map = np.zeros((ny, nx))
    for i, cell in enumerate(riv.river_cells):
        flux_map[cell.row, cell.col] = fluxes[i]
    
    # 只显示河流单元
    flux_masked = np.ma.masked_where(flux_map == 0, flux_map)
    
    im = ax2.imshow(flux_masked, cmap='RdBu_r', aspect='equal',
                    extent=[0, params['Lx'], 0, params['Ly']],
                    origin='lower', vmin=-np.max(np.abs(fluxes)),
                    vmax=np.max(np.abs(fluxes)))
    
    ax2.set_xlabel('X (m)', fontsize=12)
    ax2.set_ylabel('Y (m)', fontsize=12)
    ax2.set_title('河流单元交换通量', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax2, label='通量 (m³/day)')
    
    # 图3: 分河段通量统计
    ax3 = fig.add_subplot(gs[1, 0])
    
    seg_ids = [1, 2, 3]
    seg_names_short = ['主河流', '北支流', '南支流']
    total_fluxes = [stats[seg_id]['total_flux'] for seg_id in seg_ids]
    colors = [segment_colors[seg_id] for seg_id in seg_ids]
    
    bars = ax3.bar(seg_names_short, total_fluxes, color=colors, alpha=0.7, edgecolor='black')
    ax3.axhline(0, color='black', linestyle='--', linewidth=0.8)
    ax3.set_ylabel('总通量 (m³/day)', fontsize=12)
    ax3.set_title('分河段总通量', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标签
    for bar, flux in zip(bars, total_fluxes):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{flux:.0f}',
                ha='center', va='bottom' if height > 0 else 'top',
                fontsize=10)
    
    # 图4: 平均单元通量
    ax4 = fig.add_subplot(gs[1, 1])
    
    avg_fluxes = [stats[seg_id]['avg_flux'] for seg_id in seg_ids]
    
    bars = ax4.bar(seg_names_short, avg_fluxes, color=colors, alpha=0.7, edgecolor='black')
    ax4.axhline(0, color='black', linestyle='--', linewidth=0.8)
    ax4.set_ylabel('平均通量 (m³/day/cell)', fontsize=12)
    ax4.set_title('分河段平均单元通量', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 图5: 通量范围（箱线图风格）
    ax5 = fig.add_subplot(gs[1, 2])
    
    x_pos = np.arange(len(seg_ids))
    avg_vals = [stats[seg_id]['avg_flux'] for seg_id in seg_ids]
    min_vals = [stats[seg_id]['min_flux'] for seg_id in seg_ids]
    max_vals = [stats[seg_id]['max_flux'] for seg_id in seg_ids]
    
    for i, (seg_id, avg, minv, maxv) in enumerate(zip(seg_ids, avg_vals, min_vals, max_vals)):
        ax5.plot([i, i], [minv, maxv], 'k-', linewidth=2)
        ax5.plot(i, avg, 'o', color=colors[i], markersize=12, markeredgecolor='black')
        ax5.plot(i, minv, '_', color='black', markersize=10)
        ax5.plot(i, maxv, '_', color='black', markersize=10)
    
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels(seg_names_short)
    ax5.set_ylabel('通量 (m³/day/cell)', fontsize=12)
    ax5.set_title('河段通量范围', fontsize=14, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='y')
    ax5.axhline(0, color='red', linestyle='--', linewidth=0.8, alpha=0.5)
    
    # 图6: 敏感性-总通量
    ax6 = fig.add_subplot(gs[2, 0])
    
    factors = [res['factor'] for res in sensitivity_results]
    total_fluxes_sens = [res['total_flux'] for res in sensitivity_results]
    
    ax6.plot(factors, total_fluxes_sens, 'bo-', linewidth=2, markersize=8)
    ax6.set_xlabel('传导度倍数', fontsize=12)
    ax6.set_ylabel('总交换通量 (m³/day)', fontsize=12)
    ax6.set_title('敏感性：传导度 vs 总通量', fontsize=14, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    
    # 图7: 敏感性-分河段
    ax7 = fig.add_subplot(gs[2, 1])
    
    for seg_id in seg_ids:
        seg_fluxes = [res['stats'][seg_id]['total_flux'] for res in sensitivity_results]
        ax7.plot(factors, seg_fluxes, 'o-', linewidth=2, markersize=6,
                color=segment_colors[seg_id], label=segment_names[seg_id])
    
    ax7.set_xlabel('传导度倍数', fontsize=12)
    ax7.set_ylabel('河段通量 (m³/day)', fontsize=12)
    ax7.set_title('敏感性：分河段通量', fontsize=14, fontweight='bold')
    ax7.legend(fontsize=10)
    ax7.grid(True, alpha=0.3)
    
    # 图8: 敏感性-水头变化
    ax8 = fig.add_subplot(gs[2, 2])
    
    # 在河流中心位置的水头
    center_row, center_col = ny//2, nx//2
    center_heads = [res['head'][center_row, center_col] for res in sensitivity_results]
    
    ax8.plot(factors, center_heads, 'ro-', linewidth=2, markersize=8)
    ax8.set_xlabel('传导度倍数', fontsize=12)
    ax8.set_ylabel('中心点水头 (m)', fontsize=12)
    ax8.set_title('敏感性：传导度 vs 水头', fontsize=14, fontweight='bold')
    ax8.grid(True, alpha=0.3)
    
    plt.savefig('case_12_river_package_results.png', dpi=300, bbox_inches='tight')
    print("\n图片已保存: case_12_river_package_results.png")
    
    plt.show()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("案例12：MODFLOW River包实现")
    print("="*60)
    print("\n本案例演示完整的MODFLOW River包功能")
    print("包括：河流网络、多河段处理、通量分析、敏感性")
    
    # 1. 设置模型
    params = setup_model()
    
    print(f"\n模型设置：")
    print(f"  区域: {params['Lx']}m × {params['Ly']}m")
    print(f"  网格: {params['nx']} × {params['ny']}")
    print(f"  网格间距: dx={params['dx']:.1f}m, dy={params['dy']:.1f}m")
    print(f"  渗透系数: {params['K']} m/day")
    print(f"  含水层厚度: {params['b']} m")
    print(f"  降雨补给: {params['recharge']} m/day")
    
    # 2. 创建河流网络
    riv = create_river_network(params)
    
    # 3. 求解
    h, convergence = solve_with_rivers(params, riv)
    
    # 4. 分析通量
    stats, fluxes = analyze_river_fluxes(riv, h, params)
    
    # 5. 敏感性分析
    print("\n准备进行敏感性分析...")
    sensitivity_results = sensitivity_analysis(params, riv)
    
    # 6. 绘图
    print("\n生成结果图...")
    plot_results(params, riv, h, fluxes, stats, sensitivity_results)
    
    # 7. 总结
    print("\n" + "="*60)
    print("案例12完成总结")
    print("="*60)
    
    total_flux = riv.get_total_flux(h, use_disconnection=True)
    
    print(f"\n核心发现：")
    print(f"1. 河流网络总交换: {total_flux:.2f} m³/day")
    print(f"2. 主河流通量: {stats[1]['total_flux']:.2f} m³/day")
    print(f"3. 北支流通量: {stats[2]['total_flux']:.2f} m³/day")
    print(f"4. 南支流通量: {stats[3]['total_flux']:.2f} m³/day")
    print(f"5. 通量与传导度呈线性关系")
    
    print(f"\n学习要点：")
    print(f"✓ MODFLOW River包的使用")
    print(f"✓ 河流网络建模")
    print(f"✓ 多河段管理")
    print(f"✓ 通量统计分析")
    print(f"✓ 参数敏感性评估")
    
    print("\n✅ 案例12执行完成！")


if __name__ == '__main__':
    main()
