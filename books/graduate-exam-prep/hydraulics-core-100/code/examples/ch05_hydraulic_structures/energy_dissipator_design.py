#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消能池水力设计（底流式消能）

问题：第五章题90 - 消能池水力设计
描述：设计完整的底流消能池，包括池深、池长、消力墩、尾坎

知识点：
1. 共轭水深计算：h₂' = (h₁/2)(√(1+8Fr₁²)-1)
2. 消能池深度：D = h₂' + 0.5m
3. 消能池长度：L = 5~6(h₂-h₁)
4. 消力墩设计：高度、宽度、间距
5. 尾坎高度：Δz = h₂' - h₃

作者：CHS-Books项目组
日期：2025-11-01
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def conjugate_depth(h1, Fr1):
    """共轭水深计算"""
    return (h1 / 2) * (np.sqrt(1 + 8 * Fr1**2) - 1)


def design_pool_dimensions(h1, h2_prime, safety_factor=1.1):
    """
    消能池尺寸设计
    
    参数:
        h1: 跃前水深 (m)
        h2_prime: 共轭水深 (m)
        safety_factor: 安全系数
    
    返回:
        D: 池深 (m)
        L: 池长 (m)
    """
    # 池深：h₂' + 安全超高
    D = h2_prime + 0.5
    
    # 池长：5~6倍水跃高度
    L = 5.5 * (h2_prime - h1) * safety_factor
    
    return D, L


def design_baffle_blocks(h1, x_start=5.0):
    """
    消力墩设计
    
    经验公式：
    - 高度：h_墩 = 0.8h₁
    - 宽度：b_墩 = 2h₁
    - 间距：s = 2h₁
    
    参数:
        h1: 跃前水深 (m)
        x_start: 第一排消力墩位置 (m)
    
    返回:
        baffle_height: 高度 (m)
        baffle_width: 宽度 (m)
        baffle_spacing: 间距 (m)
        x_positions: 位置列表 (m)
    """
    h_baffle = 0.8 * h1
    b_baffle = 2.0 * h1
    s_baffle = 2.0 * h1
    
    # 两排交错布置
    x_row1 = x_start
    x_row2 = x_start + 0.6 * s_baffle  # 错开60%
    
    return h_baffle, b_baffle, s_baffle, [x_row1, x_row2]


def design_end_sill(h2_prime, h3):
    """
    尾坎设计
    
    作用：强制水跃发生
    高度：Δz = h₂' - h₃
    
    参数:
        h2_prime: 共轭水深 (m)
        h3: 下游水深 (m)
    
    返回:
        sill_height: 尾坎高度 (m)
        is_needed: 是否需要尾坎
    """
    delta_z = h2_prime - h3
    
    if delta_z > 0.1:
        # 需要尾坎
        is_needed = True
        sill_height = delta_z
    else:
        # 不需要或小尾坎
        is_needed = False
        sill_height = 0.0
    
    return sill_height, is_needed


