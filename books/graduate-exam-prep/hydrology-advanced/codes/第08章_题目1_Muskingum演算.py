"""
第8章 洪水预报
题目1：Muskingum河道洪水演算

知识点：
- Muskingum原理
- 演算公式推导
- 演算系数计算
- 河道洪水演算
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 数据
time = np.array([0, 6, 12, 18, 24, 30, 36, 42, 48])
inflow = np.array([200, 500, 1000, 1500, 1200, 800, 500, 300, 200])

# Muskingum参数
K = 12  # h
x = 0.25
dt = 6  # h
Q0 = 200  # 初始流量

print("="*70)
print("题目1：Muskingum河道洪水演算")
print("="*70)
print(f"\n河段参数：")
print(f"  河段长度 L = 50 km")
print(f"  蓄量滞时 K = {K} h")
print(f"  权重系数 x = {x}")
print(f"  时段长度 Δt = {dt} h")
print(f"  初始流量 Q₀ = {Q0} m³/s")

# 计算演算系数
C0 = (dt + 2*K*x) / (dt + 2*K*(1-x))
C1 = (dt - 2*K*x) / (dt + 2*K*(1-x))
C2 = (-dt + 2*K*(1-x)) / (dt + 2*K*(1-x))

print(f"\n演算系数：")
print(f"  C₀ = {C0:.4f}")
print(f"  C₁ = {C1:.4f}")
print(f"  C₂ = {C2:.4f}")
print(f"  验证：C₀+C₁+C₂ = {C0+C1+C2:.4f} (应=1)")

# 演算
outflow = np.zeros_like(inflow, dtype=float)
outflow[0] = Q0

for i in range(1, len(time)):
    outflow[i] = C0 * inflow[i] + C1 * inflow[i-1] + C2 * outflow[i-1]

print(f"\n演算结果：")
print(f"{'时间(h)':<10} {'入流I(m³/s)':<15} {'出流O(m³/s)':<15}")
for t, I, O in zip(time, inflow, outflow):
    print(f"{t:<10} {I:<15} {O:<15.1f}")

# 洪峰分析
peak_in_idx = np.argmax(inflow)
peak_out_idx = np.argmax(outflow)
peak_in = inflow[peak_in_idx]
peak_out = outflow[peak_out_idx]
peak_time_in = time[peak_in_idx]
peak_time_out = time[peak_out_idx]

print(f"\n洪峰分析：")
print(f"  入流洪峰：{peak_in} m³/s，出现时间：{peak_time_in} h")
print(f"  出流洪峰：{peak_out:.1f} m³/s，出现时间：{peak_time_out} h")
print(f"  洪峰削减：{(peak_in - peak_out):.1f} m³/s ({(peak_in-peak_out)/peak_in*100:.1f}%)")
print(f"  洪峰滞后：{peak_time_out - peak_time_in} h")

# 洪量分析
volume_in = np.trapz(inflow, time) * 3600  # m³
volume_out = np.trapz(outflow, time) * 3600  # m³

print(f"\n洪量分析：")
print(f"  入流洪量：{volume_in:.0f} m³")
print(f"  出流洪量：{volume_out:.0f} m³")
print(f"  洪量差：{abs(volume_in - volume_out):.0f} m³ ({abs(volume_in-volume_out)/volume_in*100:.2f}%)")
print("="*70)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

# 子图1：入流vs出流过程线
ax1 = fig.add_subplot(gs[0, :2])
ax1.plot(time, inflow, 'b-o', linewidth=2, markersize=8, label='入流I')
ax1.plot(time, outflow, 'r-s', linewidth=2, markersize=8, label='出流O')
ax1.plot(peak_time_in, peak_in, 'b*', markersize=15, label=f'入流洪峰({peak_time_in}h, {peak_in}m³/s)')
ax1.plot(peak_time_out, peak_out, 'r*', markersize=15, label=f'出流洪峰({peak_time_out}h, {peak_out:.0f}m³/s)')
ax1.set_xlabel('时间 (h)', fontsize=11)
ax1.set_ylabel('流量 (m³/s)', fontsize=11)
ax1.set_title('题目1-1：Muskingum河道洪水演算', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(-2, 50)

# 子图2：演算系数
ax2 = fig.add_subplot(gs[0, 2])
coeff_names = ['C₀', 'C₁', 'C₂']
coeff_values = [C0, C1, C2]
colors = ['blue', 'green', 'red']
bars = ax2.bar(coeff_names, coeff_values, color=colors, alpha=0.7, edgecolor='black')
for bar, val in zip(bars, coeff_values):
    ax2.text(bar.get_x() + bar.get_width()/2, val + 0.02,
             f'{val:.3f}', ha='center', fontsize=10, fontweight='bold')
ax2.axhline(1, color='gray', linestyle='--', alpha=0.5)
ax2.set_ylabel('系数值', fontsize=11)
ax2.set_title('题目1-2：Muskingum演算系数', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_ylim(-0.1, 1.2)

# 子图3：洪峰削减和滞后
ax3 = fig.add_subplot(gs[1, :2])
ax3.bar(['入流洪峰', '出流洪峰'], [peak_in, peak_out], 
        color=['blue', 'red'], alpha=0.7, edgecolor='black')
ax3.text(0, peak_in + 30, f'{peak_in}m³/s', ha='center', fontsize=10, fontweight='bold')
ax3.text(1, peak_out + 30, f'{peak_out:.0f}m³/s', ha='center', fontsize=10, fontweight='bold')
ax3.set_ylabel('洪峰流量 (m³/s)', fontsize=11)
ax3.set_title(f'题目1-3：洪峰削减（{(peak_in-peak_out)/peak_in*100:.1f}%）', 
              fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

# 子图4：Muskingum原理示意
ax4 = fig.add_subplot(gs[1, 2])
ax4.axis('off')
principle_text = f"""
Muskingum原理：

