"""
案例13：渗漏与越流模拟

本案例演示多层含水层系统中的垂向越流模拟。

演示内容：
---------
1. 三层含水层系统建模
2. 越流通量计算
3. 多层稳态求解
4. Hantush-Jacob解析解
5. 渗漏因子分析

物理场景：
---------
三层承压含水层系统：
- 第1层：浅层含水层（较薄，K较小）
- 弱透水层1：分隔层
- 第2层：中层含水层（较厚，K较大）
- 弱透水层2：分隔层  
- 第3层：深层含水层（厚，K大）

学习目标：
---------
1. 理解越流机制
2. 建立多层系统模型
3. 计算层间水量交换
4. 分析渗漏因子影响
5. 验证解析解

作者: gwflow开发团队
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d import Axes3D

# 导入gwflow模块
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gwflow.coupling import (
    MultiLayerSystem,
    compute_steady_leakage_1d,
    hantush_jacob_solution,
    estimate_leakage_factor
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def setup_three_layer_system():
    """设置三层含水层系统"""
    
    system = MultiLayerSystem(name='ThreeLayerSystem')
    
    print("\n" + "="*60)
    print("创建三层含水层系统")
    print("="*60)
    
    # 第1层：浅层含水层
    print("\n第1层（浅层含水层）：")
    print("  顶板高程: 100 m")
    print("  底板高程: 80 m")
    print("  厚度: 20 m")
    print("  水平渗透系数: 15 m/day")
    print("  储水系数: 0.0002")
    
    system.add_aquifer_layer(
        layer_id=0,
        top_elevation=100.0,
        bottom_elevation=80.0,
        K_horizontal=15.0,
        storage=0.0002,
        is_confined=True
    )
    
    # 弱透水层1
    print("\n弱透水层1：")
    print("  顶板高程: 80 m")
    print("  底板高程: 75 m")
    print("  厚度: 5 m")
    print("  垂向渗透系数: 0.01 m/day")
    print("  渗漏系数: 0.002 1/day")
    
    system.add_aquitard_layer(
        top_elevation=80.0,
        bottom_elevation=75.0,
        K_vertical=0.01
    )
    
    # 第2层：中层含水层（主力含水层）
    print("\n第2层（中层含水层）：")
    print("  顶板高程: 75 m")
    print("  底板高程: 45 m")
    print("  厚度: 30 m")
    print("  水平渗透系数: 25 m/day")
    print("  储水系数: 0.0001")
    
    system.add_aquifer_layer(
        layer_id=1,
        top_elevation=75.0,
        bottom_elevation=45.0,
        K_horizontal=25.0,
        storage=0.0001,
        is_confined=True
    )
    
    # 弱透水层2
    print("\n弱透水层2：")
    print("  顶板高程: 45 m")
    print("  底板高程: 38 m")
    print("  厚度: 7 m")
    print("  垂向渗透系数: 0.005 m/day")
    print("  渗漏系数: 0.00071 1/day")
    
    system.add_aquitard_layer(
        top_elevation=45.0,
        bottom_elevation=38.0,
        K_vertical=0.005
    )
    
    # 第3层：深层含水层
    print("\n第3层（深层含水层）：")
    print("  顶板高程: 38 m")
    print("  底板高程: 0 m")
    print("  厚度: 38 m")
    print("  水平渗透系数: 30 m/day")
    print("  储水系数: 0.00008")
    
    system.add_aquifer_layer(
        layer_id=2,
        top_elevation=38.0,
        bottom_elevation=0.0,
        K_horizontal=30.0,
        storage=0.00008,
        is_confined=True
    )
    
    # 输出摘要
    summary = system.get_summary()
    print(f"\n系统摘要：")
    print(f"  含水层数: {summary['n_layers']}")
    print(f"  弱透水层数: {summary['n_aquitards']}")
    
    return system


def scenario1_uniform_heads(system):
    """
    场景1：均匀水头分布（无越流）
    """
    print("\n" + "="*60)
    print("场景1：均匀水头分布")
    print("="*60)
    print("\n所有层水头相同，无越流")
    
    # 设置相同水头
    h_uniform = 60.0
    nx, ny = 21, 21
    
    heads = [
        np.ones((ny, nx)) * h_uniform,
        np.ones((ny, nx)) * h_uniform,
        np.ones((ny, nx)) * h_uniform
    ]
    
    # 计算越流
    cell_area = 50.0 * 50.0  # 50m × 50m
    leakage = system.compute_leakage(heads, cell_area)
    
    print(f"\n水头：")
    for i in range(3):
        print(f"  第{i+1}层: {h_uniform:.1f} m")
    
    print(f"\n越流通量：")
    for i in range(3):
        total_leak = np.sum(leakage[i])
        print(f"  第{i+1}层: {total_leak:.2e} m³/day （应为0）")
    
    return heads, leakage


def scenario2_gradient_heads(system):
    """
    场景2：水头梯度（有越流）
    """
    print("\n" + "="*60)
    print("场景2：水头梯度分布")
    print("="*60)
    print("\n第1层水头最高，第3层最低，产生向下越流")
    
    nx, ny = 21, 21
    
    # 设置不同水头（向下递减）
    heads = [
        np.ones((ny, nx)) * 65.0,  # 第1层：65m
        np.ones((ny, nx)) * 55.0,  # 第2层：55m
        np.ones((ny, nx)) * 50.0   # 第3层：50m
    ]
    
    # 计算越流
    cell_area = 50.0 * 50.0
    leakage = system.compute_leakage(heads, cell_area)
    
    print(f"\n水头设置：")
    print(f"  第1层: 65.0 m （最高）")
    print(f"  第2层: 55.0 m")
    print(f"  第3层: 50.0 m （最低）")
    
    print(f"\n单元越流通量：")
    for i in range(3):
        avg_leak = np.mean(leakage[i])
        total_leak = np.sum(leakage[i])
        print(f"  第{i+1}层:")
        print(f"    平均: {avg_leak:.2f} m³/day/cell")
        print(f"    总计: {total_leak:.2f} m³/day")
        if avg_leak > 0:
            print(f"    方向: 向下流出")
        elif avg_leak < 0:
            print(f"    方向: 向上流入")
        else:
            print(f"    方向: 无流动")
    
    # 水量平衡检查
    total_balance = sum(np.sum(leak) for leak in leakage)
    print(f"\n水量平衡检查：")
    print(f"  总净越流: {total_balance:.2e} m³/day")
    print(f"  （应接近0，误差来自数值精度）")
    
    return heads, leakage


def scenario3_pumping_effect(system):
    """
    场景3：中层抽水效应
    """
    print("\n" + "="*60)
    print("场景3：中层抽水效应")
    print("="*60)
    print("\n在第2层（中层）模拟抽水，分析越流响应")
    
    nx, ny = 41, 41
    x = np.linspace(0, 2000, nx)
    y = np.linspace(0, 2000, ny)
    X, Y = np.meshgrid(x, y)
    
    # 井位置（中心）
    well_x, well_y = 1000, 1000
    r = np.sqrt((X - well_x)**2 + (Y - well_y)**2)
    r = np.maximum(r, 10.0)  # 避免r=0
    
    # 初始水头
    h0_layer1 = 65.0
    h0_layer2 = 60.0
    h0_layer3 = 55.0
    
    # 模拟抽水引起的降深（简化）
    # 第2层：最大降深
    # 第1层和第3层：通过越流受影响
    
    Q_well = 2000.0  # 抽水量 (m³/day)
    T2 = system.aquifer_layers[1].transmissivity
    S2 = system.aquifer_layers[1].storage
    t = 10.0  # 抽水10天
    
    # 使用Theis解计算第2层降深（简化，忽略越流影响）
    from scipy.special import exp1
    u = r**2 * S2 / (4 * T2 * t)
    s2 = Q_well / (4 * np.pi * T2) * exp1(u)
    s2 = np.minimum(s2, 8.0)  # 限制最大降深
    
    # 第1层和第3层的降深（通过越流传递，约为第2层的30%和20%）
    s1 = s2 * 0.3
    s3 = s2 * 0.2
    
    heads = [
        h0_layer1 - s1,
        h0_layer2 - s2,
        h0_layer3 - s3
    ]
    
    # 计算越流
    cell_area = (x[1] - x[0]) * (y[1] - y[0])
    leakage = system.compute_leakage(heads, cell_area)
    
    print(f"\n抽水井参数：")
    print(f"  位置: ({well_x}, {well_y}) m")
    print(f"  流量: {Q_well} m³/day")
    print(f"  抽水层: 第2层（中层）")
    print(f"  时间: {t} day")
    
    print(f"\n水头变化：")
    print(f"  第1层: {h0_layer1:.1f} → {np.min(heads[0]):.1f} m （降深{np.max(s1):.2f} m）")
    print(f"  第2层: {h0_layer2:.1f} → {np.min(heads[1]):.1f} m （降深{np.max(s2):.2f} m）")
    print(f"  第3层: {h0_layer3:.1f} → {np.min(heads[2]):.1f} m （降深{np.max(s3):.2f} m）")
    
    print(f"\n总越流量：")
    for i in range(3):
        total_leak = np.sum(leakage[i])
        print(f"  第{i+1}层: {total_leak:.2f} m³/day")
    
    # 越流补给率
    leakage_in_layer2_from_above = -np.sum(leakage[0])  # 从第1层流入第2层
    leakage_in_layer2_from_below = -np.sum(leakage[2])  # 从第3层流入第2层
    total_leakage_to_layer2 = leakage_in_layer2_from_above + leakage_in_layer2_from_below
    
    print(f"\n第2层越流补给：")
    print(f"  来自第1层: {leakage_in_layer2_from_above:.2f} m³/day")
    print(f"  来自第3层: {leakage_in_layer2_from_below:.2f} m³/day")
    print(f"  总越流补给: {total_leakage_to_layer2:.2f} m³/day")
    print(f"  抽水量: {Q_well:.2f} m³/day")
    print(f"  越流补给占比: {total_leakage_to_layer2/Q_well*100:.1f}%")
    
    return heads, leakage, X, Y, r


def analyze_hantush_jacob():
    """
    分析Hantush-Jacob解
    """
    print("\n" + "="*60)
    print("Hantush-Jacob解析解分析")
    print("="*60)
    print("\n对比考虑越流与不考虑越流的抽水降深")
    
    # 参数
    Q_well = 1000.0  # m³/day
    T = 750.0        # m²/day
    S = 0.0001
    t = 1.0          # day
    
    # 径向距离
    r = np.linspace(10, 1000, 100)
    
    # 不同的渗漏系数
    leakances = [0.0, 0.0001, 0.0005, 0.001, 0.005]
    
    results = {}
    
    print(f"\n参数设置：")
    print(f"  抽水量: {Q_well} m³/day")
    print(f"  导水系数: {T} m²/day")
    print(f"  储水系数: {S}")
    print(f"  时间: {t} day")
    
    print(f"\n渗漏因子：")
    
    for L in leakances:
        s = hantush_jacob_solution(r, t, Q_well, T, S, L)
        
        if L == 0:
            label = "无越流（Theis）"
            B = np.inf
        else:
            B = estimate_leakage_factor(T, L)
            label = f"L={L:.4f} 1/day"
        
        results[label] = {'r': r, 's': s, 'L': L, 'B': B}
        
        if L == 0:
            print(f"  {label}: B = ∞")
        else:
            print(f"  {label}: B = {B:.1f} m")
    
    return results


def analyze_leakage_factor():
    """
    渗漏因子敏感性分析
    """
    print("\n" + "="*60)
    print("渗漏因子敏感性分析")
    print("="*60)
    
    T = 750.0  # m²/day
    
    # 不同的弱透水层参数
    K_values = [0.001, 0.01, 0.1, 1.0]
    b_values = [1, 5, 10, 20]
    
    print(f"\n导水系数: T = {T} m²/day")
    print(f"\n渗漏因子矩阵 B (m):")
    print(f"{'K_aquitard (m/day)':<20}", end='')
    for b in b_values:
        print(f"b={b}m".center(12), end='')
    print()
    print("-" * 68)
    
    results = []
    
    for K in K_values:
        print(f"{K:<20.3f}", end='')
        for b in b_values:
            L = K / b
            B = estimate_leakage_factor(T, L)
            print(f"{B:>12.1f}", end='')
            results.append({'K': K, 'b': b, 'L': L, 'B': B})
        print()
    
    print(f"\n解释：")
    print(f"  B > 500m:  弱越流，影响范围广")
    print(f"  100m < B < 500m: 中等越流")
    print(f"  B < 100m:  强越流，影响范围窄")
    
    return results


def plot_results(system, scenario2_data, scenario3_data, hantush_data, leakage_factor_data):
    """绘制所有结果"""
    
    fig = plt.figure(figsize=(18, 14))
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    # 解包数据
    heads2, leakage2 = scenario2_data
    heads3, leakage3, X3, Y3, r3 = scenario3_data
    
    # 图1: 场景2 - 水头剖面
    ax1 = fig.add_subplot(gs[0, 0])
    
    nx = heads2[0].shape[1]
    x_profile = np.linspace(0, 1000, nx)
    
    for i in range(3):
        h_profile = heads2[i][nx//2, :]
        ax1.plot(x_profile, h_profile, 'o-', linewidth=2, markersize=4,
                label=f'第{i+1}层')
    
    ax1.set_xlabel('距离 (m)', fontsize=11)
    ax1.set_ylabel('水头 (m)', fontsize=11)
    ax1.set_title('场景2：水头垂向分布', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 图2: 场景2 - 越流通量
    ax2 = fig.add_subplot(gs[0, 1])
    
    layer_names = ['第1层', '第2层', '第3层']
    total_leakages = [np.sum(leak) for leak in leakage2]
    colors = ['skyblue', 'lightcoral', 'lightgreen']
    
    bars = ax2.bar(layer_names, total_leakages, color=colors, alpha=0.7, edgecolor='black')
    ax2.axhline(0, color='black', linestyle='--', linewidth=0.8)
    ax2.set_ylabel('总越流通量 (m³/day)', fontsize=11)
    ax2.set_title('场景2：分层越流通量', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标签
    for bar, leak in zip(bars, total_leakages):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{leak:.1f}',
                ha='center', va='bottom' if height > 0 else 'top',
                fontsize=9)
    
    # 图3: 系统结构示意
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.axis('off')
    
    # 绘制系统结构
    y_positions = [0.8, 0.6, 0.4]
    aquifer_heights = [0.12, 0.15, 0.20]
    
    for i, (y, h) in enumerate(zip(y_positions, aquifer_heights)):
        # 含水层
        rect = plt.Rectangle((0.1, y-h), 0.8, h, 
                            facecolor='lightblue', edgecolor='black', linewidth=2)
        ax3.add_patch(rect)
        ax3.text(0.5, y-h/2, f'含水层{i+1}', ha='center', va='center',
                fontsize=11, fontweight='bold')
        
        # 弱透水层（除了最下层）
        if i < 2:
            aquitard_y = y - h - 0.03
            aquitard_h = 0.03
            rect_aq = plt.Rectangle((0.1, aquitard_y), 0.8, aquitard_h,
                                   facecolor='gray', edgecolor='black', linewidth=1,
                                   hatch='///', alpha=0.5)
            ax3.add_patch(rect_aq)
            ax3.text(0.5, aquitard_y + aquitard_h/2, '弱透水层',
                    ha='center', va='center', fontsize=8)
    
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.set_title('三层系统结构', fontsize=13, fontweight='bold')
    
    # 图4: 场景3 - 第2层水头等值线
    ax4 = fig.add_subplot(gs[1, 0])
    
    levels = np.linspace(np.min(heads3[1]), np.max(heads3[1]), 15)
    contourf = ax4.contourf(X3, Y3, heads3[1], levels=levels, cmap='RdYlBu_r', alpha=0.8)
    contour = ax4.contour(X3, Y3, heads3[1], levels=10, colors='black',
                         linewidths=0.5, alpha=0.6)
    ax4.clabel(contour, inline=True, fontsize=8)
    ax4.plot(1000, 1000, 'r*', markersize=15, label='抽水井')
    ax4.set_xlabel('X (m)', fontsize=11)
    ax4.set_ylabel('Y (m)', fontsize=11)
    ax4.set_title('场景3：第2层水头分布', fontsize=13, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.set_aspect('equal')
    plt.colorbar(contourf, ax=ax4, label='水头 (m)')
    
    # 图5: 场景3 - 径向剖面
    ax5 = fig.add_subplot(gs[1, 1])
    
    # 取一条径向剖面
    center_row = heads3[0].shape[0] // 2
    r_profile = np.linspace(0, 1400, heads3[0].shape[1]//2)
    
    for i in range(3):
        h_radial = heads3[i][center_row, heads3[i].shape[1]//2:]
        ax5.plot(r_profile, h_radial, 'o-', linewidth=2, markersize=3,
                label=f'第{i+1}层')
    
    ax5.set_xlabel('径向距离 (m)', fontsize=11)
    ax5.set_ylabel('水头 (m)', fontsize=11)
    ax5.set_title('场景3：径向水头剖面', fontsize=13, fontweight='bold')
    ax5.legend(fontsize=10)
    ax5.grid(True, alpha=0.3)
    
    # 图6: 场景3 - 越流通量分布
    ax6 = fig.add_subplot(gs[1, 2])
    
    layer_names = ['第1层', '第2层', '第3层']
    total_leakages3 = [np.sum(leak) for leak in leakage3]
    
    bars = ax6.bar(layer_names, total_leakages3, color=colors, alpha=0.7, edgecolor='black')
    ax6.axhline(0, color='black', linestyle='--', linewidth=0.8)
    ax6.set_ylabel('总越流通量 (m³/day)', fontsize=11)
    ax6.set_title('场景3：抽水引起的越流', fontsize=13, fontweight='bold')
    ax6.grid(True, alpha=0.3, axis='y')
    
    for bar, leak in zip(bars, total_leakages3):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                f'{leak:.0f}',
                ha='center', va='bottom' if height > 0 else 'top',
                fontsize=9)
    
    # 图7: Hantush-Jacob解
    ax7 = fig.add_subplot(gs[2, 0])
    
    for label, data in hantush_data.items():
        if data['L'] == 0:
            ax7.plot(data['r'], data['s'], 'k-', linewidth=2.5, label=label)
        else:
            ax7.plot(data['r'], data['s'], '--', linewidth=2, label=label)
    
    ax7.set_xlabel('径向距离 (m)', fontsize=11)
    ax7.set_ylabel('降深 (m)', fontsize=11)
    ax7.set_title('Hantush-Jacob解：越流影响', fontsize=13, fontweight='bold')
    ax7.legend(fontsize=9, loc='upper right')
    ax7.grid(True, alpha=0.3)
    ax7.set_xlim(0, 1000)
    
    # 图8: 渗漏因子热图
    ax8 = fig.add_subplot(gs[2, 1])
    
    K_values = sorted(set(d['K'] for d in leakage_factor_data))
    b_values = sorted(set(d['b'] for d in leakage_factor_data))
    
    B_matrix = np.zeros((len(K_values), len(b_values)))
    for data in leakage_factor_data:
        i = K_values.index(data['K'])
        j = b_values.index(data['b'])
        B_matrix[i, j] = data['B']
    
    im = ax8.imshow(B_matrix, cmap='YlOrRd_r', aspect='auto',
                   extent=[b_values[0]-0.5, b_values[-1]+0.5,
                          K_values[0], K_values[-1]])
    
    ax8.set_xlabel('弱透水层厚度 (m)', fontsize=11)
    ax8.set_ylabel('弱透水层K (m/day)', fontsize=11)
    ax8.set_title('渗漏因子 B (m)', fontsize=13, fontweight='bold')
    ax8.set_xticks(b_values)
    ax8.set_yticks(K_values)
    ax8.set_yscale('log')
    
    # 添加数值标注
    for i, K in enumerate(K_values):
        for j, b in enumerate(b_values):
            text = ax8.text(b, K, f'{B_matrix[i, j]:.0f}',
                          ha="center", va="center", color="black", fontsize=8)
    
    plt.colorbar(im, ax=ax8, label='B (m)')
    
    # 图9: 越流强度分类
    ax9 = fig.add_subplot(gs[2, 2])
    
    # 统计不同强度的渗漏因子
    B_values = [d['B'] for d in leakage_factor_data]
    categories = {
        '强越流\n(B<100m)': sum(1 for B in B_values if B < 100),
        '中等越流\n(100-500m)': sum(1 for B in B_values if 100 <= B < 500),
        '弱越流\n(B>500m)': sum(1 for B in B_values if B >= 500)
    }
    
    colors_cat = ['red', 'orange', 'green']
    bars = ax9.bar(categories.keys(), categories.values(),
                  color=colors_cat, alpha=0.7, edgecolor='black')
    
    ax9.set_ylabel('参数组合数', fontsize=11)
    ax9.set_title('越流强度分类统计', fontsize=13, fontweight='bold')
    ax9.grid(True, alpha=0.3, axis='y')
    
    for bar, count in zip(bars, categories.values()):
        height = bar.get_height()
        ax9.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.savefig('case_13_leakage_results.png', dpi=300, bbox_inches='tight')
    print("\n图片已保存: case_13_leakage_results.png")
    
    plt.show()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("案例13：渗漏与越流模拟")
    print("="*60)
    print("\n本案例演示多层含水层系统中的垂向越流")
    print("包括：三层系统、越流计算、Hantush-Jacob解、渗漏因子")
    
    # 1. 创建三层系统
    system = setup_three_layer_system()
    
    # 2. 场景1：均匀水头
    scenario1_uniform_heads(system)
    
    # 3. 场景2：水头梯度
    scenario2_data = scenario2_gradient_heads(system)
    
    # 4. 场景3：抽水效应
    scenario3_data = scenario3_pumping_effect(system)
    
    # 5. Hantush-Jacob解析解
    hantush_data = analyze_hantush_jacob()
    
    # 6. 渗漏因子分析
    leakage_factor_data = analyze_leakage_factor()
    
    # 7. 绘图
    print("\n生成结果图...")
    plot_results(system, scenario2_data, scenario3_data, hantush_data, leakage_factor_data)
    
    # 8. 总结
    print("\n" + "="*60)
    print("案例13完成总结")
    print("="*60)
    
    print(f"\n核心发现：")
    print(f"1. 越流方向由水头梯度决定")
    print(f"2. 抽水可以诱导上下层越流补给")
    print(f"3. 越流强度取决于弱透水层参数")
    print(f"4. 渗漏因子B控制越流影响范围")
    print(f"5. Hantush-Jacob解考虑越流效应")
    
    print(f"\n学习要点：")
    print(f"✓ 多层含水层系统建模")
    print(f"✓ 越流机制与计算")
    print(f"✓ 层间水量交换")
    print(f"✓ 渗漏因子物理意义")
    print(f"✓ 解析解验证")
    
    print("\n✅ 案例13执行完成！")


if __name__ == '__main__':
    main()
