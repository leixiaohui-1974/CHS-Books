"""
案例6：河流自净能力与环境容量评估
Self-Purification Capacity and Environmental Capacity Assessment

演示：
1. 自净能力评估（自净系数）
2. 稀释容量计算
3. 环境容量计算（考虑降解）
4. 同化容量计算（基于S-P模型）
5. 水质综合评价
6. 功能区划分
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.self_purification import (SelfPurificationCapacity, WaterQualityIndex,
                                      calculate_assimilative_capacity, 
                                      functional_zone_classification)


def main():
    """主函数"""
    print("=" * 70)
    print("案例6：河流自净能力与环境容量评估")
    print("=" * 70)
    print()
    
    # ========================================
    # 任务1：自净能力评估
    # ========================================
    print("任务1：自净能力评估")
    print("-" * 70)
    
    # 河流参数
    Q = 20.0        # 流量 (m³/s)
    u = 0.5         # 流速 (m/s)
    A = 40.0        # 断面面积 (m²)
    B = 15.0        # 河宽 (m)
    H = 2.7         # 水深 (m)
    P = B + 2*H     # 湿周 (m)
    ka = 0.6        # 复氧系数 (day⁻¹)
    kd = 0.2        # BOD降解系数 (day⁻¹)
    
    print(f"河流参数:")
    print(f"  流量 Q = {Q} m³/s")
    print(f"  流速 u = {u} m/s")
    print(f"  断面积 A = {A} m²")
    print(f"  河宽 B = {B} m")
    print(f"  水深 H = {H} m")
    print(f"  湿周 P = {P:.1f} m")
    print(f"  水力半径 R = {A/P:.2f} m")
    print()
    
    print(f"水质参数:")
    print(f"  复氧系数 ka = {ka} day⁻¹")
    print(f"  降解系数 kd = {kd} day⁻¹")
    print()
    
    # 创建自净能力评估模型
    sp_model = SelfPurificationCapacity(Q=Q, u=u, A=A, P=P, ka=ka, kd=kd)
    
    # 计算自净系数
    f, grade, color = sp_model.calculate_self_purification_coefficient()
    print()
    
    # 分析
    print("自净能力分析:")
    if f >= 5:
        print("  ✓ 自净能力强，水体恢复快")
        print("  ✓ 可容纳一定污染负荷")
    elif f >= 2:
        print("  ✓ 自净能力较强")
        print("  ⚠️  需控制污染负荷")
    elif f >= 1:
        print("  ⚠️  自净能力一般")
        print("  ⚠️  应严格控制排放")
    else:
        print("  ⚠️⚠️  自净能力弱，污染可能加重！")
        print("  ⚠️⚠️  必须严格限制排放或采取增氧措施")
    print()
    
    # ========================================
    # 任务2：稀释容量计算
    # ========================================
    print("任务2：稀释容量计算（仅稀释，不考虑降解）")
    print("-" * 70)
    
    # 水质参数和标准（注意：为了演示环境容量计算，这里使用达标的本底浓度）
    pollutants = {
        'BOD': {'background': 3.0, 'standard': 4.0},  # 使用达标的本底浓度
        'NH3-N': {'background': 0.8, 'standard': 1.0},
        'TP': {'background': 0.15, 'standard': 0.2},
    }
    
    dilution_capacities = {}
    
    for pollutant, params in pollutants.items():
        print(f"\n{pollutant}:")
        W = sp_model.calculate_dilution_capacity(
            params['background'], params['standard']
        )
        dilution_capacities[pollutant] = W
        print()
    
    # ========================================
    # 任务3：环境容量计算（考虑降解）
    # ========================================
    print("任务3：环境容量计算（稀释+降解）")
    print("-" * 70)
    
    L_river = 50  # 河段长度 (km)
    
    print(f"\n计算{L_river} km河段的BOD环境容量:")
    W_env = sp_model.calculate_environmental_capacity(
        C0=3.0, C_standard=4.0, L=L_river, decay=True
    )
    print()
    
    print(f"对比:")
    print(f"  仅稀释容量: {dilution_capacities['BOD']:.2f} kg/day")
    print(f"  总环境容量: {W_env:.2f} kg/day")
    if dilution_capacities['BOD'] > 0:
        print(f"  降解作用增加: {W_env - dilution_capacities['BOD']:.2f} kg/day " + 
              f"({(W_env/dilution_capacities['BOD']-1)*100:.0f}%)")
    else:
        print(f"  ⚠️  本底浓度已超标，需先削减污染负荷")
    print()
    
    # ========================================
    # 任务4：同化容量计算
    # ========================================
    print("任务4：同化容量计算（基于S-P模型，DO约束）")
    print("-" * 70)
    
    DOs = 9.0       # 饱和DO (mg/L)
    DO_standard = 5.0  # DO标准 (mg/L)
    L0_bg = 5.0     # 上游本底BOD (mg/L)
    
    L0_max, W_assimilative = calculate_assimilative_capacity(
        Q=Q, ka=ka, kd=kd, DOs=DOs, DO_standard=DO_standard, L0_bg=L0_bg
    )
    print()
    
    print(f"不同容量对比:")
    print(f"  稀释容量:   {dilution_capacities['BOD']:.2f} kg/day （最保守）")
    print(f"  环境容量:   {W_env:.2f} kg/day （考虑降解）")
    print(f"  同化容量:   {W_assimilative:.2f} kg/day （DO约束）")
    print()
    
    # ========================================
    # 任务5：水质综合评价
    # ========================================
    print("任务5：水质综合评价")
    print("-" * 70)
    
    # 实测水质
    C_measured = {
        'DO': 7.0,
        'BOD5': 5.0,
        'COD': 18.0,
        'NH3-N': 0.8,
        'TP': 0.15,
    }
    
    # III类水标准
    C_standard_III = {
        'DO': 5.0,
        'BOD5': 4.0,
        'COD': 20.0,
        'NH3-N': 1.0,
        'TP': 0.2,
    }
    
    print("\n实测水质:")
    for param, value in C_measured.items():
        print(f"  {param}: {value} mg/L")
    print()
    
    # 单因子评价
    print("单因子评价（相对于III类水标准）:")
    exceed_params = []
    for param in C_measured:
        P = WaterQualityIndex.single_factor_index(
            C_measured[param], C_standard_III[param]
        )
        status = "✓ 达标" if P < 1 else f"⚠️  超标{(P-1)*100:.0f}%"
        print(f"  {param}: P = {P:.3f}  {status}")
        if P >= 1:
            exceed_params.append(param)
    print()
    
    if exceed_params:
        print(f"超标参数: {', '.join(exceed_params)}")
        print("→ 按单因子法，水质为超III类")
    else:
        print("✓ 所有参数达标")
    print()
    
    # 综合污染指数
    print("综合污染指数法:")
    C_measured_list = list(C_measured.values())
    C_standard_list = list(C_standard_III.values())
    weights = [1.5, 1.0, 0.8, 1.2, 1.3]  # DO、BOD、COD、NH3-N、TP的权重
    
    P_comp = WaterQualityIndex.comprehensive_pollution_index(
        C_measured_list, C_standard_list, weights
    )
    
    print(f"  综合污染指数 P = {P_comp:.3f}")
    
    if P_comp <= 0.2:
        comp_status = "清洁"
    elif P_comp <= 0.4:
        comp_status = "尚清洁"
    elif P_comp <= 1.0:
        comp_status = "轻度污染"
    elif P_comp <= 2.0:
        comp_status = "中度污染"
    else:
        comp_status = "重度污染"
    
    print(f"  → 污染状况: {comp_status}")
    print()
    
    # ========================================
    # 任务6：功能区划分
    # ========================================
    print("任务6：河流功能区划分")
    print("-" * 70)
    
    print("\n根据现状水质划分功能区:")
    category, suitable_uses = functional_zone_classification(C_measured)
    print()
    
    print("管理建议:")
    if category <= 2:
        print("  ✓ 水质优良，可作为饮用水源")
        print("  ✓ 应划为保护区，严格管理")
    elif category == 3:
        print("  - 水质良好，适合渔业和一般用途")
        print("  - 应加强保护，防止水质下降")
    elif category == 4:
        print("  ⚠️  水质一般，仅适合工业和景观用水")
        print("  ⚠️  应实施污染治理，提升水质")
    else:
        print("  ⚠️⚠️  水质较差")
        print("  ⚠️⚠️  必须进行治理，不宜作为水源")
    print()
    
    # ========================================
    # 绘图
    # ========================================
    print("生成图表...")
    
    # 图1：自净系数对比
    fig1, ax = plt.subplots(figsize=(10, 6))
    
    ka_values = np.array([0.2, 0.4, 0.6, 0.8, 1.0])
    f_values = ka_values / kd
    colors_f = ['red' if f < 1 else 'orange' if f < 2 else 'yellow' if f < 5 else 'green' 
                for f in f_values]
    
    bars = ax.bar(range(len(ka_values)), f_values, color=colors_f, 
                  edgecolor='black', linewidth=2, alpha=0.7)
    
    # 添加分界线
    ax.axhline(y=1, color='red', linestyle='--', linewidth=2, label='弱-一般 (f=1)')
    ax.axhline(y=2, color='orange', linestyle='--', linewidth=2, label='一般-较强 (f=2)')
    ax.axhline(y=5, color='green', linestyle='--', linewidth=2, label='较强-强 (f=5)')
    
    # 标注当前值
    current_idx = np.argmin(np.abs(ka_values - ka))
    ax.plot(current_idx, f_values[current_idx], 'r*', markersize=20, 
            label=f'本案例 (ka={ka}, f={f:.1f})')
    
    ax.set_xticks(range(len(ka_values)))
    ax.set_xticklabels([f'ka={ka_val:.1f}' for ka_val in ka_values])
    ax.set_xlabel('复氧系数 ka (day⁻¹)', fontsize=11)
    ax.set_ylabel('自净系数 f = ka/kd', fontsize=11)
    ax.set_title(f'自净系数评估 (kd = {kd} day⁻¹)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('self_purification_coefficient.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: self_purification_coefficient.png")
    
    # 图2：环境容量对比
    fig2, ax = plt.subplots(figsize=(10, 6))
    
    capacity_types = ['稀释容量', '环境容量\n(50km)', '同化容量\n(DO约束)']
    capacity_values = [dilution_capacities['BOD'], W_env, W_assimilative]
    colors_cap = ['skyblue', 'lightgreen', 'gold']
    
    bars = ax.bar(capacity_types, capacity_values, color=colors_cap, 
                  edgecolor='black', linewidth=2, alpha=0.8)
    
    # 添加数值标签
    for bar, val in zip(bars, capacity_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.0f}\nkg/day',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_ylabel('BOD环境容量 (kg/day)', fontsize=11)
    ax.set_title('不同方法的环境容量对比', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('environmental_capacity.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: environmental_capacity.png")
    
    # 图3：单因子评价
    fig3, ax = plt.subplots(figsize=(10, 6))
    
    params_list = list(C_measured.keys())
    P_values = [WaterQualityIndex.single_factor_index(C_measured[p], C_standard_III[p]) 
                for p in params_list]
    colors_p = ['green' if p < 0.8 else 'yellow' if p < 1.0 else 'orange' if p < 1.5 else 'red' 
                for p in P_values]
    
    bars = ax.barh(params_list, P_values, color=colors_p, 
                   edgecolor='black', linewidth=1.5, alpha=0.7)
    
    # 达标线
    ax.axvline(x=1.0, color='red', linestyle='--', linewidth=2.5, label='达标线 (P=1)')
    
    # 添加数值标签
    for i, (bar, val) in enumerate(zip(bars, P_values)):
        status = '✓' if val < 1 else '⚠️'
        ax.text(val + 0.05, i, f'{val:.3f} {status}', 
                va='center', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('单因子指数 P = C_measured / C_standard', fontsize=11)
    ax.set_title('单因子水质评价（相对于III类水标准）', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10, loc='lower right')
    ax.grid(True, alpha=0.3, axis='x')
    ax.set_xlim([0, max(P_values) * 1.3])
    
    plt.tight_layout()
    plt.savefig('water_quality_evaluation.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: water_quality_evaluation.png")
    
    # 图4：功能区划分
    fig4, ax = plt.subplots(figsize=(12, 6))
    
    # 不同功能区的水质要求
    categories = ['I类\n源头水', 'II类\n饮用水源', 'III类\n渔业用水', 
                  'IV类\n工业用水', 'V类\n农业用水']
    do_standards = [7.5, 6.0, 5.0, 3.0, 2.0]
    bod_standards = [3, 3, 4, 6, 10]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, do_standards, width, label='DO标准 (mg/L)',
                   color='skyblue', edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, bod_standards, width, label='BOD标准 (mg/L)',
                   color='lightcoral', edgecolor='black', linewidth=1.5)
    
    # 标注实测值
    ax.axhline(y=C_measured['DO'], color='blue', linestyle='--', 
               linewidth=2, label=f'实测DO ({C_measured["DO"]} mg/L)')
    ax.axhline(y=C_measured['BOD5'], color='red', linestyle='--', 
               linewidth=2, label=f'实测BOD ({C_measured["BOD5"]} mg/L)')
    
    # 标注推荐类别
    if category <= 5:
        ax.plot(category-1, 8.5, 'g*', markersize=25, 
                label=f'推荐类别 ({category}类)')
    
    ax.set_ylabel('浓度 (mg/L)', fontsize=11)
    ax.set_xlabel('水质类别', fontsize=11)
    ax.set_title('河流功能区划分标准', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('functional_zone_classification.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: functional_zone_classification.png")
    
    # ========================================
    # 总结
    # ========================================
    print()
    print("=" * 70)
    print("案例6完成！")
    print("=" * 70)
    print()
    print("主要结论:")
    print("1. 本河段自净系数 f = {:.1f}，自净能力{}".format(f, grade))
    print("2. BOD稀释容量 = {:.0f} kg/day".format(dilution_capacities['BOD']))
    if dilution_capacities['BOD'] > 0:
        print("3. BOD环境容量 = {:.0f} kg/day（考虑降解后增加{:.0f}%）".format(
            W_env, (W_env/dilution_capacities['BOD']-1)*100))
    else:
        print("3. BOD环境容量 = {:.0f} kg/day".format(W_env))
    print("4. 现状水质为{}类，适用于{}等用途".format(category, ', '.join(suitable_uses)))
    print("5. 综合污染指数 P = {:.2f}，属于{}".format(P_comp, comp_status))
    print()
    print("管理建议:")
    print("  1. 排放总量不超过环境容量 ({:.0f} kg/day)".format(W_env))
    print("  2. 重点控制超标参数: {}".format(', '.join(exceed_params) if exceed_params else '无'))
    print("  3. 提升自净能力: 生态修复、增加曝气")
    print("  4. 分区管理: 上游饮用水源保护，中下游工业/景观用水")
    print()
    print("生成的图表:")
    print("  - self_purification_coefficient.png   (自净系数)")
    print("  - environmental_capacity.png          (环境容量)")
    print("  - water_quality_evaluation.png        (水质评价)")
    print("  - functional_zone_classification.png  (功能区划分)")
    print()
    
    plt.show()


if __name__ == '__main__':
    main()
