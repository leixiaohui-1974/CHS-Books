"""
第7章 降雨径流预报
题目2：实时校正技术（卡尔曼滤波）

知识点：
- 实时校正概念
- 误差自回归（AR）模型
- 卡尔曼滤波原理
- 预报精度提升
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# 数据
time = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
Qf = np.array([85, 120, 150, 180, 200, 190, 170, 140, 110, 90])  # 预报流量
Qo = np.array([90, 130, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])  # 观测流量

# 历史误差
errors = Qo - Qf
known_errors = errors[~np.isnan(errors)]

print("="*70)
print("题目2：实时校正技术（卡尔曼滤波）")
print("="*70)
print(f"\n已知数据：")
print(f"  时段 t-2: Qf={Qf[0]} m³/s, Qo={Qo[0]} m³/s, e={errors[0]:.0f} m³/s")
print(f"  时段 t-1: Qf={Qf[1]} m³/s, Qo={Qo[1]} m³/s, e={errors[1]:.0f} m³/s")
print(f"  时段 t:   Qf={Qf[2]} m³/s, Qo=?, e=?")

# AR(1)模型参数率定
phi1 = 0.6  # 经验值
print(f"\nAR(1)模型参数：")
print(f"  φ₁ = {phi1} (经验值)")

# 预报t时段误差
e_forecast = phi1 * known_errors[1]
print(f"\n误差预报：")
print(f"  ê(t) = φ₁ × e(t-1)")
print(f"  ê(t) = {phi1} × {known_errors[1]:.0f}")
print(f"  ê(t) = {e_forecast:.1f} m³/s")

# 校正预报流量
Qc_ar = Qf[2] + e_forecast
print(f"\nAR(1)校正结果：")
print(f"  Qc(t) = Qf(t) + ê(t)")
print(f"  Qc(t) = {Qf[2]} + {e_forecast:.1f}")
print(f"  Qc(t) = {Qc_ar:.1f} m³/s")

# 卡尔曼滤波（简化版）
# 初始化
x = np.zeros(len(time))  # 状态估计（流量）
P = np.zeros(len(time))  # 估计方差
x[0] = Qo[0]  # 初始状态
P[0] = 1.0    # 初始方差

# 卡尔曼滤波参数
Q_kf = 10.0  # 过程噪声方差（模型不确定性）
R_kf = 5.0   # 观测噪声方差（观测不确定性）
F_kf = 1.0   # 状态转移系数

# 卡尔曼滤波递推
for t in range(1, len(time)):
    # 预测
    x_pred = F_kf * x[t-1]
    P_pred = F_kf * P[t-1] * F_kf + Q_kf
    
    # 卡尔曼增益
    K = P_pred / (P_pred + R_kf)
    
    # 更新（如果有观测）
    if not np.isnan(Qo[t]):
        x[t] = x_pred + K * (Qo[t] - x_pred)
        P[t] = (1 - K) * P_pred
    else:
        # 无观测，用模型预报
        innovation = Qf[t] - x_pred
        x[t] = x_pred + K * innovation
        P[t] = (1 - K) * P_pred

Qc_kf = x[2]
print(f"\n卡尔曼滤波校正结果：")
print(f"  Qc(t) = {Qc_kf:.1f} m³/s")
print(f"  卡尔曼增益 K = {K:.3f}")

print(f"\n校正效果对比：")
print(f"  原预报：{Qf[2]} m³/s")
print(f"  AR校正：{Qc_ar:.1f} m³/s")
print(f"  KF校正：{Qc_kf:.1f} m³/s")
print("="*70)

# 创建图形
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

# 子图1：预报误差时间序列
ax1 = fig.add_subplot(gs[0, :2])
t_plot = time[:2]
e_plot = known_errors
ax1.plot(t_plot, e_plot, 'ro-', markersize=10, linewidth=2, label='历史误差')
ax1.plot(3, e_forecast, 'b*', markersize=15, label=f'预报误差 ê(t)={e_forecast:.1f}')
ax1.axhline(0, color='gray', linestyle='--', alpha=0.5)
ax1.set_xlabel('时段', fontsize=11)
ax1.set_ylabel('误差 e = Qo - Qf (m³/s)', fontsize=11)
ax1.set_title('题目2-1：预报误差时间序列', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_xticks([1, 2, 3])
ax1.set_xticklabels(['t-2', 't-1', 't'])

# 子图2：AR(1)模型示意
ax2 = fig.add_subplot(gs[0, 2])
ax2.axis('off')
ar_text = f"""
AR(1)误差自回归模型：

e(t) = φ₁·e(t-1) + ε(t)

