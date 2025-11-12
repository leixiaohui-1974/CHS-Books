"""
第6章 流域水文模型
题目2：SCS-CN模型应用

知识点：
- SCS-CN模型原理
- CN值确定
- 最大潜在下渗量S
- 产流深度计算
- 径流系数
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Rectangle, Wedge

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 数据
F = 5.0  # 流域面积，km²
land_use = ['商业区', '居住区', '公园绿地', '林地']
areas = np.array([1.5, 2.0, 1.0, 0.5])  # km²
CN_values = np.array([92, 85, 61, 45])
P = 80  # 降雨，mm
lambda_param = 0.2  # 初损系数

# 计算综合CN值
CN_composite = np.sum(CN_values * areas) / np.sum(areas)

# 计算S和Ia
S = 25400 / CN_composite - 254  # mm
Ia = lambda_param * S  # mm

# 计算产流深度R
if P > Ia:
    R = (P - Ia)**2 / (P - Ia + S)
else:
    R = 0

# 径流系数
alpha = R / P if P > 0 else 0

# 下渗量
Fa = P - Ia - R if P > Ia else 0

print("="*70)
print("题目2：SCS-CN模型应用")
print("="*70)
print(f"\n流域特征：")
print(f"  流域面积 F = {F} km²")
print(f"\n土地利用和CN值：")
for lu, area, cn in zip(land_use, areas, CN_values):
    print(f"  {lu}: {area} km², CN={cn}")

print(f"\n综合CN值计算：")
print(f"  CN综合 = Σ(CNᵢ×Aᵢ)/ΣAᵢ")
print(f"  CN综合 = {np.sum(CN_values * areas):.1f}/{np.sum(areas):.1f}")
print(f"  CN综合 = {CN_composite:.1f}")

print(f"\n参数计算：")
print(f"  最大潜在下渗量 S = 25400/CN - 254")
print(f"  S = 25400/{CN_composite:.1f} - 254")
print(f"  S = {S:.1f} mm")
print(f"\n  初损 Ia = λ·S (λ={lambda_param})")
print(f"  Ia = {lambda_param}×{S:.1f}")
print(f"  Ia = {Ia:.1f} mm")

print(f"\n产流计算：")
print(f"  降雨 P = {P} mm")
print(f"  判断：P ({P}mm) > Ia ({Ia:.1f}mm) ✓ 满足产流条件")
print(f"\n  产流深度 R = (P-Ia)²/(P-Ia+S)")
print(f"  R = ({P}-{Ia:.1f})²/({P}-{Ia:.1f}+{S:.1f})")
print(f"  R = {(P-Ia):.1f}²/{(P-Ia+S):.1f}")
print(f"  R = {R:.1f} mm")

print(f"\n  实际下渗量 Fa = P - Ia - R")
print(f"  Fa = {P} - {Ia:.1f} - {R:.1f}")
print(f"  Fa = {Fa:.1f} mm")

print(f"\n  径流系数 α = R/P")
print(f"  α = {R:.1f}/{P}")
print(f"  α = {alpha:.3f} = {alpha*100:.1f}%")

print(f"\n验证：")
print(f"  Fa/S = {Fa:.1f}/{S:.1f} = {Fa/S:.3f}")
print(f"  R/(P-Ia) = {R:.1f}/{P-Ia:.1f} = {R/(P-Ia):.3f}")
print(f"  两者应相等（误差<0.001） ✓")
print("="*70)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

# 子图1：CN值分布
ax1 = fig.add_subplot(gs[0, :2])
colors_bar = ['red', 'orange', 'green', 'darkgreen']
bars = ax1.bar(land_use, CN_values, color=colors_bar, alpha=0.7, 
               edgecolor='black', linewidth=2)

# 标注面积
for bar, area, cn in zip(bars, areas, CN_values):
    ax1.text(bar.get_x() + bar.get_width()/2, cn + 2,
             f'CN={cn}\n面积={area}km²',
             ha='center', fontsize=9)

ax1.axhline(CN_composite, color='blue', linestyle='--', linewidth=2,
            label=f'综合CN={CN_composite:.1f}')
ax1.set_ylabel('CN值', fontsize=11)
ax1.set_title('题目2-1：不同土地利用类型的CN值', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, axis='y')
ax1.set_ylim(0, 100)

# 子图2：土地利用面积占比
ax2 = fig.add_subplot(gs[0, 2])
wedges, texts, autotexts = ax2.pie(areas, labels=land_use, autopct='%1.1f%%',
                                     colors=colors_bar, startangle=90)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(10)
    autotext.set_fontweight('bold')

ax2.set_title('题目2-2：土地利用面积占比', fontsize=11, fontweight='bold')

# 子图3：SCS-CN模型原理
ax3 = fig.add_subplot(gs[1, :2])
P_range = np.linspace(0, 150, 100)
R_range = np.zeros_like(P_range)

for i, p_val in enumerate(P_range):
    if p_val > Ia:
        R_range[i] = (p_val - Ia)**2 / (p_val - Ia + S)
    else:
        R_range[i] = 0

ax3.plot(P_range, R_range, 'b-', linewidth=2, label='SCS-CN模型')
ax3.plot([0, 150], [0, 150], 'k--', linewidth=1, alpha=0.5, label='R=P（无下渗）')
ax3.plot(P, R, 'ro', markersize=12, label=f'当前降雨(P={P}mm, R={R:.1f}mm)')

ax3.axvline(Ia, color='orange', linestyle='--', linewidth=1.5,
            label=f'初损Ia={Ia:.1f}mm')
ax3.fill_between(P_range, 0, R_range, alpha=0.2, color='blue')

ax3.set_xlabel('降雨量 P (mm)', fontsize=11)
ax3.set_ylabel('径流深度 R (mm)', fontsize=11)
ax3.set_title('题目2-3：SCS-CN模型产流曲线', fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.set_xlim(0, 150)
ax3.set_ylim(0, 150)

# 子图4：水量平衡
ax4 = fig.add_subplot(gs[1, 2])
components = ['降雨\nP', '初损\nIa', '下渗\nFa', '径流\nR']
values = [P, Ia, Fa, R]
colors_comp = ['blue', 'orange', 'brown', 'red']

y_pos = np.arange(len(components))
bars = ax4.barh(y_pos, values, color=colors_comp, alpha=0.7, edgecolor='black')

for i, (bar, val) in enumerate(zip(bars, values)):
    ax4.text(val + 2, bar.get_y() + bar.get_height()/2,
             f'{val:.1f}mm', va='center', fontsize=10, fontweight='bold')

ax4.set_yticks(y_pos)
ax4.set_yticklabels(components, fontsize=10)
ax4.set_xlabel('水量 (mm)', fontsize=11)
ax4.set_title('题目2-4：水量平衡分配', fontsize=11, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='x')

# 子图5：CN值与S、R的关系
ax5 = fig.add_subplot(gs[2, :2])
CN_range = np.linspace(40, 98, 50)
S_range = 25400 / CN_range - 254
Ia_range = lambda_param * S_range
R_range_cn = np.zeros_like(CN_range)

for i, (cn_val, s_val, ia_val) in enumerate(zip(CN_range, S_range, Ia_range)):
    if P > ia_val:
        R_range_cn[i] = (P - ia_val)**2 / (P - ia_val + s_val)

ax5_twin = ax5.twinx()

line1 = ax5.plot(CN_range, S_range, 'g-', linewidth=2, label='最大下渗量S')
line2 = ax5_twin.plot(CN_range, R_range_cn, 'r-', linewidth=2, label='径流深度R')

ax5.plot(CN_composite, S, 'go', markersize=10)
ax5_twin.plot(CN_composite, R, 'ro', markersize=10)

ax5.set_xlabel('CN值', fontsize=11)
ax5.set_ylabel('最大下渗量 S (mm)', fontsize=11, color='g')
ax5_twin.set_ylabel('径流深度 R (mm)', fontsize=11, color='r')
ax5.set_title(f'题目2-5：CN值对产流的影响（P={P}mm）', fontsize=12, fontweight='bold')

lines = line1 + line2
labels = [l.get_label() for l in lines]
ax5.legend(lines, labels, fontsize=10, loc='upper left')
ax5.grid(True, alpha=0.3)
ax5.set_xlim(40, 98)

# 子图6：不同降雨量下的径流系数
ax6 = fig.add_subplot(gs[2, 2])
P_test = np.array([10, 20, 40, 60, 80, 100, 120])
alpha_test = []

for p_val in P_test:
    if p_val > Ia:
        r_val = (p_val - Ia)**2 / (p_val - Ia + S)
        alpha_test.append(r_val / p_val)
    else:
        alpha_test.append(0)

ax6.plot(P_test, alpha_test, 'bo-', linewidth=2, markersize=8)
ax6.plot(P, alpha, 'r*', markersize=15, label=f'当前(P={P}mm, α={alpha:.2f})')

ax6.set_xlabel('降雨量 P (mm)', fontsize=11)
ax6.set_ylabel('径流系数 α', fontsize=11)
ax6.set_title('题目2-6：降雨量对径流系数的影响', fontsize=11, fontweight='bold')
ax6.legend(fontsize=10)
ax6.grid(True, alpha=0.3)
ax6.set_xlim(0, 130)
ax6.set_ylim(0, 1)

plt.savefig('题目2_SCS-CN模型.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目2图形已生成：题目2_SCS-CN模型.png")
plt.show()
