"""
第14章 211高校真题精讲
题目1：华北水利水电大学2021 - SCS-CN产流模型

知识点：
- SCS-CN模型原理
- 径流曲线数（Curve Number）
- 面积加权法
- 土地利用影响分析
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 流域特征
F = 18.5  # 流域面积（km²）

# 土地利用及CN值
land_use = {
    '农田': {'area_pct': 0.40, 'CN': 78},
    '林地': {'area_pct': 0.35, 'CN': 70},
    '城镇': {'area_pct': 0.15, 'CN': 88},
    '裸地': {'area_pct': 0.10, 'CN': 82}
}

# 设计暴雨
P24 = 120  # 24小时雨量（mm）
rain_distribution = [3, 4, 5, 7, 9, 12, 15, 18, 12, 8, 5, 2]  # 各时段占比（%）

print("="*80)
print("题目1：华北水利水电大学2021 - SCS-CN产流模型")
print("="*80)

print(f"\n流域特征：")
print(f"  流域面积: F = {F} km²")
print(f"\n土地利用及CN值：")
print(f"  {'类型':<8} {'面积占比':<12} {'CN值':<8}")
print("-" * 40)
for land, props in land_use.items():
    print(f"  {land:<8} {props['area_pct']*100:<12.1f}% {props['CN']:<8}")

# 计算综合CN值
CN_composite = sum(props['area_pct'] * props['CN'] for props in land_use.values())
print(f"\n综合CN值（面积加权）：")
print(f"  CN = {CN_composite:.1f}")

# 计算最大蓄水量S和初损Ia
S = 25400 / CN_composite - 254  # mm
Ia = 0.2 * S  # mm

print(f"\nSCS-CN模型参数：")
print(f"  最大蓄水量 S = {S:.1f} mm")
print(f"  初损 Ia = {Ia:.1f} mm")

# 各时段雨量
n_periods = len(rain_distribution)
P_periods = np.array(rain_distribution) / 100 * P24  # mm

print(f"\n各时段雨量分配：")
print(f"  {'时段':<6} {'占比(%)':<10} {'雨量(mm)':<10} {'累计(mm)':<10}")
print("-" * 45)

P_cum = np.cumsum(P_periods)
for i, (pct, p, p_c) in enumerate(zip(rain_distribution, P_periods, P_cum), 1):
    print(f"  {i:<6} {pct:<10} {p:<10.1f} {p_c:<10.1f}")

print(f"\n  总雨量: {P24} mm")

# SCS-CN产流计算
def scs_cn_runoff(P_cum, S):
    """
    SCS-CN模型计算径流
    
    参数：
    P_cum: 累计降雨（mm）
    S: 最大蓄水量（mm）
    
    返回：
    Q: 累计径流（mm）
    """
    Ia = 0.2 * S
    if P_cum <= Ia:
        return 0
    else:
        Q = (P_cum - Ia)**2 / (P_cum + 0.8*S)
        return Q

print("\n" + "="*80)
print("SCS-CN产流计算")
print("="*80)

print(f"\n逐时段产流计算：")
print(f"  {'时段':<6} {'雨量(mm)':<10} {'累计雨(mm)':<12} {'累计流(mm)':<12} {'时段流(mm)':<12}")
print("-" * 60)

Q_cum = np.zeros(n_periods)
Q_periods = np.zeros(n_periods)

for i in range(n_periods):
    Q_cum[i] = scs_cn_runoff(P_cum[i], S)
    if i > 0:
        Q_periods[i] = Q_cum[i] - Q_cum[i-1]
    else:
        Q_periods[i] = Q_cum[i]
    
    print(f"  {i+1:<6} {P_periods[i]:<10.1f} {P_cum[i]:<12.1f} {Q_cum[i]:<12.1f} {Q_periods[i]:<12.1f}")

Q_total = Q_cum[-1]
runoff_coef = Q_total / P24

print("-" * 60)
print(f"\n产流统计：")
print(f"  总降雨量: {P24:.1f} mm")
print(f"  总产流量: {Q_total:.1f} mm")
print(f"  径流系数: {runoff_coef:.3f} = {runoff_coef*100:.1f}%")

# 土地利用变化情景分析
print("\n" + "="*80)
print("土地利用变化情景分析")
print("="*80)

# 情景1：城镇化（+10%城镇，-10%农田）
scenario1 = {
    '农田': {'area_pct': 0.30, 'CN': 78},
    '林地': {'area_pct': 0.35, 'CN': 70},
    '城镇': {'area_pct': 0.25, 'CN': 88},
    '裸地': {'area_pct': 0.10, 'CN': 82}
}

CN_s1 = sum(props['area_pct'] * props['CN'] for props in scenario1.values())
S_s1 = 25400 / CN_s1 - 254
Q_s1 = scs_cn_runoff(P24, S_s1)

print(f"\n情景1：城镇化（+10%城镇，-10%农田）")
print(f"  新CN值: {CN_s1:.1f}（原{CN_composite:.1f}，+{CN_s1-CN_composite:.1f}）")
print(f"  新产流: {Q_s1:.1f} mm（原{Q_total:.1f} mm，+{Q_s1-Q_total:.1f} mm，+{(Q_s1-Q_total)/Q_total*100:.1f}%）")

# 情景2：退耕还林（+10%林地，-10%农田）
scenario2 = {
    '农田': {'area_pct': 0.30, 'CN': 78},
    '林地': {'area_pct': 0.45, 'CN': 70},
    '城镇': {'area_pct': 0.15, 'CN': 88},
    '裸地': {'area_pct': 0.10, 'CN': 82}
}

CN_s2 = sum(props['area_pct'] * props['CN'] for props in scenario2.values())
S_s2 = 25400 / CN_s2 - 254
Q_s2 = scs_cn_runoff(P24, S_s2)

print(f"\n情景2：退耕还林（+10%林地，-10%农田）")
print(f"  新CN值: {CN_s2:.1f}（原{CN_composite:.1f}，{CN_s2-CN_composite:.1f}）")
print(f"  新产流: {Q_s2:.1f} mm（原{Q_total:.1f} mm，{Q_s2-Q_total:.1f} mm，{(Q_s2-Q_total)/Q_total*100:.1f}%）")

print("="*80)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# 子图1：雨量与产流过程
ax1 = fig.add_subplot(gs[0, :])

# 雨量柱状图（倒置）
ax1_rain = ax1.twinx()
ax1_rain.bar(np.arange(1, n_periods+1), P_periods, width=0.6, alpha=0.3, color='blue', label='时段雨量')
ax1_rain.set_ylabel('雨量 (mm)', fontsize=11, fontweight='bold')
ax1_rain.set_ylim(max(P_periods)*1.5, 0)  # 倒置
ax1_rain.legend(loc='upper left', fontsize=10)

# 产流过程
ax1.plot(np.arange(1, n_periods+1), Q_cum, 'r-o', linewidth=2.5, markersize=8, label='累计产流')
ax1.bar(np.arange(1, n_periods+1), Q_periods, width=0.4, alpha=0.6, color='green', label='时段产流')

ax1.set_xlabel('时段', fontsize=12, fontweight='bold')
ax1.set_ylabel('产流量 (mm)', fontsize=12, fontweight='bold')
ax1.set_title(f'题目1-1：雨量与产流过程（径流系数{runoff_coef*100:.1f}%）', fontsize=13, fontweight='bold')
ax1.legend(loc='upper right', fontsize=11)
ax1.grid(True, alpha=0.3)

# 子图2：土地利用CN值
ax2 = fig.add_subplot(gs[1, 0])

land_types = list(land_use.keys())
cn_values = [props['CN'] for props in land_use.values()]
areas = [props['area_pct']*100 for props in land_use.values()]
colors = ['gold', 'green', 'red', 'brown']

bars = ax2.bar(land_types, cn_values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)

# 添加面积占比标签
for i, (bar, area) in enumerate(zip(bars, areas)):
    ax2.text(i, cn_values[i] + 1, f'CN={cn_values[i]}\n({area:.0f}%)', 
             ha='center', va='bottom', fontsize=9, fontweight='bold')

ax2.axhline(y=CN_composite, color='red', linestyle='--', linewidth=2, alpha=0.7, 
            label=f'综合CN={CN_composite:.1f}')
ax2.set_ylabel('CN值', fontsize=11, fontweight='bold')
ax2.set_title('题目1-2：土地利用CN值', fontsize=12, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, axis='y')

# 子图3：CN值-产流关系
ax3 = fig.add_subplot(gs[1, 1])

CN_range = np.arange(60, 95, 1)
Q_range = [scs_cn_runoff(P24, 25400/cn - 254) for cn in CN_range]

ax3.plot(CN_range, Q_range, 'b-', linewidth=2.5)
ax3.plot(CN_composite, Q_total, 'ro', markersize=12, label=f'现状（CN={CN_composite:.1f}）')
ax3.plot(CN_s1, Q_s1, 'r^', markersize=12, label=f'城镇化（CN={CN_s1:.1f}）')
ax3.plot(CN_s2, Q_s2, 'rv', markersize=12, label=f'退耕还林（CN={CN_s2:.1f}）')

ax3.set_xlabel('CN值', fontsize=11, fontweight='bold')
ax3.set_ylabel('产流量 (mm)', fontsize=11, fontweight='bold')
ax3.set_title(f'题目1-3：CN值与产流关系（P={P24}mm）', fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)

# 子图4：SCS-CN模型原理
ax4 = fig.add_subplot(gs[2, :])
ax4.axis('off')

scs_text = f"""
SCS-CN模型原理与计算结果：