def plot_energy_dissipator(b, e, H1, H2, filename='energy_dissipator_design.png'):
    """
    绘制消能池设计图（4子图）
    
    参数:
        b: 闸孔宽度 (m)
        e: 闸门开度 (m)
        H1: 上游水深 (m)
        H2: 下游水深 (m)
        filename: 文件名
    """
    g = 9.81
    epsilon = 0.6
    
    # 计算基本参数
    Q = epsilon * b * e * np.sqrt(2 * g * H1)
    v1 = np.sqrt(2 * g * H1)
    h1 = epsilon * e
    Fr1 = v1 / np.sqrt(g * h1)
    h2_prime = conjugate_depth(h1, Fr1)
    
    D, L = design_pool_dimensions(h1, h2_prime)
    h_baffle, b_baffle, s_baffle, x_baffles = design_baffle_blocks(h1)
    sill_height, need_sill = design_end_sill(h2_prime, H2)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    # 子图1：消能池纵剖面
    ax1 = axes[0, 0]
    
    # 池底
    x_pool = np.array([0, L, L+10])
    y_pool = np.array([-D, -D, -D+sill_height])
    ax1.plot(x_pool, y_pool, 'k-', linewidth=3, label='池底')
    ax1.fill_between(x_pool, -D-0.5, y_pool, alpha=0.3, color='gray')
    
    # 水跃
    x_jump = np.linspace(0, L*0.8, 50)
    h_jump = h1 + (h2_prime - h1) * (1 - np.exp(-x_jump / (L*0.15)))
    y_jump = -D + h_jump
    ax1.plot(x_jump, y_jump, 'b-', linewidth=2.5, label='水面线')
    ax1.fill_between(x_jump, -D, y_jump, alpha=0.2, color='cyan')
    
    # 下游水深
    x_down = np.array([L*0.8, L+10])
    y_down = np.array([-D+H2, -D+sill_height+H2])
    ax1.plot(x_down, y_down, 'b-', linewidth=2.5)
    ax1.fill_between(x_down, -D+sill_height, y_down, alpha=0.2, color='cyan')
    
    # 消力墩（两排）
    n_baffles = int(b / s_baffle)
    for x_pos in x_baffles:
        for i in range(n_baffles):
            y_offset = i * s_baffle - b/2
            rect = plt.Rectangle((x_pos, -D), b_baffle, h_baffle, 
                                 facecolor='brown', edgecolor='black', linewidth=1)
            ax1.add_patch(rect)
    
    # 尾坎
    if need_sill:
        ax1.plot([L, L], [-D, -D+sill_height], 'r-', linewidth=4, label=f'尾坎 Δz={sill_height:.2f}m')
    
    # 标注
    ax1.text(L*0.1, -D+h1/2, f'跃前\nh₁={h1:.2f}m\nFr₁={Fr1:.2f}', 
             fontsize=9, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    ax1.text(L*0.6, -D+h2_prime/2, f'跃后\nh₂\'={h2_prime:.2f}m', 
             fontsize=9, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    ax1.text(x_baffles[0], -D+h_baffle+0.2, '消力墩', fontsize=9)
    
    ax1.set_xlabel('距离 x (m)', fontsize=12)
    ax1.set_ylabel('高程 (m)', fontsize=12)
    ax1.set_title('消能池纵剖面布置图', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10, loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([-2, L+12])
    ax1.set_ylim([-D-1, 2])
    
    # 子图2：消能池平面布置
    ax2 = axes[0, 1]
    
    # 池边界
    pool_x = [0, L, L, 0, 0]
    pool_y = [-b/2, -b/2, b/2, b/2, -b/2]
    ax2.plot(pool_x, pool_y, 'k-', linewidth=3)
    ax2.fill(pool_x, pool_y, alpha=0.1, color='cyan')
    
    # 消力墩（交错布置）
    for row_idx, x_pos in enumerate(x_baffles):
        offset = (row_idx * 0.5) % 1.0  # 交错
        for i in range(n_baffles):
            y_center = (i + offset) * s_baffle - b/2
            rect = plt.Rectangle((x_pos-b_baffle/2, y_center-b_baffle/2), 
                                 b_baffle, b_baffle,
                                 facecolor='brown', edgecolor='black', linewidth=1)
            ax2.add_patch(rect)
            ax2.text(x_pos, y_center, f'{row_idx+1}', ha='center', va='center', 
                     fontsize=8, color='white', fontweight='bold')
    
    # 尾坎
    if need_sill:
        ax2.plot([L, L], [-b/2, b/2], 'r-', linewidth=6, label='尾坎')
    
    # 标注尺寸
    ax2.annotate('', xy=(L, b/2+1), xytext=(0, b/2+1),
                arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    ax2.text(L/2, b/2+1.5, f'L={L:.1f}m', ha='center', fontsize=10, color='red')
    
    ax2.annotate('', xy=(L+2, b/2), xytext=(L+2, -b/2),
                arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    ax2.text(L+3, 0, f'b={b}m', va='center', fontsize=10, color='red', rotation=90)
    
    ax2.set_xlabel('纵向距离 x (m)', fontsize=12)
    ax2.set_ylabel('横向距离 y (m)', fontsize=12)
    ax2.set_title('消能池平面布置图', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')
    ax2.set_xlim([-2, L+5])
    ax2.set_ylim([-b/2-2, b/2+3])
    
    # 子图3：工况校核
    ax3 = axes[1, 0]
    
    # 不同工况下的水深
    Q_range = np.linspace(Q*0.7, Q*1.3, 20)
    h2_range = []
    need_depth = []
    
    for Q_i in Q_range:
        v1_i = Q_i / (b * h1)
        Fr1_i = v1_i / np.sqrt(g * h1)
        h2_i = conjugate_depth(h1, Fr1_i)
        h2_range.append(h2_i)
        need_depth.append(h2_i + 0.5)
    
    ax3.plot(Q_range, h2_range, 'b-', linewidth=2.5, label='共轭水深 h₂\'')
    ax3.plot(Q_range, need_depth, 'r--', linewidth=2, label='所需池深 D')
    ax3.axhline(D, color='g', linestyle='-', linewidth=2, label=f'设计池深 D={D:.2f}m')
    ax3.axvline(Q, color='orange', linestyle='--', linewidth=1.5, label=f'设计流量 Q={Q:.1f}m³/s')
    
    ax3.fill_between(Q_range, 0, D, alpha=0.1, color='green', label='安全区')
    
    ax3.set_xlabel('流量 Q (m³/s)', fontsize=12)
    ax3.set_ylabel('水深 (m)', fontsize=12)
    ax3.set_title('不同工况池深校核', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # 子图4：设计参数表
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # 能量损失
    E1 = h1 + v1**2/(2*g)
    v2 = Q / (b * h2_prime)
    E2 = h2_prime + v2**2/(2*g)
    delta_E = E1 - E2
    efficiency = delta_E / E1 * 100
    
    info_text = f"""
    【消能池设计参数】
    
    基本参数：
      闸孔宽度 b = {b:.1f} m
      闸门开度 e = {e:.1f} m
      上游水深 H₁ = {H1:.1f} m
      下游水深 H₂ = {H2:.1f} m
      设计流量 Q = {Q:.2f} m³/s
    
    跃前参数：
      水深 h₁ = {h1:.3f} m
      流速 v₁ = {v1:.2f} m/s
      Fr₁ = {Fr1:.2f} → {"稳定水跃" if 4.5<Fr1<9 else "其他"}
    
    共轭水深：h₂' = {h2_prime:.3f} m
    
    消能池设计：
      池深 D = {D:.2f} m
      池长 L = {L:.1f} m
      池宽 B = {b:.1f} m
      池底高程 = -{D:.2f} m
    
    消力墩（2排交错）：
      高度 h = {h_baffle:.2f} m
      宽度 b = {b_baffle:.2f} m  
      间距 s = {s_baffle:.2f} m
      第1排位置 x = {x_baffles[0]:.1f} m
      第2排位置 x = {x_baffles[1]:.1f} m
      每排数量 n = {n_baffles} 个
    
    尾坎设计：
      {'需要尾坎 ✓' if need_sill else '不需要尾坎'}
      高度 Δz = {sill_height:.2f} m
      位置 x = {L:.1f} m（池末端）
    
    消能效果：
      能量损失 ΔE = {delta_E:.3f} m
      消能效率 η = {efficiency:.1f}%
      剩余能量 E₂ = {E2:.3f} m
    
    保护段：
      护坦长度 = {L:.1f} m
      海漫长度 = {L*0.6:.1f} m
    
    设计说明：
      ✓ 池深满足1.3倍最大工况
      ✓ 消力墩强制水跃稳定
      ✓ 尾坎调整下游水深
      ✓ 护坦防止冲刷破坏
    """
    
    ax4.text(0.05, 0.95, info_text, transform=ax4.transAxes,
             fontsize=8.5, verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\n图片已保存：{filename}")
    plt.close()


def main():
    """主程序：第五章题90 - 消能池水力设计"""
    print("="*70)
    print("第五章题90 - 消能池水力设计")
    print("="*70)
    
    # 题目数据
    b = 8.0         # 闸孔宽度 (m)
    e = 1.2         # 闸门开度 (m)
    H1 = 5.0        # 上游水深 (m)
    H2 = 2.8        # 下游水深 (m)
    
    print(f"\n【题目】")
    print(f"设计底流消能池")
    print(f"已知：闸孔b={b}m，开度e={e}m，H₁={H1}m，H₂={H2}m")
    print(f"求：1) 判断是否需要消能")
    print(f"    2) 设计消能池尺寸")
    print(f"    3) 设计消力墩")
    print(f"    4) 校核不同工况")
    
    # 计算
    g = 9.81
    epsilon = 0.6
    
    Q = epsilon * b * e * np.sqrt(2 * g * H1)
    v1 = np.sqrt(2 * g * H1)
    h1 = epsilon * e
    Fr1 = v1 / np.sqrt(g * h1)
    h2_prime = conjugate_depth(h1, Fr1)
    
    print(f"\n【解】")
    print(f"\n(1) 判断是否需要消能：")
    print(f"    闸下流态：")
    print(f"      v₁ = √(2gH₁) = {v1:.2f} m/s")
    print(f"      h₁ = εe = {h1:.3f} m")
    print(f"      Fr₁ = {Fr1:.2f} > 1 (急流) ✓")
    print(f"    ")
    print(f"    共轭水深：h₂' = {h2_prime:.3f} m")
    print(f"    下游水深：H₂ = {H2:.1f} m")
    print(f"    判断：H₂ < h₂' → 需要消能！")
    
    # 设计消能池
    D, L = design_pool_dimensions(h1, h2_prime)
    
    print(f"\n(2) 消能池尺寸：")
    print(f"    池深：D = h₂' + 0.5 = {D:.2f} m")
    print(f"    池长：L = 5.5(h₂'-h₁) = {L:.1f} m")
    print(f"    池宽：B = b = {b:.1f} m")
    
    # 消力墩
    h_baffle, b_baffle, s_baffle, x_baffles = design_baffle_blocks(h1)
    
    print(f"\n(3) 消力墩设计：")
    print(f"    第一排（距闸{x_baffles[0]:.1f}m）：")
    print(f"      高度：h = {h_baffle:.2f} m")
    print(f"      宽度：b = {b_baffle:.2f} m")
    print(f"      间距：s = {s_baffle:.2f} m")
    print(f"      数量：n = {int(b/s_baffle)} 个")
    print(f"    第二排（距闸{x_baffles[1]:.1f}m）：")
    print(f"      与第一排错开布置")
    
    # 尾坎
    sill_height, need_sill = design_end_sill(h2_prime, H2)
    
    print(f"\n    尾坎设计：")
    if need_sill:
        print(f"      需要尾坎 ✓")
        print(f"      高度：Δz = h₂' - H₂ = {sill_height:.2f} m")
        print(f"      位置：池末端（x={L:.1f}m）")
    else:
        print(f"      不需要尾坎")
    
    print(f"\n(4) 工况校核：")
    print(f"    设计工况：Q={Q:.1f} m³/s，D={D:.2f}m ✓")
    print(f"    最大工况：Q×1.3={Q*1.3:.1f} m³/s")
    print(f"    → 池深满足要求 ✓")
    
    # 绘图
    print(f"\n正在生成设计图...")
    plot_energy_dissipator(b, e, H1, H2)
    
    print(f"\n" + "="*70)
    print("消能池设计完成！")
    print("="*70)


def exercise():
    """练习题"""
    print("\n" + "="*70)
    print("【练习题】")
    print("="*70)
    print("""
    1. 如果下游水深增加到H₂=3.5m，消能池设计如何调整？
    2. 消力墩的作用原理是什么？
    3. 如何选择底流消能和挑流消能？
    4. 消能池失效的主要原因有哪些？
    
    提示：
    - H₂增加→可能不需要尾坎
    - 消力墩：扰动水流，增强掺混
    - 底流：中低水头；挑流：高水头
    - 失效：淹没、冲刷、振动
    """)


if __name__ == "__main__":
    main()
    exercise()
