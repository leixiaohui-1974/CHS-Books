#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复式断面渠道均匀流计算
======================

题目：河海大学2017年真题改编（第64题）
某河道复式断面：
- 主槽：底宽b₁=10m，水深h₁=3m，糙率n₁=0.025
- 滩地：宽度b₂=15m（单侧），水深h₂=1.5m，糙率n₂=0.035
- 底坡：i=0.0002

求解：
1. 总流量Q
2. 主槽流量Q₁和滩地流量Q₂
3. 断面平均流速v
4. 洪水位抬高0.5m后的流量变化

作者：CHS-Books
日期：2025-10-31
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Rectangle, Polygon

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


def manning_Q_subsection(A, chi, n, i):
    """
    子区域曼宁公式计算流量
    
    参数：
        A: 过流面积 (m²)
        chi: 湿周 (m)
        n: 糙率系数
        i: 底坡
    
    返回：
        Q: 流量 (m³/s)
        R: 水力半径 (m)
    """
    R = A / chi if chi > 0 else 0
    Q = (A / n) * (R ** (2/3)) * (i ** 0.5)
    return Q, R


def compound_channel_flow(b1, h1, n1, b2, h2, n2, i):
    """
    复式断面流量计算（分区法）
    
    断面结构：
    |<---b2--->|<---b1--->|<---b2--->|
    └─┐       ┌─────────┐       ┌─┘  ← 滩地（左右对称）
      └───────┘         └───────┘    ← 主槽
    
    参数：
        b1: 主槽底宽 (m)
        h1: 主槽水深 (m)
        n1: 主槽糙率
        b2: 单侧滩地宽度 (m)
        h2: 滩地水深（超出主槽的深度） (m)
        n2: 滩地糙率
        i: 底坡
    
    返回：
        Q_total: 总流量 (m³/s)
        Q1: 主槽流量 (m³/s)
        Q2: 滩地流量 (m³/s)，两侧总和
        results: 详细计算结果字典
    """
    # 主槽（矩形，简化）
    A1 = b1 * h1
    chi1 = b1 + 2 * h1  # 湿周：底+两侧壁
    Q1, R1 = manning_Q_subsection(A1, chi1, n1, i)
    
    # 滩地（两侧，矩形）
    A2_single = b2 * h2  # 单侧面积
    A2 = 2 * A2_single   # 总面积
    chi2_single = b2 + h2  # 单侧湿周：滩地表面+外侧壁（不包括与主槽的交界）
    chi2 = 2 * chi2_single
    Q2, R2 = manning_Q_subsection(A2, chi2, n2, i)
    
    # 总流量
    Q_total = Q1 + Q2
    
    # 总面积和平均流速
    A_total = A1 + A2
    v_avg = Q_total / A_total
    
    # 各区流速
    v1 = Q1 / A1 if A1 > 0 else 0
    v2 = Q2 / A2 if A2 > 0 else 0
    
    results = {
        'main': {'A': A1, 'chi': chi1, 'R': R1, 'Q': Q1, 'v': v1},
        'floodplain': {'A': A2, 'chi': chi2, 'R': R2, 'Q': Q2, 'v': v2},
        'total': {'A': A_total, 'Q': Q_total, 'v': v_avg}
    }
    
    return Q_total, Q1, Q2, results


