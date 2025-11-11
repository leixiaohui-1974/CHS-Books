"""
第6章 流域水文模型
题目1：新安江模型原理与参数

知识点：
- 蓄满产流机制
- 蓄水容量曲线
- 张力水与自由水
- 三水源划分
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 参数设置
F = 500  # 流域面积，km²
WM = 150  # 最大蓄水容量，mm
b = 0.3  # 蓄水容量曲线指数
IMP = 0.02  # 不透水面积比例
UM = 20  # 上层张力水容量，mm
LM = 80  # 下层张力水容量，mm
SM = 50  # 自由水蓄水容量，mm
KG = 0.3  # 地下水出流系数
KI = 0.7  # 壤中流出流系数
C = 0.15  # 地表径流系数

# 初始状态
W0 = 80  # 初始张力水蓄量，mm
S0 = 20  # 初始自由水蓄量，mm
P = 40  # 降雨，mm
E = 5   # 蒸发，mm

# 计算
PE = P - E  # 净雨
print("="*70)
print("题目1：新安江模型原理与参数")
print("="*70)
print(f"\n模型参数：")
print(f"  流域面积 F = {F} km²")
print(f"  最大蓄水容量 WM = {WM} mm")
print(f"  曲线指数 b = {b}")
print(f"  不透水面积比例 IMP = {IMP}")
print(f"  张力水容量 UM = {UM} mm, LM = {LM} mm")
print(f"  自由水容量 SM = {SM} mm")
print(f"  出流系数 KG = {KG}, KI = {KI}, C = {C}")
print(f"\n初始状态：")
print(f"  张力水蓄量 W0 = {W0} mm")
print(f"  自由水蓄量 S0 = {S0} mm")
print(f"\n降雨蒸发：")
print(f"  降雨 P = {P} mm")
print(f"  蒸发 E = {E} mm")
print(f"  净雨 PE = {PE} mm")

# 计算初始A/F
A_F_0 = 1 - (1 - W0/WM)**(1/(1+b))
print(f"\n产流计算：")
print(f"  初始产流面积比 A/F = {A_F_0:.3f}")

# 计算降雨后W'
W_new = W0 + PE
print(f"  降雨后蓄水量 W' = {W_new} mm")

if W_new <= WM:
    A_F_new = 1 - (1 - W_new/WM)**(1/(1+b))
    print(f"  新产流面积比 A'/F = {A_F_new:.3f}")
    # 简化产流计算
    R_temp = PE - (W_new - W0)
    R = max(0, R_temp) + PE * IMP  # 加上不透水面积产流
else:
    A_F_new = 1.0
    R = PE - (WM - W0) + PE * IMP

print(f"  透水面积产流 R_per = {max(0, R_temp):.1f} mm")
print(f"  不透水面积产流 R_imp = {PE * IMP:.1f} mm")
print(f"  总产流量 R = {R:.1f} mm")

# 简化：假设R=15mm用于演示三水源划分
R_demo = 15
S = S0 + R_demo
print(f"\n三水源划分（演示用R={R_demo}mm）：")
print(f"  自由水库水量 S = {S} mm")

# 三水源划分
if S <= SM:
    RS = C * S * (S / SM)**2
    RI = KI * (S - RS)
    RG = KG * (S - RS - RI)
else:
    # 溢出部分全部作为地表径流
    RS_overflow = S - SM
    S = SM
    RS = RS_overflow + C * S * (S / SM)**2
    RI = KI * (S - RS)
    RG = KG * (S - RS - RI)

S_remain = S - (RS + RI + RG)

print(f"  地表径流 RS = {RS:.2f} mm ({RS/(RS+RI+RG)*100:.1f}%)")
print(f"  壤中流 RI = {RI:.2f} mm ({RI/(RS+RI+RG)*100:.1f}%)")
print(f"  地下径流 RG = {RG:.2f} mm ({RG/(RS+RI+RG)*100:.1f}%)")
print(f"  总出流 = {RS+RI+RG:.2f} mm")
print(f"  剩余自由水 S' = {S_remain:.2f} mm")
print("="*70)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

# 子图1：蓄水容量曲线
ax1 = fig.add_subplot(gs[0, :2])
A_F_range = np.linspace(0, 1, 100)
WMM_range = WM * (1 - (1 - A_F_range)**(1+b))

# 不同b值对比
b_values = [0.1, 0.3, 0.5]
colors = ['blue', 'green', 'red']
for b_val, color in zip(b_values, colors):
    WMM_b = WM * (1 - (1 - A_F_range)**(1+b_val))
    ax1.plot(A_F_range, WMM_b, color=color, linewidth=2, 
             label=f'b={b_val}')

# 标注当前点
ax1.plot(A_F_0, W0, 'ko', markersize=12, label=f'初始状态(A/F={A_F_0:.2f})')
ax1.plot(A_F_new, W_new, 'r*', markersize=15, label=f'降雨后(A/F={A_F_new:.2f})')

ax1.set_xlabel('产流面积比例 A/F', fontsize=11)
ax1.set_ylabel('蓄水量 W (mm)', fontsize=11)
ax1.set_title('题目1-1：新安江蓄水容量曲线（不同b值）', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(0, 1)
ax1.set_ylim(0, WM*1.1)

# 子图2：新安江模型结构
ax2 = fig.add_subplot(gs[0, 2])
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.axis('off')

# 降雨
ax2.annotate('', xy=(5, 9), xytext=(5, 9.5),
             arrowprops=dict(arrowstyle='->', color='blue', lw=2))
ax2.text(5, 9.7, '降雨P', ha='center', fontsize=10, color='blue')

# 蒸发
ax2.annotate('', xy=(2, 8), xytext=(1, 8.5),
             arrowprops=dict(arrowstyle='->', color='orange', lw=1.5))
ax2.text(0.5, 8.5, '蒸发E', fontsize=9, color='orange')

# 张力水库
tension = Rectangle((3, 6), 4, 2, facecolor='lightblue', 
                     edgecolor='blue', linewidth=2)
ax2.add_patch(tension)
ax2.text(5, 7, '张力水库', ha='center', va='center', 
         fontsize=10, fontweight='bold')
ax2.text(5, 6.5, f'W={W0}→{W_new}mm', ha='center', fontsize=8)

# 自由水库
free = Rectangle((3, 3.5), 4, 2, facecolor='lightgreen',
                 edgecolor='green', linewidth=2)
ax2.add_patch(free)
ax2.text(5, 4.5, '自由水库', ha='center', va='center',
         fontsize=10, fontweight='bold')
ax2.text(5, 4, f'S={S0}→{S:.0f}mm', ha='center', fontsize=8)

# 出流
ax2.annotate('', xy=(7.5, 4.5), xytext=(7, 4.5),
             arrowprops=dict(arrowstyle='->', color='red', lw=2))
ax2.text(8.5, 4.5, 'RS', fontsize=9, color='red')

ax2.annotate('', xy=(7.5, 4.0), xytext=(7, 4.0),
             arrowprops=dict(arrowstyle='->', color='purple', lw=2))
ax2.text(8.5, 4.0, 'RI', fontsize=9, color='purple')

ax2.annotate('', xy=(7.5, 3.5), xytext=(7, 3.5),
             arrowprops=dict(arrowstyle='->', color='brown', lw=2))
ax2.text(8.5, 3.5, 'RG', fontsize=9, color='brown')

# 连接
ax2.plot([5, 5], [6, 5.5], 'k-', linewidth=2)

ax2.set_title('题目1-2：新安江模型结构', fontsize=11, fontweight='bold')

# 子图3：产流计算过程
ax3 = fig.add_subplot(gs[1, :2])
steps = ['初始状态', '降雨输入', '蒸发扣除', '产流计算', '三水源划分']
values = [W0, W0+P, W0+P-E, W_new, R_demo]
colors_bar = ['blue', 'cyan', 'yellow', 'green', 'red']

bars = ax3.bar(steps, values, color=colors_bar, alpha=0.7, edgecolor='black')
for i, (bar, val) in enumerate(zip(bars, values)):
    ax3.text(bar.get_x() + bar.get_width()/2, val + 3, f'{val:.0f}mm',
             ha='center', fontsize=10, fontweight='bold')

ax3.axhline(WM, color='red', linestyle='--', linewidth=2, label=f'WM={WM}mm')
ax3.set_ylabel('水量 (mm)', fontsize=11)
ax3.set_title('题目1-3：产流计算过程', fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3, axis='y')

# 子图4：参数b的影响
ax4 = fig.add_subplot(gs[1, 2])
b_test = [0.1, 0.3, 0.5]
descriptions = [
    '分布不均\n产流分散',
    '中等分布\n产流适中',
    '分布均匀\n产流集中'
]
positions = [1, 2, 3]

ax4.barh(positions, b_test, color=['blue', 'green', 'red'], alpha=0.6)
for pos, b_val, desc in zip(positions, b_test, descriptions):
    ax4.text(b_val + 0.02, pos, f'b={b_val}\n{desc}',
             va='center', fontsize=9)

ax4.set_xlabel('参数 b', fontsize=11)
ax4.set_yticks([])
ax4.set_title('题目1-4：参数b的物理意义', fontsize=11, fontweight='bold')
ax4.set_xlim(0, 0.6)

# 子图5：三水源划分
ax5 = fig.add_subplot(gs[2, :2])
sources = ['地表径流\nRS', '壤中流\nRI', '地下径流\nRG']
amounts = [RS, RI, RG]
colors_pie = ['red', 'purple', 'brown']
percentages = np.array(amounts) / sum(amounts) * 100

bars = ax5.bar(sources, amounts, color=colors_pie, alpha=0.7, edgecolor='black', linewidth=2)
for bar, amt, pct in zip(bars, amounts, percentages):
    ax5.text(bar.get_x() + bar.get_width()/2, amt + 0.5, 
             f'{amt:.2f}mm\n({pct:.1f}%)',
             ha='center', fontsize=10, fontweight='bold')

ax5.set_ylabel('径流量 (mm)', fontsize=11)
ax5.set_title('题目1-5：三水源划分结果', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3, axis='y')

# 子图6：时间响应特征
ax6 = fig.add_subplot(gs[2, 2])
time = np.linspace(0, 10, 100)

# 地表径流：快速响应
RS_curve = RS * np.exp(-1.5*time)
# 壤中流：中等响应
RI_curve = RI * time * np.exp(-0.5*time) / 2
# 地下径流：慢速响应
RG_curve = RG * (1 - np.exp(-0.2*time))

ax6.plot(time, RS_curve, 'r-', linewidth=2, label='地表径流RS（1-2天）')
ax6.plot(time, RI_curve, color='purple', linewidth=2, label='壤中流RI（3-7天）')
ax6.plot(time, RG_curve, color='brown', linewidth=2, label='地下径流RG（数月）')

ax6.set_xlabel('时间 (天)', fontsize=10)
ax6.set_ylabel('流量 (mm/day)', fontsize=10)
ax6.set_title('题目1-6：三水源时间响应特征', fontsize=11, fontweight='bold')
ax6.legend(fontsize=9)
ax6.grid(True, alpha=0.3)
ax6.set_xlim(0, 10)

plt.savefig('题目1_新安江模型.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目1图形已生成：题目1_新安江模型.png")
plt.show()
