"""
第10章 水资源评价
题目2：水资源承载力分析

知识点：
- 水资源承载力概念
- 人口承载力
- 经济承载力
- 承载指数
- 承载潜力分析
- 承载状态评价
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 2020年现状数据
W_resource = 5.0e8     # m³，水资源总量
W_available = 3.0e8    # m³，可利用水量
W_transfer = 1.0e8     # m³，外调水量
W_eco = 0.5e8          # m³，生态需水

P0 = 100               # 万人，人口
q_capita = 250         # m³/(人·年)，人均用水定额
W_use = 2.5e8          # m³，用水总量

G0 = 800               # 亿元，GDP
q_gdp = 31.25          # m³/万元，万元GDP用水量

# 2030年规划数据
q_capita_2030 = 200    # m³/(人·年)
q_gdp_2030 = 20        # m³/万元
r_gdp = 0.06           # GDP年增长率
years = 10             # 年数
W_eco_2030 = 0.8e8     # m³，生态需水

print("="*70)
print("题目2：水资源承载力分析")
print("="*70)

print(f"\n【2020年现状数据】")
print(f"\n水资源条件：")
print(f"  水资源总量 = {W_resource/1e8:.1f}×10⁸ m³")
print(f"  可利用水量 = {W_available/1e8:.1f}×10⁸ m³")
print(f"  外调水量 = {W_transfer/1e8:.1f}×10⁸ m³")
print(f"  生态需水 = {W_eco/1e8:.1f}×10⁸ m³")

print(f"\n社会经济条件：")
print(f"  人口 = {P0} 万人")
print(f"  人均用水定额 = {q_capita} m³/(人·年)")
print(f"  用水总量 = {W_use/1e8:.1f}×10⁸ m³")
print(f"  GDP = {G0} 亿元")
print(f"  万元GDP用水量 = {q_gdp} m³/万元")

print(f"\n【2030年规划目标】")
print(f"  人均用水定额 = {q_capita_2030} m³/(人·年)")
print(f"  万元GDP用水量 = {q_gdp_2030} m³/万元")
print(f"  GDP年增长率 = {r_gdp*100}%")
print(f"  生态需水 = {W_eco_2030/1e8:.1f}×10⁸ m³")

# ========== 2020年承载力分析 ==========
print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("2020年水资源承载力分析")
print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# 可用水量
W_usable = W_available + W_transfer - W_eco
print(f"\n可用水量：")
print(f"  W_usable = W_available + W_transfer - W_eco")
print(f"  W_usable = {W_available/1e8:.1f} + {W_transfer/1e8:.1f} - {W_eco/1e8:.1f}")
print(f"  W_usable = {W_usable/1e8:.1f}×10⁸ m³")

# 人口承载力
P_capacity = W_usable / (q_capita * 1e4)
I_pop = P0 / P_capacity
pop_potential = P_capacity - P0
pop_potential_rate = pop_potential / P0 * 100

print(f"\n人口承载力：")
print(f"  P_capacity = W_usable / q_capita")
print(f"  P_capacity = {W_usable/1e8:.1f}×10⁸ / {q_capita}")
print(f"  P_capacity = {P_capacity:.0f} 万人")
print(f"\n  承载指数 I_pop = P0 / P_capacity = {I_pop:.3f}")
if I_pop < 0.6:
    pop_status = "未超载"
elif I_pop < 0.8:
    pop_status = "轻度超载"
elif I_pop < 1.0:
    pop_status = "中度超载"
else:
    pop_status = "严重超载"
print(f"  评价：{pop_status}")
print(f"\n  承载潜力 = {pop_potential:.0f} 万人")
print(f"  潜力率 = {pop_potential_rate:.1f}%")

# 经济承载力
G_capacity = W_usable / q_gdp * 1e4
I_gdp = G0 / G_capacity
gdp_potential = G_capacity - G0
gdp_potential_rate = gdp_potential / G0 * 100

print(f"\n经济承载力：")
print(f"  G_capacity = W_usable / q_gdp × 10⁴")
print(f"  G_capacity = {W_usable/1e8:.1f}×10⁸ / {q_gdp} × 10⁴")
print(f"  G_capacity = {G_capacity:.0f} 亿元")
print(f"\n  承载指数 I_gdp = G0 / G_capacity = {I_gdp:.3f}")
if I_gdp < 0.6:
    gdp_status = "未超载"
elif I_gdp < 0.8:
    gdp_status = "轻度超载"
elif I_gdp < 1.0:
    gdp_status = "中度超载"
else:
    gdp_status = "严重超载"
print(f"  评价：{gdp_status}")
print(f"\n  承载潜力 = {gdp_potential:.0f} 亿元")
print(f"  潜力率 = {gdp_potential_rate:.1f}%")

# 验证
W_use_check = P0 * 1e4 * q_capita
print(f"\n验证（用水总量）：")
print(f"  W_use = P0 × q_capita = {P0} × {q_capita} = {W_use_check/1e8:.1f}×10⁸ m³ ✓")

# ========== 2030年承载力预测 ==========
print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("2030年水资源承载力预测")
print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# GDP预测
G_2030 = G0 * (1 + r_gdp)**years
print(f"\nGDP预测：")
print(f"  G_2030 = G0 × (1 + r)^t")
print(f"  G_2030 = {G0} × (1 + {r_gdp})^{years}")
print(f"  G_2030 = {G_2030:.1f} 亿元")
print(f"  增长率 = {(G_2030/G0 - 1)*100:.1f}%")

# 可用水量
W_usable_2030 = W_available + W_transfer - W_eco_2030
print(f"\n可用水量：")
print(f"  W_usable = {W_available/1e8:.1f} + {W_transfer/1e8:.1f} - {W_eco_2030/1e8:.1f}")
print(f"  W_usable = {W_usable_2030/1e8:.1f}×10⁸ m³")
print(f"  变化 = {(W_usable_2030 - W_usable)/W_usable*100:+.1f}%（生态需水增加）")

# 人口承载力
P_capacity_2030 = W_usable_2030 / (q_capita_2030 * 1e4)
print(f"\n人口承载力：")
print(f"  P_capacity = {W_usable_2030/1e8:.1f}×10⁸ / {q_capita_2030}")
print(f"  P_capacity = {P_capacity_2030:.0f} 万人")
print(f"  与2020年对比：{(P_capacity_2030 - P_capacity):.0f} 万人 ({(P_capacity_2030/P_capacity-1)*100:+.1f}%)")
print(f"  原因：人均用水定额下降（节水成效）")

# 经济承载力
G_capacity_2030 = W_usable_2030 / q_gdp_2030 * 1e4
I_gdp_2030 = G_2030 / G_capacity_2030

print(f"\n经济承载力：")
print(f"  G_capacity = {W_usable_2030/1e8:.1f}×10⁸ / {q_gdp_2030} × 10⁴")
print(f"  G_capacity = {G_capacity_2030:.0f} 亿元")
print(f"  与2020年对比：{(G_capacity_2030 - G_capacity):.0f} 亿元 ({(G_capacity_2030/G_capacity-1)*100:+.1f}%)")
print(f"\n  承载指数 I_gdp = {G_2030:.1f} / {G_capacity_2030:.0f} = {I_gdp_2030:.3f}")
if I_gdp_2030 < 0.6:
    gdp_status_2030 = "未超载"
elif I_gdp_2030 < 0.8:
    gdp_status_2030 = "轻度超载"
elif I_gdp_2030 < 1.0:
    gdp_status_2030 = "中度超载"
else:
    gdp_status_2030 = "严重超载"
print(f"  评价：{gdp_status_2030}")
print(f"  与2020年对比：从{I_gdp:.3f}({gdp_status})到{I_gdp_2030:.3f}({gdp_status_2030})")
print(f"  ⚠️  承载压力增大！")

print("="*70)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

# 子图1：2020年vs2030年承载力对比
ax1 = fig.add_subplot(gs[0, :2])
years_list = ['2020年', '2030年']
pop_cap = [P_capacity, P_capacity_2030]
gdp_cap = [G_capacity/100, G_capacity_2030/100]  # 转换为百亿元

x = np.arange(len(years_list))
width = 0.35

bars1 = ax1.bar(x - width/2, pop_cap, width, label='人口承载力(万人)', color='blue', alpha=0.7)
ax1_twin = ax1.twinx()
bars2 = ax1_twin.bar(x + width/2, gdp_cap, width, label='经济承载力(百亿元)', color='green', alpha=0.7)

# 标注数值
for bar, val in zip(bars1, pop_cap):
    ax1.text(bar.get_x() + bar.get_width()/2, val + 2,
             f'{val:.0f}', ha='center', fontsize=10, fontweight='bold')
for bar, val in zip(bars2, gdp_cap):
    ax1_twin.text(bar.get_x() + bar.get_width()/2, val + 0.2,
                  f'{val:.0f}', ha='center', fontsize=10, fontweight='bold')

ax1.set_ylabel('人口承载力 (万人)', fontsize=11, fontweight='bold', color='blue')
ax1_twin.set_ylabel('经济承载力 (百亿元)', fontsize=11, fontweight='bold', color='green')
ax1.set_title('题目2-1：2020年vs2030年水资源承载力对比', fontsize=13, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(years_list)
ax1.legend(loc='upper left', fontsize=10)
ax1_twin.legend(loc='upper right', fontsize=10)
ax1.grid(True, alpha=0.3, axis='y')

# 子图2：承载指数对比
ax2 = fig.add_subplot(gs[0, 2])
indices = ['人口\n2020', '经济\n2020', '经济\n2030']
index_values = [I_pop, I_gdp, I_gdp_2030]
colors_idx = ['blue' if val < 0.8 else 'orange' if val < 1.0 else 'red' for val in index_values]

bars = ax2.bar(indices, index_values, color=colors_idx, alpha=0.7, edgecolor='black', linewidth=2)
for bar, val in zip(bars, index_values):
    ax2.text(bar.get_x() + bar.get_width()/2, val + 0.02,
             f'{val:.3f}', ha='center', fontsize=9, fontweight='bold')

# 阈值线
ax2.axhline(0.6, color='green', linestyle='--', linewidth=1.5, alpha=0.5, label='未超载(<0.6)')
ax2.axhline(0.8, color='orange', linestyle='--', linewidth=1.5, alpha=0.5, label='轻度超载(0.6-0.8)')
ax2.axhline(1.0, color='red', linestyle='--', linewidth=1.5, alpha=0.5, label='中度超载(0.8-1.0)')

ax2.set_ylabel('承载指数', fontsize=11, fontweight='bold')
ax2.set_title('题目2-2：承载指数评价', fontsize=11, fontweight='bold')
ax2.legend(fontsize=8, loc='upper left')
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_ylim(0, 1.2)

# 子图3：可用水量组成（2020年）
ax3 = fig.add_subplot(gs[1, 0])
components = ['可利用\n水量', '外调\n水量', '生态\n需水']
values_2020 = [W_available/1e8, W_transfer/1e8, -W_eco/1e8]
colors_comp = ['blue', 'green', 'red']

y_pos = np.arange(len(components))
for i, (comp, val, color) in enumerate(zip(components, values_2020, colors_comp)):
    if val > 0:
        ax3.barh(i, val, color=color, alpha=0.6, edgecolor='black')
        ax3.text(val/2, i, f'+{val:.1f}', ha='center', va='center', fontsize=10, fontweight='bold')
    else:
        ax3.barh(i, val, color=color, alpha=0.6, edgecolor='black')
        ax3.text(val/2, i, f'{val:.1f}', ha='center', va='center', fontsize=10, fontweight='bold')

# 可用水量结果
ax3.barh(len(components), W_usable/1e8, color='orange', alpha=0.7, edgecolor='black', linewidth=2)
ax3.text(W_usable/1e8/2, len(components), f'={W_usable/1e8:.1f}', ha='center', va='center', fontsize=11, fontweight='bold')

ax3.set_yticks(np.arange(len(components)+1))
ax3.set_yticklabels(components + ['可用\n水量'])
ax3.set_xlabel('水量 (×10⁸ m³)', fontsize=10, fontweight='bold')
ax3.set_title('题目2-3：2020年可用水量组成', fontsize=10, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='x')

# 子图4：可用水量组成（2030年）
ax4 = fig.add_subplot(gs[1, 1])
values_2030 = [W_available/1e8, W_transfer/1e8, -W_eco_2030/1e8]

for i, (comp, val, color) in enumerate(zip(components, values_2030, colors_comp)):
    if val > 0:
        ax4.barh(i, val, color=color, alpha=0.6, edgecolor='black')
        ax4.text(val/2, i, f'+{val:.1f}', ha='center', va='center', fontsize=10, fontweight='bold')
    else:
        ax4.barh(i, val, color=color, alpha=0.6, edgecolor='black')
        ax4.text(val/2, i, f'{val:.1f}', ha='center', va='center', fontsize=10, fontweight='bold')

ax4.barh(len(components), W_usable_2030/1e8, color='orange', alpha=0.7, edgecolor='black', linewidth=2)
ax4.text(W_usable_2030/1e8/2, len(components), f'={W_usable_2030/1e8:.1f}', ha='center', va='center', fontsize=11, fontweight='bold')

ax4.set_yticks(np.arange(len(components)+1))
ax4.set_yticklabels(components + ['可用\n水量'])
ax4.set_xlabel('水量 (×10⁸ m³)', fontsize=10, fontweight='bold')
ax4.set_title('题目2-4：2030年可用水量组成', fontsize=10, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='x')

# 子图5：承载力评价框架
ax5 = fig.add_subplot(gs[1, 2])
ax5.axis('off')
framework_text = f"""
承载力评价框架：

