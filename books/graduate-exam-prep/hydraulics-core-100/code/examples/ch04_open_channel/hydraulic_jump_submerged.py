#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淹没水跃计算与分析

问题：第四章题69 - 淹没水跃分析
描述：下游水深大于共轭水深时形成淹没水跃，消能效率降低

知识点：
1. 淹没水跃判别：h₃ > h₂'（共轭水深）
2. 淹没度：σ = h₃/h₂'
3. 消能效率降低
4. 工程处理措施

作者：CHS-Books项目组
日期：2025-10-31
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def froude_number(v, h, g=9.81):
    """
    弗劳德数计算
    
    参数:
        v: 流速 (m/s)
        h: 水深 (m)
        g: 重力加速度 (m/s²)
    
    返回:
        Fr: 弗劳德数
    """
    return v / np.sqrt(g * h)


def conjugate_depth(h1, Fr1):
    """
    共轭水深计算（矩形断面）
    
    h₂' = (h₁/2) * (√(1 + 8Fr₁²) - 1)
    
    参数:
        h1: 跃前水深 (m)
        Fr1: 跃前弗劳德数
    
    返回:
        h2_prime: 共轭水深 (m)
    """
    h2_prime = (h1 / 2) * (np.sqrt(1 + 8 * Fr1**2) - 1)
    return h2_prime


def jump_length(h1, h2):
    """
    水跃长度经验公式
    
    L_j = 5 * (h₂ - h₁)
    
    参数:
        h1: 跃前水深 (m)
        h2: 跃后水深 (m)
    
    返回:
        Lj: 水跃长度 (m)
    """
    return 5 * (h2 - h1)


def energy_loss_free_jump(h1, h2):
    """
    自由水跃能量损失
    
    ΔE = (h₂ - h₁)³ / (4h₁h₂)
    
    参数:
        h1: 跃前水深 (m)
        h2: 跃后水深 (m)
    
    返回:
        delta_E: 能量损失 (m)
    """
    return (h2 - h1)**3 / (4 * h1 * h2)


def energy_loss_submerged_jump(h1, h2_prime, h3, v1, g=9.81):
    """
    淹没水跃能量损失（近似）
    
    参数:
        h1: 跃前水深 (m)
        h2_prime: 共轭水深 (m)
        h3: 实际下游水深 (m)
        v1: 跃前流速 (m/s)
        g: 重力加速度 (m/s²)
    
    返回:
        delta_E: 能量损失 (m)
        delta_E_free: 自由水跃能量损失 (m)
        efficiency_ratio: 消能效率比
    """
    # 自由水跃能量损失
    delta_E_free = energy_loss_free_jump(h1, h2_prime)
    
    # 淹没水跃能量损失（经验公式）
    # 近似：ΔE ≈ ΔE_free * (1 - k*(h₃/h₂' - 1))
    # 其中k为经验系数，约0.3-0.5
    sigma = h3 / h2_prime  # 淹没度
    k = 0.4  # 经验系数
    
    if sigma > 1:
        delta_E = delta_E_free * (1 - k * (sigma - 1))
        if delta_E < 0:
            delta_E = 0
    else:
        delta_E = delta_E_free
    
    efficiency_ratio = delta_E / delta_E_free if delta_E_free > 0 else 1.0
    
    return delta_E, delta_E_free, efficiency_ratio


def jump_type_classification(Fr1):
    """
    水跃类型分类
    
    参数:
        Fr1: 跃前弗劳德数
    
    返回:
        jump_type: 水跃类型字符串
    """
    if Fr1 < 1:
        return "无水跃（缓流）"
    elif 1 <= Fr1 < 1.7:
        return "波状水跃（undular jump）"
    elif 1.7 <= Fr1 < 2.5:
        return "弱水跃（weak jump）"
    elif 2.5 <= Fr1 < 4.5:
        return "摆动水跃（oscillating jump）"
    elif 4.5 <= Fr1 < 9.0:
        return "稳定水跃（steady jump）"
    else:
        return "强水跃（strong jump）"


