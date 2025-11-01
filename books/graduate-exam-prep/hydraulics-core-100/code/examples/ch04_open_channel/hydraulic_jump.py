#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水跃共轭水深计算
================

题目：清华大学2019年真题改编（第68题）
矩形断面渠道，跃前水深h₁=0.8m，跃前流速v₁=8 m/s

求解：
1. 跃前弗劳德数Fr₁
2. 跃后水深h₂（共轭水深）
3. 水跃长度Lj
4. 水跃能量损失ΔE
5. 能量损失率

作者：CHS-Books
日期：2025-10-31
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Rectangle, FancyBboxPatch

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


def froude_number(v, h, g=9.81):
    """计算弗劳德数"""
    return v / np.sqrt(g * h)


def conjugate_depth(h1, Fr1):
    """
    计算共轭水深（矩形断面）
    
    公式：h₂ = (h₁/2)·(√(1 + 8Fr₁²) - 1)
    
    参数：
        h1: 跃前水深 (m)
        Fr1: 跃前弗劳德数
    
    返回：
        h2: 跃后水深 (m)
    """
    h2 = (h1 / 2) * (np.sqrt(1 + 8 * Fr1**2) - 1)
    return h2


def jump_length(h1, h2, method='standard'):
    """
    计算水跃长度
    
    参数：
        h1: 跃前水深 (m)
        h2: 跃后水深 (m)
        method: 计算方法
            - 'standard': Lj = 5(h₂-h₁)
            - 'conservative': Lj = 6(h₂-h₁)
            - 'peterka': Lj = 6.1(h₂-h₁)
    
    返回：
        Lj: 水跃长度 (m)
    """
    if method == 'standard':
        Lj = 5 * (h2 - h1)
    elif method == 'conservative':
        Lj = 6 * (h2 - h1)
    elif method == 'peterka':
        Lj = 6.1 * (h2 - h1)
    else:
        Lj = 5 * (h2 - h1)
    
    return Lj


def energy_loss(h1, h2):
    """
    计算水跃能量损失（简化公式）
    
    ΔE = (h₂ - h₁)³ / (4h₁h₂)
    
    参数：
        h1: 跃前水深 (m)
        h2: 跃后水深 (m)
    
    返回：
        ΔE: 能量损失 (m)
    """
    ΔE = (h2 - h1)**3 / (4 * h1 * h2)
    return ΔE


def jump_type(Fr1):
    """
    根据Fr₁判断水跃类型
    
    参数：
        Fr1: 跃前弗劳德数
    
    返回：
        jump_type: 水跃类型字符串
        characteristics: 特征描述
    """
    if Fr1 < 1.0:
        return "无水跃（缓流）", "Fr < 1，不能发生水跃"
    elif Fr1 < 1.7:
        return "波状水跃", "水面波动，能量损失小"
    elif Fr1 < 2.5:
        return "弱水跃", "少量滚动，较稳定"
    elif Fr1 < 4.5:
        return "振荡水跃", "强烈振荡，不稳定"
    elif Fr1 < 9.0:
        return "稳定水跃", "剧烈翻滚，消能效果好"
    else:
        return "强水跃", "极其剧烈，消能效果最好"


