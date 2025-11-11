"""
第10章 水资源评价
题目1：水资源量计算

知识点：
- 水资源量计算原理
- 地表水资源量
- 地下水资源量
- 重复水量
- 水资源总量
- 水资源模数
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch

rcParams['font.sans-serif'] = ['SimHei']
rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 流域基本数据
A = 5000  # km²
P = 800   # mm
R = 300   # mm
E = 500   # mm

# 地表水数据
Ws_surface = 10.0e8  # m³，地表径流
Wg_baseflow = 4.0e8  # m³，地下径流（基流）
Ws_total = Ws_surface + Wg_baseflow  # 河川径流总量

# 地下水数据
Wg_rain = 3.5e8    # m³，降雨入渗补给
Wg_river = 1.5e8   # m³，河道渗漏补给
Wg_total = Wg_rain + Wg_river  # 地下水补给总量

print("="*70)
print("题目1：水资源量计算")
print("="*70)

print(f"\n流域基本信息：")
print(f"  流域面积 A = {A} km²")
print(f"  年均降水量 P = {P} mm")
print(f"  年均径流深 R = {R} mm")
print(f"  年均蒸发量 E = {E} mm")

print(f"\n地表水数据：")
print(f"  地表径流 = {Ws_surface/1e8:.1f}×10⁸ m³")
print(f"  地下径流（基流）= {Wg_baseflow/1e8:.1f}×10⁸ m³")
print(f"  河川径流总量 = {Ws_total/1e8:.1f}×10⁸ m³")

print(f"\n地下水数据：")
print(f"  降雨入渗补给 = {Wg_rain/1e8:.1f}×10⁸ m³")
print(f"  河道渗漏补给 = {Wg_river/1e8:.1f}×10⁸ m³")
print(f"  地下水补给总量 = {Wg_total/1e8:.1f}×10⁸ m³")

# 计算水资源量
print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("水资源量计算")
print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# 1. 地表水资源量
Ws = Ws_total
print(f"\n1. 地表水资源量：")
print(f"   Ws = 河川径流总量")
print(f"   Ws = {Ws/1e8:.1f}×10⁸ m³")

# 2. 地下水资源量
Wg = Wg_total
print(f"\n2. 地下水资源量：")
print(f"   Wg = 地下水补给总量")
print(f"   Wg = {Wg/1e8:.1f}×10⁸ m³")

# 3. 重复水量
W_repeat = Wg_baseflow
print(f"\n3. 重复水量（基流）：")
print(f"   W_repeat = 基流")
print(f"   W_repeat = {W_repeat/1e8:.1f}×10⁸ m³")

# 4. 水资源总量
W_total = Ws + Wg - W_repeat
print(f"\n4. 水资源总量：")
print(f"   W_total = Ws + Wg - W_repeat")
print(f"   W_total = {Ws/1e8:.1f} + {Wg/1e8:.1f} - {W_repeat/1e8:.1f}")
print(f"   W_total = {W_total/1e8:.1f}×10⁸ m³")

# 验证（水量平衡）
W_balance = (P - E) * 1e-3 * A * 1e6
print(f"\n验证（水量平衡）：")
print(f"   W = (P - E) × A")
print(f"   W = ({P} - {E}) × {A} × 10⁶")
print(f"   W = {W_balance/1e8:.1f}×10⁸ m³")
print(f"   误差 = {abs(W_total - W_balance)/W_balance*100:.2f}% ✓")

# 5. 水资源模数
M_mm = W_total / (A * 1e6) * 1000  # mm
M_wm = W_total / (A * 1e4)  # 万m³/km²

print(f"\n5. 水资源模数：")
print(f"   M = W_total / A")
print(f"   M = {M_mm:.1f} mm")
print(f"   M = {M_wm:.1f} 万m³/km²")

# 丰富程度评价
if M_wm > 70:
    level = "极丰富"
    climate = "湿润区"
elif M_wm > 40:
    level = "丰富"
    climate = "半湿润区"
elif M_wm > 20:
    level = "中等"
    climate = "半干旱区"
elif M_wm > 5:
    level = "贫乏"
    climate = "干旱区"
else:
    level = "极贫乏"
    climate = "极端干旱区"

print(f"\n丰富程度评价：")
print(f"   等级：{level}")
print(f"   气候区：{climate}")
print(f"   参考：全国平均 = 28.7 万m³/km²")
print(f"        长江流域 = 60 万m³/km²")
print(f"        黄河流域 = 7.5 万m³/km²")

print("="*70)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

# 子图1：水资源量组成（桑基图风格）
ax1 = fig.add_subplot(gs[0, :2])
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.axis('off')

# 地表水
ax1.add_patch(Rectangle((1, 6), 2, 1.4, facecolor='blue', alpha=0.6, edgecolor='black', linewidth=2))
ax1.text(2, 6.7, f'地表径流\n{Ws_surface/1e8:.1f}×10⁸m³', ha='center', va='center', fontsize=10, fontweight='bold')

ax1.add_patch(Rectangle((1, 4.2), 2, 0.8, facecolor='cyan', alpha=0.6, edgecolor='black', linewidth=2))
ax1.text(2, 4.6, f'地下径流\n{Wg_baseflow/1e8:.1f}×10⁸m³', ha='center', va='center', fontsize=9, fontweight='bold')

# 河川径流
ax1.add_patch(Rectangle((4, 4.5), 2, 2.5, facecolor='steelblue', alpha=0.7, edgecolor='black', linewidth=2))
ax1.text(5, 5.75, f'河川径流\n{Ws_total/1e8:.1f}×10⁸m³', ha='center', va='center', fontsize=10, fontweight='bold')
ax1.text(5, 5.0, f'(地表水资源量)', ha='center', va='center', fontsize=8)

# 地下水
ax1.add_patch(Rectangle((1, 1.5), 2, 0.7, facecolor='lightgreen', alpha=0.6, edgecolor='black', linewidth=2))
ax1.text(2, 1.85, f'降雨入渗\n{Wg_rain/1e8:.1f}×10⁸m³', ha='center', va='center', fontsize=9)

ax1.add_patch(Rectangle((1, 0.5), 2, 0.7, facecolor='lightblue', alpha=0.6, edgecolor='black', linewidth=2))
ax1.text(2, 0.85, f'河道渗漏\n{Wg_river/1e8:.1f}×10⁸m³', ha='center', va='center', fontsize=9)

ax1.add_patch(Rectangle((4, 0.5), 2, 1.7, facecolor='green', alpha=0.6, edgecolor='black', linewidth=2))
ax1.text(5, 1.35, f'地下水补给\n{Wg_total/1e8:.1f}×10⁸m³', ha='center', va='center', fontsize=10, fontweight='bold')

# 重复水量
ax1.add_patch(FancyBboxPatch((7, 4), 2, 1.5, boxstyle="round,pad=0.1", 
                              facecolor='yellow', alpha=0.6, edgecolor='red', linewidth=2, linestyle='--'))
ax1.text(8, 4.75, f'重复水量\n{W_repeat/1e8:.1f}×10⁸m³', ha='center', va='center', fontsize=10, fontweight='bold', color='red')

# 水资源总量
ax1.add_patch(FancyBboxPatch((7, 1), 2, 2, boxstyle="round,pad=0.1", 
                              facecolor='orange', alpha=0.7, edgecolor='black', linewidth=3))
ax1.text(8, 2.3, f'水资源总量\n{W_total/1e8:.1f}×10⁸m³', ha='center', va='center', fontsize=11, fontweight='bold')
ax1.text(8, 1.6, f'={Ws/1e8:.1f}+{Wg/1e8:.1f}-{W_repeat/1e8:.1f}', ha='center', va='center', fontsize=9)

# 箭头
arrow1 = FancyArrowPatch((3, 6.7), (4, 6), arrowstyle='->', mutation_scale=20, linewidth=2, color='black')
arrow2 = FancyArrowPatch((3, 4.6), (4, 5), arrowstyle='->', mutation_scale=20, linewidth=2, color='black')
arrow3 = FancyArrowPatch((3, 1.85), (4, 1.5), arrowstyle='->', mutation_scale=20, linewidth=2, color='black')
arrow4 = FancyArrowPatch((3, 0.85), (4, 1.0), arrowstyle='->', mutation_scale=20, linewidth=2, color='black')
arrow5 = FancyArrowPatch((6, 5.5), (7, 4.75), arrowstyle='->', mutation_scale=20, linewidth=2, color='red', linestyle='--')
arrow6 = FancyArrowPatch((6, 5.5), (7, 2), arrowstyle='->', mutation_scale=20, linewidth=2, color='black')
arrow7 = FancyArrowPatch((6, 1.35), (7, 2), arrowstyle='->', mutation_scale=20, linewidth=2, color='black')

for arrow in [arrow1, arrow2, arrow3, arrow4, arrow5, arrow6, arrow7]:
    ax1.add_patch(arrow)

ax1.set_title('题目1-1：水资源量组成与计算', fontsize=13, fontweight='bold')

# 子图2：水资源模数对比
ax2 = fig.add_subplot(gs[0, 2])
regions = ['本流域', '全国平均', '长江', '黄河']
modulus = [M_wm, 28.7, 60, 7.5]
colors_modulus = ['orange', 'gray', 'blue', 'brown']

bars = ax2.barh(regions, modulus, color=colors_modulus, alpha=0.7, edgecolor='black')
for bar, val in zip(bars, modulus):
    ax2.text(val + 2, bar.get_y() + bar.get_height()/2, f'{val:.1f}', va='center', fontsize=10, fontweight='bold')

ax2.set_xlabel('水资源模数 (万m³/km²)', fontsize=11, fontweight='bold')
ax2.set_title('题目1-2：水资源模数对比', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')
ax2.set_xlim(0, 70)

# 子图3：水资源量柱状图
ax3 = fig.add_subplot(gs[1, :2])
components = ['地表水\n资源量', '地下水\n资源量', '重复\n水量', '水资源\n总量']
values = [Ws/1e8, Wg/1e8, W_repeat/1e8, W_total/1e8]
colors_comp = ['blue', 'green', 'red', 'orange']

bars = ax3.bar(components, values, color=colors_comp, alpha=0.7, edgecolor='black', linewidth=2)
for bar, val in zip(bars, values):
    ax3.text(bar.get_x() + bar.get_width()/2, val + 0.3,
             f'{val:.1f}×10⁸m³', ha='center', fontsize=10, fontweight='bold')

ax3.set_ylabel('水量 (×10⁸ m³)', fontsize=12, fontweight='bold')
ax3.set_title('题目1-3：水资源量各组成部分', fontsize=13, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')
ax3.set_ylim(0, 20)

# 子图4：计算公式
ax4 = fig.add_subplot(gs[1, 2])
ax4.axis('off')
formula_text = f"""
水资源量计算公式：

