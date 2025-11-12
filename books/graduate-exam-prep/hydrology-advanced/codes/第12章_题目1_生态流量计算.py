"""
第12章 生态水文
题目1：生态流量计算（Tennant法）

知识点：
- 生态流量概念
- Tennant法（蒙大拿法）
- 分期计算
- 生态保护等级
- 满足率分析
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 河流数据
Q_avg = 500  # 多年平均流量（m³/s）
months = np.arange(1, 13)
month_names = ['1月', '2月', '3月', '4月', '5月', '6月', 
               '7月', '8月', '9月', '10月', '11月', '12月']

# 各月平均流量（m³/s）
Q_monthly = np.array([180, 150, 200, 350, 600, 900, 1200, 1000, 700, 400, 250, 200])

# Tennant法分级标准
# 丰水期（10-3月）：10,11,12,1,2,3
# 枯水期（4-9月）：4,5,6,7,8,9
# 保护等级：理想、优良、良好、最小

print("="*80)
print("题目1：生态流量计算（Tennant法）")
print("="*80)

print(f"\n河流特征：")
print(f"  多年平均流量 Q̄ = {Q_avg} m³/s")
print(f"  最小月平均流量 = {np.min(Q_monthly)} m³/s（{month_names[np.argmin(Q_monthly)]}）")
print(f"  最大月平均流量 = {np.max(Q_monthly)} m³/s（{month_names[np.argmax(Q_monthly)]}）")

print(f"\n各月平均流量：")
for i, (m, q) in enumerate(zip(month_names, Q_monthly)):
    print(f"  {m}: {q:4.0f} m³/s", end="")
    if (i + 1) % 4 == 0:
        print()
print()

# Tennant法计算不同保护等级的生态流量
levels = ['理想', '优良', '良好', '最小']
flood_season_pct = [0.60, 0.40, 0.30, 0.10]  # 丰水期系数
dry_season_pct = [0.60, 0.30, 0.20, 0.10]     # 枯水期系数

print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("Tennant法不同保护等级生态流量")
print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"{'保护等级':<10} {'丰水期系数':<12} {'丰水期Q(m³/s)':<15} {'枯水期系数':<12} {'枯水期Q(m³/s)':<15}")
print("-" * 80)

eco_flows = {}
for level, f_pct, d_pct in zip(levels, flood_season_pct, dry_season_pct):
    Q_flood = f_pct * Q_avg
    Q_dry = d_pct * Q_avg
    eco_flows[level] = {'flood': Q_flood, 'dry': Q_dry, 'f_pct': f_pct, 'd_pct': d_pct}
    print(f"{level:<10} {f_pct*100:<12.0f}% {Q_flood:<15.0f} {d_pct*100:<12.0f}% {Q_dry:<15.0f}")

# 推荐采用"优良"等级
selected_level = '优良'
print(f"\n推荐采用保护等级：{selected_level}")

# 各月生态流量计算
# 丰水期：10,11,12,1,2,3月
# 枯水期：4,5,6,7,8,9月
flood_months = [10, 11, 12, 1, 2, 3]
dry_months = [4, 5, 6, 7, 8, 9]

Q_eco = np.zeros(12)
for i in range(12):
    month = i + 1
    if month in flood_months:
        Q_eco[i] = eco_flows[selected_level]['flood']
    else:
        Q_eco[i] = eco_flows[selected_level]['dry']

print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"各月生态流量（{selected_level}等级）")
print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"{'月份':<6} {'分期':<10} {'生态流量(m³/s)':<15} {'实际流量(m³/s)':<15} {'差值(m³/s)':<12} {'满足情况':<10}")
print("-" * 80)

satisfied = []
for i, (m, q_eco, q_act) in enumerate(zip(month_names, Q_eco, Q_monthly)):
    month = i + 1
    season = '丰水期' if month in flood_months else '枯水期'
    diff = q_act - q_eco
    status = '✅满足' if diff >= 0 else '❌不足'
    satisfied.append(diff >= 0)
    print(f"{m:<6} {season:<10} {q_eco:<15.0f} {q_act:<15.0f} {diff:<12.0f} {status:<10}")

# 统计分析
months_satisfied = np.sum(satisfied)
supply_rate = months_satisfied / 12 * 100

print("-" * 80)
print(f"\n生态流量满足情况：")
print(f"  满足月数: {months_satisfied}/12")
print(f"  满足率: {supply_rate:.1f}%")

deficit_months = [month_names[i] for i in range(12) if not satisfied[i]]
if deficit_months:
    print(f"  不满足月份: {', '.join(deficit_months)}")
    total_deficit = np.sum([Q_eco[i] - Q_monthly[i] for i in range(12) if not satisfied[i]])
    print(f"  总缺水量: {total_deficit:.0f} m³/s")
else:
    print(f"  全年满足生态流量要求")

print("="*80)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# 子图1：月均流量vs生态流量
ax1 = fig.add_subplot(gs[0, :])
x = np.arange(12)

ax1.fill_between(x, 0, Q_monthly, alpha=0.3, color='blue', label='实际流量')
ax1.plot(x, Q_monthly, 'b-o', linewidth=2.5, markersize=8, label='月均流量')
ax1.plot(x, Q_eco, 'r--s', linewidth=2.5, markersize=8, label=f'生态流量（{selected_level}）')

# 标注不满足的月份
for i in range(12):
    if not satisfied[i]:
        ax1.plot(i, Q_monthly[i], 'rx', markersize=15, markeredgewidth=3)

ax1.set_xlabel('月份', fontsize=12, fontweight='bold')
ax1.set_ylabel('流量 (m³/s)', fontsize=12, fontweight='bold')
ax1.set_title(f'题目1-1：月均流量与生态流量对比（满足率{supply_rate:.0f}%）', fontsize=13, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(month_names)
ax1.legend(fontsize=11, loc='upper left')
ax1.grid(True, alpha=0.3)

# 子图2：不同保护等级的生态流量
ax2 = fig.add_subplot(gs[1, 0])
x_levels = np.arange(len(levels))
width = 0.35

flood_values = [eco_flows[lv]['flood'] for lv in levels]
dry_values = [eco_flows[lv]['dry'] for lv in levels]

bars1 = ax2.bar(x_levels - width/2, flood_values, width, label='丰水期', color='blue', alpha=0.7)
bars2 = ax2.bar(x_levels + width/2, dry_values, width, label='枯水期', color='green', alpha=0.7)

ax2.set_xlabel('保护等级', fontsize=11, fontweight='bold')
ax2.set_ylabel('生态流量 (m³/s)', fontsize=11, fontweight='bold')
ax2.set_title('题目1-2：不同保护等级生态流量', fontsize=12, fontweight='bold')
ax2.set_xticks(x_levels)
ax2.set_xticklabels(levels)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, axis='y')

# 子图3：满足情况统计
ax3 = fig.add_subplot(gs[1, 1])
categories = ['满足', '不满足']
counts = [months_satisfied, 12 - months_satisfied]
colors_sat = ['green', 'red']

wedges, texts, autotexts = ax3.pie(counts, labels=categories, autopct='%1.1f%%',
                                     colors=colors_sat, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
ax3.set_title(f'题目1-3：生态流量满足率（{selected_level}等级）', fontsize=12, fontweight='bold')

# 子图4：Tennant法分级标准
ax4 = fig.add_subplot(gs[2, :])
ax4.axis('off')

tennant_text = f"""
Tennant法（蒙大拿法）分级标准：

