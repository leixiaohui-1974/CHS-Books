#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矩形断面临界水深计算
====================

题目：河海大学2020年真题改编（第66题）
矩形断面渠道，底宽b=5m，通过流量Q=20 m³/s

求解：
1. 临界水深hc
2. 临界流速vc和临界比能Ec
3. 不同实际水深的流态判别

作者：CHS-Books
日期：2025-10-31
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


def critical_depth_rectangular(Q, b, g=9.81):
    """
    矩形断面临界水深计算（显式公式）
    
    公式：hc = ∛(q²/g)，其中 q = Q/b
    
    参数：
        Q: 流量 (m³/s)
        b: 底宽 (m)
        g: 重力加速度 (m/s²)
    
    返回：
        hc: 临界水深 (m)
        q: 单宽流量 (m²/s)
    """
    q = Q / b  # 单宽流量
    hc = (q**2 / g) ** (1/3)
    return hc, q


def critical_velocity(q, hc):
    """
    计算临界流速
    
    参数：
        q: 单宽流量 (m²/s)
        hc: 临界水深 (m)
    
    返回：
        vc: 临界流速 (m/s)
    """
    return q / hc


def critical_specific_energy(hc, vc, g=9.81):
    """
    计算临界比能
    
    Ec = hc + vc²/(2g) = (3/2)hc （矩形断面特性）
    
    参数：
        hc: 临界水深 (m)
        vc: 临界流速 (m/s)
        g: 重力加速度 (m/s²)
    
    返回：
        Ec: 临界比能 (m)
    """
    Ec_kinetic = vc**2 / (2 * g)
    Ec = hc + Ec_kinetic
    return Ec, Ec_kinetic


def froude_number(v, h, g=9.81):
    """
    计算弗劳德数
    
    Fr = v / √(gh)
    
    参数：
        v: 流速 (m/s)
        h: 水深 (m)
        g: 重力加速度 (m/s²)
    
    返回：
        Fr: 弗劳德数
    """
    return v / np.sqrt(g * h)


def flow_regime(h, hc, Fr):
    """
    判断流态
    
    参数：
        h: 实际水深 (m)
        hc: 临界水深 (m)
        Fr: 弗劳德数
    
    返回：
        regime: 流态字符串
    """
    if Fr < 1:
        regime = "缓流（亚临界流）"
        depth_type = "缓流深度"
    elif Fr > 1:
        regime = "急流（超临界流）"
        depth_type = "急流深度"
    else:
        regime = "临界流"
        depth_type = "临界深度"
    
    if abs(h - hc) < 0.01:
        depth_relation = "h ≈ hc（临界深度）"
    elif h > hc:
        depth_relation = f"h > hc（{depth_type}）"
    else:
        depth_relation = f"h < hc（{depth_type}）"
    
    return regime, depth_relation


def specific_energy(h, v, g=9.81):
    """
    计算比能
    
    E = h + v²/(2g)
    
    参数：
        h: 水深 (m)
        v: 流速 (m/s)
        g: 重力加速度 (m/s²)
    
    返回：
        E: 比能 (m)
    """
    return h + v**2 / (2 * g)