【承载力计算】
  人口承载力：
    P_cap = W_usable / q_capita
  
  经济承载力：
    G_cap = W_usable / q_gdp × 10⁴

【承载指数】
  I = 现状值 / 承载力
  
  评价标准：
    I < 0.6: 未超载
    0.6≤I<0.8: 轻度超载
    0.8≤I<1.0: 中度超载
    I ≥ 1.0: 严重超载

【承载潜力】
  潜力 = 承载力 - 现状值
  潜力率 = 潜力/现状值×100%
"""
ax5.text(0.05, 0.95, framework_text, transform=ax5.transAxes,
         fontsize=8.5, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

# 子图6：承载力变化趋势
ax6 = fig.add_subplot(gs[2, :])
years_trend = np.array([2020, 2030])

# 人口承载力
ax6.plot(years_trend, [P_capacity, P_capacity_2030], 'bo-', linewidth=3, markersize=10, label='人口承载力(万人)')
ax6.fill_between(years_trend, [P0, P0], [P_capacity, P_capacity_2030], alpha=0.2, color='blue', label='人口承载潜力')

# 经济承载力（使用右轴）
ax6_twin = ax6.twinx()
ax6_twin.plot(years_trend, [G_capacity/100, G_capacity_2030/100], 'gs-', linewidth=3, markersize=10, label='经济承载力(百亿元)')
ax6_twin.plot(years_trend, [G0/100, G_2030/100], 'r^--', linewidth=2, markersize=8, label='实际GDP(百亿元)')
ax6_twin.fill_between(years_trend, [G0/100, G_2030/100], [G_capacity/100, G_capacity_2030/100], 
                       alpha=0.2, color='green', label='经济承载潜力')

# 标注
ax6.text(2020, P_capacity+3, f'{P_capacity:.0f}', ha='center', fontsize=10, fontweight='bold')
ax6.text(2030, P_capacity_2030+3, f'{P_capacity_2030:.0f}', ha='center', fontsize=10, fontweight='bold')
ax6_twin.text(2020, G_capacity/100+0.3, f'{G_capacity/100:.0f}', ha='center', fontsize=10, fontweight='bold')
ax6_twin.text(2030, G_capacity_2030/100+0.3, f'{G_capacity_2030/100:.0f}', ha='center', fontsize=10, fontweight='bold')
ax6_twin.text(2030, G_2030/100-0.5, f'GDP={G_2030/100:.0f}', ha='center', fontsize=9, fontweight='bold', color='red')

ax6.set_xlabel('年份', fontsize=12, fontweight='bold')
ax6.set_ylabel('人口承载力 (万人)', fontsize=11, fontweight='bold', color='blue')
ax6_twin.set_ylabel('经济承载力/GDP (百亿元)', fontsize=11, fontweight='bold', color='green')
ax6.set_title('题目2-5：水资源承载力变化趋势（2020-2030）', fontsize=13, fontweight='bold')
ax6.legend(loc='upper left', fontsize=10)
ax6_twin.legend(loc='upper right', fontsize=10)
ax6.grid(True, alpha=0.3)
ax6.set_xlim(2018, 2032)

plt.savefig('题目2_承载力分析.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目2图形已生成：题目2_承载力分析.png")
plt.show()
