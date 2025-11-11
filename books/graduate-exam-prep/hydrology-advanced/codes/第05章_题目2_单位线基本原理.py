"""
第5章 流域汇流
题目2：单位线基本原理

知识点：
- 单位线定义和假定
- 水量平衡验证
- 单位线迭加
- S曲线法
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 数据
F = 120  # km²
dt = 2   # h
time = np.array([0, 2, 4, 6, 8, 10, 12, 14, 16])
Q_unit = np.array([0, 15, 42, 58, 47, 32, 18, 8, 0])  # m³/s

# 水量平衡验证
W = np.trapz(Q_unit, time) * 3600  # m³
h = W / (F * 1e6) * 1000  # mm

print("="*70)
print("题目2：单位线基本原理")
print("="*70)
print(f"\n流域参数：")
print(f"  流域面积 F = {F} km²")
print(f"  单位线历时 Δt = {dt} h")
print(f"\n单位线数据：")
for i, (t, q) in enumerate(zip(time, Q_unit)):
    print(f"  t={t:2}h: Q={q} m³/s")

print(f"\n水量平衡验证：")
print(f"  径流总量 W = {W:.0f} m³")
print(f"  径流深度 h = {h:.1f} mm")
print(f"  理论值 = 10 mm")
print(f"  误差 = {(h-10)/10*100:.1f}%")

# 连续3个单位净雨的迭加
n_periods = 3
time_extended = np.arange(0, time[-1] + n_periods*dt + 1, dt)
Q_total = np.zeros_like(time_extended, dtype=float)

for i in range(n_periods):
    start_idx = i
    for j, q in enumerate(Q_unit):
        if start_idx + j < len(Q_total):
            Q_total[start_idx + j] += q

print(f"\n连续{n_periods}个单位净雨的径流过程：")
print(f"{'时间(h)':<10} {'流量(m³/s)':<12}")
for t, q in zip(time_extended, Q_total):
    print(f"{t:<10} {q:<12.0f}")

# S曲线
n_s = 10  # S曲线需要足够长
time_s = np.arange(0, time[-1] + n_s*dt + 1, dt)
S_curve = np.zeros_like(time_s, dtype=float)

for i in range(n_s):
    start_idx = i
    for j, q in enumerate(Q_unit):
        if start_idx + j < len(S_curve):
            S_curve[start_idx + j] += q

# Δt=4h的单位线（S曲线法）
dt_new = 4  # h
shift = dt_new // dt  # 偏移量（单位：原Δt）
U_4h = np.zeros(len(S_curve) - shift)
for i in range(len(U_4h)):
    U_4h[i] = (dt_new / dt) * (S_curve[i] - S_curve[i - shift] if i >= shift else S_curve[i])

time_4h = np.arange(0, len(U_4h)*dt, dt)

print(f"\nΔt={dt_new}h单位线（S曲线法）：")
print(f"{'时间(h)':<10} {'流量(m³/s)':<12}")
for i in range(min(10, len(time_4h))):
    print(f"{time_4h[i]:<10} {U_4h[i]:<12.1f}")

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

# 子图1：单位线
ax1 = fig.add_subplot(gs[0, :2])
ax1.plot(time, Q_unit, 'bo-', markersize=8, linewidth=2, label='Δt=2h单位线')
ax1.fill_between(time, 0, Q_unit, alpha=0.2)
ax1.plot(6, 58, 'r*', markersize=15, label=f'洪峰 Qp={58} m³/s')
ax1.grid(True, alpha=0.3)
ax1.set_xlabel('时间 (h)', fontsize=11)
ax1.set_ylabel('流量 (m³/s)', fontsize=11)
ax1.set_title('题目2-1：单位线（Δt=2h, 10mm净雨）', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.set_xlim(0, 18)

# 子图2：水量平衡
ax2 = fig.add_subplot(gs[0, 2])
ax2.axis('off')
balance_text = f"""
水量平衡验证：