def main():
    """主函数：求解强化题68"""
    
    print("=" * 70)
    print("水跃共轭水深计算")
    print("题目：清华大学2019年真题改编（第68题）")
    print("=" * 70)
    
    # ========== 已知条件 ==========
    b = 4.0          # 底宽 (m)
    h1 = 0.8         # 跃前水深 (m)
    v1 = 8.0         # 跃前流速 (m/s)
    g = 9.81         # 重力加速度 (m/s²)
    
    print("\n【已知条件】")
    print(f"底宽 b = {b} m")
    print(f"跃前水深 h₁ = {h1} m")
    print(f"跃前流速 v₁ = {v1} m/s")
    
    # ========== (1) 跃前弗劳德数Fr₁ ==========
    print("\n" + "=" * 70)
    print("(1) 跃前弗劳德数Fr₁")
    print("=" * 70)
    
    Fr1 = froude_number(v1, h1, g)
    
    print(f"\nFr₁ = v₁/√(g·h₁)")
    print(f"    = {v1}/√({g}×{h1})")
    print(f"    = {v1}/{np.sqrt(g*h1):.3f}")
    print(f"    = {Fr1:.3f}")
    
    jump_type_str, jump_char = jump_type(Fr1)
    
    print(f"\n判断：")
    print(f"  Fr₁ = {Fr1:.3f} > 1 → 急流（超临界流）")
    print(f"  可以发生水跃！")
    
    print(f"\n水跃类型：")
    print(f"  {jump_type_str}")
    print(f"  特征：{jump_char}")
    
    # ========== (2) 跃后水深h₂ ==========
    print("\n" + "=" * 70)
    print("(2) 跃后水深h₂（共轭水深）")
    print("=" * 70)
    
    h2 = conjugate_depth(h1, Fr1)
    
    print(f"\n共轭水深公式（矩形断面）：")
    print(f"  h₂ = (h₁/2)·(√(1 + 8Fr₁²) - 1)")
    print(f"     = ({h1}/2)·(√(1 + 8×{Fr1:.3f}²) - 1)")
    print(f"     = {h1/2:.1f}×(√(1 + 8×{Fr1**2:.3f}) - 1)")
    print(f"     = {h1/2:.1f}×(√(1 + {8*Fr1**2:.2f}) - 1)")
    print(f"     = {h1/2:.1f}×(√{1 + 8*Fr1**2:.2f} - 1)")
    print(f"     = {h1/2:.1f}×({np.sqrt(1 + 8*Fr1**2):.3f} - 1)")
    print(f"     = {h1/2:.1f}×{np.sqrt(1 + 8*Fr1**2) - 1:.3f}")
    print(f"     = {h2:.3f} m")
    
    # 验证
    Q = b * h1 * v1
    v2 = Q / (b * h2)
    Fr2 = froude_number(v2, h2, g)
    
    print(f"\n验证：")
    print(f"  流量守恒：Q = b·h₁·v₁ = {b}×{h1}×{v1} = {Q:.2f} m³/s")
    print(f"  跃后流速：v₂ = Q/(b·h₂) = {Q:.2f}/({b}×{h2:.3f}) = {v2:.3f} m/s")
    print(f"  跃后Fr₂：Fr₂ = v₂/√(g·h₂) = {v2:.3f}/√({g}×{h2:.3f}) = {Fr2:.3f} < 1 ✓")
    
    # ========== (3) 水跃长度Lj ==========
    print("\n" + "=" * 70)
    print("(3) 水跃长度Lj")
    print("=" * 70)
    
    Lj_standard = jump_length(h1, h2, 'standard')
    Lj_conservative = jump_length(h1, h2, 'conservative')
    
    print(f"\n经验公式：")
    print(f"  Lj = (4.5~6.0)·(h₂ - h₁)")
    
    print(f"\n标准公式（常用）：")
    print(f"  Lj = 5×(h₂ - h₁)")
    print(f"     = 5×({h2:.3f} - {h1})")
    print(f"     = 5×{h2 - h1:.3f}")
    print(f"     = {Lj_standard:.2f} m")
    
    print(f"\n保守公式：")
    print(f"  Lj = 6×(h₂ - h₁) = {Lj_conservative:.2f} m")
    
    print(f"\n根据{jump_type_str}特性：")
    if 2.5 < Fr1 < 4.5:
        factor = 5.2
        print(f"  Lj = {factor}×(h₂ - h₁) = {factor * (h2 - h1):.2f} m（振荡水跃修正）")
    
    # ========== (4) 水跃能量损失ΔE ==========
    print("\n" + "=" * 70)
    print("(4) 水跃能量损失ΔE")
    print("=" * 70)
    
    # 方法1：比能差
    E1 = h1 + v1**2 / (2 * g)
    E2 = h2 + v2**2 / (2 * g)
    ΔE_method1 = E1 - E2
    
    # 方法2：简化公式
    ΔE_method2 = energy_loss(h1, h2)
    
    print(f"\n【方法1】比能差法：")
    print(f"\n跃前比能：")
    print(f"  E₁ = h₁ + v₁²/(2g)")
    print(f"     = {h1} + {v1}²/(2×{g})")
    print(f"     = {h1} + {v1**2:.2f}/{2*g:.2f}")
    print(f"     = {h1} + {v1**2/(2*g):.3f}")
    print(f"     = {E1:.3f} m")
    
    print(f"\n跃后比能：")
    print(f"  E₂ = h₂ + v₂²/(2g)")
    print(f"     = {h2:.3f} + {v2:.3f}²/(2×{g})")
    print(f"     = {h2:.3f} + {v2**2/(2*g):.3f}")
    print(f"     = {E2:.3f} m")
    
    print(f"\n能量损失：")
    print(f"  ΔE = E₁ - E₂ = {E1:.3f} - {E2:.3f} = {ΔE_method1:.3f} m")
    
    print(f"\n【方法2】简化公式：")
    print(f"  ΔE = (h₂ - h₁)³/(4h₁h₂)")
    print(f"     = ({h2:.3f} - {h1})³/(4×{h1}×{h2:.3f})")
    print(f"     = {(h2-h1):.3f}³/{4*h1*h2:.3f}")
    print(f"     = {(h2-h1)**3:.3f}/{4*h1*h2:.3f}")
    print(f"     = {ΔE_method2:.3f} m")
    
    print(f"\n两种方法对比：")
    print(f"  方法1：ΔE = {ΔE_method1:.3f} m")
    print(f"  方法2：ΔE = {ΔE_method2:.3f} m")
    print(f"  误差：{abs(ΔE_method1 - ΔE_method2)/ΔE_method1*100:.2f}%")
    
    # ========== (5) 能量损失率 ==========
    print("\n" + "=" * 70)
    print("(5) 能量损失率")
    print("=" * 70)
    
    ε = ΔE_method1 / E1
    
    print(f"\n单位质量流体能量损失率：")
    print(f"  ε = ΔE/E₁ = {ΔE_method1:.3f}/{E1:.3f} = {ε:.4f} = {ε*100:.2f}%")
    
    print(f"\n总能量损失功率：")
    γ = 9810  # N/m³
    P_loss = γ * Q * ΔE_method1
    print(f"  P = γ·Q·ΔE")
    print(f"    = {γ}×{Q:.2f}×{ΔE_method1:.3f}")
    print(f"    = {P_loss:.0f} W")
    print(f"    = {P_loss/1000:.1f} kW")
    
    print(f"\n能量分析：")
    print(f"  跃前总能量：E₁ = {E1:.2f} m")
    print(f"  跃后总能量：E₂ = {E2:.2f} m")
    print(f"  损失能量：ΔE = {ΔE_method1:.2f} m（{ε*100:.1f}%）")
    print(f"  约{ε*100:.0f}%的能量在水跃中消耗（转化为热能和紊动能）")
    
    # ========== 绘图 ==========
    print("\n" + "=" * 70)
    print("绘制水跃示意图")
    print("=" * 70)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # ========== 子图1：水跃纵剖面 ==========
    # 渠底
    x_max = Lj_standard + 5
    ax1.plot([0, x_max], [0, 0], 'k-', linewidth=2, label='渠底')
    
    # 跃前段
    x_before = np.linspace(-3, 0, 50)
    y_before = np.ones_like(x_before) * h1
    ax1.fill_between(x_before, 0, y_before, color='lightblue', alpha=0.5)
    ax1.plot(x_before, y_before, 'b-', linewidth=2)
    
    # 水跃段
    x_jump = np.linspace(0, Lj_standard, 100)
    # 水面曲线（抛物线形状）
    y_jump = h1 + (h2 - h1) * (x_jump / Lj_standard)**0.7
    # 加入波动
    y_jump += 0.1 * (h2 - h1) * np.sin(5 * x_jump / Lj_standard) * np.exp(-x_jump / Lj_standard)
    
    ax1.fill_between(x_jump, 0, y_jump, color='cyan', alpha=0.6, label='水跃区')
    ax1.plot(x_jump, y_jump, 'b-', linewidth=2.5)
    
    # 跃后段
    x_after = np.linspace(Lj_standard, x_max, 50)
    y_after = np.ones_like(x_after) * h2
    ax1.fill_between(x_after, 0, y_after, color='lightblue', alpha=0.5)
    ax1.plot(x_after, y_after, 'b-', linewidth=2)
    
    # 标注水深
    ax1.plot([-1.5, -1.5], [0, h1], 'r-', linewidth=2)
    ax1.plot([-1.7, -1.3], [h1, h1], 'r-', linewidth=1.5)
    ax1.text(-2.2, h1/2, f'h₁={h1}m', fontsize=11, color='red', rotation=90, va='center')
    
    ax1.plot([x_max-1.5, x_max-1.5], [0, h2], 'r-', linewidth=2)
    ax1.plot([x_max-1.7, x_max-1.3], [h2, h2], 'r-', linewidth=1.5)
    ax1.text(x_max-2.2, h2/2, f'h₂={h2:.2f}m', fontsize=11, color='red', rotation=90, va='center')
    
    # 标注水跃长度
    ax1.annotate('', xy=(Lj_standard, -0.3), xytext=(0, -0.3),
                arrowprops=dict(arrowstyle='<->', color='green', lw=2))
    ax1.text(Lj_standard/2, -0.5, f'Lj={Lj_standard:.2f}m', fontsize=11, color='green', ha='center')
    
    # 标注Fr
    ax1.text(-1.5, h1+0.3, f'Fr₁={Fr1:.2f}', fontsize=10, color='blue', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    ax1.text(x_max-2, h2+0.3, f'Fr₂={Fr2:.2f}', fontsize=10, color='blue', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    
    ax1.set_xlim(-3.5, x_max)
    ax1.set_ylim(-1, h2+1)
    ax1.set_xlabel('距离 x (m)', fontsize=12)
    ax1.set_ylabel('水深 h (m)', fontsize=12)
    ax1.set_title(f'水跃纵剖面示意图（{jump_type_str}）', fontsize=14)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # ========== 子图2：能量线 ==========
    # 渠底
    ax2.plot([0, x_max], [0, 0], 'k-', linewidth=2, label='渠底')
    
    # 水面线
    x_water = np.concatenate([x_before, x_jump, x_after])
    y_water = np.concatenate([y_before, y_jump, y_after])
    ax2.plot(x_water, y_water, 'b-', linewidth=2, label='水面线')
    
    # 能量线
    # 跃前
    E_before = np.ones_like(x_before) * E1
    ax2.plot(x_before, E_before, 'r-', linewidth=2, label='能量线')
    
    # 水跃段（能量线下降）
    E_jump = E1 - ΔE_method1 * (x_jump / Lj_standard)**1.5
    ax2.plot(x_jump, E_jump, 'r-', linewidth=2)
    
    # 跃后
    E_after = np.ones_like(x_after) * E2
    ax2.plot(x_after, E_after, 'r-', linewidth=2)
    
    # 标注能量损失
    ax2.annotate('', xy=(Lj_standard/2, E2), xytext=(Lj_standard/2, E1),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax2.text(Lj_standard/2 + 0.5, (E1+E2)/2, f'ΔE={ΔE_method1:.2f}m\n({ε*100:.1f}%)', 
            fontsize=10, color='red', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    # 标注比能
    ax2.text(-1.5, E1+0.3, f'E₁={E1:.2f}m', fontsize=10, color='red', bbox=dict(boxstyle='round', facecolor='pink', alpha=0.5))
    ax2.text(x_max-2, E2+0.3, f'E₂={E2:.2f}m', fontsize=10, color='red', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    ax2.set_xlim(-3.5, x_max)
    ax2.set_ylim(-0.5, E1+1)
    ax2.set_xlabel('距离 x (m)', fontsize=12)
    ax2.set_ylabel('高程 (m)', fontsize=12)
    ax2.set_title('水跃能量线图', fontsize=14)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图片
    output_file = 'hydraulic_jump.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n图片已保存：{output_file}")
    
    plt.show()
    
    # ========== 总结 ==========
    print("\n" + "=" * 70)
    print("【总结】")
    print("=" * 70)
    print(f"1. 跃前Fr₁ = {Fr1:.2f} > 1（急流），可发生水跃")
    print(f"2. 水跃类型：{jump_type_str}")
    print(f"3. 跃后水深：h₂ = {h2:.2f} m（是h₁的{h2/h1:.2f}倍）")
    print(f"4. 水跃长度：Lj = {Lj_standard:.2f} m")
    print(f"5. 能量损失：ΔE = {ΔE_method1:.2f} m（损失{ε*100:.1f}%）")
    print(f"6. 消能功率：P = {P_loss/1000:.1f} kW")
    print(f"7. 跃后Fr₂ = {Fr2:.2f} < 1（缓流），流态稳定")
    print("=" * 70)


def exercise():
    """练习题"""
    print("\n" + "=" * 70)
    print("【练习题】")
    print("=" * 70)
    print("\n1. 若跃前流速v₁增加到10 m/s，h₂和ΔE如何变化？")
    print("2. 为什么共轭水深公式中有(h₁/2)和(-1)？")
    print("3. 水跃的能量损失到哪里去了？")
    print("4. 如何利用水跃进行消能设计？")
    print("5. 为什么Fr₁在2.5-4.5时水跃不稳定（振荡）？")
    print("=" * 70)


if __name__ == "__main__":
    main()
    exercise()
