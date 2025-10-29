"""
案例6：跌水消能设计 - 主程序

问题描述：
某山区灌溉渠道跌水设计，已知：
- 上游流量 Q = 5.0 m³/s
- 渠道宽度 b = 2.5 m
- 跌水落差 Δz = 2.0 m
- 上游水深 h0 = 1.2 m
- 下游渠底高程比跌水池底低 2.0 m

求解：
1. 跌水后的水流状态
2. 水跃共轭水深
3. 水跃能量损失
4. 消力池设计尺寸
5. 能量消散效率

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.structures import HydraulicJump


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
    print_separator("案例6：跌水消能设计")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】问题参数")
    print("-" * 80)

    Q = 5.0       # 流量 (m³/s)
    b = 2.5       # 渠道宽度 (m)
    dz = 2.0      # 跌水落差 (m)
    h0 = 1.2      # 上游水深 (m)
    g = 9.81      # 重力加速度 (m/s²)

    print(f"水工建筑物：跌水消能工")
    print(f"上游流量 Q = {Q} m³/s")
    print(f"渠道宽度 b = {b} m")
    print(f"跌水落差 Δz = {dz} m")
    print(f"上游水深 h0 = {h0} m")

    # 计算上游流速和比能
    v0 = Q / (b * h0)
    E0 = h0 + v0**2 / (2*g)
    Fr0 = v0 / np.sqrt(g * h0)

    print(f"\n上游水流状态：")
    print(f"  流速 v0 = {v0:.4f} m/s")
    print(f"  比能 E0 = {E0:.4f} m")
    print(f"  弗劳德数 Fr0 = {Fr0:.4f}")
    print(f"  流态：{'缓流' if Fr0 < 1 else '急流'}")

    # ==================== 第二步：跌水后水深计算 ====================
    print("\n【步骤2】跌水后水深计算")
    print("-" * 80)

    # 跌水后的比能
    E1 = E0 + dz
    print(f"\n跌水后总比能：E1 = E0 + Δz = {E0:.4f} + {dz:.4f} = {E1:.4f} m")

    # 临界水深
    q = Q / b
    hc = (q**2 / g) ** (1.0/3.0)
    print(f"\n临界水深：hc = (q²/g)^(1/3) = {hc:.4f} m")
    print(f"单宽流量：q = Q/b = {q:.4f} m²/s")

    # 跌水后水深（假设形成急流）
    # 使用能量方程求解：E1 = h1 + Q²/(2*g*b²*h1²)
    # 能量方程有两个解：急流解（h < hc）和缓流解（h > hc）
    # 跌水后应该是急流解
    # 迭代求解，从小于临界水深的初值开始
    h1 = hc * 0.5  # 初始猜测为0.5倍临界水深（急流解）

    for i in range(100):
        E1_calc = h1 + Q**2 / (2 * g * (b * h1)**2)
        f = E1_calc - E1

        if abs(f) < 1e-6:
            break

        # 数值导数
        dh = 1e-6
        E1_plus = (h1 + dh) + Q**2 / (2 * g * (b * (h1 + dh))**2)
        df = (E1_plus - E1_calc) / dh

        h1_new = h1 - f / df

        # 保证求得的是急流解（小于临界水深）
        if h1_new <= 0:
            h1_new = h1 / 2
        elif h1_new > hc:  # 如果超过临界水深，拉回来
            h1_new = (h1 + hc * 0.9) / 2

        h1 = h1_new

    v1 = Q / (b * h1)
    Fr1 = v1 / np.sqrt(g * h1)

    print(f"\n跌水后水流状态（跃前）：")
    print(f"  水深 h1 = {h1:.4f} m")
    print(f"  流速 v1 = {v1:.4f} m/s")
    print(f"  弗劳德数 Fr1 = {Fr1:.4f}")
    print(f"  流态：{'缓流' if Fr1 < 1 else '急流'}")

    if Fr1 < 1:
        print("\n注意：跌水后为缓流，不会发生水跃，需要增大跌水高度！")
        return

    # ==================== 第三步：水跃计算 ====================
    print("\n【步骤3】水跃计算")
    print("-" * 80)

    jump = HydraulicJump(b=b)

    # 共轭水深
    h2 = jump.conjugate_depth(h1, Fr1)
    v2 = Q / (b * h2)
    Fr2 = v2 / np.sqrt(g * h2)

    print(f"\n水跃共轭水深：")
    print(f"  跃前水深 h1 = {h1:.4f} m")
    print(f"  跃后水深 h2 = {h2:.4f} m")
    print(f"  水深比 h2/h1 = {h2/h1:.4f}")

    print(f"\n跃后水流状态：")
    print(f"  流速 v2 = {v2:.4f} m/s")
    print(f"  弗劳德数 Fr2 = {Fr2:.4f}")
    print(f"  流态：{'缓流' if Fr2 < 1 else '急流'}")

    # 水跃类型
    jump_type = jump.jump_type(Fr1)
    print(f"\n水跃类型：{jump_type}")

    # ==================== 第四步：能量损失计算 ====================
    print("\n【步骤4】能量损失计算")
    print("-" * 80)

    # 能量损失
    dE = jump.energy_loss(h1, h2)
    E1_jump = h1 + v1**2 / (2*g)
    E2_jump = h2 + v2**2 / (2*g)
    eta = jump.energy_dissipation_ratio(h1, h2, Q)

    print(f"\n跃前比能：E1 = h1 + v1²/(2g) = {E1_jump:.4f} m")
    print(f"跃后比能：E2 = h2 + v2²/(2g) = {E2_jump:.4f} m")
    print(f"能量损失：ΔE = E1 - E2 = {dE:.4f} m")
    print(f"消散效率：η = ΔE/E1 = {eta:.2f}%")

    print(f"\n能量损失分析：")
    print(f"  总跌落能量：Δz = {dz:.4f} m")
    print(f"  水跃消散能量：ΔE = {dE:.4f} m")
    print(f"  剩余能量：E2 - h2 = {E2_jump - h2:.4f} m (速度水头)")

    # ==================== 第五步：水跃长度计算 ====================
    print("\n【步骤5】水跃长度计算")
    print("-" * 80)

    Lj = jump.jump_length(h1, h2)

    print(f"\n水跃长度：Lj = {Lj:.4f} m")
    print(f"跃高：h2 - h1 = {h2 - h1:.4f} m")
    print(f"长度系数：Lj/(h2-h1) = {Lj/(h2-h1):.2f}")

    # ==================== 第六步：消力池设计 ====================
    print("\n【步骤6】消力池设计")
    print("-" * 80)

    # 消力池长度：取水跃长度的1.2倍
    L_pool = 1.2 * Lj

    # 消力池深度：保证跃前水深
    # 池底应低于跌水后水面，使h1满足要求
    d_pool = h1 + 0.3  # 增加安全余量

    # 池宽：等于渠道宽度
    B_pool = b

    # 尾坎高度：根据下游水深确定
    # 假设下游正常水深为1.0m
    h_downstream = 1.0
    if h2 > h_downstream:
        tail_sill_height = h2 - h_downstream
    else:
        tail_sill_height = 0.0

    print(f"\n消力池设计尺寸：")
    print(f"  1. 池长：L = {L_pool:.2f} m (取1.2倍水跃长度)")
    print(f"  2. 池深：d = {d_pool:.2f} m (保证跃前水深{h1:.2f}m)")
    print(f"  3. 池宽：B = {B_pool:.2f} m (等于渠道宽度)")
    print(f"  4. 尾坎高度：h = {tail_sill_height:.2f} m (抬高下游水位)")

    print(f"\n消力池结构：")
    print(f"  - 池底：钢筋混凝土，厚度0.3-0.5m")
    print(f"  - 侧墙：混凝土挡墙，顶部与渠顶平")
    print(f"  - 尾坎：混凝土尾坎，顶部做成圆弧形")
    print(f"  - 护坦：池后设置长{L_pool*0.5:.2f}m护坦过渡")

    # ==================== 第七步：消能效果分析 ====================
    print("\n【步骤7】消能效果分析")
    print("-" * 80)

    analysis = jump.analyze_jump(Q, h1)

    print(f"\n水跃综合分析：")
    print(f"  弗劳德数 Fr1 = {analysis['跃前Fr_Fr1']:.4f}")
    print(f"  水跃类型：{analysis['水跃类型']}")
    print(f"  共轭水深 h2 = {analysis['跃后水深_h2']:.4f} m")
    print(f"  能量损失 ΔE = {analysis['能量损失_dE']:.4f} m")
    print(f"  消散效率 η = {analysis['消能率_%']:.2f}%")
    print(f"  水跃长度 Lj = {analysis['水跃长度_Lj']:.4f} m")

    print(f"\n消能效果评价：")
    if Fr1 < 2.5:
        evaluation = "弱水跃，消能效果较差，建议增大跌水高度"
    elif Fr1 < 4.5:
        evaluation = "稳定水跃，消能效果良好★★★"
    elif Fr1 < 9.0:
        evaluation = "强水跃，消能效果很好★★★★"
    else:
        evaluation = "猛烈水跃，消能效果极佳但水流紊动剧烈"

    print(f"  {evaluation}")

    # ==================== 第八步：不同落差对比 ====================
    print("\n【步骤8】不同跌水落差对比")
    print("-" * 80)

    print(f"\n探讨不同跌水高度的消能效果：")
    print("-" * 110)
    print(f"{'跌水落差Δz(m)':^15} | {'跃前Fr1':^12} | {'跃后h2(m)':^13} | {'能量损失(m)':^14} | {'消散效率(%)':^14}")
    print("-" * 110)

    dz_values = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    for dz_test in dz_values:
        E1_test = E0 + dz_test

        # 求跌水后水深（急流解）
        h1_test = hc * 0.5  # 从小于临界水深开始
        for i in range(100):
            E1_calc = h1_test + Q**2 / (2 * g * (b * h1_test)**2)
            f = E1_calc - E1_test

            if abs(f) < 1e-6:
                break

            dh = 1e-6
            E1_plus = (h1_test + dh) + Q**2 / (2 * g * (b * (h1_test + dh))**2)
            df = (E1_plus - E1_calc) / dh

            h1_test = h1_test - f / df
            if h1_test <= 0:
                h1_test = hc / 2
            elif h1_test > hc:  # 保证是急流解
                h1_test = (h1_test + hc * 0.9) / 2

        v1_test = Q / (b * h1_test)
        Fr1_test = v1_test / np.sqrt(g * h1_test)

        if Fr1_test > 1:
            h2_test = jump.conjugate_depth(h1_test, Fr1_test)
            dE_test = jump.energy_loss(h1_test, h2_test)
            eta_test = jump.energy_dissipation_ratio(h1_test, h2_test, Q)
        else:
            h2_test = h1_test
            dE_test = 0.0
            eta_test = 0.0

        print(f"{dz_test:^15.2f} | {Fr1_test:^12.4f} | {h2_test:^13.4f} | {dE_test:^14.4f} | {eta_test:^14.2f}")

    print("-" * 110)
    print("\n结论：跌水高度越大，跃前Fr越大，消能效果越好")

    # ==================== 第九步：工程设计建议 ====================
    print("\n【步骤9】工程设计建议")
    print("-" * 80)

    print(f"\n基于水力计算的设计方案：")

    print(f"\n1. 跌水建筑物：")
    print(f"   - 跌水高度：Δz = {dz} m")
    print(f"   - 跌水型式：垂直跌水+消力池")
    print(f"   - 过流能力：Q = {Q} m³/s")
    print(f"   - 跌水宽度：B = {b} m")

    print(f"\n2. 消力池：")
    print(f"   - 池长：L = {L_pool:.2f} m")
    print(f"   - 池深：d = {d_pool:.2f} m")
    print(f"   - 池宽：B = {B_pool:.2f} m")
    print(f"   - 底板厚度：t = 0.4 m（钢筋混凝土）")

    print(f"\n3. 消能设施：")
    print(f"   - 尾坎高度：h = {tail_sill_height:.2f} m")
    print(f"   - 消力墩：可设置2-3排，增强消能")
    print(f"   - 护坦长度：L = {L_pool*0.5:.2f} m")
    print(f"   - 两侧挡墙：高度高出水面0.5m")

    print(f"\n4. 防冲刷措施：")
    print(f"   - 池底混凝土衬砌，C25以上")
    print(f"   - 下游海漫长度10-15m")
    print(f"   - 两侧浆砌石护坡")
    print(f"   - 齿墙深度1.5-2.0m，防止淘空")

    print(f"\n5. 水力性能：")
    print(f"   - 跌水消能：通过跌落获得急流")
    print(f"   - 水跃消能：Fr1 = {Fr1:.2f}，{jump_type}")
    print(f"   - 总消能：ΔE = {dE:.4f} m，η = {eta:.2f}%")
    print(f"   - 出池流态：缓流，Fr = {Fr2:.4f}")

    print(f"\n6. 运行管理：")
    print(f"   - 定期清除池内淤积物")
    print(f"   - 检查衬砌是否破损")
    print(f"   - 监测下游冲刷情况")
    print(f"   - 汛期加强巡查")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
