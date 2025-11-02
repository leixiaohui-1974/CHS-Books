"""
案例4：Streeter-Phelps溶解氧模型
Streeter-Phelps Dissolved Oxygen Model

演示：
1. 基本S-P模型求解（氧垂曲线）
2. 临界点计算
3. 参数影响分析（L₀、kd、ka）
4. 温度影响分析
5. 复氧系数计算
6. 工程应用（排放标准）
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.dissolved_oxygen import StreeterPhelps, calculate_reaeration_coefficient


def main():
    """主函数"""
    print("=" * 70)
    print("案例4：Streeter-Phelps溶解氧模型")
    print("=" * 70)
    print()
    
    # ========================================
    # 任务1：基本S-P模型求解
    # ========================================
    print("任务1：基本S-P模型求解")
    print("-" * 70)
    
    # 参数设置
    L0 = 30.0       # 初始BOD (mg/L)
    DO0 = 6.0       # 初始DO (mg/L)
    DOs = 9.09      # 饱和DO (mg/L, 20°C)
    D0 = DOs - DO0  # 初始DO亏损
    kd = 0.2        # BOD降解系数 (day⁻¹)
    ka = 0.4        # 复氧系数 (day⁻¹)
    T = 10.0        # 模拟时间 (day)
    u = 0.3         # 流速 (m/s)
    
    print(f"初始条件:")
    print(f"  初始BOD: L₀ = {L0} mg/L")
    print(f"  初始DO: DO₀ = {DO0} mg/L")
    print(f"  饱和DO: DOs = {DOs} mg/L")
    print(f"  初始亏损: D₀ = {D0:.2f} mg/L")
    print()
    
    print(f"水质参数:")
    print(f"  BOD降解系数: kd = {kd} day⁻¹")
    print(f"  复氧系数: ka = {ka} day⁻¹")
    print(f"  ka/kd比值: {ka/kd:.2f} （自净能力指标）")
    print()
    
    # 创建S-P模型
    model = StreeterPhelps(L0=L0, D0=D0, kd=kd, ka=ka, T=T, nt=1000)
    model.set_saturation_do(DOs)
    
    # 求解
    L, D, DO = model.solve()
    
    print("✓ S-P方程求解完成")
    print(f"  最终BOD: {L[-1]:.2f} mg/L")
    print(f"  最终DO: {DO[-1]:.2f} mg/L")
    print()
    
    # ========================================
    # 任务2：临界点分析
    # ========================================
    print("任务2：临界点分析")
    print("-" * 70)
    
    tc, Dc, DOc = model.calculate_critical_point()
    
    # 计算临界距离
    xc = u * tc * 86400 / 1000  # 转换为km
    
    print(f"临界点:")
    print(f"  临界时间: tc = {tc:.2f} 天")
    print(f"  临界距离: xc = {xc:.2f} km")
    print(f"  临界DO亏损: Dc = {Dc:.2f} mg/L")
    print(f"  临界DO浓度: DOc = {DOc:.2f} mg/L")
    print()
    
    # 水质评价
    if DOc >= 6.0:
        quality = "II类水（优）"
    elif DOc >= 5.0:
        quality = "III类水（良好）"
    elif DOc >= 4.0:
        quality = "IV类水（一般）"
    elif DOc >= 2.0:
        quality = "V类水（较差）"
    else:
        quality = "劣V类水（很差）"
    
    print(f"水质评价:")
    print(f"  临界点水质: {quality}")
    
    if DOc < 4.0:
        print(f"  ⚠️  低于鱼类生存要求（4 mg/L）")
    if DOc < 2.0:
        print(f"  ⚠️  严重缺氧，可能导致死鱼！")
    print()
    
    # ========================================
    # 任务3：参数影响分析
    # ========================================
    print("任务3：参数影响分析")
    print("-" * 70)
    
    # 3.1 L0影响
    print("\n3.1 初始BOD (L₀) 的影响:")
    L0_values = [20, 30, 40]
    results_L0 = {}
    
    for L0_test in L0_values:
        model_test = StreeterPhelps(L0=L0_test, D0=D0, kd=kd, ka=ka, T=T)
        model_test.set_saturation_do(DOs)
        _, _, DO_test = model_test.solve()
        tc_test, Dc_test, DOc_test = model_test.calculate_critical_point()
        results_L0[L0_test] = (DO_test, tc_test, DOc_test)
        print(f"  L₀ = {L0_test} mg/L: tc = {tc_test:.2f} 天, DOc = {DOc_test:.2f} mg/L")
    
    # 3.2 kd影响
    print("\n3.2 BOD降解系数 (kd) 的影响:")
    kd_values = [0.1, 0.2, 0.3]
    results_kd = {}
    
    for kd_test in kd_values:
        model_test = StreeterPhelps(L0=L0, D0=D0, kd=kd_test, ka=ka, T=T)
        model_test.set_saturation_do(DOs)
        _, _, DO_test = model_test.solve()
        tc_test, Dc_test, DOc_test = model_test.calculate_critical_point()
        results_kd[kd_test] = (DO_test, tc_test, DOc_test)
        print(f"  kd = {kd_test} day⁻¹: tc = {tc_test:.2f} 天, DOc = {DOc_test:.2f} mg/L")
    
    # 3.3 ka影响
    print("\n3.3 复氧系数 (ka) 的影响:")
    ka_values = [0.2, 0.4, 0.6]
    results_ka = {}
    
    for ka_test in ka_values:
        model_test = StreeterPhelps(L0=L0, D0=D0, kd=kd, ka=ka_test, T=T)
        model_test.set_saturation_do(DOs)
        _, _, DO_test = model_test.solve()
        tc_test, Dc_test, DOc_test = model_test.calculate_critical_point()
        results_ka[ka_test] = (DO_test, tc_test, DOc_test)
        print(f"  ka = {ka_test} day⁻¹: tc = {tc_test:.2f} 天, DOc = {DOc_test:.2f} mg/L")
        print(f"    → ka/kd = {ka_test/kd:.2f}")
    
    print("\n结论:")
    print("  - L₀增大 → DOc降低（污染加重）")
    print("  - kd增大 → tc提前，DOc变化复杂")
    print("  - ka增大 → tc延后，DOc升高（自净能力增强）")
    print("  - ka/kd > 1 是河流自净的关键条件")
    print()
    
    # ========================================
    # 任务4：温度影响分析
    # ========================================
    print("任务4：温度影响分析")
    print("-" * 70)
    
    temperatures = [10, 20, 30]
    results_temp = {}
    
    kd_20 = 0.2
    ka_20 = 0.4
    
    for T_water in temperatures:
        # 温度校正
        model_temp = StreeterPhelps(L0=L0, D0=D0, kd=0.2, ka=0.4, T=T)
        kd_T, ka_T = model_temp.temperature_correction(kd_20, ka_20, T_water)
        
        # 计算饱和DO
        DOs_T = model_temp.calculate_saturation_do(T_water)
        
        # 更新参数
        model_temp.kd = kd_T
        model_temp.ka = ka_T
        model_temp.DOs = DOs_T
        
        # 求解
        _, _, DO_temp = model_temp.solve()
        tc_temp, Dc_temp, DOc_temp = model_temp.calculate_critical_point()
        
        results_temp[T_water] = (DO_temp, tc_temp, DOc_temp, DOs_T)
        
        print(f"\n温度 {T_water}°C:")
        print(f"  饱和DO: DOs = {DOs_T:.2f} mg/L")
        print(f"  临界时间: tc = {tc_temp:.2f} 天")
        print(f"  临界DO: DOc = {DOc_temp:.2f} mg/L")
    
    print("\n温度影响总结:")
    print("  - 温度升高 → kd和ka都增大")
    print("  - 温度升高 → DOs降低")
    print("  - 综合效应: 夏季水质风险最大")
    print("  - 冬季: 降解慢，但DOs高")
    print("  - 夏季: 降解快，但DOs低，DOc最低")
    print()
    
    # ========================================
    # 任务5：复氧系数计算
    # ========================================
    print("任务5：复氧系数计算")
    print("-" * 70)
    
    u_river = 0.3  # m/s
    H_river = 1.5  # m
    
    print(f"\n河流参数:")
    print(f"  流速: u = {u_river} m/s")
    print(f"  水深: H = {H_river} m")
    print()
    
    # 三种公式
    ka_owens = calculate_reaeration_coefficient(u_river, H_river, 'Owens')
    print()
    ka_churchill = calculate_reaeration_coefficient(u_river, H_river, 'Churchill')
    print()
    ka_oconnor = calculate_reaeration_coefficient(u_river, H_river, 'OConnor-Dobbins')
    print()
    
    print("比较:")
    print(f"  Owens: ka = {ka_owens:.4f} day⁻¹ (浅水河流)")
    print(f"  Churchill: ka = {ka_churchill:.4f} day⁻¹ (大河)")
    print(f"  O'Connor-Dobbins: ka = {ka_oconnor:.4f} day⁻¹ (深水河流)")
    print(f"  平均值: ka = {(ka_owens + ka_churchill + ka_oconnor)/3:.4f} day⁻¹")
    print()
    
    # ========================================
    # 任务6：工程应用
    # ========================================
    print("任务6：工程应用 - 排放标准制定")
    print("-" * 70)
    
    # 目标: DOc ≥ 4 mg/L (保证鱼类生存)
    DO_target = 4.0
    D_target = DOs - DO_target
    
    print(f"\n目标: 临界DO ≥ {DO_target} mg/L (鱼类生存标准)")
    print(f"即: 临界亏损 Dc ≤ {D_target:.2f} mg/L")
    print()
    
    # 反推最大允许L0
    # 对于给定的kd和ka，Dc = f(L0)
    # 通过二分法或试错找到L0_max
    
    L0_test_values = np.linspace(10, 50, 50)
    DOc_values = []
    
    for L0_test in L0_test_values:
        model_test = StreeterPhelps(L0=L0_test, D0=D0, kd=kd, ka=ka, T=T)
        model_test.set_saturation_do(DOs)
        _, _, DOc_test = model_test.calculate_critical_point()
        DOc_values.append(DOc_test)
    
    # 找到DOc刚好等于4的L0
    DOc_array = np.array(DOc_values)
    idx = np.argmin(np.abs(DOc_array - DO_target))
    L0_max = L0_test_values[idx]
    
    print(f"反推结果:")
    print(f"  最大允许BOD: L₀_max ≈ {L0_max:.1f} mg/L")
    print(f"  此时临界DO: DOc ≈ {DOc_values[idx]:.2f} mg/L")
    print()
    
    print(f"排放标准建议:")
    print(f"  春秋季(20°C): BOD ≤ {L0_max:.0f} mg/L")
    print(f"  夏季(30°C): BOD ≤ {L0_max * 0.7:.0f} mg/L (更严格)")
    print(f"  冬季(10°C): BOD ≤ {L0_max * 1.3:.0f} mg/L (可放宽)")
    print()
    
    # ========================================
    # 绘图
    # ========================================
    print("生成图表...")
    
    # 图1：氧垂曲线（基本S-P模型）
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    
    # BOD降解曲线
    ax1.plot(model.t, L, 'b-', linewidth=2, label='BOD')
    ax1.axhline(y=L0*0.5, color='b', linestyle='--', linewidth=1, alpha=0.5, label='50% BOD')
    ax1.set_xlabel('时间 (天)', fontsize=11)
    ax1.set_ylabel('BOD (mg/L)', fontsize=11)
    ax1.set_title('BOD降解曲线', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # DO氧垂曲线
    ax2.plot(model.t, DO, 'r-', linewidth=2.5, label='DO')
    ax2.axhline(y=DOs, color='b', linestyle='--', linewidth=1, label=f'饱和DO ({DOs} mg/L)')
    ax2.axhline(y=6.0, color='g', linestyle='--', linewidth=1, label='II类水标准 (6 mg/L)')
    ax2.axhline(y=4.0, color='orange', linestyle='--', linewidth=1, label='鱼类生存 (4 mg/L)')
    ax2.axhline(y=2.0, color='purple', linestyle='--', linewidth=1, label='严重缺氧 (2 mg/L)')
    
    # 标注临界点
    ax2.plot(tc, DOc, 'ro', markersize=10, label=f'临界点 ({tc:.2f}天, {DOc:.2f}mg/L)')
    ax2.annotate(f'临界点\n({tc:.2f}天, {DOc:.2f}mg/L)', 
                 xy=(tc, DOc), xytext=(tc+1, DOc-0.5),
                 arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                 fontsize=10, color='red', fontweight='bold')
    
    ax2.set_xlabel('时间 (天)', fontsize=11)
    ax2.set_ylabel('溶解氧 DO (mg/L)', fontsize=11)
    ax2.set_title('氧垂曲线 (Oxygen Sag Curve)', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9, loc='lower right')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 10])
    
    plt.tight_layout()
    plt.savefig('streeter_phelps_basic.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: streeter_phelps_basic.png")
    
    # 图2：L0影响
    fig2, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['b', 'r', 'g']
    for i, L0_val in enumerate(L0_values):
        DO_curve, tc_val, DOc_val = results_L0[L0_val]
        ax.plot(model.t, DO_curve, color=colors[i], linewidth=2, 
                label=f'L₀={L0_val} mg/L (DOc={DOc_val:.2f})')
        ax.plot(tc_val, DOc_val, 'o', color=colors[i], markersize=8)
    
    ax.axhline(y=DOs, color='k', linestyle='--', linewidth=1, alpha=0.5, label='饱和DO')
    ax.axhline(y=4.0, color='orange', linestyle='--', linewidth=1, label='鱼类生存')
    ax.set_xlabel('时间 (天)', fontsize=11)
    ax.set_ylabel('溶解氧 DO (mg/L)', fontsize=11)
    ax.set_title('初始BOD (L₀) 对氧垂曲线的影响', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 10])
    
    plt.tight_layout()
    plt.savefig('L0_effect.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: L0_effect.png")
    
    # 图3：ka影响
    fig3, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['b', 'r', 'g']
    for i, ka_val in enumerate(ka_values):
        DO_curve, tc_val, DOc_val = results_ka[ka_val]
        ax.plot(model.t, DO_curve, color=colors[i], linewidth=2, 
                label=f'ka={ka_val} day⁻¹ (ka/kd={ka_val/kd:.1f}, DOc={DOc_val:.2f})')
        ax.plot(tc_val, DOc_val, 'o', color=colors[i], markersize=8)
    
    ax.axhline(y=DOs, color='k', linestyle='--', linewidth=1, alpha=0.5, label='饱和DO')
    ax.axhline(y=4.0, color='orange', linestyle='--', linewidth=1, label='鱼类生存')
    ax.set_xlabel('时间 (天)', fontsize=11)
    ax.set_ylabel('溶解氧 DO (mg/L)', fontsize=11)
    ax.set_title('复氧系数 (ka) 对氧垂曲线的影响', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 10])
    
    plt.tight_layout()
    plt.savefig('ka_effect.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: ka_effect.png")
    
    # 图4：温度影响
    fig4, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['b', 'r', 'orange']
    season_names = ['冬季', '春秋', '夏季']
    for i, T_water in enumerate(temperatures):
        DO_curve, tc_val, DOc_val, DOs_val = results_temp[T_water]
        ax.plot(model.t, DO_curve, color=colors[i], linewidth=2, 
                label=f'{season_names[i]}({T_water}°C): DOs={DOs_val:.2f}, DOc={DOc_val:.2f}')
        ax.plot(tc_val, DOc_val, 'o', color=colors[i], markersize=8)
    
    ax.axhline(y=4.0, color='purple', linestyle='--', linewidth=1.5, label='鱼类生存标准')
    ax.set_xlabel('时间 (天)', fontsize=11)
    ax.set_ylabel('溶解氧 DO (mg/L)', fontsize=11)
    ax.set_title('温度对氧垂曲线的影响', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 11])
    
    plt.tight_layout()
    plt.savefig('temperature_effect.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: temperature_effect.png")
    
    # 图5：排放标准曲线
    fig5, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(L0_test_values, DOc_values, 'b-', linewidth=2.5, label='临界DO vs 初始BOD')
    ax.axhline(y=DO_target, color='r', linestyle='--', linewidth=2, label=f'目标DO ({DO_target} mg/L)')
    ax.axvline(x=L0_max, color='g', linestyle='--', linewidth=2, label=f'最大允许BOD ({L0_max:.1f} mg/L)')
    ax.plot(L0_max, DO_target, 'ro', markersize=12, label='设计点')
    
    # 填充安全区域和风险区域
    ax.fill_between(L0_test_values, DO_target, 10, alpha=0.2, color='green', label='安全区')
    ax.fill_between(L0_test_values, 0, DO_target, alpha=0.2, color='red', label='风险区')
    
    ax.set_xlabel('初始BOD L₀ (mg/L)', fontsize=11)
    ax.set_ylabel('临界DO DOc (mg/L)', fontsize=11)
    ax.set_title('排放标准确定：临界DO vs 初始BOD', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 10])
    
    plt.tight_layout()
    plt.savefig('discharge_standard.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: discharge_standard.png")
    
    # ========================================
    # 总结
    # ========================================
    print()
    print("=" * 70)
    print("案例4完成！")
    print("=" * 70)
    print()
    print("主要结论:")
    print("1. Streeter-Phelps模型描述了DO-BOD的经典关系")
    print("2. 氧垂曲线呈现'U'型：先降后升")
    print("3. 临界点是水质最差的位置和时刻")
    print("4. ka/kd比值决定河流自净能力")
    print("5. 温度对DO有重要影响（夏季风险最大）")
    print()
    print("工程应用:")
    print("  - 排放标准制定（保证DOc ≥ 4 mg/L）")
    print("  - 污水处理厂选址")
    print("  - 分季节管理策略")
    print("  - 生态修复评估")
    print()
    print("生成的图表:")
    print("  - streeter_phelps_basic.png  (基本氧垂曲线)")
    print("  - L0_effect.png              (L₀影响)")
    print("  - ka_effect.png              (ka影响)")
    print("  - temperature_effect.png     (温度影响)")
    print("  - discharge_standard.png     (排放标准)")
    print()
    
    plt.show()


if __name__ == '__main__':
    main()
