"""
第14章 211高校真题精讲
题目2：西安理工大学2020 - 水量平衡计算

知识点：
- 水量平衡方程
- 作物需水量（ET）
- 灌溉定额计算
- 供需平衡分析
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 灌区基本情况
A_mu = 12000  # 灌溉面积（亩）
A_km2 = A_mu * 0.0006667  # 转换为km²（1亩=666.67m²）
crop_wheat = 0.6  # 小麦占比
crop_corn = 0.4  # 玉米占比

# 水文气象资料（生长季4-9月）
months = ['4月', '5月', '6月', '7月', '8月', '9月']
P = np.array([35, 45, 80, 150, 120, 60])  # 降雨（mm）
E = np.array([120, 150, 180, 160, 140, 100])  # 蒸发（mm）
Kc = np.array([0.8, 1.0, 1.2, 1.1, 0.9, 0.7])  # 作物系数

# 其他参数
alpha_infil = 0.15  # 入渗系数
eta = 0.75  # 渠系水利用系数
Wmax = 150  # 土壤有效持水量（mm）
W0 = 100  # 初始土壤含水量（mm）
W_end = 80  # 期末土壤含水量（mm）

print("="*80)
print("题目2：西安理工大学2020 - 水量平衡计算")
print("="*80)

print(f"\n灌区基本情况：")
print(f"  灌溉面积: {A_mu:.0f} 亩 = {A_km2:.2f} km²")
print(f"  作物结构: 小麦{crop_wheat*100:.0f}%，玉米{crop_corn*100:.0f}%")
print(f"  灌溉方式: 渠道灌溉")
print(f"  计算时段: 生长季（4-9月，6个月）")

print(f"\n其他参数：")
print(f"  入渗系数: α = {alpha_infil} ({alpha_infil*100:.0f}%降雨入渗补给地下水)")
print(f"  渠系水利用系数: η = {eta}")
print(f"  土壤有效持水量: Wmax = {Wmax} mm")
print(f"  初始土壤含水量: W0 = {W0} mm")

# 作物需水量（ET）计算
ET = E * Kc

print(f"\n水文气象资料及作物需水量：")
print(f"  {'月份':<6} {'降雨P(mm)':<12} {'蒸发E(mm)':<12} {'作物系数Kc':<12} {'需水ET(mm)':<12}")
print("-" * 65)

for i, (m, p, e, kc, et) in enumerate(zip(months, P, E, Kc, ET)):
    print(f"  {m:<6} {p:<12.0f} {e:<12.0f} {kc:<12.1f} {et:<12.0f}")

ET_total = np.sum(ET)
P_total = np.sum(P)

print("-" * 65)
print(f"  {'合计':<6} {P_total:<12.0f} {np.sum(E):<12.0f} {'':<12} {ET_total:<12.0f}")

# 有效降雨
Pe = 0.8 * P  # 有效降雨系数0.8

print(f"\n" + "="*80)
print("有效降雨计算")
print("="*80)

print(f"\n有效降雨（Pe = 0.8P）：")
print(f"  {'月份':<6} {'降雨P(mm)':<12} {'有效Pe(mm)':<12}")
print("-" * 35)

for m, p, pe in zip(months, P, Pe):
    print(f"  {m:<6} {p:<12.0f} {pe:<12.1f}")

Pe_total = np.sum(Pe)
print("-" * 35)
print(f"  {'合计':<6} {P_total:<12.0f} {Pe_total:<12.1f}")

# 灌溉定额计算
print(f"\n" + "="*80)
print("灌溉定额计算")
print("="*80)

# 缺水量 = ET - Pe
deficit = ET - Pe

print(f"\n各月缺水量：")
print(f"  {'月份':<6} {'需水ET(mm)':<12} {'有效雨Pe(mm)':<14} {'缺水(mm)':<12} {'灌溉定额M(mm)':<15}")
print("-" * 70)

M = np.zeros(6)  # 灌溉定额
for i, (m, et, pe, d) in enumerate(zip(months, ET, Pe, deficit)):
    # 灌溉定额略大于缺水量，考虑灌溉效率
    M[i] = max(0, d + 5)  # 加5mm作为安全系数
    print(f"  {m:<6} {et:<12.0f} {pe:<14.1f} {d:<12.1f} {M[i]:<15.0f}")

M_total = np.sum(M)
Delta_W = W_end - W0

print("-" * 70)
print(f"  {'合计':<6} {ET_total:<12.0f} {Pe_total:<14.1f} {np.sum(deficit):<12.1f} {M_total:<15.0f}")

print(f"\n土壤储水变化：")
print(f"  初始储水: W0 = {W0} mm")
print(f"  期末储水: W = {W_end} mm")
print(f"  储水变化: ΔW = {Delta_W} mm（{'消耗' if Delta_W < 0 else '增加'}）")

# 修正总灌溉定额（考虑储水变化）
M_total_corrected = M_total - Delta_W

print(f"\n修正灌溉定额：")
print(f"  净灌溉定额: {M_total:.0f} mm")
print(f"  储水消耗: {-Delta_W:.0f} mm")
print(f"  总灌溉定额: {M_total_corrected:.0f} mm")

# 渠首引水量
Q_net = M_total_corrected * A_km2 * 1e6  # m³（净水量）
Q_gross = Q_net / eta  # m³（考虑渠系损失）

print(f"\n渠首引水量：")
print(f"  净水量: {Q_net/1e6:.2f} 万m³")
print(f"  考虑渠系损失（η={eta}）: {Q_gross/1e6:.2f} 万m³")
print(f"  渠首引水定额: {Q_gross/A_km2/1e6:.0f} mm")

# 供需平衡分析
print(f"\n" + "="*80)
print("供需平衡分析")
print("="*80)

# 月供需平衡
balance = P - ET  # 月盈亏
balance_cum = np.cumsum(balance)  # 累计盈亏

print(f"\n月供需平衡：")
print(f"  {'月份':<6} {'需水ET':<10} {'降雨P':<10} {'盈亏(P-ET)':<12} {'累计盈亏':<12} {'需灌溉M':<12}")
print("-" * 70)

for m, et, p, bal, bal_c, m_irr in zip(months, ET, P, balance, balance_cum, M):
    print(f"  {m:<6} {et:<10.0f} {p:<10.0f} {bal:<12.0f} {bal_c:<12.0f} {m_irr:<12.0f}")

print("-" * 70)

# 供水结构分析
print(f"\n供水结构分析：")
water_from_rain = Pe_total
water_from_irrig = M_total_corrected
total_supply = water_from_rain + water_from_irrig

print(f"  降雨供给: {water_from_rain:.0f} mm（{water_from_rain/total_supply*100:.1f}%）")
print(f"  灌溉供给: {water_from_irrig:.0f} mm（{water_from_irrig/total_supply*100:.1f}%）")
print(f"  总供给: {total_supply:.0f} mm")
print(f"  总需求: {ET_total:.0f} mm")
print(f"  平衡情况: {'基本平衡' if abs(total_supply - ET_total) < 20 else '不平衡'}")

# 关键期分析
spring_months = [0, 1, 2]  # 4-6月
summer_months = [3, 4, 5]  # 7-9月

ET_spring = np.sum(ET[spring_months])
P_spring = np.sum(P[spring_months])
M_spring = np.sum(M[spring_months])

ET_summer = np.sum(ET[summer_months])
P_summer = np.sum(P[summer_months])
M_summer = np.sum(M[summer_months])

print(f"\n分期供需分析：")
print(f"  春旱期（4-6月）：")
print(f"    需水: {ET_spring:.0f} mm，降雨: {P_spring:.0f} mm，缺水: {ET_spring-P_spring:.0f} mm")
print(f"    需灌溉: {M_spring:.0f} mm，占全年: {M_spring/M_total*100:.1f}%")
print(f"    评价: {'严重缺水' if (ET_spring-P_spring)/ET_spring > 0.6 else '缺水'}")

print(f"  夏季（7-9月）：")
print(f"    需水: {ET_summer:.0f} mm，降雨: {P_summer:.0f} mm，缺水: {ET_summer-P_summer:.0f} mm")
print(f"    需灌溉: {M_summer:.0f} mm，占全年: {M_summer/M_total*100:.1f}%")
print(f"    评价: {'轻度缺水' if (ET_summer-P_summer)/ET_summer < 0.3 else '缺水'}")

print("="*80)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# 子图1：水量平衡过程
ax1 = fig.add_subplot(gs[0, :])

x = np.arange(len(months))
width = 0.25

bars1 = ax1.bar(x - width, ET, width, label='需水ET', color='red', alpha=0.7)
bars2 = ax1.bar(x, P, width, label='降雨P', color='blue', alpha=0.7)
bars3 = ax1.bar(x + width, M, width, label='灌溉M', color='green', alpha=0.7)

ax1.set_xlabel('月份', fontsize=12, fontweight='bold')
ax1.set_ylabel('水量 (mm)', fontsize=12, fontweight='bold')
ax1.set_title('题目2-1：月水量平衡', fontsize=13, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(months)
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3, axis='y')

# 子图2：累计盈亏
ax2 = fig.add_subplot(gs[1, 0])

ax2.plot(x, balance_cum, 'ro-', linewidth=2.5, markersize=8, label='累计盈亏')
ax2.fill_between(x, 0, balance_cum, where=(balance_cum<0), alpha=0.3, color='red', label='缺水')
ax2.axhline(y=0, color='black', linestyle='--', linewidth=1.5)

ax2.set_xlabel('月份', fontsize=11, fontweight='bold')
ax2.set_ylabel('累计盈亏 (mm)', fontsize=11, fontweight='bold')
ax2.set_title('题目2-2：累计水量盈亏', fontsize=12, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(months)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

# 子图3：供水结构
ax3 = fig.add_subplot(gs[1, 1])

supply_labels = ['降雨供给', '灌溉供给']
supply_values = [water_from_rain, water_from_irrig]
colors_supply = ['blue', 'green']

wedges, texts, autotexts = ax3.pie(supply_values, labels=supply_labels, autopct='%1.1f%%',
                                     colors=colors_supply, startangle=90, 
                                     textprops={'fontsize': 11, 'fontweight': 'bold'})
ax3.set_title(f'题目2-3：供水结构（总{total_supply:.0f}mm）', fontsize=12, fontweight='bold')

# 子图4：水量平衡原理
ax4 = fig.add_subplot(gs[2, :])
ax4.axis('off')

balance_text = f"""
水量平衡计算结果与分析：