1. 水量平衡
   I - O = dS/dt
   
2. 蓄泄关系
   S = K[xI + (1-x)O]
   
3. 演算公式
   Oₜ₊₁ = C₀Iₜ₊₁ + C₁Iₜ + C₂Oₜ
   
参数：
  K = {K} h (蓄量滞时)
  x = {x} (权重系数)
  
系数：
  C₀ = {C0:.3f}
  C₁ = {C1:.3f}
  C₂ = {C2:.3f}
"""
ax4.text(0.05, 0.95, principle_text, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

# 子图5：蓄量变化
ax5 = fig.add_subplot(gs[2, :2])
storage = K * (x * inflow + (1-x) * outflow)
ax5.fill_between(time, 0, storage, alpha=0.3, color='cyan', label='河段蓄量S')
ax5.plot(time, storage, 'c-o', linewidth=2, markersize=6)
ax5.set_xlabel('时间 (h)', fontsize=11)
ax5.set_ylabel('蓄量 (m³·h)', fontsize=11)
ax5.set_title('题目1-4：河段蓄量变化过程', fontsize=12, fontweight='bold')
ax5.legend(fontsize=10)
ax5.grid(True, alpha=0.3)
ax5.set_xlim(-2, 50)

# 子图6：参数敏感性分析
ax6 = fig.add_subplot(gs[2, 2])
x_range = np.linspace(0, 0.5, 50)
C0_range = []
C2_range = []
for x_val in x_range:
    C0_val = (dt + 2*K*x_val) / (dt + 2*K*(1-x_val))
    C2_val = (-dt + 2*K*(1-x_val)) / (dt + 2*K*(1-x_val))
    C0_range.append(C0_val)
    C2_range.append(C2_val)

ax6.plot(x_range, C0_range, 'b-', linewidth=2, label='C₀')
ax6.plot(x_range, C2_range, 'r-', linewidth=2, label='C₂')
ax6.plot(x, C0, 'bo', markersize=10, label=f'当前x={x}')
ax6.plot(x, C2, 'ro', markersize=10)
ax6.set_xlabel('权重系数 x', fontsize=11)
ax6.set_ylabel('演算系数', fontsize=11)
ax6.set_title('题目1-5：参数x对演算系数的影响', fontsize=11, fontweight='bold')
ax6.legend(fontsize=10)
ax6.grid(True, alpha=0.3)
ax6.set_xlim(0, 0.5)

plt.savefig('题目1_Muskingum演算.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目1图形已生成：题目1_Muskingum演算.png")
plt.show()
