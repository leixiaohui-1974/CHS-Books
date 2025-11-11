"""
第15章 综合应用与压轴题
题目2：工程设计 - 小流域防洪工程设计

知识点：
- 设计暴雨（第2章）
- SCS-CN产流（第4章）
- 汇流计算（第5章）
- 工程方案比选
- 综合决策
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 流域特征
F = 28.5  # 流域面积（km²）
L = 12.8  # 主河道长度（km）
i = 0.025  # 平均坡度

# 土地利用及CN值
land_use = {
    '林地': {'pct': 0.60, 'CN': 70},
    '农田': {'pct': 0.30, 'CN': 78},
    '村镇': {'pct': 0.10, 'CN': 88}
}

# 设计暴雨
P20 = 180  # 20年一遇24h雨量（mm）
r = 0.4  # 峰现系数

# 汇流参数
tau_g = 1.5  # 地面汇流时间（h）
tau_r = 2.5  # 河道汇流时间（h）
tau = 4.0  # 总汇流时间（h）

print("="*80)
print("题目2：工程设计 - 小流域防洪工程设计")
print("="*80)

print(f"\n流域特征：")
print(f"  流域面积: F = {F} km²")
print(f"  主河道长度: L = {L} km")
print(f"  平均坡度: i = {i}")

print(f"\n土地利用及CN值：")
for land, props in land_use.items():
    print(f"  {land}: {props['pct']*100:.0f}%, CN = {props['CN']}")

# 综合CN值
CN_composite = sum(props['pct'] * props['CN'] for props in land_use.values())
S = 25400 / CN_composite - 254
Ia = 0.2 * S

print(f"\nSCS-CN模型参数：")
print(f"  综合CN值: {CN_composite:.1f}")
print(f"  最大蓄水量 S: {S:.1f} mm")
print(f"  初损 Ia: {Ia:.1f} mm")

# 暴雨时程分配（典型雨型，r=0.4）
rain_dist = [3, 5, 8, 12, 20, 15, 12, 9, 7, 5, 3, 1]  # 12时段占比（%）
P_periods = np.array(rain_dist) / 100 * P20

print(f"\n设计暴雨时程分配（r={r}）：")
print(f"  24h雨量: {P20} mm")
print(f"  时段数: 12（Δt = 2h）")

# 产流计算
def scs_cn_runoff(P_cum, S):
    """SCS-CN产流"""
    Ia = 0.2 * S
    if P_cum <= Ia:
        return 0
    else:
        return (P_cum - Ia)**2 / (P_cum + 0.8*S)

P_cum = np.cumsum(P_periods)
Q_cum = np.array([scs_cn_runoff(p, S) for p in P_cum])
Q_periods = np.diff(Q_cum, prepend=0)
Q_total = Q_cum[-1]
runoff_coef = Q_total / P20

print(f"\n产流计算：")
print(f"  总降雨: {P20} mm")
print(f"  总产流: {Q_total:.1f} mm")
print(f"  径流系数: {runoff_coef:.3f} = {runoff_coef*100:.1f}%")

# 设计洪峰计算（推理公式）
P_max = np.max(P_periods)
idx_max = np.argmax(P_periods) + 1

Qp = 0.278 * runoff_coef * (F / tau) * P_max

print(f"\n设计洪峰计算（推理公式）：")
print(f"  最大时段雨量: {P_max:.1f} mm（第{idx_max}时段）")
print(f"  汇流时间: {tau} h")
print(f"  设计洪峰: Qp = {Qp:.1f} m³/s")

# 工程方案比选
print("\n" + "="*80)
print("工程方案比选")
print("="*80)

# 方案1：防洪堤
scheme1 = {
    '名称': '方案1：防洪堤',
    '投资': 600,  # 万元
    '削峰': 0,  # %
    '周期': 1,  # 年
    '生态': 3,  # 1-10分
    '综合': 6.6  # 综合得分
}

# 方案2：水库+堤
scheme2 = {
    '名称': '方案2：水库+防洪堤',
    '投资': 1200,
    '削峰': 40,
    '周期': 2.5,
    '生态': 6,
    '综合': 7.7
}

# 方案3：海绵流域
scheme3 = {
    '名称': '方案3：海绵流域',
    '投资': 800,
    '削峰': 14,
    '周期': 4,
    '生态': 10,
    '综合': 8.4
}

schemes = [scheme1, scheme2, scheme3]

print(f"\n方案对比：")
print(f"{'方案':<18} {'投资(万元)':<12} {'削峰(%)':<10} {'周期(年)':<12} {'生态(分)':<12} {'综合得分':<12}")
print("-" * 80)
for s in schemes:
    print(f"{s['名称']:<18} {s['投资']:<12} {s['削峰']:<10} {s['周期']:<12} {s['生态']:<12} {s['综合']:<12.1f}")

# 推荐方案
best_scheme = max(schemes, key=lambda x: x['综合'])
print(f"\n推荐方案：{best_scheme['名称']}（综合得分{best_scheme['综合']:.1f}）")

print("="*80)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# 子图1：暴雨时程与产流过程
ax1 = fig.add_subplot(gs[0, :])

# 暴雨柱状图（倒置）
ax1_rain = ax1.twinx()
x = np.arange(1, 13)
ax1_rain.bar(x, P_periods, width=0.6, alpha=0.3, color='blue', label='时段雨量')
ax1_rain.set_ylabel('雨量 (mm)', fontsize=11, fontweight='bold')
ax1_rain.set_ylim(max(P_periods)*1.5, 0)
ax1_rain.legend(loc='upper left', fontsize=10)

# 产流过程
ax1.plot(x, Q_cum, 'r-o', linewidth=2.5, markersize=8, label='累计产流')
ax1.bar(x, Q_periods, width=0.4, alpha=0.6, color='green', label='时段产流')

ax1.set_xlabel('时段', fontsize=12, fontweight='bold')
ax1.set_ylabel('产流量 (mm)', fontsize=12, fontweight='bold')
ax1.set_title(f'题目2-1：设计暴雨与产流过程（α={runoff_coef*100:.1f}%）', fontsize=13, fontweight='bold')
ax1.legend(loc='upper right', fontsize=11)
ax1.grid(True, alpha=0.3)

# 子图2：工程方案投资对比
ax2 = fig.add_subplot(gs[1, 0])

names = [s['名称'].split('：')[1] for s in schemes]
投资 = [s['投资'] for s in schemes]
colors = ['red', 'blue', 'green']

bars = ax2.bar(names, 投资, color=colors, alpha=0.7, edgecolor='black', linewidth=2)

for i, (bar, val) in enumerate(zip(bars, 投资)):
    ax2.text(i, val + 30, f'{val}万元', ha='center', fontsize=10, fontweight='bold')

ax2.set_ylabel('投资 (万元)', fontsize=11, fontweight='bold')
ax2.set_title('题目2-2：工程方案投资对比', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

# 子图3：方案综合评分
ax3 = fig.add_subplot(gs[1, 1])

# 雷达图
categories = ['防洪效益', '经济性', '生态效益', '可持续性']
angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
angles += angles[:1]

# 评分数据（0-10分）
scores1 = [7, 9, 3, 4] + [7]
scores2 = [10, 5, 6, 7] + [10]
scores3 = [8, 7, 10, 10] + [8]

ax3 = plt.subplot(gs[1, 1], projection='polar')
ax3.plot(angles, scores1, 'o-', linewidth=2, label='方案1', color='red')
ax3.fill(angles, scores1, alpha=0.15, color='red')
ax3.plot(angles, scores2, 's-', linewidth=2, label='方案2', color='blue')
ax3.fill(angles, scores2, alpha=0.15, color='blue')
ax3.plot(angles, scores3, '^-', linewidth=2, label='方案3', color='green')
ax3.fill(angles, scores3, alpha=0.15, color='green')

ax3.set_xticks(angles[:-1])
ax3.set_xticklabels(categories)
ax3.set_ylim(0, 10)
ax3.set_title('题目2-3：方案综合评分雷达图', fontsize=12, fontweight='bold', pad=20)
ax3.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=10)
ax3.grid(True)

# 子图4：综合分析
ax4 = fig.add_subplot(gs[2, :])
ax4.axis('off')

analysis_text = f"""
小流域防洪工程设计综合分析：