1. 基本公式：
   Q = (P - Ia)² / (P - Ia + S),  当 P > Ia
   Q = 0,                         当 P ≤ Ia
   
   其中：S = 25400/CN - 254 (mm)
         Ia = 0.2S (mm)

2. 综合CN值（面积加权）：
   CN = Σ(Ai × CNi) / ΣAi
   本流域：CN = {CN_composite:.1f}
   
3. 产流计算结果：
   • 总降雨：{P24:.1f} mm
   • 初损：{Ia:.1f} mm（前3时段未产流）
   • 总产流：{Q_total:.1f} mm
   • 径流系数：{runoff_coef*100:.1f}%

4. 土地利用变化影响：
   • 城镇化（+10%城镇）：CN {CN_composite:.1f} → {CN_s1:.1f}，产流 +{(Q_s1-Q_total)/Q_total*100:.1f}%
   • 退耕还林（+10%林地）：CN {CN_composite:.1f} → {CN_s2:.1f}，产流 {(Q_s2-Q_total)/Q_total*100:.1f}%
   • 结论：城镇化显著增加产流，退耕还林减少产流

5. 华北水利水电大学考点特色：
   ✓ SCS-CN模型：美国经典，国际通用
   ✓ 土地利用分析：城镇化、水土保持
   ✓ 小流域治理：黄河流域特色
   ✓ 工程应用：防洪设计、水土保持工程
"""

ax4.text(0.05, 0.95, scs_text, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.savefig('题目1_华水真题_SCS_CN模型.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目1图形已生成：题目1_华水真题_SCS_CN模型.png")
plt.show()
