"""
案例10：复式断面河道 - 主程序

问题描述：
某天然河道具有主槽和滩地的复式断面形式，已知：
- 主槽底宽 bm = 30 m，深度 hm = 3.5 m
- 主槽边坡 m1 = 2.0
- 左滩地宽 bl = 50 m，右滩地宽 br = 50 m
- 滩地边坡 m2 = 3.0
- 河床纵坡 S0 = 0.0003
- 主槽糙率 nm = 0.028（清洁河床）
- 滩地糙率 nf = 0.035（有植被）

求解：
1. 主槽满流量（漫滩流量）
2. 不同水深下的过流能力
3. 主槽与滩地的流量分配
4. 绘制水位-流量关系曲线
5. 评估滩地对行洪能力的贡献

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import CompoundChannel


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def main():
    """主函数"""
    print_separator("案例10：复式断面河道")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】复式断面参数")
    print("-" * 80)

    bm = 30.0    # 主槽底宽 (m)
    hm = 3.5     # 主槽深度 (m)
    m1 = 2.0     # 主槽边坡系数
    bl = 50.0    # 左滩地宽度 (m)
    br = 50.0    # 右滩地宽度 (m)
    m2 = 3.0     # 滩地边坡系数
    nm = 0.028   # 主槽糙率
    nf = 0.035   # 滩地糙率
    S0 = 0.0003  # 河床纵坡

    print(f"主槽参数：")
    print(f"  底宽 bm = {bm} m")
    print(f"  深度 hm = {hm} m")
    print(f"  边坡 m1 = {m1}（水平:垂直 = {m1}:1）")
    print(f"  糙率 nm = {nm}")

    print(f"\n滩地参数：")
    print(f"  左滩地宽度 bl = {bl} m")
    print(f"  右滩地宽度 br = {br} m")
    print(f"  边坡 m2 = {m2}")
    print(f"  糙率 nf = {nf}")

    print(f"\n河道参数：")
    print(f"  纵坡 S0 = {S0}")

    # ==================== 第二步：创建复式断面对象 ====================
    print("\n【步骤2】创建复式断面河道模型")
    print("-" * 80)

    channel = CompoundChannel(
        bm=bm, hm=hm, m1=m1,
        bl=bl, br=br, m2=m2,
        nm=nm, nf=nf, S0=S0
    )

    print(f"河道对象：{channel}")

    # ==================== 第三步：主槽几何特性 ====================
    print("\n【步骤3】主槽几何特性（满槽状态）")
    print("-" * 80)

    Am = channel.main_channel_area(hm)
    Pm = channel.main_channel_wetted_perimeter(hm)
    Tm = channel.main_channel_top_width(hm)
    Rm = Am / Pm

    print(f"主槽满槽几何：")
    print(f"  过水面积 Am = {Am:.2f} m²")
    print(f"  湿周 Pm = {Pm:.2f} m")
    print(f"  水面宽 Tm = {Tm:.2f} m")
    print(f"  水力半径 Rm = {Rm:.2f} m")

    # ==================== 第四步：主槽满流量（漫滩流量） ====================
    print("\n【步骤4】主槽满流量计算（漫滩流量）")
    print("-" * 80)

    Q_bankfull = channel.bankfull_discharge()
    v_bankfull = Q_bankfull / Am

    print(f"主槽满流量：Q_bankfull = {Q_bankfull:.2f} m³/s")
    print(f"主槽满槽流速：v = {v_bankfull:.3f} m/s")
    print(f"\n说明：当流量超过 {Q_bankfull:.2f} m³/s 时，水流开始漫滩")
    print(f"这通常对应于1-2年一遇的洪水流量")

    # ==================== 第五步：不同水深的过流能力 ====================
    print("\n【步骤5】不同水深的过流能力分析")
    print("-" * 80)

    h_values = [1.0, 2.0, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]

    print("\n过流能力对比：")
    print("-" * 130)
    print(f"{'水深h(m)':^12} | {'漫滩状态':^12} | {'总流量Q(m³/s)':^16} | "
          f"{'主槽Q(m³/s)':^15} | {'滩地Q(m³/s)':^15} | {'主槽比α_m':^13} | {'滩地比α_f':^13}")
    print("-" * 130)

    for h in h_values:
        result = channel.discharge(h)
        overbank_status = "已漫滩" if h > hm else "未漫滩"

        print(f"{h:^12.2f} | {overbank_status:^12} | {result['total']:^16.2f} | "
              f"{result['main']:^15.2f} | {result['left']+result['right']:^15.2f} | "
              f"{result['alpha_main']:^13.3f} | {result['alpha_flood']:^13.3f}")

    print("-" * 130)

    print("\n【关键观察】")
    print("1. h = 3.5m 时：主槽满流，即将漫滩")
    print("2. h > 3.5m 时：流量显著增大，滩地开始发挥作用")
    print("3. 主槽流量比：随水深增大而减小（滩地贡献增加）")
    print("4. 漫滩初期：主槽仍占主导（α_m ≈ 0.7-0.8）")

    # ==================== 第六步：流量分配详细分析 ====================
    print("\n【步骤6】流量分配详细分析")
    print("-" * 80)

    # 选择典型漫滩水深
    h_test = 5.0
    analysis = channel.analyze_flow(h_test)

    print(f"\n典型漫滩水深 h = {h_test} m 的流动状态：")
    print("-" * 80)

    print(f"\n几何参数：")
    print(f"  总过水面积 = {analysis['area_total']:.2f} m²")
    print(f"    - 主槽面积 = {analysis['area_main']:.2f} m² ({analysis['area_main']/analysis['area_total']*100:.1f}%)")
    print(f"    - 左滩地面积 = {analysis['area_left']:.2f} m² ({analysis['area_left']/analysis['area_total']*100:.1f}%)")
    print(f"    - 右滩地面积 = {analysis['area_right']:.2f} m² ({analysis['area_right']/analysis['area_total']*100:.1f}%)")
    print(f"  总水面宽 = {analysis['top_width']:.2f} m")

    print(f"\n流量分配：")
    print(f"  总流量 = {analysis['discharge_total']:.2f} m³/s")
    print(f"    - 主槽流量 = {analysis['discharge_main']:.2f} m³/s ({analysis['alpha_main']*100:.1f}%)")
    print(f"    - 左滩地流量 = {analysis['discharge_left']:.2f} m³/s ({analysis['discharge_left']/analysis['discharge_total']*100:.1f}%)")
    print(f"    - 右滩地流量 = {analysis['discharge_right']:.2f} m³/s ({analysis['discharge_right']/analysis['discharge_total']*100:.1f}%)")

    print(f"\n流速分布：")
    print(f"  平均流速 = {analysis['velocity_avg']:.3f} m/s")
    print(f"    - 主槽流速 = {analysis['velocity_main']:.3f} m/s")
    print(f"    - 左滩地流速 = {analysis['velocity_left']:.3f} m/s")
    print(f"    - 右滩地流速 = {analysis['velocity_right']:.3f} m/s")
    print(f"  速度比 v_main/v_flood = {analysis['velocity_main']/max(analysis['velocity_left'],0.01):.2f}")

    print(f"\n水流形态：")
    print(f"  Froude数（总断面）= {analysis['froude_total']:.3f}")
    flow_regime = "缓流" if analysis['froude_total'] < 1 else "急流"
    print(f"  流态：{flow_regime}")

    # ==================== 第七步：水位-流量关系曲线 ====================
    print("\n【步骤7】水位-流量关系（Q-h关系）")
    print("-" * 80)

    h_range = np.linspace(0.5, 6.5, 30)
    Q_list = []
    Qm_list = []
    Qf_list = []

    for h in h_range:
        result = channel.discharge(h)
        Q_list.append(result['total'])
        Qm_list.append(result['main'])
        Qf_list.append(result['left'] + result['right'])

    print("\nQ-h关系数据点（部分显示）：")
    print("-" * 100)
    print(f"{'水深h(m)':^12} | {'总流量Q(m³/s)':^16} | {'主槽流量(m³/s)':^17} | {'滩地流量(m³/s)':^17} | {'dQ/dh':^14}")
    print("-" * 100)

    for i in range(0, len(h_range), 3):
        h = h_range[i]
        Q = Q_list[i]
        Qm = Qm_list[i]
        Qf = Qf_list[i]

        # 计算dQ/dh（数值导数）
        if i > 0:
            dQ_dh = (Q_list[i] - Q_list[i-1]) / (h_range[i] - h_range[i-1])
        else:
            dQ_dh = 0

        marker = " ← 漫滩点" if abs(h - hm) < 0.2 else ""

        print(f"{h:^12.2f} | {Q:^16.2f} | {Qm:^17.2f} | {Qf:^17.2f} | {dQ_dh:^14.2f}{marker}")

    print("-" * 100)

    print("\n【Q-h关系特点】")
    print("1. h < hm：Q随h增加，dQ/dh较小")
    print("2. h ≈ hm：漫滩转折点，dQ/dh突然增大")
    print("3. h > hm：dQ/dh显著增大（滩地提供额外输水能力）")
    print("4. 转折点对应主槽满流量，是重要的水文特征")

    # ==================== 第八步：滩地贡献评估 ====================
    print("\n【步骤8】滩地对行洪能力的贡献")
    print("-" * 80)

    print("\n滩地贡献分析：")
    print("-" * 120)
    print(f"{'水深h(m)':^12} | {'漫滩深度(m)':^14} | {'总流量(m³/s)':^15} | "
          f"{'若无滩地Q(m³/s)':^18} | {'滩地贡献ΔQ(m³/s)':^19} | {'贡献率(%)':^13}")
    print("-" * 120)

    for h in [4.0, 4.5, 5.0, 5.5, 6.0]:
        result = channel.discharge(h)
        Q_total = result['total']
        Q_main_only = result['main']  # 主槽流量
        Q_flood_contribution = result['left'] + result['right']
        contribution_ratio = Q_flood_contribution / Q_total * 100
        overbank_depth = h - hm

        print(f"{h:^12.2f} | {overbank_depth:^14.2f} | {Q_total:^15.2f} | "
              f"{Q_main_only:^18.2f} | {Q_flood_contribution:^19.2f} | {contribution_ratio:^13.1f}")

    print("-" * 120)

    print("\n【滩地效益】")
    print("1. 漫滩1m时：滩地贡献约20-30%的流量")
    print("2. 漫滩2m时：滩地贡献增至30-40%")
    print("3. 大水深时：滩地贡献持续增大")
    print("4. 滩地极大提高了河道的行洪能力")
    print("5. 保护滩地行洪通道对防洪至关重要")

    # ==================== 第九步：设计流量反算水深 ====================
    print("\n【步骤9】设计流量反算水深")
    print("-" * 80)

    design_flows = [
        (Q_bankfull, "主槽满流", "5年一遇"),
        (300, "中等洪水", "10年一遇"),
        (400, "较大洪水", "20年一遇"),
        (500, "大洪水", "50年一遇"),
        (600, "特大洪水", "100年一遇")
    ]

    print("\n不同设计标准对应的水深：")
    print("-" * 120)
    print(f"{'设计流量Q(m³/s)':^18} | {'设计标准':^15} | {'频率':^15} | "
          f"{'所需水深h(m)':^16} | {'安全水深(m)':^15} | {'防洪评价':^15}")
    print("-" * 120)

    for Q_design, standard, frequency in design_flows:
        if Q_design <= Q_bankfull:
            h_design = channel.compute_depth_from_discharge(Q_design, h_max=hm)
        else:
            h_design = channel.compute_depth_from_discharge(Q_design, h_max=10.0)

        h_safe = h_design + 0.5  # 加0.5m安全超高

        # 评价
        if h_safe < 5.0:
            evaluation = "安全"
        elif h_safe < 6.0:
            evaluation = "基本安全"
        elif h_safe < 7.0:
            evaluation = "需要防护"
        else:
            evaluation = "风险较大"

        print(f"{Q_design:^18.2f} | {standard:^15} | {frequency:^15} | "
              f"{h_design:^16.3f} | {h_safe:^15.3f} | {evaluation:^15}")

    print("-" * 120)

    # ==================== 第十步：工程设计建议 ====================
    print("\n【步骤10】工程设计建议")
    print("-" * 80)

    print("\n基于水力计算的设计方案：")

    print(f"\n1. 主槽设计：")
    print(f"   - 满流量：Q = {Q_bankfull:.2f} m³/s（5年一遇）")
    print(f"   - 底宽：bm = {bm} m")
    print(f"   - 深度：hm = {hm} m")
    print(f"   - 边坡：m1 = {m1}（稳定坡度）")
    print(f"   - 糙率：nm = {nm}（需定期清淤）")

    print(f"\n2. 滩地设计：")
    print(f"   - 宽度：左右各 {bl} m")
    print(f"   - 边坡：m2 = {m2}（缓坡，便于植被生长）")
    print(f"   - 糙率：nf = {nf}（控制植被高度）")
    print(f"   - 高差：hm = {hm} m（适当高度，避免频繁漫滩）")

    # 计算20年一遇流量
    Q_20yr = 400.0
    h_20yr = channel.compute_depth_from_discharge(Q_20yr)
    result_20yr = channel.discharge(h_20yr)

    print(f"\n3. 防洪能力：")
    print(f"   - 主槽满流：{Q_bankfull:.0f} m³/s（5年一遇）")
    print(f"   - 复式断面：{Q_20yr:.0f} m³/s（20年一遇）")
    print(f"   - 20年一遇水深：{h_20yr:.2f} m")
    print(f"   - 安全超高：≥ 0.5 m")
    print(f"   - 设计堤顶高程：{h_20yr + 0.5:.2f} m")

    print(f"\n4. 滩地管理措施：")
    print(f"   - 禁止种植高秆作物（如玉米、高粱）")
    print(f"   - 可种植草地或低矮灌木")
    print(f"   - 严禁修建永久性建筑物")
    print(f"   - 定期清除障碍物和垃圾")
    print(f"   - 设置警示标志和水位标尺")

    print(f"\n5. 护岸措施：")
    print(f"   - 主槽：石笼护岸或混凝土护坡")
    print(f"   - 滩地：植被护坡（生态护岸）")
    print(f"   - 主槽与滩地交界处：重点防护")
    print(f"   - 弯道段：加强防护")

    print(f"\n6. 监测要求：")
    print(f"   - 水位站：记录不同流量下的水深")
    print(f"   - 流速测量：验证流量分配")
    print(f"   - 断面测量：监测河床冲淤变化")
    print(f"   - 糙率率定：定期更新糙率参数")

    print(f"\n7. 维护管理：")
    print(f"   - 汛前检查：清理河道、修复护岸")
    print(f"   - 汛期巡查：监测水位、及时预警")
    print(f"   - 汛后整治：清淤、修复损坏设施")
    print(f"   - 滩地管理：控制植被、清除障碍")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
