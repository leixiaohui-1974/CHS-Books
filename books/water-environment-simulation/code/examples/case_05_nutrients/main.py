"""
案例5：营养盐循环与富营养化评估
Nutrient Cycling and Eutrophication Assessment

演示：
1. 氮循环模拟（硝化、反硝化、氨化）
2. 磷循环模拟（矿化、沉降）
3. 富营养化评估（TSI、TLI）
4. 限制性营养元素判断
5. DO影响分析
6. 温度影响分析
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.nutrients import (NitrogenCycle, PhosphorusCycle, 
                               EutrophicationIndex, calculate_oxygen_consumption)


def main():
    """主函数"""
    print("=" * 70)
    print("案例5：营养盐循环与富营养化评估")
    print("=" * 70)
    print()
    
    # ========================================
    # 任务1：氮循环模拟
    # ========================================
    print("任务1：氮循环模拟")
    print("-" * 70)
    
    # 参数设置
    NH4_0 = 1.2   # 初始氨氮 (mg/L)
    NO3_0 = 0.8   # 初始硝态氮 (mg/L)
    OrgN_0 = 0.5  # 初始有机氮 (mg/L)
    k_n = 0.2     # 硝化速率 (day⁻¹)
    k_dn = 0.1    # 反硝化速率 (day⁻¹)
    k_am = 0.15   # 氨化速率 (day⁻¹)
    T = 30.0      # 模拟时间 (day)
    
    print(f"初始条件:")
    print(f"  氨氮 NH4-N = {NH4_0} mg/L")
    print(f"  硝态氮 NO3-N = {NO3_0} mg/L")
    print(f"  有机氮 Org-N = {OrgN_0} mg/L")
    print(f"  总氮 TN = {NH4_0 + NO3_0 + OrgN_0} mg/L")
    print()
    
    print(f"速率常数:")
    print(f"  硝化速率 k_n = {k_n} day⁻¹")
    print(f"  反硝化速率 k_dn = {k_dn} day⁻¹")
    print(f"  氨化速率 k_am = {k_am} day⁻¹")
    print()
    
    # 创建氮循环模型
    n_cycle = NitrogenCycle(NH4_0=NH4_0, NO3_0=NO3_0, OrgN_0=OrgN_0,
                            k_n=k_n, k_dn=k_dn, k_am=k_am, T=T, nt=1000)
    n_cycle.set_do(6.0)  # 设置DO = 6 mg/L
    
    # 求解
    NH4, NO3, OrgN, TN = n_cycle.solve()
    
    print("✓ 氮循环模拟完成")
    print(f"  最终NH4-N = {NH4[-1]:.3f} mg/L")
    print(f"  最终NO3-N = {NO3[-1]:.3f} mg/L")
    print(f"  最终Org-N = {OrgN[-1]:.3f} mg/L")
    print(f"  最终TN = {TN[-1]:.3f} mg/L")
    print(f"  氮损失 = {TN[0] - TN[-1]:.3f} mg/L ({(TN[0]-TN[-1])/TN[0]*100:.1f}%)")
    print()
    
    # 计算硝化耗氧量
    O2_consumption = calculate_oxygen_consumption(NH4_0, k_n)
    print(f"硝化耗氧:")
    print(f"  初始耗氧速率 = {O2_consumption:.2f} mg O2/L/day")
    print(f"  30天累积耗氧 ≈ {O2_consumption * 15:.1f} mg O2/L (平均)")
    print()
    
    # ========================================
    # 任务2：磷循环模拟
    # ========================================
    print("任务2：磷循环模拟")
    print("-" * 70)
    
    # 参数设置
    PO4_0 = 0.08   # 初始正磷酸盐 (mg/L)
    OrgP_0 = 0.07  # 初始有机磷 (mg/L)
    k_mp = 0.3     # 矿化速率 (day⁻¹)
    k_s = 0.05     # 沉降速率 (day⁻¹)
    
    print(f"初始条件:")
    print(f"  正磷酸盐 PO4-P = {PO4_0} mg/L")
    print(f"  有机磷 Org-P = {OrgP_0} mg/L")
    print(f"  总磷 TP = {PO4_0 + OrgP_0} mg/L")
    print()
    
    print(f"速率常数:")
    print(f"  矿化速率 k_mp = {k_mp} day⁻¹")
    print(f"  沉降速率 k_s = {k_s} day⁻¹")
    print()
    
    # 创建磷循环模型
    p_cycle = PhosphorusCycle(PO4_0=PO4_0, OrgP_0=OrgP_0,
                              k_mp=k_mp, k_s=k_s, T=T, nt=1000)
    
    # 求解
    PO4, OrgP, TP = p_cycle.solve()
    
    print("✓ 磷循环模拟完成")
    print(f"  最终PO4-P = {PO4[-1]:.3f} mg/L")
    print(f"  最终Org-P = {OrgP[-1]:.3f} mg/L")
    print(f"  最终TP = {TP[-1]:.3f} mg/L")
    print(f"  磷损失 = {TP[0] - TP[-1]:.3f} mg/L ({(TP[0]-TP[-1])/TP[0]*100:.1f}%，主要因沉降)")
    print()
    
    # ========================================
    # 任务3：富营养化评估
    # ========================================
    print("任务3：富营养化评估")
    print("-" * 70)
    
    # 监测数据
    Chl = 30.0      # 叶绿素a (μg/L)
    TP_val = 150.0  # 总磷 (μg/L)
    TN_val = 2.5    # 总氮 (mg/L)
    SD = 0.8        # 透明度 (m)
    CODMn = 6.0     # 高锰酸盐指数 (mg/L)
    
    print(f"监测数据:")
    print(f"  叶绿素a = {Chl} μg/L")
    print(f"  总磷 TP = {TP_val} μg/L = {TP_val/1000} mg/L")
    print(f"  总氮 TN = {TN_val} mg/L")
    print(f"  透明度 SD = {SD} m")
    print(f"  高锰酸盐指数 CODMn = {CODMn} mg/L")
    print()
    
    # Carlson TSI
    print("Carlson营养状态指数（TSI）:")
    tsi_chl = EutrophicationIndex.carlson_tsi_chl(Chl)
    tsi_tp = EutrophicationIndex.carlson_tsi_tp(TP_val)
    tsi_sd = EutrophicationIndex.carlson_tsi_sd(SD)
    TSI, status_tsi = EutrophicationIndex.carlson_tsi_综合(Chl, TP_val, SD)
    
    print(f"  TSI(Chl) = {tsi_chl:.1f}")
    print(f"  TSI(TP) = {tsi_tp:.1f}")
    print(f"  TSI(SD) = {tsi_sd:.1f}")
    print(f"  → 综合TSI = {TSI:.1f}")
    print(f"  → 营养状态: {status_tsi}")
    print()
    
    # 中国湖泊TLI
    print("中国湖泊综合营养状态指数（TLI）:")
    TLI, status_tli = EutrophicationIndex.china_tli(Chl, TP_val/1000, TN_val, SD, CODMn)
    print(f"  TLI(Σ) = {TLI:.1f}")
    print(f"  → 营养状态: {status_tli}")
    print()
    
    # 评价
    print("综合评价:")
    if TSI >= 60 or TLI >= 60:
        print("  ⚠️  水体富营养化程度较高！")
        print("  建议采取控制措施：")
        print("    - 削减营养盐输入")
        print("    - 加强底泥疏浚")
        print("    - 生态修复")
    elif TSI >= 50 or TLI >= 50:
        print("  ⚠️  水体已呈富营养化状态")
        print("  建议加强监测和预防")
    else:
        print("  ✓ 水体营养状态良好")
    print()
    
    # ========================================
    # 任务4：限制性营养元素判断
    # ========================================
    print("任务4：限制性营养元素判断")
    print("-" * 70)
    
    print(f"营养盐浓度:")
    print(f"  总氮 TN = {TN_val} mg/L")
    print(f"  总磷 TP = {TP_val/1000:.3f} mg/L")
    print()
    
    limiting = EutrophicationIndex.limiting_nutrient(TN_val, TP_val/1000)
    print()
    
    print("控制策略建议:")
    if limiting == 'N':
        print("  → 优先控制氮输入")
        print("    - 减少氮肥使用")
        print("    - 污水处理厂强化脱氮")
        print("    - 控制畜禽养殖")
    elif limiting == 'P':
        print("  → 优先控制磷输入")
        print("    - 使用无磷洗涤剂")
        print("    - 污水处理厂强化除磷")
        print("    - 底泥疏浚（内源控制）")
    else:
        print("  → 需同时控制氮和磷")
        print("    - 综合治理")
    print()
    
    # ========================================
    # 任务5：DO影响分析
    # ========================================
    print("任务5：DO影响分析")
    print("-" * 70)
    
    DO_values = [8.0, 4.0, 1.0]
    results_do = {}
    
    for DO_val in DO_values:
        n_cycle_do = NitrogenCycle(NH4_0=NH4_0, NO3_0=NO3_0, OrgN_0=OrgN_0,
                                   k_n=k_n, k_dn=k_dn, k_am=k_am, T=T, nt=1000)
        n_cycle_do.set_do(DO_val)
        NH4_do, NO3_do, OrgN_do, TN_do = n_cycle_do.solve()
        results_do[DO_val] = (NH4_do, NO3_do, OrgN_do, TN_do)
        
        print(f"\nDO = {DO_val} mg/L:")
        print(f"  最终NH4-N = {NH4_do[-1]:.3f} mg/L")
        print(f"  最终NO3-N = {NO3_do[-1]:.3f} mg/L")
        print(f"  最终TN = {TN_do[-1]:.3f} mg/L")
        print(f"  氮损失率 = {(TN_do[0]-TN_do[-1])/TN_do[0]*100:.1f}%")
        
        if DO_val >= 6:
            print("  → 硝化作用主导（NH4 → NO3）")
        elif DO_val >= 2:
            print("  → 硝化和反硝化平衡")
        else:
            print("  → 反硝化作用主导（NO3 → N2，氮损失）")
    
    print()
    
    # ========================================
    # 任务6：温度影响分析
    # ========================================
    print("任务6：温度影响分析")
    print("-" * 70)
    
    temperatures = [10, 20, 30]
    k_n_20 = 0.2
    k_dn_20 = 0.1
    k_am_20 = 0.15
    
    print("\n温度校正:")
    for T_water in temperatures:
        n_temp = NitrogenCycle(NH4_0=1.0, NO3_0=1.0, OrgN_0=0.5,
                               k_n=0.2, k_dn=0.1, k_am=0.15, T=10.0)
        
        k_n_T = n_temp.temperature_correction(k_n_20, T_water, 'nitrification')
        k_dn_T = n_temp.temperature_correction(k_dn_20, T_water, 'denitrification')
        k_am_T = n_temp.temperature_correction(k_am_20, T_water, 'ammonification')
        print()
    
    print("温度影响总结:")
    print("  - 温度升高 → 所有生物过程加快")
    print("  - 夏季（高温）：硝化和反硝化都加快")
    print("  - 冬季（低温）：转化速率明显降低")
    print("  - 高温有利于水华爆发（营养盐快速释放）")
    print()
    
    # ========================================
    # 绘图
    # ========================================
    print("生成图表...")
    
    # 图1：氮循环
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    
    # 各形态氮变化
    ax1.plot(n_cycle.t, NH4, 'b-', linewidth=2, label='NH4-N（氨氮）')
    ax1.plot(n_cycle.t, NO3, 'r-', linewidth=2, label='NO3-N（硝态氮）')
    ax1.plot(n_cycle.t, OrgN, 'g-', linewidth=2, label='Org-N（有机氮）')
    ax1.set_xlabel('时间 (天)', fontsize=11)
    ax1.set_ylabel('浓度 (mg/L)', fontsize=11)
    ax1.set_title('氮循环：各形态氮的变化', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 总氮变化
    ax2.plot(n_cycle.t, TN, 'k-', linewidth=2.5, label='总氮 TN')
    ax2.axhline(y=TN[0], color='k', linestyle='--', alpha=0.5, label='初始TN')
    ax2.fill_between(n_cycle.t, TN, TN[0], alpha=0.2, color='red', label='氮损失（反硝化）')
    ax2.set_xlabel('时间 (天)', fontsize=11)
    ax2.set_ylabel('总氮 TN (mg/L)', fontsize=11)
    ax2.set_title('总氮变化（反硝化导致氮损失）', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('nitrogen_cycle.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: nitrogen_cycle.png")
    
    # 图2：磷循环
    fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    
    # 各形态磷变化
    ax1.plot(p_cycle.t, PO4, 'b-', linewidth=2, label='PO4-P（正磷酸盐）')
    ax1.plot(p_cycle.t, OrgP, 'g-', linewidth=2, label='Org-P（有机磷）')
    ax1.set_xlabel('时间 (天)', fontsize=11)
    ax1.set_ylabel('浓度 (mg/L)', fontsize=11)
    ax1.set_title('磷循环：各形态磷的变化', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 总磷变化
    ax2.plot(p_cycle.t, TP, 'purple', linewidth=2.5, label='总磷 TP')
    ax2.axhline(y=TP[0], color='purple', linestyle='--', alpha=0.5, label='初始TP')
    ax2.fill_between(p_cycle.t, TP, TP[0], alpha=0.2, color='purple', label='磷损失（沉降）')
    ax2.set_xlabel('时间 (天)', fontsize=11)
    ax2.set_ylabel('总磷 TP (mg/L)', fontsize=11)
    ax2.set_title('总磷变化（沉降导致磷损失）', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('phosphorus_cycle.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: phosphorus_cycle.png")
    
    # 图3：DO影响
    fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    colors = ['blue', 'green', 'red']
    labels = ['高DO (8 mg/L)', '中DO (4 mg/L)', '低DO (1 mg/L)']
    
    for i, DO_val in enumerate(DO_values):
        NH4_do, NO3_do, _, TN_do = results_do[DO_val]
        ax1.plot(n_cycle.t, NH4_do, color=colors[i], linewidth=2, label=labels[i])
    
    ax1.set_xlabel('时间 (天)', fontsize=11)
    ax1.set_ylabel('NH4-N (mg/L)', fontsize=11)
    ax1.set_title('DO对氨氮的影响', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    for i, DO_val in enumerate(DO_values):
        _, NO3_do, _, _ = results_do[DO_val]
        ax2.plot(n_cycle.t, NO3_do, color=colors[i], linewidth=2, label=labels[i])
    
    ax2.set_xlabel('时间 (天)', fontsize=11)
    ax2.set_ylabel('NO3-N (mg/L)', fontsize=11)
    ax2.set_title('DO对硝态氮的影响', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('do_effect.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: do_effect.png")
    
    # 图4：富营养化评估
    fig4, ax = plt.subplots(figsize=(10, 6))
    
    # TSI/TLI指示器
    categories = ['TSI(Chl)', 'TSI(TP)', 'TSI(SD)', 'TSI综合', 'TLI综合']
    values = [tsi_chl, tsi_tp, tsi_sd, TSI, TLI]
    colors_bar = ['skyblue', 'lightcoral', 'lightgreen', 'gold', 'orange']
    
    bars = ax.barh(categories, values, color=colors_bar, edgecolor='black', linewidth=1.5)
    
    # 添加分界线
    ax.axvline(x=30, color='green', linestyle='--', linewidth=2, label='贫营养-中营养 (30)')
    ax.axvline(x=50, color='orange', linestyle='--', linewidth=2, label='中营养-富营养 (50)')
    ax.axvline(x=70, color='red', linestyle='--', linewidth=2, label='富营养-超富营养 (70)')
    
    # 添加数值标签
    for i, (bar, val) in enumerate(zip(bars, values)):
        ax.text(val + 1, i, f'{val:.1f}', va='center', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('营养状态指数', fontsize=11)
    ax.set_title('富营养化评估结果', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9, loc='lower right')
    ax.grid(True, alpha=0.3, axis='x')
    ax.set_xlim([0, 80])
    
    plt.tight_layout()
    plt.savefig('eutrophication_assessment.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: eutrophication_assessment.png")
    
    # ========================================
    # 总结
    # ========================================
    print()
    print("=" * 70)
    print("案例5完成！")
    print("=" * 70)
    print()
    print("主要结论:")
    print("1. 氮循环包括硝化、反硝化、氨化三个主要过程")
    print("2. 硝化消耗氧气，反硝化损失氮素")
    print("3. 磷循环包括矿化和沉降")
    print("4. 本案例水体呈富营养化状态（TSI≈{:.0f}, TLI≈{:.0f}）".format(TSI, TLI))
    print("5. N/P比值较高（{:.1f}），磷为限制元素".format(TN_val/(TP_val/1000)))
    print()
    print("控制策略:")
    print("  - 优先控制磷输入（限制元素）")
    print("  - 强化污水处理厂除磷")
    print("  - 禁用含磷洗涤剂")
    print("  - 底泥疏浚（内源控制）")
    print("  - 生态修复（水生植物）")
    print()
    print("生成的图表:")
    print("  - nitrogen_cycle.png               (氮循环)")
    print("  - phosphorus_cycle.png             (磷循环)")
    print("  - do_effect.png                    (DO影响)")
    print("  - eutrophication_assessment.png    (富营养化评估)")
    print()
    
    plt.show()


if __name__ == '__main__':
    main()