def plot_submerged_jump_analysis(h1, v1, h2_prime, h3, Fr1, filename='hydraulic_jump_submerged.png'):
    """
    绘制淹没水跃分析图（4子图）
    
    参数:
        h1: 跃前水深 (m)
        v1: 跃前流速 (m/s)
        h2_prime: 共轭水深 (m)
        h3: 实际下游水深 (m)
        Fr1: 跃前弗劳德数
        filename: 保存文件名
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    g = 9.81
    
    # 计算关键参数
    Q = v1 * h1  # 单宽流量
    v2_prime = Q / h2_prime  # 共轭水深处流速
    v3 = Q / h3  # 下游流速
    
    Fr2_prime = froude_number(v2_prime, h2_prime, g)
    Fr3 = froude_number(v3, h3, g)
    
    sigma = h3 / h2_prime  # 淹没度
    Lj_free = jump_length(h1, h2_prime)
    Lj_submerged = Lj_free * 1.2  # 淹没水跃长度略增
    
    delta_E, delta_E_free, eff_ratio = energy_loss_submerged_jump(h1, h2_prime, h3, v1, g)
    
    # 子图1：水跃纵剖面对比
    ax1 = axes[0, 0]
    
    # 自由水跃
    x_free = np.array([0, 0, Lj_free*0.2, Lj_free*0.5, Lj_free*0.8, Lj_free, Lj_free*1.5])
    h_free = np.array([h1, h1, h1*1.3, h2_prime*0.7, h2_prime*0.9, h2_prime, h2_prime])
    
    # 淹没水跃
    x_sub = np.array([0, 0, Lj_submerged*0.2, Lj_submerged*0.5, Lj_submerged*0.8, Lj_submerged, Lj_submerged*1.5])
    h_sub = np.array([h1, h1, h1*1.2, h2_prime*0.8, h3*0.95, h3, h3])
    
    ax1.plot(x_free, h_free, 'b-', linewidth=2.5, label=f'自由水跃（h₂\'={h2_prime:.2f}m）')
    ax1.plot(x_sub, h_sub, 'r-', linewidth=2.5, label=f'淹没水跃（h₃={h3:.2f}m）')
    
    ax1.axhline(h1, color='g', linestyle='--', linewidth=1, alpha=0.5)
    ax1.axhline(h2_prime, color='b', linestyle='--', linewidth=1, alpha=0.5)
    ax1.axhline(h3, color='r', linestyle='--', linewidth=1, alpha=0.5)
    
    ax1.fill_between(x_free, 0, h_free, alpha=0.2, color='blue')
    ax1.fill_between(x_sub, 0, h_sub, alpha=0.2, color='red')
    
    ax1.text(Lj_free/2, h2_prime*1.15, f'Lj={Lj_free:.1f}m', ha='center', fontsize=9,
             bbox=dict(boxstyle='round', facecolor='cyan', alpha=0.5))
    ax1.text(0, h1*0.5, f'h₁={h1:.2f}m\nFr₁={Fr1:.2f}', fontsize=9,
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    ax1.set_xlabel('距离 x (m)', fontsize=12)
    ax1.set_ylabel('水深 h (m)', fontsize=12)
    ax1.set_title('自由水跃vs淹没水跃纵剖面', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10, loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, Lj_submerged*1.6])
    
    # 子图2：淹没度影响曲线
    ax2 = axes[0, 1]
    
    sigma_range = np.linspace(1.0, 1.5, 100)
    eff_range = []
    delta_E_range = []
    
    for sig in sigma_range:
        h3_temp = sig * h2_prime
        dE, dE_free, eff = energy_loss_submerged_jump(h1, h2_prime, h3_temp, v1, g)
        eff_range.append(eff * 100)
        delta_E_range.append(dE)
    
    ax2_twin = ax2.twinx()
    
    line1 = ax2.plot(sigma_range, eff_range, 'b-', linewidth=2.5, label='消能效率')
    ax2.axvline(sigma, color='r', linestyle='--', linewidth=1.5, 
                label=f'设计工况 σ={sigma:.2f}')
    ax2.axhline(eff_ratio*100, color='r', linestyle='--', linewidth=1, alpha=0.5)
    ax2.plot(sigma, eff_ratio*100, 'ro', markersize=10)
    
    line2 = ax2_twin.plot(sigma_range, delta_E_range, 'g-', linewidth=2, label='能量损失')
    
    ax2.set_xlabel('淹没度 σ = h₃/h₂\'', fontsize=12)
    ax2.set_ylabel('消能效率（%）', fontsize=12, color='b')
    ax2.tick_params(axis='y', labelcolor='b')
    ax2_twin.set_ylabel('能量损失 ΔE (m)', fontsize=12, color='g')
    ax2_twin.tick_params(axis='y', labelcolor='g')
    
    ax2.set_title('淹没度对消能效率的影响', fontsize=14, fontweight='bold')
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, fontsize=10, loc='lower left')
    ax2.grid(True, alpha=0.3)
    
    # 子图3：水跃类型与Fr关系
    ax3 = axes[1, 0]
    
    Fr_array = np.linspace(1, 12, 200)
    h1_const = h1
    h2_array = conjugate_depth(h1_const, Fr_array)
    delta_E_array = energy_loss_free_jump(h1_const, h2_array)
    
    ax3.plot(Fr_array, h2_array/h1_const, 'b-', linewidth=2.5, label='h₂\'/h₁')
    ax3.axvline(Fr1, color='r', linestyle='--', linewidth=1.5, label=f'设计Fr₁={Fr1:.2f}')
    ax3.axhline(h2_prime/h1, color='r', linestyle='--', linewidth=1, alpha=0.5)
    ax3.plot(Fr1, h2_prime/h1, 'ro', markersize=10)
    
    # 标注水跃类型分区
    ax3.axvspan(1, 1.7, alpha=0.1, color='yellow', label='波状')
    ax3.axvspan(1.7, 2.5, alpha=0.1, color='orange', label='弱跃')
    ax3.axvspan(2.5, 4.5, alpha=0.1, color='pink', label='摆动')
    ax3.axvspan(4.5, 9.0, alpha=0.1, color='lightblue', label='稳定')
    ax3.axvspan(9.0, 12, alpha=0.1, color='lightgreen', label='强跃')
    
    ax3.set_xlabel('跃前弗劳德数 Fr₁', fontsize=12)
    ax3.set_ylabel('水深比 h₂\'/h₁', fontsize=12)
    ax3.set_title('水跃类型分类', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=9, loc='upper left', ncol=2)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim([1, 12])
    
    # 子图4：参数表
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    E1 = h1 + v1**2/(2*g)
    E2_prime = h2_prime + v2_prime**2/(2*g)
    E3 = h3 + v3**2/(2*g)
    
    jump_type = jump_type_classification(Fr1)
    
    info_text = f"""
    【淹没水跃计算结果】
    
    跃前断面：
      水深 h₁ = {h1:.3f} m
      流速 v₁ = {v1:.3f} m/s
      Fr₁ = {Fr1:.3f}（{jump_type}）
      比能 E₁ = {E1:.3f} m
    
    共轭水深（理论）：
      h₂' = {h2_prime:.3f} m
      v₂' = {v2_prime:.3f} m/s
      Fr₂' = {Fr2_prime:.3f}
      E₂' = {E2_prime:.3f} m
    
    实际下游（淹没）：
      h₃ = {h3:.3f} m
      v₃ = {v3:.3f} m/s
      Fr₃ = {Fr3:.3f}
      E₃ = {E3:.3f} m
    
    淹没参数：
      淹没度 σ = h₃/h₂' = {sigma:.3f}
      判别：σ > 1 → 淹没水跃 ✓
      淹没高度 Δh_s = {h3 - h2_prime:.3f} m
    
    能量损失：
      自由水跃 ΔE_free = {delta_E_free:.3f} m
      淹没水跃 ΔE_sub = {delta_E:.3f} m
      消能效率 η = {eff_ratio*100:.1f}%
      效率降低 Δη = {(1-eff_ratio)*100:.1f}%
    
    工程措施：
      • 降低下游水深（开挖）
      • 加高池深（强制水跃）
      • 增加消力墩（辅助消能）
      • 加长消能池
    """
    
    ax4.text(0.05, 0.95, info_text, transform=ax4.transAxes,
             fontsize=9.5, verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\n图片已保存：{filename}")
    plt.close()


def main():
    """
    主程序：第四章题69 - 淹没水跃分析
    """
    print("="*70)
    print("第四章题69 - 淹没水跃计算与分析")
    print("="*70)
    
    # 题目数据
    h1 = 0.5        # 跃前水深 (m)
    v1 = 8.0        # 跃前流速 (m/s)
    h3 = 3.2        # 下游实际水深 (m)
    g = 9.81        # 重力加速度 (m/s²)
    
    print(f"\n【题目】")
    print(f"跃前水深h₁={h1}m，流速v₁={v1}m/s")
    print(f"下游实际水深h₃={h3}m")
    print(f"判断水跃类型并分析消能效果")
    
    # 计算Fr₁
    Fr1 = froude_number(v1, h1, g)
    print(f"\n跃前弗劳德数：Fr₁ = {Fr1:.3f}")
    print(f"水跃类型：{jump_type_classification(Fr1)}")
    
    # 计算共轭水深
    h2_prime = conjugate_depth(h1, Fr1)
    print(f"\n共轭水深：h₂' = {h2_prime:.3f} m")
    
    # 判断淹没
    sigma = h3 / h2_prime
    print(f"淹没度：σ = h₃/h₂' = {sigma:.3f}")
    
    if sigma > 1.05:
        print(f"判断：σ > 1.05 → 淹没水跃 ⚠")
    elif sigma > 1.00:
        print(f"判断：1 < σ < 1.05 → 临界淹没")
    else:
        print(f"判断：σ ≤ 1 → 自由水跃 ✓")
    
    # 能量损失
    delta_E, delta_E_free, eff_ratio = energy_loss_submerged_jump(h1, h2_prime, h3, v1, g)
    
    print(f"\n【能量分析】")
    print(f"自由水跃能量损失：ΔE_free = {delta_E_free:.3f} m")
    print(f"淹没水跃能量损失：ΔE_sub = {delta_E:.3f} m")
    print(f"消能效率：η = {eff_ratio*100:.1f}%")
    print(f"效率降低：Δη = {(1-eff_ratio)*100:.1f}%")
    
    # 工程建议
    print(f"\n【工程措施】")
    print(f"1. 降低下游水深：需要降低Δh = {h3 - h2_prime:.2f} m")
    print(f"2. 或加深消能池：深度至少增加 {(h3 - h2_prime)*0.8:.2f} m")
    print(f"3. 增设辅助消能设施：消力墩、尾坎等")
    
    # 绘图
    plot_submerged_jump_analysis(h1, v1, h2_prime, h3, Fr1)
    
    print("\n" + "="*70)
    print("淹没水跃分析完成！")
    print("="*70)


def exercise():
    """练习题"""
    print("\n" + "="*70)
    print("【练习题】")
    print("="*70)
    
    print("""
    1. 如果下游水深降低到h₃=2.8m，水跃是否仍然淹没？
    2. 淹没度σ=1.1和σ=1.3时，消能效率相差多少？
    3. 如何设计消能池避免淹没水跃？
    4. 淹没水跃对下游渠道有什么不利影响？
    
    提示：
    - 淹没水跃：σ > 1.05
    - 消能效率随σ增大而降低
    - 池深设计：D = h₂' + 0.5m
    - 不利影响：消能不足、冲刷破坏
    """)


if __name__ == "__main__":
    main()
    exercise()
