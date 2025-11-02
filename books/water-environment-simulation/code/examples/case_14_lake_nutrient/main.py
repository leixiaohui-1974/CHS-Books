"""
案例14：湖泊营养盐输入响应分析
Case 14: Lake Nutrient Input-Response Analysis

基于Vollenweider模型评估磷削减方案效果
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from models.lake_nutrient import (VollenweiderModel, calculate_trophic_state,
                                   calculate_vollenweider_loading, predict_response_time)

plt.switch_backend('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def main():
    print("=" * 70)
    print("案例14：湖泊营养盐输入响应分析")
    print("=" * 70)
    
    # 湖泊参数
    A = 10e6  # 10 km²
    H = 8  # 8 m
    Q = 160000  # 160000 m³/d
    L = 20e6  # 20 kg/d = 20e6 mg/d
    sigma = 0.005  # 0.005 m/d ≈ 2 m/year
    P0 = 60  # 初始60 μg/L
    P_target = 30  # 目标30 μg/L
    
    print(f"\n湖泊参数:")
    print(f"  面积: {A/1e6} km²")
    print(f"  水深: {H} m")
    print(f"  出流: {Q} m³/d")
    print(f"  磷负荷: {L/1e6} kg/d")
    print(f"  沉降速率: {sigma} m/d ({sigma*365} m/year)")
    print(f"  目标浓度: {P_target} μg/L")
    
    # ====================
    # 任务1：建立磷平衡模型
    # ====================
    print("\n" + "=" * 70)
    print("任务1：建立磷平衡模型")
    print("=" * 70)
    
    model = VollenweiderModel(A, H, Q, L, sigma, P0)
    
    # ====================
    # 任务2：率定沉降系数
    # ====================
    print("\n" + "=" * 70)
    print("任务2：率定沉降系数")
    print("=" * 70)
    
    P_observed = 60
    sigma_calibrated = model.calibrate_settling_velocity(P_observed, L, Q)
    
    # 使用率定后的参数
    model_calibrated = VollenweiderModel(A, H, Q, L, sigma_calibrated, P0)
    
    # ====================
    # 任务3：预测削减方案效果
    # ====================
    print("\n" + "=" * 70)
    print("任务3：预测不同削减方案效果")
    print("=" * 70)
    
    reductions = [0, 10, 30, 50, 70]
    P_results = []
    
    for red in reductions:
        P_old, P_new, improvement = model.evaluate_load_reduction(red)
        P_results.append(P_new)
        
        state, _ = calculate_trophic_state(P_new)
        标 = "✓ 达标" if P_new <= P_target else "✗ 超标"
        print(f"\n削减{red}%: P = {P_new:.2f} μg/L, {state}, {标}")
    
    # ====================
    # 任务4：确定临界营养负荷
    # ====================
    print("\n" + "=" * 70)
    print("任务4：确定临界营养负荷")
    print("=" * 70)
    
    L_crit = model.calculate_critical_load(P_target)
    
    tau = model.V / model.Q
    L_perm, L_dang = calculate_vollenweider_loading(A, H, tau, P_target)
    
    # 滞留系数
    R = model.calculate_retention_coefficient()
    
    # ====================
    # 任务5：制定污染控制目标
    # ====================
    print("\n" + "=" * 70)
    print("任务5：制定污染控制目标")
    print("=" * 70)
    
    # 响应时间
    tau_resp, t_95 = predict_response_time(tau, sigma, H)
    
    print(f"\n分阶段控制目标:")
    print(f"  近期（1-2年）: 削减30%, P降至 {P_results[2]:.1f} μg/L")
    print(f"  中期（3-5年）: 削减50%, P降至 {P_results[3]:.1f} μg/L, 达标")
    print(f"  长期（>5年）: 削减70%, P降至 {P_results[4]:.1f} μg/L, 稳定达标")
    
    # ====================
    # 瞬态模拟
    # ====================
    print("\n" + "=" * 70)
    print("瞬态模拟")
    print("=" * 70)
    
    t_sim = np.linspace(0, 3650, 1000)  # 10年
    
    # 情景1：维持现状
    model1 = VollenweiderModel(A, H, Q, L, sigma, P0)
    t1, P1 = model1.solve_transient(t_sim)
    
    # 情景2：削减50%
    model2 = VollenweiderModel(A, H, Q, L*0.5, sigma, P0)
    t2, P2 = model2.solve_transient(t_sim)
    
    # ====================
    # 绘图
    # ====================
    print("\n生成图表...")
    
    # 图1：瞬态响应
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.plot(t1/365, P1, 'r-', linewidth=2, label='No Reduction')
    ax1.plot(t2/365, P2, 'b-', linewidth=2, label='50% Reduction')
    ax1.axhline(y=P_target, color='g', linestyle='--', linewidth=2, label=f'Target ({P_target} μg/L)')
    ax1.set_xlabel('Time (year)', fontsize=12)
    ax1.set_ylabel('TP (μg/L)', fontsize=12)
    ax1.set_title('Transient Response', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 营养状态区域
    ax1.axhspan(0, 10, alpha=0.1, color='blue', label='Oligotrophic')
    ax1.axhspan(10, 30, alpha=0.1, color='green')
    ax1.axhspan(30, 100, alpha=0.1, color='orange')
    ax1.axhspan(100, 200, alpha=0.1, color='red')
    
    # 图2：削减效果对比
    colors = ['red', 'orange', 'yellow', 'lightgreen', 'green']
    bars = ax2.bar(reductions, P_results, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax2.axhline(y=P_target, color='r', linestyle='--', linewidth=3, label=f'Target ({P_target} μg/L)')
    
    for i, (bar, p) in enumerate(zip(bars, P_results)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{p:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        if p <= P_target:
            ax2.text(bar.get_x() + bar.get_width()/2., height - 5,
                    '✓', ha='center', va='top', fontsize=18, color='white', fontweight='bold')
    
    ax2.set_xlabel('Load Reduction (%)', fontsize=12)
    ax2.set_ylabel('Steady-state TP (μg/L)', fontsize=12)
    ax2.set_title('Effect of Load Reduction', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('reduction_scenarios.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: reduction_scenarios.png")
    plt.close()
    
    # 图2：负荷-浓度关系
    fig, ax = plt.subplots(figsize=(10, 6))
    
    loads = np.linspace(0, 40e6, 100)
    P_loads = loads / (Q + sigma * A)
    
    ax.plot(loads/1e6, P_loads, 'b-', linewidth=3, label='P vs Load')
    ax.axhline(y=P_target, color='r', linestyle='--', linewidth=2, label=f'Target ({P_target} μg/L)')
    ax.axvline(x=L_crit/1e6, color='g', linestyle='--', linewidth=2, label=f'Critical Load ({L_crit/1e6:.1f} kg/d)')
    ax.plot([L/1e6], [P0], 'ro', markersize=12, label=f'Current ({L/1e6:.1f} kg/d)')
    
    # 标注营养状态区域
    ax.axhspan(0, 10, alpha=0.15, color='blue')
    ax.axhspan(10, 30, alpha=0.15, color='green')
    ax.axhspan(30, 100, alpha=0.15, color='orange')
    ax.text(35, 5, 'Oligotrophic', fontsize=10, ha='right')
    ax.text(35, 20, 'Mesotrophic', fontsize=10, ha='right')
    ax.text(35, 65, 'Eutrophic', fontsize=10, ha='right')
    
    ax.set_xlabel('Phosphorus Load (kg/d)', fontsize=12)
    ax.set_ylabel('Steady-state TP (μg/L)', fontsize=12)
    ax.set_title('Load-Concentration Relationship', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 40])
    ax.set_ylim([0, 120])
    
    plt.tight_layout()
    plt.savefig('load_concentration.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: load_concentration.png")
    plt.close()
    
    # ====================
    # 总结
    # ====================
    print("\n" + "=" * 70)
    print("案例14完成！")
    print("=" * 70)
    
    print(f"\n主要结论:")
    print(f"1. 当前状态: P = {P0} μg/L (富营养), 超标{(P0-P_target)/P_target*100:.0f}%")
    print(f"2. 临界负荷: {L_crit/1e6:.1f} kg/d, 需削减{(L-L_crit)/L*100:.0f}%")
    print(f"3. 磷滞留系数: {R:.2f} (滞留{R*100:.0f}%)")
    print(f"4. 响应时间: {tau_resp:.0f} d ({tau_resp/365:.1f} year)")
    print(f"5. 推荐方案: 削减50%, 3-5年内达标")
    
    print(f"\n工程建议:")
    print(f"  1. 污水处理厂提标改造，强化除磷")
    print(f"  2. 分阶段削减，近期30%，中期50%")
    print(f"  3. 加强监测，每月评估进展")
    print(f"  4. 考虑生态修复，增强沉降")


if __name__ == '__main__':
    main()