1. 地表水资源量：
   Ws = 河川径流总量
   Ws = {Ws/1e8:.1f}×10⁸ m³

2. 地下水资源量：
   Wg = 地下水补给总量
   Wg = {Wg/1e8:.1f}×10⁸ m³

3. 重复水量：
   W_repeat = 基流
   W_repeat = {W_repeat/1e8:.1f}×10⁸ m³

4. 水资源总量：
   W_total = Ws + Wg - W_repeat
   W_total = {W_total/1e8:.1f}×10⁸ m³

5. 水资源模数：
   M = W_total / A
   M = {M_wm:.1f} 万m³/km²
"""
ax4.text(0.05, 0.95, formula_text, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

# 子图5：丰富程度评价等级
ax5 = fig.add_subplot(gs[2, :2])
levels_list = ['极丰富', '丰富', '中等', '贫乏', '极贫乏']
ranges = ['>70', '40-70', '20-40', '5-20', '<5']
colors_level = ['darkblue', 'blue', 'yellow', 'orange', 'red']

y_pos = np.arange(len(levels_list))
# 画分级图
for i, (lv, rg, color) in enumerate(zip(levels_list, ranges, colors_level)):
    ax5.barh(i, 1, left=0, color=color, alpha=0.6, edgecolor='black', linewidth=2)
    ax5.text(0.5, i, f'{lv}\n({rg})', ha='center', va='center', fontsize=10, fontweight='bold')

# 标注本流域
basin_idx = 2  # 中等
ax5.plot(0.9, basin_idx, 'k*', markersize=25, label=f'本流域({M_wm:.1f})')

ax5.set_yticks([])
ax5.set_xlim(0, 1)
ax5.set_title('题目1-4：水资源丰富程度评价等级（万m³/km²）', fontsize=13, fontweight='bold')
ax5.legend(fontsize=11, loc='upper right')

# 子图6：水量平衡示意
ax6 = fig.add_subplot(gs[2, 2])
ax6.axis('off')
balance_text = f"""
水量平衡验证：

降水：P = {P} mm
蒸发：E = {E} mm
径流：R = P - E = {P-E} mm

水资源总量：
W = R × A
W = {P-E} × {A} × 10⁶
W = {W_balance/1e8:.1f}×10⁸ m³

计算结果：
W_total = {W_total/1e8:.1f}×10⁸ m³

误差：{abs(W_total-W_balance)/W_balance*100:.2f}%

评价：{level}（{climate}）
"""
ax6.text(0.05, 0.95, balance_text, transform=ax6.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

plt.savefig('题目1_水资源量计算.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目1图形已生成：题目1_水资源量计算.png")
plt.show()
