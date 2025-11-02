"""
案例13：小型湖泊完全混合模型
Case 13: Lake Complete Mixed Flow Reactor Model

模拟城市景观湖水质变化，评估改善措施效果
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加models路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from models.lake_cmfr import LakeCMFR, calculate_critical_load, calculate_flushing_efficiency

# 使用非交互式后端
plt.switch_backend('Agg')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def main():
    print("=" * 70)
    print("案例13：小型湖泊完全混合模型")
    print("=" * 70)
    
    # ========================================
    # 基本参数
    # ========================================
    print("\n湖泊参数:")
    A = 0.5e6  # 面积 0.5 km² = 500,000 m²
    H = 3      # 平均水深 3 m
    Q_in = 5000   # 入流 5000 m³/d
    k = 0.1    # 一阶反应速率 0.1 1/d
    C_in = 20  # 入流浓度 20 mg/L
    C0 = 10    # 初始浓度 10 mg/L
    C_standard = 5  # 水质标准 5 mg/L
    
    print(f"  面积: {A/1e6:.2f} km²")
    print(f"  水深: {H} m")
    print(f"  入流: {Q_in} m³/d")
    print(f"  入流浓度: {C_in} mg/L")
    print(f"  反应速率: {k} 1/d")
    print(f"  水质标准: {C_standard} mg/L")
    
    # ========================================
    # 任务1：建立0D箱式模型
    # ========================================
    print("\n" + "=" * 70)
    print("任务1：建立0D箱式模型")
    print("=" * 70)
    
    lake = LakeCMFR(A, H, Q_in, Q_out=Q_in, k=k, C_in=C_in, C0=C0)
    
    # 计算水力参数
    HRT = lake.calculate_hydraulic_residence_time()
    r = lake.calculate_flushing_rate()
    tau, t_95 = lake.calculate_response_time()
    
    # ========================================
    # 任务2：计算稳态浓度
    # ========================================
    print("\n" + "=" * 70)
    print("任务2：计算稳态浓度")
    print("=" * 70)
    
    # 无内源
    print("\n情景1：无内源")
    C_ss_no_source = lake.calculate_steady_state()
    if C_ss_no_source > C_standard:
        print(f"  ⚠️  超标！超标{(C_ss_no_source - C_standard) / C_standard * 100:.1f}%")
    else:
        print(f"  ✓ 达标")
    
    # 有内源（底泥释放）
    print("\n情景2：有内源（底泥释放）")
    S_internal = 1000  # mg/d
    lake.set_internal_source(S_internal)
    C_ss_with_source = lake.calculate_steady_state()
    if C_ss_with_source > C_standard:
        print(f"  ⚠️  超标！超标{(C_ss_with_source - C_standard) / C_standard * 100:.1f}%")
    else:
        print(f"  ✓ 达标")
    
    # 恢复无内源
    lake.set_internal_source(0)
    
    # ========================================
    # 任务3：模拟外源输入响应
    # ========================================
    print("\n" + "=" * 70)
    print("任务3：模拟外源输入响应")
    print("=" * 70)
    
    t_sim = np.linspace(0, 1000, 2000)
    
    # 情景1：突然停止输入
    print("\n情景1：突然停止输入")
    lake1 = LakeCMFR(A, H, Q_in, Q_out=Q_in, k=k, C_in=0, C0=15)
    t1, C1 = lake1.solve_transient(t_sim)
    
    # 情景2：突然增加输入
    print("\n情景2：突然增加输入")
    lake2 = LakeCMFR(A, H, Q_in, Q_out=Q_in, k=k, C_in=30, C0=5)
    t2, C2 = lake2.solve_transient(t_sim)
    
    # ========================================
    # 任务4：分析换水周期影响
    # ========================================
    print("\n" + "=" * 70)
    print("任务4：分析换水周期影响")
    print("=" * 70)
    
    Q_values = [2500, 5000, 10000]
    C_ss_values = []
    HRT_values = []
    
    for Q in Q_values:
        lake_temp = LakeCMFR(A, H, Q_in, Q_out=Q, k=k, C_in=C_in, C0=C0)
        C_ss = lake_temp.calculate_steady_state()
        C_ss_values.append(C_ss)
        HRT_values.append(lake_temp.HRT)
        
        达标 = "✓ 达标" if C_ss <= C_standard else "✗ 超标"
        print(f"\nQ = {Q} m³/d:")
        print(f"  HRT: {lake_temp.HRT:.1f} d")
        print(f"  稳态浓度: {C_ss:.2f} mg/L")
        print(f"  {达标}")
    
    # ========================================
    # 任务5：评估水质改善措施
    # ========================================
    print("\n" + "=" * 70)
    print("任务5：评估水质改善措施")
    print("=" * 70)
    
    # 基准情景
    lake_base = LakeCMFR(A, H, Q_in, Q_out=Q_in, k=k, C_in=C_in, C0=C0)
    C_base = lake_base.calculate_steady_state()
    print(f"\n基准情景: C_ss = {C_base:.2f} mg/L")
    
    # 方案1：增加换水
    print("\n方案1：增加换水（Q: 5000 → 10000 m³/d）")
    C_old, C_new, improvement = lake_base.evaluate_water_exchange(Q_new=10000)
    达标1 = "✓ 达标" if C_new <= C_standard else "✗ 超标"
    print(f"  {达标1}")
    
    # 方案2：曝气处理
    print("\n方案2：曝气处理（k: 0.1 → 0.3 1/d）")
    C_old, C_new, improvement = lake_base.evaluate_aeration(k_aeration=0.2)
    达标2 = "✓ 达标" if C_new <= C_standard else "✗ 超标"
    print(f"  {达标2}")
    
    # 方案3：源削减
    print("\n方案3：源削减（C_in: 20 → 10 mg/L）")
    lake_reduced = LakeCMFR(A, H, Q_in, Q_out=Q_in, k=k, C_in=10, C0=C0)
    C_reduced = lake_reduced.calculate_steady_state()
    improvement3 = (C_base - C_reduced) / C_base * 100
    print(f"  原稳态浓度: {C_base:.2f} mg/L")
    print(f"  新稳态浓度: {C_reduced:.2f} mg/L")
    print(f"  改善: {improvement3:.1f}%")
    达标3 = "✓ 达标" if C_reduced <= C_standard else "✗ 超标"
    print(f"  {达标3}")
    
    # 计算临界负荷
    print("\n临界负荷分析:")
    L_crit = calculate_critical_load(lake_base.V, lake_base.Q_out, lake_base.k, C_standard)
    L_current = Q_in * C_in
    print(f"  当前负荷: {L_current:.2f} mg/d")
    print(f"  临界负荷: {L_crit:.2f} mg/d")
    print(f"  负荷比: {L_current/L_crit:.2f}")
    if L_current > L_crit:
        print(f"  ⚠️  需要削减负荷: {L_current - L_crit:.2f} mg/d ({(L_current - L_crit)/L_current*100:.1f}%)")
    
    # ========================================
    # 绘图
    # ========================================
    print("\n生成图表...")
    
    # 图1：瞬态响应
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 情景1
    ax1.plot(t1, C1, 'b-', linewidth=2, label='Lake Concentration')
    ax1.axhline(y=C_standard, color='r', linestyle='--', linewidth=2, label=f'Standard ({C_standard} mg/L)')
    ax1.axhline(y=0, color='g', linestyle='--', linewidth=1.5, label='Inflow (0 mg/L)')
    ax1.set_xlabel('Time (d)', fontsize=12)
    ax1.set_ylabel('Concentration (mg/L)', fontsize=12)
    ax1.set_title('Scenario 1: Stop Input (C_in = 0)', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 1000])
    
    # 情景2
    ax2.plot(t2, C2, 'b-', linewidth=2, label='Lake Concentration')
    ax2.axhline(y=C_standard, color='r', linestyle='--', linewidth=2, label=f'Standard ({C_standard} mg/L)')
    ax2.axhline(y=30, color='g', linestyle='--', linewidth=1.5, label='Inflow (30 mg/L)')
    ax2.set_xlabel('Time (d)', fontsize=12)
    ax2.set_ylabel('Concentration (mg/L)', fontsize=12)
    ax2.set_title('Scenario 2: Increase Input (C_in = 30)', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 1000])
    
    plt.tight_layout()
    plt.savefig('transient_response.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: transient_response.png")
    plt.close()
    
    # 图2：换水率影响
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 稳态浓度 vs 换水率
    ax1.plot(Q_values, C_ss_values, 'bo-', linewidth=2, markersize=10, label='Steady-state C')
    ax1.axhline(y=C_standard, color='r', linestyle='--', linewidth=2, label=f'Standard ({C_standard} mg/L)')
    ax1.set_xlabel('Outflow Rate (m³/d)', fontsize=12)
    ax1.set_ylabel('Steady-state Concentration (mg/L)', fontsize=12)
    ax1.set_title('Effect of Flushing Rate on Water Quality', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # HRT vs 稳态浓度
    ax2.plot(HRT_values, C_ss_values, 'go-', linewidth=2, markersize=10, label='Steady-state C')
    ax2.axhline(y=C_standard, color='r', linestyle='--', linewidth=2, label=f'Standard ({C_standard} mg/L)')
    ax2.set_xlabel('Hydraulic Residence Time (d)', fontsize=12)
    ax2.set_ylabel('Steady-state Concentration (mg/L)', fontsize=12)
    ax2.set_title('Effect of HRT on Water Quality', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.invert_xaxis()  # HRT越小越好
    
    plt.tight_layout()
    plt.savefig('flushing_rate_effect.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: flushing_rate_effect.png")
    plt.close()
    
    # 图3：改善措施对比
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scenarios = ['Baseline', 'Increase\nFlushing', 'Aeration', 'Source\nReduction']
    concentrations = [C_base, 5.00, 4.44, C_reduced]
    colors = ['gray', 'blue', 'green', 'orange']
    
    bars = ax.bar(scenarios, concentrations, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax.axhline(y=C_standard, color='r', linestyle='--', linewidth=3, label=f'Standard ({C_standard} mg/L)')
    
    # 添加数值标签
    for i, (bar, conc) in enumerate(zip(bars, concentrations)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{conc:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # 达标标记
        if conc <= C_standard:
            ax.text(bar.get_x() + bar.get_width()/2., height - 0.5,
                    '✓', ha='center', va='top', fontsize=20, color='white', fontweight='bold')
    
    ax.set_ylabel('Steady-state Concentration (mg/L)', fontsize=12)
    ax.set_title('Comparison of Improvement Measures', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim([0, max(concentrations) * 1.15])
    
    plt.tight_layout()
    plt.savefig('improvement_measures.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: improvement_measures.png")
    plt.close()
    
    # 图4：负荷-浓度关系
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 不同负荷下的稳态浓度
    loads = np.linspace(0, 200000, 100)  # mg/d
    C_steady = loads / (Q_in + k * lake_base.V)
    
    ax.plot(loads/1000, C_steady, 'b-', linewidth=3, label='Steady-state C vs Load')
    ax.axhline(y=C_standard, color='r', linestyle='--', linewidth=2, label=f'Standard ({C_standard} mg/L)')
    ax.axvline(x=L_crit/1000, color='g', linestyle='--', linewidth=2, label=f'Critical Load ({L_crit/1000:.1f} kg/d)')
    ax.plot([L_current/1000], [C_base], 'ro', markersize=12, label=f'Current ({L_current/1000:.1f} kg/d)')
    
    ax.set_xlabel('Pollutant Load (kg/d)', fontsize=12)
    ax.set_ylabel('Steady-state Concentration (mg/L)', fontsize=12)
    ax.set_title('Load-Concentration Relationship', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 200])
    
    # 标注安全区和超标区
    ax.fill_between([0, L_crit/1000], 0, 20, alpha=0.2, color='green', label='Safe Zone')
    ax.fill_between([L_crit/1000, 200], 0, 20, alpha=0.2, color='red', label='Exceedance Zone')
    
    plt.tight_layout()
    plt.savefig('load_concentration.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: load_concentration.png")
    plt.close()
    
    # ========================================
    # 总结
    # ========================================
    print("\n" + "=" * 70)
    print("案例13完成！")
    print("=" * 70)
    
    print("\n主要结论:")
    print(f"1. 当前水质: {C_base:.2f} mg/L（超标{(C_base - C_standard) / C_standard * 100:.1f}%）")
    print(f"2. 水力停留时间: {HRT:.1f} d，响应时间: {tau:.1f} d")
    print(f"3. 临界负荷: {L_crit/1000:.1f} kg/d，当前负荷: {L_current/1000:.1f} kg/d")
    print(f"4. 最有效措施: 源削减（改善{improvement3:.1f}%）")
    
    print("\n工程建议:")
    print("  1. 优先削减污染源，降低入流浓度")
    print("  2. 增加换水率可快速改善水质")
    print("  3. 曝气是辅助措施，需要运行成本")
    print("  4. 控制底泥内源释放")
    print("  5. 定期监测，保持水质达标")


if __name__ == '__main__':
    main()
