"""
案例16：地下水开采优化

本案例演示抽水井模拟与开采方案优化。

演示内容：
---------
1. Theis解与Cooper-Jacob解对比
2. 单井降落漏斗分析
3. 多井系统叠加
4. 井间干扰分析
5. 抽水量优化
6. 敏感性分析

物理场景：
---------
某含水层计划建设水源地：
- 含水层参数：T=500 m²/day, S=0.0002
- 初始水头：h0=50 m
- 最小水位要求：h_min=45 m（生态约束）
- 计划时间：100天

目标：
- 评估单井影响
- 设计多井系统
- 优化抽水方案
- 满足生态约束

学习目标：
---------
1. 掌握Theis解和Cooper-Jacob解
2. 理解叠加原理
3. 分析井间干扰
4. 应用优化方法
5. 评估开采方案

作者: gwflow开发团队
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d import Axes3D

# 导入gwflow模块
import sys
sys.path.insert(0, '/workspace/books/underground-water-dynamics')

from gwflow.pumping import (
    PumpingWell,
    WellField,
    theis_solution,
    cooper_jacob_solution,
    theis_well_function,
    superposition_principle,
    optimize_pumping_rates,
    distance_drawdown_curve,
    time_drawdown_curve
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def experiment_1_theis_vs_cooper_jacob():
    """
    实验1：Theis解与Cooper-Jacob解对比
    """
    print("\n" + "="*60)
    print("实验1：Theis解 vs Cooper-Jacob解")
    print("="*60)
    
    # 参数
    Q = 1000  # m³/day
    T = 500   # m²/day
    S = 0.0002
    r = 100   # m
    
    # 时间序列
    t = np.logspace(-2, 2, 100)  # 0.01 to 100 days
    
    # 计算两种解
    s_theis = theis_solution(r, t, Q, T, S)
    s_cooper = cooper_jacob_solution(r, t, Q, T, S)
    
    # 计算u值
    u = (r**2 * S) / (4 * T * t)
    
    # 分析差异
    diff = np.abs(s_theis - s_cooper)
    rel_diff = diff / s_theis * 100
    
    print(f"\n参数设置：")
    print(f"  Q = {Q} m³/day")
    print(f"  T = {T} m²/day")
    print(f"  S = {S}")
    print(f"  r = {r} m")
    
    print(f"\n在不同时间的对比：")
    for t_i in [0.1, 1, 10, 100]:
        idx = np.argmin(np.abs(t - t_i))
        u_i = u[idx]
        print(f"\n  t = {t_i} day:")
        print(f"    u = {u_i:.4e}")
        print(f"    Theis降深: {s_theis[idx]:.3f} m")
        print(f"    Cooper-Jacob降深: {s_cooper[idx]:.3f} m")
        print(f"    相对误差: {rel_diff[idx]:.2f}%")
    
    print(f"\nCooper-Jacob适用性：")
    print(f"  理论要求：u < 0.01")
    print(f"  对应时间：t > {25*r**2*S/T:.2f} day")
    
    return t, s_theis, s_cooper, u


def experiment_2_single_well_cone():
    """
    实验2：单井降落漏斗分析
    """
    print("\n" + "="*60)
    print("实验2：单井降落漏斗")
    print("="*60)
    
    # 参数
    Q = 1500  # m³/day
    T = 500
    S = 0.0002
    t = 10  # days
    
    # 2D网格
    x = np.linspace(-500, 500, 101)
    y = np.linspace(-500, 500, 101)
    X, Y = np.meshgrid(x, y)
    
    # 井在(0, 0)
    well = PumpingWell(x=0, y=0, Q=Q, name='Well-1')
    
    # 计算降深
    s = well.compute_drawdown(X, Y, t, T, S, method='theis')
    
    # 统计
    print(f"\n参数：")
    print(f"  Q = {Q} m³/day")
    print(f"  t = {t} day")
    
    print(f"\n降深统计：")
    print(f"  最大降深（井筒）: {np.max(s):.2f} m")
    print(f"  平均降深: {np.mean(s):.2f} m")
    print(f"  影响半径（s>0.01m）: {np.max(np.sqrt(X**2 + Y**2)[s > 0.01]):.0f} m")
    
    # 径向剖面
    r_profile = np.sqrt(X[50, :]**2 + Y[50, :]**2)
    s_profile = s[50, :]
    
    return X, Y, s, r_profile, s_profile


def experiment_3_multi_well_superposition():
    """
    实验3：多井系统叠加
    """
    print("\n" + "="*60)
    print("实验3：多井系统叠加")
    print("="*60)
    
    # 参数
    T = 500
    S = 0.0002
    t = 10
    
    # 创建井群：3口井
    wellfield = WellField(name="示例井群")
    
    wells_config = [
        (0, 0, 1000, "Well-1"),
        (300, 0, 800, "Well-2"),
        (150, 260, 900, "Well-3")
    ]
    
    for x, y, Q, name in wells_config:
        well = PumpingWell(x=x, y=y, Q=Q, name=name)
        wellfield.add_well(well)
    
    print(f"\n井群配置：")
    for well in wellfield.wells:
        print(f"  {well.name}: 位置({well.x:.0f}, {well.y:.0f}), Q={well.Q} m³/day")
    
    print(f"\n总抽水量: {wellfield.get_total_pumping():.0f} m³/day")
    
    # 计算总降深
    x = np.linspace(-400, 600, 101)
    y = np.linspace(-400, 600, 101)
    X, Y = np.meshgrid(x, y)
    
    s_total = wellfield.compute_total_drawdown(X, Y, t, T, S, method='theis')
    
    # 计算各井独立贡献
    contributions = {}
    for well in wellfield.wells:
        s_i = well.compute_drawdown(X, Y, t, T, S, method='theis')
        contributions[well.name] = s_i
    
    print(f"\n在点(200, 100)处的降深：")
    x_test, y_test = 200, 100
    s_test_total = wellfield.compute_total_drawdown(
        np.array([x_test]), np.array([y_test]), t, T, S, method='theis'
    )[0]
    print(f"  总降深: {s_test_total:.2f} m")
    
    for well in wellfield.wells:
        s_i = well.compute_drawdown(
            np.array([x_test]), np.array([y_test]), t, T, S, method='theis'
        )[0]
        print(f"  {well.name}贡献: {s_i:.2f} m ({s_i/s_test_total*100:.1f}%)")
    
    return X, Y, s_total, wellfield, contributions


def experiment_4_well_interference():
    """
    实验4：井间干扰分析
    """
    print("\n" + "="*60)
    print("实验4：井间干扰分析")
    print("="*60)
    
    # 参数
    Q = 1000
    T = 500
    S = 0.0002
    t_range = np.logspace(-1, 2, 50)
    
    # 观测点位置（在两井中间）
    x_obs, y_obs = 150, 0
    
    # 情景1：单井
    s_single = theis_solution(
        r=np.sqrt(x_obs**2 + y_obs**2),
        t=t_range, Q=Q, T=T, S=S
    )
    
    # 情景2：两井（间距300m）
    wells_list = [(0, 0, Q), (300, 0, Q)]
    s_two_wells = superposition_principle(
        wells_list, x_obs, y_obs, t_range, T, S, method='theis'
    )
    
    # 干扰系数
    interference = s_two_wells / s_single
    
    print(f"\n分析配置：")
    print(f"  井1: (0, 0), Q={Q} m³/day")
    print(f"  井2: (300, 0), Q={Q} m³/day")
    print(f"  观测点: ({x_obs}, {y_obs})")
    print(f"  井间距: 300 m")
    
    print(f"\n在不同时间的干扰分析：")
    for t_i in [1, 10, 100]:
        idx = np.argmin(np.abs(t_range - t_i))
        print(f"\n  t = {t_i} day:")
        print(f"    单井降深: {s_single[idx]:.2f} m")
        print(f"    双井降深: {s_two_wells[idx]:.2f} m")
        print(f"    干扰系数: {interference[idx]:.2f}")
    
    return t_range, s_single, s_two_wells, interference


def experiment_5_pumping_optimization():
    """
    实验5：抽水量优化
    """
    print("\n" + "="*60)
    print("实验5：抽水量优化")
    print("="*60)
    
    # 含水层参数
    T = 500
    S = 0.0002
    h0 = 50  # 初始水头
    h_min = 45  # 最小水位
    t = 100  # 预测时间
    
    # 井的位置（已确定）
    well_locations = np.array([
        [0, 0],
        [500, 0],
        [250, 433],
        [500, 866]
    ])
    n_wells = len(well_locations)
    
    # 每口井的最大抽水量
    Q_max = np.array([1500, 1500, 1500, 1500])
    
    # 约束点（敏感区域）
    constraint_points = np.array([
        [250, 200],   # 点1
        [400, 400],   # 点2
        [250, 650],   # 点3
    ])
    
    print(f"\n优化问题设置：")
    print(f"  井数量: {n_wells}")
    print(f"  初始水头: {h0} m")
    print(f"  最小水位: {h_min} m")
    print(f"  单井上限: {Q_max[0]} m³/day")
    print(f"  约束点数: {len(constraint_points)}")
    
    # 情景1：无约束（最大抽水）
    print(f"\n情景1：无约束最大抽水")
    Q_no_constraint = Q_max.copy()
    total_Q_no = np.sum(Q_no_constraint)
    
    wells_list = [(well_locations[i, 0], well_locations[i, 1], Q_no_constraint[i]) 
                  for i in range(n_wells)]
    s_no = superposition_principle(
        wells_list,
        constraint_points[:, 0],
        constraint_points[:, 1],
        t, T, S, method='cooper_jacob'
    )
    h_no = h0 - s_no
    
    print(f"  总抽水量: {total_Q_no:.0f} m³/day")
    print(f"  约束点水头:")
    for i, h in enumerate(h_no):
        status = "✓" if h >= h_min else "✗"
        print(f"    点{i+1}: {h:.2f} m {status}")
    
    # 情景2：优化（线性规划）
    print(f"\n情景2：线性规划优化")
    result_lp = optimize_pumping_rates(
        well_locations, T, S, h0, h_min, Q_max,
        constraint_points, t, method='linear'
    )
    
    if result_lp['success']:
        print(f"  优化成功！")
        print(f"  最优抽水量:")
        for i, Q in enumerate(result_lp['Q_opt']):
            print(f"    井{i+1}: {Q:.0f} m³/day")
        print(f"  总抽水量: {result_lp['total_Q']:.0f} m³/day")
        print(f"  约束点水头:")
        for i, h in enumerate(result_lp['h_constraint']):
            status = "✓" if h >= h_min else "✗"
            print(f"    点{i+1}: {h:.2f} m {status}")
    else:
        print(f"  优化失败: {result_lp['message']}")
    
    # 情景3：优化（非线性）
    print(f"\n情景3：非线性优化（Theis）")
    result_nlp = optimize_pumping_rates(
        well_locations, T, S, h0, h_min, Q_max,
        constraint_points, t, method='nonlinear'
    )
    
    if result_nlp['success']:
        print(f"  优化成功！")
        print(f"  总抽水量: {result_nlp['total_Q']:.0f} m³/day")
        print(f"  最小约束点水头: {np.min(result_nlp['h_constraint']):.2f} m")
    else:
        print(f"  优化失败: {result_nlp['message']}")
    
    return {
        'well_locations': well_locations,
        'constraint_points': constraint_points,
        'Q_no_constraint': Q_no_constraint,
        'h_no': h_no,
        'result_lp': result_lp,
        'result_nlp': result_nlp
    }


def experiment_6_sensitivity_analysis():
    """
    实验6：敏感性分析
    """
    print("\n" + "="*60)
    print("实验6：敏感性分析")
    print("="*60)
    
    # 基准参数
    Q_base = 1000
    T_base = 500
    S_base = 0.0002
    r = 100
    t = 10
    
    # 计算基准降深
    s_base = theis_solution(r, t, Q_base, T_base, S_base)
    
    print(f"\n基准参数：")
    print(f"  Q = {Q_base} m³/day")
    print(f"  T = {T_base} m²/day")
    print(f"  S = {S_base}")
    print(f"  基准降深: {s_base:.2f} m")
    
    # 敏感性分析
    factors = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
    
    # Q的影响
    print(f"\nQ的影响（T, S固定）：")
    s_Q = [theis_solution(r, t, Q_base*f, T_base, S_base) for f in factors]
    for f, s in zip(factors, s_Q):
        sens = (s - s_base) / s_base * 100
        print(f"  Q×{f:.2f}: s={s:.2f}m, 变化{sens:+.1f}%")
    
    # T的影响
    print(f"\nT的影响（Q, S固定）：")
    s_T = [theis_solution(r, t, Q_base, T_base*f, S_base) for f in factors]
    for f, s in zip(factors, s_T):
        sens = (s - s_base) / s_base * 100
        print(f"  T×{f:.2f}: s={s:.2f}m, 变化{sens:+.1f}%")
    
    # S的影响
    print(f"\nS的影响（Q, T固定）：")
    s_S = [theis_solution(r, t, Q_base, T_base, S_base*f) for f in factors]
    for f, s in zip(factors, s_S):
        sens = (s - s_base) / s_base * 100
        print(f"  S×{f:.2f}: s={s:.2f}m, 变化{sens:+.1f}%")
    
    return factors, s_Q, s_T, s_S, s_base


def plot_results(exp1, exp2, exp3, exp4, exp5, exp6):
    """绘制所有结果"""
    
    fig = plt.figure(figsize=(20, 14))
    gs = GridSpec(3, 4, figure=fig, hspace=0.35, wspace=0.35)
    
    # 图1: Theis vs Cooper-Jacob
    ax1 = fig.add_subplot(gs[0, 0])
    t, s_theis, s_cooper, u = exp1
    ax1.loglog(t, s_theis, 'b-', linewidth=2, label='Theis')
    ax1.loglog(t, s_cooper, 'r--', linewidth=2, label='Cooper-Jacob')
    ax1.axvline(25*100**2*0.0002/500, color='gray', linestyle=':', 
               label=f't > {25*100**2*0.0002/500:.2f}d (u<0.01)')
    ax1.set_xlabel('时间 (day)', fontsize=11)
    ax1.set_ylabel('降深 (m)', fontsize=11)
    ax1.set_title('Theis vs Cooper-Jacob解', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3, which='both')
    
    # 图2: u值变化
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.loglog(t, u, 'g-', linewidth=2)
    ax2.axhline(0.01, color='red', linestyle='--', linewidth=2, 
               label='u = 0.01 (CJ适用)')
    ax2.set_xlabel('时间 (day)', fontsize=11)
    ax2.set_ylabel('u值', fontsize=11)
    ax2.set_title('Theis参数u vs 时间', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3, which='both')
    
    # 图3: 单井降落漏斗2D
    ax3 = fig.add_subplot(gs[0, 2])
    X, Y, s, r_profile, s_profile = exp2
    levels = [0.5, 1, 2, 3, 4, 5, 6, 7]
    cs = ax3.contourf(X, Y, s, levels=levels, cmap='RdYlBu_r')
    ax3.contour(X, Y, s, levels=levels, colors='black', linewidths=0.5, alpha=0.3)
    ax3.plot(0, 0, 'k*', markersize=15, label='抽水井')
    ax3.set_xlabel('x (m)', fontsize=11)
    ax3.set_ylabel('y (m)', fontsize=11)
    ax3.set_title('单井降落漏斗', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.axis('equal')
    plt.colorbar(cs, ax=ax3, label='降深 (m)')
    
    # 图4: 径向降深剖面
    ax4 = fig.add_subplot(gs[0, 3])
    ax4.semilogx(r_profile[r_profile > 0], s_profile[r_profile > 0], 
                'b-', linewidth=2)
    ax4.set_xlabel('径向距离 (m)', fontsize=11)
    ax4.set_ylabel('降深 (m)', fontsize=11)
    ax4.set_title('径向降深剖面', fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.invert_yaxis()
    
    # 图5: 多井降落漏斗
    ax5 = fig.add_subplot(gs[1, 0])
    X, Y, s_total, wellfield, contributions = exp3
    cs = ax5.contourf(X, Y, s_total, levels=20, cmap='RdYlBu_r')
    ax5.contour(X, Y, s_total, levels=10, colors='black', linewidths=0.5, alpha=0.3)
    for well in wellfield.wells:
        ax5.plot(well.x, well.y, 'k*', markersize=12)
        ax5.text(well.x, well.y+50, well.name, ha='center', fontsize=8)
    ax5.set_xlabel('x (m)', fontsize=11)
    ax5.set_ylabel('y (m)', fontsize=11)
    ax5.set_title('多井系统降落漏斗', fontsize=13, fontweight='bold')
    plt.colorbar(cs, ax=ax5, label='降深 (m)')
    
    # 图6: 井间干扰
    ax6 = fig.add_subplot(gs[1, 1])
    t_range, s_single, s_two_wells, interference = exp4
    ax6.semilogx(t_range, s_single, 'b-', linewidth=2, label='单井')
    ax6.semilogx(t_range, s_two_wells, 'r-', linewidth=2, label='双井')
    ax6.set_xlabel('时间 (day)', fontsize=11)
    ax6.set_ylabel('降深 (m)', fontsize=11)
    ax6.set_title('井间干扰', fontsize=13, fontweight='bold')
    ax6.legend(fontsize=10)
    ax6.grid(True, alpha=0.3)
    
    # 图7: 干扰系数
    ax7 = fig.add_subplot(gs[1, 2])
    ax7.semilogx(t_range, interference, 'g-', linewidth=2)
    ax7.axhline(1, color='gray', linestyle='--', alpha=0.5)
    ax7.set_xlabel('时间 (day)', fontsize=11)
    ax7.set_ylabel('干扰系数', fontsize=11)
    ax7.set_title('干扰系数 vs 时间', fontsize=13, fontweight='bold')
    ax7.grid(True, alpha=0.3)
    
    # 图8: 优化前后对比
    ax8 = fig.add_subplot(gs[1, 3])
    opt_data = exp5
    well_labels = [f'井{i+1}' for i in range(len(opt_data['well_locations']))]
    x_pos = np.arange(len(well_labels))
    
    ax8.bar(x_pos - 0.2, opt_data['Q_no_constraint'], 0.4, 
           label='优化前', alpha=0.7, color='lightcoral')
    if opt_data['result_lp']['success']:
        ax8.bar(x_pos + 0.2, opt_data['result_lp']['Q_opt'], 0.4,
               label='优化后', alpha=0.7, color='lightblue')
    ax8.set_xticks(x_pos)
    ax8.set_xticklabels(well_labels)
    ax8.set_ylabel('抽水量 (m³/day)', fontsize=11)
    ax8.set_title('优化前后抽水量对比', fontsize=13, fontweight='bold')
    ax8.legend(fontsize=10)
    ax8.grid(True, alpha=0.3, axis='y')
    
    # 图9: 约束点水头
    ax9 = fig.add_subplot(gs[2, 0])
    constraint_labels = [f'点{i+1}' for i in range(len(opt_data['constraint_points']))]
    x_pos = np.arange(len(constraint_labels))
    
    ax9.plot(x_pos, opt_data['h_no'], 'ro-', markersize=10, linewidth=2,
            label='优化前')
    if opt_data['result_lp']['success']:
        ax9.plot(x_pos, opt_data['result_lp']['h_constraint'], 'bo-',
                markersize=10, linewidth=2, label='优化后')
    ax9.axhline(45, color='red', linestyle='--', linewidth=2, label='最小水位')
    ax9.set_xticks(x_pos)
    ax9.set_xticklabels(constraint_labels)
    ax9.set_ylabel('水头 (m)', fontsize=11)
    ax9.set_title('约束点水头', fontsize=13, fontweight='bold')
    ax9.legend(fontsize=10)
    ax9.grid(True, alpha=0.3)
    
    # 图10: Q敏感性
    ax10 = fig.add_subplot(gs[2, 1])
    factors, s_Q, s_T, s_S, s_base = exp6
    ax10.plot(factors, s_Q, 'ro-', linewidth=2, markersize=8, label='Q变化')
    ax10.axhline(s_base, color='gray', linestyle='--', alpha=0.5)
    ax10.set_xlabel('参数倍数', fontsize=11)
    ax10.set_ylabel('降深 (m)', fontsize=11)
    ax10.set_title('Q敏感性分析', fontsize=13, fontweight='bold')
    ax10.legend(fontsize=10)
    ax10.grid(True, alpha=0.3)
    
    # 图11: T敏感性
    ax11 = fig.add_subplot(gs[2, 2])
    ax11.plot(factors, s_T, 'bo-', linewidth=2, markersize=8, label='T变化')
    ax11.axhline(s_base, color='gray', linestyle='--', alpha=0.5)
    ax11.set_xlabel('参数倍数', fontsize=11)
    ax11.set_ylabel('降深 (m)', fontsize=11)
    ax11.set_title('T敏感性分析', fontsize=13, fontweight='bold')
    ax11.legend(fontsize=10)
    ax11.grid(True, alpha=0.3)
    
    # 图12: S敏感性
    ax12 = fig.add_subplot(gs[2, 3])
    ax12.plot(factors, s_S, 'go-', linewidth=2, markersize=8, label='S变化')
    ax12.axhline(s_base, color='gray', linestyle='--', alpha=0.5)
    ax12.set_xlabel('参数倍数', fontsize=11)
    ax12.set_ylabel('降深 (m)', fontsize=11)
    ax12.set_title('S敏感性分析', fontsize=13, fontweight='bold')
    ax12.legend(fontsize=10)
    ax12.grid(True, alpha=0.3)
    
    plt.savefig('case_16_pumping_optimization_results.png', dpi=300, bbox_inches='tight')
    print("\n图片已保存: case_16_pumping_optimization_results.png")
    
    plt.show()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("案例16：地下水开采优化")
    print("="*60)
    print("\n本案例演示抽水井模拟与开采方案优化")
    
    # 运行所有实验
    exp1 = experiment_1_theis_vs_cooper_jacob()
    exp2 = experiment_2_single_well_cone()
    exp3 = experiment_3_multi_well_superposition()
    exp4 = experiment_4_well_interference()
    exp5 = experiment_5_pumping_optimization()
    exp6 = experiment_6_sensitivity_analysis()
    
    # 绘图
    print("\n生成结果图...")
    plot_results(exp1, exp2, exp3, exp4, exp5, exp6)
    
    # 总结
    print("\n" + "="*60)
    print("案例16完成总结")
    print("="*60)
    
    print(f"\n核心发现：")
    print(f"1. Cooper-Jacob适用于大时间（t > 25r²S/T）")
    print(f"2. 多井系统遵循叠加原理")
    print(f"3. 井间干扰随时间增加")
    print(f"4. 优化可在满足约束下最大化开采量")
    print(f"5. 降深对Q最敏感，对S最不敏感")
    
    print(f"\n学习要点：")
    print(f"✓ Theis解析解")
    print(f"✓ Cooper-Jacob近似")
    print(f"✓ 叠加原理")
    print(f"✓ 井间干扰")
    print(f"✓ 线性规划优化")
    print(f"✓ 敏感性分析")
    
    print("\n✅ 案例16执行完成！")


if __name__ == '__main__':
    main()