参数：
  φ₁ = {phi1}
  
计算：
  e(t-2) = {known_errors[0]:.0f} m³/s
  e(t-1) = {known_errors[1]:.0f} m³/s
  
  ê(t) = {phi1}×{known_errors[1]:.0f}
       = {e_forecast:.1f} m³/s
       
校正：
  Qc(t) = Qf(t) + ê(t)
        = {Qf[2]} + {e_forecast:.1f}
        = {Qc_ar:.1f} m³/s
"""
ax2.text(0.05, 0.95, ar_text, transform=ax2.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

# 子图3：流量对比
ax3 = fig.add_subplot(gs[1, :2])
t_compare = [1, 2, 3]
Qf_compare = Qf[:3]
Qo_compare = [Qo[0], Qo[1], np.nan]
Qc_compare = [Qo[0], Qo[1], Qc_ar]

ax3.plot(t_compare, Qf_compare, 'b--', linewidth=2, marker='s', 
         markersize=8, label='模型预报 Qf')
ax3.plot(t_compare[:2], Qo_compare[:2], 'ro-', linewidth=2, 
         markersize=10, label='实测流量 Qo')
ax3.plot(t_compare, Qc_compare, 'g-', linewidth=2, marker='^',
         markersize=8, label='校正预报 Qc')

ax3.set_xlabel('时段', fontsize=11)
ax3.set_ylabel('流量 (m³/s)', fontsize=11)
ax3.set_title('题目2-2：原预报vs校正预报', fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.set_xticks([1, 2, 3])
ax3.set_xticklabels(['t-2', 't-1', 't'])

# 子图4：卡尔曼滤波流程
ax4 = fig.add_subplot(gs[1, 2])
ax4.axis('off')
kf_text = """
卡尔曼滤波流程：

1. 预测步骤
   x̂ₜ₋ = F·x̂ₜ₋₁
   Pₜ₋ = F·Pₜ₋₁·Fᵀ + Q

2. 更新步骤
   K = Pₜ₋/(Pₜ₋ + R)
   x̂ₜ = x̂ₜ₋ + K·(z - x̂ₜ₋)
   Pₜ = (1-K)·Pₜ₋
   
参数：
  Q: 过程噪声
  R: 观测噪声
  K: 卡尔曼增益
  
优点：
  • 最优估计
  • 自适应权重
  • 递推计算
"""
ax4.text(0.05, 0.95, kf_text, transform=ax4.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.7))

# 子图5：卡尔曼增益变化
ax5 = fig.add_subplot(gs[2, :2])
Q_range = np.linspace(1, 50, 100)
R_fixed = 5.0
P_fixed = 10.0

K_Q = P_fixed / (P_fixed + R_fixed)  # 固定情况
K_range = P_fixed / (P_fixed + R_fixed) * np.ones_like(Q_range)  # 简化

# 不同Q值的K
K_values = []
for Q_val in Q_range:
    P_pred = P_fixed + Q_val
    K_val = P_pred / (P_pred + R_fixed)
    K_values.append(K_val)

ax5.plot(Q_range, K_values, 'b-', linewidth=2)
ax5.axhline(K, color='red', linestyle='--', linewidth=2, label=f'当前K={K:.3f}')
ax5.set_xlabel('过程噪声方差 Q', fontsize=11)
ax5.set_ylabel('卡尔曼增益 K', fontsize=11)
ax5.set_title('题目2-3：卡尔曼增益与噪声的关系', fontsize=12, fontweight='bold')
ax5.legend(fontsize=10)
ax5.grid(True, alpha=0.3)
ax5.set_xlim(0, 50)
ax5.set_ylim(0, 1)

# 子图6：三种方法对比
ax6 = fig.add_subplot(gs[2, 2])
methods = ['原预报', 'AR校正', 'KF校正']
values = [Qf[2], Qc_ar, Qc_kf]
colors = ['blue', 'green', 'red']

bars = ax6.bar(methods, values, color=colors, alpha=0.7, edgecolor='black')
for bar, val in zip(bars, values):
    ax6.text(bar.get_x() + bar.get_width()/2, val + 2,
             f'{val:.1f}', ha='center', fontsize=10, fontweight='bold')

ax6.set_ylabel('流量 (m³/s)', fontsize=11)
ax6.set_title('题目2-4：三种方法对比', fontsize=11, fontweight='bold')
ax6.grid(True, alpha=0.3, axis='y')
ax6.set_ylim(140, 170)

plt.savefig('题目2_实时校正技术.png', dpi=150, bbox_inches='tight')
print("\n✅ 题目2图形已生成：题目2_实时校正技术.png")
plt.show()