def plot_compound_section(b1, h1, b2, h2, title='复式断面'):
    """
    绘制复式断面形状
    
    参数：
        b1: 主槽底宽 (m)
        h1: 主槽水深 (m)
        b2: 单侧滩地宽度 (m)
        h2: 滩地水深 (m)
        title: 图标题
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 主槽高程（底部为0）
    main_bottom = 0
    main_top = h1
    
    # 滩地高程
    flood_bottom = h1 - h2
    flood_top = h1
    
    # 绘制主槽
    main_channel = Rectangle((0, main_bottom), b1, h1, 
                              fill=True, facecolor='lightblue', 
                              edgecolor='black', linewidth=2, label='主槽水体')
    ax.add_patch(main_channel)
    
    # 绘制左侧滩地
    left_flood = Rectangle((-b2, flood_bottom), b2, h2,
                            fill=True, facecolor='lightgreen',
                            edgecolor='black', linewidth=2, label='滩地水体')
    ax.add_patch(left_flood)
    
    # 绘制右侧滩地
    right_flood = Rectangle((b1, flood_bottom), b2, h2,
                             fill=True, facecolor='lightgreen',
                             edgecolor='black', linewidth=2)
    ax.add_patch(right_flood)
    
    # 绘制滩地"地面"
    ax.plot([-b2, 0], [flood_bottom, flood_bottom], 'k-', linewidth=2)
    ax.plot([b1, b1+b2], [flood_bottom, flood_bottom], 'k-', linewidth=2)
    
    # 标注尺寸
    # 主槽底宽
    ax.annotate('', xy=(0, -0.3), xytext=(b1, -0.3),
                arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    ax.text(b1/2, -0.6, f'b₁={b1}m', ha='center', fontsize=11, color='red')
    
    # 滩地宽度（左）
    ax.annotate('', xy=(-b2, flood_bottom-0.5), xytext=(0, flood_bottom-0.5),
                arrowprops=dict(arrowstyle='<->', color='green', lw=1.5))
    ax.text(-b2/2, flood_bottom-0.8, f'b₂={b2}m', ha='center', fontsize=11, color='green')
    
    # 主槽水深
    ax.annotate('', xy=(-0.5, 0), xytext=(-0.5, h1),
                arrowprops=dict(arrowstyle='<->', color='blue', lw=1.5))
    ax.text(-1.2, h1/2, f'h₁={h1}m', ha='center', fontsize=11, color='blue', rotation=90)
    
    # 滩地水深
    ax.annotate('', xy=(b1+b2+0.5, flood_bottom), xytext=(b1+b2+0.5, flood_top),
                arrowprops=dict(arrowstyle='<->', color='green', lw=1.5))
    ax.text(b1+b2+1.2, (flood_bottom+flood_top)/2, f'h₂={h2}m', 
            ha='center', fontsize=11, color='green', rotation=90)
    
    # 水面线
    ax.plot([-b2, b1+b2], [h1, h1], 'b--', linewidth=2, label='水面线')
    
    ax.set_xlim(-b2-2, b1+b2+2)
    ax.set_ylim(-2, h1+1)
    ax.set_xlabel('横向距离 (m)', fontsize=12)
    ax.set_ylabel('高程 (m)', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    return fig


def main():
    """主函数：求解强化题64"""
    
    print("=" * 70)
    print("复式断面渠道均匀流计算")
    print("题目：河海大学2017年真题改编（第64题）")
    print("=" * 70)
    
    # ========== 已知条件 ==========
    b1 = 10.0        # 主槽底宽 (m)
    h1 = 3.0         # 主槽水深 (m)
    n1 = 0.025       # 主槽糙率
    b2 = 15.0        # 单侧滩地宽度 (m)
    h2 = 1.5         # 滩地水深（超出主槽） (m)
    n2 = 0.035       # 滩地糙率
    i = 0.0002       # 底坡
    
    print("\n【已知条件】")
    print(f"主槽：底宽b₁={b1}m，水深h₁={h1}m，糙率n₁={n1}")
    print(f"滩地：宽度b₂={b2}m（单侧），水深h₂={h2}m，糙率n₂={n2}")
    print(f"底坡：i={i}")
    
    # ========== (1) 计算总流量Q ==========
    print("\n" + "=" * 70)
    print("(1) 计算总流量Q")
    print("=" * 70)
    
    Q_total, Q1, Q2, results = compound_channel_flow(b1, h1, n1, b2, h2, n2, i)
    
    print(f"\n【主槽】")
    print(f"  过流面积：A₁ = {results['main']['A']:.2f} m²")
    print(f"  湿周：χ₁ = {results['main']['chi']:.2f} m")
    print(f"  水力半径：R₁ = {results['main']['R']:.3f} m")
    print(f"  流量：Q₁ = {results['main']['Q']:.2f} m³/s")
    print(f"  流速：v₁ = {results['main']['v']:.3f} m/s")
    
    print(f"\n【滩地（两侧）】")
    print(f"  过流面积：A₂ = {results['floodplain']['A']:.2f} m²")
    print(f"  湿周：χ₂ = {results['floodplain']['chi']:.2f} m")
    print(f"  水力半径：R₂ = {results['floodplain']['R']:.3f} m")
    print(f"  流量：Q₂ = {results['floodplain']['Q']:.2f} m³/s")
    print(f"  流速：v₂ = {results['floodplain']['v']:.3f} m/s")
    
    print(f"\n【总计】")
    print(f"  总面积：A = {results['total']['A']:.2f} m²")
    print(f"  总流量：Q = {results['total']['Q']:.2f} m³/s")
    print(f"  平均流速：v = {results['total']['v']:.3f} m/s")
    
    print(f"\n流量分配：")
    print(f"  主槽占比：Q₁/Q = {Q1/Q_total*100:.1f}%")
    print(f"  滩地占比：Q₂/Q = {Q2/Q_total*100:.1f}%")
    
    print(f"\n分析：")
    print(f"  主槽流速v₁={results['main']['v']:.3f} m/s > 滩地流速v₂={results['floodplain']['v']:.3f} m/s")
    print(f"  原因：主槽糙率n₁={n1} < 滩地糙率n₂={n2}（滩地有植被）")
    
    # ========== (2) 洪水位抬高0.5m ==========
    print("\n" + "=" * 70)
    print("(2) 洪水位抬高0.5m后的流量变化")
    print("=" * 70)
    
    # 新水深
    h1_new = h1 + 0.5
    h2_new = h2 + 0.5
    
    Q_total_new, Q1_new, Q2_new, results_new = compound_channel_flow(
        b1, h1_new, n1, b2, h2_new, n2, i)
    
    print(f"\n新水深：")
    print(f"  主槽：h₁' = {h1_new} m")
    print(f"  滩地：h₂' = {h2_new} m")
    
    print(f"\n新流量：")
    print(f"  主槽：Q₁' = {Q1_new:.2f} m³/s（原{Q1:.2f} m³/s）")
    print(f"  滩地：Q₂' = {Q2_new:.2f} m³/s（原{Q2:.2f} m³/s）")
    print(f"  总计：Q' = {Q_total_new:.2f} m³/s（原{Q_total:.2f} m³/s）")
    
    Delta_Q = Q_total_new - Q_total
    Delta_Q1 = Q1_new - Q1
    Delta_Q2 = Q2_new - Q2
    
    print(f"\n流量增量：")
    print(f"  主槽：ΔQ₁ = {Delta_Q1:.2f} m³/s（增幅{Delta_Q1/Q1*100:.1f}%）")
    print(f"  滩地：ΔQ₂ = {Delta_Q2:.2f} m³/s（增幅{Delta_Q2/Q2*100:.1f}%）")
    print(f"  总计：ΔQ = {Delta_Q:.2f} m³/s（增幅{Delta_Q/Q_total*100:.1f}%）")
    
    print(f"\n结论：")
    print(f"  水位抬高{0.5}m（{0.5/h1*100:.1f}%），流量增加{Delta_Q:.2f} m³/s（{Delta_Q/Q_total*100:.1f}%）")
    print(f"  滩地增幅（{Delta_Q2/Q2*100:.1f}%）大于主槽增幅（{Delta_Q1/Q1*100:.1f}%）")
    
    # ========== 绘图 ==========
    print("\n" + "=" * 70)
    print("绘制图形")
    print("=" * 70)
    
    fig = plt.figure(figsize=(16, 10))
    
    # 子图1：原始水位断面
    ax1 = fig.add_subplot(221)
    plot_compound_section_axes(ax1, b1, h1, b2, h2, f'原始水位（h₁={h1}m）')
    
    # 子图2：洪水位断面
    ax2 = fig.add_subplot(222)
    plot_compound_section_axes(ax2, b1, h1_new, b2, h2_new, f'洪水位（h₁={h1_new}m）')
    
    # 子图3：流量对比
    ax3 = fig.add_subplot(223)
    
    categories = ['主槽', '滩地', '总计']
    Q_original = [Q1, Q2, Q_total]
    Q_flood = [Q1_new, Q2_new, Q_total_new]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax3.bar(x - width/2, Q_original, width, label='原始水位', color='skyblue')
    bars2 = ax3.bar(x + width/2, Q_flood, width, label='洪水位', color='salmon')
    
    ax3.set_xlabel('区域', fontsize=11)
    ax3.set_ylabel('流量 Q (m³/s)', fontsize=11)
    ax3.set_title('流量对比', fontsize=13)
    ax3.set_xticks(x)
    ax3.set_xticklabels(categories)
    ax3.legend(fontsize=10)
    ax3.grid(True, axis='y', alpha=0.3)
    
    # 标注数值
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=9)
    
    # 子图4：水深-流量曲线
    ax4 = fig.add_subplot(224)
    
    h1_range = np.linspace(1.0, 5.0, 50)
    Q_range = []
    Q1_range = []
    Q2_range = []
    
    for h in h1_range:
        h2_temp = max(0, h - (h1 - h2))  # 保持滩地高程不变
        if h <= (h1 - h2):
            # 未漫滩
            Q_temp, Q1_temp, Q2_temp, _ = compound_channel_flow(b1, h, n1, b2, 0, n2, i)
        else:
            # 已漫滩
            Q_temp, Q1_temp, Q2_temp, _ = compound_channel_flow(b1, h, n1, b2, h2_temp, n2, i)
        
        Q_range.append(Q_temp)
        Q1_range.append(Q1_temp)
        Q2_range.append(Q2_temp)
    
    ax4.plot(h1_range, Q_range, 'b-', linewidth=2, label='总流量Q')
    ax4.plot(h1_range, Q1_range, 'g--', linewidth=1.5, label='主槽Q₁')
    ax4.plot(h1_range, Q2_range, 'r--', linewidth=1.5, label='滩地Q₂')
    
    # 标注设计点
    ax4.plot(h1, Q_total, 'bo', markersize=10, label=f'原始：h={h1}m')
    ax4.plot(h1_new, Q_total_new, 'ro', markersize=10, label=f'洪水：h={h1_new}m')
    
    ax4.axvline(x=(h1-h2), color='gray', linestyle=':', alpha=0.5, label='漫滩水位')
    
    ax4.set_xlabel('主槽水深 h₁ (m)', fontsize=11)
    ax4.set_ylabel('流量 Q (m³/s)', fontsize=11)
    ax4.set_title('水深-流量关系', fontsize=13)
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图片
    output_file = 'uniform_flow_compound.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n图片已保存：{output_file}")
    
    plt.show()
    
    # ========== 总结 ==========
    print("\n" + "=" * 70)
    print("【总结】")
    print("=" * 70)
    print(f"1. 原始水位：Q={Q_total:.1f} m³/s（主槽{Q1:.1f}+滩地{Q2:.1f}）")
    print(f"2. 洪水位：  Q'={Q_total_new:.1f} m³/s（主槽{Q1_new:.1f}+滩地{Q2_new:.1f}）")
    print(f"3. 流量增加：ΔQ={Delta_Q:.1f} m³/s（增幅{Delta_Q/Q_total*100:.1f}%）")
    print(f"4. 主槽流速（{results['main']['v']:.2f} m/s）> 滩地流速（{results['floodplain']['v']:.2f} m/s）")
    print(f"5. 复式断面必须分区计算，不能用单一糙率！")
    print("=" * 70)


def plot_compound_section_axes(ax, b1, h1, b2, h2, title):
    """在指定axes上绘制复式断面"""
    # 主槽
    main_bottom = 0
    main_top = h1
    flood_bottom = h1 - h2
    flood_top = h1
    
    # 绘制
    main_channel = Rectangle((0, main_bottom), b1, h1, 
                              fill=True, facecolor='lightblue', 
                              edgecolor='black', linewidth=2)
    ax.add_patch(main_channel)
    
    if h2 > 0:
        left_flood = Rectangle((-b2, flood_bottom), b2, h2,
                                fill=True, facecolor='lightgreen',
                                edgecolor='black', linewidth=2)
        ax.add_patch(left_flood)
        
        right_flood = Rectangle((b1, flood_bottom), b2, h2,
                                 fill=True, facecolor='lightgreen',
                                 edgecolor='black', linewidth=2)
        ax.add_patch(right_flood)
        
        ax.plot([-b2, 0], [flood_bottom, flood_bottom], 'k-', linewidth=2)
        ax.plot([b1, b1+b2], [flood_bottom, flood_bottom], 'k-', linewidth=2)
    
    # 水面线
    ax.plot([-b2, b1+b2], [h1, h1], 'b--', linewidth=2)
    
    ax.set_xlim(-b2-1, b1+b2+1)
    ax.set_ylim(-0.5, h1+0.5)
    ax.set_xlabel('横向距离 (m)', fontsize=10)
    ax.set_ylabel('高程 (m)', fontsize=10)
    ax.set_title(title, fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')


def exercise():
    """练习题"""
    print("\n" + "=" * 70)
    print("【练习题】")
    print("=" * 70)
    print("\n1. 若滩地糙率n₂增加到0.050（高草），流量Q如何变化？")
    print("2. 若水深h₁减小到2m（枯水期，未漫滩），流量Q是多少？")
    print("3. 为什么主槽与滩地交界处不计入湿周？")
    print("   提示：交界面两侧都是水，不产生摩阻")
    print("4. 复式断面为何比矩形断面更生态？")
    print("=" * 70)


if __name__ == "__main__":
    main()
    exercise()