1. 计算径流总量
   W = ∫Q(t)dt
   W = {W:.0f} m³
   
2. 计算径流深度
   h = W / F
   h = {W:.0f}/{F*1e6:.0e}
   h = {h:.2f} mm
   
3. 验证
   理论值 = 10 mm
   实际值 = {h:.2f} mm
   误差 = {(h-10)/10*100:.1f}%
   
4. 结论
   {"✅ 满足" if abs(h-10) < 2 else "⚠️ 误差较大"}
"""
ax2.text(0.05, 0.95, balance_text, transform=ax2.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

# 子图3：连续净雨迭加
ax3 = fig.add_subplot(gs[1, :2])
# 分别绘制三个单位线
for i in range(n_periods):
    Q_shifted = np.zeros_like(time_extended, dtype=float)
    start_idx = i
    for j, q in enumerate(Q_unit):
        if start_idx + j < len(Q_shifted):
            Q_shifted[start_idx + j] = q
    ax3.plot(time_extended, Q_shifted, '--', alpha=0.5, linewidth=1,
             label=f'第{i+1}个单位净雨')

# 总径流
ax3.plot(time_extended, Q_total, 'r-', linewidth=2, label='总径流（迭加）')
ax3.plot(8, 147, 'r*', markersize=15)
ax3.grid(True, alpha=0.3)
ax3.set_xlabel('时间 (h)', fontsize=11)
ax3.set_ylabel('流量 (m³/s)', fontsize=11)
ax3.set_title('题目2-2：连续3个单位净雨的迭加', fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)
ax3.set_xlim(0, 22)

# 子图4：单位线假定
ax4 = fig.add_subplot(gs[1, 2])
ax4.axis('off')
assumptions_text = """
单位线三大假定：

1. 线性假定
   净雨 ∝ 径流
   • 雨强加倍→流量加倍
   
2. 时间不变性
   相同Δt净雨
   →相同单位线
   • 季节无关
   
3. 迭加原理
   总径流 = Σ各净雨径流
   • 卷积计算
   Q(t) = Σ Pᵢ·U(t-iΔt)
   
应用条件：
  ✓ 相同降雨历时
  ✓ 下垫面稳定
  ✓ 线性系统
"""
ax4.text(0.05, 0.95, assumptions_text, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.7))

# 子图5：S曲线
ax5 = fig.add_subplot(gs[2, :2])
ax5.plot(time_s, S_curve, 'g-', linewidth=2, label='S曲线')
# S曲线错位4h
S_shifted = np.roll(S_curve, shift)
S_shifted[:shift] = 0
ax5.plot(time_s, S_shifted, 'm--', linewidth=2, label=f'S曲线错位{dt_new}h')
ax5.grid(True, alpha=0.3)
ax5.set_xlabel('时间 (h)', fontsize=11)
ax5.set_ylabel('流量 (m³/s)', fontsize=11)
ax5.set_title('题目2-3：S曲线法推求不同历时单位线', fontsize=12, fontweight='bold')
ax5.legend(fontsize=10)
ax5.set_xlim(0, 30)

# 子图6：新单位线对比
ax6 = fig.add_subplot(gs[2, 2])
ax6.plot(time, Q_unit, 'b-', linewidth=2, marker='o', label='Δt=2h')
if len(time_4h) > 0:
    ax6.plot(time_4h[:len(U_4h)], U_4h, 'r-', linewidth=2, marker='s', label='Δt=4h')
ax6.grid(True, alpha=0.3)
ax6.set_xlabel('时间 (h)', fontsize=10)
ax6.set_ylabel('流量 (m³/s)', fontsize=10)
ax6.set_title('题目2-4：不同历时单位线对比', fontsize=11, fontweight='bold')
ax6.legend(fontsize=9)
ax6.set_xlim(0, 20)

plt.savefig('题目2_单位线基本原理.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目2图形已生成：题目2_单位线基本原理.png")
plt.show()
