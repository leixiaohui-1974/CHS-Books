"""
案例11：地表地下水耦合基础

本案例演示地表水和地下水相互作用的基本原理和数值模拟方法。

演示内容：
---------
1. 一维河流-地下水耦合系统
2. 河流边界条件实现
3. 弱耦合迭代求解
4. 河流渗漏分析
5. 耦合强度影响

物理场景：
---------
一维含水层，中央有一条河流穿过：
- 含水层长度：1000m
- 河流位于x=500m处
- 左右边界为定水头边界
- 分析河流对地下水的影响

学习目标：
---------
1. 理解地表地下水交互机制
2. 掌握河流边界条件
3. 实现弱耦合求解方法
4. 分析渗漏通量分布
5. 评估耦合参数影响

作者: gwflow开发团队
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# 导入gwflow模块
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gwflow.coupling import RiverBoundary, compute_exchange_flux
from gwflow.grid import generate_1d_grid
from gwflow.solvers import solve_1d_steady_gw

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def setup_model_parameters():
    """设置模型参数"""
    params = {
        # 含水层参数
        'L': 1000.0,          # 含水层长度 (m)
        'nx': 101,            # 网格数
        'K': 10.0,            # 渗透系数 (m/day)
        'b': 20.0,            # 含水层厚度 (m)
        
        # 边界条件
        'h_left': 25.0,       # 左边界水头 (m)
        'h_right': 25.0,      # 右边界水头 (m)
        
        # 河流参数
        'river_stage': 30.0,        # 河流水位 (m)
        'river_bottom': 20.0,       # 河底高程 (m)
        'river_width': 50.0,        # 河宽 (m)
        'river_bed_K': 1.0,         # 河床渗透系数 (m/day)
        'river_bed_thickness': 2.0, # 河床厚度 (m)
    }
    
    # 计算派生参数
    params['dx'] = params['L'] / (params['nx'] - 1)
    params['x'] = np.linspace(0, params['L'], params['nx'])
    params['T'] = params['K'] * params['b']
    params['river_pos_idx'] = params['nx'] // 2
    
    return params


def solve_no_river_case(params):
    """
    场景1：无河流补给的基准情况
    """
    print("\n" + "="*60)
    print("场景1：无河流补给（基准情况）")
    print("="*60)
    
    # 稳态求解
    result = solve_1d_steady_gw(
        K=params['K'],
        b=params['b'],
        L=params['L'],
        nx=params['nx'],
        bc_left=('dirichlet', params['h_left']),
        bc_right=('dirichlet', params['h_right']),
        recharge=0.0
    )
    
    h = result['head']
    
    print(f"最大水头: {np.max(h):.2f} m")
    print(f"最小水头: {np.min(h):.2f} m")
    print(f"平均水头: {np.mean(h):.2f} m")
    
    return h


def solve_with_river_standard(params):
    """
    场景2：标准河流边界条件
    """
    print("\n" + "="*60)
    print("场景2：河流补给（标准边界）")
    print("="*60)
    
    # 创建河流边界
    river = RiverBoundary(
        river_stage=params['river_stage'],
        river_bottom=params['river_bottom'],
        river_bed_K=params['river_bed_K'],
        river_bed_thickness=params['river_bed_thickness'],
        river_width=params['river_width'],
        river_length=params['dx']
    )
    
    print(f"\n河流参数:")
    print(f"  水位: {river.river_stage:.2f} m")
    print(f"  河底: {river.river_bottom:.2f} m")
    print(f"  传导度: {river.conductance:.2e} m²/day")
    print(f"  渗漏系数: {river.leakance:.3f} 1/day")
    
    # 弱耦合迭代求解
    h = params['h_left'] * np.ones(params['nx'])
    Q_river = np.zeros(params['nx'])
    
    max_iter = 50
    tol = 1e-6
    convergence = []
    
    print(f"\n开始弱耦合迭代...")
    print(f"最大迭代次数: {max_iter}")
    print(f"收敛容差: {tol} m")
    
    for iter_num in range(max_iter):
        h_old = h.copy()
        
        # 计算河流渗漏
        flux = river.compute_flux(h[params['river_pos_idx']], method='standard')
        
        # 转换为源汇项 (1/day)
        # Q = flux (m³/day) / V (m³) = flux / (dx * width * b)
        cell_volume = params['dx'] * params['river_width'] * params['b']
        Q_river[params['river_pos_idx']] = flux / cell_volume
        
        # 求解地下水
        result = solve_1d_steady_gw(
            K=params['K'],
            b=params['b'],
            L=params['L'],
            nx=params['nx'],
            bc_left=('dirichlet', params['h_left']),
            bc_right=('dirichlet', params['h_right']),
            source=Q_river
        )
        h = result['head']
        
        # 检查收敛
        error = np.max(np.abs(h - h_old))
        convergence.append(error)
        
        if error < tol:
            print(f"收敛! 迭代次数: {iter_num + 1}")
            print(f"最终误差: {error:.2e} m")
            break
        
        if iter_num == max_iter - 1:
            print(f"警告: 达到最大迭代次数，误差: {error:.2e} m")
    
    # 最终结果
    final_flux = river.compute_flux(h[params['river_pos_idx']], method='standard')
    
    print(f"\n最终结果:")
    print(f"  河流渗漏量: {final_flux:.2f} m³/day")
    print(f"  河流处水头: {h[params['river_pos_idx']]:.2f} m")
    print(f"  最大水头: {np.max(h):.2f} m")
    print(f"  水头增幅: {np.max(h) - params['h_left']:.2f} m")
    
    return h, final_flux, convergence, river


def solve_with_river_disconnected(params):
    """
    场景3：考虑断开机制的河流边界
    """
    print("\n" + "="*60)
    print("场景3：河流断开机制")
    print("="*60)
    
    # 创建河流边界（较高的河床）
    river = RiverBoundary(
        river_stage=params['river_stage'],
        river_bottom=28.0,  # 提高河底高程
        river_bed_K=params['river_bed_K'],
        river_bed_thickness=params['river_bed_thickness'],
        river_width=params['river_width'],
        river_length=params['dx']
    )
    
    print(f"\n河流参数（高河床）:")
    print(f"  水位: {river.river_stage:.2f} m")
    print(f"  河底: {river.river_bottom:.2f} m")
    print(f"  河流深度: {river.river_stage - river.river_bottom:.2f} m")
    
    # 弱耦合迭代
    h = params['h_left'] * np.ones(params['nx'])
    Q_river = np.zeros(params['nx'])
    
    for iter_num in range(50):
        h_old = h.copy()
        
        # 使用断开机制
        flux = river.compute_flux(h[params['river_pos_idx']], method='disconnected')
        
        cell_volume = params['dx'] * params['river_width'] * params['b']
        Q_river[params['river_pos_idx']] = flux / cell_volume
        
        result = solve_1d_steady_gw(
            K=params['K'],
            b=params['b'],
            L=params['L'],
            nx=params['nx'],
            bc_left=('dirichlet', params['h_left']),
            bc_right=('dirichlet', params['h_right']),
            source=Q_river
        )
        h = result['head']
        
        if np.max(np.abs(h - h_old)) < 1e-6:
            print(f"收敛! 迭代次数: {iter_num + 1}")
            break
    
    final_flux = river.compute_flux(h[params['river_pos_idx']], method='disconnected')
    
    print(f"\n最终结果:")
    print(f"  河流渗漏量: {final_flux:.2f} m³/day")
    print(f"  河流处水头: {h[params['river_pos_idx']]:.2f} m")
    print(f"  断开状态: {'是' if h[params['river_pos_idx']] < river.river_bottom else '否'}")
    
    return h, final_flux, river


def analyze_conductance_sensitivity(params):
    """
    场景4：水力传导度敏感性分析
    """
    print("\n" + "="*60)
    print("场景4：水力传导度敏感性分析")
    print("="*60)
    
    # 不同的河床渗透系数
    K_bed_values = np.array([0.1, 0.5, 1.0, 2.0, 5.0])
    
    results = []
    
    for K_bed in K_bed_values:
        river = RiverBoundary(
            river_stage=params['river_stage'],
            river_bottom=params['river_bottom'],
            river_bed_K=K_bed,
            river_bed_thickness=params['river_bed_thickness'],
            river_width=params['river_width'],
            river_length=params['dx']
        )
        
        # 快速迭代求解
        h = params['h_left'] * np.ones(params['nx'])
        Q_river = np.zeros(params['nx'])
        
        for _ in range(50):
            h_old = h.copy()
            flux = river.compute_flux(h[params['river_pos_idx']])
            cell_volume = params['dx'] * params['river_width'] * params['b']
            Q_river[params['river_pos_idx']] = flux / cell_volume
            
            result = solve_1d_steady_gw(
                K=params['K'],
                b=params['b'],
                L=params['L'],
                nx=params['nx'],
                bc_left=('dirichlet', params['h_left']),
                bc_right=('dirichlet', params['h_right']),
                source=Q_river
            )
            h = result['head']
            
            if np.max(np.abs(h - h_old)) < 1e-6:
                break
        
        final_flux = river.compute_flux(h[params['river_pos_idx']])
        
        results.append({
            'K_bed': K_bed,
            'conductance': river.conductance,
            'head': h.copy(),
            'flux': final_flux,
            'max_head': np.max(h)
        })
        
        print(f"K_bed = {K_bed:.1f} m/day: "
              f"C = {river.conductance:.2e} m²/day, "
              f"Q = {final_flux:.2f} m³/day, "
              f"h_max = {np.max(h):.2f} m")
    
    return results


def plot_results(params, h_no_river, h_with_river, h_disconnected, 
                 convergence, sensitivity_results):
    """绘制所有结果"""
    
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    x = params['x']
    river_pos = params['river_pos_idx']
    
    # 图1: 水头分布对比
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(x, h_no_river, 'b-', linewidth=2, label='无河流')
    ax1.plot(x, h_with_river, 'r-', linewidth=2, label='标准河流')
    ax1.plot(x, h_disconnected, 'g--', linewidth=2, label='断开机制')
    ax1.axvline(x[river_pos], color='gray', linestyle=':', alpha=0.5, label='河流位置')
    ax1.axhline(params['river_stage'], color='cyan', linestyle='--', alpha=0.5, label='河流水位')
    ax1.set_xlabel('距离 (m)', fontsize=12)
    ax1.set_ylabel('水头 (m)', fontsize=12)
    ax1.set_title('水头分布对比', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 图2: 河流影响范围
    ax2 = fig.add_subplot(gs[0, 1])
    head_increase = h_with_river - h_no_river
    ax2.fill_between(x, 0, head_increase, alpha=0.3, color='blue')
    ax2.plot(x, head_increase, 'b-', linewidth=2)
    ax2.axvline(x[river_pos], color='red', linestyle='--', label='河流位置')
    ax2.set_xlabel('距离 (m)', fontsize=12)
    ax2.set_ylabel('水头增量 (m)', fontsize=12)
    ax2.set_title('河流补给引起的水头增量', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 图3: 收敛历史
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.semilogy(range(1, len(convergence)+1), convergence, 'o-', linewidth=2, markersize=6)
    ax3.axhline(1e-6, color='r', linestyle='--', label='收敛容差')
    ax3.set_xlabel('迭代次数', fontsize=12)
    ax3.set_ylabel('最大误差 (m)', fontsize=12)
    ax3.set_title('弱耦合迭代收敛历史', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # 图4: 传导度敏感性（水头）
    ax4 = fig.add_subplot(gs[1, 1])
    for i, res in enumerate(sensitivity_results):
        ax4.plot(x, res['head'], linewidth=2, 
                label=f"K_bed={res['K_bed']:.1f} m/day")
    ax4.axvline(x[river_pos], color='gray', linestyle=':', alpha=0.5)
    ax4.set_xlabel('距离 (m)', fontsize=12)
    ax4.set_ylabel('水头 (m)', fontsize=12)
    ax4.set_title('不同河床渗透系数下的水头分布', fontsize=14, fontweight='bold')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    
    # 图5: 传导度敏感性（通量和水头）
    ax5 = fig.add_subplot(gs[2, 0])
    K_bed_vals = [res['K_bed'] for res in sensitivity_results]
    fluxes = [res['flux'] for res in sensitivity_results]
    ax5.plot(K_bed_vals, fluxes, 'bo-', linewidth=2, markersize=8)
    ax5.set_xlabel('河床渗透系数 (m/day)', fontsize=12)
    ax5.set_ylabel('河流渗漏量 (m³/day)', fontsize=12)
    ax5.set_title('渗漏量 vs 河床渗透系数', fontsize=14, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # 图6: 最大水头 vs 传导度
    ax6 = fig.add_subplot(gs[2, 1])
    max_heads = [res['max_head'] for res in sensitivity_results]
    ax6.plot(K_bed_vals, max_heads, 'ro-', linewidth=2, markersize=8)
    ax6.axhline(params['river_stage'], color='cyan', linestyle='--', 
                alpha=0.5, label='河流水位')
    ax6.set_xlabel('河床渗透系数 (m/day)', fontsize=12)
    ax6.set_ylabel('最大水头 (m)', fontsize=12)
    ax6.set_title('最大水头 vs 河床渗透系数', fontsize=14, fontweight='bold')
    ax6.legend(fontsize=10)
    ax6.grid(True, alpha=0.3)
    
    plt.savefig('case_11_coupling_basic_results.png', dpi=300, bbox_inches='tight')
    print("\n图片已保存: case_11_coupling_basic_results.png")
    
    plt.show()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("案例11：地表地下水耦合基础")
    print("="*60)
    print("\n本案例演示河流-地下水相互作用的基本原理")
    print("包括：弱耦合求解、断开机制、敏感性分析")
    
    # 1. 设置参数
    params = setup_model_parameters()
    
    print(f"\n模型参数:")
    print(f"  含水层长度: {params['L']} m")
    print(f"  网格数: {params['nx']}")
    print(f"  渗透系数: {params['K']} m/day")
    print(f"  含水层厚度: {params['b']} m")
    print(f"  导水系数: {params['T']} m²/day")
    
    # 2. 场景1：无河流
    h_no_river = solve_no_river_case(params)
    
    # 3. 场景2：标准河流边界
    h_with_river, flux_standard, convergence, river_std = solve_with_river_standard(params)
    
    # 4. 场景3：断开机制
    h_disconnected, flux_disconnected, river_disc = solve_with_river_disconnected(params)
    
    # 5. 场景4：敏感性分析
    sensitivity_results = analyze_conductance_sensitivity(params)
    
    # 6. 绘制结果
    plot_results(params, h_no_river, h_with_river, h_disconnected,
                 convergence, sensitivity_results)
    
    # 7. 总结
    print("\n" + "="*60)
    print("案例11完成总结")
    print("="*60)
    print(f"\n核心发现:")
    print(f"1. 河流补给使水头增加 {np.max(h_with_river) - params['h_left']:.2f} m")
    print(f"2. 标准渗漏量: {flux_standard:.2f} m³/day")
    print(f"3. 断开机制渗漏量: {flux_disconnected:.2f} m³/day")
    print(f"4. 渗漏量随河床渗透系数线性增加")
    print(f"5. 弱耦合方法{len(convergence)}次迭代达到收敛")
    
    print(f"\n学习要点:")
    print(f"✓ 地表地下水交互机制")
    print(f"✓ 河流边界条件实现")
    print(f"✓ 弱耦合迭代求解")
    print(f"✓ 断开机制的物理意义")
    print(f"✓ 传导度参数的影响")
    
    print("\n✅ 案例11执行完成！")


if __name__ == '__main__':
    main()