1. 设计暴雨与产流：
   • 20年一遇24h雨量：{P20} mm
   • 综合CN值：{CN_composite:.1f}（林地{land_use['林地']['pct']*100:.0f}%，农田{land_use['农田']['pct']*100:.0f}%，村镇{land_use['村镇']['pct']*100:.0f}%）
   • 总产流：{Q_total:.1f} mm（径流系数{runoff_coef*100:.1f}%）
   • 设计洪峰：Qp = {Qp:.1f} m³/s

2. 工程方案对比：
   方案1（防洪堤）：投资600万，无削峰，1年建成，生态差
   方案2（水库+堤）：投资1200万，削峰40%，2.5年建成，生态中等
   方案3（海绵流域）：投资800万，削峰14%，4年建成，生态优

3. 多目标评价（加权得分）：
   • 方案1：6.6分（经济性好，但生态差）
   • 方案2：7.7分（防洪效益最好，但投资大）
   • 方案3：8.4分（综合效益最高，生态优先）★ 推荐

4. 推荐方案3（海绵流域）理由：
   ✓ 综合效益最高（8.4分）
   ✓ 生态优先，源头减量，标本兼治
   ✓ 投资适中（800万），性价比高
   ✓ 可持续性强，符合生态文明建设要求
   ✓ 政策支持（海绵城市、乡村振兴）

5. 实施建议：
   • 分期实施（紧急工程→退耕还林→生态修复）
   • 政策保障（退耕补贴、生态补偿）
   • 群众参与（利益补偿、共建共享）
   • 监测评估（定期监测、适应性调整）

6. 综合应用要点：
   ✓ 跨章节综合（第2、4、5章）
   ✓ 完整设计流程（暴雨→产流→汇流→工程）
   ✓ 多方案比选（技术、经济、生态）
   ✓ 综合决策（加权评分、推荐最优）
"""

ax4.text(0.05, 0.95, analysis_text, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

plt.savefig('题目2_小流域防洪工程.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目2图形已生成：题目2_小流域防洪工程.png")
print("="*80)
plt.show()
