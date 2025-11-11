"""
第11章 水库调度
题目1：水库兴利调节计算（时历法）

知识点：
- 兴利调节原理
- 时历法逐月调节
- 水量平衡
- 供水保证率
- 弃水分析
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 基本数据
months = np.arange(1, 13)
month_names = ['1月', '2月', '3月', '4月', '5月', '6月', 
               '7月', '8月', '9月', '10月', '11月', '12月']

# 来水量（10⁶ m³）
inflow = np.array([40, 35, 50, 80, 120, 150, 180, 160, 100, 60, 45, 40])

# 用水需求（10⁶ m³）
# 非灌溉期（1-3月，10-12月）：26
# 灌溉期（4-9月）：130
demand = np.array([26, 26, 26, 130, 130, 130, 130, 130, 130, 26, 26, 26])

# 水库特征
V_N = 200  # 正常蓄水位对应库容（10⁶ m³）
V_D = 0    # 死库容（简化设为0）
V_0 = 150  # 年初库容（10⁶ m³）

print("="*80)
print("题目1：水库兴利调节计算（时历法）")
print("="*80)

print(f"\n水库特征：")
print(f"  正常蓄水位库容 V_N = {V_N} × 10⁶ m³")
print(f"  死库容 V_D = {V_D} × 10⁶ m³")
print(f"  调节库容 = {V_N - V_D} × 10⁶ m³")
print(f"  年初库容 V_0 = {V_0} × 10⁶ m³")

print(f"\n来水量：")
for i, (m, w) in enumerate(zip(month_names, inflow)):
    print(f"  {m}: {w} × 10⁶ m³", end="")
    if (i + 1) % 4 == 0:
        print()
print(f"\n  全年总来水量: {np.sum(inflow)} × 10⁶ m³")

print(f"\n用水需求：")
print(f"  非灌溉期（1-3月，10-12月）: 26 × 10⁶ m³/月")
print(f"  灌溉期（4-9月）: 130 × 10⁶ m³/月")
print(f"  全年总需水量: {np.sum(demand)} × 10⁶ m³")

# 时历法调节计算
V_start = np.zeros(13)  # 月初库容
V_end = np.zeros(12)    # 月末库容
supply = np.zeros(12)   # 实际供水
shortage = np.zeros(12) # 缺水量
spill = np.zeros(12)    # 弃水量

V_start[0] = V_0

print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("时历法逐月调节计算")
print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"{'月份':<6} {'月初库容':<10} {'来水':<8} {'需水':<8} {'实供水':<8} {'缺水':<8} {'月末库容':<10} {'弃水':<8}")
print(f"{'':6} {'(10⁶m³)':<10} {'(10⁶m³)':<8} {'(10⁶m³)':<8} {'(10⁶m³)':<8} {'(10⁶m³)':<8} {'(10⁶m³)':<10} {'(10⁶m³)':<8}")
print("-" * 80)

for i in range(12):
    V_t = V_start[i]
    W_t = inflow[i]
    U_t = demand[i]
    
    # 可供水量 = 月初库容 + 来水 - 死库容
    available = V_t + W_t - V_D
    
    # 实际供水
    if available >= U_t:
        U_actual = U_t
        short = 0
    else:
        U_actual = available
        short = U_t - U_actual
    
    # 月末库容
    V_end_temp = V_t + W_t - U_actual
    
    # 检查库容约束
    if V_end_temp > V_N:
        s = V_end_temp - V_N
        V_end[i] = V_N
    else:
        s = 0
        V_end[i] = V_end_temp
    
    supply[i] = U_actual
    shortage[i] = short
    spill[i] = s
    V_start[i+1] = V_end[i]
    
    print(f"{month_names[i]:<6} {V_t:<10.1f} {W_t:<8.0f} {U_t:<8.0f} {U_actual:<8.1f} {short:<8.1f} {V_end[i]:<10.1f} {s:<8.1f}")

print("-" * 80)
print(f"{'合计':<6} {'':<10} {np.sum(inflow):<8.0f} {np.sum(demand):<8.0f} {np.sum(supply):<8.1f} {np.sum(shortage):<8.1f} {'':<10} {np.sum(spill):<8.1f}")

# 统计分析
print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("调节性能分析")
print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# 供水保证率
months_satisfied = np.sum(shortage == 0)
supply_rate = months_satisfied / 12 * 100
print(f"\n供水情况：")
print(f"  总需水量: {np.sum(demand):.0f} × 10⁶ m³")
print(f"  实供水量: {np.sum(supply):.1f} × 10⁶ m³")
print(f"  总缺水量: {np.sum(shortage):.1f} × 10⁶ m³")
print(f"  缺水月数: {12 - months_satisfied} 个月")
print(f"  供水保证率: {supply_rate:.1f}%")

# 弃水分析
print(f"\n弃水情况：")
print(f"  总弃水量: {np.sum(spill):.1f} × 10⁶ m³")
print(f"  弃水率: {np.sum(spill)/np.sum(inflow)*100:.1f}%")
months_spill = np.sum(spill > 0)
print(f"  弃水月数: {months_spill} 个月")

# 库容利用
V_max = np.max(V_end)
V_min = np.min(V_end)
print(f"\n库容利用：")
print(f"  最大库容: {V_max:.1f} × 10⁶ m³")
print(f"  最小库容: {V_min:.1f} × 10⁶ m³")
print(f"  库容变幅: {V_max - V_min:.1f} × 10⁶ m³")
print(f"  利用率: {(V_max - V_min)/V_N*100:.1f}%")

print("="*80)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# 子图1：来水vs需水
ax1 = fig.add_subplot(gs[0, :])
x = np.arange(12)
width = 0.35

bars1 = ax1.bar(x - width/2, inflow, width, label='来水', color='blue', alpha=0.7)
bars2 = ax1.bar(x + width/2, demand, width, label='需水', color='red', alpha=0.7)

ax1.set_xlabel('月份', fontsize=12, fontweight='bold')
ax1.set_ylabel('水量 (10⁶ m³)', fontsize=12, fontweight='bold')
ax1.set_title('题目1-1：来水与需水对比', fontsize=13, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(month_names)
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3, axis='y')

# 子图2：库容变化过程
ax2 = fig.add_subplot(gs[1, :])
ax2.fill_between(months, V_D, V_end, alpha=0.3, color='cyan', label='库容变化')
ax2.plot(months, V_end, 'b-o', linewidth=2.5, markersize=8, label='月末库容')
ax2.axhline(V_N, color='red', linestyle='--', linewidth=2, label=f'正常蓄水位库容({V_N})')
ax2.axhline(V_D, color='gray', linestyle='--', linewidth=1.5, label=f'死库容({V_D})')

# 标注最大最小库容
ax2.plot(np.argmax(V_end)+1, V_max, 'r*', markersize=20, label=f'最大库容({V_max:.0f})')
ax2.plot(np.argmin(V_end)+1, V_min, 'g*', markersize=20, label=f'最小库容({V_min:.0f})')

ax2.set_xlabel('月份', fontsize=12, fontweight='bold')
ax2.set_ylabel('库容 (10⁶ m³)', fontsize=12, fontweight='bold')
ax2.set_title('题目1-2：水库库容变化过程', fontsize=13, fontweight='bold')
ax2.legend(fontsize=10, loc='best')
ax2.grid(True, alpha=0.3)
ax2.set_xticks(months)
ax2.set_xticklabels(month_names)
ax2.set_ylim(0, V_N + 50)

# 子图3：供水与缺水分析
ax3 = fig.add_subplot(gs[2, 0])
ax3.bar(months, supply, color='green', alpha=0.7, edgecolor='black', label='实际供水')
ax3.bar(months, shortage, bottom=supply, color='red', alpha=0.7, edgecolor='black', label='缺水')
ax3.set_xlabel('月份', fontsize=11, fontweight='bold')
ax3.set_ylabel('水量 (10⁶ m³)', fontsize=11, fontweight='bold')
ax3.set_title(f'题目1-3：供水情况（保证率{supply_rate:.0f}%）', fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3, axis='y')
ax3.set_xticks(months)
ax3.set_xticklabels(month_names, rotation=45)

# 子图4：弃水分析
ax4 = fig.add_subplot(gs[2, 1])
colors_spill = ['red' if s > 0 else 'gray' for s in spill]
bars = ax4.bar(months, spill, color=colors_spill, alpha=0.7, edgecolor='black')
ax4.set_xlabel('月份', fontsize=11, fontweight='bold')
ax4.set_ylabel('弃水量 (10⁶ m³)', fontsize=11, fontweight='bold')
ax4.set_title(f'题目1-4：弃水分布（总弃水{np.sum(spill):.0f}×10⁶m³）', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')
ax4.set_xticks(months)
ax4.set_xticklabels(month_names, rotation=45)

plt.savefig('题目1_兴利调节.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目1图形已生成：题目1_兴利调节.png")
plt.show()
