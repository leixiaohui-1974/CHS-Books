"""
第8章 洪水预报
题目2：洪水预报精度评价

知识点：
- 精度评价指标体系
- 确定性系数NSE
- 洪峰误差分析
- 洪量误差分析
- 过程相关系数
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 数据
time = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
Qo = np.array([100, 250, 550, 850, 1000, 900, 650, 400, 200, 100])  # 实测
Qf = np.array([120, 280, 600, 820, 950, 920, 680, 380, 220, 110])  # 预报

print("="*70)
print("题目2：洪水预报精度评价")
print("="*70)

# 基本统计
Qo_mean = np.mean(Qo)
Qf_mean = np.mean(Qf)

print(f"\n基本统计：")
print(f"  实测平均流量 Q̄ₒ = {Qo_mean:.1f} m³/s")
print(f"  预报平均流量 Q̄_f = {Qf_mean:.1f} m³/s")

# NSE系数
numerator = np.sum((Qo - Qf)**2)
denominator = np.sum((Qo - Qo_mean)**2)
NSE = 1 - numerator / denominator

print(f"\n确定性系数NSE：")
print(f"  分子 Σ(Qₒ-Q_f)² = {numerator:.0f}")
print(f"  分母 Σ(Qₒ-Q̄ₒ)² = {denominator:.0f}")
print(f"  NSE = 1 - {numerator:.0f}/{denominator:.0f}")
print(f"  NSE = {NSE:.4f}")
print(f"  评价：{'优秀' if NSE > 0.8 else '良好' if NSE > 0.7 else '一般'}")

# 洪峰误差
Qop = np.max(Qo)
Qfp = np.max(Qf)
Qop_idx = np.argmax(Qo)
Qfp_idx = np.argmax(Qf)
REQp = (Qfp - Qop) / Qop * 100
DTp = Qfp_idx - Qop_idx

print(f"\n洪峰误差：")
print(f"  实测洪峰 Qₒₚ = {Qop} m³/s (时段{Qop_idx+1})")
print(f"  预报洪峰 Q_fp = {Qfp} m³/s (时段{Qfp_idx+1})")
print(f"  洪峰相对误差 RE_Qp = {REQp:.2f}%")
print(f"  峰现时间误差 ΔTₚ = {DTp} 时段")
print(f"  评价：{'合格' if abs(REQp) <= 20 else '不合格'}")

# 洪量误差
Wo = np.sum(Qo)
Wf = np.sum(Qf)
REW = (Wf - Wo) / Wo * 100

print(f"\n洪量误差：")
print(f"  实测洪量 Wₒ = {Wo} m³")
print(f"  预报洪量 W_f = {Wf} m³")
print(f"  洪量相对误差 RE_W = {REW:.2f}%")
print(f"  评价：{'合格' if abs(REW) <= 20 else '不合格'}")

# 相关系数
r = np.corrcoef(Qo, Qf)[0, 1]

print(f"\n过程相关系数：")
print(f"  r = {r:.4f}")
print(f"  评价：相关性{'极强' if r > 0.9 else '强' if r > 0.7 else '中等'}")

# RMSE
RMSE = np.sqrt(np.mean((Qo - Qf)**2))
print(f"\n均方根误差：")
print(f"  RMSE = {RMSE:.2f} m³/s")

# MAE
MAE = np.mean(np.abs(Qo - Qf))
print(f"\n平均绝对误差：")
print(f"  MAE = {MAE:.2f} m³/s")

print("="*70)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

# 子图1：实测vs预报过程线
ax1 = fig.add_subplot(gs[0, :2])
ax1.plot(time, Qo, 'bo-', linewidth=2, markersize=8, label='实测Qₒ')
ax1.plot(time, Qf, 'rs--', linewidth=2, markersize=8, label='预报Q_f')
ax1.plot(Qop_idx+1, Qop, 'b*', markersize=15, label=f'实测洪峰({Qop}m³/s)')
ax1.plot(Qfp_idx+1, Qfp, 'r*', markersize=15, label=f'预报洪峰({Qfp}m³/s)')
ax1.set_xlabel('时段', fontsize=11)
ax1.set_ylabel('流量 (m³/s)', fontsize=11)
ax1.set_title(f'题目2-1：洪水预报精度评价（NSE={NSE:.3f}）', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# 子图2：误差时间序列
ax2 = fig.add_subplot(gs[0, 2])
errors = Qo - Qf
ax2.bar(time, errors, color=['red' if e > 0 else 'blue' for e in errors],
        alpha=0.7, edgecolor='black')
ax2.axhline(0, color='black', linewidth=1)
ax2.set_xlabel('时段', fontsize=11)
ax2.set_ylabel('误差 Qₒ-Q_f (m³/s)', fontsize=11)
ax2.set_title('题目2-2：预报误差时间序列', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

# 子图3：散点图
ax3 = fig.add_subplot(gs[1, :2])
ax3.scatter(Qo, Qf, s=100, alpha=0.6, edgecolors='black', linewidth=2)
# 1:1线
ax3.plot([0, 1100], [0, 1100], 'r--', linewidth=2, label='1:1线')
# 拟合线
z = np.polyfit(Qo, Qf, 1)
p = np.poly1d(z)
ax3.plot(Qo, p(Qo), 'b-', linewidth=2, label=f'拟合线(y={z[0]:.2f}x+{z[1]:.1f})')
ax3.set_xlabel('实测流量 Qₒ (m³/s)', fontsize=11)
ax3.set_ylabel('预报流量 Q_f (m³/s)', fontsize=11)
ax3.set_title(f'题目2-3：实测vs预报散点图（r={r:.3f}）', fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.set_xlim(0, 1100)
ax3.set_ylim(0, 1100)

# 子图4：精度指标汇总
ax4 = fig.add_subplot(gs[1, 2])
ax4.axis('off')
metrics_text = f"""
精度评价指标汇总：