def plot_specific_energy_curve(Q, b, h_range=None, g=9.81):
    """
    绘制比能曲线（E-h关系）
    
    参数：
        Q: 流量 (m³/s)
        b: 底宽 (m)
        h_range: 水深范围 (m)
        g: 重力加速度 (m/s²)
    
    返回：
        fig: 图形对象
    """
    if h_range is None:
        hc, q = critical_depth_rectangular(Q, b, g)
        h_range = [0.3 * hc, 3.0 * hc]
    
    h_values = np.linspace(h_range[0], h_range[1], 200)
    q = Q / b
    
    # 计算比能
    E_values = []
    for h in h_values:
        v = q / h
        E = specific_energy(h, v, g)
        E_values.append(E)
    
    # 临界点
    hc, q = critical_depth_rectangular(Q, b, g)
    vc = critical_velocity(q, hc)
    Ec, _ = critical_specific_energy(hc, vc, g)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 绘制比能曲线
    ax.plot(E_values, h_values, 'b-', linewidth=2, label='E-h曲线')
    
    # 标注临界点
    ax.plot(Ec, hc, 'ro', markersize=12, label=f'临界点: hc={hc:.3f}m, Ec={Ec:.3f}m', zorder=5)
    
    # 分界线
    ax.axhline(y=hc, color='red', linestyle='--', alpha=0.5, label='临界水深线')
    ax.axvline(x=Ec, color='red', linestyle='--', alpha=0.5, label='最小比能线')
    
    # 区域标注
    h_mid_upper = (hc + h_range[1]) / 2
    h_mid_lower = (hc + h_range[0]) / 2
    
    E_at_mid_upper = h_mid_upper + (q/h_mid_upper)**2 / (2*g)
    E_at_mid_lower = h_mid_lower + (q/h_mid_lower)**2 / (2*g)
    
    ax.text(E_at_mid_upper, h_mid_upper, '缓流区\n(Fr<1)', 
            fontsize=12, ha='left', va='center', color='blue', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    ax.text(E_at_mid_lower, h_mid_lower, '急流区\n(Fr>1)', 
            fontsize=12, ha='left', va='center', color='green', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    
    ax.set_xlabel('比能 E (m)', fontsize=12)
    ax.set_ylabel('水深 h (m)', fontsize=12)
    ax.set_title(f'比能曲线（Q={Q}m³/s, b={b}m）', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    return fig


def main():
    """主函数：求解基础题66"""
    
    print("=" * 70)
    print("矩形断面临界水深计算")
    print("题目：河海大学2020年真题改编（第66题）")
    print("=" * 70)
    
    # ========== 已知条件 ==========
    b = 5.0          # 底宽 (m)
    Q = 20.0         # 流量 (m³/s)
    g = 9.81         # 重力加速度 (m/s²)
    
    print("\n【已知条件】")
    print(f"底宽 b = {b} m")
    print(f"流量 Q = {Q} m³/s")
    
    # ========== (1) 临界水深hc ==========
    print("\n" + "=" * 70)
    print("(1) 临界水深hc")
    print("=" * 70)
    
    hc, q = critical_depth_rectangular(Q, b, g)
    
    print(f"\n单宽流量：q = Q/b = {Q}/{b} = {q:.3f} m²/s")
    print(f"\n临界水深公式（矩形）：")
    print(f"  hc = ∛(q²/g)")
    print(f"     = ∛({q:.3f}²/{g})")
    print(f"     = ∛({q**2:.3f}/{g})")
    print(f"     = ∛{q**2/g:.3f}")
    print(f"     = {hc:.3f} m")
    
    # ========== (2) 临界流速vc和临界比能Ec ==========
    print("\n" + "=" * 70)
    print("(2) 临界流速vc和临界比能Ec")
    print("=" * 70)
    
    vc = critical_velocity(q, hc)
    Ec, Ec_kinetic = critical_specific_energy(hc, vc, g)
    
    print(f"\n临界流速：")
    print(f"  vc = q/hc = {q:.3f}/{hc:.3f} = {vc:.3f} m/s")
    
    # 验证Fr = 1
    Fr_c = froude_number(vc, hc, g)
    print(f"\n验证弗劳德数：")
    print(f"  Fr = vc/√(g·hc) = {vc:.3f}/√({g}×{hc:.3f})")
    print(f"     = {vc:.3f}/{np.sqrt(g*hc):.3f}")
    print(f"     = {Fr_c:.6f} ≈ 1.000 ✓")
    
    print(f"\n临界比能：")
    print(f"  Ec = hc + vc²/(2g)")
    print(f"     = {hc:.3f} + {vc:.3f}²/(2×{g})")
    print(f"     = {hc:.3f} + {vc**2:.3f}/{2*g:.2f}")
    print(f"     = {hc:.3f} + {Ec_kinetic:.3f}")
    print(f"     = {Ec:.3f} m")
    
    # 验证矩形断面特性 Ec = 1.5hc
    Ec_theory = 1.5 * hc
    print(f"\n验证矩形断面特性：")
    print(f"  Ec = (3/2)hc = 1.5×{hc:.3f} = {Ec_theory:.3f} m")
    print(f"  实际计算：Ec = {Ec:.3f} m")
    print(f"  误差：{abs(Ec-Ec_theory)/Ec_theory*100:.4f}%")
    
    # ========== (3) 实际水深h=1.5m的流态 ==========
    print("\n" + "=" * 70)
    print("(3) 实际水深h=1.5m的流态")
    print("=" * 70)
    
    h1 = 1.5
    v1 = Q / (b * h1)
    Fr1 = froude_number(v1, h1, g)
    E1 = specific_energy(h1, v1, g)
    regime1, depth_rel1 = flow_regime(h1, hc, Fr1)
    
    print(f"\n实际水深：h = {h1} m")
    print(f"临界水深：hc = {hc:.3f} m")
    print(f"对比：h = {h1} m {'>' if h1 > hc else '<' if h1 < hc else '='} hc = {hc:.3f} m")
    
    print(f"\n流速计算：")
    print(f"  v = Q/(b·h) = {Q}/({b}×{h1}) = {v1:.3f} m/s")
    
    print(f"\n弗劳德数：")
    print(f"  Fr = v/√(g·h) = {v1:.3f}/√({g}×{h1})")
    print(f"     = {v1:.3f}/{np.sqrt(g*h1):.3f}")
    print(f"     = {Fr1:.3f}")
    
    print(f"\n流态判断：")
    print(f"  Fr = {Fr1:.3f} {'<' if Fr1 < 1 else '>' if Fr1 > 1 else '='} 1")
    print(f"  流态：{regime1}")
    print(f"  水深关系：{depth_rel1}")
    
    print(f"\n比能：")
    print(f"  E = h + v²/(2g) = {h1} + {v1:.3f}²/(2×{g})")
    print(f"    = {h1} + {v1**2/(2*g):.3f}")
    print(f"    = {E1:.3f} m")
    print(f"  与Ec对比：E = {E1:.3f} m {'>' if E1 > Ec else '<'} Ec = {Ec:.3f} m")
    
    # ========== (4) 实际水深h=2.5m的流态 ==========
    print("\n" + "=" * 70)
    print("(4) 实际水深h=2.5m的流态")
    print("=" * 70)
    
    h2 = 2.5
    v2 = Q / (b * h2)
    Fr2 = froude_number(v2, h2, g)
    E2 = specific_energy(h2, v2, g)
    regime2, depth_rel2 = flow_regime(h2, hc, Fr2)
    
    print(f"\n实际水深：h = {h2} m")
    print(f"临界水深：hc = {hc:.3f} m")
    print(f"对比：h = {h2} m > hc = {hc:.3f} m")
    
    print(f"\n流速：v = {v2:.3f} m/s")
    print(f"弗劳德数：Fr = {Fr2:.3f} < 1")
    print(f"流态：{regime2}")
    print(f"比能：E = {E2:.3f} m")
    
    # ========== 对比分析 ==========
    print("\n" + "=" * 70)
    print("对比分析")
    print("=" * 70)
    
    print(f"\n{'水深h(m)':<12} {'流速v(m/s)':<15} {'Fr':<10} {'比能E(m)':<12} {'流态':<20}")
    print("-" * 70)
    print(f"{hc:<12.3f} {vc:<15.3f} {Fr_c:<10.3f} {Ec:<12.3f} {'临界流':<20}")
    print(f"{h1:<12.3f} {v1:<15.3f} {Fr1:<10.3f} {E1:<12.3f} {regime1:<20}")
    print(f"{h2:<12.3f} {v2:<15.3f} {Fr2:<10.3f} {E2:<12.3f} {regime2:<20}")
    
    print(f"\n结论：")
    print(f"  - 水深越大，流速越小，Fr越小")
    print(f"  - h > hc时，Fr < 1，为缓流（稳定）")
    print(f"  - h < hc时，Fr > 1，为急流（不稳定）")
    print(f"  - 比能E在h=hc时取最小值Ec={Ec:.3f}m")
    
    # ========== 绘图：比能曲线 ==========
    print("\n" + "=" * 70)
    print("绘制比能曲线")
    print("=" * 70)
    
    fig = plot_specific_energy_curve(Q, b, g=g)
    
    # 标注示例点
    ax = fig.axes[0]
    ax.plot(E1, h1, 'bs', markersize=10, label=f'h={h1}m: E={E1:.2f}m, Fr={Fr1:.2f}', zorder=4)
    ax.plot(E2, h2, 'gs', markersize=10, label=f'h={h2}m: E={E2:.2f}m, Fr={Fr2:.2f}', zorder=4)
    ax.legend(fontsize=9)
    
    plt.tight_layout()
    
    # 保存图片
    output_file = 'critical_depth_rectangular.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n图片已保存：{output_file}")
    
    plt.show()
    
    # ========== 总结 ==========
    print("\n" + "=" * 70)
    print("【总结】")
    print("=" * 70)
    print(f"1. 临界水深：hc = {hc:.2f} m")
    print(f"2. 临界流速：vc = {vc:.2f} m/s")
    print(f"3. 临界比能：Ec = {Ec:.2f} m = (3/2)hc")
    print(f"4. h=1.5m：{regime1}（Fr={Fr1:.2f}）")
    print(f"5. h=2.5m：{regime2}（Fr={Fr2:.2f}）")
    print(f"6. 比能曲线呈U型，hc处比能最小")
    print("=" * 70)


def exercise():
    """练习题"""
    print("\n" + "=" * 70)
    print("【练习题】")
    print("=" * 70)
    print("\n1. 若流量Q增加到30 m³/s，hc如何变化？")
    print("2. 若底宽b减小到3m（保持Q不变），hc如何变化？")
    print("3. 为什么临界比能Ec = (3/2)hc仅对矩形断面成立？")
    print("4. 比能曲线的物理意义是什么？")
    print("5. 工程中为什么要避免Fr ≈ 1的流态？")
    print("=" * 70)


if __name__ == "__main__":
    main()
    exercise()