{'保护等级':<12} {'丰水期(10-3月)':<20} {'枯水期(4-9月)':<20} {'栖息地状态':<20}
{'-'*80}
{'理想':<12} {'60-100% Q̄':<20} {'60-100% Q̄':<20} {'最佳':<20}
{'优良':<12} {'40% Q̄ (200 m³/s)':<20} {'30% Q̄ (150 m³/s)':<20} {'很好，适宜大部分生物':<20}
{'良好':<12} {'30% Q̄ (150 m³/s)':<20} {'20% Q̄ (100 m³/s)':<20} {'良好，满足大部分需求':<20}
{'最小':<12} {'10% Q̄ (50 m³/s)':<20} {'10% Q̄ (50 m³/s)':<20} {'生存下限，仅短期维持':<20}

说明：
• Q̄ = {Q_avg} m³/s（多年平均流量）
• 丰水期：10、11、12、1、2、3月
• 枯水期：4、5、6、7、8、9月（含鱼类产卵期）
• 本河流采用{selected_level}等级，{supply_rate:.0f}%时间满足
• 不满足月份：{', '.join(deficit_months) if deficit_months else '无'}
"""

ax4.text(0.05, 0.95, tennant_text, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.savefig('题目1_生态流量计算.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目1图形已生成：题目1_生态流量计算.png")
plt.show()