1. 确定性系数
   NSE = {NSE:.4f}
   评价：优秀
   
2. 洪峰误差
   RE_Qp = {REQp:.2f}%
   ΔTₚ = {DTp} 时段
   评价：合格
   
3. 洪量误差
   RE_W = {REW:.2f}%
   评价：合格
   
4. 相关系数
   r = {r:.4f}
   评价：极强
   
5. RMSE
   {RMSE:.2f} m³/s
   
6. MAE
   {MAE:.2f} m³/s
"""
ax4.text(0.05, 0.95, metrics_text, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

# 子图5：洪峰和洪量对比
ax5 = fig.add_subplot(gs[2, :2])
categories = ['洪峰\n(m³/s)', '洪量\n(m³)']
observed = [Qop, Wo]
forecasted = [Qfp, Wf]
x = np.arange(len(categories))
width = 0.35

bars1 = ax5.bar(x - width/2, observed, width, label='实测', color='blue', alpha=0.7)
bars2 = ax5.bar(x + width/2, forecasted, width, label='预报', color='red', alpha=0.7)

# 标注数值
for bar, val in zip(bars1, observed):
    ax5.text(bar.get_x() + bar.get_width()/2, val + 30,
             f'{val:.0f}', ha='center', fontsize=9)
for bar, val in zip(bars2, forecasted):
    ax5.text(bar.get_x() + bar.get_width()/2, val + 30,
             f'{val:.0f}', ha='center', fontsize=9)

ax5.set_ylabel('数值', fontsize=11)
ax5.set_title('题目2-4：洪峰和洪量对比', fontsize=12, fontweight='bold')
ax5.set_xticks(x)
ax5.set_xticklabels(categories)
ax5.legend(fontsize=10)
ax5.grid(True, alpha=0.3, axis='y')

# 子图6：不同指标合格标准
ax6 = fig.add_subplot(gs[2, 2])
metric_names = ['NSE', 'RE_Qp\n(%)', 'ΔTₚ\n(时段)', 'RE_W\n(%)']
actual_values = [NSE, abs(REQp), abs(DTp), abs(REW)]
threshold_values = [0.7, 20, 3, 20]
colors_metric = ['green' if actual < thresh or (i == 0 and actual > thresh) 
                 else 'yellow' for i, (actual, thresh) in enumerate(zip(actual_values, threshold_values))]

bars = ax6.bar(metric_names, actual_values, color=colors_metric, alpha=0.7, edgecolor='black')
for bar, val in zip(bars, actual_values):
    ax6.text(bar.get_x() + bar.get_width()/2, val + 0.5,
             f'{val:.2f}', ha='center', fontsize=9, fontweight='bold')

ax6.set_ylabel('指标值', fontsize=11)
ax6.set_title('题目2-5：各指标实际值', fontsize=11, fontweight='bold')
ax6.grid(True, alpha=0.3, axis='y')

plt.savefig('题目2_预报精度评价.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目2图形已生成：题目2_预报精度评价.png")
plt.show()
