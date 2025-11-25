"""
案例18：污染物运移模拟

本案例演示地下水污染物运移预测与修复方案设计。

演示内容：
---------
1. 一维对流-弥散解析解验证
2. 吸附作用影响
3. 衰减作用影响
4. 二维污染羽演化
5. 数值方法稳定性
6. 修复方案设计

物理场景：
---------
某地发生地下水污染：
- 污染源持续泄漏
- 污染羽随地下水扩散
- 饮用水井受威胁
- 需要修复方案

学习目标：
---------
1. 理解对流-弥散过程
2. 掌握ADE方程
3. 分析吸附和衰减影响
4. 预测污染羽演化
5. 设计修复方案
6. 评估风险

作者: gwflow开发团队
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.animation import FuncAnimation

# 导入gwflow模块
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from gwflow.transport import (
    analytical_1d_instantaneous,
    analytical_1d_continuous,
    analytical_2d_instantaneous,
    ogata_banks_solution,
    ADESolver1D,
    ADESolver2D,
    retardation_factor,
    linear_sorption,
    solve_ade_1d_implicit,
    solve_ade_2d_implicit
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def experiment_1_analytical_verification():
    """
    实验1：解析解验证
    """
    print("\n" + "="*60)
    print("实验1：一维对流-弥散解析解")
    print("="*60)
    
    # 参数
    v = 0.5  # m/day
    D = 0.1  # m²/day
    C0 = 100  # kg/m³
    t = 50  # days
    
    # 空间域
    x = np.linspace(0, 100, 200)
    
    # Ogata-Banks解（连续源）
    C_ogata = ogata_banks_solution(x, t, C0, v, D, R=1.0)
    
    # 瞬时源
    M = 10  # kg
    C_instant = analytical_1d_instantaneous(x, t, M, v, D, R=1.0)
    
    print(f"\n参数：")
    print(f"  流速 v = {v} m/day")
    print(f"  弥散系数 D = {D} m²/day")
    print(f"  时间 t = {t} day")
    
    print(f"\nPeclet数：")
    Pe = v * 1 / D  # 特征长度1m
    print(f"  Pe = vL/D = {Pe:.1f}")
    if Pe > 10:
        print(f"  对流主导")
    elif Pe < 0.1:
        print(f"  弥散主导")
    else:
        print(f"  对流和弥散都重要")
    
    print(f"\n连续源（Ogata-Banks）：")
    print(f"  边界浓度 C0 = {C0} kg/m³")
    print(f"  中心位置 x ≈ {v*t:.1f} m")
    print(f"  最大浓度 {np.max(C_ogata):.1f} kg/m³")
    
    print(f"\n瞬时源：")
    print(f"  总质量 M = {M} kg")
    print(f"  中心位置 x ≈ {v*t:.1f} m")
    print(f"  峰值浓度 {np.max(C_instant):.2f} kg/m³")
    
    return x, C_ogata, C_instant, v, D


def experiment_2_sorption_effect():
    """
    实验2：吸附作用影响
    """
    print("\n" + "="*60)
    print("实验2：吸附作用影响")
    print("="*60)
    
    # 参数
    v = 0.5  # m/day
    D = 0.1  # m²/day
    C0 = 100  # kg/m³
    t = 50  # days
    x = np.linspace(0, 100, 200)
    
    # 土壤参数
    rho_b = 1500  # kg/m³
    n = 0.3
    
    # 不同吸附强度
    Kd_values = [0, 0.001, 0.005, 0.01]  # m³/kg
    
    print(f"\n土壤参数：")
    print(f"  干密度 ρb = {rho_b} kg/m³")
    print(f"  孔隙度 n = {n}")
    
    print(f"\n不同吸附强度的影响：")
    print(f"{'Kd (m³/kg)':<15} {'阻滞因子R':<15} {'速度(m/day)':<15}")
    print("-" * 45)
    
    C_dict = {}
    for Kd in Kd_values:
        R = retardation_factor(rho_b, n, Kd)
        v_eff = v / R
        C = ogata_banks_solution(x, t, C0, v, D, R=R)
        C_dict[Kd] = C
        print(f"{Kd:<15.3f} {R:<15.2f} {v_eff:<15.3f}")
    
    print(f"\n物理意义：")
    print(f"  Kd=0: 无吸附，保守运移")
    print(f"  Kd↑: 阻滞因子R↑，运移速度↓")
    print(f"  吸附作用延缓污染扩散")
    
    return x, C_dict, Kd_values


def experiment_3_decay_effect():
    """
    实验3：衰减作用影响
    """
    print("\n" + "="*60)
    print("实验3：衰减作用影响")
    print("="*60)
    
    # 参数
    v = 0.5
    D = 0.1
    C0 = 100
    t = 50
    x = np.linspace(0, 100, 200)
    
    # 不同衰减系数
    lambda_values = [0, 0.01, 0.05, 0.1]  # 1/day
    
    print(f"\n衰减动力学：")
    print(f"  C(t) = C0 * exp(-λt)")
    print(f"  半衰期 t1/2 = ln(2)/λ")
    
    print(f"\n不同衰减系数的影响：")
    print(f"{'λ (1/day)':<15} {'半衰期(day)':<15} {'最大浓度':<15}")
    print("-" * 45)
    
    C_dict = {}
    for lam in lambda_values:
        C = ogata_banks_solution(x, t, C0, v, D, R=1.0)
        C = C * np.exp(-lam * t)  # 叠加衰减
        C_dict[lam] = C
        t_half = np.log(2) / lam if lam > 0 else np.inf
        print(f"{lam:<15.2f} {t_half:<15.1f} {np.max(C):<15.1f}")
    
    print(f"\n应用：")
    print(f"  生物降解：λ较大")
    print(f"  放射性衰变：λ固定")
    print(f"  化学反应：λ取决于条件")
    
    return x, C_dict, lambda_values


def experiment_4_2d_plume_evolution():
    """
    实验4：二维污染羽演化
    """
    print("\n" + "="*60)
    print("实验4：二维污染羽演化")
    print("="*60)
    
    # 参数
    vx = 0.5  # m/day
    vy = 0.0
    alpha_L = 5.0  # 纵向弥散度 m
    alpha_T = 0.5  # 横向弥散度 m
    Dx = alpha_L * vx + 0.01  # 纵向弥散系数
    Dy = alpha_T * vx + 0.01  # 横向弥散系数
    M = 100  # kg
    
    # 网格
    x = np.linspace(-20, 100, 60)
    y = np.linspace(-30, 30, 60)
    X, Y = np.meshgrid(x, y)
    
    # 不同时刻
    times = [10, 30, 50, 100]
    
    print(f"\n参数：")
    print(f"  流速 vx = {vx} m/day")
    print(f"  纵向弥散度 αL = {alpha_L} m")
    print(f"  横向弥散度 αT = {alpha_T} m")
    print(f"  Dx = {Dx:.2f} m²/day")
    print(f"  Dy = {Dy:.2f} m²/day")
    
    print(f"\n污染羽特征：")
    print(f"{'时间(day)':<12} {'中心x(m)':<12} {'长度(m)':<12} {'宽度(m)':<12}")
    print("-" * 48)
    
    C_dict = {}
    for t in times:
        C = analytical_2d_instantaneous(X, Y, t, M, vx, vy, Dx, Dy)
        C_dict[t] = C
        
        # 估计尺度
        center_x = vx * t
        length = 4 * np.sqrt(Dx * t)  # 95%范围
        width = 4 * np.sqrt(Dy * t)
        
        print(f"{t:<12} {center_x:<12.1f} {length:<12.1f} {width:<12.1f}")
    
    print(f"\n特征：")
    print(f"  污染羽沿流向拉长")
    print(f"  纵向扩散 > 横向扩散")
    print(f"  浓度峰值随时间降低")
    
    return X, Y, C_dict, times


def experiment_5_numerical_stability():
    """
    实验5：数值方法稳定性
    """
    print("\n" + "="*60)
    print("实验5：数值方法稳定性")
    print("="*60)
    
    # 参数
    v = 0.5
    D = 0.1
    x = np.linspace(0, 50, 51)
    dx = x[1] - x[0]
    
    # 初始条件（脉冲）
    C0 = np.zeros(len(x))
    C0[10:15] = 100
    
    # 不同时间步长
    dt_values = [0.5, 1.0, 2.0]
    
    print(f"\n稳定性分析：")
    print(f"  Courant数 Cr = v*dt/dx")
    print(f"  扩散数 Cd = D*dt/dx²")
    print(f"\n稳定性条件（显式）：")
    print(f"  Cr ≤ 1, Cd ≤ 0.5")
    
    print(f"\n不同时间步长：")
    print(f"{'dt (day)':<12} {'Cr':<12} {'Cd':<12} {'稳定性':<12}")
    print("-" * 48)
    
    C_dict = {}
    for dt in dt_values:
        Cr = v * dt / dx
        Cd = D * dt / dx**2
        
        stable = "✓" if (Cr <= 1 and Cd <= 0.5) else "✗"
        print(f"{dt:<12.1f} {Cr:<12.2f} {Cd:<12.2f} {stable:<12}")
        
        # 求解（隐式，总是稳定）
        C_history = solve_ade_1d_implicit(C0, dx, dt, int(20/dt), v, D)
        C_dict[dt] = C_history[-1, :]
    
    print(f"\n隐式方法：")
    print(f"  无条件稳定")
    print(f"  可使用大时间步长")
    print(f"  计算效率高")
    
    return x, C_dict, dt_values


def experiment_6_remediation_design():
    """
    实验6：修复方案设计
    """
    print("\n" + "="*60)
    print("实验6：抽取修复方案")
    print("="*60)
    
    # 污染羽
    vx = 0.5
    vy = 0.0
    Dx = 2.5
    Dy = 0.25
    M = 100
    t = 50
    
    x = np.linspace(-20, 100, 60)
    y = np.linspace(-30, 30, 60)
    X, Y = np.meshgrid(x, y)
    
    C = analytical_2d_instantaneous(X, Y, t, M, vx, vy, Dx, Dy)
    
    # 饮用水井位置
    well_x, well_y = 40, 5
    
    # 计算井处浓度
    C_well = analytical_2d_instantaneous(well_x, well_y, t, M, vx, vy, Dx, Dy)
    
    # 标准
    C_standard = 0.01  # kg/m³
    
    print(f"\n污染状况：")
    print(f"  时间：t = {t} day")
    print(f"  饮用水井位置：({well_x}, {well_y})")
    print(f"  井处浓度：{C_well:.4f} kg/m³")
    print(f"  标准限值：{C_standard:.4f} kg/m³")
    
    if C_well > C_standard:
        print(f"  ⚠️ 超标{C_well/C_standard:.1f}倍！需要修复")
        
        # 修复方案
        print(f"\n修复方案设计：")
        print(f"1. 抽取修复（Pump & Treat）")
        print(f"   - 在污染源设置抽水井")
        print(f"   - 形成捕获带，拦截污染羽")
        print(f"   - 处理抽出的污染水")
        
        print(f"\n2. 监测自然衰减（MNA）")
        print(f"   - 依靠自然衰减过程")
        print(f"   - 定期监测")
        print(f"   - 适用于低风险情况")
        
        print(f"\n3. 反应墙（PRB）")
        print(f"   - 在污染羽前方设置反应墙")
        print(f"   - 原位处理")
        print(f"   - 被动修复")
    else:
        print(f"  ✓ 未超标，继续监测")
    
    return X, Y, C, well_x, well_y, C_well, C_standard


def plot_results(exp1, exp2, exp3, exp4, exp5, exp6):
    """绘制所有结果"""
    
    fig = plt.figure(figsize=(18, 14))
    gs = GridSpec(4, 3, figure=fig, hspace=0.35, wspace=0.35)
    
    # 图1: 解析解验证
    ax1 = fig.add_subplot(gs[0, 0])
    x, C_ogata, C_instant, v, D = exp1
    ax1.plot(x, C_ogata, 'b-', linewidth=2, label='连续源(Ogata-Banks)')
    ax1.plot(x, C_instant, 'r--', linewidth=2, label='瞬时源')
    ax1.set_xlabel('距离 (m)', fontsize=11)
    ax1.set_ylabel('浓度 (kg/m³)', fontsize=11)
    ax1.set_title('一维解析解', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 图2: 吸附影响
    ax2 = fig.add_subplot(gs[0, 1])
    x, C_dict, Kd_values = exp2
    for Kd in Kd_values:
        ax2.plot(x, C_dict[Kd], linewidth=2, label=f'Kd={Kd}')
    ax2.set_xlabel('距离 (m)', fontsize=11)
    ax2.set_ylabel('浓度 (kg/m³)', fontsize=11)
    ax2.set_title('吸附作用影响', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 图3: 衰减影响
    ax3 = fig.add_subplot(gs[0, 2])
    x, C_dict, lambda_values = exp3
    for lam in lambda_values:
        ax3.plot(x, C_dict[lam], linewidth=2, label=f'λ={lam}')
    ax3.set_xlabel('距离 (m)', fontsize=11)
    ax3.set_ylabel('浓度 (kg/m³)', fontsize=11)
    ax3.set_title('衰减作用影响', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    # 图4-7: 二维污染羽演化（4个时刻）
    X, Y, C_dict, times = exp4
    for idx, t in enumerate(times[:4]):
        ax = fig.add_subplot(gs[1 + idx//2, idx%2])
        C = C_dict[t]
        levels = np.logspace(-3, np.log10(np.max(C)), 10)
        cs = ax.contourf(X, Y, C, levels=levels, cmap='YlOrRd', norm=plt.matplotlib.colors.LogNorm())
        ax.contour(X, Y, C, levels=levels, colors='black', linewidths=0.5, alpha=0.3)
        ax.set_xlabel('x (m)', fontsize=11)
        ax.set_ylabel('y (m)', fontsize=11)
        ax.set_title(f't = {t} day', fontsize=13, fontweight='bold')
        ax.axis('equal')
        plt.colorbar(cs, ax=ax, label='C (kg/m³)')
    
    # 图8: 数值稳定性
    ax8 = fig.add_subplot(gs[2, 2])
    x, C_dict, dt_values = exp5
    for dt in dt_values:
        ax8.plot(x, C_dict[dt], linewidth=2, label=f'dt={dt}')
    ax8.set_xlabel('距离 (m)', fontsize=11)
    ax8.set_ylabel('浓度 (kg/m³)', fontsize=11)
    ax8.set_title('数值稳定性', fontsize=13, fontweight='bold')
    ax8.legend(fontsize=10)
    ax8.grid(True, alpha=0.3)
    
    # 图9: 修复方案
    ax9 = fig.add_subplot(gs[3, :])
    X, Y, C, well_x, well_y, C_well, C_standard = exp6
    levels = np.logspace(-3, np.log10(np.max(C)), 10)
    cs = ax9.contourf(X, Y, C, levels=levels, cmap='YlOrRd', norm=plt.matplotlib.colors.LogNorm())
    ax9.contour(X, Y, C, levels=levels, colors='black', linewidths=0.5, alpha=0.3)
    
    # 标记饮用水井
    ax9.plot(well_x, well_y, 'b^', markersize=15, label=f'饮用水井 (C={C_well:.3f})')
    
    # 标记超标区域
    C_standard_contour = [C_standard]
    ax9.contour(X, Y, C, levels=C_standard_contour, colors='red', 
               linewidths=3, linestyles='--', label=f'超标线 (C={C_standard})')
    
    ax9.set_xlabel('x (m)', fontsize=11)
    ax9.set_ylabel('y (m)', fontsize=11)
    ax9.set_title('污染羽与修复方案', fontsize=13, fontweight='bold')
    ax9.legend(fontsize=10)
    ax9.axis('equal')
    plt.colorbar(cs, ax=ax9, label='浓度 (kg/m³)')
    
    plt.savefig('case_18_contaminant_transport_results.png', dpi=300, bbox_inches='tight')
    print("\n图片已保存: case_18_contaminant_transport_results.png")
    
    plt.show()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("案例18：污染物运移模拟")
    print("="*60)
    print("\n本案例演示地下水污染物运移预测与修复设计")
    
    # 运行所有实验
    exp1 = experiment_1_analytical_verification()
    exp2 = experiment_2_sorption_effect()
    exp3 = experiment_3_decay_effect()
    exp4 = experiment_4_2d_plume_evolution()
    exp5 = experiment_5_numerical_stability()
    exp6 = experiment_6_remediation_design()
    
    # 绘图
    print("\n生成结果图...")
    plot_results(exp1, exp2, exp3, exp4, exp5, exp6)
    
    # 总结
    print("\n" + "="*60)
    print("案例18完成总结")
    print("="*60)
    
    print(f"\n核心发现：")
    print(f"1. 对流主导方向扩散，弥散导致扩展")
    print(f"2. 吸附延缓运移（R↑→速度↓）")
    print(f"3. 衰减降低浓度（λ↑→浓度↓）")
    print(f"4. 污染羽沿流向拉长")
    print(f"5. 数值方法需要稳定性检查")
    print(f"6. 修复方案需要综合考虑")
    
    print(f"\n学习要点：")
    print(f"✓ 对流-弥散方程（ADE）")
    print(f"✓ 解析解应用")
    print(f"✓ 吸附与阻滞因子")
    print(f"✓ 衰减动力学")
    print(f"✓ 数值方法与稳定性")
    print(f"✓ 污染羽预测")
    print(f"✓ 修复方案设计")
    
    print(f"\n工程意义：")
    print(f"✓ 污染事故应急")
    print(f"✓ 风险评估")
    print(f"✓ 修复方案设计")
    print(f"✓ 监测网优化")
    
    print("\n✅ 案例18执行完成！")
    print("\n🎉🎉🎉 第四篇全部完成！🎉🎉🎉")


if __name__ == '__main__':
    main()
