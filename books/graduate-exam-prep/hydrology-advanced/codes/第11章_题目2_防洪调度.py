"""
第11章 水库调度
题目2：水库防洪调度计算

知识点：
- 防洪调度原理
- 调洪演算（水量平衡法）
- 削峰效果分析
- 防洪库容利用
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 基本数据
time = np.array([0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36])  # 小时
inflow = np.array([1000, 2000, 4000, 6000, 7000, 6500, 5000, 3500, 2000, 1500, 1000, 800, 600])  # m³/s

# 水库特征
V_Z = 150  # 汛限水位库容（10⁶ m³）
V_N = 200  # 正常蓄水位库容（10⁶ m³）
V_S = 250  # 设计洪水位库容（10⁶ m³）
V_flood = V_S - V_Z  # 防洪库容

# 下游安全泄量
Q_safe = 3000  # m³/s

# 初始条件
V_0 = V_Z  # 汛前库容
Q_0 = inflow[0]  # 初始出流

dt = 3 * 3600  # 时段长度（秒）

print("="*80)
print("题目2：水库防洪调度计算")
print("="*80)

print(f"\n水库特征：")
print(f"  汛限水位库容 V_Z = {V_Z} × 10⁶ m³")
print(f"  正常蓄水位库容 V_N = {V_N} × 10⁶ m³")
print(f"  设计洪水位库容 V_S = {V_S} × 10⁶ m³")
print(f"  防洪库容 = {V_flood} × 10⁶ m³")

print(f"\n下游条件：")
print(f"  安全泄量 Q_safe = {Q_safe} m³/s")

print(f"\n入库洪水：")
print(f"  洪峰流量 = {np.max(inflow)} m³/s（t={time[np.argmax(inflow)]}h）")
print(f"  洪水总量 = {np.trapz(inflow, time)*3600/1e6:.1f} × 10⁶ m³")

print(f"\n初始条件：")
print(f"  初始库容 V_0 = {V_0} × 10⁶ m³")
print(f"  初始出流 Q_0 = {Q_0} m³/s")

# 调洪演算
n = len(time)
volume = np.zeros(n)  # 库容（10⁶ m³）
outflow = np.zeros(n)  # 出流（m³/s）

volume[0] = V_0
outflow[0] = Q_0

print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("调洪演算（水量平衡法）")
print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"{'时刻':<6} {'入流I':<8} {'出流Q':<8} {'平均I':<8} {'平均Q':<8} {'蓄增ΔV':<9} {'库容V':<9} {'状态':<12}")
print(f"{'(h)':<6} {'(m³/s)':<8} {'(m³/s)':<8} {'(m³/s)':<8} {'(m³/s)':<8} {'(10⁶m³)':<9} {'(10⁶m³)':<9}")
print("-" * 80)

for i in range(1, n):
    I_t = inflow[i-1]
    I_t1 = inflow[i]
    Q_t = outflow[i-1]
    V_t = volume[i-1]
    
    # 调度策略
    if I_t1 <= Q_safe:
        Q_t1 = I_t1  # 自由泄流
    else:
        Q_t1 = Q_safe  # 控制泄流
    
    # 水量平衡计算蓄水增量
    I_avg = (I_t + I_t1) / 2
    Q_avg = (Q_t + Q_t1) / 2
    delta_V = (I_avg - Q_avg) * dt / 1e6  # 转换为10⁶m³
    
    # 更新库容
    V_t1 = V_t + delta_V
    
    # 检查库容约束
    if V_t1 > V_S:
        status = "超蓄！"
        # 实际应加大泄流，这里简化处理
        V_t1 = V_S
    elif V_t1 > V_N:
        status = "高水位"
    elif V_t1 > V_Z:
        status = "拦洪"
    else:
        status = "正常"
    
    volume[i] = V_t1
    outflow[i] = Q_t1
    
    print(f"{time[i]:<6.0f} {I_t1:<8.0f} {Q_t1:<8.0f} {I_avg:<8.0f} {Q_avg:<8.0f} {delta_V:<9.1f} {V_t1:<9.1f} {status:<12}")

print("-" * 80)

# 统计分析
V_max = np.max(volume)
V_max_idx = np.argmax(volume)
I_peak = np.max(inflow)
Q_peak = np.max(outflow)

print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("防洪调度效果分析")
print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

print(f"\n最高洪水位：")
print(f"  最大库容 V_max = {V_max:.1f} × 10⁶ m³（t={time[V_max_idx]}h）")
if V_max > V_S:
    print(f"  ⚠️  超过设计洪水位库容！超蓄 {V_max - V_S:.1f} × 10⁶ m³")
elif V_max > V_N:
    print(f"  在设计洪水位以下，正常蓄水位以上")
else:
    print(f"  未超过正常蓄水位")

print(f"\n削峰效果：")
print(f"  入流洪峰 I_peak = {I_peak} m³/s")
print(f"  出流洪峰 Q_peak = {Q_peak} m³/s")
print(f"  削减流量 = {I_peak - Q_peak} m³/s")
peak_reduction = (I_peak - Q_peak) / I_peak * 100
print(f"  削峰率 = {peak_reduction:.1f}%")

print(f"\n下游保护：")
if Q_peak <= Q_safe:
    print(f"  ✅ 出流始终≤{Q_safe} m³/s，下游安全")
else:
    print(f"  ⚠️  出流超过安全泄量")

print(f"\n防洪库容利用：")
used_flood = V_max - V_Z
utilization = used_flood / V_flood * 100
print(f"  使用防洪库容 = {used_flood:.1f} × 10⁶ m³")
print(f"  利用率 = {utilization:.1f}%")

print("="*80)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# 子图1：入流vs出流过程线
ax1 = fig.add_subplot(gs[0, :])
ax1.fill_between(time, 0, inflow, alpha=0.3, color='blue', label='入流过程')
ax1.plot(time, inflow, 'b-o', linewidth=2.5, markersize=8, label='入流I')
ax1.plot(time, outflow, 'r-s', linewidth=2.5, markersize=8, label='出流Q')
ax1.axhline(Q_safe, color='orange', linestyle='--', linewidth=2, label=f'安全泄量({Q_safe}m³/s)')

# 标注洪峰
ax1.plot(time[np.argmax(inflow)], I_peak, 'b*', markersize=20, label=f'入流洪峰({I_peak}m³/s)')
ax1.plot(time[np.argmax(outflow)], Q_peak, 'r*', markersize=20, label=f'出流洪峰({Q_peak}m³/s)')

ax1.set_xlabel('时间 (h)', fontsize=12, fontweight='bold')
ax1.set_ylabel('流量 (m³/s)', fontsize=12, fontweight='bold')
ax1.set_title(f'题目2-1：防洪调度过程（削峰率{peak_reduction:.1f}%）', fontsize=13, fontweight='bold')
ax1.legend(fontsize=10, loc='upper right')
ax1.grid(True, alpha=0.3)
ax1.set_xlim(-1, 37)

# 子图2：库容变化过程
ax2 = fig.add_subplot(gs[1, :])
ax2.fill_between(time, V_Z, volume, where=(volume>=V_Z), alpha=0.3, color='red', label='使用防洪库容')
ax2.plot(time, volume, 'b-o', linewidth=2.5, markersize=8, label='库容变化')
ax2.axhline(V_Z, color='green', linestyle='--', linewidth=2, label=f'汛限水位({V_Z})')
ax2.axhline(V_N, color='blue', linestyle='--', linewidth=2, label=f'正常蓄水位({V_N})')
ax2.axhline(V_S, color='red', linestyle='--', linewidth=2, label=f'设计洪水位({V_S})')
ax2.plot(time[V_max_idx], V_max, 'r*', markersize=20, label=f'最高水位({V_max:.0f})')

ax2.set_xlabel('时间 (h)', fontsize=12, fontweight='bold')
ax2.set_ylabel('库容 (10⁶ m³)', fontsize=12, fontweight='bold')
ax2.set_title('题目2-2：水库库容变化过程', fontsize=13, fontweight='bold')
ax2.legend(fontsize=10, loc='upper left')
ax2.grid(True, alpha=0.3)
ax2.set_xlim(-1, 37)
ax2.set_ylim(140, 260)

# 子图3：蓄水增量
ax3 = fig.add_subplot(gs[2, 0])
delta_V_series = np.diff(volume)
delta_V_series = np.insert(delta_V_series, 0, 0)
colors = ['red' if dv > 0 else 'blue' for dv in delta_V_series]
ax3.bar(time, delta_V_series, width=2, color=colors, alpha=0.7, edgecolor='black')
ax3.axhline(0, color='black', linewidth=1)
ax3.set_xlabel('时间 (h)', fontsize=11, fontweight='bold')
ax3.set_ylabel('蓄水增量 (10⁶ m³)', fontsize=11, fontweight='bold')
ax3.set_title('题目2-3：逐时段蓄水增量', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

# 子图4：防洪效果评价
ax4 = fig.add_subplot(gs[2, 1])
ax4.axis('off')
evaluation_text = f"""
防洪调度效果评价：

【削峰效果】
  入流洪峰：{I_peak} m³/s
  出流洪峰：{Q_peak} m³/s
  削峰率：{peak_reduction:.1f}%
  评价：{'优秀' if peak_reduction > 50 else '良好'}

【下游保护】
  安全泄量：{Q_safe} m³/s
  实际最大出流：{Q_peak} m³/s
  评价：{'✅安全' if Q_peak <= Q_safe else '⚠️超标'}

【库容利用】
  防洪库容：{V_flood} × 10⁶ m³
  使用防洪库容：{used_flood:.1f} × 10⁶ m³
  利用率：{utilization:.1f}%
  评价：{'⚠️接近上限' if utilization > 90 else '正常'}

【综合评价】
  {'✅调度成功，达到预期目标' if Q_peak <= Q_safe and V_max <= V_S else '⚠️存在风险，需要优化'}
"""
ax4.text(0.05, 0.95, evaluation_text, transform=ax4.transAxes,
         fontsize=10, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.savefig('题目2_防洪调度.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目2图形已生成：题目2_防洪调度.png")
plt.show()