1. 水量平衡方程：
   P + I - ET - R = ΔW
   简化：I = ET - Pe + ΔW（忽略径流）

2. 作物需水量：
   • 生长季总需水：ET = {ET_total:.0f} mm
   • 逐月：4月({ET[0]:.0f})、5月({ET[1]:.0f})、6月({ET[2]:.0f})、7月({ET[3]:.0f})、8月({ET[4]:.0f})、9月({ET[5]:.0f})
   • 高峰期：6月（{ET[2]:.0f} mm）

3. 灌溉需求：
   • 总降雨：{P_total:.0f} mm，有效降雨：{Pe_total:.0f} mm（{Pe_total/P_total*100:.0f}%）
   • 总灌溉定额：{M_total_corrected:.0f} mm（含储水消耗{-Delta_W:.0f} mm）
   • 渠首引水：{Q_gross/1e6:.2f} 万m³（考虑渠系损失{(1-eta)*100:.0f}%）

4. 供需平衡：
   • 降雨供给：{water_from_rain:.0f} mm（{water_from_rain/total_supply*100:.1f}%）
   • 灌溉供给：{water_from_irrig:.0f} mm（{water_from_irrig/total_supply*100:.1f}%）
   • 关键期：4-6月严重缺水（缺{ET_spring-P_spring:.0f} mm），需灌溉{M_spring:.0f} mm

5. 管理建议：
   ✓ 发展节水灌溉（滴灌、喷灌）→ 提高η至0.85
   ✓ 建设调蓄工程（水库、蓄水池）→ 缓解春旱
   ✓ 调整作物结构（耐旱品种）→ 降低需水
   ✓ 优化灌溉制度→ 适时适量灌溉

6. 西安理工大学考点特色：
   ✓ 水量平衡：灌区水资源管理基础
   ✓ 作物需水：农业水文核心内容
   ✓ 西北特色：春旱严重，灌溉依赖度高
   ✓ 实用性强：灌区设计、调度运行
"""

ax4.text(0.05, 0.95, balance_text, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

plt.savefig('题目2_西理工真题_水量平衡.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目2图形已生成：题目2_西理工真题_水量平衡.png")
plt.show()
